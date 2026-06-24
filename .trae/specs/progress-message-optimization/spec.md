# 字段处理进度信息优化 - PRD

## Overview
- **Summary**: 修改第三步（jieba分词）和第四步（历史词根匹配）的进度更新信息，使其返回更详细的统计数据
- **Purpose**: 让用户能够直观看到分词和词根匹配的详细统计信息
- **Target Users**: 所有使用批量建表功能的用户

## Goals
- 第三步（jieba分词）返回统计信息：分词总数和去重后数量
- 第四步（历史词根匹配）返回统计信息：匹配数量、LLM需生成数量和总数

## Non-Goals (Out of Scope)
- 不修改里程碑结构
- 不修改其他步骤的进度信息

## Background & Context
用户希望在批量建表过程中看到更详细的进度统计信息：
- jieba分词步骤：想知道总共分词多少个，去重后有多少个词根
- 词根匹配步骤：想知道历史词根匹配了多少个，需要LLM生成多少个，总共多少个词根

## Functional Requirements
- **FR-1**: jieba分词完成时，进度消息应显示"分词：分词XX个，去重后YY个"
- **FR-2**: 历史词根匹配完成时，进度消息应显示"历史词根匹配X个，LLM需生成N个，共M个"

## Non-Functional Requirements
- **NFR-1**: 修改不应影响现有功能的正确性
- **NFR-2**: 进度消息格式应保持一致

## Constraints
- **Technical**: 必须保持与现有API接口兼容
- **Dependencies**: 无外部依赖变更

## Assumptions
- 前端能正确显示更新后的进度消息

## Acceptance Criteria

### AC-1: jieba分词进度消息格式
- **Given**: jieba分词完成
- **When**: 调用_update_progress报告完成
- **Then**: 进度消息格式为"分词：分词XX个，去重后YY个"
- **Verification**: `programmatic`

### AC-2: 历史词根匹配进度消息格式
- **Given**: 历史词根匹配完成
- **When**: 调用_update_progress报告完成
- **Then**: 进度消息格式为"历史词根匹配X个，LLM需生成N个，共M个"
- **Verification**: `programmatic`

## Open Questions
- [ ] 无
