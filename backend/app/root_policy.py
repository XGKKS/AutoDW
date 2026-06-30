import re
from typing import Dict, Iterable, List, Tuple


DEFAULT_ABBR_MAX_LEN = 4
MIN_ABBR_MAX_LEN = 1
MAX_ABBR_MAX_LEN = 12
LAYER_PREFIXES = ("ods", "dim", "dwd", "dws", "ads", "input")
CONFLICTING_LEADING_DOMAIN_PREFIXES = {"pub", "scm"}


FULL_ROOT_CONSTRAINTS = """[Root naming rules] These are mandatory rules and must be followed strictly.\n1. In full mode, field names and table-name bodies may only use full roots (`full_root`).\n2. Do not use abbreviated roots (`abbr_root`) in full mode, even if they exist in the root library.\n3. Separate words with underscores and keep everything lowercase.\n4. Newly generated roots must be complete English words; do not truncate or abbreviate them."""


def resolve_abbr_max_len(abbr_max_len: int = DEFAULT_ABBR_MAX_LEN) -> int:
    try:
        value = int(abbr_max_len)
    except (TypeError, ValueError):
        value = DEFAULT_ABBR_MAX_LEN
    return max(MIN_ABBR_MAX_LEN, min(MAX_ABBR_MAX_LEN, value))


ROOT_REUSE_FULL = "[Root reuse principle] Use only full roots (`full_root`) and never abbreviations. The same Chinese business concept must map to the same English full root across the warehouse."


def normalize_priority(priority: str) -> str:
    return "abbr" if priority == "abbr" else "full"


def get_root_constraints(priority: str, abbr_max_len: int = DEFAULT_ABBR_MAX_LEN) -> str:
    if normalize_priority(priority) != "abbr":
        return FULL_ROOT_CONSTRAINTS

    max_len = resolve_abbr_max_len(abbr_max_len)
    return (
        "[Root naming rules] These are mandatory rules and must be followed strictly.\n"
        "1. In abbreviation mode, field names and table-name bodies may only use abbreviated roots (`abbr_root`).\n"
        f"2. Each abbreviated root must be at most {max_len} characters long.\n"
        "3. Separate words with underscores and keep everything lowercase.\n"
        "4. Newly generated roots must also follow the same abbreviation-length limit."
    )


def get_root_reuse_principle(priority: str, abbr_max_len: int = DEFAULT_ABBR_MAX_LEN) -> str:
    if normalize_priority(priority) != "abbr":
        return ROOT_REUSE_FULL

    max_len = resolve_abbr_max_len(abbr_max_len)
    return (
        "[Root reuse principle] Use only abbreviated roots (`abbr_root`), "
        f"each no longer than {max_len} characters. The same Chinese business concept "
        "must map to the same English abbreviated root across the warehouse."
    )


DEFAULT_THEME_PREFIXES = {
    "公共": "pub",
    "用户": "user",
    "客户": "cust",
    "商品": "prod",
    "订单": "order",
    "财务": "fin",
    "营销": "mkt",
    "供应链": "scm",
    "工单": "ticket",
    "索赔": "claim",
    "门店": "store",
    "库存": "inv",
    "仓库": "wh",
    "人员": "staff",
}


def get_theme_prefix_map(standards_content: str = "") -> Dict[str, str]:
    """Extract theme-prefix mappings from standards, with built-in defaults as fallback."""
    theme_map = dict(DEFAULT_THEME_PREFIXES)
    if not standards_content:
        return theme_map

    for raw_line in standards_content.splitlines():
        line = raw_line.strip()
        if not line.startswith("|") or line.count("|") < 3:
            continue

        cells = [cell.strip(" `") for cell in line.strip("|").split("|")]
        if len(cells) < 2:
            continue

        prefix = ""
        theme = ""
        for cell in cells:
            lowered = cell.lower() if cell else ""
            if re.fullmatch(r"[a-z][a-z0-9_]{1,9}", lowered):
                prefix = lowered
            elif re.search(r"[\u4e00-\u9fa5]", cell):
                theme = cell

        if theme and prefix:
            theme_map[theme] = prefix

    return theme_map


def render_theme_prefix_guide(standards_content: str = "") -> str:
    theme_map = get_theme_prefix_map(standards_content)
    rows = ["### Theme Prefixes", "| 主题域 | 缩写 |", "|------|------|"]
    for theme, prefix in sorted(theme_map.items(), key=lambda item: item[0]):
        rows.append(f"| {theme} | {prefix} |")
    return "\n".join(rows)


def infer_theme_prefix(*texts: str, standards_content: str = "") -> str:
    """Infer a theme prefix from standards or surrounding context."""
    theme_map = get_theme_prefix_map(standards_content)
    haystack = " ".join(text for text in texts if text).lower()

    if not haystack.strip():
        return ""

    explicit_match = re.search(
        r"(?:主题域缩写|主题域|subject(?:_?prefix|_?domain)?)\s*[:：]?\s*([a-z][a-z0-9_]{1,9})",
        haystack,
    )
    if explicit_match:
        return explicit_match.group(1).lower()

    for theme, prefix in sorted(theme_map.items(), key=lambda item: len(item[0]), reverse=True):
        if theme.lower() in haystack:
            return prefix

    return ""


def get_theme_prefix_values(standards_content: str = "") -> set:
    return {
        prefix.lower().strip("_")
        for prefix in get_theme_prefix_map(standards_content).values()
        if prefix and prefix.strip("_")
    }


