# 字段处理进度信息优化 - 实现计划

## [ ] Task 1: 修改 jieba 分词进度消息格式
- **Priority**: P0
- **Depends On**: None
- **Description**:
  - 修改 `backend/app/processors/field_processor.py` 中的 `tokenize_all_fields_root_level` 方法
  - 在分词完成时更新进度消息格式为"分词：分词XX个，去重后YY个"
  - XX = len(all_roots)（所有分词数量，不去重）
  - YY = len(unique_roots)（去重后的词根数量）
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 分词完成时进度消息包含分词总数和去重后数量
  - `programmatic` TR-1.2: 消息格式为"分词：分词XX个，去重后YY个"
- **Notes**: 修改位置在第656行

## [x] Task 2: 修改历史词根匹配进度消息格式
- **Priority**: P0
- **Depends On**: None
- **Description**:
  - 修改 `backend/app/processors/field_processor.py` 中的 `match_roots_against_history` 方法
  - 在匹配完成时更新进度消息格式为"历史词根匹配X个，LLM需生成N个，共M个"
  - X = len(matched_roots)（匹配的词根数量）
  - N = len(unmatched_roots)（需要LLM生成的数量）
  - M = len(unique_roots)（总词根数量）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 匹配完成时进度消息包含匹配数量、LLM需生成数量和总数
  - `programmatic` TR-2.2: 消息格式为"历史词根匹配X个，LLM需生成N个，共M个"
- **Notes**: 修改位置在第697行

## [x] Task 3: 验证修改效果
- **Priority**: P1
- **Depends On**: Task 1, Task 2
- **Description**:
  - 运行测试验证修改是否生效
  - 确保进度消息格式正确
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-3.1: 测试脚本验证分词进度消息格式
  - `programmatic` TR-3.2: 测试脚本验证词根匹配进度消息格式
- **Notes**: 可以基于现有的测试脚本修改

# Task Dependencies
- [Task 3] depends on [Task 1, Task 2]
