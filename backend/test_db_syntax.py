#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库语法适配功能
"""
import os
import sys

# 添加 app 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.processors.field_processor import FieldProcessor


def test_db_syntax_adaptation():
    """测试不同数据库类型的DDL生成"""
    print("=" * 80)
    print("数据库语法适配测试")
    print("=" * 80)
    
    # 创建 FieldProcessor 实例
    processor = FieldProcessor(
        api_key="test",
        api_url="http://localhost",
        model="test",
        word_roots=[],
        root_match_priority="full"
    )
    
    # 测试数据
    table_info = {
        'layer': 'dim',
        'fields': [
            {'name': '商品ID', 'type': 'VARCHAR(64)'},
            {'name': '商品名称', 'type': 'VARCHAR(128)'},
            {'name': '创建时间', 'type': 'DATETIME'},
            {'name': '数量', 'type': 'INT'},
            {'name': '金额', 'type': 'DECIMAL(18,4)'},
            {'name': '状态', 'type': 'TINYINT'}
        ]
    }
    
    # 字段映射
    field_mapping = {
        '商品ID': ('item_id', 'VARCHAR(64)'),
        '商品名称': ('item_name', 'VARCHAR(128)'),
        '创建时间': ('create_time', 'DATETIME'),
        '数量': ('qty', 'INT'),
        '金额': ('amount', 'DECIMAL(18,4)'),
        '状态': ('status', 'TINYINT')
    }
    
    # 测试 MySQL
    print("\n[MySQL]")
    print("-" * 80)
    mysql_ddl = processor.generate_ddl_for_table('商品表', table_info, field_mapping, db_type='mysql')
    print(mysql_ddl)
    
    # 测试 PostgreSQL
    print("\n[PostgreSQL]")
    print("-" * 80)
    pg_ddl = processor.generate_ddl_for_table('商品表', table_info, field_mapping, db_type='postgresql')
    print(pg_ddl)
    
    # 测试 Oracle
    print("\n[Oracle]")
    print("-" * 80)
    oracle_ddl = processor.generate_ddl_for_table('商品表', table_info, field_mapping, db_type='oracle')
    print(oracle_ddl)
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    test_db_syntax_adaptation()
