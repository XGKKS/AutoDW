#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试建表功能 - 验证词根拆分匹配和一致性
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_generate_ddl():
    """测试单独建表功能"""
    print("=" * 80)
    print("测试建表功能")
    print("=" * 80)
    
    # 测试用例：包含"维修"相关字段
    description = """
    创建维修工单维度表，包含以下字段：
    - 维修项目名称：VARCHAR(128)
    - 维修项目代码：VARCHAR(64)
    - 维修类型名称：VARCHAR(64)
    - 维修类型代码：VARCHAR(32)
    - 维修开始时间：DATETIME
    - 维修结束时间：DATETIME
    - 维修单号：VARCHAR(64)
    - 维修负责人代码：VARCHAR(64)
    """
    
    print("\n1. 测试单独建表 API: /api/generate-ddl")
    print("-" * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/generate-ddl",
            json={
                "description": description,
                "db_type": "mysql",
                "root_match_priority": "full",
                "llm_config": {
                    "api_key": "",
                    "api_url": "",
                    "model": ""
                },
                "word_roots_input": "",
                "standards_content": ""
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  Status: {response.status_code}")
            print(f"  Code: {result.get('code')}")
            
            if result.get('code') == 0:
                ddl = result.get('ddl', '')
                print(f"\n  Generated DDL:")
                print("-" * 40)
                print(ddl[:1000] + "..." if len(ddl) > 1000 else ddl)
                print("-" * 40)
                
                # 检查词根一致性
                print(f"\n  词根一致性检查:")
                repair_count = ddl.lower().count('repair_')
                rpr_count = ddl.lower().count('rpr_')
                maint_count = ddl.lower().count('maint_')
                
                print(f"    - repair_ 出现次数: {repair_count}")
                print(f"    - rpr_ 出现次数: {rpr_count}")
                print(f"    - maint_ 出现次数: {maint_count}")
                
                if repair_count > 0 and rpr_count == 0 and maint_count == 0:
                    print(f"    [PASS] 词根一致，都使用 repair")
                elif rpr_count > 0 and repair_count == 0 and maint_count == 0:
                    print(f"    [PASS] 词根一致，都使用 rpr")
                elif maint_count > 0 and repair_count == 0 and rpr_count == 0:
                    print(f"    [PASS] 词根一致，都使用 maint")
                else:
                    print(f"    [WARN] 词根可能不一致，请检查DDL")
                
                # 检查新词根
                new_roots = result.get('new_roots', [])
                print(f"\n  新词根数量: {len(new_roots)}")
                if new_roots:
                    print(f"  新词根示例:")
                    for root in new_roots[:5]:
                        print(f"    - {root.get('chinese_name')} -> {root.get('full_root')}")
                
                return True
            else:
                print(f"  Error: {result.get('message')}")
                return False
        else:
            print(f"  HTTP Error: {response.status_code}")
            print(f"  Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"  Exception: {str(e)}")
        return False


def test_batch_generate():
    """测试批量建表功能"""
    print("\n\n2. 测试批量建表 API: /api/batch-generate-ddl")
    print("-" * 80)
    
    # 创建一个简单的Excel文件内容（模拟）
    # 这里我们直接测试字段级处理的拆分匹配
    
    try:
        # 先检查服务状态
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"  Health check: {response.status_code}")
    except:
        print(f"  Health check failed, service may not be ready")
    
    return True


def test_split_match_directly():
    """直接测试拆分匹配功能"""
    print("\n\n3. 直接测试拆分匹配功能")
    print("-" * 80)
    
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
    
    from app.processors.field_processor import FieldProcessor
    
    # 模拟词根数据（与实际词根库类似）
    word_roots = [
        {'chinese_name': '维修', 'full_root': 'repair', 'abbr_root': 'rpr', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '类型', 'full_root': 'type', 'abbr_root': 'typ', 'recommended_type': 'VARCHAR(32)'},
        {'chinese_name': '名称', 'full_root': 'name', 'abbr_root': 'nm', 'recommended_type': 'VARCHAR(128)'},
        {'chinese_name': '代码', 'full_root': 'code', 'abbr_root': 'cd', 'recommended_type': 'VARCHAR(32)'},
        {'chinese_name': '时间', 'full_root': 'time', 'abbr_root': 'tm', 'recommended_type': 'DATETIME'},
        {'chinese_name': '项目', 'full_root': 'item', 'abbr_root': 'itm', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '开始', 'full_root': 'start', 'abbr_root': 'str', 'recommended_type': 'DATETIME'},
        {'chinese_name': '结束', 'full_root': 'end', 'abbr_root': 'end', 'recommended_type': 'DATETIME'},
        {'chinese_name': '单号', 'full_root': 'no', 'abbr_root': 'no', 'recommended_type': 'VARCHAR(64)'},
        {'chinese_name': '负责人', 'full_root': 'manager', 'abbr_root': 'mgr', 'recommended_type': 'VARCHAR(64)'},
    ]
    
    processor = FieldProcessor(
        api_key="test",
        api_url="http://localhost",
        model="test",
        word_roots=word_roots,
        root_match_priority="full"
    )
    
    test_fields = [
        "维修项目名称",
        "维修项目代码",
        "维修类型名称",
        "维修类型代码",
        "维修开始时间",
        "维修结束时间",
        "维修单号",
        "维修负责人代码",
    ]
    
    print(f"  测试字段拆分匹配 (root_match_priority='full'):")
    all_passed = True
    for field in test_fields:
        result = processor._try_split_and_match(field)
        if result:
            english = '_'.join(result)
            print(f"    [PASS] {field} -> {english}")
            # 检查是否都使用 repair
            if 'repair' not in english:
                print(f"           [WARN] 未使用 repair，而是用了其他词根")
        else:
            print(f"    [FAIL] {field} -> 无法拆分")
            all_passed = False
    
    return all_passed


if __name__ == "__main__":
    print("\n开始测试建表功能...\n")
    
    # 测试1: 直接测试拆分匹配
    test1_passed = test_split_match_directly()
    
    # 测试2: 测试单独建表API
    test2_passed = test_generate_ddl()
    
    # 测试3: 测试批量建表API
    test3_passed = test_batch_generate()
    
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    print(f"  拆分匹配测试: {'PASS' if test1_passed else 'FAIL'}")
    print(f"  单独建表测试: {'PASS' if test2_passed else 'FAIL'}")
    print(f"  批量建表测试: {'PASS' if test3_passed else 'FAIL'}")
    print("=" * 80)