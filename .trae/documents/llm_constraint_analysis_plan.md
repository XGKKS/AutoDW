# 开发规范与自定义提示词对大模型的约束分析报告

## 一、核心问题：基础词根翻译规则硬编码问题

### 1.1 用户发现的问题

**问题定位**：基础词根速查表的强制翻译规则存在**硬编码**问题

**硬编码位置**（代码层面）：

| 文件 | 行号 | 硬编码内容 |
|-----|------|-----------|
| [field_processor.py](file:///d:/Data/Trae/数仓AI助手-Trae1.0/AI-WarHouse/XGKK-AI/_internal/app/processors/field_processor.py) | 1136-1145 | System Prompt中的强制翻译规则 |
| [field_processor.py](file:///d:/Data/Trae/数仓AI助手-Trae1.0/AI-WarHouse/XGKK-AI/_internal/app/processors/field_processor.py) | 1332-1339 | 提示词模板中的基础词根速查 |

**硬编码内容示例**：
```python
# field_processor.py 第1136-1145行
system_content = f"""你是一位数据仓库专家，请根据中文业务词根生成符合规范的英文翻译。

【开发规范】
{self.standards}

请严格按照开发规范和已有词根进行翻译，并注意同一汉语意思要翻译为同一词根

【重要约束】{style_guide}
"""
```

### 1.2 开发规范中的对应内容

**查看 [dev_standards.json](file:///d:/Data/Trae/数仓AI助手-Trae1.0/AI-WarHouse/XGKK-AI/_internal/dev_standards.json)**：

规范中仅在"字段类型规范"部分提到了核心词根的推荐类型，但**没有包含这些基础词根的强制翻译规则**：

```json
{
  "content": "## 数仓开发规范（内部标准规范）\n\n### 四、字段类型规范\n\n| 核心词根 | 适用场景 | 推荐类型 |\n|---------|---------|---------|\n| `id` | 主键/唯一标识 | VARCHAR(64) |\n| `name` | 名称 | VARCHAR(128) |\n| `code` | 编码 | VARCHAR(64) |\n| `num` | 数量 | INT/BIGINT |\n| `amt` | 金额 | DECIMAL(18,2) |\n| `date` | 日期 | DATE |\n| `time` | 时间 | DATETIME |\n| `flag` | 标志位 | TINYINT(1) |\n| `desc` | 描述 | VARCHAR(512) |"
}
```

---

## 二、硬编码问题的影响分析

### 2.1 当前架构的耦合问题

```
┌─────────────────────────────────────────────────────────────┐
│                    当前架构问题                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  开发规范 (dev_standards.json)                              │
│  └── 只包含字段类型规范（无基础词根翻译规则）                  │
│                                                             │
│  代码层 (field_processor.py)                                │
│  └── 硬编码基础词根翻译规则 ← 【问题所在】                    │
│                                                             │
│  问题：开发规范与代码逻辑不一致，规则修改需要改代码             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 问题带来的后果

| 问题类型 | 后果 |
|---------|-----|
| **可维护性差** | 修改基础词根翻译规则需要改动代码，重启服务 |
| **规范不一致** | 开发规范文档与实际执行规则不一致，造成困惑 |
| **灵活性不足** | 无法通过配置文件动态调整规则 |
| **代码重复** | 相同规则在多处硬编码（第1136行和第1332行） |

---

## 三、优化方案

### 3.1 方案一：将基础词根规则加入开发规范（推荐）

**修改 `dev_standards.json`**：
```json
{
  "version": "1.0",
  "last_modified": "2026-06-09 00:00:00",
  "content": "## 数仓开发规范（内部标准规范）\n\n### 零、基础词根速查表（强制）\n\n以下中文词根必须严格按照指定的英文词根翻译：\n\n| 中文词根类别 | 英文词根 | 说明 |\n|------------|---------|-----|\n| 是否/布尔 | is | 表示是/否、开关、标志等含义 |\n| 状态 | status | 表示状态、状态码等含义 |\n| 类型 | type | 表示类型、类别等含义 |\n| 名称 | name | 表示名称、标题等含义 |\n| 编号/标识 | id | 表示标识、编号、ID等含义 |\n| 数量 | num | 表示数量、数目等含义 |\n| 金额 | amt | 表示金额、价格等含义 |\n| 日期 | date | 表示日期 |\n| 时间 | time | 表示时间、时刻等含义 |\n\n### 一、词根原则\n...",
  "basic_roots": {
    "是否": "is",
    "状态": "status",
    "类型": "type",
    "名称": "name",
    "编号": "id",
    "标识": "id",
    "数量": "num",
    "金额": "amt",
    "日期": "date",
    "时间": "time"
  }
}
```

**修改代码**：从规范中读取基础词根规则，不再硬编码

```python
# field_processor.py - 优化后的实现
def _get_basic_root_rules(self) -> str:
    """从开发规范中提取基础词根规则"""
    if hasattr(self.standards, 'basic_roots') and self.standards.basic_roots:
        rules = []
        for chinese, english in self.standards.basic_roots.items():
            rules.append(f'- "{chinese}"类词根必须翻译为 "{english}"')
        return "\n".join(rules)
    return ""

def _build_system_prompt(self):
    """构建系统提示词（优化后）"""
    basic_root_rules = self._get_basic_root_rules()
    
    system_content = f"""你是一位数据仓库专家，请根据中文业务词根生成符合规范的英文翻译。

【开发规范】
{self.standards.content}

{"【基础词根强制规则】\n" + basic_root_rules if basic_root_rules else ""}

【重要约束】{self._root_style_guide()}
"""
    return system_content
```

### 3.2 方案二：独立配置文件管理基础词根

**新建配置文件 `config/basic_roots.json`**：
```json
{
  "version": "1.0",
  "rules": [
    {
      "chinese_patterns": ["是否", "布尔", "开关", "标志"],
      "english_root": "is",
      "description": "表示是/否、开关、标志等含义"
    },
    {
      "chinese_patterns": ["状态", "状态码"],
      "english_root": "status",
      "description": "表示状态、状态码等含义"
    },
    {
      "chinese_patterns": ["类型", "类别"],
      "english_root": "type",
      "description": "表示类型、类别等含义"
    },
    {
      "chinese_patterns": ["名称", "标题"],
      "english_root": "name",
      "description": "表示名称、标题等含义"
    },
    {
      "chinese_patterns": ["编号", "标识", "ID", "id"],
      "english_root": "id",
      "description": "表示标识、编号、ID等含义"
    },
    {
      "chinese_patterns": ["数量", "数目", "个数"],
      "english_root": "num",
      "description": "表示数量、数目等含义"
    },
    {
      "chinese_patterns": ["金额", "价格", "费用"],
      "english_root": "amt",
      "description": "表示金额、价格等含义"
    },
    {
      "chinese_patterns": ["日期"],
      "english_root": "date",
      "description": "表示日期"
    },
    {
      "chinese_patterns": ["时间", "时刻"],
      "english_root": "time",
      "description": "表示时间、时刻等含义"
    }
  ]
}
```

**新增配置加载模块 `config_loader.py`**：
```python
import json
import os

class BasicRootsConfig:
    def __init__(self, config_path: str = "config/basic_roots.json"):
        self.config_path = config_path
        self.rules = self._load_rules()
    
    def _load_rules(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('rules', [])
        return []
    
    def get_rules_for_prompt(self) -> str:
        """生成提示词格式的规则文本"""
        rules = []
        for rule in self.rules:
            chinese = "/".join(rule['chinese_patterns'])
            english = rule['english_root']
            rules.append(f'- "{chinese}"类词根必须翻译为 "{english}"')
        return "\n".join(rules)
    
    def match_basic_root(self, chinese_text: str) -> str:
        """检查文本是否匹配基础词根规则"""
        for rule in self.rules:
            for pattern in rule['chinese_patterns']:
                if pattern in chinese_text:
                    return rule['english_root']
        return None
```

### 3.3 方案对比

| 维度 | 方案一（加入开发规范） | 方案二（独立配置） |
|-----|---------------------|------------------|
| **一致性** | 规范与规则统一 | 规则与规范分离 |
| **灵活性** | 中等 | 高 |
| **复杂度** | 低 | 中 |
| **推荐度** | **推荐** | 可选 |

---

## 四、代码层面强制校验（硬约束）

### 4.1 当前问题：仅依赖LLM自律

当前的约束机制主要是"软约束"——通过提示词引导LLM遵守规则，但LLM可能忽略或误解规则。

### 4.2 优化建议：代码层面强制校验

**新增基础词根强制校验逻辑**：

```python
# field_processor.py - 新增方法
def _enforce_basic_root_rules(self, chinese_name: str, english_root: str) -> bool:
    """
    在代码层面强制校验基础词根规则
    :param chinese_name: 中文词根
    :param english_root: LLM生成的英文词根
    :return: 是否符合规则
    """
    # 基础词根规则映射（从配置加载）
    basic_root_rules = {
        '是否': 'is',
        '状态': 'status',
        '类型': 'type',
        '名称': 'name',
        '编号': 'id',
        '标识': 'id',
        '数量': 'num',
        '金额': 'amt',
        '日期': 'date',
        '时间': 'time'
    }
    
    for chinese_pattern, expected_root in basic_root_rules.items():
        if chinese_pattern in chinese_name:
            # 如果包含基础词根模式，必须使用对应的英文词根
            if english_root != expected_root:
                logger.warning(f"【基础词根校验失败】'{chinese_name}' 包含'{chinese_pattern}'，"
                            f"期望词根: '{expected_root}'，实际生成: '{english_root}'")
                return False
    return True

def _validate_and_correct_root(self, chinese_name: str, english_root: str) -> str:
    """
    校验并修正词根翻译
    :param chinese_name: 中文词根
    :param english_root: LLM生成的英文词根
    :return: 修正后的英文词根
    """
    # 基础词根规则映射
    basic_root_rules = {
        '是否': 'is',
        '状态': 'status',
        '类型': 'type',
        '名称': 'name',
        '编号': 'id',
        '标识': 'id',
        '数量': 'num',
        '金额': 'amt',
        '日期': 'date',
        '时间': 'time'
    }
    
    for chinese_pattern, expected_root in basic_root_rules.items():
        if chinese_pattern in chinese_name:
            # 强制替换为正确的基础词根
            if english_root != expected_root:
                logger.info(f"【基础词根修正】'{chinese_name}' -> '{expected_root}' (原生成: '{english_root}')")
                return expected_root
    
    return english_root
```

**使用示例**：在LLM返回结果后立即进行校验和修正

```python
# field_processor.py - 在解析LLM响应后添加校验
def parse_llm_response(self, content):
    mapping = {}
    
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('--') or line.startswith('#'):
            continue
        
        parts = line.split(':')
        if len(parts) >= 2:
            chinese_name = parts[0].strip()
            english_name = parts[1].strip() if len(parts) > 1 else ''
            field_type = parts[2].strip() if len(parts) > 2 else 'VARCHAR(255)'
            
            if chinese_name and english_name:
                # 代码层面强制校验基础词根规则
                corrected_root = self._validate_and_correct_root(chinese_name, english_name)
                mapping[chinese_name] = (corrected_root, field_type)
                logger.debug(f"解析映射: {chinese_name} -> {corrected_root}")
    
    return mapping
```

---

## 五、优化实施计划

### 5.1 阶段一：消除硬编码（P0）

| 任务 | 描述 | 预计时间 |
|-----|-----|---------|
| 1 | 将基础词根规则加入 `dev_standards.json` | 0.5天 |
| 2 | 修改 `field_processor.py` 从配置读取规则 | 0.5天 |
| 3 | 测试验证 | 0.5天 |

### 5.2 阶段二：代码层面强制校验（P1）

| 任务 | 描述 | 预计时间 |
|-----|-----|---------|
| 1 | 实现 `_enforce_basic_root_rules()` 方法 | 0.5天 |
| 2 | 实现 `_validate_and_correct_root()` 方法 | 0.5天 |
| 3 | 在解析LLM响应后添加校验逻辑 | 0.5天 |
| 4 | 测试验证 | 0.5天 |

### 5.3 阶段三：完善配置化（P2）

| 任务 | 描述 | 预计时间 |
|-----|-----|---------|
| 1 | 新增独立配置文件管理基础词根 | 0.5天 |
| 2 | 实现配置加载模块 | 0.5天 |
| 3 | 支持动态重载配置 | 0.5天 |
| 4 | 测试验证 | 0.5天 |

---

## 六、总结

### 当前问题总结

1. **基础词根翻译规则硬编码**：规则写死在代码中，无法通过配置修改
2. **开发规范与实际执行不一致**：规范文档中没有包含这些强制规则
3. **仅依赖软约束**：约束主要通过提示词引导，缺乏代码层面的强制保障

### 优化收益

| 优化项 | 收益 |
|-------|-----|
| 消除硬编码 | 规则可配置，无需改代码 |
| 规范与执行一致 | 文档即规则，减少困惑 |
| 代码层面强制校验 | 确保规则被严格遵守，不依赖LLM自律 |
| 提高灵活性 | 支持动态调整基础词根映射 |

### 推荐方案

**首选方案一**：将基础词根规则加入开发规范JSON文件，同时在代码层面添加强制校验逻辑。

这样既保持了规范文档与执行规则的一致性，又通过代码层面的校验确保规则被严格遵守。
