#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一校验流程优化测试脚本
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.validators.unified_validator import UnifiedValidator


def test_extract_error_fields():
    """测试提取错误字段"""
    print("\n" + "="*60)
    print("测试1: 提取错误字段")
    print("="*60)
    
    # 创建模拟的UnifiedValidator
    validator = UnifiedValidator(word_roots=[])
    
    # 模拟违规列表
    violations = [
        {
            'table_name': 'order_table',
            'field_name': 'order_id_new',
            'level': 'error',
            'rule': '字段命名规范',
            'message': '字段名包含禁用占位符"_new"'
        },
        {
            'table_name': 'order_table', 
            'field_name': 'user_name_new',
            'level': 'error',
            'rule': '字段命名规范',
            'message': '字段名包含禁用占位符"_new"'
        },
        {
            'table_name': 'user_table',
            'field_name': 'status_new',
            'level': 'warning',  # 警告级别，不应被提取
            'rule': '跨表一致性',
            'message': '状态字段命名不一致'
        }
    ]
    
    # 模拟解析后的表结构
    parsed_tables = {
        'order_table': {
            'columns': [
                {'name': 'order_id_new', 'comment': '订单ID'},
                {'name': 'user_name_new', 'comment': '用户名'}
            ]
        }
    }
    
    # 提取错误字段
    error_fields = validator.extract_error_fields(violations, parsed_tables)
    
    print(f"\n输入违规列表: {len(violations)} 条")
    print(f"输出错误字段: {sum(len(f) for f in error_fields.values())} 个")
    
    # 验证结果
    assert 'order_table' in error_fields
    assert 'order_id_new' in error_fields['order_table']
    assert 'user_name_new' in error_fields['order_table']
    assert 'user_table' not in error_fields  # 警告级别不应被提取
    
    print(f"\n错误字段详情:")
    for table, fields in error_fields.items():
        for field, info in fields.items():
            print(f"  {table}.{field}:")
            print(f"    中文注释: {info['comment']}")
            print(f"    当前名称: {info['current_name']}")
            print(f"    违规数量: {len(info['violations'])}")
    
    print("\n[OK] 提取错误字段测试通过")
    return True


def test_generate_field_fix_prompt():
    """测试生成字段修正提示词"""
    print("\n" + "="*60)
    print("测试2: 生成字段修正提示词")
    print("="*60)
    
    validator = UnifiedValidator(word_roots=[
        {'chinese_name': '订单', 'full_root': 'order', 'abbr_root': 'ord'},
        {'chinese_name': 'ID', 'full_root': 'id', 'abbr_root': 'id'},
        {'chinese_name': '用户', 'full_root': 'user', 'abbr_root': 'usr'}
    ])
    
    # 模拟错误字段
    error_fields = {
        'order_table': {
            'order_id_new': {
                'comment': '订单ID',
                'current_name': 'order_id_new',
                'violations': [{'rule': '字段命名规范', 'message': '包含禁用占位符'}]
            }
        }
    }
    
    # 生成提示词
    prompt = validator.generate_field_fix_prompt(error_fields)
    
    print(f"\n生成的提示词长度: {len(prompt)} 字符")
    print("-"*40)
    print(prompt)
    print("-"*40)
    
    # 验证提示词包含必要内容
    assert "订单ID" in prompt
    assert "order_id_new" in prompt
    assert "表: order_table" in prompt
    assert "可用词根列表" in prompt
    assert "order" in prompt
    
    print("\n[OK] 生成字段修正提示词测试通过")
    return True


def test_parse_field_fix_result():
    """测试解析字段修正结果"""
    print("\n" + "="*60)
    print("测试3: 解析字段修正结果")
    print("="*60)
    
    validator = UnifiedValidator(word_roots=[])
    
    # 模拟LLM输出
    llm_output = """order_table.order_id_new:order_id
user_table.user_name_new:user_name
product_table.product_code_new:product_code"""
    
    # 解析结果
    fix_results = validator.parse_field_fix_result(llm_output)
    
    print(f"\nLLM输出:")
    print(llm_output)
    print(f"\n解析结果:")
    for table, fields in fix_results.items():
        for field, corrected in fields.items():
            print(f"  {table}.{field} -> {corrected}")
    
    # 验证解析结果
    assert 'order_table' in fix_results
    assert fix_results['order_table']['order_id_new'] == 'order_id'
    assert 'user_table' in fix_results
    assert fix_results['user_table']['user_name_new'] == 'user_name'
    
    print("\n[OK] 解析字段修正结果测试通过")
    return True


