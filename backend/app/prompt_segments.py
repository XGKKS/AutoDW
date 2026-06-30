import json
import os
import re
import shutil
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


PROMPT_SEGMENT_DEFAULTS: List[Dict[str, Any]] = [
    {
        "key": "text_schema_extract",
        "title": "1. 文本需求结构化抽取",
        "stage": "text-generate-ddl-task",
        "business_description": "把用户输入的自然语言建表需求提炼成单表结构化定义，供后续字段和表名流程继续处理。",
        "auto_context_labels": [
            {"key": "db_type", "label": "数据库类型"},
            {"key": "description", "label": "建表需求原文"},
        ],
        "notes": "文本模式专用。这里只负责抽取中文表结构，不生成英文名或 DDL。",
        "guidance_placeholder": "例如：如果需求里出现多个候选表，只保留核心业务主表；字段类型不确定时宁可留空，不要猜测。",
        "guidance_anchor": "数据库类型：{db_type}",
        "guidance_insert_mode": "before_anchor",
        "base_system_prompt": "你是结构化信息抽取助手，只返回合法 JSON 对象。",
        "base_user_prompt": """请从下面的中文建表需求中提取单张表的结构化定义，并严格只输出 JSON 对象，不要输出解释。

要求：
1. 只能提取 1 张表；如果文本中明显描述了多张表，也仍只允许返回 1 张表，否则视为失败。
2. JSON 格式必须为：
{
  "table_name": "中文表名",
  "layer": "ods|dim|dwd|dws|ads|input|",
  "user_specified_subject_domain": "主题域缩写或空字符串",
  "fields": [
    {"name": "中文字段名", "type": "字段类型或空字符串"}
  ]
}
3. 如果字段类型无法明确判断，type 返回空字符串。
4. 不要生成英文表名或英文字段名。

数据库类型：{db_type}

建表需求：
{description}""",
    },
    {
        "key": "root_semantic_normalize",
        "title": "2. 未匹配词根语义归一",
        "stage": "field_processor.normalize_unmatched_roots_semantically",
        "business_description": "对尚未命中的中文词根做同义、近义归并，尽量统一成已有的标准英文词根。",
        "auto_context_labels": [
            {"key": "roots_text", "label": "待归一中文词根列表"},
            {"key": "history_text", "label": "标准词根映射"},
            {"key": "style_guide", "label": "当前词根模式约束"},
        ],
        "notes": "这里的标准词根映射来自 standard_roots，不是 historical_roots。",
        "guidance_placeholder": "例如：像“预计/预估”“启用/生效”这类同义概念优先合并；不要为了字面差异拆成多个英文词根。",
        "guidance_anchor": "【输出格式】",
        "guidance_insert_mode": "before_anchor",
        "base_system_prompt": "你是一位数据仓库词根语义归一专家，请识别同义/近义业务词根并统一英文命名。",
        "base_user_prompt": """请对以下中文业务词根做语义归一和英文翻译。

【待归一词根列表】
{roots_text}

【当前标准词根映射（来自标准词根库，优先沿用）】
{history_text}

【当前词根模式约束】
{style_guide}

【要求】
1. 判断待归一词根中是否存在同义词、近义词或同一业务概念的不同说法。
2. 同义/近义词必须输出同一个英文词根，例如“预计”和“预估”如果语义相同，应使用同一个英文词根。
3. 如果当前标准词根映射中已有相同中文词根，或存在明显同义/近义语义，请优先沿用其中英文词根。
4. 必须为每个待归一词根输出一行。

【输出格式】
中文词根:英文词根

不要输出任何解释，只输出词根映射。""",
    },
    {
        "key": "root_translate",
        "title": "3. 未匹配词根批量翻译",
        "stage": "field_processor._translate_roots_batch",
        "business_description": "对仍未命中的中文词根做英文翻译，生成可复用的标准词根，后续字段名由本地按分词顺序拼接。",
        "auto_context_labels": [
            {"key": "standards", "label": "附加命名约束/行业背景"},
            {"key": "style_guide", "label": "当前词根模式约束"},
            {"key": "industry_context_block", "label": "行业背景"},
            {"key": "roots_text", "label": "待翻译中文词根列表"},
            {"key": "semantic_text", "label": "已确定同义词归一表"},
        ],
        "notes": "这里只翻译词根，不直接输出字段名或 DDL。",
        "guidance_placeholder": "例如：财务场景优先使用更稳定的行业通用词根；遇到缩写歧义时优先可读性和复用一致性。",
        "guidance_anchor": "请按以下格式输出，每行一个：",
        "guidance_insert_mode": "before_anchor",
        "base_system_prompt": """你是一位数据仓库专家，请根据中文业务词根生成符合规范的英文翻译。

【附加命名约束/行业背景（可能为空）】
{standards}

如提供了附加命名约束或行业背景，请一并遵守；核心仍以已有词根和当前词根模式约束为准，并注意同一汉语意思要翻译为同一词根

【重要约束】{style_guide}""",
        "base_user_prompt": """请为以下中文业务词根生成英文翻译，严禁使用无意义的命名翻译：

{industry_context_block}

【待翻译词根列表】
{roots_text}

【词根规则】
1. 词根必须全部小写
2. {style_guide}
3. 每个词根单独一行
4. 同义/近义中文词根必须翻译为同一个英文词根

【已确定同义词归一表】
{semantic_text}

如果待翻译词根与归一表中的词根同义或近义，必须使用归一表中的相同英文词根，不得改写。

请按以下格式输出，每行一个：
中文词根:英文词根
示例：
订单:order
客户:customer
创建时间:create_time
用户ID:user_id

不要输出任何解释，只输出词根映射。""",
    },
    {
        "key": "table_name_generate",
        "title": "4. 表名生成",
        "stage": "field_processor.generate_table_name",
        "business_description": "根据中文表名、词根约束、主题域和数据库类型生成最终英文表名。",
        "auto_context_labels": [
            {"key": "chinese_table_name", "label": "中文表名"},
            {"key": "industry_context_block", "label": "行业背景"},
            {"key": "standards_content", "label": "附加命名约束/行业背景"},
            {"key": "db_type", "label": "数据库类型"},
            {"key": "table_format", "label": "表名格式要求"},
            {"key": "available_roots", "label": "可用词根列表"},
            {"key": "root_constraints", "label": "词根模式强制约束"},
            {"key": "root_reuse_principle", "label": "词根复用原则"},
            {"key": "theme_prefix", "label": "主题域缩写"},
            {"key": "theme_prefix_guide", "label": "主题域缩写规则"},
            {"key": "table_name_example", "label": "输出示例"},
        ],
        "notes": "这里只输出英文表名，不生成整表 DDL。",
        "guidance_placeholder": "例如：主题域不明确时不要默认 pub；更偏向业务语义稳定、可复用的命名，不要为了简短牺牲辨识度。",
        "guidance_anchor": "【输出格式】",
        "guidance_insert_mode": "before_anchor",
        "base_system_prompt": "你是一位数据仓库专家，请根据中文表名生成符合规范的英文表名。",
        "base_user_prompt": """【任务】根据以下信息生成符合规范的英文表名

【中文表名】{chinese_table_name}

{industry_context_block}

【附加命名约束/行业背景（可能为空）】
{standards_content}

【数据库类型】{db_type}

【表名格式要求】{table_format}

【可用词根列表】
{available_roots}

{root_constraints}
{root_reuse_principle}

【主题域缩写】{theme_prefix}

【主题域缩写规则】
{theme_prefix_guide}

【输出格式】
请只输出英文表名，不要包含任何解释或额外内容。

【输出示例】
{table_name_example}""",
    },
    {
        "key": "duplicate_field_fix",
        "title": "5. 同表重复字段名修正",
        "stage": "field_processor._request_duplicate_field_name_fix",
        "business_description": "当同一张表里出现重复英文字段名时，针对冲突字段重新命名，保证同表唯一且语义贴合。",
        "auto_context_labels": [
            {"key": "industry_context_block", "label": "行业背景"},
            {"key": "table_name", "label": "问题表名"},
            {"key": "duplicate_count", "label": "重复字段数量"},
            {"key": "duplicate_english_name", "label": "重复英文字段名"},
            {"key": "field_lines", "label": "待修正字段列表"},
            {"key": "used_name_text", "label": "当前表内其他已使用字段名"},
            {"key": "available_roots", "label": "可用词根列表"},
            {"key": "style_guide", "label": "当前词根模式约束"},
        ],
        "notes": "只有本地检测到同表重复字段名时才会触发。",
        "guidance_placeholder": "例如：优先通过补充业务语义区分字段，不要依赖序号或无意义前后缀凑唯一。",
        "guidance_anchor": "【输出格式】",
        "guidance_insert_mode": "before_anchor",
        "base_system_prompt": "你是一位数据仓库字段命名修正专家，请专门修复同表重复英文字段名问题。",
        "base_user_prompt": """请修正同一张表内重复的英文字段名，只输出修正结果，不要解释。

{industry_context_block}

【问题表】
{table_name}

【重复情况】
这个表里有 {duplicate_count} 个字段重复映射成了 `{duplicate_english_name}`，需要修正成不重复的字段名。

【待修正字段】
{field_lines}

【当前表内其他已使用字段名】
{used_name_text}

【可用词根列表】
{available_roots}

【命名规则】
1. 字段名必须使用下划线分隔，全部小写
2. {style_guide}
3. 这几个字段修正后必须彼此不同
4. 修正后不得与当前表内其他已使用字段名重复
5. 要贴合中文语义，不允许直接加无意义序号凑唯一
6. 推荐字段类型保持原值

【输出格式】
表名|字段序号|中文字段名:修正英文字段名:推荐字段类型

【输出示例】
{table_name}|1|送修人:repair_sender:VARCHAR(128)
{table_name}|2|送单人:dispatch_sender:VARCHAR(128)""",
    },
    {
        "key": "validation_field_fix",
        "title": "6. 统一校验字段修正",
        "stage": "unified_validator.generate_field_fix_prompt",
        "business_description": "在统一校验发现问题后，按字段级上下文重新修正错误字段名，保证符合词根规则和已有词根约束。",
        "auto_context_labels": [
            {"key": "get_system_prompt()", "label": "系统基础规则"},
            {"key": "fields_text", "label": "错误字段列表"},
            {"key": "roots_text", "label": "可用词根列表"},
            {"key": "root_mode_block", "label": "当前词根模式说明"},
        ],
        "notes": "这个阶段会看到字段中文注释和 jieba 分词词根，但只修正错误字段，不做全局重写。",
        "guidance_placeholder": "例如：优先沿用已经稳定使用的字段词根；若多个字段中文相近，也要按字段序号逐条判断，不要批量替换。",
        "guidance_anchor": "【输出格式】",
        "guidance_insert_mode": "before_anchor",
        "base_system_prompt": "{get_system_prompt()}",
        "base_user_prompt": """请修正以下错误字段的英文字段名：

【错误字段列表】
{fields_text}

【可用词根列表】
{roots_text}

{root_mode_block}

【修正要求】
1. 必须按 jieba分词词根 逐词翻译并按原顺序用下划线拼接字段名
2. 同一个中文词根在所有字段中必须使用同一个英文词根
3. 优先使用可用词根列表中的词根，必须满足当前词根模式强制约束
4. 保持字段类型和其他属性不变
5. 不得输出 table、field、column 等无意义字段名
6. 不得对同名字段做全局替换，必须按字段序号定位

【输出格式】
每行一个：表名.字段序号.当前字段名:修正后的字段名

【输出示例】
order_table.2.table:product_id
user_table.4.table:create_time""",
    },
]

