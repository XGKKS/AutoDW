import requests
import json
import time

# 测试配置
API_URL = "http://localhost:8000/api/generate-ddl"
TEST_CASE = "创建一个营销活动效果表，包含活动ID、活动名称、优惠券编码、促销类型、广告渠道、点击量、曝光量、订单金额、折扣金额、活动状态、开始时间、结束时间，内容，杂七杂八"
DB_TYPE = "mysql"
ROOT_PRIORITY = "full"

# LLM配置
LLM_CONFIG = {
    "api_key": "sk-e86ae4039c534863bf160f9c3c662b22",
    "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen3.5-122b-a10b"
}

def test_generate_ddl(iteration):
    """执行单次DDL生成测试"""
    print("\n=== 第 %d 次测试 ===" % iteration)

    payload = {
        "llm_config": LLM_CONFIG,
        "word_roots_input": {
            "type": "text",
            "content": ""
        },
        "standards_input": {
            "type": "text",
            "content": ""
        },
        "description": TEST_CASE,
        "db_type": DB_TYPE,
        "custom_prompt": "",
        "root_match_priority": ROOT_PRIORITY,
        "history_roots": []
    }

    start_time = time.time()
    try:
        response = requests.post(API_URL, json=payload, timeout=300)
        elapsed = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                ddl_length = len(result.get("data", ""))
                extracted_roots = result.get("extracted_roots", [])
                print("[OK] 成功 | 耗时: %.2f秒 | DDL长度: %d字符 | 新词根: %d个" % (elapsed, ddl_length, len(extracted_roots)))
                return {
                    "success": True,
                    "elapsed": elapsed,
                    "ddl_length": ddl_length,
                    "extracted_roots_count": len(extracted_roots)
                }
            else:
                print("[FAIL] 失败 | 耗时: %.2f秒 | 错误: %s" % (elapsed, result.get('message', '未知错误')))
                return {
                    "success": False,
                    "elapsed": elapsed,
                    "error": result.get("message", "未知错误")
                }
        else:
            print("[ERR] HTTP错误 | 耗时: %.2f秒 | 状态码: %d" % (elapsed, response.status_code))
            return {
                "success": False,
                "elapsed": elapsed,
                "error": "HTTP %d" % response.status_code
            }
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print("[TOUT] 超时 | 耗时: %.2f秒" % elapsed)
        return {
            "success": False,
            "elapsed": elapsed,
            "error": "请求超时"
        }
    except Exception as e:
        elapsed = time.time() - start_time
        print("[EXCP] 异常 | 耗时: %.2f秒 | 错误: %s" % (elapsed, str(e)))
        return {
            "success": False,
            "elapsed": elapsed,
            "error": str(e)
        }

def main():
    print("="*70)
    print("         DDL生成性能测试")
    print("="*70)
    print("测试用例: %s" % TEST_CASE[:50])
    print("数据库类型: %s" % DB_TYPE)
    print("模型: %s" % LLM_CONFIG['model'])
    print("="*70)

    results = []
    total_elapsed = 0
    success_count = 0

    for i in range(1, 6):
        result = test_generate_ddl(i)
        results.append(result)
        if result["success"]:
            success_count += 1
            total_elapsed += result["elapsed"]

    print("\n" + "="*70)
    print("         测试结果汇总")
    print("="*70)
    print("总测试次数: 5次")
    print("成功次数: %d次" % success_count)
    print("失败次数: %d次" % (5 - success_count))

    if success_count > 0:
        avg_elapsed = total_elapsed / success_count
        elapsed_times = [r["elapsed"] for r in results if r["success"]]
        min_elapsed = min(elapsed_times)
        max_elapsed = max(elapsed_times)

        print("\n耗时统计 (仅成功请求):")
        print("  平均耗时: %.2f秒" % avg_elapsed)
        print("  最小耗时: %.2f秒" % min_elapsed)
        print("  最大耗时: %.2f秒" % max_elapsed)
        print("  总耗时: %.2f秒" % total_elapsed)

    # 保存测试结果到文件
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n测试结果已保存到: test_results.json")

if __name__ == "__main__":
    main()
