#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regression tests for naming normalization.
"""

from app.processors.field_processor import FieldProcessor, FieldInfo
from app.validators.ddl_validator import DDLValidator


STANDARDS = """## 表命名规范
| 主题域 | 缩写 |
| 公共 | pub |
| 商品 | prod |
| 订单 | order |
"""


def build_processor():
    return FieldProcessor(
        "",
        "",
        "",
        word_roots=[
            {"chinese_name": "商品", "full_root": "product", "abbr_root": "prod", "recommended_type": "VARCHAR(64)"},
            {"chinese_name": "明细", "full_root": "detail", "abbr_root": "dtl", "recommended_type": "VARCHAR(64)"},
            {"chinese_name": "代码", "full_root": "code", "abbr_root": "code", "recommended_type": "VARCHAR(64)"},
            {"chinese_name": "编号", "full_root": "id", "abbr_root": "id", "recommended_type": "VARCHAR(64)"},
            {"chinese_name": "名称", "full_root": "name", "abbr_root": "name", "recommended_type": "VARCHAR(64)"},
            {"chinese_name": "状态", "full_root": "status", "abbr_root": "sts", "recommended_type": "VARCHAR(64)"},
            {"chinese_name": "门店", "full_root": "store", "abbr_root": "stor", "recommended_type": "VARCHAR(64)"},
        ],
        standards=STANDARDS,
    )


def build_groups(*names):
    groups = {}
    for idx, name in enumerate(names, start=1):
        groups[name] = [
            FieldInfo(
                table_name="demo",
                chinese_name=name,
                suggested_type="VARCHAR(64)",
                table_layer="dwd",
                field_index=idx,
            )
        ]
    return groups


def test_synonym_roots_share_canonical_prefix():
    processor = build_processor()
    field_mapping, _, _ = processor.process_fields_root_level(
        build_groups("主损件代码", "主损件ID", "主店名称", "主店代码")
    )

    assert field_mapping["主损件代码"][0] == "main_damaged_part_code"
    assert field_mapping["主损件ID"][0] == "main_damaged_part_id"
    assert field_mapping["主店名称"][0] == "main_store_name"
    assert field_mapping["主店代码"][0] == "main_store_code"


def test_noise_units_are_removed_from_identifier():
    processor = build_processor()
    field_mapping, _, _ = processor.process_fields_root_level(build_groups("最大车速 (km/h)"))

    assert field_mapping["最大车速 (km/h)"][0] == "maximum_speed"
    assert "(" not in field_mapping["最大车速 (km/h)"][0]
    assert "km" not in field_mapping["最大车速 (km/h)"][0]


def test_acronym_is_preserved_as_atomic_token():
    processor = build_processor()
    field_mapping, _, _ = processor.process_fields_root_level(build_groups("PDC 跟进状态"))

    assert field_mapping["PDC 跟进状态"][0] == "pdc_status"
    assert "pdc" in field_mapping["PDC 跟进状态"][0]


def test_theme_prefix_is_retained_for_table_names():
    processor = build_processor()
    table_name = processor.translate_table_name("商品明细表", "dwd")

    assert table_name.startswith("prod_")

    validator = DDLValidator([], standards={"content": STANDARDS}, root_match_priority="full")
    violations = validator.validate_table_name("dwd_prod_detail")
    assert not any(v.get("level") == "error" for v in violations)


if __name__ == "__main__":
    test_synonym_roots_share_canonical_prefix()
    test_noise_units_are_removed_from_identifier()
    test_acronym_is_preserved_as_atomic_token()
    test_theme_prefix_is_retained_for_table_names()
    print("naming normalization tests passed")
