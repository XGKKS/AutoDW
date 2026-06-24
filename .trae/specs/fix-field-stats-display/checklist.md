# Checklist

## 调试和诊断
- [x] 后端日志中能看到 "【进度更新】任务 xxx 保存匹配统计: matched_count=xxx" 日志
- [x] FieldProcessor._update_progress 方法在 split_into_batches 时被正确调用
- [x] update_progress 函数将 matched_count、unmatched_count、total_fields 保存到 progress_store

## 前端接收
- [x] 前端轮询时能从 /api/progress/{task_id} 获取到 matched_count
- [x] 前端轮询时能从 /api/progress/{task_id} 获取到 unmatched_count
- [x] 前端轮询时能从 /api/progress/{task_id} 获取到 total_fields
- [x] fieldStats.value 被正确更新

## 显示验证
- [x] 批量建表界面显示"历史词根匹配"数量
- [x] 批量建表界面显示"LLM生成"数量
- [x] 批量建表界面显示"总字段数"

## 功能测试
- [x] 测试批量建表流程，统计数据在进度中正确显示
- [x] 测试字段级处理，统计数据实时更新