GUIDANCE_BLOCK_TITLE = "【本阶段补充要求】"
MIGRATION_NOTICE = "检测到旧版分段模板自定义内容，系统已备份为 prompt_segments.legacy.json，并切换为安全模式。旧版自由编辑内容不会自动迁移，请手工提炼为各阶段的“补充要求”。"


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_prompt_segments_file(base_dir: str) -> str:
    return os.path.join(base_dir, "prompt_segments.json")


def get_prompt_segments_legacy_file(base_dir: str) -> str:
    return os.path.join(base_dir, "prompt_segments.legacy.json")


def default_prompt_segments() -> List[Dict[str, Any]]:
    return deepcopy(PROMPT_SEGMENT_DEFAULTS)


def _defaults_by_key() -> Dict[str, Dict[str, Any]]:
    return {item["key"]: item for item in default_prompt_segments()}


def _normalize_guidance(value: Any) -> str:
    text = str(value or "").replace("\r\n", "\n").strip()
    return text


def _write_guidance_store(path: str, records: List[Dict[str, str]]):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def _load_raw_store(path: str) -> Any:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        return None


def _is_legacy_prompt_segment_data(data: Any) -> bool:
    if not isinstance(data, list):
        return False
    for item in data:
        if isinstance(item, dict) and ("system_prompt" in item or "user_prompt" in item):
            return True
    return False


