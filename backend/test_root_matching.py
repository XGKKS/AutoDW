#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试词根匹配功能
"""
import json
import os
import sys

# 添加 app 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.processors.field_processor import FieldProcessor


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
    else:
        print(f"词根文件不存在: {word_roots_path}")
        return []


def test_root_matching():
    """测试词根匹配"""
    print("=" * 60)
    print("词根匹配测试")
    print("=" * 60)
    
    # 1. 加载词根
    print("\n1. 加载词根文件...")
    word_roots = load_word_roots()
    print(f"   共加载 {len(word_roots)} 条词根")
    
    # 打印前 10 条词根
    print(f"\n   前 10 条词根示例:")
    for i, root in enumerate(word_roots[:10]):
        print(f"     {i+1}. {root.get('chinese_name', '')} -> {root.get('full_root', '')}")
    
    # 2. 创建 FieldProcessor 实例
    print("\n2. 创建 FieldProcessor 实例...")
    processor = FieldProcessor(
        api_key="test_key",
        api_url="http://localhost",
        model="test_model",
        word_roots=word_roots,
        root_match_priority="full"
    )
    
    # 3. 测试一些常见的中文名称
    test_names = [
        "订单", "客户", "用户", "产品", "商品", "时间", 
        "日期", "金额", "数量", "名称", "类型", "状态",
        "创建", "更新", "删除", "描述", "备注", "编码",
        "规格", "颜色", "尺寸", "仓库", "库位", "优惠券",
        "折扣", "交易", "流水", "支付", "下单", "入库",
        "出库", "成本", "品牌", "品类", "SKU", "SPU",
        "门店", "运费", "税费", "值", "号", "单价", "方式",
        "支付方式"
    ]
    
    print("\n3. 测试词根匹配...")
    print(f"   测试 {len(test_names)} 个中文名称:")
    
    success_count = 0
    for name in test_names:
        result = processor.match_existing_root(name)
        if result:
            english, field_type = result
            print(f"   OK '{name}' -> '{english}'")
            success_count += 1
        else:
            print(f"   NO '{name}' -> (未匹配到)")
    
    print(f"\n4. 测试结果:")
    print(f"   成功匹配: {success_count}/{len(test_names)}")
    print(f"   成功率: {success_count/len(test_names)*100:.1f}%")
    
    # 5. 检查一些可能存在问题的匹配
    print("\n5. 检查映射表中的所有词根:")
    print(f"   映射表大小: {len(processor.existing_root_map)}")
    print(f"   映射表中的键 (前 20 个): {list(processor.existing_root_map.keys())[:20]}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    test_root_matching()
