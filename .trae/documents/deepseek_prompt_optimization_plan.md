# DeepSeek 模型 Prompt 格式优化计划

## 一、研究结论

### 1.1 当前问题

DeepSeek 模型（尤其是 R1 推理系列）在批量建表的字段级处理流程中，解析失败率较高，导致频繁回退到无防护的表级处理路径，从而产生 `x34f` 等无意义字段名。

### 1.2 根因分析

当前 prompt 设计存在以下不适应 DeepSeek 模型的问题：

| 问题 | 影响 |
|------|------|
| 输出格式要求放在 prompt 中间位置 | DeepSeek 对长 prompt 的末尾内容记忆更强（recency bias），中间的格式约束容易被忽略 |
| "不要输出解释"约束力度不够 | 推理模型天然倾向输出思考过程，弱约束下容易夹带解释性文字 |
| 格式标记不够明确 | 用 `【】` 标记段落，DeepSeek 容易忽略这些标记，输出格式混乱 |
| system prompt 信息不足 | 关键约束散落在 user prompt 中，system prompt 过于简单 |
| 示例数量偏少 | 仅 2-4 个示例，模型对格式的理解不充分 |
| Layer3 输出格式过于复杂 | `字段名:英文名\|词根1:英1,词根2:英2` 的格式对模型要求太高 |

### 1.3 涉及的 LLM 调用点

共 6 个关键 LLM 调用点需要优化：

| 序号 | 调用函数 | 文件位置 | 作用 |
|------|---------|---------|------|
| 1 | `build_prompt_for_batch` | field_processor.py#L690-L744 | 旧版批量字段翻译（已弃用但保留） |
| 2 | `generate_table_name` | field_processor.py#L810-L920 | 表名生成 |
| 3 | `normalize_unmatched_roots_semantically` | field_processor.py#L1093-L1198 | 词根语义归一 |
| 4 | `_translate_roots_batch` | field_processor.py#L1247-L1400 | 词根批量翻译（核心路径） |
| 5 | `build_layer3_prompt` / `_design_fields_batch` | field_processor.py#L1502-L1587 | Layer3 字段设计 |
| 6 | `generate_single_table_ddl` | main.py#L2310-L2398 | 表级 DDL 生成（回退路径） |

---

## 二、优化策略总览

### 2.1 核心原则

1. **格式后置原则**：输出格式要求放在 prompt 最后，利用 recency bias
2. **强约束原则**：对"禁止输出解释"使用多重强调
3. **清晰边界原则**：使用明确的开始/结束标记包裹输出
4. **分工原则**：system prompt 放角色和核心约束，user prompt 放具体数据和格式
5. **示例充足原则**：每个格式点至少 3 个以上示例
6. **简化原则**：尽量简化输出格式，降低模型理解成本

### 2.2 通用优化模板

所有 prompt 统一调整为以下结构：

```
【角色与任务】
一句话说明任务

【输入数据】
...具体数据...

【核心规则】
...规则列表（精简）...

【输出格式】
=== 开始输出 ===
...格式说明 + 多个示例...
=== 结束输出 ===

【重要提醒】
- 只输出格式范围内的内容，不要输出任何解释、说明、思考过程
- 严格按照示例格式输出，不要添加额外文字
- 输出必须可以被程序直接解析
```

---

## 三、具体修改步骤

### 步骤 1：优化词根批量翻译（_translate_roots_batch）—— 最高优先级

**文件**：`backend/app/processors/field_processor.py`

**位置**：`_translate_roots_batch` 方法，约 L1266-L1316

**修改内容**：

1. 将输出格式从中间移到末尾
2. 增加 `===输出开始===` / `===输出结束===` 标记
3. 示例从 2 个增加到 5 个，覆盖不同场景
4. "严禁使用无意义命名"从开头移到末尾提醒
5. system prompt 增强，加入格式约束
6. 在末尾增加三重强调：
   - 不要输出解释
   - 不要输出思考过程
   - 只输出词根映射行

**预期效果**：词根翻译解析成功率提升，减少因格式错乱导致的未匹配词根。

---

### 步骤 2：优化 Layer3 字段设计（build_layer3_prompt）—— 高优先级

**文件**：`backend/app/processors/field_processor.py`

**位置**：`build_layer3_prompt` 方法，约 L1502-L1538

**修改内容**：

1. 重新组织 prompt 结构，格式要求后置
2. 简化输出格式：从 `字段名:英文名|词根1:英1,词根2:英2`
   改为更简单的多行格式（降低模型出错概率）
