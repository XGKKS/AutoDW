# 字段级处理子流程提级 Spec

## Why
当前里程碑系统中，jieba分词和历史词根匹配隐藏在第3步内部，用户无法直观看到这些重要步骤的执行进度。用户需要将这些子流程提级到主流程，以便实时监控分词、匹配等关键步骤的执行情况。

## What Changes
- 将里程碑系统从7步扩展到9步
- 将"jieba分词"和"历史词根匹配"从第3步内部提级为独立的里程碑步骤
- 调整后续步骤的编号和进度更新逻辑
- 更新前端里程碑显示组件以支持新的步骤结构

## Impact
- Affected specs: 批量建表进度显示系统
- Affected code:
  - backend/app/main.py (update_progress函数)
  - backend/app/processors/field_processor.py (进度更新调用)
  - frontend/src/App.vue (里程碑显示)

## ADDED Requirements

### Requirement: 里程碑步骤扩展
系统 SHALL 将里程碑从7步扩展到9步，新增步骤包括：
1. 解析Excel
2. 字段分组
3. **jieba分词** (原第3步，现独立)
4. **历史词根匹配** (新增)
5. 生成字段名 (原第4步)
6. 组装DDL (原第5步)
7. 最终校验 (原第6步)
8. 完成建表 (原第7步)

#### Scenario: jieba分词进度显示
- **WHEN** 系统执行jieba分词时
- **THEN** 用户能看到第3步"jieba分词"处于active状态，并显示子进度（如"100/500"）

#### Scenario: 历史词根匹配进度显示
- **WHEN** 系统执行历史词根匹配时
- **THEN** 用户能看到第4步"历史词根匹配"处于active状态，并显示匹配进度

### Requirement: 进度更新逻辑调整
系统 SHALL 调整所有进度更新调用以匹配新的步骤编号：
- jieba分词: 步骤编号从3调整为3
- 历史词根匹配: 步骤编号为4 (新增)
- 生成字段名: 步骤编号从4调整为5
- 组装DDL: 步骤编号从5调整为6
- 最终校验: 步骤编号从6调整为7
- 完成建表: 步骤编号从7调整为8

## MODIFIED Requirements

### Requirement: 里程碑显示
系统 SHALL 显示扩展后的里程碑列表，每个里程碑包含：
- step: 步骤编号 (1-9)
- title: 步骤标题
- icon: 步骤图标 (如"[1/9]")
- status: 步骤状态 (pending/active/completed)
- sub_progress: 子进度信息 (可选)
- optional: 是否为可选步骤 (可选)

## REMOVED Requirements

### Requirement: 第3步内部子流程隐藏
**Reason**: 用户需要看到分词和匹配的详细进度
**Migration**: 将子流程提级为独立的主里程碑步骤
