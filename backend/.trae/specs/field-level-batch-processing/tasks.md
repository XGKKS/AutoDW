# 字段级批量处理建表方案 - Implementation Plan

## [x] Task 1: 创建字段处理器模块
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 创建 `app/processors/field_processor.py` 模块
  - 实现字段提取、语义分组、批量生成词根等核心功能
- **Acceptance Criteria Addressed**: FR-1, FR-2, FR-3, FR-4
- **Test Requirements**:
  - `programmatic` TR-1.1: 成功从Excel解析100张表的字段信息
  - `programmatic` TR-1.2: 相同中文词义的字段被正确分组
  - `programmatic` TR-1.3: 每组字段数量不超过50个
- **Notes**: 语义分组采用完全匹配策略（相同中文即视为同一词义）

## [x] Task 2: 实现字段级DDL组装逻辑
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 在字段处理器中添加DDL组装方法
  - 根据字段映射表和原表结构生成完整DDL
- **Acceptance Criteria Addressed**: FR-5
- **Test Requirements**:
  - `programmatic` TR-2.1: 根据字段映射表成功生成DDL
  - `programmatic` TR-2.2: 同含义字段使用相同词根
- **Notes**: 支持MySQL、PostgreSQL、Oracle三种数据库类型

## [x] Task 3: 实现多线程并行处理
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 使用ThreadPoolExecutor实现字段组的并行处理
  - 控制最大并发数为5
- **Acceptance Criteria Addressed**: FR-6
- **Test Requirements**:
  - `programmatic` TR-3.1: 多个字段组并行处理
  - `programmatic` TR-3.2: 并发数不超过5
- **Notes**: 使用现有executor线程池

## [x] Task 4: 修改批量建表API
- **Priority**: P0
- **Depends On**: Task 1, Task 2, Task 3
- **Description**: 
  - 修改 `process_batch_task` 函数使用新的字段级处理流程
  - 保持与现有API接口的兼容性
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-4.1: 批量建表API正常工作
  - `programmatic` TR-4.2: 跨表词根一致性得到保证
  - `human-judgement` TR-4.3: 日志显示正确的处理流程
- **Notes**: 需要处理原有的统一校验逻辑，可能需要简化或移除

## [ ] Task 5: 测试与验证
- **Priority**: P1
- **Depends On**: Task 4
- **Description**: 
  - 编写单元测试验证字段分组和DDL生成
  - 集成测试验证完整流程
- **Acceptance Criteria Addressed**: 所有AC
- **Test Requirements**:
  - `programmatic` TR-5.1: 单元测试通过
  - `programmatic` TR-5.2: 集成测试通过
- **Notes**: 使用现有测试框架