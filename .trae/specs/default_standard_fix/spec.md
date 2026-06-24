# 默认规范（内置）功能修复 - PRD

## Overview
- **Summary**: 修复默认规范（内置）无法删除和启用的问题
- **Purpose**: 解决用户反馈的默认规范操作按钮无效的bug
- **Target Users**: 所有使用规范管理功能的用户

## Goals
- 默认规范显示正确的激活状态
- 默认规范支持启用操作（切换到默认规范）
- 默认规范禁用删除按钮（避免误删）

## Non-Goals (Out of Scope)
- 不改变默认规范的核心存储机制
- 不修改其他规范的管理逻辑

## Background & Context
从代码分析发现：
1. 默认规范存储在 `dev_standards.json` 中，不是 `STANDARDS_DIR` 目录下的普通文件
2. `delete_standard_by_id()` 对 `default` 的处理只是清空内容，不会真正删除（设计如此）
3. `activate_standard()` 只操作 `STANDARDS_DIR` 中的文件，默认规范不在其中
4. 默认规范没有 `is_active` 字段，前端显示为"未启用"，但实际上它始终生效

## Functional Requirements
- **FR-1**: 默认规范应显示正确的激活状态（当前生效的规范）
- **FR-2**: 默认规范支持启用操作（切换到使用默认规范）
- **FR-3**: 默认规范的删除按钮应被禁用或隐藏
- **FR-4**: 禁用其他规范时应自动切换回默认规范

## Non-Functional Requirements
- **NFR-1**: 修复不应影响现有功能的正确性
- **NFR-2**: 用户体验应清晰明确

## Constraints
- **Technical**: 必须保持与现有API接口兼容
- **Dependencies**: 无外部依赖变更

## Assumptions
- 默认规范是系统必需的，不能被真正删除
- 默认规范始终作为兜底规范存在

## Acceptance Criteria

### AC-1: 默认规范显示正确状态
- **Given**: 用户进入规范管理页面
- **When**: 加载规范列表
- **Then**: 默认规范显示正确的激活状态
- **Verification**: `human-judgment`

### AC-2: 默认规范支持启用操作
- **Given**: 用户点击默认规范的"启用"按钮
- **When**: 调用启用API
- **Then**: 系统切换到使用默认规范
- **Verification**: `programmatic`

### AC-3: 默认规范禁用删除按钮
- **Given**: 用户进入规范管理页面
- **When**: 查看默认规范操作列
- **Then**: 删除按钮被禁用或隐藏
- **Verification**: `human-judgment`

## Open Questions
- [ ] 无