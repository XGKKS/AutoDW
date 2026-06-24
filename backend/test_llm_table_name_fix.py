#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试LLM生成表名重复问题修复
模拟LLM返回schema.table格式的表名
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.processors.field_processor import FieldProcessor

# 创建测试用的FieldProcessor
processor = FieldProcessor(
    api_key="test",
    api_url="http://localhost",
    model="test",
    word_roots=[],
    root_match_priority="full"
)

# 测试1: 模拟LLM返回 dim.dim_product_info
print("Test 1: 处理LLM返回的 schema.table 格式")
print("=" * 60)
# 模拟LLM返回的表名
llm_table_name = "dim.dim_product_info"
# 处理表名
if '.' in llm_table_name:
    parts = llm_table_name.split('.')
    if parts[-1]:
        llm_table_name = parts[-1]
print(f"  Input: {llm_table_name}")
print(f"  After removing schema: {llm_table_name}")
print()

# 测试2: 测试translate_table_name处理schema.table格式
print("Test 2: translate_table_name处理schema.table格式")
print("=" * 60)
# 模拟一个包含点号的表名（虽然translate_table_name不会返回这种格式，但测试防御性）
english_name = processor.translate_table_name('商品维度表', 'dim')
print(f"  Input: 商品维度表 (layer=dim)")
print(f"  Output: {english_name}")
print(f"  Expected: item_info")
print()

# 测试3: 完整DDL生成 - 模拟LLM返回schema.table格式
print("Test 3: 完整DDL生成")
print("=" * 60)
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

# 检查表名是否正确
if '"dim"."item_info"' in ddl:
    print("\n  ✓ 表名正确: dim.item_info")
elif '"dim"."dim.item_info"' in ddl:
    print("\n  ✗ 表名错误: 仍然包含重复的dim")
else:
    print(f"\n  ? 表名: {ddl.split('\"')[1]}.{ddl.split('\"')[3]}")

# 测试4: 测试修复前的问题场景
print("\n\nTest 4: 模拟修复前的问题场景")
print("=" * 60)
# 修复前：LLM返回 dim.dim_product_info，然后代码又包装一层schema
llm_output = "dim.dim_product_info"
layer = "dim"
# 修复前的逻辑
full_table_name_before = f'"{layer}"."{llm_output}"'
print(f"  LLM返回: {llm_output}")
print(f"  修复前结果: {full_table_name_before}")
# 修复后的逻辑
if '.' in llm_output:
    parts = llm_output.split('.')
    if parts[-1]:
        llm_output = parts[-1]
full_table_name_after = f'"{layer}"."{llm_output}"'
print(f"  修复后结果: {full_table_name_after}")