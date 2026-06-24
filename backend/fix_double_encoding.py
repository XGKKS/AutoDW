#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级编码修复：处理双重编码问题
"""
import os
import json

def fix_double_encoding(file_path):
    """修复双重编码问题（UTF-8 → GBK → UTF-8）"""
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return None
    
    # 读取原始字节
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    
    try:
        # 尝试：UTF-8 -> GBK -> UTF-8
        # 这是常见的双重编码模式
        utf8_text = raw_data.decode('utf-8', errors='ignore')
        gbk_bytes = utf8_text.encode('gbk', errors='ignore')
        fixed_text = gbk_bytes.decode('utf-8', errors='ignore')
        
        if fixed_text and len(fixed_text) > 0:
            # 检查是否有中文
            if any('\u4e00' <= c <= '\u9fff' for c in fixed_text):
                print("成功修复双重编码问题")
                return fixed_text
    except Exception as e:
        print(f"尝试修复失败: {e}")
    
    return None

def fix_json_double_encoding(json_path):
    """修复JSON文件的双重编码问题"""
    if not os.path.exists(json_path):
        print(f"文件不存在: {json_path}")
        return False
    
    # 读取原始字节
    with open(json_path, 'rb') as f:
        raw_data = f.read()
    
    # 尝试修复双重编码
    try:
        # UTF-8 -> GBK -> UTF-8
        utf8_text = raw_data.decode('utf-8')
        gbk_bytes = utf8_text.encode('gbk', errors='replace')
        fixed_text = gbk_bytes.decode('utf-8', errors='replace')
        
        # 解析JSON
        data = json.loads(fixed_text)
        
        # 修复content字段
        if 'content' in data:
            content = data['content']
            # 对content也进行同样的修复
            try:
                content_gbk = content.encode('gbk', errors='replace')
                fixed_content = content_gbk.decode('utf-8', errors='replace')
                data['content'] = fixed_content
            except:
                pass
        
        # 写入UTF-8
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"已修复JSON文件: {json_path}")
        return True
        
    except Exception as e:
        print(f"修复失败: {e}")
        return False

def fix_text_double_encoding(file_path):
    """修复文本文件的双重编码问题"""
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return False
    
    # 读取原始字节
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    
    try:
        # UTF-8 -> GBK -> UTF-8
        utf8_text = raw_data.decode('utf-8')
        gbk_bytes = utf8_text.encode('gbk', errors='replace')
        fixed_text = gbk_bytes.decode('utf-8', errors='replace')
        
        # 写入UTF-8
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_text)
        print(f"已修复文本文件: {file_path}")
        return True
        
    except Exception as e:
        print(f"修复失败: {e}")
        return False

def main():
    print("=" * 60)
    print("高级编码修复：处理双重编码问题")
    print("=" * 60)
    
    # 修复开发规范文件
    print("\n1. 修复开发规范文件")
    standards_file = os.path.join(os.path.dirname(__file__), "dev_standards.json")
    fix_json_double_encoding(standards_file)
    
    # 修复自定义提示词文件
    print("\n2. 修复自定义提示词文件")
    prompt_file = os.path.join(os.path.dirname(__file__), "custom_prompt.txt")
    fix_text_double_encoding(prompt_file)
    
    print("\n" + "=" * 60)
    print("修复完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
