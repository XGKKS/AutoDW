# -*- coding: utf-8 -*-
import json, os, logging, uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STANDARD_ROOTS_FILE = os.path.join(BASE_DIR, 'standard_roots.json')
HISTORICAL_ROOTS_FILE = os.path.join(BASE_DIR, 'historical_roots.json')
ROOT_MAPPING_FILE = os.path.join(BASE_DIR, 'root_mapping.json')
LEGACY_WORD_ROOTS_FILE = os.path.join(BASE_DIR, 'word_roots.json')

BUSINESS_DOMAINS = {
    'fin': '财务',
    'prod': '生产',
    'ord': '订单',
    'cust': '客户',
    'pub': '通用',
    'log': '物流',
    'mkt': '营销',
}

GOVERNANCE_CHUNK_SIZE = 50
GOVERNANCE_MERGE_CHUNK_SIZE = 20


def _now_iso() -> str:
    return datetime.now().isoformat(timespec='seconds')


def _standard_root_key(root: dict) -> tuple:
    return (
        str(root.get('domain_code') or '').strip().lower(),
        str(root.get('business_domain') or '').strip().lower(),
        str(root.get('chinese_name') or '').strip().lower(),
        str(root.get('full_root') or '').strip().lower(),
        str(root.get('abbr_root') or '').strip().lower(),
        str(root.get('recommended_type') or '').strip().lower(),
    )


def _standard_root_edit_fields(root: dict) -> dict:
    return {
        'domain_code': str(root.get('domain_code') or '').strip().lower(),
        'business_domain': str(root.get('business_domain') or '').strip(),
        'chinese_name': str(root.get('chinese_name') or '').strip(),
        'full_root': str(root.get('full_root') or '').strip(),
        'abbr_root': str(root.get('abbr_root') or '').strip(),
        'recommended_type': str(root.get('recommended_type') or '').strip(),
        'governance_status': str(root.get('governance_status') or 'governed').strip(),
        'merged_from': root.get('merged_from') if isinstance(root.get('merged_from'), list) else [],
    }


def _normalize_change_history(history: Any) -> list:
    if not isinstance(history, list):
        return []
    normalized = []
    for item in history:
        if not isinstance(item, dict):
            continue
        normalized.append({
            'edited_at': str(item.get('edited_at') or '').strip(),
            'action': str(item.get('action') or 'edited').strip() or 'edited',
            'before': item.get('before') if isinstance(item.get('before'), dict) else {},
            'after': item.get('after') if isinstance(item.get('after'), dict) else {},
        })
    return normalized


def _select_recommended_type_from_historical(root: dict, historical_roots: list) -> str:
    candidates = []
    chinese_name = str(root.get('chinese_name') or '').strip().lower()
    full_root = str(root.get('full_root') or '').strip().lower()
    abbr_root = str(root.get('abbr_root') or '').strip().lower()
    for item in historical_roots or []:
        if not isinstance(item, dict):
            continue
        item_type = str(item.get('recommended_type') or '').strip()
        if not item_type:
            continue
        item_chinese = str(item.get('chinese_name') or '').strip().lower()
        item_full = str(item.get('full_root') or '').strip().lower()
        item_abbr = str(item.get('abbr_root') or '').strip().lower()
        if (
            (chinese_name and item_chinese == chinese_name) or
            (full_root and item_full == full_root) or
            (abbr_root and item_abbr == abbr_root)
        ):
            candidates.append(item_type)
    if not candidates:
        return ''
    counts = {}
    for candidate in candidates:
        counts[candidate] = counts.get(candidate, 0) + 1
    return max(counts.items(), key=lambda item: item[1])[0]


def normalize_standard_root_record(root: dict, existing: Optional[dict] = None) -> dict:
    existing = existing if isinstance(existing, dict) else {}
    current = _standard_root_edit_fields(root)
    now = _now_iso()
    normalized = {
        **current,
        'root_id': str(root.get('root_id') or existing.get('root_id') or uuid.uuid4().hex),
        'usage_count': int(root.get('usage_count') or existing.get('usage_count') or root.get('source_count') or 1),
        'created_at': str(root.get('created_at') or existing.get('created_at') or now),
        'updated_at': str(root.get('updated_at') or existing.get('updated_at') or now),
        'change_history': _normalize_change_history(root.get('change_history') or existing.get('change_history')),
    }

    previous = _standard_root_edit_fields(existing) if existing else None
    if previous is None:
        normalized['change_history'].append({
            'edited_at': normalized['created_at'],
            'action': 'created',
            'before': {},
            'after': current,
        })
    elif previous != current:
        normalized['updated_at'] = now
        normalized['change_history'].append({
            'edited_at': now,
            'action': 'edited',
            'before': previous,
            'after': current,
        })

    return normalized


