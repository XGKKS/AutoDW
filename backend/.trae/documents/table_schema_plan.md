# 数据库分层字段处理方案

## 用户需求

当用户切换不同数据库类型时，系统应自动适配表名格式和语法：

### 数据库语法差异

| 数据库 | 表名格式 | 表注释语法 | 字段注释语法 |
|-------|---------|-----------|------------|
| MySQL | `dim_order_info` | 在 CREATE TABLE 末尾 | 在字段定义后 |
| PostgreSQL | `dim.order_info` | `COMMENT ON TABLE ...` | `COMMENT ON COLUMN ...` |
| Oracle | `DIM.ORDER_INFO` | `COMMENT ON TABLE ...` | `COMMENT ON COLUMN ...` |

## 实现方案

### 方案：动态提示词组装

**核心思路**：在提示词模板中动态插入数据库特定的建表示例，让 LLM 生成正确格式的 DDL。

### 修改内容

**1. 创建数据库特定示例配置**
**文件**: `backend/app/config/db_examples.py`

```python
DB_EXAMPLES = {
    'mysql': {
        'table_format': '使用下划线前缀表示分层',
        'example': '''CREATE TABLE dim_order_info (
    pk_order BIGINT PRIMARY KEY COMMENT '订单主键',
    order_name VARCHAR(128) COMMENT '订单名称',
    order_amt DECIMAL(18,4) COMMENT '订单金额'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';''',
        'table_comment_syntax': '在 CREATE TABLE 末尾使用 COMMENT',
        'column_comment_syntax': '在字段定义后使用 COMMENT'
    },
    'postgresql': {
        'table_format': '使用 schema.table 格式表示分层',
        'example': '''CREATE TABLE dim.order_info (
    pk_order BIGINT PRIMARY KEY,
    order_name VARCHAR(128),
    order_amt DECIMAL(18,4)
);

COMMENT ON TABLE dim.order_info IS '订单表';
COMMENT ON COLUMN dim.order_info.pk_order IS '订单主键';
COMMENT ON COLUMN dim.order_info.order_name IS '订单名称';
COMMENT ON COLUMN dim.order_info.order_amt IS '订单金额';''',
        'table_comment_syntax': 'COMMENT ON TABLE schema.table IS',
        'column_comment_syntax': 'COMMENT ON COLUMN schema.table.column IS'
    },
    'oracle': {
        'table_format': '使用大写 SCHEMA.TABLE 格式表示分层',
        'example': '''CREATE TABLE DIM.ORDER_INFO (
    PK_ORDER NUMBER(19) PRIMARY KEY,
    ORDER_NAME VARCHAR2(128),
    ORDER_AMT NUMBER(18,4)
);

COMMENT ON TABLE DIM.ORDER_INFO IS '订单表';
COMMENT ON COLUMN DIM.ORDER_INFO.PK_ORDER IS '订单主键';
COMMENT ON COLUMN DIM.ORDER_INFO.ORDER_NAME IS '订单名称';
COMMENT ON COLUMN DIM.ORDER_INFO.ORDER_AMT IS '订单金额';''',
        'table_comment_syntax': 'COMMENT ON TABLE SCHEMA.TABLE IS',
        'column_comment_syntax': 'COMMENT ON COLUMN SCHEMA.TABLE.COLUMN IS'
    }
}
```

**2. 修改提示词模板**
**文件**: `backend/app/main.py`
- 在 USER_PROMPT_TEMPLATE 中添加数据库特定示例占位符
- 在组装提示词时动态插入对应数据库的示例

**3. 更新 generate_ddl 方法**
- 根据 db_type 选择对应的示例配置
- 将示例插入到提示词中

## 实施步骤

1. 创建数据库示例配置文件
2. 修改提示词模板添加示例占位符
3. 更新 generate_ddl 方法动态组装提示词
4. 测试验证

## 预期结果

| 数据库类型 | 表名格式 | 生成的 DDL 格式 |
|-----------|---------|---------------|
| MySQL | `dim_order_info` | CREATE TABLE + inline COMMENT |
| PostgreSQL | `dim.order_info` | CREATE TABLE + separate COMMENT ON statements |
| Oracle | `DIM.ORDER_INFO` | CREATE TABLE + separate COMMENT ON statements |

## 风险评估

- 低风险：仅修改提示词组装逻辑，不影响核心验证功能
- 向后兼容：现有代码逻辑不变