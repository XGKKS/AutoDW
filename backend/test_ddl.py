import requests
import json
import time

url = 'http://localhost:8000/api/generate-ddl'

# 测试复合词匹配：会员等级
print('=' * 70)
print('测试：复合词匹配 - 会员等级')
print('=' * 70)

data = {
    "llm_config": {
        "api_key": "sk-e86ae4039c534863bf160f9c3c662b22",
        "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen3.5-122b-a10b"
    },
    "word_roots_input": {"type": "text", "content": ""},
    "standards_input": {"type": "text", "content": ""},
    "description": "创建一个会员表，包含会员等级、会员名称、会员积分、会员手机号字段",
    "db_type": "mysql",
    "custom_prompt": "",
    "root_match_priority": "abbr",
    "history_roots": []
}

print(f'建表需求: {data["description"]}')
print(f'词根匹配优先级: 缩写')
print('-' * 70)

start = time.time()
try:
    response = requests.post(url, json=data, timeout=120)
    elapsed = time.time() - start
    result = response.json()
    
    if result.get('code') == 0:
        print(f'耗时: {elapsed:.2f}秒')
        print('生成的DDL:')
        print(result.get('data'))
    else:
        print(f'错误: {result.get("message")}')
except Exception as e:
    print(f'错误: {e}')