def enrich_standard_roots_with_historical_types(roots: list, historical_roots: list) -> list:
    enriched = []
    for root in roots or []:
        if not isinstance(root, dict):
            continue
        current_type = str(root.get('recommended_type') or '').strip()
        if not current_type or current_type.upper() == 'VARCHAR(64)':
            inferred_type = _select_recommended_type_from_historical(root, historical_roots)
            if inferred_type:
                root = {**root, 'recommended_type': inferred_type}
        enriched.append(root)
    return enriched

def _load_json(path: str) -> list:
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    logger.warning(f"词根文件格式异常，期望 list 但实际为 {type(data).__name__}: {path}")
                    return []
                return data
        except Exception as e:
            logger.exception(f"读取词根文件失败: {path} -> {e}")
            raise
    return []

def _save_json(path: str, data: list):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_standard_roots() -> list:
    raw_roots = _load_json(STANDARD_ROOTS_FILE)
    roots = []
    changed = False
    for root in raw_roots:
        if not isinstance(root, dict):
            continue
        normalized = normalize_standard_root_record(root, root)
        if normalized != root:
            changed = True
        roots.append(normalized)
    if changed:
        _save_json(STANDARD_ROOTS_FILE, roots)
    logger.info(f"加载标准词根文件: {STANDARD_ROOTS_FILE}, 共 {len(roots)} 条")
    return roots

def save_standard_roots(roots: list):
    existing = load_standard_roots() if os.path.exists(STANDARD_ROOTS_FILE) else []
    existing_by_id = {
        str(root.get('root_id') or '').strip(): root
        for root in existing
        if isinstance(root, dict) and str(root.get('root_id') or '').strip()
    }
    existing_by_key = {
        _standard_root_key(root): root
        for root in existing
        if isinstance(root, dict)
    }
    normalized_roots = []
    for root in roots:
        if not isinstance(root, dict):
            continue
        root_id = str(root.get('root_id') or '').strip()
        existing_root = existing_by_id.get(root_id) if root_id else None
        if existing_root is None:
            existing_root = existing_by_key.get(_standard_root_key(root))
        normalized_roots.append(normalize_standard_root_record(root, existing_root))
    _save_json(STANDARD_ROOTS_FILE, normalized_roots)

def load_historical_roots() -> list:
    roots = _load_json(HISTORICAL_ROOTS_FILE)
    logger.info(f"加载治理历史词根文件: {HISTORICAL_ROOTS_FILE}, 共 {len(roots)} 条")
    return roots

def save_historical_roots(roots: list):
    _save_json(HISTORICAL_ROOTS_FILE, roots)

def load_legacy_historical_roots() -> list:
    roots = _load_json(LEGACY_WORD_ROOTS_FILE)
    logger.info(f"加载旧版词根文件: {LEGACY_WORD_ROOTS_FILE}, 共 {len(roots)} 条")
    return roots

def load_effective_historical_roots() -> list:
    roots = load_historical_roots()
    if roots:
        logger.info(f"词根治理使用历史词根源: {HISTORICAL_ROOTS_FILE}")
        return roots
    legacy = load_legacy_historical_roots()
    logger.info(f"词根治理回退到旧版词根源: {LEGACY_WORD_ROOTS_FILE}")
    return legacy

def save_effective_historical_roots(roots: list):
    save_historical_roots(roots)

def load_root_mapping() -> list:
    return _load_json(ROOT_MAPPING_FILE)

def save_root_mapping(mapping: list):
    _save_json(ROOT_MAPPING_FILE, mapping)

def migrate_from_legacy(word_roots: list) -> list:
    existing = load_standard_roots()
    if existing:
        return existing
    migrated = []
    for r in word_roots:
        domain = r.get('business_domain', '基础通用')
        domain_code = 'pub'
        for code, name in BUSINESS_DOMAINS.items():
            if name in domain or domain in name:
                domain_code = code
                break
        migrated.append({
            'domain_code': domain_code,
            'business_domain': domain,
            'chinese_name': r.get('chinese_name', ''),
            'full_root': r.get('full_root', ''),
            'abbr_root': r.get('abbr_root', ''),
            'recommended_type': r.get('recommended_type', 'VARCHAR(64)'),
            'governance_status': 'governed',
        })
    save_standard_roots(migrated)
    return migrated


