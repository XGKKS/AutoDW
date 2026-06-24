# Tasks

## 1. 添加表名转换方法
- [x] 1.1 在 `field_processor.py` 中添加 `translate_table_name` 方法
- [x] 1.2 实现从历史词根匹配表名的逻辑
- [x] 1.3 实现表名转换的fallback机制

## 2. 修改DDL生成方法
- [x] 2.1 修改 `generate_ddl_for_table` 方法，使用英文表名
- [x] 2.2 确保表名符合各数据库的命名规范

## 3. 集成到字段级处理流程
- [x] 3.1 在批量处理完成后调用表名转换
- [x] 3.2 更新批量建表流程中的DDL生成

## 4. 验证修复效果
- [x] 4.1 创建测试脚本验证表名转换
- [x] 4.2 测试不同数据库类型的表名格式

# Task Dependencies
- Task 1 必须先完成 ✅
- Task 2 依赖于 Task 1 ✅
- Task 3 依赖于 Task 2 ✅
- Task 4 在 Task 3 完成后进行验证 ✅