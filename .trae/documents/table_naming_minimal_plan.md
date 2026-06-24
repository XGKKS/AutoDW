# 表名LLM生成方案（最小化修改）

## 修改内容

### 1. db_examples.py - 仅添加 table_name_format 字段

```python
# 原文件结构保持不变，仅在每个数据库配置中添加一行：

DB_EXAMPLES = {
    'mysql': {
        'table_format': '使用下划线前缀表示分层（如 dwd_fin_order）',
        'example_full': '''CREATE TABLE dwd_fin_order (...)''',
        'example_abbr': '''CREATE TABLE dwd_fin_ord (...)''',
        'table_comment_syntax': '在 CREATE TABLE 末尾使用 COMMENT',
        'column_comment_syntax': '在字段定义后使用 COMMENT',
        'table_name_format': '{layer}_{subject}_{table}'  # 新增
    },
    'postgresql': {
        # ... 原有内容保持不变 ...
        'table_name_format': '{layer}.{subject}_{table}'  # 新增
    },
    'oracle': {
        # ... 原有内容保持不变 ...
        'table_name_format': '{LAYER}.{SUBJECT}_{TABLE}'  # 新增
    }
}
```

### 2. prompts.py - 添加表名生成提示词

```python
# 新增提示词模板
TABLE_NAME_PROMPT = """
【任务】根据以下信息生成符合规范的英文表名

【中文表名】{chinese_table_name}

【开发规范】
{standards_content}

【数据库类型】{db_type}

【表名格式要求】{table_format}

【输出示例】
{table_name_example}
"""
```

### 3. field_processor.py - 添加表名生成方法

```python
def generate_table_name(self, chinese_table_name, db_type, standards_content):
    """调用LLM生成英文表名"""
    db_config = get_db_example(db_type, self.root_match_priority)
    
    # 根据数据库类型设置输出示例
    table_name_example = {
        'mysql': 'dwd_fin_order',
        'postgresql': 'dwd.fin_order',
        'oracle': 'DWD.FIN_ORDER'
    }.get(db_type, 'dwd_fin_order')
    
    prompt = TABLE_NAME_PROMPT.format(
        chinese_table_name=chinese_table_name,
        standards_content=standards_content,
        db_type=db_type,
        table_format=db_config['table_format'],
        table_name_example=table_name_example
    )
    
    response = self._call_llm(prompt)
    return response.strip()
```

### 4. field_processor.py - 修改 generate_ddl_for_table

```python
def generate_ddl_for_table(self, table_name, table_info, field_mapping, 
                           db_type='mysql', root_match_priority='full',
                           standards_content=''):
    # 新增：调用LLM生成表名
    english_table_name = self.generate_table_name(
        table_name, db_type, standards_content
    )
    
    # 以下原有逻辑保持不变
    # ... 字段定义生成 ...
    # ... DDL组装 ...
    
    return ddl
```

## 文件修改清单

| 文件 | 修改类型 | 修改内容 |
|------|---------|---------|
| `db_examples.py` | 修改 | 每个数据库配置添加 `table_name_format` 字段 |
| `prompts.py` | 修改 | 添加 `TABLE_NAME_PROMPT` 模板 |
| `field_processor.py` | 修改 | 添加 `generate_table_name` 方法 |
| `field_processor.py` | 修改 | `generate_ddl_for_table` 添加表名生成调用 |

## 最小侵入性

- ✅ 不修改任何原有字段生成逻辑
- ✅ 不修改任何原有配置内容
- ✅ 只添加必要的新字段和方法
- ✅ 原有功能完全保留