def test_reassemble_ddl():
    """测试重组DDL"""
    print("\n" + "="*60)
    print("测试4: 重组DDL")
    print("="*60)
    
    validator = UnifiedValidator(word_roots=[])
    
    # 模拟原始DDL
    original_ddl = {
        'order_table': """CREATE TABLE order_table (
    id INT PRIMARY KEY,
    order_id_new VARCHAR(64) COMMENT '订单ID',
    user_name_new VARCHAR(128) COMMENT '用户名',
    create_time DATETIME
);""",
        'product_table': """CREATE TABLE product_table (
    id INT PRIMARY KEY,
    product_name VARCHAR(255)
);"""
    }
    
    # 模拟修正结果
    fix_results = {
        'order_table': {
            'order_id_new': 'order_id',
            'user_name_new': 'user_name'
        }
    }
    
    # 重组DDL
    corrected_ddl = validator.reassemble_ddl(original_ddl, fix_results, {})
    
    print(f"\n原始DDL:")
    for table, ddl in original_ddl.items():
        print(f"【{table}】")
        print(ddl)
    
    print(f"\n修正后的DDL:")
    for table, ddl in corrected_ddl.items():
        print(f"【{table}】")
        print(ddl)
    
    # 验证修正结果
    assert 'order_id' in corrected_ddl['order_table']
    assert 'order_id_new' not in corrected_ddl['order_table']
    assert 'user_name' in corrected_ddl['order_table']
    assert 'user_name_new' not in corrected_ddl['order_table']
    # product_table 没有修正，应保持不变
    assert corrected_ddl['product_table'] == original_ddl['product_table']
    
    print("\n[OK] 重组DDL测试通过")
    return True


def test_full_flow():
    """测试完整流程"""
    print("\n" + "="*60)
    print("测试5: 完整校验修正流程")
    print("="*60)
    
    # 准备测试数据
    word_roots = [
        {'chinese_name': '订单', 'full_root': 'order', 'abbr_root': 'ord'},
        {'chinese_name': 'ID', 'full_root': 'id', 'abbr_root': 'id'},
        {'chinese_name': '用户', 'full_root': 'user', 'abbr_root': 'usr'},
        {'chinese_name': '状态', 'full_root': 'status', 'abbr_root': 'stat'}
    ]
    
    validator = UnifiedValidator(word_roots=word_roots)
    
    # 模拟DDL
    ddl_dict = {
        'order_table': """CREATE TABLE order_table (
    id INT PRIMARY KEY,
    order_id_new VARCHAR(64) COMMENT '订单ID',
    user_name VARCHAR(128) COMMENT '用户名',
    status_code VARCHAR(32) COMMENT '状态'
);""",
        'user_table': """CREATE TABLE user_table (
    id INT PRIMARY KEY,
    user_id_new VARCHAR(64) COMMENT '用户ID',
    user_name VARCHAR(128) COMMENT '用户名'
);"""
    }
    
    print(f"\n阶段1: 校验阶段")
    validation_result = validator.validate_batch(ddl_dict)
    print(f"  错误数: {validation_result['error_count']}")
    print(f"  警告数: {validation_result['warning_count']}")
    
    # 模拟错误字段提取
    print(f"\n阶段2: 提取错误字段")
    parsed_tables = validator.parse_all_ddl(ddl_dict)
    error_fields = validator.extract_error_fields(
        validation_result['single_violations'],
        parsed_tables
    )
    print(f"  错误字段数: {sum(len(f) for f in error_fields.values())}")
    
    # 模拟LLM修正
    print(f"\n阶段3: LLM修正")
    if error_fields:
        fix_prompt = validator.generate_field_fix_prompt(error_fields)
        print(f"  提示词长度: {len(fix_prompt)}")
        
        # 模拟LLM输出
        llm_output = """order_table.order_id_new:order_id
user_table.user_id_new:user_id"""
        
        fix_results = validator.parse_field_fix_result(llm_output)
        print(f"  修正字段数: {sum(len(f) for f in fix_results.values())}")
        
        # 重组DDL
        print(f"\n阶段4: DDL重组")
        corrected_ddl = validator.reassemble_ddl(ddl_dict, fix_results, parsed_tables)
        
        # 验证结果
        assert 'order_id' in corrected_ddl['order_table']
        assert 'user_id' in corrected_ddl['user_table']
        print("  [OK] 完整流程测试通过")
    
    print("\n[OK] 完整校验修正流程测试通过")
    return True


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("统一校验流程优化测试套件")
    print("="*60)
    
    tests = [
        test_extract_error_fields,
        test_generate_field_fix_prompt,
        test_parse_field_fix_result,
        test_reassemble_ddl,
        test_full_flow,
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