def _backup_legacy_store(base_dir: str, data: Any):
    legacy_path = get_prompt_segments_legacy_file(base_dir)
    if os.path.exists(legacy_path):
        return
    if data is not None:
        with open(legacy_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        source = get_prompt_segments_file(base_dir)
        if os.path.exists(source):
            shutil.copyfile(source, legacy_path)


def _load_guidance_records(base_dir: str) -> Tuple[Dict[str, Dict[str, str]], Optional[str]]:
    path = get_prompt_segments_file(base_dir)
    raw = _load_raw_store(path)
    migration_notice = None

    if _is_legacy_prompt_segment_data(raw):
        _backup_legacy_store(base_dir, raw)
        _write_guidance_store(
            path,
            [{"key": item["key"], "guidance": "", "updated_at": ""} for item in default_prompt_segments()],
        )
        raw = []
        migration_notice = MIGRATION_NOTICE

    if not isinstance(raw, list):
        return {}, migration_notice

    defaults_by_key = _defaults_by_key()
    records: Dict[str, Dict[str, str]] = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        key = item.get("key")
        if key not in defaults_by_key:
            continue
        records[key] = {
            "key": key,
            "guidance": _normalize_guidance(item.get("guidance")),
            "updated_at": str(item.get("updated_at") or ""),
        }
    return records, migration_notice


def _persist_guidance_records(base_dir: str, records: Dict[str, Dict[str, str]]):
    defaults = default_prompt_segments()
    serializable = []
    for item in defaults:
        record = records.get(item["key"], {})
        serializable.append({
            "key": item["key"],
            "guidance": _normalize_guidance(record.get("guidance")),
            "updated_at": str(record.get("updated_at") or ""),
        })
    _write_guidance_store(get_prompt_segments_file(base_dir), serializable)


def _build_guidance_block(guidance: str) -> str:
    guidance = _normalize_guidance(guidance)
    if not guidance:
        return ""
    return f"{GUIDANCE_BLOCK_TITLE}\n{guidance}\n\n"


def _insert_guidance(base_prompt: str, segment: Dict[str, Any], guidance: str) -> str:
    prompt = str(base_prompt or "")
    guidance_block = _build_guidance_block(guidance)
    if not guidance_block:
        return prompt

    anchor = str(segment.get("guidance_anchor") or "").strip()
    mode = str(segment.get("guidance_insert_mode") or "before_anchor")

    if mode == "before_anchor" and anchor and anchor in prompt:
        return prompt.replace(anchor, guidance_block + anchor, 1)
    return prompt.rstrip() + "\n\n" + guidance_block.rstrip()


def _placeholder_preview_label(key: str, fallback: str = "") -> str:
    key = str(key or "").strip()
    label = str(fallback or key).strip()
    return f"（系统自动注入：{label}）"


def _render_preview_template(template: str, segment: Dict[str, Any]) -> str:
    label_map = {}
    for item in segment.get("auto_context_labels") or []:
        if isinstance(item, dict) and item.get("key"):
            label_map[str(item["key"])] = str(item.get("label") or item["key"])

    rendered = str(template or "")
    if "{get_system_prompt()}" in rendered:
        rendered = rendered.replace("{get_system_prompt()}", _placeholder_preview_label("get_system_prompt()", label_map.get("get_system_prompt()", "系统基础规则")))

    def replace(match: re.Match) -> str:
        key = match.group(1)
        return _placeholder_preview_label(key, label_map.get(key, key))

    return re.sub(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", replace, rendered)


def _build_runtime_segment(base_dir: str, key: str) -> Dict[str, Any]:
    defaults_by_key = _defaults_by_key()
    if key not in defaults_by_key:
        raise KeyError(key)

    records, _ = _load_guidance_records(base_dir)
    segment = deepcopy(defaults_by_key[key])
    record = records.get(key, {})
    guidance = _normalize_guidance(record.get("guidance"))
    segment["guidance"] = guidance
    segment["updated_at"] = str(record.get("updated_at") or "")
    segment["system_prompt"] = _insert_guidance(segment.get("base_system_prompt", ""), segment, guidance)
    segment["user_prompt"] = _insert_guidance(segment.get("base_user_prompt", ""), segment, guidance)
    return segment


def _build_ui_segment(base_dir: str, key: str) -> Dict[str, Any]:
    segment = _build_runtime_segment(base_dir, key)
    return {
        "key": segment["key"],
        "title": segment["title"],
        "stage": segment["stage"],
        "business_description": segment.get("business_description", ""),
        "auto_context_labels": [item.get("label", "") for item in segment.get("auto_context_labels", []) if isinstance(item, dict)],
        "guidance": segment.get("guidance", ""),
        "guidance_placeholder": segment.get("guidance_placeholder", ""),
        "notes": segment.get("notes", ""),
        "updated_at": segment.get("updated_at", ""),
        "preview_system_prompt": _render_preview_template(segment.get("system_prompt", ""), segment),
        "preview_user_prompt": _render_preview_template(segment.get("user_prompt", ""), segment),
    }


def load_prompt_segments(base_dir: str) -> List[Dict[str, Any]]:
    return [_build_ui_segment(base_dir, item["key"]) for item in default_prompt_segments()]


def load_prompt_segments_response(base_dir: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    _, migration_notice = _load_guidance_records(base_dir)
    return load_prompt_segments(base_dir), migration_notice


def get_prompt_segment(base_dir: str, key: str) -> Dict[str, Any]:
    return _build_runtime_segment(base_dir, key)


def render_prompt_template(template: str, values: Dict[str, Any]) -> str:
    value_map = {str(k): "" if v is None else str(v) for k, v in (values or {}).items()}
    rendered = str(template or "")
    if "get_system_prompt" in value_map:
        rendered = rendered.replace("{get_system_prompt()}", value_map["get_system_prompt"])

    def replace(match: re.Match) -> str:
        key = match.group(1)
        return value_map.get(key, match.group(0))

    return re.sub(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", replace, rendered)


def render_prompt_segment(base_dir: str, key: str, values: Dict[str, Any]) -> Dict[str, Any]:
    segment = get_prompt_segment(base_dir, key)
    return {
        **segment,
        "system_prompt": render_prompt_template(segment.get("system_prompt", ""), values),
        "user_prompt": render_prompt_template(segment.get("user_prompt", ""), values),
    }


def _validate_guidance_payload(segment: Dict[str, Any], allow_key: bool = False) -> Dict[str, str]:
    if not isinstance(segment, dict):
        raise ValueError("提示词分段配置格式错误")
    allowed = {"guidance"}
    if allow_key:
        allowed.add("key")
    extra_fields = set(segment.keys()) - allowed
    if extra_fields:
        raise ValueError(f"只允许保存 guidance，检测到非法字段: {', '.join(sorted(extra_fields))}")
    return {"guidance": _normalize_guidance(segment.get("guidance"))}


def save_prompt_segments(base_dir: str, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    defaults_by_key = _defaults_by_key()
    records, _ = _load_guidance_records(base_dir)

    for incoming in segments or []:
        if not isinstance(incoming, dict):
            raise ValueError("提示词分段配置格式错误")
        key = incoming.get("key")
        if key not in defaults_by_key:
            raise ValueError(f"未知提示词分段: {key}")
        normalized = _validate_guidance_payload(incoming, allow_key=True)
        records[key] = {
            "key": key,
            "guidance": normalized["guidance"],
            "updated_at": _now_text(),
        }

    for key in defaults_by_key:
        records.setdefault(key, {"key": key, "guidance": "", "updated_at": ""})

    _persist_guidance_records(base_dir, records)
    return load_prompt_segments(base_dir)


def reset_prompt_segments(base_dir: str) -> List[Dict[str, Any]]:
    records = {item["key"]: {"key": item["key"], "guidance": "", "updated_at": ""} for item in default_prompt_segments()}
    _persist_guidance_records(base_dir, records)
    return load_prompt_segments(base_dir)


def save_prompt_segment(base_dir: str, key: str, segment: Dict[str, Any]) -> List[Dict[str, Any]]:
    defaults_by_key = _defaults_by_key()
    if key not in defaults_by_key:
        raise KeyError(key)

    normalized = _validate_guidance_payload(segment, allow_key=False)
    records, _ = _load_guidance_records(base_dir)
    records[key] = {
        "key": key,
        "guidance": normalized["guidance"],
        "updated_at": _now_text(),
    }
    _persist_guidance_records(base_dir, records)
    return load_prompt_segments(base_dir)


def reset_prompt_segment(base_dir: str, key: str) -> List[Dict[str, Any]]:
    defaults_by_key = _defaults_by_key()
    if key not in defaults_by_key:
        raise KeyError(key)

    records, _ = _load_guidance_records(base_dir)
    records[key] = {"key": key, "guidance": "", "updated_at": ""}
    _persist_guidance_records(base_dir, records)
    return load_prompt_segments(base_dir)
