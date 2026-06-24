import re
import jieba
from typing import List, Dict, Tuple, Optional
from .ddl_validator import DDLValidator
from app.root_policy import get_root_constraints, get_root_reuse_principle, normalize_priority


class UnifiedValidator:
    def __init__(self, word_roots: List[Dict], standards: Dict = None, root_match_priority: str = 'full'):
        self.word_roots = word_roots
        self.standards = standards or {}
        self.root_match_priority = root_match_priority
        self.ddl_validator = DDLValidator(word_roots, standards, root_match_priority)
        
        self.root_set = set()
        self.chinese_to_roots = {}
        self.build_root_index()

    def build_root_index(self):
        for root in self.word_roots:
            full = root.get('full_root', '').lower()
            abbr = root.get('abbr_root', '').lower()
            chinese = root.get('chinese_name', '')
            
            if full:
                self.root_set.add(full)
            if abbr and abbr != chinese:
                self.root_set.add(abbr)
            
            if chinese:
                if chinese not in self.chinese_to_roots:
                    self.chinese_to_roots[chinese] = []
                if normalize_priority(self.root_match_priority) == 'full' and full:
                    self.chinese_to_roots[chinese].append(full)
                if normalize_priority(self.root_match_priority) == 'abbr' and abbr and abbr != full and abbr != chinese:
                    self.chinese_to_roots[chinese].append(abbr)

    def get_available_roots_for_mode(self) -> List[str]:
        return self.ddl_validator.get_available_roots_for_mode()

    def get_root_mode_prompt_block(self) -> str:
        return "\n".join([
            get_root_constraints(self.root_match_priority),
            get_root_reuse_principle(self.root_match_priority),
            self.ddl_validator.get_root_mode_fix_requirements()
        ])

    def parse_all_ddl(self, ddl_dict: Dict[str, str]) -> Dict[str, Dict]:
        parsed_tables = {}
        
        for table_name, ddl in ddl_dict.items():
            tables = self.ddl_validator.parse_ddl(ddl)
            if tables:
                parsed_tables[table_name] = tables[0]
        
        return parsed_tables

    def validate_single_rules(self, ddl_dict: Dict[str, str]) -> List[Dict]:
        violations = []
        
        for table_name, ddl in ddl_dict.items():
            table_violations = self.ddl_validator.validate(ddl)
            for v in table_violations:
                v['table_name'] = table_name
            violations.extend(table_violations)
        
        return violations

    def validate_cross_table_consistency(self, parsed_tables: Dict[str, Dict]) -> List[Dict]:
        violations = []
        
        field_info = []
        for table_name, table_data in parsed_tables.items():
            for column in table_data.get('columns', []):
                field_info.append({
                    'table_name': table_name,
                    'field_name': column['name'],
                    'field_index': column.get('index'),
                    'comment': column.get('comment', '')
                })
        
        comment_to_fields = {}
        for field in field_info:
            comment = field['comment']
            if comment:
                if comment not in comment_to_fields:
                    comment_to_fields[comment] = []
                comment_to_fields[comment].append(field)
        
        for comment, fields in comment_to_fields.items():
            if len(fields) > 1:
                roots_used = set()
                root_to_tables = {}
                
                for field in fields:
                    field_name = field['field_name']
                    table_name = field['table_name']
                    
                    roots = self.ddl_validator.split_field_into_roots(field_name)
                    root_key = tuple(sorted(roots))
                    roots_used.add(root_key)
                    
                    if root_key not in root_to_tables:
                        root_to_tables[root_key] = []
                    root_to_tables[root_key].append(table_name)
                
                if len(roots_used) > 1:
                    violation_detail = f"中文含义 '{comment}' 在不同表中使用了不一致的词根：\n"
                    for root_key, tables in root_to_tables.items():
                        violation_detail += f"  - {'_'.join(root_key)}: {', '.join(tables)}\n"
                    
                    for field in fields:
                        violations.append({
                            'rule': '跨表一致性检查：同一中文含义使用不一致词根',
                            'level': 'error',
                            'message': f"中文含义 '{comment}' 在不同表中使用了不一致的词根命名，必须统一",
                            'detail': violation_detail.strip(),
                            'tables': list(set([f['table_name'] for f in fields])),
                            'table_name': field['table_name'],
                            'field_name': field['field_name'],
                            'field_index': field.get('field_index'),
                            'comment': comment,
                            'roots_used': [list(r) for r in roots_used],
                            'violation_target': 'field'
                        })
        
        return violations

    def validate_batch(self, ddl_dict: Dict[str, str]) -> Dict:
        parsed_tables = self.parse_all_ddl(ddl_dict)
        
        single_violations = self.validate_single_rules(ddl_dict)
        cross_violations = self.validate_cross_table_consistency(parsed_tables)
        
        return {
            'single_violations': single_violations,
            'cross_violations': cross_violations,
            'total_violations': len(single_violations) + len(cross_violations),
            'error_count': sum(1 for v in single_violations + cross_violations if v.get('level') == 'error'),
            'warning_count': sum(1 for v in single_violations + cross_violations if v.get('level') != 'error')
        }

    def group_violations_by_table(self, violations):
        violations_by_table = {}
        for v in violations:
            table_name = v.get('table_name')
            if table_name:
                if table_name not in violations_by_table:
                    violations_by_table[table_name] = []
                violations_by_table[table_name].append(v)
        return violations_by_table
    
    def generate_batch_fix_prompt(self, ddl_subset, violations_subset, tables_info=None):
        error_violations = [v for v in violations_subset if v.get('level') == 'error']
        warning_violations = [v for v in violations_subset if v.get('level') != 'error']
        
        error_list = "\n".join([f"- 【{v.get('rule', '')}】{v.get('message', '')}" for v in error_violations])
        warning_list = "\n".join([f"- 【{v.get('rule', '')}】{v.get('message', '')}" for v in warning_violations])
        
        cross_violations_detail = ""
        for v in violations_subset:
            if 'detail' in v:
                cross_violations_detail += f"\n{v['detail']}"
        
        available_roots = ", ".join(self.get_available_roots_for_mode())
        root_mode_block = self.get_root_mode_prompt_block()
        
        all_ddl_subset = "\n\n".join(ddl_subset.values())
        
        prompt = f"""请修正以下DDL中的规范违规问题：

【当前DDL（本批次）】
{all_ddl_subset}

【可用词根列表】
{available_roots}

{root_mode_block}

【错误问题（必须修正）】
{error_list if error_list else '无错误'}

【警告问题（建议修正）】
{warning_list if warning_list else '无警告'}

【跨表一致性问题详情】
{cross_violations_detail if cross_violations_detail else '无跨表一致性问题'}

【修正要求】
1. 针对上述每个问题给出具体修改
2. 对于同一中文含义在不同表中使用不同词根的情况，请选择最合理的词根进行统一
3. 修改后保持其他正确的字段不变
4. 如果在可用词根列表中找不到合适的替换词根，可以生成新词根，但必须满足当前词根模式强制约束
5. 保持所有表结构完整，不要遗漏任何表
6. 不得保留已经违反词根模式的原字段名或原表名

请输出修正后的完整DDL，不要解释。"""
        
        return prompt
    
    def generate_fix_prompt(self, all_ddl, violations, tables_info=None):
        error_violations = [v for v in violations if v.get('level') == 'error']
        warning_violations = [v for v in violations if v.get('level') != 'error']
        
        error_list = "\n".join([f"- 【{v.get('rule', '')}】{v.get('message', '')}" for v in error_violations])
        warning_list = "\n".join([f"- 【{v.get('rule', '')}】{v.get('message', '')}" for v in warning_violations])
        
        cross_violations_detail = ""
        for v in violations:
            if 'detail' in v:
                cross_violations_detail += f"\n{v['detail']}"
        
        available_roots = ", ".join(self.get_available_roots_for_mode())
        root_mode_block = self.get_root_mode_prompt_block()
        
        prompt = f"""请修正以下DDL中的规范违规问题：

【当前DDL】
{all_ddl}

【可用词根列表】
{available_roots}

{root_mode_block}

【错误问题（必须修正）】
{error_list if error_list else '无错误'}

【警告问题（建议修正）】
{warning_list if warning_list else '无警告'}

【跨表一致性问题详情】
{cross_violations_detail if cross_violations_detail else '无跨表一致性问题'}

【修正要求】
1. 针对上述每个问题给出具体修改
2. 对于同一中文含义在不同表中使用不同词根的情况，请选择最合理的词根进行统一
3. 修改后保持其他正确的字段不变
4. 如果在可用词根列表中找不到合适的替换词根，可以生成新词根，但必须满足当前词根模式强制约束
5. 保持所有表结构完整，不要遗漏任何表
6. 不得保留已经违反词根模式的原字段名或原表名

请输出修正后的完整DDL，不要解释。"""
        
        return prompt
    
    def _extract_field_name_from_location(self, location: str) -> str:
        if not location:
            return ""
        match = re.search(r'字段:\s*([^,\s]+)', location)
        if match:
            return match.group(1).strip()
        return ""

    def _find_column_by_name_or_index(self, table_data: Dict, field_name: str, field_index: int = None) -> Dict:
        columns = table_data.get('columns', []) if table_data else []
        if field_index:
            for column in columns:
                if column.get('index') == field_index:
                    return column
        if field_name:
            for column in columns:
                if column.get('name') == field_name:
                    return column
        return {}

    def extract_error_fields(self, violations: List[Dict], parsed_tables: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        从违规列表提取错误字段信息
        
        Args:
            violations: 单表违规列表
            parsed_tables: 解析后的表结构
        
        Returns:
            error_fields: {table_name: {field_name: {comment, current_name, violations}}}
        """
        error_fields = {}
        
        for violation in violations:
            if violation.get('level') != 'error':
                continue
            
            table_name = violation.get('table_name')
            field_name = violation.get('field_name') or self._extract_field_name_from_location(violation.get('location', ''))
            field_index = violation.get('field_index')
            
            if not table_name or not field_name:
                continue
            
            # 获取字段的中文注释
            column = self._find_column_by_name_or_index(parsed_tables.get(table_name), field_name, field_index)
            comment = violation.get('comment') or column.get('comment', '')
            if not field_index:
                field_index = column.get('index')
            token_roots = [root for root in jieba.lcut(comment or field_name, cut_all=False) if root.strip()]
            
            # 初始化表的错误字段
            if table_name not in error_fields:
                error_fields[table_name] = {}
            
            field_key = str(field_index) if field_index else field_name
            # 初始化字段的违规信息
            if field_key not in error_fields[table_name]:
                error_fields[table_name][field_key] = {
                    'comment': comment,
                    'current_name': field_name,
                    'field_index': field_index,
                    'token_roots': token_roots,
                    'violations': []
                }
            
            # 添加违规信息
            error_fields[table_name][field_key]['violations'].append({
                'rule': violation.get('rule', ''),
                'level': violation.get('level', ''),
                'message': violation.get('message', '')
            })
        
        return error_fields
    
    def generate_field_fix_prompt(self, error_fields: Dict[str, Dict], available_roots: List[str] = None) -> str:
        """
        生成针对错误字段的修正提示词
        
        Args:
            error_fields: 错误字段信息
            available_roots: 可用词根列表
        
        Returns:
            prompt: LLM修正提示词
        """
        if not error_fields:
            return ""
        
        fields_text = ""
        for table_name, fields in error_fields.items():
            for _, info in fields.items():
                violations_text = "\n".join([
                    f"  - {v['message']}" for v in info['violations']
                ])
                fields_text += f"""表: {table_name}
字段序号: {info.get('field_index') or ''}
当前字段: {info['current_name']}
中文注释: {info['comment']}
jieba分词词根: {', '.join(info.get('token_roots') or [])}
违规问题:
{violations_text}

"""
        
        roots_text = ", ".join(self.get_available_roots_for_mode())
        root_mode_block = self.get_root_mode_prompt_block()
        
        prompt = f"""请修正以下错误字段的英文字段名：

【错误字段列表】
{fields_text}

【可用词根列表】
{roots_text}

{root_mode_block}

【修正要求】
1. 必须按 jieba分词词根 逐词翻译并按原顺序用下划线拼接字段名
2. 同一个中文词根在所有字段中必须使用同一个英文词根
3. 优先使用可用词根列表中的词根，必须满足当前词根模式强制约束
4. 保持字段类型和其他属性不变
5. 不得输出 table、field、column 等无意义字段名
6. 不得对同名字段做全局替换，必须按字段序号定位

【输出格式】
每行一个：表名.字段序号.当前字段名:修正后的字段名

【输出示例】
order_table.2.table:product_id
user_table.4.table:create_time
"""
        
        return prompt
    
    def parse_field_fix_result(self, llm_output: str) -> Dict[str, Dict]:
        """
        解析LLM返回的字段修正结果
        
        Args:
            llm_output: LLM输出的修正结果
        
        Returns:
            fix_results: {table_name: {field_name: corrected_name}}
        """
        fix_results = {}
        
        if not llm_output:
            return fix_results
        
        lines = llm_output.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or ':' not in line:
                continue
            
            # 解析格式：表名.字段名:修正后的字段名
            parts = line.split(':', 1)
            if len(parts) != 2:
                continue
            
            field_key = parts[0].strip()
            corrected_name = parts[1].strip().strip('`"\'').lower()
            
            field_index = None
            if '.' in field_key:
                parts = field_key.rsplit('.', 2)
                if len(parts) == 3 and parts[1].isdigit():
                    table_name = parts[0].strip()
                    field_index = int(parts[1])
                    field_name = parts[2].strip()
                else:
                    table_name, field_name = field_key.rsplit('.', 1)
                    table_name = table_name.strip()
                    field_name = field_name.strip()
            else:
                # 如果没有表名，跳过或记录错误
                continue

            if self.ddl_validator.validate_root_usage(corrected_name, f"字段修正结果: {field_key}"):
                continue
            if self.ddl_validator.validate_forbidden_field_name(corrected_name):
                continue
            
            # 确保表名存在
            if table_name not in fix_results:
                fix_results[table_name] = {}
            
            fix_key = field_index if field_index else field_name
            fix_results[table_name][fix_key] = corrected_name
        
        return fix_results

    def _replace_column_by_index(self, ddl: str, field_index: int, new_name: str) -> str:
        lines = ddl.splitlines()
        in_table = False
        depth = 0
        current_index = 0
        column_pattern = re.compile(r'^(\s*)([`"]?)(\w+)([`"]?)(\s+.+)$')

        for idx, line in enumerate(lines):
            if re.search(r'CREATE\s+TABLE', line, re.IGNORECASE):
                in_table = True
                depth += line.count('(') - line.count(')')
                continue

            if in_table:
                depth += line.count('(') - line.count(')')
                match = column_pattern.match(line)
                if match and not match.group(3).upper() in {'PRIMARY', 'KEY', 'INDEX', 'CONSTRAINT'}:
                    current_index += 1
                    if current_index == field_index:
                        prefix, quote1, _old_name, quote2, suffix = match.groups()
                        lines[idx] = f"{prefix}{quote1}{new_name}{quote2}{suffix}"
                        return "\n".join(lines)
                if depth <= 0:
                    in_table = False

        return ddl
    
    def reassemble_ddl(self, original_ddl: Dict[str, str], fix_results: Dict[str, Dict], parsed_tables: Dict[str, Dict]) -> Dict[str, str]:
        """
        重组修正后的DDL
        
        Args:
            original_ddl: 原始DDL字典
            fix_results: 修正结果
            parsed_tables: 解析后的表结构
        
        Returns:
            corrected_ddl: 修正后的DDL字典
        """
        corrected_ddl = {}
        
        for table_name, ddl in original_ddl.items():
            if table_name not in fix_results:
                # 没有需要修正的字段，保持原DDL
                corrected_ddl[table_name] = ddl
                continue
            
            # 获取需要修正的字段映射
            table_fixes = fix_results[table_name]
            
            # 如果没有字段需要修正，保持原DDL
            if not table_fixes:
                corrected_ddl[table_name] = ddl
                continue
            
            modified_ddl = ddl
            for field_key, new_name in table_fixes.items():
                if isinstance(field_key, int):
                    modified_ddl = self._replace_column_by_index(modified_ddl, field_key, new_name)
                else:
                    modified_ddl = re.sub(rf'\b{re.escape(field_key)}\b', new_name, modified_ddl)
            
            corrected_ddl[table_name] = modified_ddl
        
        return corrected_ddl
