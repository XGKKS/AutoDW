# 字段级批量处理建表方案 - Product Requirement Document

## Overview
- **Summary**: 实现字段级批量处理建表方案，将100张表的1000+字段按中文词义分组，批量请求LLM生成英文词根，确保跨表词根一致性
- **Purpose**: 解决当前批量建表时跨表词根不一致的问题，减少LLM调用次数，提升处理效率
- **Target Users**: 需要批量建表的数据仓库开发人员

## Goals
- 实现字段级语义分组，将相同/相近中文词义的字段归类
- 批量调用LLM生成英文词根，确保同一中文含义使用相同词根
- 大幅减少LLM调用次数（从100+次降低到20次左右）
- 保持与现有API接口的兼容性

## Non-Goals (Out of Scope)
- 不修改前端接口定义
- 不引入外部语义相似度模型（如BERT），使用简单的关键词匹配策略
- 不改变现有的单表建表流程

## Background & Context
当前批量建表流程存在以下问题：
1. 每张表独立调用LLM，导致同一中文含义在不同表中可能使用不同的英文词根
2. 44张表以上时，统一修正阶段可能超时
3. LLM调用次数过多，效率低下

新方案通过字段级处理，从根本上解决词根一致性问题。

## Functional Requirements
- **FR-1**: 从Excel中提取所有表的字段信息
- **FR-2**: 按中文词义对字段进行分组（相同词义放入同一组）
- **FR-3**: 每组字段批量调用LLM生成英文词根
- **FR-4**: 建立中文到英文词根的映射表
- **FR-5**: 根据映射表为每张表生成DDL
- **FR-6**: 支持多线程并行处理不同字段组

## Non-Functional Requirements
- **NFR-1**: 每组字段数量不超过50个，避免Prompt过长
- **NFR-2**: 支持100张表、1000个字段的批量处理
- **NFR-3**: 保持与现有API接口的兼容性

## Constraints
- **Technical**: Python 3.13, FastAPI, 现有项目结构
- **Dependencies**: requests, openpyxl, 现有validators模块

## Assumptions
- 用户上传的Excel文件格式符合现有模板规范
- LLM API响应格式稳定
- 字段中文名具有较好的语义一致性

## Acceptance Criteria

### AC-1: 字段提取完成
- **Given**: 用户上传包含100张表的Excel文件
- **When**: 系统解析Excel文件
- **Then**: 成功提取所有字段信息，包含表名、字段中文名、建议类型
- **Verification**: `programmatic`

### AC-2: 语义分组正确
- **Given**: 包含1000个字段的列表
- **When**: 执行语义分组
- **Then**: 相同中文词义的字段被分到同一组，每组不超过50个字段
- **Verification**: `programmatic`

### AC-3: 批量生成词根
- **Given**: 分组后的字段列表
- **When**: 批量调用LLM
- **Then**: 同一中文词义获得相同的英文词根
- **Verification**: `programmatic`

### AC-4: DDL组装完成
- **Given**: 字段映射表和原表结构
- **When**: 组装DDL
- **Then**: 生成完整的DDL语句，所有同含义字段使用相同词根
- **Verification**: `programmatic`

### AC-5: 多线程并行处理
- **Given**: 多个字段组
- **When**: 启动批量建表任务
- **Then**: 不同字段组并行处理，提升效率
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要支持近义词识别（当前仅支持完全匹配）
- [ ] 是否需要增加字段映射表的持久化缓存