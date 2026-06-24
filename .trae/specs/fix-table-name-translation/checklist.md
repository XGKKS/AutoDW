# Checklist

## 表名转换功能
- [x] `field_processor.py` 中添加了 `translate_table_name` 方法
- [x] 实现了从历史词根匹配表名的逻辑
- [x] 实现了表名转换的fallback机制

## DDL生成修改
- [x] `generate_ddl_for_table` 方法使用英文表名
- [x] 表名符合各数据库的命名规范（MySQL/PostgreSQL/Oracle）

## 集成测试
- [x] 测试中文表名正确转换为英文
- [x] 测试不同数据库类型的表名格式
- [x] 测试批量建表流程中的表名转换