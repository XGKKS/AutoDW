# 默认规范（内置）功能修复 - 实现计划

## [x] Task 1: 后端支持默认规范启用操作
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 修改 `activate_standard()` 函数，支持 `default` 规范的启用
  - 启用默认规范时清空 `dev_standards.json` 的内容，使用内置默认
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-1.1: 调用 `/api/standards/default/activate` 返回成功
  - `programmatic` TR-1.2: 启用后 `dev_standards.json` 内容被清空
- **Notes**: 修改位置在 `backend/app/main.py`

## [x] Task 2: 后端返回正确的激活状态
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 修改 `load_all_standards()` 函数，返回默认规范的正确激活状态
  - 当没有其他规范激活时，默认规范应显示为已激活
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-2.1: 默认规范返回正确的 `is_active` 状态
  - `human-judgment` TR-2.2: 前端显示正确的状态标签
- **Notes**: 修改位置在 `backend/app/main.py`

## [x] Task 3: 前端禁用默认规范的删除按钮
- **Priority**: P1
- **Depends On**: None
- **Description**: 
  - 修改前端表格，对默认规范禁用或隐藏删除按钮
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `human-judgment` TR-3.1: 默认规范的删除按钮被禁用
  - `human-judgment` TR-3.2: 用户无法删除默认规范
- **Notes**: 修改位置在 `frontend/src/App.vue`

## [x] Task 4: 验证修复效果
- **Priority**: P1
- **Depends On**: Task 1, Task 2, Task 3
- **Description**: 
  - 验证默认规范显示正确状态
  - 验证默认规范可以启用
  - 验证默认规范无法删除
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3
- **Test Requirements**:
  - `human-judgment` TR-4.1: 默认规范显示正确的激活状态
  - `human-judgment` TR-4.2: 默认规范支持启用操作
  - `human-judgment` TR-4.3: 默认规范无法删除
- **Notes**: 需要手动测试