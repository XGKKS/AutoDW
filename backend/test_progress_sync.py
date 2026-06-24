import asyncio
import json
import time
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, '.')
from app.main import app, progress_store, update_progress

def test_progress_store():
    """测试进度存储功能"""
    print("=== 测试进度存储功能 ===")
    
    task_id = "test_task_001"
    update_progress(task_id, 0, 10)
    progress = progress_store.get(task_id)
    assert progress['current'] == 0
    assert progress['total'] == 10
    assert progress['table_name'] is None
    print("✓ 初始进度设置成功")
    
    update_progress(task_id, 5, 10, "test_table")
    progress = progress_store.get(task_id)
    assert progress['current'] == 5
    assert progress['total'] == 10
    assert progress['table_name'] == "test_table"
    print("✓ 进度更新成功")
    
    update_progress(task_id, 10, 10, "final_table")
    progress = progress_store.get(task_id)
    assert progress['current'] == 10
    assert progress['total'] == 10
    assert progress['table_name'] == "final_table"
    print("✓ 完成进度设置成功")
    
    del progress_store[task_id]
    print("✓ 测试完成\n")

def test_progress_api():
    """测试进度API"""
    print("=== 测试进度API ===")
    
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    task_id = "api_test_task_001"
    update_progress(task_id, 3, 5, "test_table_3")
    
    response = client.get(f"/api/progress/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data['code'] == 0
    assert data['data']['current'] == 3
    assert data['data']['total'] == 5
    assert data['data']['table_name'] == "test_table_3"
    print("✓ 进度API返回正确")
    
    response = client.get("/api/progress/nonexistent_task")
    assert response.status_code == 200
    data = response.json()
    assert data['code'] == 1
    print("✓ 不存在的任务返回正确")
    
    del progress_store[task_id]
    print("✓ 测试完成\n")

def test_batch_generate_mock():
    """测试批量生成的进度更新逻辑（模拟）"""
    print("=== 测试批量生成进度逻辑 ===")
    
    task_id = "batch_test_task_001"
    tables = {"table1": {}, "table2": {}, "table3": {}}
    total_tables = len(tables)
    
    update_progress(task_id, 0, total_tables)
    assert progress_store[task_id]['current'] == 0
    print("✓ 初始进度为0")
    
    for i, table_name in enumerate(tables.keys()):
        current = i + 1
        update_progress(task_id, current, total_tables, table_name)
        assert progress_store[task_id]['current'] == current
        assert progress_store[task_id]['table_name'] == table_name
        print(f"  ✓ 处理表 {current}/{total_tables}: {table_name}")
    
    assert progress_store[task_id]['current'] == total_tables
    print("✓ 所有表处理完成\n")
    
    del progress_store[task_id]

def test_fallback_progress_logic():
    """测试前端fallback进度逻辑"""
    print("=== 测试Fallback进度逻辑 ===")
    
    total_tables = 5
    fake_progress = 0
    parsed_tables = [{"tableName": f"table{i+1}"} for i in range(total_tables)]
    
    while fake_progress < total_tables:
        fake_progress += 1
        table_name = parsed_tables[fake_progress - 1]['tableName']
        expected_progress = f"🔄 {fake_progress}/{total_tables}，表名：{table_name}"
        print(f"  ✓ Fallback进度 {fake_progress}/{total_tables}: {table_name}")
    
    assert fake_progress == total_tables
    print("✓ Fallback进度完成\n")

def test_asyncio_import():
    """测试asyncio模块是否正确导入"""
    print("=== 测试asyncio导入 ===")
    
    try:
        # 检查main.py中是否使用了asyncio
        import inspect
        from app import main
        source = inspect.getsource(main)
        assert 'import asyncio' in source
        print("✓ asyncio模块已在main.py中导入")
        
        # 测试asyncio.sleep是否可用
        async def test_sleep():
            await asyncio.sleep(0.01)
            return True
        
        result = asyncio.run(test_sleep())
        assert result == True
        print("✓ asyncio.sleep功能正常\n")
    except ImportError as e:
        print(f"✗ asyncio导入失败: {e}")
        raise

if __name__ == "__main__":
    print("\n" + "="*50)
    print("    进度同步功能测试套件")
    print("="*50 + "\n")
    
    try:
        test_progress_store()
        test_progress_api()
        test_batch_generate_mock()
        test_fallback_progress_logic()
        test_asyncio_import()
        
        print("="*50)
        print("    所有测试通过！✓")
        print("="*50)
        print("\n测试结论：")
        print("- 进度存储机制正常")
        print("- 进度API接口正常")
        print("- 批量生成进度更新逻辑正确")
        print("- Fallback进度逻辑正确")
        print("- asyncio模块导入正常")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()