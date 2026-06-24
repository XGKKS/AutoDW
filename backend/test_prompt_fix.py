"""测试自定义提示词修复逻辑"""

def test_custom_prompt_without_placeholders():
    """测试自定义提示词中没有占位符时，建表需求是否会被自动添加"""
    custom_prompt = """你是一位专业的数据仓库DDL生成专家。你的职责是根据用户需求和开发规范，生成100%符合规范的DDL语句。"""
    
    description = "创建一个会员表，包含会员等级、会员名称、会员积分、会员手机号字段"
    db_type_name = "MySQL"
    db_example = "表名格式: dwd_xxx\n示例DDL: CREATE TABLE..."
    word_roots_content = "会员:mbr\n等级:lvl\n积分:pts"
    
    # 模拟修复后的逻辑
    try:
        prompt = custom_prompt.format(
            word_roots_content=word_roots_content,
            description=description,
            db_type=db_type_name,
            root_match_priority="全称",
            standards_content="",
            db_example=db_example
        )
    except KeyError:
        prompt = f"{custom_prompt}\n\n【建表需求】\n{description}\n\n【数据库类型】\n{db_type_name}\n{db_example}\n\n【词根参考】\n{word_roots_content}"
    
    # 新增的检查逻辑
    if description and description not in prompt:
        prompt = f"{custom_prompt}\n\n【建表需求】\n{description}\n\n【数据库类型】\n{db_type_name}\n{db_example}\n\n【词根参考】\n{word_roots_content}"
    
    # 验证结果
    print("测试1: 自定义提示词中没有占位符")
    print("=" * 60)
    print(f"原始自定义提示词长度: {len(custom_prompt)}")
    print(f"处理后的提示词长度: {len(prompt)}")
    print(f"建表需求是否包含在提示词中: {'【建表需求】' in prompt}")
    print(f"具体需求是否包含: {'会员等级' in prompt and '会员名称' in prompt}")
    print()
    print("处理后的提示词内容:")
    print("-" * 60)
    print(prompt[:500], "..." if len(prompt) > 500 else "")
    print("-" * 60)
    print()
    
    assert "【建表需求】" in prompt, "建表需求标记应该在提示词中"
    assert description in prompt, "具体建表需求应该在提示词中"
    print("[OK] 测试1通过: 建表需求已正确添加到提示词中")
    print()


def test_custom_prompt_with_placeholders():
    """测试自定义提示词中有占位符时，是否正常工作"""
    custom_prompt = """你是DDL专家。【建表需求】{description}\n【词根参考】{word_roots_content}"""
    
    description = "创建订单表，包含订单ID、订单金额"
    word_roots_content = "订单:ord\n金额:amt"
    db_type_name = "MySQL"
    db_example = "示例DDL..."
    
    # 模拟修复后的逻辑
    try:
        prompt = custom_prompt.format(
            word_roots_content=word_roots_content,
            description=description,
            db_type=db_type_name,
            root_match_priority="全称",
            standards_content="",
            db_example=db_example
        )
    except KeyError:
        prompt = f"{custom_prompt}\n\n【建表需求】\n{description}"
    
    # 新增的检查逻辑
    if description and description not in prompt:
        prompt = f"{custom_prompt}\n\n【建表需求】\n{description}"
    
    print("测试2: 自定义提示词中有占位符")
    print("=" * 60)
    print(f"处理后的提示词:")
    print(prompt)
    print("-" * 60)
    
    assert description in prompt, "具体建表需求应该在提示词中"
    assert "订单表" in prompt, "订单表应该在提示词中"
    print("[OK] 测试2通过: 有占位符时正常工作")
    print()


if __name__ == "__main__":
    print("测试自定义提示词修复逻辑")
    print("=" * 60)
    print()
    
    test_custom_prompt_without_placeholders()
    test_custom_prompt_with_placeholders()
    
    print("=" * 60)
    print("所有测试通过!")
