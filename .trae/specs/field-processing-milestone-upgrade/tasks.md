# 字段级处理子流程提级 - 实现计划

## [x] Task 1: 修改后端里程碑定义
- **Priority**: P0
- **Depends On**: None
- **Description**:
  - 修改 `backend/app/main.py` 中的 `update_progress` 函数
  - 将里程碑从7步扩展到8步（jieba分词和历史词根匹配各占一步）
  - 更新里程碑定义：
    1. 解析Excel
    2. 字段分组
    3. jieba分词
    4. 历史词根匹配 (新增)
    5. 生成字段名
    6. 组装DDL
    7. 最终校验
    8. 完成建表
  - 调整子进度处理逻辑，支持新的步骤编号
- **Acceptance Criteria Addressed**: 里程碑步骤扩展
- **Test Requirements**:
  - `programmatic` TR-1.1: 里程碑数量应为8
  - `programmatic` TR-1.2: 第4步标题应为"历史词根匹配"
- **Notes**: 需要调整所有步骤的状态判断逻辑

## [x] Task 2: 修改字段级处理进度更新
- **Priority**: P0
- **Depends On**: Task 1
- **Description**:
  - 修改 `backend/app/processors/field_processor.py` 中的进度更新调用
  - 在 `tokenize_all_fields_root_level` 方法中保持步骤编号为3
  - 在 `match_roots_against_history` 方法中添加进度更新，步骤编号为4
  - 调整后续步骤的编号：
    - 生成字段名: 从4调整为5
    - 组装DDL: 从5调整为6
- **Acceptance Criteria Addressed**: 进度更新逻辑调整
- **Test Requirements**:
  - `programmatic` TR-2.1: jieba分词进度更新应使用步骤编号3
  - `programmatic` TR-2.2: 历史词根匹配进度更新应使用步骤编号4
- **Notes**: 需要找到所有 `_update_progress` 调用并调整编号

## [x] Task 3: 修改主流程进度更新
- **Priority**: P0
- **Depends On**: Task 1
- **Description**:
  - 修改 `backend/app/main.py` 中 `process_batch_task` 函数的进度更新调用
  - 调整校验步骤编号从6调整为7
  - 调整完成步骤编号从7调整为8
- **Acceptance Criteria Addressed**: 进度更新逻辑调整
- **Test Requirements**:
  - `programmatic` TR-3.1: 校验进度更新应使用步骤编号7
  - `programmatic` TR-3.2: 完成进度更新应使用步骤编号8
- **Notes**: 需要检查所有进度更新调用

## [x] Task 4: 更新前端里程碑显示
- **Priority**: P1
- **Depends On**: Task 1
- **Description**:
  - 前端里程碑显示组件已支持动态里程碑列表，无需修改
  - 验证前端能正确显示8步里程碑
- **Acceptance Criteria Addressed**: 里程碑显示
- **Test Requirements**:
  - `human-judgment` TR-4.1: 前端应显示8个里程碑步骤
  - `human-judgment` TR-4.2: 每个步骤应显示正确的标题和状态
- **Notes**: 前端使用v-for动态渲染，应该自动适配

## [x] Task 5: 创建测试脚本验证修改
- **Priority**: P1
- **Depends On**: Task 1, Task 2, Task 3
- **Description**:
  - 创建或修改测试脚本验证里程碑扩展
  - 测试所有步骤的进度更新是否正确
  - 验证子进度信息是否正确显示
- **Acceptance Criteria Addressed**: 所有需求
- **Test Requirements**:
  - `programmatic` TR-5.1: 测试脚本应验证里程碑数量为8
  - `programmatic` TR-5.2: 测试脚本应验证所有步骤都能正确完成
- **Notes**: 可以基于现有的 test_milestone_fix.py 修改

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1]
- [Task 4] depends on [Task 1]
- [Task 5] depends on [Task 1, Task 2, Task 3]
