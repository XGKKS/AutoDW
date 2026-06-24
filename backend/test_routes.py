import requests
import time

BASE_URL = "http://localhost:8000"

def test_route(name, url, method="GET", payload=None, iterations=5):
    """测试单个路由的性能"""
    print(f"\n=== 测试路由: {name} ===")
    print(f"URL: {url}")
    
    total_elapsed = 0
    success_count = 0
    min_elapsed = float('inf')
    max_elapsed = 0
    
    for i in range(1, iterations + 1):
        start_time = time.time()
        try:
            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=payload, timeout=30)
            
            elapsed = time.time() - start_time
            total_elapsed += elapsed
            min_elapsed = min(min_elapsed, elapsed)
            max_elapsed = max(max_elapsed, elapsed)
            
            if response.status_code == 200:
                success_count += 1
                print("[OK] 第%d次 | 耗时: %.3f秒" % (i, elapsed))
            else:
                print("[ERR] 第%d次 | 耗时: %.3f秒 | 状态码: %d" % (i, elapsed, response.status_code))
                
        except Exception as e:
            elapsed = time.time() - start_time
            print("[EXC] 第%d次 | 耗时: %.3f秒 | 错误: %s" % (i, elapsed, str(e)))
    
    if success_count > 0:
        avg_elapsed = total_elapsed / success_count
        print("\n统计结果 (%d/%d 成功):" % (success_count, iterations))
        print("  平均耗时: %.3f秒" % avg_elapsed)
        print("  最小耗时: %.3f秒" % min_elapsed)
        print("  最大耗时: %.3f秒" % max_elapsed)
    
    return {
        "name": name,
        "url": url,
        "success_count": success_count,
        "total_count": iterations,
        "avg_elapsed": total_elapsed / iterations if iterations > 0 else 0,
        "min_elapsed": min_elapsed,
        "max_elapsed": max_elapsed
    }

def main():
    print("="*70)
    print("         API 路由性能测试")
    print("="*70)
    
    results = []
    
    # 测试各个路由
    results.append(test_route("根路径", f"{BASE_URL}/"))
    results.append(test_route("获取词根列表", f"{BASE_URL}/api/word-roots"))
    results.append(test_route("获取历史字段", f"{BASE_URL}/api/history-fields"))
    results.append(test_route("获取日志", f"{BASE_URL}/api/logs?lines=10"))
    results.append(test_route("获取日志文件列表", f"{BASE_URL}/api/logs/list"))
    
    print("\n" + "="*70)
    print("         测试汇总")
    print("="*70)
    print(f"{'路由名称':<20} {'成功率':<10} {'平均耗时':<10} {'最大耗时':<10}")
    print("-"*70)
    
    for r in results:
        success_rate = "%.0f%%" % (r["success_count"] / r["total_count"] * 100)
        print(f"{r['name']:<20} {success_rate:<10} {r['avg_elapsed']:.3f}s      {r['max_elapsed']:.3f}s")
    
    print("\n注意: DDL生成接口(/api/generate-ddl)需要配置API Key才能测试")
    print("如需测试完整的DDL生成性能，请在前端界面配置API Key后进行测试")

if __name__ == "__main__":
    main()
