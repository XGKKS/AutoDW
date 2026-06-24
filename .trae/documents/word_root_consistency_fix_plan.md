# 词根一致性问题修复计划

## 问题分析

### 现象

用户反馈：同一中文词"维修"在不同表中被翻译成不同的英文：

* `repair_item_name` / 维修项目名称 → 全称 `repair`

* `rpr_iss_ord_no` / 维修领料单号 → 简称 `rpr`

* `maint_type_name` / 维修类型名称 → 简称 `maint`

用户要求匹配全称，但实际出现简称和全称混用。

### 根本原因

**关键问题**：`build_prompt_for_batch` 方法（第271-315行）的提示词有严重问题：

1. **硬编码优先使用缩写**：

   ```python
   # 第301行
   2. 优先使用缩写形式，每个词根不超过4个字母
   ```

   * 没有根据用户设置的 `root_match_priority` 调整

   * 无论用户选择"全称优先"还是"缩写优先"，都告诉LLM优先使用缩写

2. **没有传递历史词根给LLM**：

   * `batch` 中只包含 `chinese_name` 和 `suggested_type`

   * **LLM不知道哪些词根已存在，应该复用**

3. **导致的结果**：

   * LLM可能自己创造缩写（如 `rpr` 代替 `repair`）

   * 同一中文含义在不同批次产生不同的翻译

## 修复方案

### 方案设计

#### 用户反馈要点：

1. 提示词约束不够强，"优先使用"改成"**必须使用**"
2. 暂不传递历史词根给LLM（历史词根应该已经完成本地匹配了）
3. **长字段拆分匹配问题**："维修类型名称"这种长字段，当前不会拆分成多个词进行本地匹配

#### 修复方案：

**方案A（推荐）：长字段智能拆分本地匹配**
在发送LLM之前，将未匹配的完整字段拆分成多个词，逐一进行本地匹配：

1. 如果"维修类型名称"未匹配到历史词根
2. 拆分成 \["维修", "类型", "名称"]
3. 逐一匹配历史词根：   - "维修" → 匹配到 `repair`

   * "类型" → 匹配到 `type`   - "名称" → 匹配到 `name`
4. 如果所有子词都能匹配，则使用拆分组合：`repair_type_name`   - 如果有子词匹配失败，则仍发送到LLM处理

**方案B：强化LLM提示词**
将历史词根中的**相关关键词根**传递给LLM，明确要求必须使用：

1. 收集与当前批次相关的历史词根
2. 在提示词中列出这些词根
3. 将"优先使用"改成"**必须使用**"
4. 明确告诉LLM每个中文词应该翻译成什么

## 实施步骤

### 方案A：长字段智能拆分本地匹配（推荐）

#### 步骤1：修改 `split_into_batches` 方法

在第205-216行的匹配逻辑之后，添加长字段拆分匹配：

```python
# 对未匹配的字段，尝试拆分匹配
for chinese_name, field_list in list(unmatched_groups.items()):
    # 尝试拆分成多个词进行匹配
    parts = self._try_split_and_match(chinese_name)
    if parts:
        # 所有子词都匹配成功，组合使用
        english_name = '_'.join(parts)
        matched_fields[chinese_name] = (english_name, field_list[0].suggested_type)
        del unmatched_groups[chinese_name]
        logger.info(f"【字段级处理】✅ 拆分匹配成功: '{chinese_name}' -> '{english_name}'")
```

#### 步骤2：添加 `_try_split_and_match` 方法

新增拆分匹配逻辑：

```python
def _try_split_and_match(self, chinese_name):
    """尝试将中文名称拆分成多个词，逐一匹配历史词根"""
    # 常用单字词映射（来自历史词根）
    single_char_map = {...}  # 从 existing_root_map 构建
    
    # 尝试从长到短匹配子串
    parts = []
    remaining = chinese_name
    
    while remaining:
        matched = False
        # 先尝试两字词
        for length in [4, 3, 2]:
            if len(remaining) >= length:
                substring = remaining[:length]
                if substring in self.existing_root_map:
                    info = self.existing_root_map[substring]
                    root = info.get('abbr') or info.get('full')
                    parts.append(root)
                    remaining = remaining[length:]
                    matched = True
                    break
        if not matched:
            return None  # 拆分失败
    
    return parts if parts else None
```

### 方案B：强化LLM提示词（补充）

#### 步骤1：修改 `build_prompt_for_batch` 方法

* 将"优先使用"改成"**必须使用**"

* 添加相关历史词根列表

#### 步骤2：修改提示词内容

```python
prompt = f"""...
【已有关键词根 - 必须使用这些翻译】
{existing_roots}

【词根规则】
1. 字段名必须使用下划线分隔，全部小写
2. 必须使用【已有关键词根】中的翻译，禁止自创新词根
3. 同一中文含义必须使用相同的英文词根
4. ...
"""
```

### 建议：同时实施方案A和B

* 方案A解决本地匹配问题，减少对LLM的依赖

* 方案B作为兜底，确保LLM也遵循规则

## 文件修改

### backend/app/processors/field\_processor.py

#### 修改1：添加 `_try_split_and_match` 方法

新增拆分匹配方法，用于将长字段拆分成多个词进行本地匹配。

#### 修改2：修改 `split_into_batches` 方法

在第205-216行的匹配逻辑之后，添加长字段拆分匹配逻辑。

#### 修改3：修改 `build_prompt_for_batch` 方法

将"优先使用"改成"**必须使用**"，并添加历史词根提示。

### 预期效果

**修复前**：

* "维修类型名称" → 发送到LLM → 可能翻译成 `maint_type_name` 或 `repair_type_name`

* 不同批次结果不一致

**修复后（方案A）**：

* "维修类型名称" → 拆分匹配 → \["维修", "类型", "名称"] → 本地匹配 → `repair_type_name`

* 本地匹配确保一致性

**修复后（方案B）**：

* LLM收到提示词："维修"必须翻译成 `repair`，禁止自创新词根

* 即使发送到LLM，也能保证一致性

## 验证步骤

### 测试用例

| 场景     | 输入                  | 预期输出               | 验证方式  |
| ------ | ------------------- | ------------------ | ----- |
| 拆分匹配   | "维修类型名称"（历史词根有"维修"） | `repair_type_name` | 单元测试  |
| 拆分匹配失败 | "新字段X"（词根库没有）       | 发送到LLM处理           | 单元测试  |
| 跨表一致   | "维修项目"、"维修类型"       | 都用 `repair_*`      | 集成测试  |
| LLM提示词 | "维修"                | 必须翻译成 `repair`     | 提示词审查 |

### 验证方法

1. **单元测试**：

   * 运行 `python backend/test_split_match.py`

   * 验证"维修类型名称"拆分匹配正确

2. **集成测试**：

   * 使用包含"维修"字段的Excel文件测试

   * 验证不同表中的"维修"翻译一致

3. **提示词审查**：

   * 检查生成的提示词中是否包含"必须使用"

   * 检查历史词根是否正确传递

