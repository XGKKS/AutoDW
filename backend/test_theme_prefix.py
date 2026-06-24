#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Theme prefix regression tests.
"""

from app.processors.field_processor import FieldProcessor
from app.root_policy import infer_theme_prefix
from app.validators.ddl_validator import DDLValidator


STANDARDS = """## \u8868\u547d\u540d\u89c4\u8303
| \u4e3b\u9898\u57df | \u7f29\u5199 |
| \u516c\u5171 | pub |
| \u5546\u54c1 | prod |
| \u8ba2\u5355 | order |
"""


def test_infer_theme_prefix_from_standards():
    assert infer_theme_prefix("\u5546\u54c1\u7ef4\u5ea6\u8868", standards_content=STANDARDS) == "prod"
    assert infer_theme_prefix("\u8ba2\u5355\u660e\u7ec6\u8868", standards_content=STANDARDS) == "order"
    assert infer_theme_prefix("\u516c\u5171\u660e\u7ec6\u8868", standards_content=STANDARDS) == "pub"


def test_translate_table_name_keeps_theme_prefix():
    processor = FieldProcessor(
        "",
        "",
        "",
        word_roots=[
            {"chinese_name": "\u660e\u7ec6", "full_root": "detail", "abbr_root": "dtl", "recommended_type": "VARCHAR(64)"}
        ],
        standards=STANDARDS,
    )

    translated = processor.translate_table_name("\u5546\u54c1\u660e\u7ec6\u8868", "dwd")
    assert translated.startswith("prod_")


def test_validator_ignores_theme_prefix_for_table_names():
    validator = DDLValidator([], standards={"content": STANDARDS}, root_match_priority="full")
    violations = validator.validate_table_name("dwd_prod_detail")
    assert not any(v.get("level") == "error" for v in violations)


if __name__ == "__main__":
    test_infer_theme_prefix_from_standards()
    test_translate_table_name_keeps_theme_prefix()
    test_validator_ignores_theme_prefix_for_table_names()
    print("theme prefix tests passed")
