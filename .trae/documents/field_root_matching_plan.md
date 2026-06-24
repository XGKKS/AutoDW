# 字段级处理流程 - 历史词根匹配功能实现计划

## 一、需求分析

### 1.1 需求描述
在字段级处理流程中，阶段3分批处理时，加入历史词根匹配功能：
- 根据词根匹配优先级（full/abbr）推荐对应的缩写或全称
- 只将匹配到的词根传递给大模型，而非全部词根
- 确保本次建表与历史建表词根的一致性

### 1.2 核心目标
- **一致性保证**：相同中文含义使用相同的英文词根
- **减少LLM调用**：优先使用历史词根，减少对大模型的依赖
- **灵活配置**：支持词根匹配优先级配置

### 1.3 功能位置
字段级处理流程 → 阶段3：分批处理

---

## 二、当前代码分析

### 2.1 当前字段处理器结构
```python
class FieldProcessor:
    def __init__(self, ..., word_roots: list = None):
        self.word_roots = word_roots or []
        # 已构建历史词根映射表
        self.existing_root_map = {}  # 中文 -> {'full': xxx, 'abbr': xxx, 'type': xxx}
```

### 2.2 问题分析
当前字段处理器虽然接收了 `word_roots` 参数并构建了映射表，但在分批处理时：
- ✅ 已有历史词根映射表
- ❌ 未在字段分组时使用历史词根匹配
- ❌ 未根据优先级选择缩写或全称
- ❌ 未将匹配到的词根传递给LLM

---

## 三、实现方案

### 3.1 核心流程设计

```
字段分组 → 历史词根匹配 → 生成提示词 → 调用LLM → 合并结果
     ↓              ↓
  按中文分组    匹配历史词根
                ↓
        根据优先级选择
        (full/abbr)
                ↓
        已匹配的字段直接使用历史词根
        未匹配的字段提交给LLM
```

### 3.2 实现步骤

#### 步骤1：添加词根匹配优先级参数
- 修改 `FieldProcessor.__init__` 添加 `root_match_priority` 参数

#### 步骤2：实现历史词根匹配方法
- 添加 `match_existing_root(chinese_name)` 方法
- 根据优先级返回对应的英文词根

#### 步骤3：修改分批处理逻辑
- 在 `group_fields_by_chinese` 后添加历史词根匹配
- 将字段分为：已匹配字段 + 未匹配字段
- 已匹配字段直接加入结果，未匹配字段提交给LLM

#### 步骤4：修改提示词构建
- 只将未匹配的字段传递给LLM
- 在提示词中包含已匹配的词根作为参考

#### 步骤5：修改调用处（main.py）
- 传递 `word_roots` 和 `root_match_priority` 参数

---

## 四、文件修改清单

| 文件路径 | 修改内容 | 说明 |
|---------|---------|------|
| `app/processors/field_processor.py` | 添加 `root_match_priority` 参数 | 支持优先级配置 |
| `app/processors/field_processor.py` | 添加 `match_existing_root()` 方法 | 历史词根匹配逻辑 |
| `app/processors/field_processor.py` | 修改 `build_field_mapping()` | 整合匹配逻辑 |
| `app/processors/field_processor.py` | 修改 `build_prompt_for_batch()` | 只传递未匹配字段 |
| `app/main.py` | 修改 FieldProcessor 调用 | 传递 word_roots 和 root_match_priority |

---

## 五、关键实现逻辑

### 5.1 历史词根匹配方法
```python
def match_existing_root(self, chinese_name: str) -> Optional[str]:
    """
    根据词根匹配优先级查找历史词根
    :param chinese_name: 中文字段名
    :return: 匹配到的英文词根，未匹配返回 None
    """
    if chinese_name in self.existing_root_map:
        root_info = self.existing_root_map[chinese_name]
        if self.root_match_priority == 'abbr' and root_info['abbr']:
            return root_info['abbr']
        elif root_info['full']:
            return root_info['full']
    return None
```

### 5.2 字段处理流程
```python
def process_fields_with_history_roots(self, all_fields):
    # 1. 按中文分组
    groups = self.group_fields_by_chinese(all_fields)
    
    # 2. 分离已匹配和未匹配字段
    matched_fields = {}  # 中文 -> 英文词根
    unmatched_fields = []  # 需要提交给LLM的字段
    
    for chinese_name, field_list in groups.items():
        matched_root = self.match_existing_root(chinese_name)
        if matched_root:
            matched_fields[chinese_name] = matched_root
        else:
            unmatched_fields.extend(field_list)
    
    # 3. 未匹配字段分批处理
    if unmatched_fields:
        # 继续使用LLM处理未匹配字段
        pass
    
    return matched_fields
```

---

## 六、测试验证

### 6.1 测试场景

| 场景 | 描述 | 预期结果 |
|------|------|---------|
| 完全匹配 | 所有字段都有历史词根 | 不调用LLM，直接使用历史词根 |
| 部分匹配 | 部分字段有历史词根 | 已匹配字段直接使用，未匹配字段调用LLM |
| 完全未匹配 | 所有字段都无历史词根 | 全部调用LLM处理 |
| 优先级测试(full) | 设置优先全称 | 返回全称词根 |
| 优先级测试(abbr) | 设置优先缩写 | 返回缩写词根 |

### 6.2 验证要点

1. 检查 `existing_root_map` 是否正确构建
2. 检查已匹配字段是否跳过LLM调用
3. 检查优先级配置是否生效
4. 检查最终生成的DDL中相同中文使用相同词根

---

## 七、风险评估

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| 历史词根数据不一致 | 中 | 在校验阶段检测并修正 |
| 中文名称匹配失败 | 低 | 使用模糊匹配或相似度匹配 |
| 性能影响 | 低 | 预构建映射表，O(1)查找 |
