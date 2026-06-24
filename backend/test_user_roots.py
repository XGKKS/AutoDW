#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户提供的词根列表
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
    print("=" * 70)
    print("词根匹配测试（用户提供的词根列表）")
    print("=" * 70)
    
    # 1. 加载词根
    print("\n1. 加载词根文件...")
    word_roots = load_word_roots()
    print(f"   共加载 {len(word_roots)} 条词根")
    
    # 2. 创建 FieldProcessor 实例
    print("\n2. 创建 FieldProcessor 实例...")
    processor = FieldProcessor(
        api_key="test_key",
        api_url="http://localhost",
        model="test_model",
        word_roots=word_roots,
        root_match_priority="full"
    )
    
    # 3. 测试词根列表
    test_names = [
        "商品ID",
        "SKU编码",
        "SPU编码",
        "商品名称",
        "品牌名称",
        "品类名称",
        "商品规格",
        "商品颜色",
        "商品尺寸",
        "条形码",
        "商品状态",
        "创建时间",
        "更新时间",
        "仓库ID",
        "仓库名称",
        "仓库编码",
        "库位编码",
        "仓库状态",
        "优惠券ID",
        "优惠券名称",
        "优惠券类型",
        "折扣值",
        "优惠券状态",
        "订单ID",
        "交易流水号",
        "订单号",
        "用户ID",
        "门店ID",
        "商品数量",
        "商品单价",
        "订单金额",
        "折扣金额",
        "税费金额",
        "运费金额",
        "支付方式",
        "支付状态",
        "下单时间",
        "支付时间",
        "订单状态",
        "订单类型",
        "是否删除",
        "入库单ID",
        "库位ID",
        "入库数量",
        "入库成本",
        "入库类型",
        "入库时间",
        "入库状态",
    ]
    
    print("\n3. 测试词根匹配...")
    print(f"   测试 {len(test_names)} 个词根:")
    print("-" * 70)
    
    success_count = 0
    failed_list = []
    
    for name in test_names:
        result = processor.match_existing_root(name)
        if result:
            english, field_type = result
            print(f"OK   '{name}' -> '{english}'")
            success_count += 1
        else:
            print(f"FAIL '{name}'")
            failed_list.append(name)
    
    print("-" * 70)
    
    print(f"\n4. 测试结果:")
    print(f"   成功匹配: {success_count}/{len(test_names)}")
    print(f"   成功率: {success_count/len(test_names)*100:.1f}%")
    
    # 5. 显示匹配失败的词根
    if failed_list:
        print(f"\n5. 未匹配到的词根列表 ({len(failed_list)} 个):")
        print("-" * 70)
        for i, name in enumerate(failed_list, 1):
            print(f"   {i:2d}. {name}")
        print("-" * 70)
        
        # 6. 尝试模糊匹配
        print(f"\n6. 尝试模糊匹配（尝试匹配词根中的子串）:")
        print("-" * 70)
        fuzzy_matches = []
        
        # 获取所有词根
        all_roots = list(processor.existing_root_map.keys())
        
        for failed_name in failed_list:
            # 尝试查找是否包含在某个词根中
            found = False
            for root_name in all_roots:
                if failed_name in root_name or root_name in failed_name:
                    info = processor.existing_root_map[root_name]
                    print(f"   '{failed_name}' 可能属于 '{root_name}' -> '{info['full']}'")
                    fuzzy_matches.append((failed_name, root_name, info['full']))
                    found = True
                    break
            
            if not found:
                # 尝试查找组合字段中的单个词
                parts = []
                for char in failed_name:
                    if char in all_roots:
                        parts.append(char)
                        info = processor.existing_root_map[char]
                        print(f"   '{char}' 在词根库中 -> '{info['full']}'")
                
                if parts:
                    fuzzy_matches.append((failed_name, parts, "部分匹配"))
        
        print("-" * 70)
        
        if fuzzy_matches:
            print(f"\n7. 建议: {len(fuzzy_matches)} 个词根可以添加组合词根")
    
    print("\n" + "=" * 70)
    print("测试完成!")
    print("=" * 70)


if __name__ == "__main__":
    test_root_matching()
