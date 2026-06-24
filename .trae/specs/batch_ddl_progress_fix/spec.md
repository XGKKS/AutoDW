# 批量建表进度状态同步修复 - PRD

## Overview
- **Summary**: 修复批量建表任务完成后，前端持续轮询进度且无法获取DDL结果的问题
- **Purpose**: 解决后端任务完成但进度状态未正确清除，导致前端无法感知任务结束的bug
- **Target Users**: 所有使用批量建表功能的用户

## Goals
- 任务完成后正确清除进度数据，使前端能感知任务结束
- 前端收到任务完成信号后正确停止轮询并获取结果

## Non-Goals (Out of Scope)
- 不修改批量建表的核心业务逻辑
- 不添加新功能

## Background & Context
从日志分析发现：
1. 后端显示任务完成（"批量建表任务完成，共5张表，成功5张"）
2. 但前端仍在不断请求 `/api/progress/{task_id}`
3. 前端无法预览到生成的DDL

根本原因：
- 后端任务完成后未清除 `progress_store` 中的进度数据
- 前端轮询逻辑未处理 `code === 1`（任务完成）的情况

## Functional Requirements
- **FR-1**: 后端批量建表任务完成后必须清除 `progress_store` 中的进度数据
- **FR-2**: 前端收到 `code === 1` 响应时应停止轮询并获取结果

## Non-Functional Requirements
- **NFR-1**: 修复不应影响现有功能的正确性和性能
- **NFR-2**: 前端轮询停止后不应继续产生无效请求

## Constraints
- **Technical**: 必须保持与现有API接口兼容
- **Dependencies**: 无外部依赖变更

## Assumptions
- 前端轮询间隔为500ms
- 任务完成后 `task_results` 中已存储正确结果

## Acceptance Criteria

### AC-1: 后端任务完成后清除进度数据
- **Given**: 批量建表任务执行完成
- **When**: 任务结果写入 `task_results`
- **Then**: `progress_store` 中对应任务的进度数据被删除
- **Verification**: `programmatic`

### AC-2: 前端正确处理任务完成状态
- **Given**: 前端轮询 `/api/progress/{task_id}`
- **When**: 收到 `code === 1` 的响应
- **Then**: 前端停止轮询并调用 `fetchBatchResult()` 获取结果
- **Verification**: `programmatic`

### AC-3: 前端能正确显示DDL结果
- **Given**: 批量建表任务完成且结果已保存
- **When**: 前端调用 `/api/batch-result/{task_id}`
- **Then**: 前端正确显示生成的DDL
- **Verification**: `human-judgment`

## Open Questions
- [ ] 无