# 统一校验流程优化计划

## 一、问题分析

### 当前流程问题

当前统一校验流程在修正阶段存在以下问题：

1. **传入内容过多**：修正时传入整个批次所有表的完整DDL，上下文过大
2. **效率低下**：LLM需要处理大量无关内容
3. **准确性问题**：过多的上下文可能导致LLM忽略关键问题

### 用户建议的优化方案

```
阶段1: 检查阶段
  → 按表传入批次完整的DDL进行校验

阶段2: 修正阶段  
  → 仅传入错误字段和错误的英文字段建表语句
  → 给出针对性的LLM修正提示词

阶段3: 重组阶段
  → 将修正后的字段重组回完整DDL
```

---

## 二、优化设计

### 2.1 架构设计

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 阶段1: 检查阶段                                                        │
│ ┌─────────────────────────────────────────────────────────────────┐    │
│ │ 输入: 批次完整DDL {table_name: ddl}                           │    │
│ │ 处理: UnifiedValidator.validate_batch()                      │    │
│ │ 输出: 违规列表 {table_name: [violations]}                    │    │
│ └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                         │
│ ┌─────────────────────────────────────────────────────────────────┐    │
│ 阶段2: 提取错误字段                                                 │    │
│ │ 输入: 违规列表 + 原始DDL                                      │    │
│ │ 处理: 提取错误字段信息                                        │    │
│ │ 输出: {table_name: {field_name: {error_info, current_value}}} │    │
│ └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                         │
│ ┌─────────────────────────────────────────────────────────────────┐    │
│ 阶段3: LLM修正阶段                                                  │    │
│ │ 输入: 错误字段信息 + 可用词根                                  │    │
│ │ 处理: 生成针对性提示词 → 调用LLM                              │    │
│ │ 输出: 修正后的字段映射                                        │    │
│ └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                         │
│ ┌─────────────────────────────────────────────────────────────────┐    │
│ 阶段4: DDL重组阶段                                                  │    │
│ │ 输入: 原始DDL + 修正映射                                      │    │
│ │ 处理: 替换错误字段的英文名称                                   │    │
│ │ 输出: 修正后的完整DDL                                         │    │
│ └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 关键数据结构

```python
# 错误字段信息结构
error_fields = {
    "table_name": {
        "field_name": {
            "comment": "中文注释",           # 字段中文含义
            "current_name": "current_name",  # 当前错误的英文字段名
            "violations": [                 # 违规信息列表
                {
                    "rule": "规则名称",
                    "level": "error/warning",
                    "message": "错误描述"
                }
            ]
        }
    }
}

# 修正结果结构
fix_results = {
    "table_name": {
        "field_name": "corrected_name"  # 修正后的英文字段名
    }
}
```

---

## 三、修改方案

### 3.1 修改 `UnifiedValidator` 类

**新增方法**：

| 方法 | 作用 | 参数 | 返回值 |
|------|------|------|--------|
| `extract_error_fields` | 从违规列表提取错误字段 | `violations`, `parsed_tables` | `error_fields` |
| `generate_field_fix_prompt` | 生成针对字段的修正提示词 | `error_fields`, `available_roots` | `prompt` |
| `parse_field_fix_result` | 解析LLM返回的字段修正结果 | `llm_output` | `fix_results` |

### 3.2 修改 `main.py` 中的校验流程

**修改位置**：第2432-2489行

**修改逻辑**：

```python
# 阶段1: 检查阶段（保持不变）
validation_result = unified_validator.validate_batch(results)

# 阶段2: 提取错误字段
parsed_tables = unified_validator.parse_all_ddl(results)
error_fields = unified_validator.extract_error_fields(
    validation_result['single_violations'],
    parsed_tables
)

# 阶段3: LLM修正阶段（仅传入错误字段）
if error_fields:
    fix_prompt = unified_validator.generate_field_fix_prompt(
        error_fields,
        available_roots
    )
    # 调用LLM获取修正结果
    fix_results = call_llm(fix_prompt)
    
    # 阶段4: DDL重组阶段
    corrected_results = unified_validator.reassemble_ddl(
        results,
        fix_results,
        parsed_tables
    )
```

### 3.3 新提示词设计

```python
def generate_field_fix_prompt(self, error_fields, available_roots):
    """
    生成针对错误字段的修正提示词
    """
    fields_text = ""
    for table_name, fields in error_fields.items():
        for field_name, info in fields.items():
            violations_text = "\n".join([
                f"  - {v['message']}" for v in info['violations']
            ])
            fields_text += f"""表: {table_name}
字段: {field_name}
中文注释: {info['comment']}
当前英文名称: {info['current_name']}
违规问题:
{violations_text}

"""
    
    return f"""请修正以下错误字段的英文字段名：

【错误字段列表】
{fields_text}

【可用词根列表】
{', '.join(sorted(available_roots))}

【修正要求】
1. 针对每个错误字段给出修正后的英文字段名
2. 必须使用下划线分隔，全部小写
3. 优先使用可用词根列表中的词根
4. 保持字段类型和其他属性不变
5. 如果找不到合适的词根，可以使用行业通用名称

【输出格式】
每行一个：表名.字段名:修正后的字段名

【输出示例】
order_table.order_id_new:order_id
user_table.user_name_new:user_name
"""
```

---

## 四、文件修改清单

| 文件 | 修改内容 | 类型 |
|------|---------|------|
| `app/validators/unified_validator.py` | 新增 `extract_error_fields` 方法 | 新增 |
| `app/validators/unified_validator.py` | 新增 `generate_field_fix_prompt` 方法 | 新增 |
| `app/validators/unified_validator.py` | 新增 `parse_field_fix_result` 方法 | 新增 |
| `app/validators/unified_validator.py` | 新增 `reassemble_ddl` 方法 | 新增 |
| `app/main.py` | 修改校验流程，引入新方法 | 修改 |

---

## 五、实施步骤

### Phase 1: 新增方法（1天）
1. 新增 `extract_error_fields` 方法
2. 新增 `generate_field_fix_prompt` 方法
3. 新增 `parse_field_fix_result` 方法
4. 新增 `reassemble_ddl` 方法

### Phase 2: 修改校验流程（1天）
1. 修改 `main.py` 中的校验逻辑
2. 集成新方法

### Phase 3: 测试验证（0.5天）
1. 单元测试
2. 集成测试

---

## 六、预期效果

| 指标 | 当前 | 优化后 |
|------|------|--------|
| LLM上下文大小 | 整个批次DDL | 仅错误字段 |
| 修正准确性 | 中 | 高（针对性更强） |
| LLM调用成本 | 高 | 低（上下文更小） |
| 修正效率 | 中 | 高 |
