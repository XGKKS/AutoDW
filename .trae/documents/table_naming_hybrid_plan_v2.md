# 混合方案：字段定义纯代码 + 表名LLM生成（修正版）

## 核心改进

根据用户反馈，确保提示词模板中的**建表示例**和**示例输出**保持一致，根据不同数据库类型提供正确的格式。

## 数据库类型与表名格式映射

| 数据库 | 建表格式示例 | 表名输出格式示例 |
|--------|-------------|----------------|
| MySQL | `CREATE TABLE dwd_fin_order (...)` | `dwd_fin_order` |
| PostgreSQL | `CREATE TABLE dwd.fin_order (...)` | `dwd.fin_order` |
| Oracle | `CREATE TABLE DWD.FIN_ORDER (...)` | `DWD.FIN_ORDER` |

## 实施计划

### 步骤1：更新数据库示例配置

修改 `db_examples.py`，为每个数据库添加 `table_name_format` 字段：

```python
DB_EXAMPLES = {
    'mysql': {
        'table_format': '使用下划线前缀表示分层（如 dwd_fin_order）',
        'table_name_format': '{layer}_{subject}_{table}',
        'example': '''CREATE TABLE dwd_fin_order (...)''',
        ...
    },
    'postgresql': {
        'table_format': '使用 schema.table 格式（如 dwd.fin_order）',
        'table_name_format': '{layer}.{subject}_{table}',
        'example': '''CREATE TABLE dwd.fin_order (...)''',
        ...
    },
    'oracle': {
        'table_format': '使用大写 SCHEMA.TABLE 格式（如 DWD.FIN_ORDER）',
        'table_name_format': '{LAYER}.{SUBJECT}_{TABLE}',
        'example': '''CREATE TABLE DWD.FIN_ORDER (...)''',
        ...
    }
}
```

### 步骤2：创建表名生成提示词模板

为不同数据库类型提供匹配的示例输出：

```python
TABLE_NAME_PROMPT = """
【任务】根据以下信息生成符合规范的英文表名

【中文表名】{chinese_table_name}

【开发规范】
{standards_content}

【数据库类型】{db_type}

【表名格式要求】{table_format}

【建表示例】
{db_example}

【输出格式】
请只输出英文表名，不要包含任何解释或额外内容。

【输出示例】
{table_name_example}
"""
```

### 步骤3：创建表名生成方法

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
    # 获取数据库配置
    db_config = get_db_example(db_type, self.root_match_priority)
    
    # 根据数据库类型生成示例输出
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
        db_example=db_config['example'],
        table_name_example=table_name_example
    )
    
    # 调用LLM
    response = self._call_llm(prompt)
    return response.strip()
```

### 步骤4：修改DDL生成流程

修改 `generate_ddl_for_table` 方法：

```python
def generate_ddl_for_table(self, table_name, table_info, field_mapping, 
                           db_type='mysql', root_match_priority='full',
                           standards_content=''):
    # 1. 调用LLM生成英文表名
    english_table_name = self.generate_table_name(
        table_name, db_type, standards_content
    )
    
    # 2. 纯代码生成字段定义（保持不变）
    field_definitions = []
    for field in fields:
        english_name = field_mapping.get(chinese_name, fallback_name)
        field_definitions.append(f"    `{english_name}` {field_type}")
    
    # 3. 根据数据库类型组装DDL（保持不变）
    if db_type == 'postgresql':
        schema_name = english_table_name.split('.')[0]
        table_name_only = english_table_name.split('.')[1]
        ddl = f'CREATE TABLE "{schema_name}"."{table_name_only}" (...)'
    else:
        ddl = f'CREATE TABLE `{english_table_name}` (...)'
    
    return ddl
```

## 文件修改清单

| 文件 | 修改类型 | 说明 |
|------|---------|------|
| `backend/app/config/db_examples.py` | 修改 | 添加 `table_name_format` 字段 |
| `backend/app/prompts.py` | 修改 | 添加表名生成提示词模板 |
| `backend/app/processors/field_processor.py` | 修改 | 添加 `generate_table_name` 方法 |
| `backend/app/processors/field_processor.py` | 修改 | 修改 `generate_ddl_for_table` 方法 |

## 关键改进点

1. **示例一致性**：建表示例和输出示例保持一致
2. **数据库适配**：根据数据库类型提供正确的格式示例
3. **规范遵从**：LLM根据最新开发规范生成表名
4. **代码复用**：字段定义继续使用纯代码生成

## 预期效果

修改后：
- PostgreSQL 生成 `dwd.fin_order` 格式
- MySQL 生成 `dwd_fin_order` 格式  
- Oracle 生成 `DWD.FIN_ORDER` 格式
- 开发规范修改后，LLM自动遵从最新规范