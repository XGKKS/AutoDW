#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的字段级处理测试（模拟真实场景）
"""
import json
import os
import sys
import base64
import logging

# 添加 app 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# 设置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from app.processors.field_processor import FieldProcessor
import openpyxl


def load_word_roots():
    """加载词根文件"""
    word_roots_path = os.path.join(os.path.dirname(__file__), 'word_roots.json')
    if os.path.exists(word_roots_path):
        try:
            with open(word_roots_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载词根文件失败: {e}")
            return []
    return []


def simulate_field_level_processing(excel_path):
    """模拟字段级处理流程"""
    print("=" * 80)
    print("字段级处理流程测试（模拟真实场景）")
    print("=" * 80)
    
    # 1. 加载词根
    print("\n[步骤1] 加载历史词根...")
    word_roots = load_word_roots()
    print(f"  词根总数: {len(word_roots)} 条")
    
    # 2. 创建 FieldProcessor
    print("\n[步骤2] 创建 FieldProcessor 实例...")
    processor = FieldProcessor(
        api_key="test_key",
        api_url="http://localhost",
        model="test_model",
        word_roots=word_roots,
        root_match_priority="full"
    )
    print(f"  映射表大小: {len(processor.existing_root_map)} 条")
    
    # 3. 读取 Excel 文件
    print(f"\n[步骤3] 读取 Excel 文件...")
    with open(excel_path, 'rb') as f:
        file_content = f.read()
    print(f"  文件大小: {len(file_content)} bytes")
    
    # 4. 提取字段
    print("\n[步骤4] 提取字段...")
    tables, all_fields = processor.extract_fields_from_excel(file_content)
    print(f"  表数量: {len(tables)} 张")
    print(f"  字段总数: {len(all_fields)} 个")
    
    # 5. 分组
    print("\n[步骤5] 按中文名称分组...")
    groups = processor.group_fields_by_chinese(all_fields)
    print(f"  分组数量: {len(groups)} 个不同的中文字段名")
    
    # 6. 分批处理和词根匹配
    print("\n[步骤6] 分批处理和词根匹配...")
    batches, matched_fields, stats = processor.split_into_batches(groups)
    
    print(f"\n[结果统计]")
    print(f"  总字段数: {stats['total_fields']} 个")
    print(f"  匹配成功: {stats['matched_count']} 个")
    print(f"  未匹配:   {stats['unmatched_count']} 个")
    print(f"  匹配率:   {stats['matched_count']/stats['total_fields']*100:.1f}%")
    print(f"  批次数:   {len(batches)} 批")
    
    # 7. 显示匹配成功的字段
    print(f"\n[匹配成功的字段] ({stats['matched_count']} 个)")
    print("-" * 80)
    for i, (name, (english, field_type)) in enumerate(list(matched_fields.items())[:20], 1):
        print(f"  {i:2d}. {name:20s} -> {english:20s}")
    if len(matched_fields) > 20:
        print(f"  ... 还有 {len(matched_fields) - 20} 个")
    
    # 8. 显示未匹配的字段
    if stats['unmatched_count'] > 0:
        print(f"\n[未匹配的字段] ({stats['unmatched_count']} 个)")
        print("-" * 80)
        # 获取未匹配的字段
        unmatched_groups = {}
        for chinese_name in groups.keys():
            if chinese_name not in matched_fields:
                unmatched_groups[chinese_name] = groups[chinese_name]
        
        for i, name in enumerate(list(unmatched_groups.keys())[:20], 1):
            print(f"  {i:2d}. {name}")
        if len(unmatched_groups) > 20:
            print(f"  ... 还有 {len(unmatched_groups) - 20} 个")
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    # 查找 Excel 文件
    excel_path = os.path.join(os.path.dirname(__file__), '..', 'DDL建表测试用例4表.xlsx')
    if not os.path.exists(excel_path):
        excel_path = os.path.join(os.path.dirname(__file__), 'DDL建表测试用例4表.xlsx')
    
    if not os.path.exists(excel_path):
        print(f"\n错误: Excel文件不存在")
        print(f"查找路径: {excel_path}")
        sys.exit(1)
    
    simulate_field_level_processing(excel_path)
