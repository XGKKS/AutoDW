#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试字段统计传递流程
"""
import json
import os
import sys
import logging

# 添加 app 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from app.processors.field_processor import FieldProcessor


def test_progress_callback():
    """测试进度回调是否正确传递统计数据"""
    print("=" * 80)
    print("测试字段统计传递流程")
    print("=" * 80)
    
    # 创建模拟的进度回调
    progress_data = {}
    
    def mock_progress_callback(task_id, current, total, stage=None, matched_count=None, unmatched_count=None, total_fields=None):
        print(f"\n[进度回调] task_id={task_id}, current={current}, total={total}")
        if stage:
            print(f"  stage={stage}")
        if matched_count is not None:
            print(f"  matched_count={matched_count}")
        if unmatched_count is not None:
            print(f"  unmatched_count={unmatched_count}")
        if total_fields is not None:
            print(f"  total_fields={total_fields}")
        
        # 保存到全局变量
        progress_data['current'] = current
        progress_data['total'] = total
        progress_data['stage'] = stage
        progress_data['matched_count'] = matched_count
        progress_data['unmatched_count'] = unmatched_count
        progress_data['total_fields'] = total_fields
    
    # 创建 FieldProcessor
    word_roots = load_word_roots()
    
    print("\n[步骤1] 创建 FieldProcessor 实例...")
    processor = FieldProcessor(
        api_key="test_key",
        api_url="http://localhost",
        model="test_model",
        word_roots=word_roots,
        root_match_priority="full",
        progress_callback=mock_progress_callback
    )
    
    # 创建测试数据
    print("\n[步骤2] 创建测试数据...")
    from app.processors.field_processor import FieldInfo
    
    test_fields = [
        FieldInfo("商品表", "商品ID", "VARCHAR(64)"),
        FieldInfo("商品表", "SKU编码", "VARCHAR(64)"),
        FieldInfo("商品表", "商品名称", "VARCHAR(128)"),
        FieldInfo("商品表", "创建时间", "DATETIME"),
        FieldInfo("商品表", "更新时间", "DATETIME"),
    ]
    
    # 测试分组
    print("\n[步骤3] 测试分组...")
    groups = processor.group_fields_by_chinese(test_fields)
    print(f"  分组结果: {len(groups)} 个不同的中文字段名")
    
    # 测试分批和统计
    print("\n[步骤4] 测试分批和词根匹配...")
    batches, matched_fields, stats = processor.split_into_batches(groups)
    
    print("\n[步骤5] 验证统计数据...")
    print(f"  统计结果:")
    print(f"    total_fields: {stats['total_fields']}")
    print(f"    matched_count: {stats['matched_count']}")
    print(f"    unmatched_count: {stats['unmatched_count']}")
    
    print("\n[步骤6] 验证进度回调...")
    if 'matched_count' in progress_data:
        print(f"  ✅ 进度回调接收到了 matched_count={progress_data['matched_count']}")
    else:
        print(f"  ❌ 进度回调没有接收到 matched_count")
    
    if 'unmatched_count' in progress_data:
        print(f"  ✅ 进度回调接收到了 unmatched_count={progress_data['unmatched_count']}")
    else:
        print(f"  ❌ 进度回调没有接收到 unmatched_count")
    
    if 'total_fields' in progress_data:
        print(f"  ✅ 进度回调接收到了 total_fields={progress_data['total_fields']}")
    else:
        print(f"  ❌ 进度回调没有接收到 total_fields")
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)


def load_word_roots():
    """加载词根"""
    word_roots_path = os.path.join(os.path.dirname(__file__), 'word_roots.json')
    if os.path.exists(word_roots_path):
        try:
            with open(word_roots_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载词根文件失败: {e}")
            return []
    return []


if __name__ == "__main__":
    test_progress_callback()
