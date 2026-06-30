from pathlib import Path

import pytest

from app.prompt_segments import (
    get_prompt_segments_file,
    get_prompt_segments_legacy_file,
    load_prompt_segments,
    load_prompt_segments_response,
    render_prompt_segment,
    save_prompt_segment,
)


def test_load_prompt_segments_returns_safe_dto(tmp_path):
    segments = load_prompt_segments(str(tmp_path))

    assert len(segments) == 6
    first = segments[0]
    assert "system_prompt" not in first
    assert "user_prompt" not in first
    assert "guidance" in first
    assert "preview_system_prompt" in first
    assert "preview_user_prompt" in first
    assert "{description}" not in first["preview_user_prompt"]


def test_save_and_render_guidance_keeps_runtime_placeholders_safe(tmp_path):
    save_prompt_segment(
        str(tmp_path),
        "root_semantic_normalize",
        {"guidance": "若出现“预计{金额}”这类写法，也按业务同义判断。\n优先沿用已有标准词根。"},
    )

    segments = load_prompt_segments(str(tmp_path))
    current = next(item for item in segments if item["key"] == "root_semantic_normalize")
    assert "预计{金额}" in current["guidance"]
    assert "本阶段补充要求" in current["preview_user_prompt"]

    rendered = render_prompt_segment(
        str(tmp_path),
        "root_semantic_normalize",
        {
            "roots_text": "预计\n预估",
            "history_text": "金额:amount",
            "style_guide": "统一使用全称词根",
        },
    )
    assert "预计{金额}" in rendered["user_prompt"]
    assert "金额:amount" in rendered["user_prompt"]


def test_legacy_prompt_segment_store_is_backed_up_and_migrated(tmp_path):
    prompt_file = Path(get_prompt_segments_file(str(tmp_path)))
    prompt_file.write_text(
        """
[
  {
    "key": "text_schema_extract",
    "system_prompt": "legacy system",
    "user_prompt": "legacy user"
  }
]
        """.strip(),
        encoding="utf-8",
    )

    segments, migration_notice = load_prompt_segments_response(str(tmp_path))

    assert migration_notice
    assert len(segments) == 6
    assert Path(get_prompt_segments_legacy_file(str(tmp_path))).exists()
    assert prompt_file.exists()
    assert '"guidance"' in prompt_file.read_text(encoding="utf-8")


def test_save_prompt_segment_rejects_extra_fields(tmp_path):
    with pytest.raises(ValueError):
        save_prompt_segment(
            str(tmp_path),
            "text_schema_extract",
            {"guidance": "只抽取主表", "system_prompt": "forbidden"},
        )
