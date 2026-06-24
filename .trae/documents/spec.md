# 批量建表前后端不一致修正规范

## 1. 需求背景

### 1.1 问题描述
当前批量建表功能存在前后端流程不一致的问题：
1. **jieba分词过程未体现**：后端执行了jieba分词，但前端里程碑中没有显示这一步
2. **最终校验环节未显示**：后端有统一校验和修正逻辑，但前端里程碑中没有这一步
3. **用户困惑**：用户看不到完整的处理流程，不知道系统在做什么

### 1.2 影响范围
- 用户体验：用户无法了解完整的处理进度
- 系统透明度：关键处理步骤对用户不可见
- 问题排查：难以定位性能瓶颈

## 2. 解决方案

### 2.1 核心思路
扩展里程碑系统，从5步扩展为7步，增加：
- 第3步：jieba分词（在字段分组后）
- 第6步：最终校验（在组装DDL后，可选）

### 2.2 修改后的里程碑流程

**不开启校验时（6步）：**
```
1. ✅ 解析Excel
2. ✅ 字段分组
3. ✅ jieba分词 [100/500]
4. ✅ 生成字段名 [3/10]
5. ✅ 组装DDL [5/20]
6. ✅ 完成建表
```

**开启校验时（7步）：**
```
1. ✅ 解析Excel
2. ✅ 字段分组
3. ✅ jieba分词 [100/500]
4. ✅ 生成字段名 [3/10]
5. ✅ 组装DDL [5/20]
6. ✅ 最终校验 [修正中...]
7. ✅ 完成建表
```

## 3. 详细设计

### 3.1 后端修改

#### 3.1.1 扩展里程碑定义
**文件**：`backend/app/main.py`
**位置**：第105-183行 `update_progress` 函数

**修改内容**：
```python
def update_progress(task_id, current, total, table_name=None, stage=None, 
                   matched_count=None, unmatched_count=None, total_fields=None, 
                   enable_validation=False):
    """
    更新任务进度
    
    Args:
        task_id: 任务ID
        current: 当前步骤编号（1-7）
        total: 总步骤数（6或7）
        table_name: 当前处理的表名
        stage: 当前阶段的描述
        matched_count: 已匹配的历史词根数量
        unmatched_count: 未匹配的字段数量
        total_fields: 总字段数量
        enable_validation: 是否启用最终校验
    """
    milestones = [
        {
            "step": 1,
            "title": "解析Excel",
            "icon": "[1/7]",
            "status": "completed" if current >= 1 else "pending"
        },
        {
            "step": 2,
            "title": "字段分组",
            "icon": "[2/7]",
            "status": "completed" if current >= 2 else "pending"
        },
        {
            "step": 3,
            "title": "jieba分词",
            "icon": "[3/7]",
            "status": "active" if current == 3 else ("completed" if current > 3 else "pending"),
            "sub_progress": None
        },
        {
            "step": 4,
            "title": "生成字段名",
            "icon": "[4/7]",
            "status": "active" if current == 4 else ("completed" if current > 4 else "pending"),
            "sub_progress": None
        },
        {
            "step": 5,
            "title": "组装DDL",
            "icon": "[5/7]",
            "status": "active" if current == 5 else ("completed" if current > 5 else "pending"),
            "sub_progress": None
        },
        {
            "step": 6,
            "title": "最终校验",
            "icon": "[6/7]",
            "status": "active" if current == 6 else ("completed" if current > 6 else "pending"),
            "optional": not enable_validation,  # 标记为可选步骤
            "sub_progress": None
        },
        {
            "step": 7,
            "title": "完成建表",
            "icon": "[7/7]",
            "status": "completed" if current >= 7 else "pending"
        }
    ]
    
    # 处理子进度
    if stage:
        if "jieba分词" in stage:
            for m in milestones:
                if m["step"] == 3:
                    m["sub_progress"] = stage.split("[")[-1].replace("]", "")
        elif "生成字段英文名" in stage:
            for m in milestones:
                if m["step"] == 4:
                    m["sub_progress"] = stage.split("[")[-1].replace("]", "")
        elif "组装DDL" in stage:
            for m in milestones:
                if m["step"] == 5:
                    m["sub_progress"] = stage.split("[")[-1].replace("]", "")
        elif "校验" in stage or "修正" in stage:
            for m in milestones:
                if m["step"] == 6:
                    m["sub_progress"] = stage
    
    # ... 其余逻辑保持不变
```