def strip_table_layer(table_name: str, layer: str = "") -> str:
    name = (table_name or "").strip().strip("`\"'").lower().strip("_")
    if "." in name:
        name = name.split(".")[-1].strip("_")

    parts = [part for part in name.split("_") if part]
    if not parts:
        return ""

    layer_candidates = set(LAYER_PREFIXES)
    if layer:
        layer_candidates.add(layer.lower().strip("_"))

    if parts[0] in layer_candidates and len(parts) > 1:
        parts = parts[1:]

    return "_".join(parts)


def normalize_table_business_domain(
    table_name: str,
    theme_prefix: str = "",
    standards_content: str = "",
    layer: str = "",
) -> str:
    """Normalize a table body to at most one leading business-domain token."""
    name = strip_table_layer(table_name, layer)
    parts = [part for part in name.split("_") if part]
    if not parts:
        return ""

    domain_prefixes = get_theme_prefix_values(standards_content)
    selected_domain = (theme_prefix or "").lower().strip("_")
    if selected_domain:
        domain_prefixes.add(selected_domain)

    domain_run = []
    for part in parts:
        if part in domain_prefixes:
            domain_run.append(part)
        else:
            break

    if selected_domain and domain_run:
        return "_".join([selected_domain] + parts[len(domain_run):])

    if len(domain_run) <= 1:
        return "_".join(parts)

    selected_domain = domain_run[-1]
    return "_".join([selected_domain] + parts[len(domain_run):])


def table_business_domain_errors(table_name: str, standards_content: str = "") -> List[str]:
    body = strip_table_layer(table_name)
    parts = [part for part in body.split("_") if part]
    domain_prefixes = get_theme_prefix_values(standards_content)

    domain_run = []
    for part in parts:
        if part in domain_prefixes:
            domain_run.append(part)
        else:
            break

    if len(domain_run) > 1 and domain_run[0] in CONFLICTING_LEADING_DOMAIN_PREFIXES:
        return [f"table name '{table_name}' contains multiple business-domain prefixes: {'_'.join(domain_run)}"]

    return []


def ensure_theme_prefix(table_name: str, theme_prefix: str = "") -> str:
    """Ensure the table-name body starts with the expected theme prefix without duplication."""
    name = (table_name or "").strip().strip("`\"'").lower().strip("_")
    if not name:
        return theme_prefix.lower().strip("_") if theme_prefix else name

    if not theme_prefix:
        return name

    theme_prefix = theme_prefix.lower().strip("_")
    parts = [part for part in name.split("_") if part]
    if parts and parts[0] == theme_prefix:
        return name

    return f"{theme_prefix}_{name}"


def build_root_sets(word_roots: Iterable[Dict]) -> Tuple[set, set, Dict[str, List[str]]]:
    full_roots = set()
    abbr_roots = set()
    abbr_to_full = {}

    for item in word_roots or []:
        full = (item.get("full_root") or "").strip().lower()
        abbr = (item.get("abbr_root") or "").strip().lower()
        chinese = (item.get("chinese_name") or "").strip().lower()

        if full:
            full_roots.add(full)
        if abbr and abbr != chinese:
            abbr_roots.add(abbr)
            if full:
                abbr_to_full.setdefault(abbr, [])
                if full not in abbr_to_full[abbr]:
                    abbr_to_full[abbr].append(full)

    return full_roots, abbr_roots, abbr_to_full


def split_identifier(identifier: str) -> List[str]:
    return [part for part in (identifier or "").lower().split("_") if part]


def validate_identifier_mode(
    identifier: str,
    priority: str,
    full_roots: set,
    abbr_roots: set,
    abbr_to_full: Dict[str, List[str]] = None,
    abbr_max_len: int = DEFAULT_ABBR_MAX_LEN,
) -> List[str]:
    errors = []
    mode = normalize_priority(priority)
    abbr_to_full = abbr_to_full or {}
    max_len = resolve_abbr_max_len(abbr_max_len)
    full_root_words = set()
    if mode == "full":
        for full_root in full_roots:
            full_root_words.update(split_identifier(full_root))

    for root in split_identifier(identifier):
        if mode == "full" and root in abbr_roots and root not in full_roots and root not in full_root_words:
            suggestions = abbr_to_full.get(root, [])
            suffix = f", consider using {', '.join(suggestions)}" if suggestions else ""
            errors.append(f"identifier '{identifier}' uses abbreviated root '{root}'{suffix}")
        elif mode == "abbr" and len(root) > max_len:
            errors.append(f"identifier '{identifier}' contains abbreviated root '{root}' longer than {max_len} characters")

    return errors


def filter_translation_by_mode(
    chinese_root: str,
    english_root: str,
    priority: str,
    full_roots: set,
    abbr_roots: set,
    abbr_to_full: Dict[str, List[str]] = None,
    abbr_max_len: int = DEFAULT_ABBR_MAX_LEN,
) -> Tuple[bool, str]:
    root = (english_root or "").strip().strip("`\"'").rstrip("_").lower()
    if not root:
        return False, "root is empty"

    errors = validate_identifier_mode(root, priority, full_roots, abbr_roots, abbr_to_full, abbr_max_len)
    if errors:
        return False, f"{chinese_root}: {'; '.join(errors)}"
    return True, root
