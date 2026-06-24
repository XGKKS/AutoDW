#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试表名修复效果
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.processors.field_processor import FieldProcessor

processor = FieldProcessor(
    api_key="test",
    api_url="http://localhost",
    model="test",
    word_roots=[],
    root_match_priority="full"
)

# 测试商品维度表，layer=dim
print("Test 1: 商品维度表 (layer=dim)")
english_name = processor.translate_table_name('商品维度表', 'dim')
print(f"  Input: 商品维度表")
print(f"  Output: {english_name}")
print(f"  Expected: item_info")
print(f"  PASS: {english_name == 'item_info'}")
print()

# 测试订单明细表，layer=dwd
print("Test 2: 订单明细表 (layer=dwd)")
english_name = processor.translate_table_name('订单明细表', 'dwd')
print(f"  Input: 订单明细表")
print(f"  Output: {english_name}")
print(f"  Expected: order_detail")
print(f"  PASS: {english_name == 'order_detail'}")
print()

# 测试完整DDL生成
print("Test 3: PostgreSQL DDL - 商品维度表")
table_info = {
    'layer': 'dim',
    'fields': [
        {'name': '商品ID', 'type': 'VARCHAR(64)'},
        {'name': '商品名称', 'type': 'VARCHAR(128)'},
    ]
}

field_mapping = {
    '商品ID': ('item_id', 'VARCHAR(64)'),
    '商品名称': ('item_name', 'VARCHAR(128)'),
}

ddl = processor.generate_ddl_for_table('商品维度表', table_info, field_mapping, db_type='postgresql')
print(ddl)
has_correct_name = '"dim"."item_info"' in ddl
print(f"\n  Table name correct (dim.item_info): {has_correct_name}")