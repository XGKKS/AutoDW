#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试词组拆分功能
验证"总装计划下线时间"等长字段按词组分拆
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.processors.field_processor import FieldProcessor


def test_phrase_split():
    """测试词组拆分功能"""
    print("=" * 80)
    print("词组拆分功能测试")
    print("=" * 80)

    # 模拟词根数据
    word_roots = [
        {'chinese_name': '总装', 'full_root': 'assembly', 'abbr_root': 'asm', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '计划', 'full_root': 'plan', 'abbr_root': 'pln', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '下线', 'full_root': 'offline', 'abbr_root': 'ofl', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '时间', 'full_root': 'time', 'abbr_root': 'tm', 'recommended_type': 'DATETIME'},
        {'chinese_name': '维修', 'full_root': 'repair', 'abbr_root': 'rpr', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '类型', 'full_root': 'type', 'abbr_root': 'typ', 'recommended_type': 'VARCHAR(32)'},
        {'chinese_name': '名称', 'full_root': 'name', 'abbr_root': 'nm', 'recommended_type': 'VARCHAR(128)'},
        {'chinese_name': '代码', 'full_root': 'code', 'abbr_root': 'cd', 'recommended_type': 'VARCHAR(32)'},
    ]

    processor = FieldProcessor(
        api_key="test",
        api_url="http://localhost",
        model="test",
        word_roots=word_roots,
        root_match_priority="full"
    )

    print("\n1. 测试词组拆分功能 (root_match_priority='full')")
    print("-" * 80)

    test_cases = [
        ("总装计划下线时间", ["assembly", "plan", "offline", "time"]),
        ("维修类型名称", ["repair", "type", "name"]),
        ("维修类型代码", ["repair", "type", "code"]),
        ("总装计划", ["assembly", "plan"]),
        ("下线时间", ["offline", "time"]),
    ]

    passed = 0
    failed = 0

    for chinese_name, expected_parts in test_cases:
        result = processor._try_split_and_match(chinese_name)
        if result == expected_parts:
            english = '_'.join(result)
            print(f"  [PASS] '{chinese_name}' -> {english}")
            passed += 1
        else:
            print(f"  [FAIL] '{chinese_name}' -> {result} (期望 {expected_parts})")
            # 手动测试词组分词
            print(f"         词根库中的键: {list(processor.existing_root_map.keys())}")
            
            # 手动测试词组分词逻辑
            common_phrases = [
                '计划下线', '总装计划', '下线时间', '总装', '计划', '下线', '时间',
            ]
            sorted_phrases = sorted(common_phrases, key=len, reverse=True)
            parts = []
            remaining = chinese_name
            while remaining:
                matched = False
                for phrase in sorted_phrases:
                    if len(phrase) <= len(remaining) and remaining.startswith(phrase):
                        parts.append(phrase)
                        remaining = remaining[len(phrase):]
                        matched = True
                        break
                if not matched:
                    break
            print(f"         词组分词: {parts}, 剩余: '{remaining}'")
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
    success = test_phrase_split()
    sys.exit(0 if success else 1)