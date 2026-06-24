# 中文字段命名问题修复计划

## 问题分析

### 问题1：中文字段命名
生成的DDL中出现了 `工_单_number`、`原_工_单_number` 等混合中英文的字段名。

**根本原因**：`_fallback_name` 方法在处理中文时，单个中文字符（如"工"、"单"）没有对应的英文映射，导致直接保留中文并添加下划线。

### 问题2：新词根拆分
新词根应该拆分成单个单词，而不是词组。例如"总装计划下线时间"应该拆分成"总装"、"计划"、"下线"、"时间"。

**根本原因**：新词根提取时直接使用了完整的中文字段名作为词根，没有进行拆分。

## 修复方案

### 方案1：修复中文字段命名
在 `_fallback_name` 方法中，当单个中文字符没有匹配时：
1. 使用拼音首字母代替
2. 添加更多常用中文词汇到 replacements 映射表

### 方案2：修复新词根拆分
修改新词根提取逻辑：
1. 将复合词拆分成单个词
2. 对于每个拆分后的词，如果不在历史词根中，作为新词根记录

## 实施步骤

### 步骤1：修改 `_fallback_name` 方法
- 添加拼音首字母映射
- 添加更多常用中文词汇

### 步骤2：修改新词根提取逻辑
- 在 `generate_all_ddl` 方法中，将中文字段名拆分成单个词
- 每个拆分后的词作为独立的新词根

## 文件修改

### backend/app/processors/field_processor.py

#### 修改1：扩展 `_fallback_name` 方法的 replacements
```python
replacements = {
    # 现有映射...
    '工': 'work',
    '单': 'order',
    '原': 'original',
    '预': 'pre',
    '约': 'appointment',
    '估': 'estimate',
    '价': 'price',
    '备': 'spare',
    '件': 'part',
    '销': 'sale',
    '售': 'sell',
    '出': 'out',
    '险': 'risk',
    '理': 'handle',
    '赔': 'compensate',
    '索': 'claim',
    '保': 'insurance',
    '养': 'maintain',
    '收': 'receive',
    '费': 'fee',
    '区': 'area',
    '分': 'distinguish',
    '代': 'code',
    '码': 'code',
    '公': 'company',
    '司': 'company',
    '状': 'status',
    '车': 'car',
    '主': 'owner',
    '编': 'number',
    '性': 'nature',
    '质': 'quality',
    '牌': 'plate',
    'vin': 'vin',
    '发': 'engine',
    '动': 'engine',
    '机': 'machine',
    '城': 'city',
    '市': 'city',
    '包': 'package',
    '工': 'work',
    '付': 'pay',
    '费': 'fee',
    '故': 'fault',
    '障': 'fault',
    '描': 'describe',
    '述': 'describe',
    '洗': 'wash',
    '类': 'category',
    '别': 'category',
    '供': 'supply',
    '应': 'supply',
    '商': 'supplier',
    '提': 'submit',
    '报': 'report',
    '三': 'three',
    '保': 'guarantee',
    '预': 'expect',
    '开': 'start',
    '竣': 'complete',
    '验': 'inspect',
    '收': 'accept',
    '人': 'person',
    '员': 'person',
    '送': 'deliver',
    '修': 'repair',
    '性': 'gender',
    '别': 'gender',
    '电': 'phone',
    '话': 'phone',
    '驾': 'driver',
    '驶': 'drive',
    '员': 'member',
    '员': 'member',
    '交': 'deliver',
    '标': 'flag',
    '识': 'flag',
    '试': 'test',
    '员': 'member',
    '结': 'settle',
    '算': 'settle',
    '案': 'case',
    '旧': 'old',
    '处': 'handle',
    '理': 'handle',
    '备': 'remark',
    '注': 'remark',
    '进': 'enter',
    '厂': 'factory',
    '里': 'mileage',
    '程': 'mileage',
    '行': 'drive',
    '出': 'exit',
    '换': 'change',
    '表': 'meter',
    '累': 'total',
    '计': 'total',
    '单': 'unit',
    '价': 'price',
    '应': 'receivable',
    '收': 'receive',
    '材': 'material',
    '料': 'material',
    '附': 'extra',
    '加': 'add',
    '辅': 'auxiliary',
    '管': 'manage',
    '理': 'manage',
    '金': 'amount',
    '额': 'amount',
    '质': 'quality',
    '检': 'inspect',
    '快': 'quick',
    '延': 'delay',
    '期': 'delay',
}
```

#### 修改2：添加拼音首字母映射作为兜底
```python
pinyin_map = {
    '工': 'g',
    '单': 'd',
    '原': 'y',
    '预': 'y',
    '约': 'y',
    '估': 'g',
    '价': 'j',
    '备': 'b',
    '件': 'j',
    '销': 'x',
    '售': 's',
    '出': 'c',
    '险': 'x',
    '理': 'l',
    '赔': 'p',
    '索': 's',
    '保': 'b',
    '养': 'y',
    '收': 's',
    '费': 'f',
    '区': 'q',
    '分': 'f',
    '代': 'd',
    '码': 'm',
    '公': 'g',
    '司': 's',
    '状': 'z',
    '车': 'c',
    '主': 'z',
    '编': 'b',
    '性': 'x',
    '质': 'z',
    '牌': 'p',
    '发': 'f',
    '动': 'd',
    '机': 'j',
    '城': 'c',
    '市': 's',
    '包': 'b',
    '付': 'f',
    '故': 'g',
    '障': 'z',
    '描': 'm',
    '述': 's',
    '洗': 'x',
    '类': 'l',
    '别': 'b',
    '供': 'g',
    '应': 'y',
    '商': 's',
    '提': 't',
    '报': 'b',
    '三': 's',
    '开': 'k',
    '竣': 'j',
    '验': 'y',
    '人': 'r',
    '员': 'y',
    '送': 's',
    '修': 'x',
    '电': 'd',
    '话': 'h',
    '驾': 'j',
    '驶': 's',
    '交': 'j',
    '标': 'b',
    '识': 's',
    '试': 's',
    '结': 'j',
    '算': 's',
    '案': 'a',
    '旧': 'j',
    '处': 'c',
    '理': 'l',
    '备': 'b',
    '注': 'z',
    '进': 'j',
    '厂': 'c',
    '里': 'l',
    '程': 'c',
    '行': 'x',
    '出': 'c',
    '换': 'h',
    '表': 'b',
    '累': 'l',
    '计': 'j',
    '单': 'd',
    '价': 'j',
    '应': 'y',
    '收': 's',
    '材': 'c',
    '料': 'l',
    '附': 'f',
    '加': 'j',
    '辅': 'f',
    '管': 'g',
    '理': 'l',
    '金': 'j',
    '额': 'e',
    '质': 'z',
    '检': 'j',
    '快': 'k',
    '延': 'y',
    '期': 'q',
}
```

#### 修改3：修改新词根提取逻辑
在 `generate_all_ddl` 方法中，将中文字段名拆分成单个词后作为新词根。

## 验证步骤

### 测试用例

| 场景 | 输入 | 预期输出 |
|------|------|----------|
| 中文单字 | "工" | "work" |
| 中文单字 | "单" | "order" |
| 中文词组 | "工单" | "work_order" |
| 中文长字段 | "工单号" | "work_order_number" |
| 新词根拆分 | "总装计划下线时间" | ["总装", "计划", "下线", "时间"] |

### 验证方法

1. 运行单元测试验证字段翻译
2. 使用包含中文字段的Excel文件测试批量建表
3. 检查生成的DDL中是否还存在中文字段名