#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试 jieba 分词结果
"""
import jieba

failed_cases = [
    "保养单号",
    "订单金额",
    "应收金额",
    "是否完成"
]

print("=== 调试 jieba 分词 ===\n")
for phrase in failed_cases:
    result = jieba.lcut(phrase, cut_all=False)
    print(f"'{phrase}' -> {result}")
