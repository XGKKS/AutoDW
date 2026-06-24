#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复配置文件编码问题
"""
import os
import json

def fix_encoding(file_path):
    """修复文件编码"""
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return False
    
    # 尝试多种编码读取
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
    
    content = None
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                # 如果读取成功且内容看起来正常（不是乱码）
                if content and not content.startswith('\x00'):
                    print(f"使用 {encoding} 编码读取成功")
                    break
        except Exception:
            continue
    
    if content is None:
        print(f"无法读取文件: {file_path}")
        return False
    
    # 写入时强制使用UTF-8
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已修复文件编码: {file_path}")
        return True
    except Exception as e:
        print(f"修复失败: {e}")
        return False

def fix_json_encoding(json_path):
    """修复JSON文件编码"""
    if not os.path.exists(json_path):
        print(f"文件不存在: {json_path}")
        return False
    
    # 读取原始字节
    with open(json_path, 'rb') as f:
        raw_data = f.read()
    
    # 尝试解码
    encodings = ['utf-8', 'gbk', 'gb2312']
    data = None
    
    for encoding in encodings:
        try:
            decoded = raw_data.decode(encoding)
            # 尝试解析JSON
            data = json.loads(decoded)
            print(f"使用 {encoding} 编码解析成功")
            break
        except Exception:
            continue
    
    if data is None:
        print(f"无法解析JSON文件: {json_path}")
        return False
    
    # 重新写入UTF-8
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"已修复JSON文件: {json_path}")
        return True
    except Exception as e:
        print(f"修复失败: {e}")
        return False

def main():
    print("=" * 60)
    print("修复配置文件编码问题")
    print("=" * 60)
    
    # 修复开发规范文件
    print("\n1. 修复开发规范文件")
    standards_file = os.path.join(os.path.dirname(__file__), "dev_standards.json")
    fix_json_encoding(standards_file)
    
    # 修复自定义提示词文件
    print("\n2. 修复自定义提示词文件")
    prompt_file = os.path.join(os.path.dirname(__file__), "custom_prompt.txt")
    fix_encoding(prompt_file)
    
    print("\n" + "=" * 60)
    print("修复完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
