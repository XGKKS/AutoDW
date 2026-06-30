#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

import pytest

from app.processors.field_processor import FieldProcessor


def _roots():
    return [
        {"chinese_name": "400", "full_root": "four_hundred", "abbr_root": "400", "recommended_type": "VARCHAR(255)"},
        {"chinese_name": "工单", "full_root": "ticket", "abbr_root": "tkt", "recommended_type": "VARCHAR(255)"},
        {"chinese_name": "反馈", "full_root": "feedback", "abbr_root": "feed", "recommended_type": "VARCHAR(255)"},
        {"chinese_name": "派单", "full_root": "dispatch", "abbr_root": "disp", "recommended_type": "VARCHAR(255)"},
        {"chinese_name": "申请", "full_root": "apply", "abbr_root": "appl", "recommended_type": "VARCHAR(255)"},
        {"chinese_name": "结案", "full_root": "close", "abbr_root": "clos", "recommended_type": "VARCHAR(255)"},
        {"chinese_name": "主键", "full_root": "primary_key", "abbr_root": "pk", "recommended_type": "VARCHAR(64)"},
        {"chinese_name": "ID", "full_root": "id", "abbr_root": "id", "recommended_type": "VARCHAR(64)"},
    ]


def test_table_name_uses_root_library_longest_match_full_mode():
    processor = FieldProcessor("", "", "", word_roots=_roots(), root_match_priority="full")

    translated = {
        table_name: processor.translate_table_name(table_name, "dwd")
        for table_name in ["400工单反馈表", "400工单派单表", "400工单申请结案表"]
    }

    assert translated == {
        "400工单反馈表": "ticket_feedback",
        "400工单派单表": "ticket_dispatch",
        "400工单申请结案表": "ticket_apply_close",
    }
    assert len(set(translated.values())) == len(translated)


def test_table_name_uses_root_library_longest_match_abbr_mode():
    processor = FieldProcessor("", "", "", word_roots=_roots(), root_match_priority="abbr")

    translated = {
        table_name: processor.translate_table_name(table_name, "dwd")
        for table_name in ["400工单反馈表", "400工单派单表", "400工单申请结案表"]
    }

    assert translated == {
        "400工单反馈表": "tkt_feed",
        "400工单派单表": "tkt_disp",
        "400工单申请结案表": "tkt_appl_clos",
    }
    assert len(set(translated.values())) == len(translated)


def test_generated_mysql_ddl_uses_distinct_table_names_from_root_library():
    processor = FieldProcessor("", "", "", word_roots=_roots(), root_match_priority="abbr")
    table_info = {
        "layer": "dwd",
        "fields": [{"name": "主键ID", "type": "VARCHAR(64)"}],
    }
    field_mapping = {"主键ID": ("pk_id", "VARCHAR(64)")}

    ddls = [
        processor.generate_ddl_for_table(table_name, table_info, field_mapping, db_type="mysql")
        for table_name in ["400工单反馈表", "400工单派单表", "400工单申请结案表"]
    ]
    created_tables = [
        re.search(r"CREATE TABLE `([^`]+)`", ddl).group(1)
        for ddl in ddls
    ]

    assert created_tables == [
        "dwd_tkt_feed",
        "dwd_tkt_disp",
        "dwd_tkt_appl_clos",
    ]
    assert len(set(created_tables)) == len(created_tables)
    assert "dwd_tbl" not in created_tables


def test_missing_table_roots_fail_instead_of_using_placeholder_name():
    processor = FieldProcessor(
        "",
        "",
        "",
        word_roots=[{"chinese_name": "工单", "full_root": "ticket", "abbr_root": "tkt"}],
        root_match_priority="abbr",
    )

    with pytest.raises(ValueError, match="表名"):
        processor.translate_table_name("年度计划表", "dwd")


def test_llm_table_name_extracts_identifier_from_create_table_response(monkeypatch):
    processor = FieldProcessor(
        "test-key",
        "http://llm.example/v1",
        "test-model",
        word_roots=[
            {"chinese_name": "生产", "full_root": "product", "abbr_root": "prod"},
            {"chinese_name": "计划", "full_root": "plan", "abbr_root": "plan"},
        ],
        root_match_priority="abbr",
    )

    class Response:
        status_code = 200
        encoding = "utf-8"

        def json(self):
            return {"choices": [{"message": {"content": "CREATE TABLE dwd_prod_plan"}}]}

    monkeypatch.setattr(processor, "_post_llm", lambda payload, timeout: Response())

    assert processor.generate_table_name("年度计划表", "mysql", "enable llm", "dwd") == "prod_plan"