#### 3.1.2 修改字段级处理进度
**文件**：`backend/app/processors/field_processor.py`

**修改点1**：调整所有 `_update_progress` 调用的进度编号
```python
# 第210行：解析Excel
self._update_progress(1, 7, "解析Excel文件...")

# 第262行：字段分组
self._update_progress(2, 7, "按中文词义分组...")

# 第353行：jieba分词（新增）
self._update_progress(3, 7, "jieba分词中...")

# 第581行：生成字段名
self._update_progress(4, 7, "批量生成字段英文名...")

# 第1502行：组装DDL
self._update_progress(5, 7, "组装DDL...")
```

**修改点2**：在 `tokenize_all_fields_root_level` 方法中添加进度更新
```python
def tokenize_all_fields_root_level(self, groups):
    """
    对所有字段进行 jieba 分词，收集所有词根并去重
    """
    logger.info(f"【字段级处理】开始对所有字段进行 jieba 词根级分词，模式: {self.cut_mode}")
    
    # 更新进度：开始jieba分词
    self._update_progress(3, 7, "jieba分词中...")
    
    field_tokenization = {}
    all_roots = []
    total_fields = len(groups)
    processed_fields = 0
    
    for chinese_name in groups.keys():
        # 根据分词模式选择不同的分词方法
        if self.cut_mode == "full":
            roots = jieba.lcut(chinese_name, cut_all=True)
        elif self.cut_mode == "search":
            roots = jieba.lcut_for_search(chinese_name)
        else:
            roots = jieba.lcut(chinese_name, cut_all=False)
        
        # 过滤空字符串
        roots = [r.strip() for r in roots if r.strip()]
        
        field_tokenization[chinese_name] = roots
        all_roots.extend(roots)
        processed_fields += 1
        
        # 每处理100个字段更新一次进度
        if processed_fields % 100 == 0:
            self._update_progress(3, 7, f"jieba分词 [{processed_fields}/{total_fields}]")
        
        logger.debug(f"【字段级处理】分词: '{chinese_name}' -> {roots}")
    
    # 去重
    unique_roots = list(dict.fromkeys(all_roots))
    
    # 更新进度：jieba分词完成
    self._update_progress(3, 7, f"jieba分词完成，共{len(unique_roots)}个词根")
    
    logger.info(f"【字段级处理】词根分词完成，共 {len(field_tokenization)} 个字段，{len(unique_roots)} 个唯一词根")
    
    return field_tokenization, unique_roots
```

#### 3.1.3 修改主流程校验进度
**文件**：`backend/app/main.py`
**位置**：第2411-2509行

**修改内容**：
```python
if enable_validation and results:
    # 更新进度：开始校验（第6步）
    update_progress(task_id, 6, 7, "🔍 统一校验中...")
    logger.info(f"开始统一校验，共 {len(results)} 张表")
    
    error_count = 0
    warning_count = 0
    all_violations = []
    corrected = False
    
    try:
        from app.validators.unified_validator import UnifiedValidator
        
        unified_validator = UnifiedValidator(word_roots=load_word_roots(), standards=load_standards())
        validation_result = unified_validator.validate_batch(results)
        
        all_violations = validation_result['single_violations'] + validation_result['cross_violations']
        error_count = validation_result['error_count']
        warning_count = validation_result['warning_count']
        
        logger.info(f"统一校验完成：{error_count} 个错误，{warning_count} 个警告")
        
        if error_count > 0:
            # 更新进度：开始修正
            update_progress(task_id, 6, 7, "🔧 统一修正中...")
            logger.info("开始统一修正...")
            
            # ... 修正逻辑 ...
            
            logger.info(f"统一修正完成")
    except Exception as e:
        logger.error(f"统一校验或修正失败: {e}")
        update_progress(task_id, 6, 7, f"❌ 校验失败: {str(e)[:50]}")
    
    # ... 其余逻辑 ...
```

