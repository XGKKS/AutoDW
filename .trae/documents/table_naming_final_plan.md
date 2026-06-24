# 表名LLM生成方案（保留原有字段生成逻辑）

## 核心原则

**保留所有现有功能**，只添加表名生成能力：
- ✅ 保留 `db_examples.py` 中的字段生成约束和 comment 示例
- ✅ 保留原有的词根匹配 + LLM字段生成逻辑
- ✅ 只添加 `table_name_format` 配置项
- ✅ 表名生成由LLM完成，字段生成保持不变

## 实施计划

### 步骤1：补充 db_examples.py

**只添加** `table_name_format` 字段，不修改任何现有内容：

```python
DB_EXAMPLES = {
    'mysql': {
        'table_format': '使用下划线前缀表示分层（如 dwd_fin_order）',
        'table_name_format': '{layer}_{subject}_{table}',  # 新增
        'example_full': '''CREATE TABLE dwd_fin_order (...)''',
        'example_abbr': '''CREATE TABLE dwd_fin_ord (...)''',
        'table_comment_syntax': '在 CREATE TABLE 末尾使用 COMMENT',
        'column_comment_syntax': '在字段定义后使用 COMMENT'
    },
    'postgresql': {
        'table_format': '使用 schema.table 格式（如 dwd.fin_order）',
        'table_name_format': '{layer}.{subject}_{table}',  # 新增
        'example_full': '''CREATE TABLE dwd.fin_order (...)''',
        'example_abbr': '''CREATE TABLE dwd.fin_ord (...)''',
        'table_comment_syntax': 'COMMENT ON TABLE schema.table IS',
        'column_comment_syntax': 'COMMENT ON COLUMN schema.table.column IS'
    },
    'oracle': {
        'table_format': '使用大写 SCHEMA.TABLE 格式（如 DWD.FIN_ORDER）',
        'table_name_format': '{LAYER}.{SUBJECT}_{TABLE}',  # 新增
        'example_full': '''CREATE TABLE DWD.FIN_ORDER (...)''',
        'example_abbr': '''CREATE TABLE DWD.FIN_ORD (...)''',
        'table_comment_syntax': 'COMMENT ON TABLE SCHEMA.TABLE IS',
        'column_comment_syntax': 'COMMENT ON COLUMN SCHEMA.TABLE.COLUMN IS'
    }
}
```

### 步骤2：创建表名生成提示词模板

在 `prompts.py` 中添加：

```python
TABLE_NAME_PROMPT = """
【任务】根据以下信息生成符合规范的英文表名

【中文表名】{chinese_table_name}

【开发规范】
{standards_content}

【数据库类型】{db_type}

【表名格式要求】{table_format}

【输出格式】
请只输出英文表名，不要包含任何解释或额外内容。

【输出示例】
{table_name_example}
"""
```

### 步骤3：添加表名生成方法

在 `FieldProcessor` 中添加 `generate_table_name` 方法：

```python
def generate_table_name(self, chinese_table_name, db_type, standards_content):
    """
    调用LLM生成英文表名
    :param chinese_table_name: 中文表名
    :param db_type: 数据库类型
    :param standards_content: 开发规范内容
    :return: 英文表名
    """
    # 获取数据库配置（保留原有逻辑）
    db_config = get_db_example(db_type, self.root_match_priority)
    
    # 根据数据库类型设置输出示例
    if db_type == 'mysql':
        table_name_example = 'dwd_fin_order'
    elif db_type == 'postgresql':
        table_name_example = 'dwd.fin_order'
    elif db_type == 'oracle':
        table_name_example = 'DWD.FIN_ORDER'
    else:
        table_name_example = 'dwd_fin_order'
    
    # 构建提示词
    prompt = TABLE_NAME_PROMPT.format(
        chinese_table_name=chinese_table_name,
        standards_content=standards_content,
        db_type=db_type,
        table_format=db_config['table_format'],
        table_name_example=table_name_example
    )
    
    # 调用LLM生成表名
    response = self._call_llm(prompt)
    return response.strip()
```

### 步骤4：修改 DDL 生成流程

**只修改表名部分**，字段生成逻辑保持不变：

```python
def generate_ddl_for_table(self, table_name, table_info, field_mapping, 
                           db_type='mysql', root_match_priority='full',
                           standards_content=''):
    # 1. 调用LLM生成英文表名（新增）
    english_table_name = self.generate_table_name(
        table_name, db_type, standards_content
    )
    
    # 2. 字段生成（完全保留原有逻辑）
    field_definitions = []
    for field in fields:
        chinese_name = field['name']
        if chinese_name in field_mapping:
            english_name, llm_type = field_mapping[chinese_name]
            final_type = llm_type if llm_type else field['type']
        else:
            english_name = self._fallback_name(chinese_name)
            final_type = field['type']
        
        # 类型转换（保留）
        final_type = self._convert_db_type(final_type, db_type)
        
        # 字段定义（保留）
        if db_type == 'mysql':
            field_definitions.append(f"    `{english_name}` {final_type} COMMENT '{chinese_name}'")
        else:
            field_definitions.append(f'    "{english_name}" {final_type}')
    
    # 3. 组装DDL（保留原有逻辑，使用新生成的表名）
    if db_type == 'postgresql':
        schema_name = english_table_name.split('.')[0] if '.' in english_table_name else 'public'
        table_name_only = english_table_name.split('.')[1] if '.' in english_table_name else english_table_name
        ddl = f'CREATE TABLE "{schema_name}"."{table_name_only}" (...)'
    else:
        ddl = f'CREATE TABLE `{english_table_name}` (...)'
    
    return ddl
```

## 文件修改清单

| 文件 | 修改类型 | 说明 |
|------|---------|------|
| `backend/app/config/db_examples.py` | 修改 | **只添加** `table_name_format` 字段 |
| `backend/app/prompts.py` | 修改 | 添加表名生成提示词模板 |
| `backend/app/processors/field_processor.py` | 修改 | 添加 `generate_table_name` 方法 |
| `backend/app/processors/field_processor.py` | 修改 | 修改 `generate_ddl_for_table` 使用LLM生成表名 |

## 保留的功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 词根匹配 | ✅ 保留 | 字段名优先使用历史词根 |
| LLM字段生成 | ✅ 保留 | 未匹配词根时调用LLM |
| 字段类型转换 | ✅ 保留 | 根据数据库类型转换 |
| Comment示例 | ✅ 保留 | 不同数据库的注释语法 |

## 新增的功能

| 功能 | 说明 |
|------|------|
| 表名LLM生成 | 根据开发规范和数据库类型生成 |
| 表名格式配置 | 支持不同数据库的表名格式 |

## 预期效果

修改后：
- ✅ 字段生成逻辑完全保留
- ✅ 表名由LLM根据开发规范生成
- ✅ 不同数据库类型生成对应格式的表名
- ✅ 开发规范修改后自动遵从