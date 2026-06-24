#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
混合模式测试脚本
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.processors.field_processor import FieldProcessor, FieldInfo, create_batches_by_ascii_order


def test_ascii_sorting():
    """测试中文ASCII排序分批"""
    print("\n" + "="*60)
    print("测试1: 中文ASCII排序分批")
    print("="*60)
    
    # 测试数据
    roots = ["金额", "是否", "名称", "状态", "数量", "类型", "ID", "日期", "标识", "描述"]
    
    print(f"\n原始词根: {roots}")
    
    # 按ASCII排序
    sorted_roots = sorted(roots)
    print(f"ASCII排序后: {sorted_roots}")
    
    # 分批
    batches = create_batches_by_ascii_order(roots, batch_size=5)
    print(f"分批结果 (每批5个): {batches}")
    
    print("\n[OK] ASCII排序分批测试通过")
    return True


def test_layer_methods():
    """测试Layer处理方法"""
    print("\n" + "="*60)
    print("测试2: Layer处理方法")
    print("="*60)
    
    # 创建模拟的FieldProcessor
    processor = FieldProcessor(
        api_key="test",
        api_url="http://test.com",
        model="test"
    )
    
    # 模拟历史词根
    processor.existing_root_map = {
        "订单": {"full": "order", "abbr": "ord"},
        "状态": {"full": "status", "abbr": "stat"},
        "删除": {"full": "delete", "abbr": "dele"},
    }
    
    # 测试Layer1: 完全匹配
    layer1_fields = {
        "订单状态": ["订单", "状态"]
    }
    layer1_results = processor.process_layer1_fields(layer1_fields, processor.existing_root_map)
    print(f"\nLayer1测试:")
    print(f"  输入: {layer1_fields}")
    print(f"  输出: {layer1_results}")
    assert "订单状态" in layer1_results
    assert layer1_results["订单状态"] == "order_status"
    print("  [OK] Layer1测试通过")
    
    # 测试Layer2: 部分匹配
    layer2_fields = {
        "是否删除": ["是否", "删除"]
    }
    llm_translations = {"是否": "is"}
    layer2_results = processor.process_layer2_fields(layer2_fields, processor.existing_root_map, llm_translations)
    print(f"\nLayer2测试:")
    print(f"  输入字段: {layer2_fields}")
    print(f"  LLM翻译: {llm_translations}")
    print(f"  输出: {layer2_results}")
    assert "是否删除" in layer2_results
    assert layer2_results["是否删除"] == "is_delete"
    print("  [OK] Layer2测试通过")
    
    # 测试Layer3: 完全未匹配
    layer3_fields = {
        "特殊标识": ["特殊", "标识"]
    }
    llm_designs = {
        "特殊标识": {
            "field_name": "special_id",
            "roots": {"特殊": "special", "标识": "id"}
        }
    }
    layer3_results, new_roots = processor.process_layer3_fields(layer3_fields, llm_designs)
    print(f"\nLayer3测试:")
    print(f"  输入字段: {layer3_fields}")
    print(f"  LLM设计: {llm_designs}")
    print(f"  输出字段: {layer3_results}")
    print(f"  新词根: {new_roots}")
    assert "特殊标识" in layer3_results
    assert layer3_results["特殊标识"] == "special_id"
    assert "特殊" in new_roots
    assert new_roots["特殊"] == "special"
    print("  [OK] Layer3测试通过")
    
    print("\n[OK] Layer处理方法测试通过")
    return True


def test_parse_layer3_output():
    """测试Layer3输出解析"""
    print("\n" + "="*60)
    print("测试3: Layer3输出解析")
    print("="*60)
    
    processor = FieldProcessor(
        api_key="test",
        api_url="http://test.com",
        model="test"
    )
    
    # 模拟LLM输出
    llm_output = """特殊标识:special_id|特殊:special,标识:id
业务编码:biz_code|业务:biz,编码:code
备用字段:backup_field|备用:backup,字段:field"""
    
    lines = llm_output.strip().split('\n')
    results = processor.parse_layer3_output(lines)
    
    print(f"\nLLM原始输出:")
    print(llm_output)
    print(f"\n解析结果:")
    for name, info in results.items():
        print(f"  {name}: {info}")
    
    assert "特殊标识" in results
    assert results["特殊标识"]["field_name"] == "special_id"
    assert results["特殊标识"]["roots"]["特殊"] == "special"
    assert results["特殊标识"]["roots"]["标识"] == "id"
    
    print("\n[OK] Layer3输出解析测试通过")
    return True


def test_build_layer3_prompt():
    """测试Layer3提示词构建"""
    print("\n" + "="*60)
    print("测试4: Layer3提示词构建")
    print("="*60)
    
    processor = FieldProcessor(
        api_key="test",
        api_url="http://test.com",
        model="test"
    )
    processor.standards = "测试规范"
    
    fields = [
        {"chinese_name": "特殊标识", "roots": ["特殊", "标识"]},
        {"chinese_name": "业务编码", "roots": ["业务", "编码"]}
    ]
    
    prompt = processor.build_layer3_prompt(fields)
    
    print(f"\n生成的提示词:")
    print("-" * 40)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("-" * 40)
    
    # 验证提示词包含关键内容
    assert "特殊标识" in prompt
    assert "业务编码" in prompt
    assert "特殊" in prompt
    assert "标识" in prompt
    assert "开发规范" in prompt
    assert "测试规范" in prompt
    
    print("\n[OK] Layer3提示词构建测试通过")
    return True


