import re
from typing import List, Dict, Tuple, Optional
from app.root_policy import (
    build_root_sets,
    DEFAULT_ABBR_MAX_LEN,
    get_root_constraints,
    get_root_reuse_principle,
    get_theme_prefix_map,
    normalize_priority,
    resolve_abbr_max_len,
    table_business_domain_errors,
    validate_identifier_mode,
)
from app.name_normalizer import VALIDATION_ROOT_TOKENS


class DDLValidator:
    ALLOWED_TABLE_PREFIXES = ['ods_', 'dim_', 'dwd_', 'dws_', 'ads_', 'input_']
    ALLOWED_SCHEMAS = ['ods', 'dim', 'dwd', 'dws', 'ads', 'input']
    FORBIDDEN_PLACEHOLDERS = ['_attr', 'biz_attr', 'fld_', 'tbl_', '_field', '_column']
    FORBIDDEN_FIELD_NAMES = {
        'table', 'field', 'column', 'select', 'insert', 'update', 'delete',
        'create', 'drop', 'alter', 'where', 'group', 'order', 'by'
    }
    
    AMOUNT_SUFFIXES = ['amt', 'amount', '_amt', '_amount']
    NUMBER_SUFFIXES = ['num', 'number', '_num', '_number', 'cnt', '_cnt', 'count', '_count']
    ID_SUFFIXES = ['id', '_id']
    CODE_SUFFIXES = ['code', '_code', 'cd', '_cd']
    NAME_SUFFIXES = ['name', '_name', 'nm', '_nm']
    DESC_SUFFIXES = ['desc', '_desc', 'description', '_description']
    TIME_SUFFIXES = ['time', '_time', 'tm', '_tm']
    DATE_SUFFIXES = ['date', '_date']
    STATUS_SUFFIXES = ['status', '_status', 'sts', '_sts']
    TYPE_SUFFIXES = ['type', '_type', 'tp', '_tp']
    FLAG_SUFFIXES = ['flag', '_flag', 'flg', '_flg']

    def __init__(
        self,
        word_roots: List[Dict],
        standards: Dict = None,
        root_match_priority: str = 'full',
        abbr_max_len: int = DEFAULT_ABBR_MAX_LEN,
    ):
        self.word_roots = word_roots
        self.standards = standards or {}
        self.root_match_priority = root_match_priority
        self.abbr_max_len = resolve_abbr_max_len(abbr_max_len)
        
        self.root_set = set()
        self.full_root_set, self.abbr_root_set, self.abbr_to_full_roots = build_root_sets(word_roots)
        self.chinese_to_roots = {}
        self.build_root_index()

    def build_root_index(self):
        for root in self.word_roots:
            full = root.get('full_root', '').lower()
            abbr = root.get('abbr_root', '').lower()
            chinese = root.get('chinese_name', '')

            if full:
                self.root_set.add(full)
                self.full_root_set.add(full)
            if abbr and abbr != chinese:
                self.root_set.add(abbr)
                self.abbr_root_set.add(abbr)
                if full:
                    self.abbr_to_full_roots.setdefault(abbr, [])
                    if full not in self.abbr_to_full_roots[abbr]:
                        self.abbr_to_full_roots[abbr].append(full)

            if chinese:
                if chinese not in self.chinese_to_roots:
                    self.chinese_to_roots[chinese] = []
                if normalize_priority(self.root_match_priority) == 'full' and full:
                    self.chinese_to_roots[chinese].append(full)
                if normalize_priority(self.root_match_priority) == 'abbr' and abbr and abbr != full and abbr != chinese:
                    self.chinese_to_roots[chinese].append(abbr)

        for token in VALIDATION_ROOT_TOKENS:
            self.root_set.add(token)
            self.full_root_set.add(token)
            self.abbr_root_set.add(token)
    def parse_ddl(self, ddl: str, db_type: str = 'mysql') -> List[Dict]:
        tables = []
        table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([`"\']?)(\w+)([`"\']?)\s*\('
        column_pattern = r'^\s*([`"\']?)(\w+)([`"\']?)\s+(\w+(?:\([^)]+\))?)\s*(?:COMMENT\s*["\']([^"\']+)["\'])?'
        
        for match in re.finditer(table_pattern, ddl, re.IGNORECASE | re.MULTILINE):
            table_name = match.group(2)
            columns = []
            
            start_pos = match.end()
            depth = 1
            i = start_pos
            
            while i < len(ddl) and depth > 0:
                if ddl[i] == '(':
                    depth += 1
                elif ddl[i] == ')':
                    depth -= 1
                i += 1
            
            table_content = ddl[start_pos:i]
            
            for col_match in re.finditer(column_pattern, table_content, re.MULTILINE):
                col_name = col_match.group(2)
                col_type = col_match.group(4)
                col_comment = col_match.group(5)
                
                columns.append({
                    'name': col_name,
                    'type': col_type,
                    'comment': col_comment,
                    'index': len(columns) + 1
                })
            
            tables.append({
                'name': table_name,
                'columns': columns
            })
        
        return tables

    def split_field_into_roots(self, field_name: str) -> List[str]:
        parts = re.split(r'_', field_name.lower())
        return [p for p in parts if p]

    def validate(self, ddl: str, db_type: str = 'mysql') -> List[Dict]:
        violations = []
        tables = self.parse_ddl(ddl, db_type)
        
        for table in tables:
            violations.extend(self.validate_table_name(table['name']))
            violations.extend(self.validate_duplicate_columns(table['columns'], table['name']))

            for column in table['columns']:
                column_violations = self.validate_column(column, table['name'])
                for violation in column_violations:
                    violation.setdefault('table_name', table['name'])
                    violation.setdefault('field_index', column.get('index'))
                    violation.setdefault('field_name', column.get('name'))
                    violation.setdefault('comment', column.get('comment', ''))
                    violation.setdefault('violation_target', 'field')
                violations.extend(column_violations)
        
        return violations

    def validate_duplicate_columns(self, columns: List[Dict], table_name: str) -> List[Dict]:
        violations = []
        seen = {}
        for column in columns:
            field_name = column.get('name', '')
            field_lower = field_name.lower()
            if field_lower in seen:
                for duplicated in (seen[field_lower], column):
                    violations.append({
                        'rule': '规则2: 字段名唯一性检查',
                        'level': 'error',
                        'message': f"表 '{table_name}' 中字段名 '{field_name}' 重复",
                        'location': f"表: {table_name}, 字段序号: {duplicated.get('index')}, 字段: {duplicated.get('name')}",
                        'table_name': table_name,
                        'field_index': duplicated.get('index'),
                        'field_name': duplicated.get('name'),
                        'comment': duplicated.get('comment', ''),
                        'violation_target': 'field'
                    })
            else:
                seen[field_lower] = column
        return violations

    def validate_table_name(self, table_name: str) -> List[Dict]:
        violations = []
        
        if not any(table_name.startswith(prefix) for prefix in self.ALLOWED_TABLE_PREFIXES):
            violations.append({
                'rule': '规则1: 表名层级前缀检查',
                'level': 'error',
                'message': f"表名 '{table_name}' 未以允许的前缀开头（应为 ods_/dim_/dwd_/dws_/ads_/input_）",
                'location': f"表: {table_name}"
            })
        
            return violations

        table_body = table_name
        for prefix in self.ALLOWED_TABLE_PREFIXES:
            if table_body.startswith(prefix):
                table_body = table_body[len(prefix):]
                break

        for error in table_business_domain_errors(table_name, self.standards.get('content', '')):
            violations.append({
                'rule': '规则1: 表名业务域结构检查',
                'level': 'error',
                'message': error,
                'location': f"表 {table_name}"
            })

        theme_prefixes = set(get_theme_prefix_map(self.standards.get('content', '')).values())
        for prefix in sorted(theme_prefixes, key=len, reverse=True):
            if table_body.startswith(f"{prefix}_"):
                table_body = table_body[len(prefix) + 1:]
                break

        violations.extend(self.validate_root_usage(table_body, f"表: {table_name}"))
        
        return violations

    def validate_root_usage(self, name: str, location: str) -> List[Dict]:
        violations = []

        for error in validate_identifier_mode(
            name,
            self.root_match_priority,
            self.full_root_set,
            self.abbr_root_set,
            self.abbr_to_full_roots,
            self.abbr_max_len,
        ):
            violations.append({
                'rule': '规则2: 词根模式检查',
                'level': 'error',
                'message': error,
                'location': location
            })

        return violations

    def get_available_roots_for_mode(self) -> List[str]:
        if normalize_priority(self.root_match_priority) == 'abbr':
            return sorted(root for root in self.abbr_root_set if len(root) <= self.abbr_max_len)
        return sorted(self.full_root_set)

    def get_root_mode_fix_requirements(self) -> str:
        if normalize_priority(self.root_match_priority) == 'abbr':
            return (
                "【词根模式修正要求】\n"
                f"1. 当前为缩写模式，只能修正为词根库中的 abbr_root 或新的 <={self.abbr_max_len} 字母缩写词根\n"
                f"2. 字段名和表名主体中的每个词根都不能超过 {self.abbr_max_len} 个字母\n"
                f"3. 不允许输出 full_root、完整英文单词或超过 {self.abbr_max_len} 个字母的词根"
            )
        return (
            "【词根模式修正要求】\n"
            "1. 当前为全称模式，只能修正为词根库中的 full_root 或新的完整英文词根\n"
            "2. 如果名称中出现词根库定义过的 abbr_root，必须替换为对应 full_root\n"
            "3. 不允许继续输出缩写、首字母缩写或截断词根"
        )

    def validate_column(self, column: Dict, table_name: str) -> List[Dict]:
        violations = []
        field_name = column['name']
        field_type = column['type'].upper()
        field_comment = column.get('comment', '')
        
        violations.extend(self.validate_forbidden_field_name(field_name))
        violations.extend(self.validate_field_roots(field_name, table_name))
        violations.extend(self.validate_base_root_suffix(field_name, field_type))
        violations.extend(self.validate_root_count(field_name))
        violations.extend(self.validate_field_length(field_name))
        violations.extend(self.validate_forbidden_placeholders(field_name))
        violations.extend(self.validate_synonym_conflict(field_name, field_comment))
        
        return violations

    def validate_field_roots(self, field_name: str, table_name: str) -> List[Dict]:
        violations = []
        roots = self.split_field_into_roots(field_name)
        
        common_roots = {'id', 'time', 'date', 'is', 'has', 'can', 'will', 'not', 'del', 'deleted', 'pay', 'cust', 'main', 'damaged', 'part', 'maximum', 'speed', 'pdc', 'order', 'amt', 'create', 'update', 'name', 'code', 'status', 'type', 'flag'}
        
        for root in roots:
            if root not in self.root_set:
                if root in common_roots:
                    violations.append({
                        'rule': '规则2: 词根一词一根检查',
                        'level': 'warning',
                        'message': f"字段 '{field_name}' 中的词根 '{root}' 不在词根库中，但属于常见词根",
                        'location': f"表: {table_name}, 字段: {field_name}"
                    })
                else:
                    suggestions = self.find_similar_roots(root)
                    suggestion_str = f"，建议使用: {', '.join(suggestions)}" if suggestions else ""
                    violations.append({
                        'rule': '规则2: 词根一词一根检查',
                        'level': 'error',
                        'message': f"字段 '{field_name}' 中的词根 '{root}' 不存在于词根库中{suggestion_str}",
                        'location': f"表: {table_name}, 字段: {field_name}"
                    })
        
        violations.extend(self.validate_root_usage(field_name, f"表: {table_name}, 字段: {field_name}"))

        return violations

    def validate_forbidden_field_name(self, field_name: str) -> List[Dict]:
        violations = []
        field_lower = field_name.lower()
        if field_lower in self.FORBIDDEN_FIELD_NAMES or field_lower.startswith('field_'):
            violations.append({
                'rule': '规则8: 禁止保留字字段名检查',
                'level': 'error',
                'message': f"字段名 '{field_name}' 是保留字或无意义占位名，禁止作为最终字段名",
                'location': f"字段: {field_name}"
            })
        return violations

    def find_similar_roots(self, target: str) -> List[str]:
        similar = []
        target_lower = target.lower()
        
        for root in self.root_set:
            if target_lower in root or root in target_lower:
                similar.append(root)
        
        return similar[:5]

    def validate_base_root_suffix(self, field_name: str, field_type: str) -> List[Dict]:
        violations = []
        field_lower = field_name.lower()
        
        if field_type.startswith('DECIMAL') or field_type.startswith('NUMERIC') or field_type.startswith('FLOAT') or field_type.startswith('DOUBLE'):
            if not any(field_lower.endswith(suffix) for suffix in self.AMOUNT_SUFFIXES):
                violations.append({
                    'rule': '规则3: 基础词根后缀检查',
                    'level': 'warning',
                    'message': f"金额类型字段 '{field_name}' 建议以 amt/amount 结尾",
                    'location': f"字段: {field_name}"
                })
        
        if field_type.startswith('INT') or field_type.startswith('BIGINT') or field_type.startswith('SMALLINT'):
            if not any(field_lower.endswith(suffix) for suffix in self.NUMBER_SUFFIXES) and not any(field_lower.endswith(suffix) for suffix in self.ID_SUFFIXES):
                if 'count' in field_lower or 'num' in field_lower or 'quantity' in field_lower:
                    violations.append({
                        'rule': '规则3: 基础词根后缀检查',
                        'level': 'warning',
                        'message': f"数量类型字段 '{field_name}' 建议以 num/count 结尾",
                        'location': f"字段: {field_name}"
                    })
        
        return violations

    def validate_root_count(self, field_name: str) -> List[Dict]:
        violations = []
        roots = self.split_field_into_roots(field_name)
        
        if len(roots) > 4:
            violations.append({
                'rule': '规则4: 词根数量检查',
                'level': 'error',
                'message': f"字段 '{field_name}' 包含 {len(roots)} 个词根，超过最大允许的 4 个",
                'location': f"字段: {field_name}"
            })
        
        return violations

    def validate_field_length(self, field_name: str) -> List[Dict]:
        violations = []
        
        if len(field_name) > 60:
            violations.append({
                'rule': '规则5: 字段长度检查',
                'level': 'error',
                'message': f"字段名 '{field_name}' 长度为 {len(field_name)}，超过最大允许的 60 个字符",
                'location': f"字段: {field_name}"
            })
        
        return violations

    def validate_forbidden_placeholders(self, field_name: str) -> List[Dict]:
        violations = []
        
        for placeholder in self.FORBIDDEN_PLACEHOLDERS:
            if placeholder in field_name.lower():
                violations.append({
                    'rule': '规则8: 禁止占位符检查',
                    'level': 'error',
                    'message': f"字段 '{field_name}' 包含禁用的占位符 '{placeholder}'",
                    'location': f"字段: {field_name}"
                })
        
        return violations

    def validate_synonym_conflict(self, field_name: str, comment: str) -> List[Dict]:
        violations = []
        
        if not comment:
            return violations
        
        for chinese, roots in self.chinese_to_roots.items():
            if chinese in comment and len(roots) > 0:
                field_roots = self.split_field_into_roots(field_name)
                matched = False
                
                for root in roots:
                    if root in field_roots:
                        matched = True
                        break
                
                if not matched:
                    violations.append({
                        'rule': '规则7: 同义词根冲突检查',
                        'level': 'warning',
                        'message': f"字段 '{field_name}' 的注释包含 '{chinese}'，建议使用词根 {', '.join(roots)}",
                        'location': f"字段: {field_name}"
                    })
        
        return violations

    def extract_field_name(self, location: str) -> str:
        """从location字符串中提取字段名
        
        示例：
        - "表: user_info, 字段: user_id" -> "user_id"
        - "字段: create_time" -> "create_time"
        - "表: order_table" -> "order_table"
        """
        if "字段: " in location:
            return location.split("字段: ")[-1].strip()
        elif "表: " in location:
            return location.split("表: ")[-1].strip()
        return location.strip()

    def generate_fix_prompt(self, ddl: str, violations: List[Dict], attempt: int = 1) -> str:
        """生成修正Prompt - 包含详细的违规信息
        
        Args:
            ddl: 当前的DDL语句
            violations: 违规列表
            attempt: 当前修正轮次（第1轮、第2轮等）
        """
        violations_by_field = {}
        for v in violations:
            if v['level'] == 'error':
                field = self.extract_field_name(v['location'])
                if field not in violations_by_field:
                    violations_by_field[field] = []
                violations_by_field[field].append(v)
        
        detailed_violations = []
        for field, field_violations in violations_by_field.items():
            violation_text = f"\n字段 '{field}' 存在以下问题："
            for v in field_violations:
                violation_text += f"\n  - 【{v['rule']}】{v['message']}"
                violation_text += f"\n    位置: {v['location']}"
            detailed_violations.append(violation_text)
        
        error_list = "\n".join([f"- {v['message']}" for v in violations if v['level'] == 'error'])
        warning_list = "\n".join([f"- {v['message']}" for v in violations if v['level'] == 'warning'])
        
        available_roots = ", ".join(self.get_available_roots_for_mode())
        root_constraints = get_root_constraints(self.root_match_priority, self.abbr_max_len)
        root_reuse_principle = get_root_reuse_principle(self.root_match_priority, self.abbr_max_len)
        root_mode_fix_requirements = self.get_root_mode_fix_requirements()
        
        prompt = f"""请修正以下DDL的规范违规问题（第{attempt}轮修正）：

【当前DDL】
{ddl}

【可用词根列表】
{available_roots}

{root_constraints}
{root_reuse_principle}
{root_mode_fix_requirements}

【需要修正的问题（按字段分组）】
{''.join(detailed_violations) if detailed_violations else '无错误违规'}

{"【警告信息】\n" + warning_list if warning_list else ""}

【修正要求】
1. 针对上述每个问题给出具体修改
2. 修改后保持其他正确的字段不变
3. 如果在可用词根列表中找不到合适的替换词根，可以生成新词根，但必须满足当前词根模式强制约束
4. 不得保留已经违反词根模式的原字段名或原表名
5. 使用下划线分隔，全部小写，避免使用禁用占位符

请输出修正后的DDL，不要解释。"""
        
        return prompt
