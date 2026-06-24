# 修复历史 App.vue 文件功能缺失问题

## 问题描述
用户提供的历史版本 App.vue 文件缺少以下三个功能：
1. 基础配置界面没有 temperature 参数调整模块
2. 单一建表界面没有词根固定预览部分
3. 批量建表界面没有词根固定预览部分

## 需要完成的任务

### 任务1：添加基础配置界面的 temperature 参数调整模块
**位置**: 基础配置界面的 LLM 配置部分
**功能**:
- 添加 temperature 滑块或输入框
- 范围: 0.0 - 1.0，步进 0.1
- 默认值: 0.3
- 说明: temperature 控制输出的随机性，较低值更确定性，较高值更有创造性

**参考代码**:
```vue
<el-form-item label="Temperature">
  <el-slider
    v-model="llmConfig.temperature"
    :min="0"
    :max="1"
    :step="0.1"
    :show-tooltip="true"
    style="width: 200px"
  />
  <span style="margin-left: 10px">{{ llmConfig.temperature }}</span>
</el-form-item>
```

**需要修改的地方**:
1. 在基础配置界面的 LLM 配置表单中添加 temperature 表单项
2. 确保 llmConfig 对象中包含 temperature 属性
3. 确保 API 调用时传递 temperature 参数（generateDDL 和 startBatchGenerate）

### 任务2：添加单一建表界面的词根固定预览部分
**位置**: 单一建表界面的建表配置卡片中
**功能**:
- 显示当前使用的历史词根
- 只读展示，不可编辑
- 可以折叠/展开

**参考代码**:
```vue
<div class="config-item" v-if="historyRoots.length > 0">
  <el-collapse>
    <el-collapse-item title="📚 当前词根预览" name="roots">
      <div class="roots-preview">
        <el-tag v-for="(root, index) in historyRoots.slice(0, 20)" :key="index" size="small" class="root-tag">
          {{ root.chinese_name }}: {{ root.full_root }}
        </el-tag>
        <el-tag v-if="historyRoots.length > 20" size="small" type="info">
          ...还有 {{ historyRoots.length - 20 }} 个词根
        </el-tag>
      </div>
    </el-collapse-item>
  </el-collapse>
</div>
```

**需要添加的 CSS**:
```css
.roots-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.root-tag {
  margin: 2px;
}
```

### 任务3：添加批量建表界面的词根固定预览部分
**位置**: 批量建表界面的配置区域
**功能**:
- 显示当前使用的历史词根
- 只读展示，不可编辑
- 可以折叠/展开

**参考代码**:
与任务2相同，放置在批量配置区域

### 任务4：确保 API 调用传递 temperature 参数
**修改文件**: frontend/src/App.vue

**generateDDL 函数**:
在 axios.post 请求中添加 temperature 参数:
```javascript
const response = await axios.post('/api/generate-ddl', {
  llm_config: {
    api_key: llmConfig.apiKey,
    api_url: llmConfig.apiUrl,
    model: llmConfig.model,
    temperature: llmConfig.temperature || 0.3  // 添加这行
  },
  // ... 其他参数
})
```

**startBatchGenerate 函数**:
在 formData 中添加 temperature 参数:
```javascript
formData.append('temperature', llmConfig.temperature || 0.3)
```

## 实现步骤

1. **等待用户提供历史版本的 App.vue 文件**
2. **添加 llmConfig.temperature 默认值** (在 reactive 对象初始化时)
3. **在基础配置界面添加 temperature 调整模块**
4. **在单一建表界面添加词根预览**
5. **在批量建表界面添加词根预览**
6. **修改 generateDDL 函数传递 temperature 参数**
7. **修改 startBatchGenerate 函数传递 temperature 参数**
8. **测试功能是否正常工作**

## 注意事项
- 词根预览应该是只读的，用户不能直接编辑
- temperature 默认值为 0.3
- 词根预览应该限制显示数量，避免占用太多空间（建议最多显示 20 条）
