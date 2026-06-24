# LLM生成表名重复问题修复 - 实现计划

## [x] Task 1: 修改 `generate_table_name()` 方法提取纯表名
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 在LLM返回表名后，检查是否包含schema.table格式（如 `dim.product_info`）
  - 如果包含，提取表名部分（如 `product_info`）
  - 处理不同数据库类型的格式（点号分隔或下划线分隔）
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 输入 `dim.dim_product_info` 返回 `dim_product_info`
  - `programmatic` TR-1.2: 输入 `dwd.fin_order` 返回 `fin_order`
- **Notes**: 修改位置在 `backend/app/processors/field_processor.py`

## [x] Task 2: 修改 `translate_table_name()` 方法保持一致性
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 在fallback翻译表名时，也添加相同的去schema前缀逻辑
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-2.1: 保持与 `generate_table_name()` 一致的行为
- **Notes**: 修改位置在 `backend/app/processors/field_processor.py`

## [x] Task 3: 验证修复效果
- **Priority**: P1
- **Depends On**: Task 1, Task 2
- **Description**: 
  - 测试PostgreSQL表名生成
  - 确保表名不再出现三重重复
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-3.1: PostgreSQL表名应为 `"dim"."product_info"`
  - `human-judgment` TR-3.2: 生成的DDL中表名无重复
- **Notes**: 需要运行测试验证