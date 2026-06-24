#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将常见词根添加到 word_roots.json 文件
"""
import json
import os


def load_word_roots():
    """加载现有词根"""
    word_roots_path = os.path.join(os.path.dirname(__file__), 'word_roots.json')
    if os.path.exists(word_roots_path):
        try:
            with open(word_roots_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载词根文件失败: {e}")
            return []
    return []


def save_word_roots(roots):
    """保存词根到文件"""
    word_roots_path = os.path.join(os.path.dirname(__file__), 'word_roots.json')
    try:
        with open(word_roots_path, 'w', encoding='utf-8') as f:
            json.dump(roots, f, ensure_ascii=False, indent=2)
        print(f"成功保存 {len(roots)} 条词根到 {word_roots_path}")
        return True
    except Exception as e:
        print(f"保存词根文件失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("添加常见词根")
    print("=" * 60)
    
    # 1. 加载现有词根
    existing_roots = load_word_roots()
    print(f"\n现有词根数量: {len(existing_roots)}")
    
    # 2. 创建现有中文名称的集合
    existing_chinese_names = set()
    for root in existing_roots:
        chinese_name = root.get('chinese_name', '').strip()
        if chinese_name:
            existing_chinese_names.add(chinese_name)
    
    print(f"现有中文名称数量: {len(existing_chinese_names)}")
    
    # 3. 定义常见词根
    common_roots = [
        ("订单", "order", "order", "INT"),
        ("客户", "customer", "cust", "VARCHAR(64)"),
        ("用户", "user", "user", "VARCHAR(64)"),
        ("产品", "product", "prod", "VARCHAR(64)"),
        ("时间", "time", "time", "DATETIME"),
        ("日期", "date", "date", "DATE"),
        ("金额", "amount", "amt", "DECIMAL(18,2)"),
        ("数量", "quantity", "qty", "INT"),
        ("删除", "delete", "del", "BOOLEAN"),
        ("描述", "description", "desc", "VARCHAR(512)"),
        ("备注", "remark", "remark", "VARCHAR(512)"),
        ("编码", "code", "code", "VARCHAR(64)"),
        ("优惠券", "coupon", "coup", "VARCHAR(64)"),
        ("折扣", "discount", "disc", "DECIMAL(18,2)"),
        ("交易", "transaction", "trans", "VARCHAR(64)"),
        ("流水", "serial", "serial", "VARCHAR(64)"),
        ("支付", "pay", "pay", "VARCHAR(32)"),
        ("下单", "place_order", "order", "DATETIME"),
        ("出库", "outbound", "out", "VARCHAR(64)"),
        ("SKU", "sku", "sku", "VARCHAR(64)"),
        ("sku", "sku", "sku", "VARCHAR(64)"),
        ("SPU", "spu", "spu", "VARCHAR(64)"),
        ("spu", "spu", "spu", "VARCHAR(64)"),
        ("门店", "store", "store", "VARCHAR(64)"),
        ("运费", "freight", "frei", "DECIMAL(18,2)"),
        ("税费", "tax", "tax", "DECIMAL(18,2)"),
        ("值", "value", "val", "VARCHAR(255)"),
        ("号", "number", "num", "VARCHAR(64)"),
        ("方式", "method", "meth", "VARCHAR(32)"),
    ]
    
    print(f"\n准备添加 {len(common_roots)} 条常见词根")
    
    # 4. 添加新词根（只添加不存在的）
    added_count = 0
    for chinese_name, full_root, abbr_root, recommended_type in common_roots:
        if chinese_name not in existing_chinese_names:
            existing_roots.append({
                "business_domain": "基础通用",
                "chinese_name": chinese_name,
                "full_root": full_root,
                "abbr_root": abbr_root,
                "recommended_type": recommended_type
            })
            added_count += 1
            print(f"  + 添加: '{chinese_name}' -> '{full_root}'")
        else:
            print(f"  - 跳过: '{chinese_name}' (已存在)")
    
    print(f"\n成功添加 {added_count} 条新词根")
    print(f"词根总数: {len(existing_roots)}")
    
    # 5. 保存
    if save_word_roots(existing_roots):
        print("\n" + "=" * 60)
        print("完成!")
        print("=" * 60)
    else:
        print("\n保存失败!")


if __name__ == "__main__":
    main()
