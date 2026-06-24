# 词根匹配优先级优化方案

## 一、问题分析

### 1.1 DDL示例存储位置确认

已找到DDL示例单独存储在 `backend/app/config/db_examples.py` 文件中。

**当前结构：**

```python
DB_EXAMPLES = {
    'mysql': {
        'table_format': '使用下划线前缀表示分层',
        'example': '''CREATE TABLE dim_order_info (...)''',
        ...
    },
    'postgresql': {...},
    'oracle': {...}
}
```

### 1.2 用户核心需求

> "我希望根据我们选择的参数，能传入我们不同数据库的不同DDL示例。（现在已经有不同数据库的DDL，只不过需要根据缩写、全拼，分为两个版本）。而且这个prompt 应该是系统内置的一段可根据不同参数变化的约束。"

**优化目标：**

1. 为每个数据库添加全拼版和缩写版两套示例
2. 根据优先级参数动态选择示例
3. 添加动态约束规则（全拼要求完整单词，缩写要求词根≤4字母）

***

## 二、解决方案

### 2.1 修改 db\_examples.py

为每个数据库添加 `example_full`（全拼版）和 `example_abbr`（缩写版）：

```python
DB_EXAMPLES = {
    'mysql': {
        'table_format': '使用下划线前缀表示分层（如 dim_order_info）',
        'example_full': '''CREATE TABLE dim_order_info (
    order_id BIGINT PRIMARY KEY COMMENT '订单ID',
    order_name VARCHAR(128) COMMENT '订单名称',
    create_time DATETIME COMMENT '创建时间'
) COMMENT='订单表';''',
        'example_abbr': '''CREATE TABLE dim_order_info (
    ord_id BIGINT PRIMARY KEY COMMENT '订单ID',
    ord_nm VARCHAR(128) COMMENT '订单名称',
    crt_tm DATETIME COMMENT '创建时间'
) COMMENT='订单表';''',
        'table_comment_syntax': '在 CREATE TABLE 末尾使用 COMMENT',
        'column_comment_syntax': '在字段定义后使用 COMMENT'
    },
    # postgresql 和 oracle 同理
}
```

### 2.2 修改 get\_db\_example 函数

增加优先级参数：

```python
def get_db_example(db_type: str, priority: str = 'full') -> dict:
    """获取数据库特定的示例配置"""
    config = DB_EXAMPLES.get(db_type.lower(), DB_EXAMPLES['mysql'])
    
    # 根据优先级选择对应的示例
    if priority == 'abbr':
        config['example'] = config.get('example_abbr', config['example'])
    else:
        config['example'] = config.get('example_full', config['example'])
    
    return config
```

### 2.3 添加动态约束规则

在 `main.py` 中添加约束规则模板：

```python
# 全拼模式约束
FULL_ROOT_CONSTRAINTS = """【词根命名规则】
1. 字段名必须使用完整的英文单词，禁止使用缩写
2. 单词之间使用下划线分隔
3. 示例：create_time（正确），crt_tm（错误）"""

# 缩写模式约束
ABBR_ROOT_CONSTRAINTS = """【词根命名规则】
1. 字段名必须使用缩写形式
2. 每个词根不超过4个字母
3. 单词之间使用下划线分隔
4. 示例：crt_tm（正确），create_time（错误）"""
```

***

## 三、实施计划

### 3.1 阶段一：修改 db\_examples.py

**文件：** `backend/app/config/db_examples.py`

**修改内容：**

1. 为每个数据库添加 `example_full`（全拼版）和 `example_abbr`（缩写版）字段
2. 修改 `get_db_example` 函数，增加 `priority` 参数

### 3.2 阶段二：修改 main.py

**文件：** `backend/app/main.py`

**修改内容：**

1. 添加全拼/缩写模式的约束规则模板
2. 修改调用 `get_db_example` 的地方，传入优先级参数
3. 在Prompt中引入动态约束规则

***

## 四、文件修改清单

| 文件路径                                | 修改类型 | 说明                     |
| ----------------------------------- | ---- | ---------------------- |
| `backend/app/config/db_examples.py` | 修改   | 添加分版本DDL示例             |
| `backend/app/main.py`               | 修改   | 添加动态约束规则               |
| `backend/app/main.py`               | 修改   | 更新 `get_db_example` 调用 |

***

## 五、预期效果

| 场景     | 修改前  | 修改后                    |
| ------ | ---- | ---------------------- |
| 选择"全拼" | 固定示例 | 使用全拼版示例 + 全拼约束         |
| 选择"缩写" | 固定示例 | 使用缩写版示例 + 缩写约束（词根≤4字母） |
| 约束力    | 弱    | 强（明确规则约束）              |

