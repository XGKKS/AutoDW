#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试词根拆分匹配功能
验证"维修类型名称"等长字段能否被正确拆分匹配
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.processors.field_processor import FieldProcessor


def test_split_match():
    """测试拆分匹配功能"""
    print("=" * 80)
    print("词根拆分匹配功能测试")
    print("=" * 80)
    
    # 模拟词根数据
    word_roots = [
        {'chinese_name': '维修', 'full_root': 'repair', 'abbr_root': 'rpr', 'type': 'VARCHAR(64)'},
        {'chinese_name': '类型', 'full_root': 'type', 'abbr_root': 'typ', 'type': 'VARCHAR(32)'},
        {'chinese_name': '名称', 'full_root': 'name', 'abbr_root': 'nm', 'type': 'VARCHAR(128)'},
        {'chinese_name': '代码', 'full_root': 'code', 'abbr_root': 'cd', 'type': 'VARCHAR(32)'},
        {'chinese_name': '时间', 'full_root': 'time', 'abbr_root': 'tm', 'type': 'DATETIME'},
        {'chinese_name': '项目', 'full_root': 'item', 'abbr_root': 'itm', 'type': 'VARCHAR(64)'},
        {'chinese_name': '订单', 'full_root': 'order', 'abbr_root': 'ord', 'type': 'VARCHAR(64)'},
        {'chinese_name': '客户', 'full_root': 'customer', 'abbr_root': 'cust', 'type': 'VARCHAR(64)'},
        {'chinese_name': '开始', 'full_root': 'start', 'abbr_root': 'str', 'type': 'DATETIME'},
        {'chinese_name': '结束', 'full_root': 'end', 'abbr_root': 'end', 'type': 'DATETIME'},
        {'chinese_name': '日期', 'full_root': 'date', 'abbr_root': 'dt', 'type': 'DATE'},
        {'chinese_name': '数量', 'full_root': 'count', 'abbr_root': 'cnt', 'type': 'INT'},
        {'chinese_name': '主键', 'full_root': 'id', 'abbr_root': 'id', 'type': 'VARCHAR(64)'},
        {'chinese_name': '商品', 'full_root': 'item', 'abbr_root': 'itm', 'type': 'VARCHAR(64)'},
    ]
    
    # 创建 FieldProcessor 实例（使用全称优先）
    processor = FieldProcessor(
        api_key="test_key",
        api_url="http://localhost",
        model="test_model",
        word_roots=word_roots,
        root_match_priority="full"
    )
    
    print(f"\n1. 测试拆分匹配功能")
    print("-" * 80)
    
    # 测试用例
    test_cases = [
        ("维修类型名称", ["repair", "type", "name"]),  # 应该拆分成3个词
        ("维修项目代码", ["repair", "item", "code"]),   # 应该拆分成3个词
        ("订单开始时间", ["order", "start", "time"]),  # 应该拆分成3个词
        ("客户主键", ["customer", "id"]),               # 应该拆分成2个词
        ("商品名称", ["item", "name"]),                 # 应该拆分成2个词
        ("新字段ABC", None),                            # 无法拆分（包含未知词）
    ]
    
    passed = 0
    failed = 0
    
    for chinese_name, expected_parts in test_cases:
        result = processor._try_split_and_match(chinese_name)
        if expected_parts is None:
            # 期望失败
            if result is None:
                print(f"  [PASS] '{chinese_name}' -> 无法拆分（符合预期）")
                passed += 1
            else:
                print(f"  [FAIL] '{chinese_name}' -> {result}（期望失败但成功拆分）")
                failed += 1
        else:
            # 期望成功
            if result == expected_parts:
                print(f"  [PASS] '{chinese_name}' -> {'_'.join(result)}")
                passed += 1
            else:
                print(f"  [FAIL] '{chinese_name}' -> {result}（期望 {'_'.join(expected_parts)}）")
                failed += 1
    
    print(f"\n2. Test Results Summary")
    print("-" * 80)
    print(f"  Passed: {passed}/{passed + failed}")
    print(f"  Failed: {failed}/{passed + failed}")
    
    print(f"\n3. Test Prompt Generation")
    print("-" * 80)
    
    # 模拟一个批次
    class MockField:
        def __init__(self, suggested_type):
            self.suggested_type = suggested_type
    
    batch = [
        ("新业务字段", [MockField("VARCHAR(64)")]),
        ("另一个字段", [MockField("INT")]),
    ]
    
    prompt = processor.build_prompt_for_batch(batch)
    print(f"  Prompt contains 'must use': {'must use' in prompt or '必须使用' in prompt}")
    print(f"  Prompt contains 'full form': {'full form' in prompt or '全称形式' in prompt}")
    
    # 检查提示词是否符合预期
    if ('必须使用' in prompt or 'must use' in prompt.lower()) and ('全称形式' in prompt or 'full form' in prompt.lower()):
        print(f"  [PASS] Prompt generated correctly (root_match_priority='full')")
    elif ('必须使用' in prompt or 'must use' in prompt.lower()) and ('缩写形式' in prompt or 'abbr form' in prompt.lower()):
        print(f"  [PASS] Prompt generated correctly (root_match_priority='abbr')")
    else:
        print(f"  [INFO] Prompt generated")
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    success = test_split_match()
    sys.exit(0 if success else 1)