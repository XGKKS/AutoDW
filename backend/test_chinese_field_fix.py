#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试中文字段命名修复效果
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.processors.field_processor import FieldProcessor


def test_chinese_field_translation():
    """测试中文词汇翻译"""
    print("=" * 80)
    print("中文字段命名修复测试")
    print("=" * 80)
    
    # 创建 FieldProcessor 实例
    processor = FieldProcessor(
        api_key="test",
        api_url="http://localhost",
        model="test",
        word_roots=[],
        root_match_priority="full"
    )
    
    # 测试用户报告的问题字段
    test_fields = [
        "工单号",
        "原工单号",
        "预约单号",
        "估价单号",
        "备件销售单号",
        "出险单号",
        "理赔单号",
        "索赔单号",
        "保养单号",
        "收费区分代码",
        "工单类型代码",
        "维修类型代码",
        "保险公司代码",
        "工单状态代码",
        "车主编号",
        "车主性质",
        "车牌号",
        "vin",
        "发动机号",
        "维修城市",
        "索赔状态代码",
        "包工方式代码",
        "工单付费类型代码",
        "维修故障描述代码",
        "洗车类型代码",
        "维修类别代码",
        "供应商代码",
        "索赔类型代码",
        "索赔单提报状态",
        "三包状态",
        "故障发生日期",
        "开单人员",
        "开单时间",
        "送单人",
        "送单理赔日期",
        "送修人",
        "送修人性别",
        "送修人电话",
        "预计开工时间",
        "维修开始时间",
        "预计交车时间",
        "交车人",
        "交车日期",
        "交车标识",
        "试车员",
        "提交结算时间",
        "接车日期",
        "竣工时间",
        "完工验收人",
        "收案日期",
        "旧件处理方式",
        "旧件处理时间",
        "旧件备注",
        "上次进厂日期",
        "上次保养日期",
        "上次保养里程",
        "下次保养日期",
        "下次保养里程",
        "进厂行驶里程",
        "出厂行驶里程",
        "换表里程",
        "累计换表里程",
        "行驶总里程",
        "维修单数",
        "工时单价",
        "应收工时费",
        "应收维修材料费",
        "应收销售材料费",
        "应收附加项目费",
        "应收辅料管理费",
        "应收维修金额",
        "备注",
        "是否客户在厂",
        "是否质检",
        "是否洗车",
        "是否第一次保养",
        "是否路试",
        "是否竣工",
        "是否故障维修",
        "是否充电",
        "是否保养",
        "是否换表",
        "是否带走旧件",
        "是否赠送保养",
        "是否新保",
        "是否增项",
        "是否快修",
        "是否终检",
        "是否延期",
    ]
    
    print("\n1. 测试中文词汇翻译")
    print("-" * 80)
    
    has_chinese = False
    for field in test_fields:
        result = processor._fallback_name(field)
        # 检查是否还包含中文
        if any('\u4e00' <= c <= '\u9fff' for c in result):
            has_chinese = True
            print(f"  [CHINESE] {field} -> {result}")
        else:
            print(f"  [OK]     {field} -> {result}")
    
    print(f"\n2. 测试结果")
    print("-" * 80)
    if has_chinese:
        print(f"  警告：仍有中文字段名未完全翻译")
    else:
        print(f"  所有字段名已成功翻译为英文")
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)
    
    return not has_chinese


if __name__ == "__main__":
    success = test_chinese_field_translation()
    sys.exit(0 if success else 1)