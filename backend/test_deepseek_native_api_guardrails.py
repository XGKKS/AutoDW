#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from app.main import add_deepseek_thinking_body
from app.processors.field_processor import FieldProcessor


def test_reasoning_only_response_is_treated_as_empty():
    processor = FieldProcessor("", "", "")
    result = {
        "choices": [
            {"message": {"reasoning_content": "先思考，但没有最终 content"}}
        ]
    }

    assert processor._extract_llm_content(result) == ""



def test_deepseek_native_api_disables_thinking_body():
    payload = {"model": "deepseek-v4-flash"}

    result = add_deepseek_thinking_body("https://api.deepseek.com", payload)

    assert result["thinking"] == {"type": "disabled"}

def test_single_theme_table_name_is_rejected():
    processor = FieldProcessor("", "", "", root_match_priority="abbr")

    assert not processor._is_safe_table_body("pub", "pub")
    assert not processor._is_safe_table_body("tbl", "pub")
    assert processor._is_safe_table_body("pub_order", "pub")


def test_abbr_field_repair_uses_valid_short_fallback_without_unbounded_field_loop():
    processor = FieldProcessor("", "", "", root_match_priority="abbr")

    repaired = processor._repair_field_name("合同证书", "")

    assert repaired == "fld"
    assert processor._is_safe_generated_identifier(repaired, "test field")


def test_repair_table_name_fails_for_untranslated_theme_only_name():
    processor = FieldProcessor("", "", "", root_match_priority="abbr")

    with pytest.raises(ValueError, match="业务表名"):
        processor._repair_table_name("年度计划表", "pub", "fill", "pub")


def test_root_translation_prompt_starts_with_meaningful_name_guard(monkeypatch):
    captured = {}

    class Response:
        status_code = 200
        encoding = "utf-8"

        def json(self):
            return {"choices": [{"message": {"content": "订单:ord"}}]}

    def fake_post(url, headers, json, timeout):
        captured["prompt"] = json["messages"][1]["content"]
        return Response()

    processor = FieldProcessor(
        "key",
        "https://api.deepseek.com",
        "deepseek-test",
        root_match_priority="abbr",
    )
    monkeypatch.setattr("app.processors.field_processor.requests.post", fake_post)

    processor._translate_roots_batch(["订单"])

    assert captured["prompt"].startswith("请为以下中文业务词根生成英文翻译，严禁使用无意义的命名翻译")

def test_field_processor_only_adds_thinking_for_deepseek_native():
    deepseek_processor = FieldProcessor("key", "https://api.deepseek.com", "deepseek-test")
    openai_processor = FieldProcessor("key", "https://api.openai.com/v1", "gpt-test")

    deepseek_payload = deepseek_processor._prepare_llm_payload({"model": "deepseek-test"})
    openai_payload = openai_processor._prepare_llm_payload({"model": "gpt-test"})

    assert deepseek_payload["thinking"] == {"type": "disabled"}
    assert "thinking" not in openai_payload

