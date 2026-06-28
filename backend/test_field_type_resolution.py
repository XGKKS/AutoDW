#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io

import openpyxl
import pytest

from app.field_type_resolver import normalize_field_type, resolve_field_type
from app.main import parse_batch_table_excel
from app.processors.field_processor import FieldProcessor


def _build_excel(rows):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["表名", "表分层", "字段名", "推荐字段类型"])
    for row in rows:
        sheet.append(row)

    output = io.BytesIO()
    workbook.save(output)
    return output.getvalue()


def test_resolve_field_type_prefers_excel_type_and_normalizes_format():
    assert normalize_field_type("decimal（18，6）") == "DECIMAL(18,6)"
    assert resolve_field_type("订单金额", "decimal（18，6）") == "DECIMAL(18,6)"
    assert resolve_field_type("创建时间", "") == "DATETIME"
    assert resolve_field_type("创建人", "") == "VARCHAR(128)"
    assert resolve_field_type("创建人ID", "") == "VARCHAR(64)"
    assert resolve_field_type("更新人", None) == "VARCHAR(128)"
    assert resolve_field_type("订单数量", None) == "INT"
    assert resolve_field_type("客户名称", None) == "VARCHAR(128)"


def test_extract_fields_from_excel_recommends_missing_types():
    processor = FieldProcessor("", "", "", word_roots=[], root_match_priority="full")
    content = _build_excel([
        ["订单表", "dwd", "创建时间", ""],
        ["订单表", "dwd", "创建人", ""],
        ["订单表", "dwd", "订单数量", None],
        ["订单表", "dwd", "订单金额", "decimal（18，6）"],
        ["订单表", "dwd", "客户名称", ""],
    ])

    tables, all_fields = processor.extract_fields_from_excel(content)

    assert len(all_fields) == 5
    types = {field["name"]: field["type"] for field in tables["订单表"]["fields"]}
    assert types["创建时间"] == "DATETIME"
    assert types["创建人"] == "VARCHAR(128)"
    assert types["订单数量"] == "INT"
    assert types["订单金额"] == "DECIMAL(18,6)"
    assert types["客户名称"] == "VARCHAR(128)"


def test_legacy_batch_parser_uses_same_type_resolution():
    content = _build_excel([
        ["订单表", "dwd", "统计日期", ""],
        ["订单表", "dwd", "销售数量", ""],
        ["订单表", "dwd", "销售金额", "DECIMAL（18，6）"],
    ])

    tables = parse_batch_table_excel(content)

    types = {field["name"]: field["type"] for field in tables["订单表"]["fields"]}
    assert types["统计日期"] == "DATETIME"
    assert types["销售数量"] == "INT"
    assert types["销售金额"] == "DECIMAL(18,6)"


def test_build_field_mapping_repairs_same_table_duplicate_english_names(monkeypatch):
    processor = FieldProcessor("", "", "", word_roots=[], root_match_priority="full")
    tables_data = {
        "维修工单表": {
            "layer": "dwd",
            "fields": [
                {"name": "送修人", "type": "VARCHAR(128)", "field_index": 1},
                {"name": "送单人", "type": "VARCHAR(128)", "field_index": 2},
            ],
        }
    }

    monkeypatch.setattr(
        processor,
        "process_fields_root_level",
        lambda groups: (
            {
                "送修人": ("send_pers", "VARCHAR(128)"),
                "送单人": ("send_pers", "VARCHAR(128)"),
            },
            {"matched_count": 0, "unmatched_count": 0, "total_fields": 2, "new_roots_count": 0},
            {},
        ),
    )

    monkeypatch.setattr(
        processor,
        "_request_duplicate_field_name_fix",
        lambda conflict: {
            ("维修工单表", 1, "送修人"): ("repair_sender", "VARCHAR(128)"),
            ("维修工单表", 2, "送单人"): ("dispatch_sender", "VARCHAR(128)"),
        },
    )

    _tables, field_mapping, _stats, _roots = processor.build_field_mapping(tables_data=tables_data)

    assert field_mapping["送修人"][0] == "repair_sender"
    assert field_mapping["送单人"][0] == "dispatch_sender"


def test_build_field_mapping_fails_only_when_duplicate_fix_still_conflicts(monkeypatch):
    processor = FieldProcessor("", "", "", word_roots=[], root_match_priority="full")
    tables_data = {
        "维修工单表": {
            "layer": "dwd",
            "fields": [
                {"name": "送修人", "type": "VARCHAR(128)", "field_index": 1},
                {"name": "送单人", "type": "VARCHAR(128)", "field_index": 2},
            ],
        }
    }

    monkeypatch.setattr(
        processor,
        "process_fields_root_level",
        lambda groups: (
            {
                "送修人": ("send_pers", "VARCHAR(128)"),
                "送单人": ("send_pers", "VARCHAR(128)"),
            },
            {"matched_count": 0, "unmatched_count": 0, "total_fields": 2, "new_roots_count": 0},
            {},
        ),
    )

    monkeypatch.setattr(
        processor,
        "_request_duplicate_field_name_fix",
        lambda conflict: {
            ("维修工单表", 1, "送修人"): ("send_pers", "VARCHAR(128)"),
            ("维修工单表", 2, "送单人"): ("send_pers", "VARCHAR(128)"),
        },
    )

    with pytest.raises(ValueError, match="自动修正后仍未消除"):
        processor.build_field_mapping(tables_data=tables_data)


def test_generate_ddl_converts_recommended_types_by_database():
    processor = FieldProcessor("", "", "", word_roots=[], root_match_priority="full")
    table_info = {
        "layer": "dwd",
        "fields": [
            {"name": "创建时间", "type": "DATETIME"},
            {"name": "订单数量", "type": "INT"},
            {"name": "订单金额", "type": "DECIMAL(18,6)"},
        ],
    }
    field_mapping = {
        "创建时间": ("create_time", "DATETIME"),
        "订单数量": ("order_qty", "INT"),
        "订单金额": ("order_amount", "DECIMAL(18,6)"),
    }

    mysql_ddl = processor.generate_ddl_for_table("订单表", table_info, field_mapping, db_type="mysql")
    postgres_ddl = processor.generate_ddl_for_table("订单表", table_info, field_mapping, db_type="postgresql")
    oracle_ddl = processor.generate_ddl_for_table("订单表", table_info, field_mapping, db_type="oracle")

    assert "`create_time` DATETIME" in mysql_ddl
    assert "`order_qty` INT" in mysql_ddl
    assert "`order_amount` DECIMAL(18,6)" in mysql_ddl

    assert '"create_time" TIMESTAMP' in postgres_ddl
    assert '"order_qty" INTEGER' in postgres_ddl
    assert '"order_amount" DECIMAL(18,6)' in postgres_ddl

    assert '"CREATE_TIME" DATE' in oracle_ddl
    assert '"ORDER_QTY" NUMBER(10)' in oracle_ddl
    assert '"ORDER_AMOUNT" NUMBER(18,6)' in oracle_ddl
