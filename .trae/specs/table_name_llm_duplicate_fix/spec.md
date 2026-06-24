# LLM生成表名重复问题修复 - PRD

## Overview
- **Summary**: 修复LLM生成表名时已经包含schema前缀，导致最终表名出现三重重复（如 `dim.dim.dim_product_info`）
- **Purpose**: 解决字段级处理模式下，LLM生成的表名已包含schema.table格式，代码又再次包装导致重复的问题
- **Target Users**: 所有使用批量建表功能的用户

## Goals
- LLM生成表名后，正确提取纯表名部分（去除schema前缀）
- 避免表名出现三重重复

## Non-Goals (Out of Scope)
- 不修改提示词内容
- 不修改其他核心业务逻辑

## Background & Context
从用户反馈的DDL可以看出：
```sql
CREATE TABLE "dim"."dim.dim_product_info" ...
```
表名变成了 `dim.dim.dim_product_info`，出现三重重复。

**根本原因分析**：
1. LLM根据提示词生成表名，提示词中要求PostgreSQL使用 `schema.table` 格式（如 `dwd.fin_order`）
2. LLM生成的表名可能是 `dim.dim_product_info`（包含schema前缀）
3. `generate_ddl_for_table()` 又再次包装一层schema：`"dim"."english_table_name"`
4. 最终结果变成 `"dim"."dim.dim_product_info"`

## Functional Requirements
- **FR-1**: `generate_table_name()` 方法应正确处理LLM返回的表名，提取纯表名部分
- **FR-2**: 当LLM返回的表名已包含schema.table格式时，应只提取表名部分

## Non-Functional Requirements
- **NFR-1**: 修复不应影响现有功能的正确性
- **NFR-2**: 向后兼容

## Constraints
- **Technical**: 必须保持与现有API接口兼容
- **Dependencies**: 无外部依赖变更

## Assumptions
- LLM可能返回纯表名或schema.table格式的表名
- 需要正确处理两种情况

## Acceptance Criteria

### AC-1: 正确提取纯表名
- **Given**: LLM返回 `dim.dim_product_info`
- **When**: 调用 `generate_table_name()`
- **Then**: 返回 `dim_product_info`（去除schema前缀）
- **Verification**: `programmatic`

### AC-2: 正确生成PostgreSQL DDL
- **Given**: 商品维度表，layer=dim
- **When**: 生成DDL
- **Then**: 表名应为 `"dim"."product_info"`
- **Verification**: `programmatic`

## Open Questions
- [ ] 无