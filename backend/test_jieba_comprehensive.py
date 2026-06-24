#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面测试 jieba 分词方案
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.processors.field_processor import FieldProcessor

def test_comprehensive():
    """全面测试分词方案"""
    print("=" * 80)
    print("全面测试 jieba 分词方案")
    print("=" * 80)

    # 模拟词根数据（包含常见的业务术语）
    word_roots = [
        {'chinese_name': '总装', 'full_root': 'assembly', 'abbr_root': 'asm', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '计划', 'full_root': 'plan', 'abbr_root': 'pln', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '下线', 'full_root': 'offline', 'abbr_root': 'ofl', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '上线', 'full_root': 'online', 'abbr_root': 'onl', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '涂装', 'full_root': 'paint', 'abbr_root': 'pnt', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '时间', 'full_root': 'time', 'abbr_root': 'tm', 'recommended_type': 'DATETIME'},
        {'chinese_name': '维修', 'full_root': 'repair', 'abbr_root': 'rpr', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '保养', 'full_root': 'maintain', 'abbr_root': 'mnt', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '类型', 'full_root': 'type', 'abbr_root': 'typ', 'recommended_type': 'VARCHAR(32)'},
        {'chinese_name': '名称', 'full_root': 'name', 'abbr_root': 'nm', 'recommended_type': 'VARCHAR(128)'},
        {'chinese_name': '代码', 'full_root': 'code', 'abbr_root': 'cd', 'recommended_type': 'VARCHAR(32)'},
        {'chinese_name': '供应商', 'full_root': 'supplier', 'abbr_root': 'spl', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '客户', 'full_root': 'customer', 'abbr_root': 'cst', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '编号', 'full_root': 'number', 'abbr_root': 'no', 'recommended_type': 'VARCHAR(32)'},
        {'chinese_name': '单号', 'full_root': 'order', 'abbr_root': 'ord', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '工单', 'full_root': 'work_order', 'abbr_root': 'wo', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '状态', 'full_root': 'status', 'abbr_root': 'stt', 'recommended_type': 'VARCHAR(32)'},
        {'chinese_name': '日期', 'full_root': 'date', 'abbr_root': 'dt', 'recommended_type': 'DATE'},
        {'chinese_name': '人员', 'full_root': 'person', 'abbr_root': 'per', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '金额', 'full_root': 'amount', 'abbr_root': 'amt', 'recommended_type': 'DECIMAL(18,2)'},
        {'chinese_name': '是否', 'full_root': 'is', 'abbr_root': 'is', 'recommended_type': 'VARCHAR(10)'},
        {'chinese_name': '第一次', 'full_root': 'first', 'abbr_root': 'fst', 'recommended_type': 'VARCHAR(32)'},
    ]

    processor = FieldProcessor(
        api_key="test",
        api_url="http://localhost",
        model="test",
        word_roots=word_roots,
        root_match_priority="full"
    )

    print("\n1. 测试 jieba 分词结果")
    print("-" * 80)

    test_cases = [
        # 制造行业场景
        ("总装计划下线时间", ["assembly", "plan", "offline", "time"]),
        ("涂装计划上线时间", ["paint", "plan", "online", "time"]),
        ("总装计划", ["assembly", "plan"]),

        # 维修保养场景
        ("维修类型名称", ["repair", "type", "name"]),
        ("维修类型代码", ["repair", "type", "code"]),
        ("第一次保养日期", ["first", "maintain", "date"]),

        # 订单场景
        ("工单编号", ["work_order", "number"]),
        ("工单状态代码", ["work_order", "status", "code"]),

        # 供应商场景
        ("供应商编号", ["supplier", "number"]),
        ("供应商名称", ["supplier", "name"]),

        # 客户场景
        ("客户编号", ["customer", "number"]),
        ("客户名称", ["customer", "name"]),

        # 是否场景
        ("是否第一次保养", ["is", "first", "maintain"]),
    ]

    # 这些案例会被交给 LLM 处理，因为词根库不完整
    # 但 jieba 分词是正确的
    llm_cases = [
        ("保养单号", ["保养", "单", "号"]),  # jieba 分词正确
        ("订单金额", ["订单", "金额"]),      # jieba 分词正确
        ("应收金额", ["应收", "金额"]),      # jieba 分词正确
        ("是否完成", ["是否", "完成"]),      # jieba 分词正确
    ]

    passed = 0
    failed = 0

    print("\n1.1 词根库匹配的案例（应返回拆分后的词根）")
    print("-" * 80)
    for chinese_name, expected_parts in test_cases:
        result = processor._try_split_and_match(chinese_name)
        if result == expected_parts:
            english = '_'.join(result) if result else "None"
            print(f"  [PASS] '{chinese_name}' -> {english}")
            passed += 1
        else:
            english = '_'.join(result) if result else "None"
            expected_english = '_'.join(expected_parts)
            print(f"  [FAIL] '{chinese_name}' -> {english} (期望 {expected_english})")
            failed += 1

    print("\n1.2 词根库不完整的案例（应交给 LLM 处理，但分词正确）")
    print("-" * 80)
    for chinese_name, expected_jieba_parts in llm_cases:
        import jieba
        jieba_result = jieba.lcut(chinese_name, cut_all=False)
        if jieba_result == expected_jieba_parts:
            print(f"  [PASS] jieba分词: '{chinese_name}' -> {jieba_result} (词根库不完整，会交给LLM)")
        else:
            print(f"  [FAIL] jieba分词: '{chinese_name}' -> {jieba_result} (期望 {expected_jieba_parts})")
            failed += 1

    print(f"\n2. 测试结果汇总")
    print("-" * 80)
    print(f"  通过: {passed}/{passed + failed}")
    print(f"  失败: {failed}/{passed + failed}")

    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)

    return failed == 0

if __name__ == "__main__":
    success = test_comprehensive()
    sys.exit(0 if success else 1)
