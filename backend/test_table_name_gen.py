#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试表名LLM生成功能
"""
import os
import sys

# 添加 app 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.processors.field_processor import FieldProcessor


def test_table_name_generation():
    """测试表名生成功能"""
    print("=" * 80)
    print("表名LLM生成测试")
    print("=" * 80)
    
    # 创建 FieldProcessor 实例（使用测试配置）
    processor = FieldProcessor(
        api_key="test",
        api_url="http://localhost:8000/v1",
        model="test",
        word_roots=[],
        root_match_priority="full"
    )
    
    # 测试表名转换（fallback模式，不调用LLM）
    print("\n[Fallback模式 - 不调用LLM]")
    print("-" * 80)
    
    test_cases = ['入库明细表', '订单明细表', '商品维度表']
    for chinese_name in test_cases:
        english_name = processor.translate_table_name(chinese_name)
        print(f"  '{chinese_name}' -> '{english_name}'")
    
    # 测试不同数据库类型的表名示例
    print("\n[数据库类型表名格式示例]")
    print("-" * 80)
    print(f"  MySQL: dwd_fin_order")
    print(f"  PostgreSQL: dwd.fin_order")
    print(f"  Oracle: DWD.FIN_ORDER")
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    test_table_name_generation()
