#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

import pytest

from app.config.db_examples import DB_EXAMPLES
from app.main import remove_primary_key_clauses
from app.processors.field_processor import FieldProcessor


ROOTS = [
    {"chinese_name": "测试", "full_root": "test", "abbr_root": "test"},
    {"chinese_name": "ID", "full_root": "id", "abbr_root": "id"},
    {"chinese_name": "创建人", "full_root": "creator", "abbr_root": "crtr"},
    {"chinese_name": "主键", "full_root": "primary_key", "abbr_root": "pk"},
]


@pytest.mark.parametrize("db_type", ["mysql", "postgresql", "oracle"])
def test_generated_ddl_keeps_id_fields_without_primary_key(db_type):
    processor = FieldProcessor(
        "",
        "",
        "",
        word_roots=ROOTS,
        root_match_priority="abbr",
    )
    table_info = {
        "layer": "dwd",
        "fields": [
            {"name": "ID", "type": "VARCHAR(64)"},
            {"name": "创建人ID", "type": "VARCHAR(64)"},
            {"name": "主键ID", "type": "VARCHAR(64)"},
        ],
    }
    field_mapping = {
        "ID": ("id", "VARCHAR(64)"),
        "创建人ID": ("crtr_id", "VARCHAR(64)"),
        "主键ID": ("pk_id", "VARCHAR(64)"),
    }

    ddl = processor.generate_ddl_for_table(
        "测试表",
        table_info,
        field_mapping,
        db_type=db_type,
    )

    assert "PRIMARY KEY" not in ddl.upper()
    assert "ID" in ddl.upper()
    assert "CRTR_ID" in ddl.upper()
    assert "PK_ID" in ddl.upper()


def test_remove_primary_key_clauses_preserves_fields_and_comments():
    ddl = """CREATE TABLE demo (
    id BIGINT PRIMARY KEY,
    `crtr_id` VARCHAR(64),
    PRIMARY KEY (`crtr_id`)
);
COMMENT ON TABLE demo IS '测试表';"""

    cleaned = remove_primary_key_clauses(ddl)

    assert "PRIMARY KEY" not in cleaned.upper()
    assert "id BIGINT," in cleaned
    assert "`crtr_id` VARCHAR(64)," in cleaned
    assert "COMMENT ON TABLE demo" in cleaned


def test_runtime_examples_and_default_standards_do_not_require_primary_keys():
    for config in DB_EXAMPLES.values():
        assert "PRIMARY KEY" not in config["example_full"].upper()
        assert "PRIMARY KEY" not in config["example_abbr"].upper()

    backend_dir = Path(__file__).parent
    default_standards = (backend_dir / "builtin" / "default_standards.md").read_text(encoding="utf-8")
    dev_standards = (backend_dir / "dev_standards.json").read_text(encoding="utf-8")

    for content in (default_standards, dev_standards):
        assert "PRIMARY KEY" not in content.upper()
        assert "pk_词根" not in content
        assert "所有表必须定义主键" not in content