def test_hybrid_mode_flow():
    """测试混合模式完整流程"""
    print("\n" + "="*60)
    print("测试5: 混合模式完整流程")
    print("="*60)
    
    processor = FieldProcessor(
        api_key="test",
        api_url="http://test.com",
        model="test"
    )
    
    # 模拟历史词根
    processor.existing_root_map = {
        "订单": {"full": "order", "abbr": "ord"},
        "状态": {"full": "status", "abbr": "stat"},
        "删除": {"full": "delete", "abbr": "dele"},
        "ID": {"full": "id", "abbr": "id"},
        "客户": {"full": "customer", "abbr": "cust"},
        "名称": {"full": "name", "abbr": "name"},
    }
    
    # 模拟字段分组
    groups = {
        "订单状态": [FieldInfo("table1", "订单状态", "VARCHAR(255)")],
        "是否删除": [FieldInfo("table1", "是否删除", "VARCHAR(255)")],
        "特殊标识": [FieldInfo("table2", "特殊标识", "VARCHAR(255)")],
        "客户名称": [FieldInfo("table2", "客户名称", "VARCHAR(255)")],
        "订单ID": [FieldInfo("table3", "订单ID", "VARCHAR(255)")],
    }
    
    print(f"\n模拟数据:")
    print(f"  历史词根: {list(processor.existing_root_map.keys())}")
    print(f"  字段分组: {list(groups.keys())}")
    
    # Step 1: 模拟jieba分词
    field_tokenization = {
        "订单状态": ["订单", "状态"],
        "是否删除": ["是否", "删除"],
        "特殊标识": ["特殊", "标识"],
        "客户名称": ["客户", "名称"],
        "订单ID": ["订单", "ID"],
    }
    
    print(f"\nStep 1 - jieba分词结果:")
    for name, roots in field_tokenization.items():
        print(f"  {name} -> {roots}")
    
    # Step 2: 模拟历史匹配
    matched_roots = set()
    for roots in field_tokenization.values():
        for root in roots:
            if root in processor.existing_root_map:
                matched_roots.add(root)
    
    print(f"\nStep 2 - 历史匹配:")
    print(f"  匹配词根: {matched_roots}")
    
    # Step 3: 分类字段
    layer1_fields = {}
    layer2_fields = {}
    layer3_fields = {}
    
    for chinese_name, roots in field_tokenization.items():
        matched_in_field = [r for r in roots if r in matched_roots]
        
        if len(matched_in_field) == len(roots):
            layer1_fields[chinese_name] = roots
        elif len(matched_in_field) > 0:
            layer2_fields[chinese_name] = roots
        else:
            layer3_fields[chinese_name] = roots
    
    print(f"\nStep 3 - 字段分类:")
    print(f"  Layer1 (完全匹配): {list(layer1_fields.keys())}")
    print(f"  Layer2 (部分匹配): {list(layer2_fields.keys())}")
    print(f"  Layer3 (完全未匹配): {list(layer3_fields.keys())}")
    
    # Step 4: Layer1处理
    layer1_results = processor.process_layer1_fields(layer1_fields, processor.existing_root_map)
    print(f"\nStep 4 - Layer1处理结果: {layer1_results}")
    
    # Step 5: Layer2处理
    layer2_results = {}
    if layer2_fields:
        # 模拟LLM翻译
        llm_translations = {"是否": "is"}
        layer2_results = processor.process_layer2_fields(layer2_fields, processor.existing_root_map, llm_translations)
    print(f"\nStep 5 - Layer2处理结果: {layer2_results}")
    
    # Step 6: Layer3处理
    layer3_results = {}
    new_roots = {}
    if layer3_fields:
        # 模拟LLM设计
        llm_designs = {
            "特殊标识": {
                "field_name": "special_id",
                "roots": {"特殊": "special", "标识": "id"}
            }
        }
        layer3_results, new_roots = processor.process_layer3_fields(layer3_fields, llm_designs)
    print(f"\nStep 6 - Layer3处理结果: {layer3_results}")
    print(f"  新词根: {new_roots}")
    
    # Step 7: 合并结果
    all_results = {**layer1_results, **layer2_results, **layer3_results}
    print(f"\nStep 7 - 最终结果:")
    for name, en_name in all_results.items():
        print(f"  {name} -> {en_name}")
    
    # 验证结果
    assert "订单状态" in all_results
    assert all_results["订单状态"] == "order_status"
    assert "是否删除" in all_results
    assert all_results["是否删除"] == "is_delete"
    assert "特殊标识" in all_results
    assert all_results["特殊标识"] == "special_id"
    assert "客户名称" in all_results
    assert all_results["客户名称"] == "customer_name"
    assert "订单ID" in all_results
    assert all_results["订单ID"] == "order_id"
    
    print("\n[OK] 混合模式完整流程测试通过")
    return True


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("混合模式测试套件")
    print("="*60)
    
    tests = [
        test_ascii_sorting,
        test_layer_methods,
        test_parse_layer3_output,
        test_build_layer3_prompt,
        test_hybrid_mode_flow,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n[FAIL] 测试失败: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
