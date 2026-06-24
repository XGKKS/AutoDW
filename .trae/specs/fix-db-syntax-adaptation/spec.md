# 数据库语法适配修复方案

## Why
用户选择 PostgreSQL 数据库时，生成的 SQL 仍然使用 MySQL 语法：
- 使用 `VARCHAR` 而不是 `VARCHAR(n)` 或 `TEXT`
- 使用 `DATETIME` 而不是 `TIMESTAMP`
- 使用 MySQL 的 `COMMENT` 语法而不是 PostgreSQL 的 `COMMENT ON TABLE`

## What Changes
- 增强提示词，明确要求 LLM 按照目标数据库语法生成 SQL
- 添加数据库语法后处理器，在 LLM 生成后进行语法修正
- 更新数据库配置，添加更多语法差异信息

## Impact
- Affected specs: DDL生成、字段级处理
- Affected code:
  - `backend/app/main.py` - LLM提示词构建
  - `backend/app/config/db_examples.py` - 数据库配置
  - `backend/app/processors/field_processor.py` - 字段级DDL生成

## ADDED Requirements

### Requirement: 数据库语法正确适配
系统应该根据用户选择的数据库类型，生成符合该数据库语法规范的DDL语句。

#### Scenario: PostgreSQL语法生成
- **WHEN** 用户选择 PostgreSQL 数据库并执行批量建表
- **THEN** 生成的DDL应该符合PostgreSQL语法：
  - 使用 `TIMESTAMP` 代替 `DATETIME`
  - 使用 `COMMENT ON TABLE` 语法添加表注释
  - 使用 `COMMENT ON COLUMN` 语法添加字段注释
  - 使用 schema.table 格式（如 dim.item_info）

#### Scenario: MySQL语法生成
- **WHEN** 用户选择 MySQL 数据库并执行批量建表
- **THEN** 生成的DDL应该符合MySQL语法：
  - 使用 `DATETIME` 类型
  - 在 CREATE TABLE 语句末尾使用 COMMENT 添加表注释
  - 在字段定义后使用 COMMENT 添加字段注释

#### Scenario: Oracle语法生成
- **WHEN** 用户选择 Oracle 数据库并执行批量建表
- **THEN** 生成的DDL应该符合Oracle语法：
  - 使用 `NUMBER` 代替 `INT/BIGINT`
  - 使用 `VARCHAR2` 代替 `VARCHAR`
  - 使用 `DATE` 类型
  - 使用大写表名和字段名

## MODIFIED Requirements

### Requirement: DDL生成流程
在LLM生成DDL后，添加数据库语法后处理步骤，确保最终输出符合目标数据库语法规范。

## REMOVED Requirements
None