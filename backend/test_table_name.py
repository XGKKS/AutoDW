#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.processors.field_processor import FieldProcessor


def _roots():
    return [
        {"chinese_name": "商品", "full_root": "product", "abbr_root": "prod", "recommended_type": "VARCHAR(255)"},
        {"chinese_name": "仓库", "full_root": "warehouse", "abbr_root": "wh", "recommended_type": "VARCHAR(255)"},
        {"chinese_name": "优惠券", "full_root": "coupon", "abbr_root": "coup", "recommended_type": "VARCHAR(255)"},
        {"chinese_name": "订单", "full_root": "order", "abbr_root": "orde", "recommended_type": "VARCHAR(255)"},
        {"chinese_name": "入库", "full_root": "inbound", "abbr_root": "inbo", "recommended_type": "VARCHAR(255)"},
        {"chinese_name": "ID", "full_root": "id", "abbr_root": "id", "recommended_type": "VARCHAR(64)"},
        {"chinese_name": "时间", "full_root": "time", "abbr_root": "time", "recommended_type": "DATETIME"},
    ]


def test_table_name_translation_uses_root_library():
    processor = FieldProcessor(
        api_key="test",
        api_url="http://localhost",
        model="test",
        word_roots=_roots(),
        root_match_priority="full",
    )

    assert processor.translate_table_name("商品维度表") == "product"
    assert processor.translate_table_name("仓库维度表") == "warehouse"
    assert processor.translate_table_name("优惠券维度表") == "coupon"
    assert processor.translate_table_name("订单明细表") == "order"
    assert processor.translate_table_name("入库明细表") == "inbound"


def test_postgresql_ddl_uses_root_library_table_name():
    processor = FieldProcessor(
        api_key="test",
        api_url="http://localhost",
        model="test",
        word_roots=_roots(),
        root_match_priority="full",
    )
    table_info = {
        "layer": "dwd",
        "fields": [
            {"name": "入库ID", "type": "VARCHAR(64)"},
            {"name": "仓库ID", "type": "VARCHAR(64)"},
            {"name": "入库时间", "type": "DATETIME"},
        ],
    }
    field_mapping = {
        "入库ID": ("inbound_id", "VARCHAR(64)"),
        "仓库ID": ("warehouse_id", "VARCHAR(64)"),
        "入库时间": ("inbound_time", "TIMESTAMP"),
    }

    ddl = processor.generate_ddl_for_table("入库明细表", table_info, field_mapping, db_type="postgresql")

    assert 'CREATE TABLE "dwd"."inbound"' in ddl