3. 增加输出边界标记
4. 增加 3 个以上完整示例
5. 末尾加强"只输出结果"约束
6. 同步修改 `parse_layer3_output` 解析逻辑适配新格式

**备选方案**：如果简化格式风险太大，则保持格式不变，只做结构调整和示例增强。

**预期效果**：Layer3 解析成功率提升，更多字段能走到字段级处理的完整路径。

---

### 步骤 3：优化词根语义归一（normalize_unmatched_roots_semantically）—— 中优先级

**文件**：`backend/app/processors/field_processor.py`

**位置**：`normalize_unmatched_roots_semantically` 方法，约 L1119-L1139

**修改内容**：

1. 格式要求后置
2. 增加输出边界标记
3. 增加同义归一的具体示例（展示"相同语义用同一词根"）
4. 末尾加强约束

**预期效果**：语义归一准确率提升，减少同义词根不一致问题。

---

### 步骤 4：优化表名生成（generate_table_name）—— 中优先级

**文件**：`backend/app/processors/field_processor.py`

**位置**：`generate_table_name` 方法 + `TABLE_NAME_PROMPT` 常量，约 L31-L54 和 L838-L852

**修改内容**：

1. 重构 `TABLE_NAME_PROMPT`，格式要求后置
2. 增加输出边界标记
3. 示例从 1 个增加到 3 个（覆盖不同分层）
4. 末尾加强"只输出表名"约束
5. system prompt 增强

**预期效果**：表名生成格式更稳定，减少因表名格式错误导致的修复失败。

---

### 步骤 5：优化表级 DDL 生成（generate_single_table_ddl）—— 低优先级（兜底路径）

**文件**：`backend/app/main.py`

**位置**：`generate_single_table_ddl` 函数，约 L2372-L2396

**修改内容**：

1. 在 prompt 末尾增加字段名安全约束：
   - 严禁使用 `x` 开头加十六进制字符的无意义命名（如 x34f、xab1）
   - 严禁使用 `fld_`、`tbl_`、`_attr` 等占位符
2. 末尾增加"只输出 SQL"的强约束
3. 调整要求顺序，把格式相关要求放在最后

**注意**：这是兜底路径，优先级低于字段级处理的优化。

---

### 步骤 6：统一 system prompt 优化

**文件**：`backend/app/processors/field_processor.py`

**修改内容**：

为 6 个调用点分别优化 system prompt，原则：
- system prompt 放"角色定义 + 核心约束 + 输出原则"
- 具体数据和格式细节放 user prompt
- 每个 system prompt 都明确"输出必须可被程序直接解析"

---

## 四、需要修改的文件清单

| 文件 | 修改内容 |
|------|---------|
| `backend/app/processors/field_processor.py` | 主要修改文件，5 个调用点的 prompt 重构 |
| `backend/app/main.py` | 表级 DDL 生成的 prompt 优化 |

---

## 五、潜在风险与应对

### 风险 1：prompt 调整后，其他模型（如 GPT 系列）效果下降

**应对**：
- 优化方向是通用的（格式后置、强约束、清晰边界），对所有模型都有正向作用
- 保留现有解析逻辑的兼容性，不破坏原有格式的解析能力
- 可以先在 DeepSeek 上验证，再确认对其他模型的影响

### 风险 2：Layer3 格式简化后，词根信息丢失

**应对**：
- 优先采用"格式不变，只做结构和示例优化"的保守方案
- 激进的格式简化作为备选方案，单独评估
- 确保解析逻辑向后兼容

### 风险 3：prompt 变长导致 token 消耗增加

**应对**：
- 精简规则描述，用更凝练的语言
- 示例数量控制在合理范围（3-5 个），不是越多越好
- 边界标记用简短的符号

### 风险 4：改动点多，容易引入新 bug

**应对**：
- 按优先级逐步实施，先做核心路径（词根翻译）
- 每步修改后运行现有测试（`test_deepseek_native_api_guardrails.py` 等）
- 保留旧格式的解析兼容性

---

## 六、验证方法

1. 运行现有的 DeepSeek 相关测试：`pytest test_deepseek_native_api_guardrails.py -v`
2. 运行字段处理器相关测试
3. 用实际的批量建表 Excel 测试，对比优化前后的字段级处理成功率
4. 检查日志中"字段级处理失败，回退到表级处理"的出现频率是否下降
5. 确认最终 DDL 中不再出现 `x34f` 等无意义字段名