def format_standard_roots_for_prompt(roots: list, priority: str = 'full') -> str:
    if not roots:
        return '(暂无标准词根)'
    lines = []
    for i, r in enumerate(roots, 1):
        domain = r.get('business_domain', '')
        cn = r.get('chinese_name', '')
        full = r.get('full_root', '')
        abbr = r.get('abbr_root', '')
        dtype = r.get('recommended_type', '')
        if priority == 'abbr':
            lines.append(f'{i}. [{domain}] {cn}: {abbr} / {full} ({dtype})')
        else:
            lines.append(f'{i}. [{domain}] {cn}: {full} / {abbr} ({dtype})')
    return chr(10).join(lines)


def add_to_historical_roots(new_root: dict):
    roots = load_effective_historical_roots()
    roots.append(new_root)
    save_historical_roots(roots)


def build_governance_prompt(historical_roots: list, industry_context: str = "") -> str:
    lines = ['请对以下历史词根进行语义归类治理。']
    lines.append('')
    if str(industry_context or '').strip():
        lines.append('【行业背景】')
        lines.append(str(industry_context).strip())
        lines.append('')
    lines.append('要求：')
    lines.append('1. 按业务语义归并（不是按表面文本），解决近义/上下位混杂')
    lines.append('2. 对每个词根补齐：domain_code（从受控枚举选）、chinese_name、full_root、abbr_root、business_domain')
    lines.append('3. 如果只有简称，补齐全称；如果只有全称，补齐缩写')
    lines.append(f'4. domain_code 只能从以下选择：{json.dumps(BUSINESS_DOMAINS, ensure_ascii=False)}')
    lines.append('5. 无法确定业务域时用 pub')
    lines.append('6. 每行只输出一个 JSON 对象，不要输出 JSON 数组，不要输出代码块，不要输出解释')
    lines.append('7. 仅输出对象本身，最后单独输出 END')
    lines.append('')
    lines.append('输出格式示例：')
    lines.append('{"domain_code":"pub","business_domain":"通用","chinese_name":"编号","full_root":"number","abbr_root":"num","governance_status":"governed","merged_from":[0,1,2]}')
    lines.append('END')
    lines.append('')
    lines.append('历史词根列表：')
    for i, r in enumerate(historical_roots):
        lines.append(
            f'{i}. chinese_name={r.get("chinese_name","")} | full_root={r.get("full_root","")} | '
            f'abbr_root={r.get("abbr_root","")} | domain={r.get("business_domain","")} | '
            f'domain_code={r.get("domain_code","")} | source_count={r.get("source_count", 1)}'
        )
    return chr(10).join(lines)


def build_governance_merge_prompt(candidates: list, industry_context: str = "") -> str:
    lines = ['以下是多批次词根治理的中间结果，请进行全局合并与去重。']
    lines.append('')
    if str(industry_context or '').strip():
        lines.append('【行业背景】')
        lines.append(str(industry_context).strip())
        lines.append('')
    lines.append('要求：')
    lines.append('1. 以语义为主，全局合并同义、近义、上下位和重复词根')
    lines.append('2. 对重复或相近项保留最规范、最稳定的表达')
    lines.append('3. 继续补齐 domain_code、business_domain、chinese_name、full_root、abbr_root、recommended_type')
    lines.append(f'4. domain_code 只能从以下选择：{json.dumps(BUSINESS_DOMAINS, ensure_ascii=False)}')
    lines.append('5. 如果无法确定业务域，使用 pub / 通用')
    lines.append('6. 每行只输出一个 JSON 对象，不要输出 JSON 数组，不要输出代码块，不要输出解释')
    lines.append('7. 仅输出对象本身，最后单独输出 END')
    lines.append('')
    lines.append('输出格式示例：')
    lines.append('{"domain_code":"pub","business_domain":"通用","chinese_name":"编号","full_root":"number","abbr_root":"num","governance_status":"governed","merged_from":[0,1,2]}')
    lines.append('END')
    lines.append('')
    lines.append('候选词根列表：')
    for i, r in enumerate(candidates):
        lines.append(
            f'{i}. chinese_name={r.get("chinese_name","")} | full_root={r.get("full_root","")} | '
            f'abbr_root={r.get("abbr_root","")} | domain={r.get("business_domain","")} | '
            f'domain_code={r.get("domain_code","")} | recommended_type={r.get("recommended_type","")}'
        )
    return chr(10).join(lines)


def chunk_roots_for_governance(historical_roots: list, chunk_size: int = GOVERNANCE_CHUNK_SIZE) -> list:
    if chunk_size <= 0:
        chunk_size = GOVERNANCE_CHUNK_SIZE
    return [
        historical_roots[i:i + chunk_size]
        for i in range(0, len(historical_roots), chunk_size)
    ]


