import re

def extract_new_roots_from_response(content: str, existing_roots: list) -> list:
    new_roots = []
    if '【新词根】' not in content:
        return new_roots

    print("检测到【新词根】标记")

    existing_chinese = {r.get('chinese_name', '') for r in existing_roots}

    chinese_pattern = re.compile(r'[\u4e00-\u9fa5]')

    pattern = re.compile(r'【新词根】(.+?)(?=\n|$|【新词根】)', re.DOTALL)
    matches = pattern.findall(content)

    print(f"找到 {len(matches)} 个新词根匹配")

    for match in matches:
        line = match.strip()
        if not line:
            continue
        parts = line.split(':', 3)
        if len(parts) >= 4:
            chinese_name = parts[2].strip()
            if chinese_name and chinese_name not in existing_chinese:
                full_root = parts[0].strip()
                abbr_root = parts[1].strip()

                has_chinese_0 = bool(chinese_pattern.search(full_root))
                has_chinese_1 = bool(chinese_pattern.search(abbr_root))

                if has_chinese_0 and not has_chinese_1:
                    full_root, abbr_root = abbr_root, full_root
                    print(f"交换词根顺序: {abbr_root} -> {full_root}")

                new_roots.append({
                    'business_domain': '基础通用',
                    'chinese_name': chinese_name,
                    'full_root': full_root,
                    'abbr_root': abbr_root,
                    'recommended_type': parts[3].strip()
                })
                existing_chinese.add(chinese_name)
                print(f"提取新词根: {chinese_name} -> {full_root}")

    print(f"共提取 {len(new_roots)} 个新词根")
    return new_roots

test_content = """【新词根】销售:sale:销售:-
【新词根】数:cnt:数量:INT
【新词根】客单价:avg_usr_amt:客单价:DECIMAL(18,4)
【新词根】客流量:traffic:客流量:INT
【新词根】坪效:sale_per_area:坪效:DECIMAL(18,4)
【新词根】面积:area:面积:DECIMAL(10,2)"""

existing_roots = []

result = extract_new_roots_from_response(test_content, existing_roots)

print("\n=== 提取结果 ===")
for root in result:
    print(f"中文名称: {root['chinese_name']}, 全称: {root['full_root']}, 缩写: {root['abbr_root']}, 类型: {root['recommended_type']}")

print(f"\n总提取数量: {len(result)}")

print("\n=== 验证 ===")
all_correct = all(
    not re.search(r'[\u4e00-\u9fa5]', root['full_root']) and
    not re.search(r'[\u4e00-\u9fa5]', root['abbr_root'])
    for root in result
)
print(f"所有词根的full_root和abbr_root都不包含中文: {'✓' if all_correct else '✗'}")