#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新初始化配置文件
"""
import os
import json
from datetime import datetime

def reinitialize_config():
    """重新初始化配置文件"""
    base_dir = os.path.dirname(__file__)
    
    # 1. 重新初始化开发规范文件
    print("1. 重新初始化开发规范文件")
    standards_file = os.path.join(base_dir, "dev_standards.json")
    builtin_standards = os.path.join(base_dir, "builtin", "default_standards.md")
    
    if os.path.exists(builtin_standards):
        with open(builtin_standards, 'r', encoding='utf-8') as f:
            content = f.read()
        
        data = {
            "version": "1.0",
            "last_modified": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "content": content
        }
        
        with open(standards_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("   OK: 已从内置文件初始化: %s" % standards_file)
    else:
        print("   ERROR: 内置文件不存在: %s" % builtin_standards)
    
    # 2. 重新初始化自定义提示词文件
    print("\n2. 重新初始化自定义提示词文件")
    prompt_file = os.path.join(base_dir, "custom_prompt.txt")
    builtin_prompt = os.path.join(base_dir, "builtin", "default_prompt.txt")
    
    if os.path.exists(builtin_prompt):
        with open(builtin_prompt, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("   OK: 已从内置文件初始化: %s" % prompt_file)
    else:
        print("   ERROR: 内置文件不存在: %s" % builtin_prompt)
    
    print("\n初始化完成！")

if __name__ == "__main__":
    reinitialize_config()
