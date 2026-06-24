# 混合模式实施计划

## 一、计划概述

### 1.1 目标
将现有的"分词→匹配→翻译→拼接"架构优化为**混合模式**，按中文ASCII排序分批处理，提高字段名翻译的准确性。

### 1.2 优化要点
1. **分层处理**：按匹配程度分为三层处理
2. **中文排序**：按中文ASCII排序后再分批
3. **上下文增强**：为LLM提供完整上下文
4. **词根分解**：Layer 3返回词根分解，保证词根库正确保存

---

## 二、新架构设计

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 混合模式架构：三层分层处理                                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ Layer 0: jieba分词                                                │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                              ↓                                          │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ Layer 1: 完全匹配（无需LLM）                                        │ │
│  │ 所有词根都命中历史词根 → 直接拼接                                     │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                              ↓                                          │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ Layer 2: 部分匹配（LLM翻译词根）                                    │ │
│  │ 部分词根未命中 → LLM翻译 → 拼接                                      │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                              ↓                                          │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ Layer 3: 完全未匹配（LLM设计字段名 + 词根分解）                     │ │
│  │ 所有词根都未命中 → LLM设计字段名 + 返回词根分解                      │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 三、分批策略

### 3.1 中文ASCII排序

```python
def create_batches_by_ascii_order(roots, batch_size=50):
    """
    按中文ASCII排序创建批次
    中文按Unicode编码排序，相近语义的词根会相邻排列
    """
    # 中文ASCII排序（按Unicode编码）
    sorted_roots = sorted(roots)
    
    # 分批
    batches = []
    for i in range(0, len(sorted_roots), batch_size):
        batch = sorted_roots[i:i + batch_size]
        batches.append(batch)
    
    return batches
```

**示例**：
```
原始词根: [金额, 是否, 名称, 状态, 数量, 类型, ID, 日期, 标识]
ASCII排序: [ID, 标识, 日期, 金额, 名称, 数量, 类型, 状态, 是否]
分批(每批50): [["ID", "标识", "日期", "金额", "名称", "数量", "类型", "状态", "是否"]]
```

---

## 四、Layer处理详细设计

### 4.1 Layer 1: 完全匹配

```python
def process_layer1_fields(layer1_fields, existing_root_map):
    """所有词根都命中历史词根，直接拼接"""
    results = {}
    for chinese_name, roots in layer1_fields.items():
        english_parts = []
        for root in roots:
            translation = existing_root_map[root]
            english_parts.append(translation.get('full') or translation.get('abbr', root))
        results[chinese_name] = '_'.join(english_parts)
    return results
```

### 4.2 Layer 2: 部分匹配

```python
def process_layer2_fields(layer2_fields, existing_root_map, llm_translations):
    """未匹配词根使用LLM翻译，然后拼接"""
    results = {}
    for chinese_name, roots in layer2_fields.items():
        english_parts = []
        for root in roots:
            if root in existing_root_map:
                translation = existing_root_map[root]
                english_parts.append(translation.get('full') or translation.get('abbr', root))
            elif root in llm_translations:
                english_parts.append(llm_translations[root])
            else:
                english_parts.append(root)
        results[chinese_name] = '_'.join(english_parts)
    return results
```

### 4.3 Layer 3: 完全未匹配

```python
def process_layer3_fields(layer3_fields, llm_designs):
    """LLM直接设计字段名，同时返回词根分解"""
    results = {}
    new_roots = {}
    for chinese_name, roots in layer3_fields.items():
        if chinese_name in llm_designs:
            design = llm_designs[chinese_name]
            results[chinese_name] = design['field_name']
            for cn_root, en_root in design['roots'].items():
                if cn_root not in new_roots:
                    new_roots[cn_root] = en_root
    return results, new_roots
```

---

## 五、LLM调用设计

### 5.1 Layer 2: 词根翻译提示词

```python
def build_layer2_prompt(unmatched_roots, matched_context, standards):
    """按中文ASCII排序，提示词包含已匹配词根作为上下文"""
    sorted_roots = sorted(unmatched_roots)
    roots_text = "\n".join(sorted_roots)
    
    matched_info = "\n".join([f"- {cn} → {en}" for cn, en in sorted(matched_context.items())])
    
    return f"""请为以下中文业务词根生成英文翻译：

【待翻译词根列表】（已按中文排序）
{roots_text}

【已匹配词根（参考）】
{matched_info if matched_info else "无"}

【开发规范】
{standards}

【翻译要求】
1. 基础词根必须使用规范中的标准翻译：
   - "是否"类 → "is"
   - "状态"类 → "status"
   - "类型"类 → "type"
   - "名称"类 → "name"
   - "数量"类 → "num"
   - "金额"类 → "amt"
   - "日期"类 → "date"
   - "时间"类 → "time"
   - "ID"类 → "id"
2. 词根必须全部小写

请按以下格式输出：
中文词根:英文词根"""
```

### 5.2 Layer 3: 字段设计提示词

