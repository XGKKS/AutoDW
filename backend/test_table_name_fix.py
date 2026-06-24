#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.processors.field_processor import FieldProcessor


def test_table_name_does_not_repeat_layer_prefix():
    roots = [
        {"chinese_name": "商品", "full_root": "product", "abbr_root": "prod"},
        {"chinese_name": "订单", "full_root": "order", "abbr_root": "orde"},
        {"chinese_name": "销售", "full_root": "sales", "abbr_root": "sale"},
        {"chinese_name": "汇总", "full_root": "summary", "abbr_root": "summ"},
        {"chinese_name": "ID", "full_root": "id", "abbr_root": "id"},
        {"chinese_name": "名称", "full_root": "name", "abbr_root": "name"},
        {"chinese_name": "品牌", "full_root": "brand", "abbr_root": "bran"},
    ]
    processor = FieldProcessor(
        api_key="test",
        api_url="http://localhost",
        model="test",
        word_roots=roots,
        root_match_priority="full",
    )

    assert processor.translate_table_name("商品维度表", "dim") == "product"
    assert processor.translate_table_name("订单明细表", "dwd") == "order"
    assert processor.translate_table_name("销售汇总表", "dws") == "sales_summary"

    table_info = {
        "layer": "dim",
        "fields": [
            {"name": "商品ID", "type": "VARCHAR(64)"},
            {"name": "商品名称", "type": "VARCHAR(128)"},
            {"name": "品牌名称", "type": "VARCHAR(64)"},
        ],
    }
    field_mapping = {
        "商品ID": ("product_id", "VARCHAR(64)"),
        "商品名称": ("product_name", "VARCHAR(128)"),
        "品牌名称": ("brand_name", "VARCHAR(64)"),
    }

    ddl = processor.generate_ddl_for_table("商品维度表", table_info, field_mapping, db_type="postgresql")

    assert 'CREATE TABLE "dim"."product"' in ddl
    assert '"dim"."dim_' not in ddl
