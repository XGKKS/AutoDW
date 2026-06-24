# 新词根重复问题修复计划

## 问题描述

当字段列表中同时存在"商品名称"、"商品"、"名称"等具有包含关系的字段时，新词根列表会同时出现这三个词根，导致词根冗余。

### 问题原因

1. jieba 默认使用精准模式分词，"商品名称"被当作一个完整词
2. "商品"和"名称"各自独立分词
3. 分词后没有进行包含关系检查

### 测试验证

```python
import jieba
print('商品名称:', jieba.lcut('商品名称', cut_all=False))  # ['商品名称']
print('商品:', jieba.lcut('商品', cut_all=False))          # ['商品']
print('名称:', jieba.lcut('名称', cut_all=False))          # ['名称']
```

---

## 修复方案

### 修改文件

- `app/processors/field_processor.py`

### 修改位置

`tokenize_all_fields_root_level` 方法（第 585-615 行）

### 修复逻辑

在分词去重后，增加包含关系检查：

```python
def tokenize_all_fields_root_level(self, groups):
    # ... 现有分词逻辑 ...
    
    # 去重
    unique_roots = list(dict.fromkeys(all_roots))
    
    # 新增：移除被其他词根包含的词根
    # 例如：如果同时有"商品名称"、"商品"、"名称"，移除"商品"和"名称"
    filtered_roots = []
    for root in unique_roots:
        is_substring = False
        for other in unique_roots:
            if root != other and root in other:
                is_substring = True
                break
        if not is_substring:
            filtered_roots.append(root)
    
    unique_roots = filtered_roots
    
    return field_tokenization, unique_roots
```

---

## 预期效果

### 修复前

| 输入字段 | 分词结果 | 新词根 |
|---------|---------|--------|
| 商品名称 | ['商品名称'] | 商品名称 |
| 商品 | ['商品'] | 商品 |
| 名称 | ['名称'] | 名称 |

**新词根列表**：["商品名称", "商品", "名称"]

### 修复后

| 输入字段 | 分词结果 | 新词根 |
|---------|---------|--------|
| 商品名称 | ['商品名称'] | 商品名称 |
| 商品 | ['商品'] | （被移除） |
| 名称 | ['名称'] | （被移除） |

**新词根列表**：["商品名称"]

---

## 风险评估

| 风险 | 描述 | 解决方案 |
|-----|------|---------|
| 误删风险 | 可能误删应该保留的词根（如"状态"在其他字段中单独使用） | 只有当词根被其他词根完全包含时才移除 |
| 性能影响 | 增加 O(n²) 复杂度的包含检查 | 词根数量通常较少（几十到几百），影响可接受 |

---

## 实施步骤

1. 修改 `field_processor.py` 中的 `tokenize_all_fields_root_level` 方法
2. 添加包含关系检查逻辑
3. 测试验证修复效果
4. 运行完整测试确保没有引入新问题

---

## 测试用例

```python
# 测试1：包含关系去重
groups = {
    '商品名称': [...],
    '商品': [...],
    '名称': [...]
}
# 预期：新词根只包含"商品名称"

# 测试2：无包含关系的正常情况
groups = {
    '订单状态': [...],
    '支付状态': [...],
    '状态': [...]
}
# 预期：新词根包含"订单状态"、"支付状态"、"状态"（因为没有一个词根完全包含另一个）
```