```python
def build_layer3_prompt(unmatched_fields, standards):
    """LLM直接设计字段名，同时返回词根分解"""
    fields_text = "\n".join([
        f"{i+1}. \"{field['chinese_name']}\" - 分词: {field['roots']}"
        for i, field in enumerate(unmatched_fields)
    ])
    
    return f"""请为以下中文字段设计英文字段名，并同时返回词根分解：

{fields_text}

【开发规范】
{standards}

【输出格式】
中文字段名:英文字段名|中文词根1:英文词根1,中文词根2:英文词根2

【输出示例】
特殊标识:special_id|特殊:special,标识:id"""
```

### 5.3 解析Layer 3输出

```python
def parse_layer3_output(output_lines):
    """解析Layer 3的LLM输出"""
    results = {}
    for line in output_lines:
        line = line.strip()
        if not line or ':' not in line:
            continue
        try:
            parts = line.split('|')
            field_part = parts[0]
            root_part = parts[1] if len(parts) > 1 else ""
            
            chinese_field, english_field = field_part.split(':', 1)
            
            roots = {}
            if root_part:
                for root_pair in root_part.split(','):
                    if ':' in root_pair:
                        cn_root, en_root = root_pair.split(':', 1)
                        roots[cn_root.strip()] = en_root.strip()
            
            results[chinese_field.strip()] = {
                "field_name": english_field.strip(),
                "roots": roots
            }
        except Exception as e:
            logger.warning(f"解析Layer3输出失败: {line}")
    return results
```

---

## 六、完整流程

```python
def process_fields_hybrid_mode(self, groups):
    """混合模式主流程"""
    # Step 0: jieba分词
    field_tokenization, unique_roots = self.tokenize_all_fields_root_level(groups)
    
    # Step 1: 历史词根匹配
    matched_roots, unmatched_roots = self.match_roots_against_history(unique_roots)
    
    # 分类字段
    layer1_fields = {}
    layer2_fields = {}
    layer3_fields = {}
    
    for chinese_name, roots in field_tokenization.items():
        matched = [r for r in roots if r in matched_roots]
        if len(matched) == len(roots):
            layer1_fields[chinese_name] = roots
        elif len(matched) > 0:
            layer2_fields[chinese_name] = roots
        else:
            layer3_fields[chinese_name] = roots
    
    # Layer 1 - 完全匹配
    layer1_results = self.process_layer1_fields(layer1_fields, matched_roots)
    
    # Layer 2 - 部分匹配（按中文排序分批）
    layer2_unmatched_roots = set()
    for roots in layer2_fields.values():
        layer2_unmatched_roots.update([r for r in roots if r not in matched_roots])
    
    if layer2_unmatched_roots:
        batches = create_batches_by_ascii_order(list(layer2_unmatched_roots))
        llm_translations = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._translate_roots_batch, batch): batch for batch in batches}
            for future in as_completed(futures):
                llm_translations.update(future.result())
        layer2_results = self.process_layer2_fields(layer2_fields, matched_roots, llm_translations)
    else:
        layer2_results = {}
    
    # Layer 3 - 完全未匹配
    if layer3_fields:
        layer3_data = [{"chinese_name": cn, "roots": roots} for cn, roots in layer3_fields.items()]
        llm_designs = {}
        new_roots = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for i in range(0, len(layer3_data), 20):
                batch = layer3_data[i:i+20]
                result = executor.submit(self._design_fields_batch, batch).result()
                for cn, design in result.items():
                    llm_designs[cn] = design
                    new_roots.update(design['roots'])
        layer3_results, batch_new_roots = self.process_layer3_fields(layer3_fields, llm_designs)
        new_roots.update(batch_new_roots)
    else:
        layer3_results = {}
        new_roots = {}
    
    # 合并结果
    all_results = {**layer1_results, **layer2_results, **layer3_results}
    
    field_mapping = {}
    for chinese_name, english_name in all_results.items():
        field_list = groups[chinese_name]
        field_type = field_list[0].suggested_type if field_list else 'VARCHAR(255)'
        field_mapping[chinese_name] = (english_name, field_type)
    
    stats = {
        'layer1_count': len(layer1_fields),
        'layer2_count': len(layer2_fields),
        'layer3_count': len(layer3_fields),
        'new_roots_count': len(new_roots)
    }
    
    return field_mapping, stats, new_roots
```

---

## 七、文件修改清单

| 文件 | 修改内容 |
|------|---------|
| `field_processor.py` | 新增 `create_batches_by_ascii_order` 方法 |
| `field_processor.py` | 新增 `process_layer1_fields` 方法 |
| `field_processor.py` | 新增 `process_layer2_fields` 方法 |
| `field_processor.py` | 新增 `process_layer3_fields` 方法 |
| `field_processor.py` | 新增 `parse_layer3_output` 方法 |
| `field_processor.py` | 重构 `_translate_roots_batch` 提示词 |
| `field_processor.py` | 新增 `_design_fields_batch` 方法 |
| `field_processor.py` | 重构 `process_fields_root_level` 为混合模式 |

---

## 八、实施步骤

1. 新增基础方法（`create_batches_by_ascii_order`、Layer处理方法）
2. 重构LLM调用（提示词、字段设计）
3. 集成测试

---

## 九、预期效果

| 指标 | 当前 | 优化后 |
|------|------|--------|
| "是否"翻译准确率 | ~70% | ~99% |
| 翻译一致性 | 低 | 中（按中文排序） |
| 新词根可复用性 | 低 | 高（词根分解） |
