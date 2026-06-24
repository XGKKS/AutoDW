# 中文表名转换为英文修复方案

## Why
用户反馈即使完全匹配词根后，DDL中的表名仍然使用中文（如"入库明细表"），这不符合数据仓库的命名规范。需要将中文表名转换为英文表名。

## What Changes
- 在字段级处理流程中添加表名转换功能
- 尝试从历史词根中匹配表名中的中文词汇
- 提供表名转换的fallback机制（使用LLM或默认规则）
- 修改 `generate_ddl_for_table` 方法，使用英文表名

## Impact
- Affected specs: DDL生成、字段级处理
- Affected code:
  - `backend/app/processors/field_processor.py` - 添加表名转换逻辑
  - `backend/app/main.py` - 批量建表流程

## ADDED Requirements

### Requirement: 表名自动转换
系统应该将中文表名转换为英文表名，遵循数据仓库命名规范。

#### Scenario: 表名转换
- **WHEN** 生成DDL时遇到中文表名
- **THEN** 尝试从历史词根中匹配表名中的中文词汇
- **AND** 将匹配成功的词根组合成英文表名
- **AND** 对于未匹配的部分，使用fallback机制生成英文

#### Scenario: 分层表名格式
- **WHEN** 用户选择不同数据库类型
- **THEN** 表名格式应符合对应数据库规范：
  - MySQL: `layer_table_name`（下划线连接）
  - PostgreSQL: `layer.table_name`（schema.table格式）
  - Oracle: `LAYER.TABLE_NAME`（大写schema.table格式）

## MODIFIED Requirements

### Requirement: DDL生成流程
在字段级处理完成后，先转换表名为英文，再生成DDL。

## REMOVED Requirements
None