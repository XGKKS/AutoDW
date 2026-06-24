#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试主模式：调用LLM生成表名（模拟）
"""
import os
import sys

# 添加 app 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.processors.field_processor import TABLE_NAME_PROMPT


# 开发规范内容（从用户提供的规范中提取）
DEVELOPMENT_STANDARDS = """## 表命名规范

### 分层命名
| 层级 | 格式 | 示例 |
|------|------|------|
| ODS | ods_{源系统缩写}_{源表名} | ods_crm_order |
| DIM | dim_{主题缩写}_{实体名} | dim_pub_store |
| DWD | dwd_{主题缩写}_{内容} | dwd_fin_cashflow |
| DWS | dws_{主题}_{内容}_{维度}_{日期后缀} | dws_fin_revenue_comp_m |
| ADS | ads_{主题}_{内容}_{维度}_{日期后缀} | ads_sales_report_d |

### 主题域缩写
| 主题 | 缩写 |
|------|------|
| 公共 | pub |
| 用户 | user |
| 客户 | cust |
| 商品 | prod |
| 订单 | order |
| 财务 | fin |
| 营销 | mkt |
| 供应链 | scm |
| 工单 | ticket |
| 门店 | store |
| 库存 | inv |
| 人员 | staff |

### 日期后缀
- _d（日）、_w（周）、_m（月）、_q（季）、_y（年）
- 全量快照可省略日期后缀
"""


def build_table_name_prompt(chinese_table_name, db_type, layer):
    """构建表名生成提示词"""
    # 根据数据库类型设置输出示例
    table_name_example = {
        'mysql': 'dwd_fin_order',
        'postgresql': 'dwd.fin_order',
        'oracle': 'DWD.FIN_ORDER'
    }.get(db_type.lower(), 'dwd_fin_order')
    
    # 获取数据库表名格式要求
    table_format = {
        'mysql': '使用下划线前缀表示分层（如 dwd_fin_order）',
        'postgresql': '使用 schema.table 格式（如 dwd.fin_order）',
        'oracle': '使用大写 SCHEMA.TABLE 格式（如 DWD.FIN_ORDER）'
    }.get(db_type.lower(), '使用下划线前缀表示分层')
    
    # 添加分层信息到提示词
    standards_with_layer = DEVELOPMENT_STANDARDS + f"\n\n【当前表分层】{layer}\n【中文表名】{chinese_table_name}"
    
    prompt = TABLE_NAME_PROMPT.format(
        chinese_table_name=chinese_table_name,
        standards_content=standards_with_layer,
        db_type=db_type,
        table_format=table_format,
        table_name_example=table_name_example
    )
    
    return prompt


def simulate_llm_response(chinese_table_name, db_type, layer):
    """模拟LLM生成表名的结果"""
    # 简单的规则匹配模拟
    mappings = {
        ('400工单反馈表', 'mysql', 'dwd'): 'dwd_ticket_feedback',
        ('400工单反馈表', 'postgresql', 'dwd'): 'dwd.ticket_feedback',
        ('400工单回访表', 'mysql', 'dwd'): 'dwd_ticket_return_visit',
        ('400工单回访表', 'postgresql', 'dwd'): 'dwd.ticket_return_visit',
        ('400工单派单表', 'mysql', 'dwd'): 'dwd_ticket_dispatch',
        ('400工单派单表', 'postgresql', 'dwd'): 'dwd.ticket_dispatch',
        ('400工单申请结案表', 'mysql', 'dwd'): 'dwd_ticket_close_apply',
        ('400工单申请结案表', 'postgresql', 'dwd'): 'dwd.ticket_close_apply',
        ('400工单数量', 'mysql', 'dwd'): 'dwd_ticket_qty',
        ('400工单数量', 'postgresql', 'dwd'): 'dwd.ticket_qty',
        ('400工单数量表', 'mysql', 'dwd'): 'dwd_ticket_qty',
        ('400工单数量表', 'postgresql', 'dwd'): 'dwd.ticket_qty',
        ('400工单维度表', 'mysql', 'dim'): 'dim_ticket',
        ('400工单维度表', 'postgresql', 'dim'): 'dim.ticket',
        ('400工单响应表', 'mysql', 'dwd'): 'dwd_ticket_response',
        ('400工单响应表', 'postgresql', 'dwd'): 'dwd.ticket_response',
        ('BU维度表', 'mysql', 'dim'): 'dim_bu',
        ('BU维度表', 'postgresql', 'dim'): 'dim.bu',
        ('门店库存快照表', 'mysql', 'dwd'): 'dwd_store_inv_snapshot',
        ('门店库存快照表', 'postgresql', 'dwd'): 'dwd.store_inv_snapshot',
        ('门店人员维度表', 'mysql', 'dim'): 'dim_store_staff',
        ('门店人员维度表', 'postgresql', 'dim'): 'dim.store_staff',
    }
    
    return mappings.get((chinese_table_name, db_type, layer), f"{layer}_{chinese_table_name}")


def test_main_mode():
    """测试主模式：调用LLM生成表名"""
    print("=" * 80)
    print("主模式测试：调用LLM生成表名")
    print("=" * 80)
    
    # 测试数据
    test_tables = [
        ('400工单反馈表', 'dwd'),
        ('400工单回访表', 'dwd'),
        ('400工单派单表', 'dwd'),
        ('400工单申请结案表', 'dwd'),
        ('400工单数量', 'dwd'),
        ('400工单数量表', 'dwd'),
        ('400工单维度表', 'dim'),
        ('400工单响应表', 'dwd'),
        ('BU维度表', 'dim'),
        ('门店库存快照表', 'dwd'),
        ('门店人员维度表', 'dim'),
    ]
    
    # 显示提示词示例
    print("\n【提示词示例】")
    print("-" * 80)
    sample_prompt = build_table_name_prompt('400工单反馈表', 'postgresql', 'dwd')
    print(sample_prompt[:500] + "...")  # 只显示前500字符
    
    # 测试MySQL
    print("\n\n【MySQL 表名生成结果】")
    print("-" * 80)
    print(f"{'中文表名':<15} {'分层':<5} {'英文表名'}")
    print("-" * 80)
    for chinese_name, layer in test_tables:
        english_name = simulate_llm_response(chinese_name, 'mysql', layer)
        print(f"{chinese_name:<15} {layer:<5} {english_name}")
    
    # 测试PostgreSQL
    print("\n\n【PostgreSQL 表名生成结果】")
    print("-" * 80)
    print(f"{'中文表名':<15} {'分层':<5} {'英文表名'}")
    print("-" * 80)
    for chinese_name, layer in test_tables:
        english_name = simulate_llm_response(chinese_name, 'postgresql', layer)
        print(f"{chinese_name:<15} {layer:<5} {english_name}")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
    print("\n说明：实际使用时，提示词会发送给LLM，LLM根据开发规范生成表名。")
    print("以上是模拟结果，实际结果取决于LLM的理解能力和开发规范的清晰度。")


if __name__ == "__main__":
    test_main_mode()
