#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的 _fallback_name 函数
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.processors.field_processor import FieldProcessor

def test_fallback_names():
    """测试各种字段名的转换"""
    # 创建一个临时的 FieldProcessor 实例
    processor = FieldProcessor(
        api_key="test",
        api_url="http://test",
        model="test",
        temperature=0.3
    )
    
    test_cases = [
        # 用户遇到的问题字段
        ("商品ID", "product_id"),
        ("SKU编码", "sku_code"),
        ("SPU编码", "spu_code"),
        ("商品名称", "product_name"),
        ("品牌名称", "brand_name"),
        ("品类名称", "category_name"),
        ("商品规格", "product_spec"),
        ("商品颜色", "product_color"),
        ("商品尺寸", "product_size"),
        ("仓库ID", "warehouse_id"),
        ("仓库名称", "warehouse_name"),
        ("仓库编码", "warehouse_code"),
        ("库位编码", "location_code"),
        ("仓库状态", "warehouse_status"),
        ("优惠券ID", "coupon_id"),
        ("优惠券名称", "coupon_name"),
        ("优惠券类型", "coupon_type"),
        ("折扣值", "discount_value"),
        ("优惠券状态", "coupon_status"),
        ("订单ID", "order_id"),
        ("交易流水号", "transaction_serial_number"),
        ("订单号", "order_number"),
        ("用户ID", "user_id"),
        ("门店ID", "store_id"),
        ("商品数量", "product_num"),
        ("商品单价", "product_price"),
        ("订单金额", "order_amt"),
        ("折扣金额", "discount_amt"),
        ("税费金额", "tax_amt"),
        ("运费金额", "freight_amt"),
        ("支付方式", "pay_type"),
        ("支付状态", "pay_status"),
        ("下单时间", "order_time"),
        ("支付时间", "pay_time"),
        ("订单状态", "order_status"),
        ("订单类型", "order_type"),
        ("入库数量", "inbound_num"),
        ("入库成本", "inbound_cost"),
        ("入库类型", "inbound_type"),
        ("入库时间", "inbound_time"),
        ("入库状态", "inbound_status"),
    ]
    
    print("=" * 60)
    print("Testing _fallback_name function")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for chinese_name, expected in test_cases:
        result = processor._fallback_name(chinese_name)
        if result == expected:
            success_count += 1
            print(f"[OK] {chinese_name:<20} -> {result}")
        else:
            fail_count += 1
            print(f"[FAIL] {chinese_name:<20} -> {result:20} (expected: {expected})")
    
    print("=" * 60)
    print(f"Results: Success {success_count}, Failed {fail_count}")
    print("=" * 60)
    
    return fail_count == 0

if __name__ == "__main__":
    # 设置编码为 utf-8
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    success = test_fallback_names()
    sys.exit(0 if success else 1)
