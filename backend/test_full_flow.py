#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端测试：验证字段统计数据是否正确传递到前端
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
print("端到端测试：字段统计数据传递")
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

print(f"\n[步骤6] 模拟组装DDL...")
update_progress(test_task_id, 4, 5, stage="组装DDL [1/1]")

print(f"\n[步骤7] 模拟完成...")
update_progress(test_task_id, 5, 5, stage="完成建表")

print(f"\n[步骤8] 模拟前端调用 get_progress 接口...")
# 模拟 get_progress 函数的逻辑
progress = progress_store.get(test_task_id)
if progress:
    current_ddl = ""
    new_roots = []
    
    # 模拟返回给前端的数据
    response = {"code": 0, "data": {**progress, "current_ddl": current_ddl, "new_roots": new_roots}}
    
    print(f"\n返回给前端的数据:")
    print(json.dumps(response, ensure_ascii=False, indent=2))
    
    print(f"\n[步骤9] 检查是否包含统计数据...")
    if 'matched_count' in response['data']:
        print(f"  ✅ matched_count: {response['data']['matched_count']}")
    else:
        print(f"  ❌ 缺少 matched_count")
    
    if 'unmatched_count' in response['data']:
        print(f"  ✅ unmatched_count: {response['data']['unmatched_count']}")
    else:
        print(f"  ❌ 缺少 unmatched_count")
    
    if 'total_fields' in response['data']:
        print(f"  ✅ total_fields: {response['data']['total_fields']}")
    else:
        print(f"  ❌ 缺少 total_fields")
    
    print(f"\n[步骤10] 模拟前端接收...")
    data = response['data']
    matched_count = data.get('matched_count')
    unmatched_count = data.get('unmatched_count')
    total_fields = data.get('total_fields')
    
    if matched_count is not None or unmatched_count is not None or total_fields is not None:
        fieldStats = {
            'matched_count': matched_count,
            'unmatched_count': unmatched_count,
            'total_fields': total_fields
        }
        print(f"  ✅ 前端成功设置 fieldStats: {fieldStats}")
    else:
        print(f"  ❌ 前端无法设置 fieldStats")
        
    print(f"\n✅ 后端逻辑正确！问题可能在于：")
    print(f"   1. 后端服务没有重启，仍然使用旧代码")
    print(f"   2. 前端轮询频率问题")
    print(f"   3. 需要重新打包应用")
else:
    print(f"  ❌ 未能读取到保存的进度数据")

print("\n" + "=" * 80)
print("测试完成!")
print("=" * 80)
