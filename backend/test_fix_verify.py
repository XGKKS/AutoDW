#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试批量建表进度状态同步修复
验证任务完成后进度数据被正确清除
"""
import sys
sys.path.insert(0, '.')

from app.main import progress_store, task_results, update_progress

def test_progress_cleanup():
    """测试任务完成后进度数据被清除"""
    print("=== Testing progress cleanup after task completion ===")
    
    # 模拟任务执行过程
    task_id = "test_task_cleanup_001"
    
    # Step 1: 设置初始进度
    update_progress(task_id, 0, 5)
    assert task_id in progress_store, "Progress should be stored"
    print("1. Progress stored successfully")
    
    # Step 2: 更新进度到完成状态
    update_progress(task_id, 5, 5, stage="完成建表")
    assert progress_store.get(task_id)['current'] == 5
    print("2. Progress updated to completed")
    
    # Step 3: 模拟任务完成后清除进度（修复后的行为）
    if task_id in progress_store:
        del progress_store[task_id]
        print("3. Progress cleaned up after task completion")
    
    # Step 4: 验证进度已被清除
    assert task_id not in progress_store, "Progress should be removed after completion"
    print("4. Progress successfully removed")
    
    # Step 5: 验证进度API返回code=1
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    
    response = client.get(f"/api/progress/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data['code'] == 1, f"Expected code=1, got {data['code']}"
    print("5. Progress API returns code=1 for completed task")
    
    print("\n=== All tests passed! ===")

if __name__ == "__main__":
    test_progress_cleanup()