# 优化字段翻译流程 - 产品需求文档

## Overview

- **Summary**: 优化现有的字段翻译流程，移除 `_fallback_name` 函数，采用更合理的词根级处理方案
- **Purpose**: 解决当前逐字段级翻译流程过于复杂的问题，采用更直接的词根级处理方式
- **Target Users**: 数据仓库开发者、数仓AI助手用户

## Goals

- 1. 采用分词后对所有字段进行 jieba 智能分词
- 2. 对分词结果进行词根级别分组，同一词根在多个字段中出现时进行归并处理
- 3. 优先使用历史词根进行匹配
- 4. 未匹配到的词根统一交由 LLM 处理，同时作为新词根返回，方便保存
- 5. 完成词根翻译后再拼接回完整的字段名

## Non-Goals (Out of Scope)

- 保留 `_fallback_name` 函数（该功能将被移除）
- 修改表名处理流程不做改动
- 不引入新的外部依赖

## Background & Context

当前代码中存在：
- [`_fallback_name`](file:///d:/Data/Trae/数仓AI助手-Trae1.0/backend/app/processors/field_processor.py#L849-L1172) 函数，使用预定义中文替换表，过于复杂且不可维护
- [`_try_split_and_match`](file:///d:/Data/Trae/数仓AI助手-Trae1.0/backend/app/processors/field_processor.py#L117-L172) 函数，使用 jieba 分词，但是是字段级处理
- 现在需要改为：先分词，词根级分组，词根级处理，最后拼接

## Functional Requirements

- **FR-1**: 对所有输入字段先通过 jieba 进行智能分词
- **FR-2**: 对所有分词结果进行词根级分组（去重）
- **FR-3**: 对所有词根优先匹配历史词根
- **FR-4**: 未匹配到的词根统一交由 LLM 处理，同时返回新词根列表
- **FR-5**: 使用翻译好的词根重新拼接回完整的字段名
- **FR-6**: 移除 `_fallback_name` 函数

## Non-Functional Requirements

- **NFR-1**: 保持现有 API 不变，向前兼容
- **NFR-2**: 保持表名处理流程不变
- **NFR-3**: 保持返回的数据结构不变

## Constraints

- **Technical**: 必须使用现有的代码结构，不要重写整个处理器
- **Business**: 用户现有功能保持不变，只优化内部实现
- **Dependencies**: jieba 已引入，无需新增依赖

## Assumptions

- jieba 的分词结果可以正确拆分中文业务术语
- 历史词根的数据结构保持不变
- LLM 调用接口不变

## Acceptance Criteria

### AC-1: jieba 智能分词
- **Given**: 有一组中文业务字段列表
- **When**: 对这些字段进行处理
- **Then**: 每个字段都被 jieba 正确分词为最小语义单元
- **Verification**: `programmatic`

### AC-2: 词根级分组
- **Given**: 所有字段的分词结果
- **When**: 对所有分词进行收集和归并
- **Then**: 所有分词进行去重，同一词根在多个字段中共用
- **Verification**: `programmatic`

### AC-3: 历史词根优先匹配
- **Given**: 有历史词根库
- **When**: 对所有分词进行匹配
- **Then**: 能够匹配到的直接使用历史词根
- **Verification**: `programmatic`

### AC-4: LLM 处理未匹配词根
- **Given**: 历史词根库中没有的分词
- **When**: 这些分词被发送给 LLM
- **Then**: LLM 返回对应的英文词根，并且可以作为新词根保存
- **Verification**: `programmatic`

### AC-5: 完整字段拼接
- **Given**: 翻译后的词根翻译结果和原始字段的分词结构
- **When**: 重新拼接成完整的英文字段名
- **Then**: 能够正确地将词根组合
- **Verification**: `programmatic`

### AC-6: `_fallback_name` 函数被移除
- **Given**: 优化后的代码
- **When**: 检查代码
- **Then**: `_fallback_name` 函数不存在
- **Verification**: `programmatic`

## Open Questions

- 无

