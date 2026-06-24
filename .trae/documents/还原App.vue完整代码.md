# 新词根预览区域不显示问题排查计划

## 问题描述

用户反馈：历史词根清空后，单一建表创建新表时，所有字段都是新词根，但新词根预览区域没有显示任何内容。

## 数据流分析

### 1. 前端请求流程

```
generateDDL() 
  → formatHistoryRoots() → 生成历史词根文本
  → axios.post('/api/generate-ddl', { word_roots_input: { content: ... } })
  → 接收响应 → 更新 singleNewRoots.value
```

### 2. 后端处理流程

```
/api/generate-ddl
  → 解析 word_roots_input.content（如果非空）
  → filter_and_prepare_roots() → 从文件加载词根
  → 生成提示词（包含【新词根扩展】要求）
  → 调用 LLM
  → extract_new_roots_from_response() → 提取新词根
  → 返回响应（包含 extracted_roots）
```

### 3. 关键函数 `extract_new_roots_from_response()` 逻辑

```python
def extract_new_roots_from_response(content: str, existing_roots: list) -> list:
    if '【新词根】' not in content:
        return []  # 如果没有标记，直接返回空
    # ... 解析标记后的内容
```

## 可能的问题点

### 问题1：LLM 没有输出【新词根】标记

* 当历史词根为空时，提示词中的【词根参考】为"无"

* LLM 可能没有理解需要输出新词根标记

### 问题2：提示词不够明确

* 虽然提示词包含【新词根扩展】要求，但可能不够强调

### 问题3：前端没有传递历史词根

* 前端 `word_roots_input.content` 传递的是 `formatHistoryRoots()` 的结果

* 当历史词根为空时，传递空字符串

### 问题4：后端没有正确提取新词根

* `extract_new_roots_from_response()` 依赖 LLM 输出 `【新词根】` 标记

## 排查步骤

### 步骤1：添加调试日志（前端）

在 `generateDDL` 函数中添加日志，查看后端返回的响应内容。

### 步骤2：检查后端日志

查看后端日志，确认：

* LLM 请求是否成功

* LLM 响应内容是否包含【新词根】标记

* `extract_new_roots_from_response()` 的执行结果

### 步骤3：增强提示词

修改提示词，更加明确地要求 LLM 输出新词根标记。

### 步骤4：测试验证

清空历史词根，创建新表，检查新词根是否显示。

## 修改方案

### 修改1：前端添加调试日志

在 `generateDDL` 函数中添加 console.log 打印响应数据。

### 修改2：后端增强提示词

在 USER\_PROMPT\_TEMPLATE 中增加更明确的新词根输出要求。

### 修改3：确保前端正确传递历史词根

确认 `formatHistoryRoots()` 函数正常工作。

## 文件修改清单

| 文件                   | 修改内容       |
| -------------------- | ---------- |
| frontend/src/App.vue | 添加调试日志     |
| backend/app/main.py  | 增强提示词，添加日志 |

## 风险评估

| 风险            | 影响         | 缓解措施          |
| ------------- | ---------- | ------------- |
| 提示词修改可能影响其他功能 | LLM 响应格式变化 | 测试所有功能        |
| 日志过多影响性能      | 生产环境日志膨胀   | 使用 DEBUG 级别控制 |

## 验证标准

1. 清空历史词根后创建新表，新词根预览区域显示新词根
2. 新词根数量与表字段数量匹配
3. 保存新词根功能正常工作

