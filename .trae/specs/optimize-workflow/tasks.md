# 优化字段翻译流程 - 实施计划

## [ ] Task 1: 设计新的流程数据结构
- **Priority**: P0
- **Depends On**: None
- **Description**:
  - 设计用于存储字段分词结构的数据结构
  - 设计词根翻译的缓存和映射结构
  - 确保与现有代码接口兼容
- **Acceptance Criteria Addressed**: [FR-1, FR-2, FR-5]
- **Test Requirements**:
  - `programmatic` TR-1.1: 可以正确存储和恢复字段的分词结构
  - `programmatic` TR-1.2: 词根映射结构支持中英文互查
- **Notes**:

## [ ] Task 2: 实现 jieba 分词和词根分组功能
- **Priority**: P0
- **Depends On**: Task 1
- **Description**:
  - 对所有输入字段进行 jieba 分词
  - 收集所有分词结果并去重
  - 构建词根到字段的映射关系
- **Acceptance Criteria Addressed**: [FR-1, FR-2]
- **Test Requirements**:
  - `programmatic` TR-2.1: jieba 可以正确拆分中文业务术语
  - `programmatic` TR-2.2: 所有分词正确去重
  - `programmatic` TR-2.3: 建立分词与字段的关系索引
- **Notes**: 重用现有 jieba 初始化代码

## [ ] Task 3: 实现历史词根优先匹配
- **Priority**: P0
- **Depends On**: Task 2
- **Description**:
  - 对所有分词优先匹配历史词根
  - 区分匹配到和未匹配到的词根
- **Acceptance Criteria Addressed**: [FR-3]
- **Test Requirements**:
  - `programmatic` TR-3.1: 历史词根匹配逻辑正确
  - `programmatic` TR-3.2: 正确区分已匹配和未匹配词根
- **Notes**: 重用现有 `match_existing_root` 逻辑

## [ ] Task 4: 实现 LLM 处理未匹配词根
- **Priority**: P0
- **Depends On**: Task 3
- **Description**:
  - 把未匹配到的词根交给 LLM 翻译
  - 修改提示词，让 LLM 返回词根级翻译而不是字段级翻译
  - 保存返回的新词根
- **Acceptance Criteria Addressed**: [FR-4]
- **Test Requirements**:
  - `programmatic` TR-4.1: 提示词正确，只返回词根级翻译
  - `programmatic` TR-4.2: LLM 返回的结果被正确解析
  - `programmatic` TR-4.3: 新词根可以被正确保存
- **Notes**: 需要修改 `build_prompt_for_batch` 函数

## [ ] Task 5: 实现词根拼接回完整字段名
- **Priority**: P0
- **Depends On**: Task 4
- **Description**:
  - 使用已翻译的词根
  - 按照原始分词结构重新拼接成完整字段名
- **Acceptance Criteria Addressed**: [FR-5]
- **Test Requirements**:
  - `programmatic` TR-5.1: 词根拼接正确
  - `programmatic` TR-5.2: 特殊字符处理正确
- **Notes**:

## [ ] Task 6: 整合到现有处理流程
- **Priority**: P0
- **Depends On**: Task 5
- **Description**:
  - 修改 `split_into_batches` 或相关主流程
  - 保持现有 API 接口不变
  - 保持返回的数据结构不变
- **Acceptance Criteria Addressed**: [FR-1, FR-2, FR-3, FR-4, FR-5]
- **Test Requirements**:
  - `programmatic` TR-6.1: 现有单元测试通过
  - `programmatic` TR-6.2: API 调用返回格式不变
  - `human-judgement` TR-6.3: 整体流程运行正常
- **Notes**: 向后兼容是关键

## [ ] Task 7: 移除 `_fallback_name` 函数
- **Priority**: P1
- **Depends On**: Task 6
- **Description**:
  - 完全删除 `_fallback_name` 函数
  - 删除相关的预定义中文替换表
  - 清理不再使用的代码
- **Acceptance Criteria Addressed**: [FR-6]
- **Test Requirements**:
  - `programmatic` TR-7.1: `_fallback_name` 函数被彻底删除
  - `programmatic` TR-7.2: 所有相关调用被清理
- **Notes**: 确保没有其他地方在调用

