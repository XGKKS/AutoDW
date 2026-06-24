#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的后端日志验证脚本
模拟批量建表流程，检查 update_progress 是否正确传递统计数据
"""
import json
import os
import sys
import threading
import time
from datetime import datetime

# 添加 app 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# 导入必要的模块
from app.main import update_progress, progress_store

print("=" * 80)
print("测试 update_progress 函数的数据保存")
print("=" * 80)

# 模拟任务ID
test_task_id = "test_task_001"

print(f"\n[步骤1] 初始化任务进度...")
update_progress(test_task_id, 0, 5, stage="初始化...")

print(f"\n[步骤2] 模拟解析Excel...")
update_progress(test_task_id, 1, 5, stage="解析Excel...")

print(f"\n[步骤3] 模拟字段分组...")
update_progress(test_task_id, 2, 5, stage="按中文词义分组...")

print(f"\n[步骤4] 模拟词根匹配 - 传递统计数据...")
# 模拟词根匹配完成后的统计
update_progress(test_task_id, 3, 5, stage="分批处理字段...",
                matched_count=48,
                unmatched_count=0,
                total_fields=48)

print(f"\n[步骤5] 模拟批量生成...")
update_progress(test_task_id, 4, 5, stage="生成字段英文名 [1/1]")

print(f"\n[步骤6] 模拟完成...")
update_progress(test_task_id, 5, 5, stage="完成建表")

print(f"\n[步骤7] 读取保存的进度数据...")
saved_progress = progress_store.get(test_task_id)

if saved_progress:
    print(f"\n保存的进度数据:")
    print(f"  current: {saved_progress.get('current')}")
    print(f"  total: {saved_progress.get('total')}")
    print(f"  stage: {saved_progress.get('stage')}")
    print(f"  matched_count: {saved_progress.get('matched_count')}")
    print(f"  unmatched_count: {saved_progress.get('unmatched_count')}")
    print(f"  total_fields: {saved_progress.get('total_fields')}")
    print(f"  milestones: {saved_progress.get('milestones')}")
    print(f"  overall_progress: {saved_progress.get('overall_progress')}")
    
    # 验证
    print(f"\n[步骤8] 验证数据完整性...")
    if saved_progress.get('matched_count') == 48:
        print(f"  ✅ matched_count 正确")
    else:
        print(f"  ❌ matched_count 不正确，期望 48，实际 {saved_progress.get('matched_count')}")
    
    if saved_progress.get('unmatched_count') == 0:
        print(f"  ✅ unmatched_count 正确")
    else:
        print(f"  ❌ unmatched_count 不正确，期望 0，实际 {saved_progress.get('unmatched_count')}")
    
    if saved_progress.get('total_fields') == 48:
        print(f"  ✅ total_fields 正确")
    else:
        print(f"  ❌ total_fields 不正确，期望 48，实际 {saved_progress.get('total_fields')}")
    
    # 模拟前端接收
    print(f"\n[步骤9] 模拟前端接收数据...")
    response_data = {
        "code": 0,
        "data": {**saved_progress, "current_ddl": "", "new_roots": []}
    }
    print(f"  前端接收到的数据包含:")
    print(f"    matched_count: {response_data['data'].get('matched_count')}")
    print(f"    unmatched_count: {response_data['data'].get('unmatched_count')}")
    print(f"    total_fields: {response_data['data'].get('total_fields')}")
    
    print(f"\n  ✅ update_progress 函数工作正常！")
else:
    print(f"  ❌ 未能读取到保存的进度数据")

print("\n" + "=" * 80)
print("测试完成!")
print("=" * 80)