#### 3.1.4 调整最终完成进度
**文件**：`backend/app/main.py`
**位置**：第2519行附近

**修改内容**：
```python
# 更新进度：完成建表（第7步）
update_progress(task_id, 7, 7, "✅ 批量建表完成")

save_ddl_history({
    "type": "batch",
    "tables_count": len(tables),
    "success_count": len(tables) - len(errors),
    "ddl": all_ddl,
    "description": f"批量建表: {', '.join(table_names)[:50]}...",
    "db_type": db_type,
    "root_match_priority": root_match_priority,
    "new_roots": deduplicated_new_roots
})
```

### 3.2 前端修改

#### 3.2.1 优化里程碑显示
**文件**：`frontend/src/App.vue`
**位置**：第616-638行

**修改内容**：
```vue
<div v-if="realProgress && realProgress.milestones && realProgress.milestones.length > 0" class="milestone-section">
  <div class="milestone-track">
    <div 
      v-for="(milestone, index) in realProgress.milestones" 
      :key="milestone.step"
      class="milestone-item"
      v-show="!milestone.optional || milestone.status !== 'pending'"
    >
      <div :class="['milestone-circle', milestone.status]">
        <span v-if="milestone.status === 'completed'">✓</span>
        <span v-else-if="milestone.status === 'active'">{{ milestone.step }}</span>
        <span v-else>{{ milestone.step }}</span>
      </div>
      <div class="milestone-icon">{{ milestone.icon }}</div>
      <div class="milestone-title">{{ milestone.title }}</div>
      <div v-if="milestone.sub_progress" class="milestone-sub">
        {{ milestone.sub_progress }}
      </div>
      <div v-if="index < realProgress.milestones.length - 1" class="milestone-line">
        <div :class="['line-fill', milestone.status === 'completed' ? 'completed' : '']"></div>
      </div>
    </div>
  </div>
</div>
```

**关键改动**：
- 添加 `v-show="!milestone.optional || milestone.status !== 'pending'"` 来隐藏未启用的可选步骤

## 4. 测试计划

### 4.1 测试场景

#### 场景1：不开启校验的批量建表
**前置条件**：
- 准备一个包含10张表的Excel文件
- 前端配置：`enable_validation = false`

**预期结果**：
- 显示6步里程碑（跳过第6步"最终校验"）
- 第3步显示jieba分词进度
- 所有步骤按顺序完成

**验证点**：
```
✅ 1. 解析Excel
✅ 2. 字段分组
✅ 3. jieba分词 [100/500]
✅ 4. 生成字段名 [3/10]
✅ 5. 组装DDL [5/10]
✅ 6. 完成建表
```

#### 场景2：开启校验的批量建表
**前置条件**：
- 准备一个包含10张表的Excel文件
- 前端配置：`enable_validation = true`

**预期结果**：
- 显示完整7步里程碑
- 第3步显示jieba分词进度
- 第6步显示校验和修正进度
- 所有步骤按顺序完成

**验证点**：
```
✅ 1. 解析Excel
✅ 2. 字段分组
✅ 3. jieba分词 [100/500]
✅ 4. 生成字段名 [3/10]
✅ 5. 组装DDL [5/10]
✅ 6. 最终校验 [修正中...]
✅ 7. 完成建表
```

#### 场景3：大量字段的jieba分词性能测试
**前置条件**：
- 准备一个包含1000个字段的Excel文件

**预期结果**：
- jieba分词步骤显示实时进度
- 进度更新频率合理（每100个字段更新一次）
- 不会出现界面卡顿

**验证点**：
- 第3步显示进度：`jieba分词 [100/1000]`、`[200/1000]`、...、`[1000/1000]`
- 进度更新间隔约0.5秒

#### 场景4：校验发现错误的修正流程
**前置条件**：
- 准备一个包含命名违规的Excel文件
- 前端配置：`enable_validation = true`

**预期结果**：
- 第6步显示"统一校验中..."
- 发现错误后，显示"统一修正中..."
- 修正完成后，显示修正结果