def dedupe_governed_roots(roots: list) -> list:
    deduped = []
    seen = set()
    for root in roots or []:
        if not isinstance(root, dict):
            continue
        normalized = {
            'domain_code': str(root.get('domain_code') or 'pub').strip().lower(),
            'business_domain': str(root.get('business_domain') or '').strip(),
            'chinese_name': str(root.get('chinese_name') or '').strip(),
            'full_root': str(root.get('full_root') or '').strip(),
            'abbr_root': str(root.get('abbr_root') or '').strip(),
            'recommended_type': str(root.get('recommended_type') or '').strip(),
            'governance_status': str(root.get('governance_status') or 'governed').strip(),
            'merged_from': root.get('merged_from') if isinstance(root.get('merged_from'), list) else [],
            'usage_count': int(root.get('usage_count') or root.get('source_count') or 1),
        }
        key = (
            normalized.get('domain_code', ''),
            normalized.get('business_domain', '').lower(),
            normalized.get('chinese_name', '').lower(),
            normalized.get('full_root', '').lower(),
            normalized.get('abbr_root', '').lower(),
            normalized.get('recommended_type', '').lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(normalized)
    return deduped


def prepare_historical_roots_for_governance(historical_roots: list) -> list:
    prepared = {}
    for root in historical_roots:
        if not isinstance(root, dict):
            continue
        normalized = {
            'business_domain': str(root.get('business_domain') or '').strip(),
            'domain_code': str(root.get('domain_code') or '').strip(),
            'chinese_name': str(root.get('chinese_name') or '').strip(),
            'full_root': str(root.get('full_root') or '').strip(),
            'abbr_root': str(root.get('abbr_root') or '').strip(),
            'recommended_type': str(root.get('recommended_type') or '').strip(),
        }
        if not normalized['chinese_name']:
            continue

        key = (
            normalized['business_domain'].lower(),
            normalized['domain_code'].lower(),
            normalized['chinese_name'].lower(),
            normalized['full_root'].lower(),
            normalized['abbr_root'].lower(),
            normalized['recommended_type'].lower(),
        )
        if key not in prepared:
            prepared[key] = {**normalized, 'source_count': 0}
        prepared[key]['source_count'] += 1

    return list(prepared.values())


def _normalize_compare_value(value: Any) -> str:
    return str(value or '').strip().lower()


def filter_historical_roots_against_standard(historical_roots: list, standard_roots: list) -> dict:
    standard_chinese = set()
    standard_full = set()
    standard_abbr = set()
    standard_pair = set()

    for root in standard_roots or []:
        if not isinstance(root, dict):
            continue
        chinese_name = _normalize_compare_value(root.get('chinese_name'))
        full_root = _normalize_compare_value(root.get('full_root'))
        abbr_root = _normalize_compare_value(root.get('abbr_root'))
        if chinese_name:
            standard_chinese.add(chinese_name)
        if full_root:
            standard_full.add(full_root)
        if abbr_root:
            standard_abbr.add(abbr_root)
        if full_root or abbr_root:
            standard_pair.add((full_root, abbr_root))

    kept = []
    excluded = []
    for root in historical_roots or []:
        if not isinstance(root, dict):
            continue
        chinese_name = _normalize_compare_value(root.get('chinese_name'))
        full_root = _normalize_compare_value(root.get('full_root'))
        abbr_root = _normalize_compare_value(root.get('abbr_root'))
        matched_standard = (
            (chinese_name and chinese_name in standard_chinese) or
            (full_root and full_root in standard_full) or
            (abbr_root and abbr_root in standard_abbr) or
            ((full_root or abbr_root) and (full_root, abbr_root) in standard_pair)
        )
        if matched_standard:
            excluded.append(root)
        else:
            kept.append(root)

    return {
        'kept': kept,
        'excluded': excluded,
        'excluded_count': len(excluded),
        'kept_count': len(kept),
        'standard_count': len(standard_roots or []),
    }


def apply_governance_result(governed_roots: list):
    existing = load_standard_roots()
    existing_by_key = {}
    for r in existing:
        key = (r.get('full_root',''), r.get('abbr_root',''))
        existing_by_key[key] = r
    for gr in governed_roots:
        key = (gr.get('full_root',''), gr.get('abbr_root',''))
        if key in existing_by_key:
            merged_usage_count = int(existing_by_key[key].get('usage_count') or 1) + int(gr.get('usage_count') or gr.get('source_count') or 1)
            existing_by_key[key].update(gr)
            existing_by_key[key]['usage_count'] = merged_usage_count
        else:
            existing.append(gr)
    save_standard_roots(existing)
    return existing