**验证点**：
```
步骤6的子进度显示：
- "🔍 统一校验中..." → 发现5个错误
- "🔧 统一修正中..." → 修正完成
```

### 4.2 性能测试

#### 测试点1：进度更新频率
- **测试方法**：监控 `update_progress` 函数的调用频率
- **预期结果**：不超过10次/秒
- **验证方式**：查看日志中的进度更新记录

#### 测试点2：前端渲染性能
- **测试方法**：使用Chrome DevTools的Performance面板
- **预期结果**：里程碑更新不会导致明显的界面卡顿
- **验证方式**：FPS保持在50以上

### 4.3 兼容性测试

#### 测试点1：向后兼容
- **测试方法**：使用旧版前端（5步里程碑）连接新版后端
- **预期结果**：前端能正常显示，忽略新增的步骤
- **验证方式**：里程碑显示为前5步

#### 测试点2：混合环境
- **测试方法**：新版前端连接旧版后端
- **预期结果**：前端能正常显示，缺失的步骤显示为pending
- **验证方式**：里程碑显示为5步，第6、7步不显示

## 5. 实施步骤

### 步骤1：修改后端进度更新函数
- 文件：`backend/app/main.py`
- 修改：`update_progress` 函数（第105-183行）
- 验证：单元测试通过

### 步骤2：修改字段级处理进度
- 文件：`backend/app/processors/field_processor.py`
- 修改：所有 `_update_progress` 调用
- 验证：字段级处理流程正常

### 步骤3：修改主流程校验进度
- 文件：`backend/app/main.py`
- 修改：校验和修正进度更新
- 验证：校验流程正常

### 步骤4：修改前端里程碑显示
- 文件：`frontend/src/App.vue`
- 修改：里程碑显示逻辑
- 验证：前端显示正常

### 步骤5：集成测试
- 执行所有测试场景
- 验证性能指标
- 验证兼容性

### 步骤6：文档更新
- 更新用户手册
- 更新API文档
- 更新开发文档

## 6. 验收标准

### 6.1 功能验收
- [ ] 不开启校验时，显示6步里程碑
- [ ] 开启校验时，显示7步里程碑
- [ ] jieba分词进度正常显示
- [ ] 校验进度正常显示
- [ ] 所有测试场景通过

### 6.2 性能验收
- [ ] 进度更新频率不超过10次/秒
- [ ] 前端FPS保持在50以上
- [ ] 无明显界面卡顿

### 6.3 兼容性验收
- [ ] 向后兼容测试通过
- [ ] 混合环境测试通过

### 6.4 文档验收
- [ ] 用户手册已更新
- [ ] API文档已更新
- [ ] 开发文档已更新

## 7. 风险评估

### 7.1 技术风险
- **风险等级**：低
- **原因**：修改仅涉及进度显示，不影响核心业务逻辑
- **缓解措施**：充分测试，确保向后兼容

### 7.2 性能风险
- **风险等级**：低
- **原因**：进度更新频率已控制（每100个字段更新一次）
- **缓解措施**：性能测试验证

### 7.3 兼容性风险
- **风险等级**：中
- **原因**：前后端版本不一致可能导致显示问题
- **缓解措施**：
  - 向后兼容设计
  - 混合环境测试
  - 版本号检查机制

## 8. 发布计划

### 8.1 发布版本
- 版本号：v1.1.0
- 发布类型：功能增强

### 8.2 发布内容
- 扩展里程碑系统（5步→7步）
- 添加jieba分词进度显示
- 添加最终校验进度显示
- 优化前端里程碑显示

### 8.3 发布步骤
1. 代码审查
2. 单元测试
3. 集成测试
4. 性能测试
5. 文档更新
6. 发布公告
7. 用户通知

## 9. 附录

### 9.1 相关文件列表
- `backend/app/main.py` - 主流程和进度更新
- `backend/app/processors/field_processor.py` - 字段级处理
- `frontend/src/App.vue` - 前端里程碑显示

### 9.2 参考文档
- [批量建表前后端不一致修正计划](./批量建表前后端不一致修正计划.md)
- [数仓建表助手开发文档](../../README.md)

### 9.3 变更历史
- 2026-06-07：创建规范文档
