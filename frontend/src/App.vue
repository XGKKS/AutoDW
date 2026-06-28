<template>
  <div class="app-wrapper">
    <aside class="sidebar">
      <div class="logo">
        <div class="logo-icon">🗄️</div>
        <div class="logo-text">数仓建表助手</div>
      </div>
      <nav class="nav-menu">
        <div
          class="nav-item"
          :class="{ active: activeMenu === 'config' }"
          @click="activeMenu = 'config'"
        >
          <span class="nav-icon">📋</span>
          <span class="nav-text">基础配置</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: activeMenu === 'standards' }"
          @click="activeMenu = 'standards'"
        >
          <span class="nav-icon">📜</span>
          <span class="nav-text">规范管理</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: activeMenu === 'batch' }"
          @click="activeMenu = 'batch'"
        >
          <span class="nav-icon">⚡</span>
          <span class="nav-text">建表生成</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: activeMenu === 'history' }"
          @click="activeMenu = 'history'"
        >
          <span class="nav-icon">📜</span>
          <span class="nav-text">建表历史</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: activeMenu === 'governance' }"
          @click="activeMenu = 'governance'"
        >
          <span class="nav-icon">&#x1F4CA;</span>
          <span class="nav-text">词根治理</span>
        </div>
      </nav>
    </aside>

    <div class="main-container">
      <header class="header">
        <div class="header-title">
          {{ activeMenu === 'config' ? '基础配置' : (activeMenu === 'standards' ? '开发规范管理' : (activeMenu === 'governance' ? '词根治理' : (activeMenu === 'batch' ? '建表生成' : (activeMenu === 'history' ? '建表历史' : '单一建表')))) }}
        </div>
        <div class="header-actions">
          <el-button circle @click="showSettings = true">
            <span>⚙️</span>
          </el-button>
        </div>
      </header>

      <main class="content">
        <div v-show="activeMenu === 'config'" class="config-view">
          <el-card class="config-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">🤖 LLM 配置</span>
              </div>
            </template>
            <div class="config-selector">
              <el-select v-model="selectedConfig" placeholder="选择配置" size="large" style="width: 240px">
                <el-option
                  v-for="config in savedConfigs"
                  :key="config.name"
                  :label="config.name + (config.isDefault ? ' ⭐' : '')"
                  :value="config.name"
                />
              </el-select>
              <el-button type="warning" plain @click="setAsDefault" :disabled="!selectedConfig">设为默认</el-button>
              <el-button type="primary" @click="showSaveDialog">保存配置</el-button>
              <el-button type="danger" plain @click="deleteConfig" :disabled="!selectedConfig">删除</el-button>
            </div>
            <div class="llm-form-container">
              <div class="llm-form-left">
                <el-form :model="llmConfig" label-width="100px" class="llm-form">
                  <el-form-item label="API Key">
                    <div class="api-key-input">
                      <el-input
                        v-if="!apiKeySaved"
                        v-model="llmConfig.apiKey"
                        type="password"
                        placeholder="请输入 API Key"
                        size="large"
                      />
                      <div v-else class="api-key-saved">
                        <span class="key-placeholder">API Key 已设置</span>
                        <el-button type="warning" size="small" @click="resetApiKey">修改</el-button>
                      </div>
                    </div>
                  </el-form-item>
                  <el-form-item label="API URL">
                    <el-input
                      v-model="llmConfig.apiUrl"
                      placeholder="请输入 API URL"
                      size="large"
                    />
                  </el-form-item>
                  <el-form-item label="Model">
                    <el-input
                      v-model="llmConfig.model"
                      placeholder="请输入模型名称"
                      size="large"
                    />
                  </el-form-item>
                  <el-form-item label="行业背景">
                    <el-input
                      v-model="llmConfig.industryContext"
                      type="textarea"
                      :rows="4"
                      placeholder="请输入当前项目所属行业背景，例如：保险、零售、电商、制造、医疗等，并补充核心业务术语或场景"
                    />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" size="large" @click="testConnection" :loading="testing">
                      测试连接
                    </el-button>
                  </el-form-item>
                </el-form>
              </div>
                <div class="llm-form-right">
                  <div class="temperature-section">
                    <div class="section-title">🌡️ Temperature</div>
                    <div class="temperature-config-horizontal">
                    <el-slider
                      v-model="llmConfig.temperature"
                      :min="0"
                      :max="1"
                      :step="0.1"
                      :marks="{0:'0', 0.3:'0.3', 0.5:'0.5', 0.7:'0.7', 1:'1'}"
                      style="flex: 1; margin-right: 15px"
                    />
                    <el-input-number
                      v-model="llmConfig.temperature"
                      :min="0"
                      :max="1"
                      :step="0.1"
                      :precision="1"
                      controls-position="right"
                      style="width: 90px"
                    />
                  </div>
                    <div class="temperature-hint">
                      <span>控制输出随机性：0=确定性输出，1=创意输出。推荐值：0.3（DDL生成）</span>
                    </div>
                    <div class="config-divider"></div>
                    <div class="section-title">🔤 缩写最大字母数</div>
                    <div class="temperature-config-horizontal">
                      <el-slider
                        v-model="llmConfig.abbrMaxLen"
                        :min="1"
                        :max="12"
                        :step="1"
                        :marks="{1:'1', 4:'4', 8:'8', 12:'12'}"
                        style="flex: 1; margin-right: 15px"
                      />
                      <el-input-number
                        v-model="llmConfig.abbrMaxLen"
                        :min="1"
                        :max="12"
                        :step="1"
                        controls-position="right"
                        style="width: 90px"
                      />
                    </div>
                    <div class="temperature-hint">
                      <span>仅在“优先缩写”模式生效，默认 4。单表生成、批量生成、校验都会使用这个上限。</span>
                    </div>
                  </div>
                </div>
              </div>
            </el-card>

          <el-card class="config-card db-config-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">数据库连接配置</span>
                <div class="header-actions">
                  <el-button type="info" plain size="small" @click="loadDbConnections">刷新</el-button>
                  <el-button type="primary" size="small" @click="showDbConnectionDialog()">新增连接</el-button>
                </div>
              </div>
            </template>
            <el-table :data="dbConnections" size="small" stripe>
              <el-table-column prop="name" label="连接名称" min-width="140" />
              <el-table-column prop="db_type" label="数据库类型" width="140">
                <template #default="scope">
                  <el-tag>{{ formatDbType(scope.row.db_type) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="host" label="主机" min-width="150" show-overflow-tooltip />
              <el-table-column prop="port" label="端口" width="90" />
              <el-table-column prop="database" label="数据库/服务名" min-width="160" show-overflow-tooltip />
              <el-table-column prop="username" label="用户名" width="120" />
              <el-table-column label="密码" width="80">
                <template #default="scope">
                  <el-tag :type="scope.row.has_password ? 'success' : 'info'" size="small">
                    {{ scope.row.has_password ? '已配置' : '未配置' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="240">
                <template #default="scope">
                  <el-button size="small" @click="testDbConnection(scope.row)" :loading="testingDbConnectionId === scope.row.id">测试</el-button>
                  <el-button size="small" type="primary" @click="showDbConnectionDialog(scope.row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteDbConnection(scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-if="dbConnections.length === 0" description="暂无数据库连接配置" />
          </el-card>

          <div class="side-by-side-container">
            <el-card class="prompt-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="card-title">💡 自定义提示词</span>
                  <div class="header-actions">
                    <el-button type="primary" plain size="small" @click="saveCustomPrompt">保存</el-button>
                    <el-button type="info" plain size="small" @click="resetPrompt">恢复默认</el-button>
                  </div>
                </div>
              </template>
              <el-input
                v-model="customPrompt"
                type="textarea"
                :rows="15"
                placeholder="提示词支持变量：
{history_roots} - 历史词根
{word_roots_content} - 词根内容
{standards_content} - 规范内容
{industry_context} - 行业背景
{description} - 建表需求
{db_type} - 数据库类型
                {root_match_priority} - 词根匹配优先级"
              />
            </el-card>
          </div>
        </div>

        <div v-show="activeMenu === 'standards'" class="standards-view">
          <div class="standards-layout">
            <el-card class="standards-list-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="card-title">📚 规范列表</span>
                  <div class="header-actions">
                    <el-button type="primary" plain size="small" @click="createNewStandard">
                      <span>➕</span> 新建规范
                    </el-button>
                    <el-button type="info" plain size="small" @click="loadStandards">刷新</el-button>
                  </div>
                </div>
              </template>
              <div class="standards-list">
                <el-table :data="standardsList" size="small" @row-click="selectStandard">
                  <el-table-column type="index" label="序号" width="60" />
                  <el-table-column prop="name" label="规范名称" min-width="300" show-overflow-tooltip />
                  <el-table-column prop="is_active" label="状态" width="80">
                    <template #default="scope">
                      <el-tag :type="scope.row.is_active ? 'success' : 'info'">
                        {{ scope.row.is_active ? '✓ 启用' : '未启用' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="updated_at" label="更新时间" width="180" />
                  <el-table-column label="操作" width="240">
                    <template #default="scope">
                      <el-button 
                        :type="scope.row.is_active ? 'warning' : 'success'" 
                        link 
                        size="small" 
                        @click="toggleStandardActive(scope.row)"
                      >
                        {{ scope.row.is_active ? '禁用' : '启用' }}
                      </el-button>
                      <el-button type="primary" link size="small" @click="editStandard(scope.row)">编辑</el-button>
                      <el-button 
                        type="danger" 
                        link 
                        size="small" 
                        @click="deleteStandard(scope.row.id)"
                        :disabled="scope.row.id === 'default'"
                        :class="{ 'disabled-btn': scope.row.id === 'default' }"
                      >
                        {{ scope.row.id === 'default' ? '不可删除' : '删除' }}
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-card>
            
            <div class="standards-content">
              <el-card class="standards-editor-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span class="card-title">✏️ 规范编辑</span>
                    <div class="header-actions">
                      <el-button type="primary" plain size="small" @click="saveStandards" :disabled="!standardsContent">保存修改</el-button>
                      <el-button type="info" plain size="small" @click="loadStandards">刷新</el-button>
                    </div>
                  </div>
                </template>
                <div class="standards-edit-container">
                  <el-input
                    v-model="standardsContent"
                    type="textarea"
                    :rows="20"
                    placeholder="在此编辑开发规范文档..."
                    class="standards-textarea"
                  />
                </div>
              </el-card>
              
              <el-card class="standards-preview-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span class="card-title">👁️ 实时预览</span>
                  </div>
                </template>
                <div class="standards-preview-container">
                  <div v-if="!standardsContent" class="empty-preview">
                    <el-empty description="暂无规范内容，请先编辑或上传" />
                  </div>
                  <div v-else class="preview-content" v-html="renderMarkdown(standardsContent)"></div>
                </div>
              </el-card>
            </div>
          </div>
        </div>

        <div v-show="activeMenu === 'ddl'" class="ddl-view">
          <el-card class="config-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">⚙️ 建表配置</span>
                <div class="timer-display">
                  <el-tag :type="generating ? 'warning' : (generateDuration > 0 ? 'success' : 'info')" size="small">
                    <span v-if="generating">⏱️ 生成中: {{ formatDuration(currentDuration) }}</span>
                    <span v-else-if="generateDuration > 0">✅ 耗时: {{ formatDuration(generateDuration) }}</span>
                    <span v-else>⏳ 准备就绪</span>
                  </el-tag>
                </div>
              </div>
            </template>
            <div class="ddl-config-row">
              <div class="config-item">
                <span class="config-label">词根匹配优先级：</span>
                <el-select v-model="rootMatchPriority" style="width: 180px">
                  <el-option label="🌟 优先词根全称" value="full" />
                  <el-option label="🔤 优先缩写词根" value="abbr" />
                </el-select>
              </div>
              <div class="config-item">
                <span class="config-label">数据库类型：</span>
                <el-select v-model="dbType" style="width: 150px">
                  <el-option label="🐬 MySQL" value="mysql" />
                  <el-option label="🐘 PostgreSQL" value="postgresql" />
                  <el-option label="🔶 Oracle" value="oracle" />
                </el-select>
              </div>
              <div class="config-item">
                <span class="config-label">最终校验：</span>
                <el-switch v-model="enableValidation" active-text="开启" inactive-text="关闭" />
                <span class="config-hint">（关闭可提高生成速度）</span>
              </div>
            </div>
          </el-card>

          <div class="ddl-input-section">
            <el-card class="input-card requirement-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="card-title">📋 建表需求</span>
                </div>
              </template>
              <el-input
                v-model="description"
                type="textarea"
                :rows="8"
                placeholder="请输入自然语言描述，例如：
创建一个订单表，包含订单号、用户ID、金额、下单时间等字段"
              />
              <div class="generate-action">
                <el-button type="success" size="large" @click="generateDDL" :loading="generating" class="generate-btn">
                  <span v-if="!generating">✨</span>
                  {{ generating ? '生成中...' : '生成 DDL' }}
                </el-button>
              </div>
            </el-card>

            <el-card class="new-roots-card" shadow="hover">
              <div class="new-roots-header">
                <span class="new-roots-title">🌱 发现新词根</span>
                <el-tag type="warning" size="small">{{ singleNewRoots.length }} 个</el-tag>
                <el-button type="success" size="small" @click="saveSingleNewRoots" class="save-roots-btn" :disabled="singleNewRoots.length === 0">
                  💾 保存到历史词根
                </el-button>
              </div>
              <div class="new-roots-list">
                <el-table v-if="singleNewRoots.length > 0" :data="singleNewRoots" size="small" max-height="300" stripe>
                  <el-table-column prop="chinese_name" label="中文名" width="120" />
                  <el-table-column prop="full_root" label="词根全称" width="150" />
                  <el-table-column prop="abbr_root" label="缩写" width="100" />
                  <el-table-column prop="recommended_type" label="推荐类型" width="120" />
                  <el-table-column prop="business_domain" label="业务域" />
                </el-table>
                <el-empty v-else description="暂无新词根，生成 DDL 后将自动显示" />
              </div>
            </el-card>
          </div>

          <el-card class="result-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">🎯 生成的 DDL</span>
                <el-button
                  v-if="generatedSQL"
                  type="primary"
                  plain
                  size="small"
                  @click="copySQL"
                >
                  复制 SQL
                </el-button>
              </div>
            </template>
            <div v-if="generatedSQL" class="sql-container">
              <pre class="sql-output" v-html="highlightSQL(generatedSQL)"></pre>
            </div>
            <el-empty v-else description="点击上方「生成 DDL」按钮生成建表语句" />
          </el-card>
        </div>

        <div v-show="activeMenu === 'batch'" class="batch-view">
          <div class="batch-top-section">
            <el-card class="config-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">⚡ 建表生成</span>
              </div>
            </template>

            <div class="generation-mode-switch">
              <span class="config-label">输入方式：</span>
              <el-radio-group v-model="generationMode" :disabled="batchGenerating">
                <el-radio-button label="text">文本输入</el-radio-button>
                <el-radio-button label="excel">Excel上传</el-radio-button>
              </el-radio-group>
            </div>

            <el-card v-if="generationMode === 'text'" class="text-input-card" shadow="never">
              <template #header>
                <div class="card-header">
                  <span class="card-title">📝 建表需求</span>
                </div>
              </template>
              <el-input
                v-model="description"
                type="textarea"
                :rows="8"
                :disabled="batchGenerating"
                placeholder="请输入自然语言描述，例如：
创建一个订单表，包含订单号、用户ID、金额、下单时间等字段"
              />
            </el-card>
            
            <div v-else class="batch-upload-section">
              <el-upload
                ref="batchUpload"
                :auto-upload="false"
                :on-change="handleBatchFileChange"
                :limit="1"
                accept=".xlsx"
                :disabled="batchGenerating"
              >
                <el-button type="primary" plain :disabled="batchGenerating">
                  <span>📁</span> 选择Excel文件
                </el-button>
              </el-upload>
              <el-button type="success" @click="downloadBatchTemplate" :disabled="batchGenerating">
                <span>📥</span> 下载模板
              </el-button>
            </div>

            <div v-if="generationMode === 'excel' && batchFileName" class="batch-file-info">
              <el-tag effect="dark">{{ batchFileName }}</el-tag>
              <span class="batch-file-hint">已选择文件，可点击"开始生成"按钮</span>
            </div>

            <div v-if="generationMode === 'excel' && parsedBatchTables.length > 0" class="batch-preview">
              <div class="preview-title">📋 解析预览 ({{ parsedBatchTables.length }} 张表)</div>
              <el-table :data="parsedBatchTables" size="small" max-height="700" stripe>
                <el-table-column type="index" label="序号" width="70" :index="(index) => index + 1" />
                <el-table-column prop="layer" label="分层" width="100" />
                <el-table-column prop="subjectDomain" label="主题域" width="120" />
                <el-table-column prop="tableName" label="表名" width="260" />
                <el-table-column prop="fieldCount" label="字段数量" width="100" />
                <el-table-column prop="fields" label="字段明细" show-overflow-tooltip />
              </el-table>
            </div>

            <div class="batch-config-row">
              <div class="config-item">
                <span class="config-label">数据库类型：</span>
                <el-select v-model="batchDbType" style="width: 150px" :disabled="batchGenerating">
                  <el-option label="🐬 MySQL" value="mysql" />
                  <el-option label="🐘 PostgreSQL" value="postgresql" />
                  <el-option label="🔶 Oracle" value="oracle" />
                </el-select>
              </div>
              <div class="config-item">
                <span class="config-label">词根匹配：</span>
                <el-select v-model="batchRootPriority" style="width: 150px" :disabled="batchGenerating">
                  <el-option label="🌟 优先全称" value="full" />
                  <el-option label="🔤 优先缩写" value="abbr" />
                </el-select>
              </div>
              <div class="config-item">
                <span class="config-label">分词模式：</span>
                <el-select v-model="batchCutMode" style="width: 180px" :disabled="batchGenerating">
                  <el-option label="🎯 精准模式" value="accurate" />
                  <el-option label="📊 全模式" value="full" />
                  <el-option label="🔍 搜索引擎模式" value="search" />
                </el-select>
              </div>
              <div class="config-item">
                <span class="config-label">最终校验：</span>
                <el-switch v-model="batchEnableValidation" :disabled="batchGenerating" active-text="开启" inactive-text="关闭" />
                <span class="config-hint">（关闭可提高生成速度）</span>
              </div>
              <div v-if="generationMode === 'excel'" class="config-item">
                <span class="config-label">并发线程：</span>
                <el-select v-model="batchMaxWorkers" style="width: 120px" :disabled="batchGenerating">
                  <el-option v-for="num in 10" :key="num" :label="num + ' 个'" :value="num" />
                </el-select>
                <span class="config-hint">（1-10个线程）</span>
              </div>
            </div>

            <div class="batch-action">
              <el-button 
                type="success" 
                size="large" 
                @click="startGenerate" 
                :loading="batchGenerating"
                :disabled="!llmConfig.apiKey || (generationMode === 'excel' ? !batchFile : !description.trim())"
                class="generate-btn"
              >
                <span v-if="!batchGenerating">✨</span>
                {{ batchGenerating ? '生成中...' : (generationMode === 'excel' ? '开始生成' : '开始解析并生成') }}
              </el-button>
              <el-button 
                v-if="batchGenerating"
                type="danger" 
                size="large" 
                @click="cancelBatchTask"
                class="cancel-btn"
              >
                ⛔ 终止任务
              </el-button>
            </div>

            <div v-if="batchGenerating || batchResult" class="batch-progress-section">
              <div class="progress-header">
                <span class="progress-title">📊 建表进度</span>
                <span class="progress-text">{{ batchProgress }}</span>
              </div>
              <el-progress 
                :percentage="batchProgressPercent" 
                :status="batchResult ? 'success' : 'active'"
                :show-text="false"
                stroke-width="8"
              />
              
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
              
              <div v-if="fieldProgressAvailable" class="field-progress-section">
                <div class="field-stats-title">🔎 字段生成进度</div>
                <div class="field-progress-line">
                  <span>{{ fieldProgress.phase_label || '字段生成中' }}</span>
                  <span v-if="fieldProgress.thread_count !== undefined">线程 {{ fieldProgress.thread_count }}</span>
                  <span v-if="fieldProgress.batch_count !== undefined">批次 {{ fieldProgress.completed_batches || 0 }}/{{ fieldProgress.batch_count || 0 }}</span>
                  <span v-if="fieldProgress.current_batch">当前第 {{ fieldProgress.current_batch }} 批</span>
                  <span v-if="fieldProgress.total_items !== undefined">
                    {{ fieldProgress.completed_items || 0 }}/{{ fieldProgress.total_items || 0 }} {{ fieldProgress.target_item_label || '项' }}
                  </span>
                </div>
                <el-progress
                  :percentage="fieldProgressPercent"
                  :show-text="true"
                  stroke-width="6"
                />
                <div v-if="fieldProgress.unique_root_count !== undefined" class="field-progress-hint">
                  去重后词根：{{ fieldProgress.unique_root_count }} 个
                  <span v-if="fieldProgress.raw_root_count !== undefined">，原始词根：{{ fieldProgress.raw_root_count }} 个</span>
                  <span v-if="fieldProgress.layer1_count !== undefined">
                    ，分层：Layer1 {{ fieldProgress.layer1_count }} / Layer2 {{ fieldProgress.layer2_count }} / Layer3 {{ fieldProgress.layer3_count }}
                  </span>
                </div>
              </div>

              <div v-if="fieldStatsAvailable" class="field-stats-section">
                <div class="field-stats-title">📈 字段匹配统计</div>
                <div class="field-stats-grid">
                  <div class="field-stat-item matched">
                    <div class="stat-value">{{ fieldStats.matched_count }}</div>
                    <div class="stat-label">历史词根匹配</div>
                  </div>
                  <div class="field-stat-item llm">
                    <div class="stat-value">{{ fieldStats.unmatched_count }}</div>
                    <div class="stat-label">需要 LLM 生成</div>
                  </div>
                  <div class="field-stat-item total">
                    <div class="stat-value">{{ fieldStats.total_fields }}</div>
                    <div class="stat-label">去重词根数</div>
                  </div>
                </div>
              </div>
            </div>
          </el-card>

          <el-card class="new-roots-card" shadow="hover">
            <div class="new-roots-header">
              <span class="new-roots-title">🌱 发现新词根</span>
              <el-tag type="warning" size="small">{{ batchNewRoots.length }} 个</el-tag>
              <el-button type="success" size="small" @click="saveBatchNewRoots" class="save-roots-btn" :disabled="batchNewRoots.length === 0">
                💾 保存到历史词根
              </el-button>
            </div>
            <div class="new-roots-list">
              <el-table v-if="batchNewRoots.length > 0" :data="batchNewRoots" size="small" max-height="600" stripe>
                <el-table-column prop="chinese_name" label="中文名" width="120" />
                <el-table-column prop="full_root" label="词根全称" width="150" />
                <el-table-column prop="abbr_root" label="缩写" width="100" />
                <el-table-column prop="recommended_type" label="推荐类型" width="120" />
                <el-table-column prop="business_domain" label="业务域" />
              </el-table>
              <el-empty v-else description="暂无新词根，生成 DDL 后将自动显示" />
            </div>
          </el-card>
          </div>
          <el-card v-if="batchResult" class="result-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">🎯 生成结果</span>
                <div class="header-actions">
                  <el-button type="primary" plain size="small" @click="copyBatchDDL">
                    复制全部SQL
                  </el-button>
                  <el-button type="success" plain size="small" @click="downloadBatchDDL">
                    下载SQL文件
                  </el-button>
                </div>
              </div>
            </template>
            
            <div class="batch-result-stats">
              <el-tag type="success" size="small">成功: {{ batchResult.success_count }}</el-tag>
              <el-tag v-if="batchResult.error_count > 0" type="danger" size="small">失败: {{ batchResult.error_count }}</el-tag>
              <el-tag type="info" size="small">⏱️ 耗时: {{ batchResult.elapsed_time_str || '--' }}</el-tag>
            </div>

            <div v-if="batchResult.errors && batchResult.errors.length > 0" class="batch-errors">
              <div class="error-title">⚠️ 错误信息：</div>
              <div v-for="(error, index) in batchResult.errors" :key="index" class="error-item">
                {{ error }}
              </div>
            </div>

            <div v-if="batchResult.validation_info" class="validation-section">
              <div class="validation-stats">
                <el-tag type="danger" size="small">错误: {{ batchResult.validation_info.error_count }}</el-tag>
                <el-tag type="warning" size="small">警告: {{ batchResult.validation_info.warning_count }}</el-tag>
                <el-tag v-if="batchResult.validation_info.corrected" type="success" size="small">✅ 已自动修正</el-tag>
              </div>
              
              <div v-if="batchResult.validation_info.violations && batchResult.validation_info.violations.length > 0" class="violations-section">
                <div class="section-header">
                  <span>📋 违规详情</span>
                  <el-button type="text" size="small" @click="showViolations = !showViolations">
                    {{ showViolations ? '收起' : '展开' }}
                  </el-button>
                </div>
                <div v-if="showViolations" class="violations-list">
                  <div v-for="(violation, index) in batchResult.validation_info.violations" :key="index" 
                       class="violation-item" :class="violation.level === 'error' ? 'error' : 'warning'">
                    <span class="violation-level">{{ violation.level === 'error' ? '❌' : '⚠️' }}</span>
                    <span class="violation-message">{{ violation.message }}</span>
                  </div>
                  <div v-if="batchResult.validation_info.total_violations > batchResult.validation_info.violations.length" 
                       class="violations-more">
                    还有 {{ batchResult.validation_info.total_violations - batchResult.validation_info.violations.length }} 条违规未显示
                  </div>
                </div>
              </div>

            </div>

            <div class="sql-container">
              <pre class="sql-output" v-html="highlightSQL(batchResult.full_ddl)"></pre>
            </div>
          </el-card>
        </div>

        <div v-show="activeMenu === 'history'" class="history-view">
          <el-card class="config-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">📜 建表历史记录</span>
                <div class="header-actions">
                  <el-button type="info" plain size="small" @click="loadHistory">
                    🔄 刷新
                  </el-button>
                  <el-button type="danger" plain size="small" @click="clearAllHistory" v-if="historyList.length > 0">
                    🗑️ 清空全部
                  </el-button>
                </div>
              </div>
            </template>
            
            <div v-if="historyLoading" class="loading-container">
              <el-loading text="加载中..." />
            </div>
            
            <div v-else-if="historyList.length === 0" class="empty-history">
              <el-empty description="暂无建表记录" />
            </div>
            
            <div v-else class="history-list">
              <el-table :data="historyList" size="small" stripe height="100%">
                <el-table-column prop="id" label="ID" width="80" />
                <el-table-column prop="type" label="类型" width="80">
                  <template #default="scope">
                    <el-tag :type="scope.row.type === 'batch' ? 'success' : 'primary'">
                      {{ scope.row.type === 'batch' ? '批量' : '单一' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="description" label="描述" />
                <el-table-column prop="tables_count" label="表数量" width="80" />
                <el-table-column prop="success_count" label="成功数" width="80" />
                <el-table-column prop="db_type" label="数据库类型" width="120">
                  <template #default="scope">
                    <el-tag :type="scope.row.db_type ? 'info' : ''">
                      {{ formatDbType(scope.row.db_type) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="root_match_priority" label="词根匹配" width="100">
                  <template #default="scope">
                    <el-tag :type="scope.row.root_match_priority ? 'warning' : ''">
                      {{ formatRootPriority(scope.row.root_match_priority) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="timestamp" label="时间" width="180">
                  <template #default="scope">
                    {{ formatTimestamp(scope.row.timestamp) }}
                  </template>
                </el-table-column>
                <el-table-column label="建表记录" width="220">
                  <template #default="scope">
                    <div v-if="scope.row.execute_status" class="execute-record-cell">
                      <el-tag :type="scope.row.execute_status === 'success' ? 'success' : 'danger'" size="small">
                        {{ scope.row.execute_status === 'success' ? '已建表' : '执行失败' }}
                      </el-tag>
                      <span class="execute-record-text">{{ scope.row.connection_name || '-' }}</span>
                    </div>
                    <span v-else class="execute-record-empty">未执行</span>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="200">
                  <template #default="scope">
                    <el-button size="small" @click="viewHistoryDDL(scope.row)">查看</el-button>
                    <el-button size="small" type="success" @click="downloadHistoryDDL(scope.row.id)">下载</el-button>
                    <el-button size="small" type="danger" @click="deleteHistoryRecord(scope.row.id)">删除</el-button>
                  </template>
                </el-table-column>
                <el-table-column label="一键建表" width="120" fixed="right">
                  <template #default="scope">
                    <el-button size="small" type="primary" @click="showExecuteDialog(scope.row)">建表</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </div>
              <div v-show="activeMenu === 'governance'" class="governance-view">
          <el-card class="config-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">📝 词根输入</span>
                <div class="header-actions">
                  <el-button type="primary" plain size="small" @click="previewWordRootsInput">
                    解析预览
                  </el-button>
                  <el-button type="success" size="small" @click="saveWordRoots">
                    保存到标准词根
                  </el-button>
                </div>
              </div>
            </template>
            <el-tabs v-model="wordRootsTab" class="custom-tabs">
              <el-tab-pane label="粘贴文本" name="text">
                <el-input
                  v-model="wordRootsText"
                  type="textarea"
                  :rows="6"
                  placeholder="每行格式：业务域:域编码:中文名称:全称词根:缩写词根:推荐类型
示例：订单:ord:订单:order:ord:VARCHAR(64)
仅中文名称必填，其他字段允许为空"
                />
              </el-tab-pane>
              <el-tab-pane label="上传文件" name="file">
                <div class="upload-section">
                  <el-upload
                    ref="wordRootsUpload"
                    :auto-upload="false"
                    :on-change="handleWordRootsFileChange"
                    :limit="1"
                    accept=".xlsx,.csv,.txt"
                  >
                    <el-button type="primary" plain>
                      <span>📁</span> 选择文件
                    </el-button>
                  </el-upload>
                  <el-button type="success" @click="downloadTemplate">
                    <span>📥</span> 下载模板
                  </el-button>
                </div>
                <div v-if="wordRootsFileName" class="file-info">
                  <el-tag effect="dark">{{ wordRootsFileName }}</el-tag>
                  <el-button type="primary" size="small" @click="previewWordRootsInput">解析预览</el-button>
                  <el-button type="danger" plain size="small" @click="clearWordRootsFile">清除</el-button>
                </div>
              </el-tab-pane>
            </el-tabs>
            <div v-if="parsedWordRoots.length > 0" class="preview-table">
              <div class="preview-title">预览 ({{ parsedWordRoots.length }} 条)</div>
              <el-table :data="parsedWordRoots" size="small" max-height="220" stripe>
                <el-table-column prop="business_domain" label="业务域" width="120" />
                <el-table-column prop="domain_code" label="域编码" width="90" />
                <el-table-column prop="chinese_name" label="中文名称" width="140" />
                <el-table-column prop="full_root" label="全称词根" width="160" />
                <el-table-column prop="abbr_root" label="缩写词根" width="120" />
                <el-table-column prop="recommended_type" label="推荐类型" min-width="140" />
              </el-table>
            </div>
          </el-card>

          <el-card class="config-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">标准词根治理</span>
                <div class="header-actions">
                  <el-button type="primary" size="small" :loading="governanceRunning" @click="runGovernance">
                    发起治理
                  </el-button>
                  <el-button
                    type="success"
                    size="small"
                    :disabled="governanceCandidates.length === 0"
                    @click="applyGovernance"
                  >
                    应用结果
                  </el-button>
                  <el-button type="primary" plain size="small" @click="loadGovernanceData">刷新</el-button>
                </div>
              </div>
            </template>
            <div v-if="governanceProgressVisible" class="governance-progress-card">
              <div class="governance-progress-header">
                <span class="governance-panel-title">治理进度</span>
                <el-tag :type="governanceRunning ? 'warning' : 'success'">
                  {{ governanceStatusText || '未开始' }}
                </el-tag>
              </div>
              <div class="governance-progress-meta">
                <span>原始词根：{{ governanceStats.rawCount }}</span>
                <span>整理后：{{ governanceStats.preparedCount }}</span>
                <span>剔除标准：{{ governanceStats.excludedStandardCount }}</span>
                <span>待治理：{{ governanceStats.filteredCount }}</span>
                <span>候选结果：{{ governanceStats.candidateCount }}</span>
                <span>已耗时：{{ governanceElapsedText }}</span>
              </div>
              <div class="governance-progress-meta" v-if="governanceStats.chunkCount > 0">
                <span>总批次：{{ governanceStats.chunkCount }}</span>
                <span>并发线程：{{ governanceStats.actualWorkers || governanceStats.requestedWorkers }}</span>
                <span>已完成：{{ governanceStats.completedChunks }}/{{ governanceStats.chunkCount }}</span>
                <span v-if="governanceStats.activeChunksText">处理中：{{ governanceStats.activeChunksText }}</span>
              </div>
              <div class="governance-progress-detail">
                {{ governanceDetailText }}
              </div>
              <el-steps :active="governanceActiveStep" finish-status="success" simple>
                <el-step title="加载历史词根" />
                <el-step title="清洗去重" />
                <el-step title="构建治理提示词" />
                <el-step title="发送模型请求" />
                <el-step title="等待模型响应" />
                <el-step title="解析返回结果" />
                <el-step title="生成候选词根" />
              </el-steps>
              <el-progress
                :percentage="governanceProgressPercent"
                :status="governanceRunning ? '' : 'success'"
                style="margin-top: 12px;"
              />
            </div>
            <div class="gov-stats" style="margin-bottom: 12px">
              <el-tag type="success">标准词根: {{ standardRoots.length }} 条</el-tag>
              <el-tag type="info" style="margin-left: 10px">治理来源: {{ historicalRoots.length }} 条</el-tag>
            </div>
            <div class="governance-panels">
              <div class="governance-panel">
                <div class="governance-panel-title">历史词根</div>
                <div class="header-actions governance-toolbar">
                  <el-input
                    v-model="rootSearchQuery"
                    placeholder="搜索词根（中文或英文）"
                    size="small"
                    clearable
                    class="governance-search"
                  />
                  <el-button type="primary" plain size="small" @click="saveHistoricalRoots" :disabled="historicalRoots.length === 0">
                    保存
                  </el-button>
                  <el-button type="info" plain size="small" @click="loadGovernanceData">刷新</el-button>
                  <el-button type="warning" plain size="small" @click="showAddRootDialog">手动添加</el-button>
                  <el-button type="danger" plain size="small" @click="clearHistoricalRoots" :disabled="historicalRoots.length === 0">
                    清除全部
                  </el-button>
                </div>
                <el-table v-if="filteredHistoricalRoots.length > 0" :data="filteredHistoricalRoots" size="small" max-height="320" stripe>
                  <el-table-column prop="business_domain" label="业务域" width="120" />
                  <el-table-column prop="domain_code" label="域编码" width="90" />
                  <el-table-column prop="chinese_name" label="中文名称" width="140" />
                  <el-table-column prop="full_root" label="全称词根" width="150" />
                  <el-table-column prop="abbr_root" label="缩写词根" width="120" />
                  <el-table-column prop="recommended_type" label="推荐类型" min-width="120" />
                  <el-table-column label="操作" width="100">
                    <template #default="{ row }">
                      <el-button type="primary" link size="small" @click="editHistoricalRoot(row)">编辑</el-button>
                      <el-button type="danger" link size="small" @click="removeHistoricalRoot(row)">删除</el-button>
                    </template>
                  </el-table-column>
                </el-table>
                <el-empty v-else description="暂无历史词根，生成DDL后会自动记录" />
              </div>
              <div class="governance-panel">
                <div class="governance-panel-title">治理结果</div>
                <el-empty
                  v-if="governanceCandidates.length === 0"
                  description="点击“发起治理”后，这里会展示待应用的标准词根候选"
                />
                <el-table v-else :data="governanceCandidates" size="small" max-height="320" stripe>
                  <el-table-column prop="business_domain" label="业务域" width="100" />
                  <el-table-column prop="domain_code" label="域编码" width="80" />
                  <el-table-column prop="chinese_name" label="中文名称" width="120" />
                  <el-table-column prop="full_root" label="全称词根" width="150" />
                  <el-table-column prop="abbr_root" label="缩写词根" width="100" />
                  <el-table-column prop="recommended_type" label="推荐类型" width="120" />
                  <el-table-column prop="governance_status" label="治理状态" width="100" />
                </el-table>
              </div>
            </div>
            <div class="governance-panel-title" style="margin-top: 16px;">当前标准词根</div>
            <div class="header-actions governance-toolbar" style="margin-bottom: 12px;">
              <el-input
                v-model="standardRootSearchQuery"
                placeholder="搜索标准词根（中文或英文）"
                size="small"
                clearable
                class="governance-search"
              />
              <el-button type="info" plain size="small" @click="loadGovernanceData">刷新</el-button>
              <el-button type="warning" plain size="small" @click="showAddRootDialog('standard')">手动添加</el-button>
              <el-upload
                ref="standardRootsUpload"
                :auto-upload="false"
                :show-file-list="false"
                :on-change="handleStandardRootsImportFileChange"
                :limit="1"
                accept=".xlsx,.csv,.txt"
              >
                <el-button type="primary" plain size="small">Excel导入</el-button>
              </el-upload>
              <el-button type="success" plain size="small" @click="exportStandardRootsToExcel" :disabled="standardRoots.length === 0">导出Excel</el-button>
            </div>
            <el-table :data="filteredStandardRoots" size="small" max-height="320" stripe>
              <el-table-column prop="business_domain" label="业务域" width="100" />
              <el-table-column prop="domain_code" label="域编码" width="80" />
              <el-table-column prop="chinese_name" label="中文名称" width="120" />
              <el-table-column prop="full_root" label="全称词根" width="150" />
              <el-table-column prop="abbr_root" label="缩写词根" width="100" />
              <el-table-column prop="recommended_type" label="推荐类型" width="120" />
              <el-table-column prop="updated_at" label="最近修改" width="170" />
              <el-table-column label="操作" width="160">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="editStandardRoot(row)">编辑</el-button>
                  <el-button type="danger" link size="small" @click="removeStandardRoot(row)">删除</el-button>
                  <el-button type="info" link size="small" @click="showStandardRootHistory(row)">记录</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
</main>

      <footer class="footer">
        © 2025 数仓建表助手 - AI 驱动的智能 DDL 生成工具
      </footer>
    </div>

    <el-dialog v-model="historyViewDialog" :title="currentHistoryTitle" width="800px">
      <div class="sql-container-header">
        <el-button type="success" size="small" @click="copyAllDDL">📋 复制全部</el-button>
        <el-button
          type="primary"
          size="small"
          @click="showExecuteDialog(currentHistoryRecord)"
          :disabled="!currentHistoryRecord"
        >
          建表
        </el-button>
      </div>
      <div v-if="currentHistoryRecord?.execute_status" class="history-execute-summary">
        <el-tag :type="currentHistoryRecord.execute_status === 'success' ? 'success' : 'danger'" size="small">
          {{ currentHistoryRecord.execute_status === 'success' ? '已建表' : '执行失败' }}
        </el-tag>
        <span>连接：{{ currentHistoryRecord.connection_name || '-' }}</span>
        <span>时间：{{ formatTimestamp(currentHistoryRecord.execute_time) }}</span>
        <span v-if="currentHistoryRecord.executed_count">语句：{{ currentHistoryRecord.executed_count }} 条</span>
        <span v-if="currentHistoryRecord.execute_message">结果：{{ currentHistoryRecord.execute_message }}</span>
      </div>
      <div class="sql-container">
        <pre class="sql-output" v-html="highlightSQL(currentHistoryDDL)"></pre>
      </div>
      <template #footer>
        <el-button @click="historyViewDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="saveDialogVisible" title="💾 保存配置" width="450px">
      <el-form :model="saveForm" label-width="100px">
        <el-form-item label="配置名称">
          <el-input v-model="saveForm.name" placeholder="请输入配置名称" size="large" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="saveForm.isDefault" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveConfig">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="dbConnectionDialogVisible" title="数据库连接配置" width="720px">
      <el-form :model="dbConnectionForm" label-width="120px">
        <el-form-item label="连接名称">
          <el-input v-model="dbConnectionForm.name" placeholder="请输入连接名称" />
        </el-form-item>
        <el-form-item label="数据库类型">
          <el-select v-model="dbConnectionForm.db_type" style="width: 220px">
            <el-option label="MySQL" value="mysql" />
            <el-option label="PostgreSQL" value="postgresql" />
            <el-option label="Oracle" value="oracle" />
          </el-select>
        </el-form-item>
        <el-form-item label="主机">
          <el-input v-model="dbConnectionForm.host" placeholder="数据库服务器地址" />
        </el-form-item>
        <el-form-item label="端口">
          <el-input-number v-model="dbConnectionForm.port" :min="1" :max="65535" controls-position="right" />
        </el-form-item>
        <el-form-item label="数据库/服务名">
          <el-input v-model="dbConnectionForm.database" placeholder="MySQL/PG数据库名，Oracle服务名" />
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="dbConnectionForm.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="dbConnectionForm.password" type="password" show-password placeholder="编辑时留空表示不修改" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dbConnectionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveDbConnection">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="executeDialogVisible" title="历史SQL一键建表" width="620px">
      <el-form label-width="120px">
        <el-form-item label="脚本类型">
          <el-tag>{{ formatDbType(executeRecord?.db_type) }}</el-tag>
        </el-form-item>
        <el-form-item label="建表语句数">
          <span>{{ executeStatementCount }}</span>
        </el-form-item>
        <el-form-item label="目标连接">
          <el-select v-model="selectedExecuteConnectionId" placeholder="请选择数据库连接" style="width: 360px">
            <el-option
              v-for="conn in matchedExecuteConnections"
              :key="conn.id"
              :label="`${conn.name} (${formatDbType(conn.db_type)})`"
              :value="conn.id"
            />
          </el-select>
        </el-form-item>
        <el-alert
          v-if="matchedExecuteConnections.length === 0"
          title="没有匹配的数据库连接，请先到基础配置添加同类型连接。"
          type="warning"
          show-icon
          :closable="false"
        />
      </el-form>
      <template #footer>
        <el-button @click="executeDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="executingHistoryDDL"
          :disabled="!selectedExecuteConnectionId"
          @click="executeHistoryDDL"
        >
          确认建表
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editRootDialogVisible" title="编辑词根" width="500px">
      <el-form :model="editingRoot" label-width="100px">
        <el-form-item label="业务域">
          <el-input v-model="editingRoot.business_domain" />
        </el-form-item>
        <el-form-item label="域编码">
          <el-input v-model="editingRoot.domain_code" />
        </el-form-item>
        <el-form-item label="中文名称">
          <el-input v-model="editingRoot.chinese_name" />
        </el-form-item>
        <el-form-item label="词根全称">
          <el-input v-model="editingRoot.full_root" />
        </el-form-item>
        <el-form-item label="缩写词根">
          <el-input v-model="editingRoot.abbr_root" />
        </el-form-item>
        <el-form-item label="推荐类型">
          <el-input v-model="editingRoot.recommended_type" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editRootDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveHistoricalRootEdit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="standardRootEditDialogVisible" title="编辑标准词根" width="520px">
      <el-form :model="editingStandardRoot" label-width="100px">
        <el-form-item label="业务域">
          <el-input v-model="editingStandardRoot.business_domain" />
        </el-form-item>
        <el-form-item label="域编码">
          <el-input v-model="editingStandardRoot.domain_code" />
        </el-form-item>
        <el-form-item label="中文名称">
          <el-input v-model="editingStandardRoot.chinese_name" />
        </el-form-item>
        <el-form-item label="词根全称">
          <el-input v-model="editingStandardRoot.full_root" />
        </el-form-item>
        <el-form-item label="缩写词根">
          <el-input v-model="editingStandardRoot.abbr_root" />
        </el-form-item>
        <el-form-item label="推荐类型">
          <el-input v-model="editingStandardRoot.recommended_type" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="standardRootEditDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveStandardRootEdit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="standardRootHistoryDialogVisible" :title="currentStandardRootTitle" width="760px">
      <el-table :data="currentStandardRootHistory" size="small" max-height="420" stripe>
        <el-table-column prop="edited_at" label="修改时间" width="180" />
        <el-table-column prop="action" label="动作" width="90" />
        <el-table-column label="修改前" min-width="220">
          <template #default="{ row }">
            <div>{{ formatRootSnapshot(row.before) }}</div>
          </template>
        </el-table-column>
        <el-table-column label="修改后" min-width="220">
          <template #default="{ row }">
            <div>{{ formatRootSnapshot(row.after) }}</div>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="standardRootHistoryDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="addRootDialogVisible" title="➕ 添加词根" width="500px">
      <el-form :model="addRootForm" label-width="100px">
        <el-form-item label="业务域">
          <el-input v-model="addRootForm.businessDomain" placeholder="如：订单" size="large" />
        </el-form-item>
        <el-form-item label="域编码">
          <el-input v-model="addRootForm.domainCode" placeholder="如：ord" size="large" />
        </el-form-item>
        <el-form-item label="中文名称">
          <el-input v-model="addRootForm.chineseName" placeholder="如：订单号" size="large" />
        </el-form-item>
        <el-form-item label="词根全称">
          <el-input v-model="addRootForm.fullRoot" placeholder="如：order_no" size="large" />
        </el-form-item>
        <el-form-item label="缩写词根">
          <el-input v-model="addRootForm.abbrRoot" placeholder="如：ord_no" size="large" />
        </el-form-item>
        <el-form-item label="推荐类型">
          <el-input v-model="addRootForm.recommendedType" placeholder="如：VARCHAR(64)" size="large" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addRootDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addRoot">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, watch, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import * as XLSX from 'xlsx'

const md5 = (str) => {
  const crypto = window.crypto || window.msCrypto
  const toUtf8 = (str) => {
    return decodeURIComponent(encodeURIComponent(str.replace(/-/g, '+').replace(/_/g, '/')))
  }
  const rotateLeft = (lVal, iShift) => (lVal << iShift) | (lVal >>> (32 - iShift))
  const ff = (n, c, d, e, f, g, h) => {
    n = (n + (c & d | ~c & e) + f + h) >>> 0
    return (rotateLeft(n, g) + e) >>> 0
  }
  const gg = (n, c, d, e, f, g, h) => {
    n = (n + (c & d | ~c & e) + f + h) >>> 0
    return (rotateLeft(n, g) + e) >>> 0
  }
  const hh = (n, c, d, e, f, g, h) => {
    n = (n + (c ^ d ^ e) + f + h) >>> 0
    return (rotateLeft(n, g) + e) >>> 0
  }
  const ii = (n, c, d, e, f, g, h) => {
    n = (n + (d ^ (c | ~e)) + f + h) >>> 0
    return (rotateLeft(n, g) + e) >>> 0
  }
  const x = toUtf8(str)
  const k = x.length
  const a = 1732584193, b = -271733879, c = -1732584194, d = 271733878
  for (let i = 0; i < k; i += 64) {
    let p = a, q = b, r = c, s = d
    const u = x.substring(i, i + 64)
    const j = [0, 7, 1, 12, 2, 17, 3, 22, 4, 7, 5, 12, 6, 17, 7, 22, 8, 7, 9, 12, 10, 17, 11, 22, 12, 7, 13, 12, 14, 17, 15, 22, 4, 9, 1, 20, 5, 9, 13, 14, 8, 20, 12, 15, 2, 4, 14, 18, 0, 1, 6, 10, 2, 15, 14, 3, 6, 9, 11, 2, 15, 8, 12, 4, 13, 13, 15, 0, 5, 9, 7, 4, 11, 10, 15, 2, 5, 8, 14, 12, 0, 1, 6, 10, 3, 8, 14, 2, 11, 4, 13, 9, 0, 5, 12, 1, 2, 4, 14, 3, 7, 10, 12, 6, 0, 9, 3, 15, 5, 0, 12, 8, 5, 2, 0, 13, 5, 3, 6, 11, 11, 2, 14, 1, 7, 5, 10, 4, 8, 13, 14, 6, 15, 13, 12, 11, 2, 8, 1, 3, 10, 0, 6, 10, 13, 0, 3, 7, 11, 5, 9, 0, 4, 2, 1, 11, 8, 6, 13, 4, 9, 1, 7, 5, 12, 3, 10, 7, 9, 15, 14, 1, 0, 12, 11, 7, 3, 9, 12, 2, 13, 2, 15, 8, 1, 3, 8, 9, 11, 7, 7, 4, 9, 10, 12, 1, 4, 5, 2, 3, 12, 5, 2, 9, 8, 10, 3, 15, 2, 0, 0, 4, 14, 3, 9, 11, 6, 4, 15, 3, 8, 13, 1, 3, 8, 1, 11, 7, 1, 14, 4, 11, 13, 12, 6, 0, 9, 4, 0, 3, 5, 5, 3, 2, 0, 2, 4, 13, 5, 3, 2, 12, 0, 2, 0, 4, 14, 2, 0, 1, 2, 4, 14, 3, 8, 13, 1, 3, 8, 1, 11, 7, 1, 14, 4, 11, 13, 12, 6, 0, 9, 4, 0, 3, 5, 5, 3, 2, 0, 2, 4, 13, 5, 3, 2, 12, 0, 2, 0, 4, 14, 2, 0, 1, 2, 4, 14, 3, 8, 13, 1, 3, 8, 1, 11, 7, 1, 14, 4, 11, 13, 12, 6, 0, 9, 4, 0, 3, 5, 5, 3, 2, 0, 2, 4, 13, 5, 3, 2, 12, 0, 2, 0, 4, 14, 2, 0, 1, 2, 4, 14, 3, 8, 13, 1, 3, 8, 1, 11, 7, 1, 14, 4, 11, 13, 12, 6, 0, 9, 4, 0, 3, 5, 5, 3, 2, 0, 2, 4, 13, 5, 3, 2, 12, 0, 2, 0, 4, 14, 2, 0, 1, 2, 4, 14, 3, 8, 13, 1, 3, 8, 1, 11, 7, 1, 14, 4, 11, 13, 12, 6, 0, 9, 4, 0, 3, 5, 5, 3, 2, 0, 2, 4, 13, 5, 3, 2, 12, 0, 2, 0, 4, 14]
    for (let j = 0; j < 64; j++) {
      const m = j < 16 ? u.charCodeAt(j) || 0 : u.charCodeAt(j - 3) || u.charCodeAt(j - 8) || u.charCodeAt(j - 14) || 0
      const s = j / 16 | 0, t = j % 16
      let v = m << t | m >>> (32 - t)
      if (j < 16) {
        p = ff(p, q, r, s, a, b, c, d, e, f, g, h, v, j)
        q = ff(q, r, s, t, a, b, c, d, e, f, g, h, v, j + 1)
        r = ff(r, s, t, t, a, b, c, d, e, f, g, h, v, j + 2)
        s = ff(s, t, t, t, a, b, c, d, e, f, g, h, v, j + 3)
      } else if (j < 32) {
        p = gg(p, q, r, s, a, b, c, d, e, f, g, h, v, j)
        q = gg(q, r, s, t, a, b, c, d, e, f, g, h, v, j + 1)
        r = gg(r, s, t, t, a, b, c, d, e, f, g, h, v, j + 2)
        s = gg(s, t, t, t, a, b, c, d, e, f, g, h, v, j + 3)
      } else if (j < 48) {
        p = hh(p, q, r, s, a, b, c, d, e, f, g, h, v, j)
        q = hh(q, r, s, t, a, b, c, d, e, f, g, h, v, j + 1)
        r = hh(r, s, t, t, a, b, c, d, e, f, g, h, v, j + 2)
        s = hh(s, t, t, t, a, b, c, d, e, f, g, h, v, j + 3)
      } else {
        p = ii(p, q, r, s, a, b, c, d, e, f, g, h, v, j)
        q = ii(q, r, s, t, a, b, c, d, e, f, g, h, v, j + 1)
        r = ii(r, s, t, t, a, b, c, d, e, f, g, h, v, j + 2)
        s = ii(s, t, t, t, a, b, c, d, e, f, g, h, v, j + 3)
      }
      [p, q, r, s] = [q, r, s, p]
    }
    [a, b, c, d] = [(a + p) >>> 0, (b + q) >>> 0, (c + r) >>> 0, (d + s) >>> 0]
  }
  const final = a ^ b ^ c ^ d
  return (final >>> 0).toString(16).padStart(8, '0') +
    (b >>> 0).toString(16).padStart(8, '0') +
    (c >>> 0).toString(16).padStart(8, '0') +
    (d >>> 0).toString(16).padStart(8, '0')
}

const encodeKey = (str) => btoa(encodeURIComponent(str))
const decodeKey = (str) => {
  try {
    return decodeURIComponent(atob(str))
  } catch {
    return ''
  }
}

const DEFAULT_PROMPT = `你是一位专业的数据仓库DDL生成专家。请严格遵守当前词根模式，不要把全称和缩写混用。

【当前词根模式强制约束】
{root_constraints}
{root_reuse_principle}

【基础词根约定】
【地址、位置、住址】→ 必须是 address
【创建、新增、新建时间】→ 必须是 create + time
【修改、更新、编辑时间】→ 必须是 update + time
【描述、说明、备注】→ 必须是 desc 或 description
【版本、版次】→ 必须是 version
【路径、文件路径】→ 必须是 path
【用户、操作人员】→ 必须是 user
【密码、密钥】→ 必须是 password
【邮箱、电子邮箱】→ 必须是 email
【电话、手机号】→ 必须是 phone
【价格、单价】→ 必须是 price
【开始、起始日期】→ 必须是 start + date
【结束、截止日期】→ 必须是 end + date
【备注、注释】→ 必须是 remark
【链接、网址】→ 必须是 url
【大小、文件大小】→ 必须是 size
【创建人、创建者】→ 必须是 creator
【修改人、更新人】→ 必须是 updater
【分类、类别分组】→ 必须是 category
【标签、标记】→ 必须是 tag
【费用、金额、成本、花费】→ 必须是amount或amt

要求：
1. 字段名和表名主体必须符合【当前词根模式强制约束】。
2. 只输出 CREATE TABLE 和 COMMENT 语句，不要解释。
3. 如发现新词根，在 SQL 结束后按【新词根】词根全称:词根缩写:中文名称:推荐字段类型 输出。
`

const activeMenu = ref('config')
const selectedConfig = ref('')
const savedConfigs = ref([])
const llmConfig = reactive({
  apiKey: '',
  apiUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  model: 'qwen3.5-122b-a10b',
  temperature: 0.3,
  abbrMaxLen: 4,
  industryContext: ''
})
const testing = ref(false)
const apiKeySaved = ref(false)

const wordRootsTab = ref('text')
const wordRootsText = ref('')
const wordRootsFileName = ref('')
const parsedWordRoots = ref([])
const wordRootsUpload = ref(null)
const wordRootsFile = ref(null)
const standardRootsUpload = ref(null)

const standardsTab = ref('text')
const standardsText = ref('')

const standardsViewTab = ref('edit')
const standardsContent = ref('')
const standardsList = ref([])
const currentStandardId = ref('')

const batchUpload = ref(null)
const batchFile = ref(null)
const batchFileName = ref('')
const generationMode = ref('text')
const batchDbType = ref('mysql')
const batchRootPriority = ref('abbr')
const batchCutMode = ref('accurate')
const batchEnableValidation = ref(true)
const batchMaxWorkers = ref(5)
const batchGenerating = ref(false)
const batchProgress = ref('')
const batchProgressPercent = ref(0)
const batchResult = ref(null)
const batchNewRoots = ref([])
const parsedBatchTables = ref([])
const currentTaskId = ref('')
const realProgress = ref(null)
const showViolations = ref(false)
const fieldStats = ref(null)
const fieldProgress = ref(null)
const fieldStatsAvailable = computed(() => {
  return fieldStats.value !== null
})
const fieldProgressAvailable = computed(() => {
  return fieldProgress.value !== null
})
const fieldProgressPercent = computed(() => {
  if (!fieldProgress.value || !fieldProgress.value.total_items) return 0
  return Math.min(100, Math.round(((fieldProgress.value.completed_items || 0) / fieldProgress.value.total_items) * 100))
})
let progressPollingInterval = null
let fallbackProgressInterval = null
let governanceProgressInterval = null
let governanceServerProgressInterval = null

const historyList = ref([])
const historyLoading = ref(false)
const historyViewDialog = ref(false)
const currentHistoryDDL = ref('')
const currentHistoryTitle = ref('')
const currentHistoryRecord = ref(null)

const customPrompt = ref('')
const rootMatchPriority = ref('abbr')
const dbType = ref('mysql')
const enableValidation = ref(true)
const description = ref('')
const generatedSQL = ref('')
const generating = ref(false)
const generateStartTime = ref(0)
const generateDuration = ref(0)
const currentDuration = ref(0)
let timerInterval = null

const singleNewRoots = ref([])

const standardRoots = ref([])
const historicalRoots = ref([])
const governanceCandidates = ref([])
const governanceRunning = ref(false)
const governanceTaskId = ref('')
const governanceActiveStep = ref(0)
const governanceStatusText = ref('')
const governanceDetailText = ref('')
const governanceStartedAt = ref(0)
const governanceElapsedMs = ref(0)
const governanceStats = reactive({
  rawCount: 0,
  preparedCount: 0,
  filteredCount: 0,
  excludedStandardCount: 0,
  standardRootCount: 0,
  candidateCount: 0,
  promptLength: 0,
  llmElapsedMs: 0,
  chunkCount: 0,
  requestedWorkers: 0,
  actualWorkers: 0,
  completedChunks: 0,
  currentChunk: 0,
  activeChunksText: ''
})
const rootSearchQuery = ref('')
const standardRootSearchQuery = ref('')
const editRootDialogVisible = ref(false)
const editHistoricalRootIndex = ref(-1)
const standardRootEditDialogVisible = ref(false)
const standardRootHistoryDialogVisible = ref(false)
const editingStandardRootId = ref('')
const currentStandardRootTitle = ref('')
const currentStandardRootHistory = ref([])
const editingRoot = reactive({
  business_domain: '',
  domain_code: '',
  chinese_name: '',
  full_root: '',
  abbr_root: '',
  recommended_type: ''
})
const editingStandardRoot = reactive({
  root_id: '',
  business_domain: '',
  domain_code: '',
  chinese_name: '',
  full_root: '',
  abbr_root: '',
  recommended_type: '',
  updated_at: '',
  change_history: []
})
const governanceProgressVisible = computed(() => governanceRunning.value || governanceStatusText.value || governanceCandidates.value.length > 0)
const governanceProgressPercent = computed(() => Math.round(((governanceActiveStep.value + 1) / 7) * 100))
const governanceElapsedText = computed(() => formatDuration(governanceElapsedMs.value))

const filteredHistoricalRoots = computed(() => {
  if (!rootSearchQuery.value) return historicalRoots.value
  const query = rootSearchQuery.value.toLowerCase()
  return historicalRoots.value.filter(r => 
    r.chinese_name?.toLowerCase().includes(query) || 
    r.full_root?.toLowerCase().includes(query) ||
    r.abbr_root?.toLowerCase().includes(query)
  )
})

const filteredStandardRoots = computed(() => {
  if (!standardRootSearchQuery.value) return standardRoots.value
  const query = standardRootSearchQuery.value.toLowerCase()
  return standardRoots.value.filter(r =>
    r.chinese_name?.toLowerCase().includes(query) ||
    r.full_root?.toLowerCase().includes(query) ||
    r.abbr_root?.toLowerCase().includes(query)
  )
})

const saveDialogVisible = ref(false)
const saveForm = reactive({ name: '', isDefault: false })

const dbConnections = ref([])
const testingDbConnectionId = ref('')
const dbConnectionDialogVisible = ref(false)
const editingDbConnectionId = ref('')
const dbConnectionForm = reactive({
  name: '',
  db_type: 'mysql',
  host: '',
  port: 3306,
  database: '',
  username: '',
  password: ''
})

const executeDialogVisible = ref(false)
const executeRecord = ref(null)
const selectedExecuteConnectionId = ref('')
const executingHistoryDDL = ref(false)
const matchedExecuteConnections = computed(() => {
  if (!executeRecord.value) return []
  return dbConnections.value.filter(conn => conn.db_type === executeRecord.value.db_type)
})
const executeStatementCount = computed(() => {
  const ddl = executeRecord.value?.ddl || ''
  return (ddl.match(/\bCREATE\s+TABLE\b/gi) || []).length
})

const addRootDialogVisible = ref(false)
const addRootTarget = ref('historical')
const addRootForm = reactive({
  businessDomain: '',
  domainCode: '',
  chineseName: '',
  fullRoot: '',
  abbrRoot: '',
  recommendedType: ''
})

const formatDuration = (ms) => {
  if (ms < 1000) {
    return `${ms}ms`
  } else if (ms < 60000) {
    return `${(ms / 1000).toFixed(2)}秒`
  } else {
    const minutes = Math.floor(ms / 60000)
    const seconds = ((ms % 60000) / 1000).toFixed(2)
    return `${minutes}分${seconds}秒`
  }
}

const highlightSQL = (sql) => {
  if (!sql) return ''
  
  const keywords = [
    'CREATE', 'TABLE', 'IF', 'NOT', 'EXISTS', 'DROP', 'ALTER', 'ADD', 'MODIFY', 
    'COLUMN', 'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES', 'INDEX', 'UNIQUE', 
    'DEFAULT', 'NULL', 'NOT NULL', 'AUTO_INCREMENT', 'COMMENT', 'ENGINE', 
    'CHARSET', 'COLLATE', 'DEFAULT', 'CHAR', 'VARCHAR', 'INT', 'BIGINT', 
    'SMALLINT', 'TINYINT', 'DECIMAL', 'FLOAT', 'DOUBLE', 'DATE', 'DATETIME', 
    'TIMESTAMP', 'TEXT', 'LONGTEXT', 'MEDIUMTEXT', 'ENUM', 'SET', 'BOOL', 
    'BOOLEAN', 'ON', 'CASCADE', 'RESTRICT', 'NO ACTION', 'CONSTRAINT', 
    'CHECK', 'ORDER', 'BY', 'ASC', 'DESC', 'ENGINE=InnoDB', 'CHARSET=utf8mb4'
  ]
  
  let result = sql
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  keywords.forEach(keyword => {
    const regex = new RegExp(`\\b(${keyword})\\b`, 'gi')
    result = result.replace(regex, '<span class="sql-keyword">$1</span>')
  })
  
  result = result.replace(/'([^']*)'/g, '<span class="sql-string">\'$1\'</span>')
  result = result.replace(/`([^`]*)`/g, '<span class="sql-backtick">`$1`</span>')
  result = result.replace(/--.*$/gm, '<span class="sql-comment">--$&</span>')
  result = result.replace(/\/\*[\s\S]*?\*\//g, '<span class="sql-comment">$&</span>')
  result = result.replace(/(\d+\.?\d*)/g, '<span class="sql-number">$1</span>')
  
  return result
}

const formatHistoryRoots = () => {
  if (historicalRoots.value.length === 0) return ''
  return historicalRoots.value.map(r => {
    const parts = [
      r.business_domain || '',
      r.domain_code || '',
      r.chinese_name || '',
      r.full_root || '',
      r.abbr_root || '',
      r.recommended_type || ''
    ]
    return parts.join(':')
  }).join('\n')
}

const normalizeRootItem = (item = {}) => ({
  business_domain: item.business_domain?.trim?.() || '',
  domain_code: item.domain_code?.trim?.() || '',
  chinese_name: item.chinese_name?.trim?.() || '',
  full_root: item.full_root?.trim?.() || '',
  abbr_root: item.abbr_root?.trim?.() || '',
  recommended_type: item.recommended_type?.trim?.() || '',
  root_id: item.root_id || '',
  usage_count: Number(item.usage_count || item.source_count || 1),
  updated_at: item.updated_at || '',
  created_at: item.created_at || '',
  governance_status: item.governance_status || '',
  merged_from: Array.isArray(item.merged_from) ? item.merged_from : [],
  change_history: Array.isArray(item.change_history) ? item.change_history : []
})

const buildRootIdentity = (item = {}) => {
  const normalized = normalizeRootItem(item)
  return [
    normalized.business_domain.toLowerCase(),
    normalized.domain_code.toLowerCase(),
    normalized.chinese_name.toLowerCase(),
    normalized.full_root.toLowerCase(),
    normalized.abbr_root.toLowerCase(),
    normalized.recommended_type.toLowerCase()
  ].join('|')
}

const mergeRootLists = (baseRoots = [], incomingRoots = []) => {
  const mergedMap = new Map()
  baseRoots.forEach((item) => {
    mergedMap.set(buildRootIdentity(item), normalizeRootItem(item))
  })
  incomingRoots.forEach((item) => {
    const normalized = normalizeRootItem(item)
    if (!normalized.chinese_name) return
    mergedMap.set(buildRootIdentity(normalized), normalized)
  })
  return [...mergedMap.values()]
}

const formatRootSnapshot = (snapshot = {}) => {
  const normalized = normalizeRootItem(snapshot)
  const parts = [
    normalized.business_domain || '-',
    normalized.chinese_name || '-',
    normalized.full_root || '-',
    normalized.abbr_root || '-',
    normalized.recommended_type || '-'
  ]
  return parts.join(' / ')
}

const estimatePreparedHistoricalRoots = (roots = []) => {
  const seen = new Set()
  let count = 0
  roots.forEach((root) => {
    const normalized = normalizeRootItem(root)
    if (!normalized.chinese_name) return
    const key = [
      normalized.business_domain.toLowerCase(),
      normalized.domain_code.toLowerCase(),
      normalized.chinese_name.toLowerCase(),
      normalized.full_root.toLowerCase(),
      normalized.abbr_root.toLowerCase(),
      normalized.recommended_type.toLowerCase()
    ].join('|')
    if (seen.has(key)) return
    seen.add(key)
    count += 1
  })
  return count
}

const buildStandardRootIndexes = (roots = []) => {
  const chinese = new Set()
  const full = new Set()
  const abbr = new Set()
  const pair = new Set()
  roots.forEach((root) => {
    const normalized = normalizeRootItem(root)
    const chineseName = normalized.chinese_name.toLowerCase()
    const fullRoot = normalized.full_root.toLowerCase()
    const abbrRoot = normalized.abbr_root.toLowerCase()
    if (chineseName) chinese.add(chineseName)
    if (fullRoot) full.add(fullRoot)
    if (abbrRoot) abbr.add(abbrRoot)
    if (fullRoot || abbrRoot) pair.add(`${fullRoot}|${abbrRoot}`)
  })
  return { chinese, full, abbr, pair }
}

const estimateGovernanceFilterStats = (historicalRoots = [], standardRootsList = []) => {
  const indexes = buildStandardRootIndexes(standardRootsList)
  const preparedMap = new Map()
  historicalRoots.forEach((root) => {
    const normalized = normalizeRootItem(root)
    if (!normalized.chinese_name) return
    const key = [
      normalized.business_domain.toLowerCase(),
      normalized.domain_code.toLowerCase(),
      normalized.chinese_name.toLowerCase(),
      normalized.full_root.toLowerCase(),
      normalized.abbr_root.toLowerCase(),
      normalized.recommended_type.toLowerCase()
    ].join('|')
    if (!preparedMap.has(key)) {
      preparedMap.set(key, normalized)
    }
  })

  let excluded = 0
  let kept = 0
  preparedMap.forEach((root) => {
    const chineseName = root.chinese_name.toLowerCase()
    const fullRoot = root.full_root.toLowerCase()
    const abbrRoot = root.abbr_root.toLowerCase()
    const matchedStandard = (
      (chineseName && indexes.chinese.has(chineseName)) ||
      (fullRoot && indexes.full.has(fullRoot)) ||
      (abbrRoot && indexes.abbr.has(abbrRoot)) ||
      ((fullRoot || abbrRoot) && indexes.pair.has(`${fullRoot}|${abbrRoot}`))
    )
    if (matchedStandard) {
      excluded += 1
    } else {
      kept += 1
    }
  })

  return {
    preparedCount: preparedMap.size,
    excludedStandardCount: excluded,
    filteredCount: kept,
    standardRootCount: standardRootsList.length
  }
}

const stopGovernanceHeartbeat = () => {
  if (governanceProgressInterval) {
    clearInterval(governanceProgressInterval)
    governanceProgressInterval = null
  }
  if (governanceServerProgressInterval) {
    clearInterval(governanceServerProgressInterval)
    governanceServerProgressInterval = null
  }
}

const startGovernanceHeartbeat = () => {
  stopGovernanceHeartbeat()
  governanceProgressInterval = setInterval(() => {
    governanceElapsedMs.value = Date.now() - governanceStartedAt.value
    if (governanceActiveStep.value === 4) {
      const dots = '.'.repeat((Math.floor(governanceElapsedMs.value / 1000) % 3) + 1)
      const chunkInfo = governanceStats.chunkCount > 0
        ? `，共 ${governanceStats.chunkCount} 批，已完成 ${governanceStats.completedChunks} 批`
        : ''
      governanceDetailText.value = `模型正在归并历史词根并补齐标准字段${dots}${chunkInfo}，已等待 ${formatDuration(governanceElapsedMs.value)}`
    }
  }, 1000)
}

const applyGovernanceProgress = (progress) => {
  if (!progress) return
  governanceStats.rawCount = progress.raw_root_count ?? governanceStats.rawCount
  governanceStats.preparedCount = progress.prepared_root_count ?? governanceStats.preparedCount
  governanceStats.filteredCount = progress.filtered_root_count ?? governanceStats.filteredCount
  governanceStats.excludedStandardCount = progress.excluded_standard_count ?? governanceStats.excludedStandardCount
  governanceStats.standardRootCount = progress.standard_root_count ?? governanceStats.standardRootCount
  governanceStats.chunkCount = progress.chunk_count ?? governanceStats.chunkCount
  governanceStats.requestedWorkers = progress.requested_workers ?? governanceStats.requestedWorkers
  governanceStats.actualWorkers = progress.actual_workers ?? governanceStats.actualWorkers
  governanceStats.completedChunks = progress.completed_chunks ?? governanceStats.completedChunks
  governanceStats.currentChunk = progress.current_chunk ?? governanceStats.currentChunk
  governanceStats.candidateCount = progress.final_candidate_count ?? governanceStats.candidateCount
  governanceStats.llmElapsedMs = progress.llm_elapsed_ms ?? governanceStats.llmElapsedMs
  governanceStats.activeChunksText = Array.isArray(progress.active_chunks) && progress.active_chunks.length > 0
    ? progress.active_chunks.join(', ')
    : ''

  if (progress.stage === 'chunk_running') {
    governanceActiveStep.value = 4
    governanceStatusText.value = `第 5/7 步：分批治理中`
  } else if (progress.stage === 'merge_running') {
    governanceActiveStep.value = 4
    governanceStatusText.value = `第 5/7 步：全局合并中`
  } else if (progress.stage === 'filtering_standard') {
    governanceActiveStep.value = 1
    governanceStatusText.value = '第 2/7 步：清洗并过滤标准词根'
  } else if (progress.stage === 'completed') {
    governanceActiveStep.value = 6
    governanceStatusText.value = progress.message || governanceStatusText.value
  } else if (progress.stage && governanceRunning.value) {
    governanceStatusText.value = progress.message || governanceStatusText.value
  }

  if (progress.message && governanceRunning.value) {
    governanceDetailText.value = progress.message
  }
}

const startGovernanceProgressPolling = (taskId) => {
  if (!taskId) return
  governanceTaskId.value = taskId
  if (governanceServerProgressInterval) {
    clearInterval(governanceServerProgressInterval)
  }
  const poll = async () => {
    try {
      const response = await axios.get(`/api/governance/progress/${taskId}`)
      if (response.data.code === 0 && response.data.data) {
        applyGovernanceProgress(response.data.data)
      }
    } catch (error) {
      console.error('加载治理进度失败:', error)
    }
  }
  poll()
  governanceServerProgressInterval = setInterval(poll, 1000)
}

const parseWordRootsTextInput = () => {
  return wordRootsText.value
    .split('\n')
    .map(line => line.trim())
    .filter(line => line && !line.startsWith('#') && !line.startsWith('//'))
    .map(line => line.replace(/：/g, ':').split(':').map(part => part.trim()))
    .map(parts => {
      if (parts.length >= 6) {
        return normalizeRootItem({
          business_domain: parts[0],
          domain_code: parts[1],
          chinese_name: parts[2],
          full_root: parts[3],
          abbr_root: parts[4],
          recommended_type: parts[5]
        })
      }
      if (parts.length >= 4) {
        return normalizeRootItem({
          chinese_name: parts[0],
          full_root: parts[1],
          abbr_root: parts[2],
          recommended_type: parts[3]
        })
      }
      if (parts.length >= 2) {
        return normalizeRootItem({
          chinese_name: parts[0],
          full_root: parts[1],
          abbr_root: parts[2] || '',
          recommended_type: parts[3] || ''
        })
      }
      return null
    })
    .filter(item => item && item.chinese_name)
}

const loadConfigs = async () => {
  const configs = localStorage.getItem('llm_configs')
  if (configs) {
    savedConfigs.value = JSON.parse(configs)
    if (savedConfigs.value.length > 0) {
      const defaultConfig = savedConfigs.value.find(c => c.isDefault) || savedConfigs.value[0]
        selectedConfig.value = defaultConfig.name
        llmConfig.apiUrl = defaultConfig.apiUrl
        llmConfig.model = defaultConfig.model
        llmConfig.temperature = defaultConfig.temperature !== undefined ? defaultConfig.temperature : 0.3
        llmConfig.abbrMaxLen = defaultConfig.abbrMaxLen !== undefined ? defaultConfig.abbrMaxLen : 4
        llmConfig.industryContext = defaultConfig.industryContext || ''
        if (defaultConfig.apiKey) {
          llmConfig.apiKey = decodeKey(defaultConfig.apiKey)
        apiKeySaved.value = true
      } else {
        apiKeySaved.value = false
      }
    }
  }
  
  try {
    const response = await axios.get('/api/custom-prompt')
    if (response.data.code === 0 && response.data.data) {
      customPrompt.value = response.data.data
      return
    }
  } catch (error) {
    console.error('从后端加载提示词失败:', error)
  }
  
  const savedPrompt = localStorage.getItem('custom_prompt')
  if (savedPrompt) {
    customPrompt.value = savedPrompt
    return
  }
  
  if (!customPrompt.value) {
    customPrompt.value = DEFAULT_PROMPT
  }
}

const saveCustomPrompt = async () => {
  try {
    const response = await axios.post('/api/custom-prompt', { content: customPrompt.value })
    if (response.data.code === 0) {
      ElMessage.success('自定义提示词保存成功')
    } else {
      ElMessage.error(response.data.message || '保存失败')
    }
  } catch (error) {
    console.error('保存提示词失败:', error)
    localStorage.setItem('custom_prompt', customPrompt.value)
    ElMessage.success('自定义提示词保存成功（本地）')
  }
}

const saveConfigToStorage = () => {
  localStorage.setItem('llm_configs', JSON.stringify(savedConfigs.value))
}

const resetApiKey = () => {
  apiKeySaved.value = false
  llmConfig.apiKey = ''
}

const showSaveDialog = () => {
  if (!llmConfig.apiKey && !apiKeySaved.value) {
    ElMessage.warning('请先输入 API Key')
    return
  }
  if (!llmConfig.apiUrl || !llmConfig.model) {
    ElMessage.warning('请先填写完整的 LLM 配置')
    return
  }
  saveDialogVisible.value = true
  saveForm.name = ''
  saveForm.isDefault = false
}

const saveConfig = () => {
  if (!saveForm.name) {
    ElMessage.warning('请输入配置名称')
    return
  }
  if (saveForm.isDefault) {
    savedConfigs.value.forEach(c => c.isDefault = false)
  }
    const config = {
      name: saveForm.name,
      apiKey: encodeKey(llmConfig.apiKey),
      apiUrl: llmConfig.apiUrl,
      model: llmConfig.model,
      temperature: llmConfig.temperature,
      abbrMaxLen: llmConfig.abbrMaxLen,
      industryContext: llmConfig.industryContext,
      isDefault: saveForm.isDefault
    }
  const existingIndex = savedConfigs.value.findIndex(c => c.name === config.name)
  if (existingIndex >= 0) {
    savedConfigs.value[existingIndex] = config
  } else {
    savedConfigs.value.push(config)
  }
  saveConfigToStorage()
  selectedConfig.value = config.name
  apiKeySaved.value = true
  llmConfig.apiKey = decodeKey(config.apiKey)
  saveDialogVisible.value = false
  ElMessage.success('配置保存成功')
}

const setAsDefault = () => {
  if (!selectedConfig.value) return
  savedConfigs.value.forEach(c => c.isDefault = false)
  const config = savedConfigs.value.find(c => c.name === selectedConfig.value)
  if (config) {
    config.isDefault = true
    saveConfigToStorage()
    ElMessage.success('已将 "' + config.name + '" 设为默认配置')
  }
}

const deleteConfig = async () => {
  if (!selectedConfig.value) return
  try {
    await ElMessageBox.confirm('确定要删除该配置吗？', '提示', { type: 'warning' })
    savedConfigs.value = savedConfigs.value.filter(c => c.name !== selectedConfig.value)
    saveConfigToStorage()
    selectedConfig.value = ''
    ElMessage.success('配置已删除')
  } catch {}
}

watch(selectedConfig, (newVal) => {
  if (newVal) {
    const config = savedConfigs.value.find(c => c.name === newVal)
    if (config) {
      if (config.apiKey) {
        llmConfig.apiKey = decodeKey(config.apiKey)
        apiKeySaved.value = true
      } else {
        llmConfig.apiKey = ''
        apiKeySaved.value = false
      }
        llmConfig.apiUrl = config.apiUrl
        llmConfig.model = config.model
        llmConfig.temperature = config.temperature !== undefined ? config.temperature : 0.3
        llmConfig.abbrMaxLen = config.abbrMaxLen !== undefined ? config.abbrMaxLen : 4
        llmConfig.industryContext = config.industryContext || ''
      }
    }
  })

const testConnection = async () => {
  if (!llmConfig.apiKey) {
    ElMessage.warning('请输入 API Key')
    return
  }
  testing.value = true
  try {
    const response = await axios.post('/api/test-connection', {
      api_key: llmConfig.apiKey,
      api_url: llmConfig.apiUrl,
      model: llmConfig.model
    })
    if (response.data.code === 0) {
      ElMessage.success('连接成功')
    } else {
      ElMessage.error(response.data.message || '连接失败')
    }
  } catch (error) {
    ElMessage.error('连接异常: ' + (error.message || '未知错误'))
  } finally {
    testing.value = false
  }
}

const defaultDbPort = (dbType) => {
  const map = {
    mysql: 3306,
    postgresql: 5432,
    oracle: 1521
  }
  return map[dbType] || 3306
}

const loadDbConnections = async () => {
  try {
    const response = await axios.get('/api/db-connections')
    if (response.data.code === 0) {
      dbConnections.value = response.data.data || []
    }
  } catch (error) {
    ElMessage.error('加载数据库连接失败')
  }
}

const showDbConnectionDialog = (connection = null) => {
  editingDbConnectionId.value = connection?.id || ''
  dbConnectionForm.name = connection?.name || ''
  dbConnectionForm.db_type = connection?.db_type || 'mysql'
  dbConnectionForm.host = connection?.host || ''
  dbConnectionForm.port = connection?.port || defaultDbPort(dbConnectionForm.db_type)
  dbConnectionForm.database = connection?.database || ''
  dbConnectionForm.username = connection?.username || ''
  dbConnectionForm.password = ''
  dbConnectionDialogVisible.value = true
}

watch(() => dbConnectionForm.db_type, (dbType) => {
  dbConnectionForm.port = defaultDbPort(dbType)
})

const saveDbConnection = async () => {
  if (!dbConnectionForm.name || !dbConnectionForm.db_type || !dbConnectionForm.host || !dbConnectionForm.port || !dbConnectionForm.database) {
    ElMessage.warning('请填写完整的数据库连接配置')
    return
  }
  const payload = { ...dbConnectionForm }
  try {
    const response = editingDbConnectionId.value
      ? await axios.put(`/api/db-connections/${editingDbConnectionId.value}`, payload)
      : await axios.post('/api/db-connections', payload)
    if (response.data.code === 0) {
      ElMessage.success(response.data.message || '数据库连接保存成功')
      dbConnectionDialogVisible.value = false
      await loadDbConnections()
    } else {
      ElMessage.error(response.data.message || '数据库连接保存失败')
    }
  } catch (error) {
    ElMessage.error('数据库连接保存失败')
  }
}

const testDbConnection = async (connection) => {
  testingDbConnectionId.value = connection.id
  try {
    const response = await axios.post(`/api/db-connections/${connection.id}/test`)
    if (response.data.code === 0) {
      ElMessage.success(response.data.message || '数据库连接成功')
    } else {
      ElMessage.error(response.data.message || '数据库连接失败')
    }
  } catch (error) {
    ElMessage.error('数据库连接测试失败')
  } finally {
    testingDbConnectionId.value = ''
  }
}

const deleteDbConnection = async (connection) => {
  try {
    await ElMessageBox.confirm(`确定删除数据库连接「${connection.name}」吗？`, '提示', { type: 'warning' })
    const response = await axios.delete(`/api/db-connections/${connection.id}`)
    if (response.data.code === 0) {
      ElMessage.success(response.data.message || '删除成功')
      await loadDbConnections()
    } else {
      ElMessage.error(response.data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.info('已取消删除')
    }
  }
}

const downloadTemplate = async () => {
  try {
    const response = await axios.get('/api/download-template', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = '词根模板.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('模板下载成功')
  } catch (error) {
    ElMessage.error('模板下载失败')
  }
}

const handleWordRootsFileChange = (file) => {
  wordRootsFileName.value = file.name
  wordRootsFile.value = file.raw
}

const parseWordRootsFile = async () => {
  if (!wordRootsFile.value) return
  try {
    const formData = new FormData()
    formData.append('file', wordRootsFile.value)
    formData.append('parse_type', 'roots')
    const response = await axios.post('/api/parse-file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (response.data.code === 0) {
      parsedWordRoots.value = (response.data.data || []).map(normalizeRootItem).filter(item => item.chinese_name)
      ElMessage.success(`成功解析 ${parsedWordRoots.value.length} 条词根`)
    }
  } catch (error) {
    ElMessage.error('文件解析失败')
  }
}

const previewWordRootsInput = async () => {
  if (wordRootsTab.value === 'text') {
    parsedWordRoots.value = parseWordRootsTextInput()
    if (parsedWordRoots.value.length === 0) {
      ElMessage.warning('没有解析到有效词根，请至少填写中文名称')
      return
    }
    ElMessage.success(`成功解析 ${parsedWordRoots.value.length} 条词根`)
    return
  }

  await parseWordRootsFile()
}

const saveWordRoots = async () => {
  if (wordRootsTab.value === 'text') {
    parsedWordRoots.value = parseWordRootsTextInput()
  } else if (parsedWordRoots.value.length === 0) {
    await parseWordRootsFile()
  }

  if (parsedWordRoots.value.length === 0) {
    ElMessage.warning('没有可保存的词根')
    return
  }
  try {
    await axios.post('/api/word-roots', parsedWordRoots.value)
    await loadGovernanceData()
    ElMessage.success('标准词根保存成功')
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.message || '未知错误'))
  }
}

const saveStandardRoots = async (roots, successMessage = '标准词根保存成功') => {
  await axios.post('/api/word-roots', roots)
  await loadGovernanceData()
  ElMessage.success(successMessage)
}

const clearWordRootsFile = () => {
  wordRootsFileName.value = ''
  wordRootsFile.value = null
  parsedWordRoots.value = []
  if (wordRootsUpload.value) {
    wordRootsUpload.value.clearFiles()
  }
}

const loadStandards = async () => {
  try {
    const response = await axios.get('/api/standards')
    if (response.data.code === 0) {
      const data = response.data.data
      if (data && Array.isArray(data)) {
        standardsList.value = data
        if (!currentStandardId.value && standardsList.value.length > 0) {
          selectStandard(standardsList.value[0])
        }
      } else {
        standardsList.value = []
      }
    }
  } catch (error) {
    console.error('加载规范失败:', error)
  }
}

const selectStandard = (row) => {
  currentStandardId.value = row.id
  standardsContent.value = row.content || ''
}

const createNewStandard = () => {
  currentStandardId.value = ''
  standardsContent.value = ''
  ElMessage.info('请在下方编辑区输入新的规范内容，保存时需要输入规范名称')
}

const editStandard = (row) => {
  currentStandardId.value = row.id
  standardsContent.value = row.content || ''
}

const deleteStandard = async (id) => {
  try {
    const response = await axios.delete(`/api/standards/${id}`)
    if (response.data.code === 0) {
      ElMessage.success('删除成功')
      loadStandards()
      if (currentStandardId.value === id) {
        standardsContent.value = ''
        currentStandardId.value = ''
      }
    }
  } catch (error) {
    ElMessage.error('删除失败: ' + (error.message || '未知错误'))
  }
}

const toggleStandardActive = async (standard) => {
  try {
    const action = standard.is_active ? 'deactivate' : 'activate'
    const response = await axios.put(`/api/standards/${standard.id}/${action}`)
    if (response.data.code === 0) {
      const message = standard.is_active ? '已禁用规范' : '已启用规范'
      ElMessage.success(message)
      loadStandards()
    }
  } catch (error) {
    ElMessage.error('操作失败: ' + (error.message || '未知错误'))
  }
}

const saveStandards = async () => {
  if (!standardsContent.value.trim()) {
    ElMessage.warning('请输入规范内容')
    return
  }
  
  let standardName = ''
  if (currentStandardId.value) {
    const existingStandard = standardsList.value.find(s => s.id === currentStandardId.value)
    if (existingStandard) {
      standardName = existingStandard.name
    }
  }
  
  if (!standardName) {
    try {
      const name = await ElMessageBox.prompt('请输入规范名称', '新建规范', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPlaceholder: '例如：数仓命名规范'
      })
      standardName = name.value || '未命名规范'
    } catch {
      ElMessage.info('已取消保存')
      return
    }
  }
  
  try {
    let response
    if (currentStandardId.value) {
      response = await axios.put(`/api/standards/${currentStandardId.value}`, { 
        content: standardsContent.value,
        name: standardName
      })
    } else {
      response = await axios.post('/api/standards', { 
        content: standardsContent.value, 
        name: standardName 
      })
    }
    if (response.data.code === 0) {
      ElMessage.success('规范保存成功')
      loadStandards()
    }
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.message || '未知错误'))
  }
}

const handleBatchFileChange = (file) => {
  const uploadRef = batchUpload.value
  if (uploadRef) {
    uploadRef.clearFiles()
  }
  
  batchFileName.value = file.name
  batchFile.value = file.raw
  batchResult.value = null
  parsedBatchTables.value = []
  ElMessage.info('文件已选择，正在解析...')
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target.result)
      const workbook = XLSX.read(data, { type: 'array' })
      const sheetName = workbook.SheetNames[0]
      const worksheet = workbook.Sheets[sheetName]
      const jsonData = XLSX.utils.sheet_to_json(worksheet)
      
      console.log('解析到的数据:', jsonData)
      
      const tables = {}
      const subjectDomainMap = {}
      for (const row of jsonData) {
        const tableName = row['表名']
        const layer = row['表分层'] || ''
        const subjectDomain = row['主题域'] || ''
        const fieldName = row['字段名']
        const fieldType = row['推荐字段类型'] || 'VARCHAR(255)'
        
        if (!tableName || !fieldName) continue
        
        if (!tables[tableName]) {
          tables[tableName] = {
            tableName,
            layer,
            fields: []
          }
          subjectDomainMap[tableName] = new Set()
        }
        if (subjectDomain) {
          subjectDomainMap[tableName].add(subjectDomain)
        }
        tables[tableName].fields.push({ name: fieldName, type: fieldType })
      }
      
      parsedBatchTables.value = Object.values(tables).map(t => {
        const domains = subjectDomainMap[t.tableName] || new Set()
        const domainList = [...domains]
        let finalDomain = domainList.length > 0 ? domainList[0] : ''
        if (domainList.length > 1) {
          console.warn(`表[${t.tableName}]存在多个主题域值: ${domainList.join(', ')}，已取第一个`)
        }
        return {
          tableName: t.tableName,
          layer: t.layer,
          subjectDomain: finalDomain,
          fieldCount: t.fields.length,
          fields: t.fields.map(f => `${f.name}(${f.type})`).join(', ')
        }
      })
      
      console.log('解析结果:', parsedBatchTables.value)
      ElMessage.success(`解析完成，共 ${parsedBatchTables.value.length} 张表`)
    } catch (error) {
      ElMessage.error('Excel解析失败: ' + error.message)
      console.error('Excel解析错误:', error)
    }
  }
  reader.readAsArrayBuffer(file.raw)
}

const downloadBatchTemplate = () => {
  axios({
    url: '/api/download-batch-template',
    method: 'GET',
    responseType: 'blob'
  }).then(response => {
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', '批量建表模板.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    ElMessage.success('模板下载成功')
  }).catch(() => {
    ElMessage.error('模板下载失败，请检查后端服务')
  })
}

const generateTaskId = () => {
  return 'task_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
}

const resetGenerationTaskState = () => {
  batchGenerating.value = true
  batchProgress.value = generationMode.value === 'text' ? '输入解析中...' : '准备中...'
  batchProgressPercent.value = 0
  batchResult.value = null
  batchNewRoots.value = []
  currentTaskId.value = generateTaskId()
  realProgress.value = null
  fieldStats.value = null
  fieldProgress.value = null
}

const startTextGenerate = async () => {
  if (!description.value.trim()) {
    ElMessage.warning('请输入建表需求')
    return
  }
  if (!llmConfig.apiKey) {
    ElMessage.warning('请先在基础配置中设置API Key')
    return
  }

  resetGenerationTaskState()

  try {
    const response = await axios.post('/api/text-generate-ddl-task', {
      llm_config: {
        api_key: llmConfig.apiKey,
        api_url: llmConfig.apiUrl,
        model: llmConfig.model,
        temperature: llmConfig.temperature,
        abbr_max_len: llmConfig.abbrMaxLen,
        industry_context: llmConfig.industryContext || ''
      },
      description: description.value,
      db_type: batchDbType.value,
      custom_prompt: customPrompt.value,
      root_match_priority: batchRootPriority.value,
      cut_mode: batchCutMode.value,
      enable_validation: batchEnableValidation.value,
      task_id: currentTaskId.value
    })

    if (response.data.code === 0) {
      ElMessage.info('任务已启动，正在处理...')
      startProgressPolling()
    } else {
      ElMessage.error(response.data.message || '任务启动失败')
      batchGenerating.value = false
    }
  } catch (error) {
    ElMessage.error('任务启动失败: ' + (error.message || '未知错误'))
    console.error(error)
    batchGenerating.value = false
  }
}

const handleStandardRootsImportFileChange = async (file) => {
  const uploadRef = standardRootsUpload.value
  if (uploadRef) {
    uploadRef.clearFiles()
  }
  if (!file?.raw) {
    return
  }
  try {
    const formData = new FormData()
    formData.append('file', file.raw)
    formData.append('parse_type', 'roots')
    const response = await axios.post('/api/parse-file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    const parsedRoots = response.data.code === 0
      ? (response.data.data || []).map(normalizeRootItem).filter(item => item.chinese_name)
      : []
    if (parsedRoots.length === 0) {
      ElMessage.warning('没有解析到可导入的标准词根')
      return
    }
    const mergedRoots = mergeRootLists(standardRoots.value, parsedRoots)
    await saveStandardRoots(mergedRoots, `标准词根导入成功，共新增/合并 ${parsedRoots.length} 条`)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || error.message || '标准词根导入失败')
  }
}

const exportStandardRootsToExcel = () => {
  if (standardRoots.value.length === 0) {
    ElMessage.warning('暂无可导出的标准词根')
    return
  }
  const exportRows = standardRoots.value.map((item) => {
    const normalized = normalizeRootItem(item)
    return {
      '业务域': normalized.business_domain,
      '域编码': normalized.domain_code,
      '中文名称': normalized.chinese_name,
      '全称词根': normalized.full_root,
      '缩写词根': normalized.abbr_root,
      '推荐类型': normalized.recommended_type
    }
  })
  const worksheet = XLSX.utils.json_to_sheet(exportRows)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, '标准词根')
  XLSX.writeFile(workbook, '标准词根.xlsx')
  ElMessage.success('标准词根导出成功')
}

const startBatchGenerate = async () => {
  if (!batchFile.value) {
    ElMessage.warning('请先选择Excel文件')
    return
  }
  if (!llmConfig.apiKey) {
    ElMessage.warning('请先在基础配置中设置API Key')
    return
  }

  resetGenerationTaskState()

  const formData = new FormData()
  formData.append('file', batchFile.value)
  formData.append('api_key', llmConfig.apiKey)
  formData.append('api_url', llmConfig.apiUrl)
  formData.append('model', llmConfig.model)
  formData.append('industry_context', llmConfig.industryContext || '')
  formData.append('db_type', batchDbType.value)
  formData.append('root_match_priority', batchRootPriority.value)
  formData.append('cut_mode', batchCutMode.value)
  formData.append('enable_validation', batchEnableValidation.value)
  formData.append('max_workers', batchMaxWorkers.value)
    formData.append('task_id', currentTaskId.value)
    formData.append('custom_prompt', customPrompt.value)
    formData.append('temperature', llmConfig.temperature)
    formData.append('abbr_max_len', llmConfig.abbrMaxLen)

  try {
    const response = await axios.post('/api/batch-generate-ddl', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    if (response.data.code === 0) {
      ElMessage.info('任务已启动，正在处理...')
      startProgressPolling()
      startFallbackProgress()
    } else {
      ElMessage.error(response.data.message || '任务启动失败')
      batchGenerating.value = false
    }
  } catch (error) {
    ElMessage.error('任务启动失败: ' + (error.message || '未知错误'))
    console.error(error)
    batchGenerating.value = false
  }
}

const startGenerate = async () => {
  if (generationMode.value === 'text') {
    await startTextGenerate()
    return
  }
  await startBatchGenerate()
}

const startProgressPolling = () => {
  if (progressPollingInterval) {
    clearInterval(progressPollingInterval)
  }
  
  progressPollingInterval = setInterval(async () => {
    if (!currentTaskId.value) return
    
    try {
      const response = await axios.get(`/api/progress/${currentTaskId.value}`)
      console.log('完整进度响应:', response.data)
      if (response.data.code === 0) {
        const progress = response.data.data
        console.log('进度数据:', progress)
        console.log('matched_count:', progress.matched_count)
        console.log('unmatched_count:', progress.unmatched_count)
        console.log('total_fields:', progress.total_fields)
        
        if (progress) {
          realProgress.value = progress
          
          if (fallbackProgressInterval) {
            clearInterval(fallbackProgressInterval)
            fallbackProgressInterval = null
          }
          
          const { current, total, table_name, new_roots, stage, milestones, overall_progress, 
                 matched_count, unmatched_count, total_fields, field_progress } = progress
          
          if (stage) {
            batchProgress.value = stage
          } else if (table_name) {
            batchProgress.value = `🔄 ${current}/${total}，表名：${table_name}`
          } else {
            batchProgress.value = `🔄 ${current}/${total}，请稍等...`
          }
          if (overall_progress !== undefined) {
            batchProgressPercent.value = overall_progress
          } else {
            batchProgressPercent.value = Math.round((current / total) * 100)
          }
          
          if (milestones) {
            console.log('里程碑数据:', milestones)
          }
          
          if (matched_count !== undefined || unmatched_count !== undefined || total_fields !== undefined) {
            fieldStats.value = { 
              matched_count: matched_count, 
              unmatched_count: unmatched_count, 
              total_fields: total_fields 
            }
            console.log('字段统计数据:', fieldStats.value)
          }

          if (field_progress) {
            fieldProgress.value = field_progress
            console.log('字段生成进度:', fieldProgress.value)
          }
          
          if (new_roots && new_roots.length > 0) {
            batchNewRoots.value = new_roots
          }
          
          if (current >= total) {
            await fetchBatchResult()
          }
        }
      } else if (response.data.code === 1) {
        console.log('进度API返回任务已完成，尝试获取结果')
        await fetchBatchResult()
      }
    } catch (error) {
      console.error('获取进度失败:', error)
    }
  }, 500)
}

const fetchBatchResult = async () => {
  if (!currentTaskId.value) return
  let shouldStopPolling = false
  
  try {
    const response = await axios.get(`/api/batch-result/${currentTaskId.value}`)
    console.log('获取任务结果响应:', response.data)
    if (response.data.code === 0) {
      shouldStopPolling = true
      batchResult.value = response.data.data
      batchProgress.value = `✅ 完成 (${batchResult.value.success_count}/${batchResult.value.total_tables})`
      batchProgressPercent.value = 100
      
      if (batchResult.value.new_roots && batchResult.value.new_roots.length > 0) {
        batchNewRoots.value = batchResult.value.new_roots
      }
      
      console.log('结果中的字段统计:', batchResult.value.field_stats)
      if (batchResult.value.field_stats) {
        fieldStats.value = batchResult.value.field_stats
      }
      
      ElMessage.success(generationMode.value === 'text' ? '生成完成' : '批量生成完成')
    } else if (response.data.code === 1 && response.data.message === '任务处理中或不存在') {
      return
    } else {
      shouldStopPolling = true
      ElMessage.error(response.data.message || '任务执行失败')
    }
  } catch (error) {
    console.error('获取任务结果失败:', error)
  } finally {
    if (shouldStopPolling) {
      stopProgressPolling()
      batchGenerating.value = false
      currentTaskId.value = ''
    }
  }
}

const cancelBatchTask = async () => {
  if (!currentTaskId.value) {
    ElMessage.warning('没有正在执行的任务')
    return
  }
  
  try {
    const response = await axios.post(`/api/batch-task/${currentTaskId.value}/cancel`)
    if (response.data.code === 0) {
      ElMessage.info('任务已终止')
      batchGenerating.value = false
      batchProgress.value = '⛔ 任务已终止'
      stopProgressPolling()
    }
  } catch (error) {
    ElMessage.error('终止任务失败: ' + (error.message || '未知错误'))
  }
}

const startFallbackProgress = () => {
  if (fallbackProgressInterval) {
    clearInterval(fallbackProgressInterval)
  }
  
  const totalTables = parsedBatchTables.value.length
  let fakeProgress = 0
  
  fallbackProgressInterval = setInterval(() => {
    if (realProgress.value) return
    
    if (fakeProgress < totalTables) {
      fakeProgress++
      const tableName = parsedBatchTables.value[fakeProgress - 1]?.tableName || '未知表'
      batchProgress.value = `🔄 ${fakeProgress}/${totalTables}，表名：${tableName}`
      batchProgressPercent.value = Math.round((fakeProgress / totalTables) * 100)
    }
  }, 1000)
}

const stopProgressPolling = () => {
  if (progressPollingInterval) {
    clearInterval(progressPollingInterval)
    progressPollingInterval = null
  }
  if (fallbackProgressInterval) {
    clearInterval(fallbackProgressInterval)
    fallbackProgressInterval = null
  }
}

const copyBatchDDL = async () => {
  if (batchResult.value && batchResult.value.full_ddl) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(batchResult.value.full_ddl)
        ElMessage.success('SQL已复制到剪贴板')
      } else {
        const textArea = document.createElement('textarea')
        textArea.value = batchResult.value.full_ddl
        textArea.style.position = 'fixed'
        textArea.style.left = '-9999px'
        textArea.style.top = '-9999px'
        document.body.appendChild(textArea)
        textArea.focus()
        textArea.select()
        try {
          document.execCommand('copy')
          ElMessage.success('SQL已复制到剪贴板')
        } catch (err) {
          ElMessage.error('复制失败，请手动复制')
        }
        document.body.removeChild(textArea)
      }
    } catch (error) {
      console.error('复制失败:', error)
      ElMessage.error('复制失败，请手动复制')
    }
  }
}

const downloadBatchDDL = () => {
  if (!batchResult.value || !batchResult.value.full_ddl) {
    ElMessage.warning('没有可下载的SQL')
    return
  }
  
  const blob = new Blob([batchResult.value.full_ddl], { type: 'text/plain;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `batch_ddl_${Date.now()}.sql`)
  document.body.appendChild(link)
  link.click()
  link.remove()
  ElMessage.success('SQL文件下载成功')
}

const validateRootItem = (item) => {
  const requiredFields = ['chinese_name']
  const missingFields = requiredFields.filter(field => !item[field])
  if (missingFields.length > 0) {
    console.warn('词根数据缺少必填字段:', { item, missingFields })
    return false
  }
  return true
}

const saveBatchNewRoots = async () => {
  if (batchNewRoots.value.length === 0) {
    ElMessage.warning('没有新词根需要保存')
    return
  }
  
  console.log('准备保存批量新词根，数据结构:', batchNewRoots.value)
  
  // 验证数据结构
  const validRoots = batchNewRoots.value.filter(validateRootItem)
  if (validRoots.length === 0) {
    ElMessage.error('没有有效的词根数据可保存，请检查数据格式')
    return
  }
  
  try {
    const response = await axios.post('/api/save-new-roots', validRoots)
    if (response.data.code === 0) {
      ElMessage.success(response.data.message || '新词根保存成功')
      batchNewRoots.value = []
      await loadGovernanceData()
    } else {
      ElMessage.error(response.data.message || '保存失败')
    }
  } catch (error) {
    console.error('保存批量新词根失败:', error)
    if (error.response) {
      console.error('错误响应:', error.response.data)
    }
    ElMessage.error('保存新词根失败，请查看控制台了解详细信息')
  }
}

const saveSingleNewRoots = async () => {
  if (singleNewRoots.value.length === 0) {
    ElMessage.warning('没有新词根需要保存')
    return
  }

  console.log('准备保存单个新词根，数据结构:', singleNewRoots.value)
  
  // 验证数据结构
  const validRoots = singleNewRoots.value.filter(validateRootItem)
  if (validRoots.length === 0) {
    ElMessage.error('没有有效的词根数据可保存，请检查数据格式')
    return
  }
  
  try {
    const response = await axios.post('/api/save-new-roots', validRoots)
    if (response.data.code === 0) {
      ElMessage.success(response.data.message || '新词根保存成功')
      singleNewRoots.value = []
      await loadGovernanceData()
    } else {
      ElMessage.error(response.data.message || '保存失败')
    }
  } catch (error) {
    console.error('保存单个新词根失败:', error)
    if (error.response) {
      console.error('错误响应:', error.response.data)
    }
    ElMessage.error('保存新词根失败，请查看控制台了解详细信息')
  }
}

const loadHistory = async () => {
  historyLoading.value = true
  try {
    const response = await axios.get('/api/ddl-history', { params: { limit: 20 } })
    if (response.data.code === 0) {
      historyList.value = response.data.data
    }
  } catch (error) {
    ElMessage.error('加载历史记录失败')
    console.error(error)
  } finally {
    historyLoading.value = false
  }
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const formatDbType = (db_type) => {
  if (!db_type) return '-'
  const dbMap = {
    'mysql': '🐬 MySQL',
    'postgresql': '🐘 PostgreSQL',
    'oracle': '🔶 Oracle'
  }
  return dbMap[db_type] || db_type
}

const formatRootPriority = (priority) => {
  if (!priority) return '-'
  return priority === 'full' ? '全称' : '缩写'
}

const viewHistoryDDL = (record) => {
  currentHistoryDDL.value = record.ddl
  currentHistoryTitle.value = `记录 ${record.id} - ${record.description}`
  currentHistoryRecord.value = record
  historyViewDialog.value = true
}

const showExecuteDialog = async (record) => {
  if (!record) return
  executeRecord.value = record
  selectedExecuteConnectionId.value = ''
  await loadDbConnections()
  const matched = dbConnections.value.filter(conn => conn.db_type === record.db_type)
  if (matched.length > 0) {
    selectedExecuteConnectionId.value = matched[0].id
  }
  executeDialogVisible.value = true
}

const refreshCurrentHistoryRecord = () => {
  if (!currentHistoryRecord.value) return
  const latest = historyList.value.find(item => item.id === currentHistoryRecord.value.id)
  if (latest) {
    currentHistoryRecord.value = latest
    currentHistoryDDL.value = latest.ddl
  }
}

const executeHistoryDDL = async () => {
  if (!executeRecord.value || !selectedExecuteConnectionId.value) return
  const connection = dbConnections.value.find(conn => conn.id === selectedExecuteConnectionId.value)
  try {
    await ElMessageBox.confirm(
      `确认使用「${connection?.name || ''}」执行该历史SQL建表吗？`,
      '确认建表',
      { type: 'warning' }
    )
  } catch {
    return
  }

  executingHistoryDDL.value = true
  try {
    const response = await axios.post(`/api/ddl-history/${executeRecord.value.id}/execute`, {
      connection_id: selectedExecuteConnectionId.value
    })
    if (response.data.code === 0) {
      ElMessage.success(response.data.message || '建表执行成功')
      executeDialogVisible.value = false
      await loadHistory()
      refreshCurrentHistoryRecord()
    } else {
      ElMessage.error(response.data.message || '建表执行失败')
      await loadHistory()
      refreshCurrentHistoryRecord()
    }
  } catch (error) {
    ElMessage.error('建表执行失败')
  } finally {
    executingHistoryDDL.value = false
  }
}

const copyAllDDL = async () => {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(currentHistoryDDL.value)
      ElMessage.success('已复制到剪贴板')
    } else {
      const textArea = document.createElement('textarea')
      textArea.value = currentHistoryDDL.value
      textArea.style.position = 'fixed'
      textArea.style.left = '-9999px'
      textArea.style.top = '-9999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      try {
        document.execCommand('copy')
        ElMessage.success('已复制到剪贴板')
      } catch (err) {
        ElMessage.error('复制失败，请手动复制')
      }
      document.body.removeChild(textArea)
    }
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动复制')
  }
}

const downloadHistoryDDL = async (recordId) => {
  try {
    const response = await axios.get(`/api/ddl-history/${recordId}/download`, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `ddl_${recordId}.sql`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    ElMessage.success('SQL文件下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
    console.error(error)
  }
}

const deleteHistoryRecord = async (recordId) => {
  ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await axios.delete(`/api/ddl-history/${recordId}`)
      ElMessage.success('删除成功')
      loadHistory()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

const clearAllHistory = () => {
  ElMessageBox.confirm('确定要清空所有历史记录吗？此操作不可恢复！', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'danger'
  }).then(async () => {
    for (const record of historyList.value) {
      try {
        await axios.delete(`/api/ddl-history/${record.id}`)
      } catch (e) {
        console.error(e)
      }
    }
    historyList.value = []
    ElMessage.success('清空成功')
  }).catch(() => {
    ElMessage.info('已取消清空')
  })
}

const renderMarkdown = (text) => {
  if (!text) return ''
  
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  html = html.replace(/^##### (.+)$/gm, '<h5>$1</h5>')
  html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>')
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>')
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>')
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>')
  
  html = html.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
  
  html = processTables(html)
  
  html = processLists(html)
  
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  html = html.replace(/~~(.+?)~~/g, '<s>$1</s>')
  html = html.replace(/__(.+?)__/g, '<u>$1</u>')
  
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
  html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="code-block"><code>$2</code></pre>')
  
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" />')
  
  html = html.replace(/\n/g, '<br>')
  
  html = html.replace(/<\/?(ul|ol|li|table|tr|td|th|pre|blockquote)><br>/g, '</$1>')
  html = html.replace(/<br><(ul|ol|li|table|tr|td|th|pre|blockquote)/g, '<$1')
  
  return html
}

const processLists = (html) => {
  const lines = html.split('\n')
  let result = []
  let inUnorderedList = false
  let inOrderedList = false
  
  for (let line of lines) {
    const unorderedMatch = line.match(/^(\s*)- (.+)$/)
    const orderedMatch = line.match(/^(\s*)\d+\. (.+)$/)
    
    if (unorderedMatch) {
      if (!inUnorderedList) {
        result.push('<ul>')
        inUnorderedList = true
      }
      if (inOrderedList) {
        result.push('</ol>')
        inOrderedList = false
      }
      result.push(`<li>${unorderedMatch[2]}</li>`)
    } else if (orderedMatch) {
      if (!inOrderedList) {
        result.push('<ol>')
        inOrderedList = true
      }
      if (inUnorderedList) {
        result.push('</ul>')
        inUnorderedList = false
      }
      result.push(`<li>${orderedMatch[2]}</li>`)
    } else {
      if (inUnorderedList) {
        result.push('</ul>')
        inUnorderedList = false
      }
      if (inOrderedList) {
        result.push('</ol>')
        inOrderedList = false
      }
      result.push(line)
    }
  }
  
  if (inUnorderedList) {
    result.push('</ul>')
  }
  if (inOrderedList) {
    result.push('</ol>')
  }
  
  return result.join('\n')
}

const processTables = (html) => {
  const lines = html.split('\n')
  let result = []
  let inTable = false
  let headerRow = []
  
  for (let line of lines) {
    const trimmedLine = line.trimStart()
    const hasPipe = trimmedLine.includes('|')
    
    if (hasPipe && trimmedLine.match(/^\s*\|.*\|/)) {
      if (!inTable) {
        result.push('<table class="markdown-table">')
        inTable = true
        headerRow = []
      }
      
      const content = trimmedLine.replace(/^\s*\|/, '').replace(/\|$/, '')
      const parts = content.split('|').map(p => p.trim()).filter(p => p)
      
      const isSeparator = parts.every(p => p.replace(/\s/g, '').match(/^-+$/))
      
      if (isSeparator) {
        if (headerRow.length > 0) {
          result.push('<thead><tr><th>' + headerRow.join('</th><th>') + '</th></tr></thead><tbody>')
          headerRow = []
        }
      } else if (headerRow.length === 0 && !inTable) {
        headerRow = parts
      } else {
        result.push('<tr><td>' + parts.join('</td><td>') + '</td></tr>')
      }
    } else {
      if (inTable) {
        if (headerRow.length > 0) {
          result.push('<thead><tr><th>' + headerRow.join('</th><th>') + '</th></tr></thead><tbody>')
          headerRow = []
        }
        result.push('</tbody></table>')
        inTable = false
      }
      result.push(line)
    }
  }
  
  if (inTable) {
    if (headerRow.length > 0) {
      result.push('<thead><tr><th>' + headerRow.join('</th><th>') + '</th></tr></thead><tbody>')
    }
    result.push('</tbody></table>')
  }
  
  return result.join('\n')
}

const loadGovernanceData = async () => {
  try {
    const s = await axios.get("/api/standard-roots")
    const h = await axios.get("/api/historical-roots")
    standardRoots.value = s.data.code === 0 && Array.isArray(s.data.data) ? s.data.data.map(normalizeRootItem) : []
    historicalRoots.value = h.data.code === 0 && Array.isArray(h.data.data) ? h.data.data.map(normalizeRootItem) : []
  } catch (e) {
    console.error(e)
    standardRoots.value = []
    historicalRoots.value = []
  }
}

const runGovernance = async () => {
  if (!llmConfig.apiKey) {
    ElMessage.warning('请先在基础配置中填写可用的 LLM API Key')
    return
  }

  const taskId = window.crypto?.randomUUID?.() || `gov-${Date.now()}-${Math.random().toString(16).slice(2)}`
  governanceRunning.value = true
  governanceTaskId.value = taskId
  governanceStartedAt.value = Date.now()
  governanceElapsedMs.value = 0
  governanceStats.rawCount = historicalRoots.value.length
  governanceStats.preparedCount = 0
  governanceStats.filteredCount = 0
  governanceStats.excludedStandardCount = 0
  governanceStats.standardRootCount = standardRoots.value.length
  governanceStats.candidateCount = 0
  governanceStats.promptLength = 0
  governanceStats.llmElapsedMs = 0
  governanceStats.chunkCount = 0
  governanceStats.requestedWorkers = batchMaxWorkers.value
  governanceStats.actualWorkers = 0
  governanceStats.completedChunks = 0
  governanceStats.currentChunk = 0
  governanceStats.activeChunksText = ''
  governanceActiveStep.value = 0
  governanceStatusText.value = '第 1/7 步：加载历史词根'
  governanceDetailText.value = '正在刷新历史词根与标准词根数据'
  startGovernanceHeartbeat()
  try {
    await loadGovernanceData()
    governanceStats.rawCount = historicalRoots.value.length

    governanceActiveStep.value = 1
    governanceStatusText.value = '第 2/7 步：清洗去重'
    {
      const filterStats = estimateGovernanceFilterStats(historicalRoots.value, standardRoots.value)
      governanceStats.preparedCount = filterStats.preparedCount
      governanceStats.filteredCount = filterStats.filteredCount
      governanceStats.excludedStandardCount = filterStats.excludedStandardCount
      governanceStats.standardRootCount = filterStats.standardRootCount
    }
    governanceDetailText.value = `已加载 ${governanceStats.rawCount} 条历史词根，去重后 ${governanceStats.preparedCount} 条，剔除标准已存在 ${governanceStats.excludedStandardCount} 条，剩余 ${governanceStats.filteredCount} 条待治理`

    governanceActiveStep.value = 2
    governanceStatusText.value = '第 3/7 步：构建治理提示词'
    governanceDetailText.value = `正在为剩余 ${governanceStats.filteredCount} 条待治理词根整理业务域、中文名称、全称词根、缩写词根等上下文`

    governanceActiveStep.value = 3
    governanceStatusText.value = '第 4/7 步：发送模型请求'
    governanceDetailText.value = `准备调用模型 ${llmConfig.model} 发起词根治理`

    governanceActiveStep.value = 4
    governanceStatusText.value = '第 5/7 步：等待模型响应'
    governanceDetailText.value = '已发出治理请求，正在等待模型返回归并结果'
    const estimatedChunkCount = governanceStats.filteredCount > 0 ? Math.ceil(governanceStats.filteredCount / 50) : 0
    governanceStats.chunkCount = estimatedChunkCount
    governanceStats.actualWorkers = estimatedChunkCount > 0 ? Math.min(estimatedChunkCount, batchMaxWorkers.value) : 0
    startGovernanceProgressPolling(taskId)
    const response = await axios.post('/api/governance/run', {
      llm_config: {
        api_key: llmConfig.apiKey,
        api_url: llmConfig.apiUrl,
        model: llmConfig.model,
        temperature: llmConfig.temperature,
        abbr_max_len: llmConfig.abbrMaxLen,
        industry_context: llmConfig.industryContext || ''
      },
      max_workers: batchMaxWorkers.value,
      task_id: taskId
    })

    governanceActiveStep.value = 5
    governanceStatusText.value = '第 6/7 步：解析治理结果'
    governanceDetailText.value = '模型已返回结果，正在解析 JSON 并标准化字段'
    if (response.data.code === 0) {
      governanceCandidates.value = Array.isArray(response.data.data) ? response.data.data.map(item => ({ ...normalizeRootItem(item), governance_status: item.governance_status || '' })) : []
      governanceActiveStep.value = 6
      governanceStats.rawCount = response.data.meta?.raw_root_count ?? governanceStats.rawCount
      governanceStats.preparedCount = response.data.meta?.prepared_root_count ?? governanceStats.preparedCount
      governanceStats.filteredCount = response.data.meta?.filtered_root_count ?? governanceStats.filteredCount
      governanceStats.excludedStandardCount = response.data.meta?.excluded_standard_count ?? governanceStats.excludedStandardCount
      governanceStats.standardRootCount = response.data.meta?.standard_root_count ?? governanceStats.standardRootCount
      governanceStats.promptLength = response.data.meta?.prompt_length ?? 0
      governanceStats.candidateCount = response.data.meta?.final_candidate_count ?? governanceCandidates.value.length
      governanceStats.llmElapsedMs = response.data.meta?.llm_elapsed_ms ?? 0
      governanceStats.chunkCount = response.data.meta?.chunk_count ?? governanceStats.chunkCount
      governanceStats.requestedWorkers = response.data.meta?.requested_workers ?? governanceStats.requestedWorkers
      governanceStats.actualWorkers = response.data.meta?.actual_workers ?? governanceStats.actualWorkers
      governanceStats.completedChunks = response.data.meta?.chunk_count ?? governanceStats.completedChunks
      governanceStats.currentChunk = response.data.meta?.chunk_count ?? governanceStats.currentChunk
      governanceStats.activeChunksText = ''
      governanceElapsedMs.value = response.data.meta?.elapsed_ms ?? (Date.now() - governanceStartedAt.value)
      governanceStatusText.value = `治理完成，生成 ${governanceCandidates.value.length} 条候选标准词根`
      governanceDetailText.value = governanceStats.chunkCount > 0
        ? `已剔除标准已存在 ${governanceStats.excludedStandardCount} 条，实际治理 ${governanceStats.filteredCount} 条，共 ${governanceStats.chunkCount} 批，并发 ${governanceStats.actualWorkers} 个线程，最终提示词长度 ${governanceStats.promptLength} 字符，模型耗时 ${formatDuration(governanceStats.llmElapsedMs)}`
        : `历史词根已被现有标准词根覆盖，已剔除 ${governanceStats.excludedStandardCount} 条，无需再调用模型`
      ElMessage.success(response.data.message || '词根治理完成')
    } else {
      governanceStatusText.value = '词根治理失败'
      governanceDetailText.value = '治理请求已返回，但服务端未生成有效候选结果'
      ElMessage.error(response.data.message || '词根治理失败')
    }
  } catch (error) {
    governanceStatusText.value = '词根治理失败'
    governanceDetailText.value = error.response?.data?.detail || error.message || '治理过程中发生异常'
    ElMessage.error(error.response?.data?.detail || error.message || '词根治理失败')
  } finally {
    governanceRunning.value = false
    governanceElapsedMs.value = Date.now() - governanceStartedAt.value
    stopGovernanceHeartbeat()
  }
}

const applyGovernance = async () => {
  if (governanceCandidates.value.length === 0) {
    ElMessage.warning('当前没有可应用的治理结果')
    return
  }

  try {
    const response = await axios.post('/api/governance/apply', governanceCandidates.value)
    if (response.data.code === 0) {
      standardRoots.value = Array.isArray(response.data.data) ? response.data.data.map(normalizeRootItem) : []
      governanceCandidates.value = []
      await loadGovernanceData()
      ElMessage.success('治理结果已写入标准词根')
    } else {
      ElMessage.error(response.data.message || '应用治理结果失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || error.message || '应用治理结果失败')
  }
}

const loadHistoricalRoots = async () => {
  try {
    const response = await axios.get('/api/historical-roots')
    if (response.data.code === 0) {
      historicalRoots.value = response.data.data || []
    }
  } catch (error) {
    console.error('加载历史词根失败:', error)
  }
}

const showAddRootDialog = (target = 'historical') => {
  addRootTarget.value = target
  addRootDialogVisible.value = true
  addRootForm.businessDomain = ''
  addRootForm.domainCode = ''
  addRootForm.chineseName = ''
  addRootForm.fullRoot = ''
  addRootForm.abbrRoot = ''
  addRootForm.recommendedType = ''
}

const addRoot = async () => {
  if (!addRootForm.chineseName) {
    ElMessage.warning('请填写中文名称')
    return
  }
  const newRoot = normalizeRootItem({
    business_domain: addRootForm.businessDomain,
    domain_code: addRootForm.domainCode,
    chinese_name: addRootForm.chineseName,
    full_root: addRootForm.fullRoot,
    abbr_root: addRootForm.abbrRoot,
    recommended_type: addRootForm.recommendedType
  })
  try {
    if (addRootTarget.value === 'standard') {
      const mergedRoots = mergeRootLists(standardRoots.value, [newRoot])
      await saveStandardRoots(mergedRoots, '标准词根添加成功')
    } else {
      await axios.post('/api/historical-roots', [...historicalRoots.value, newRoot])
      await loadGovernanceData()
      ElMessage.success('词根添加成功')
    }
    addRootDialogVisible.value = false
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const saveHistoricalRoots = async () => {
  if (historicalRoots.value.length === 0) {
    ElMessage.warning('没有可保存的词根')
    return
  }
  try {
    await axios.post('/api/historical-roots', historicalRoots.value)
    ElMessage.success('历史词根保存成功')
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.message || '未知错误'))
  }
}

const removeHistoricalRoot = async (root) => {
  const index = historicalRoots.value.findIndex(r => r === root)
  if (index === -1) return
  const removed = historicalRoots.value.splice(index, 1)[0]
  try {
    await axios.post('/api/historical-roots', historicalRoots.value)
  } catch (error) {
    historicalRoots.value.splice(index, 0, removed)
    ElMessage.error('删除失败')
  }
}

const editHistoricalRoot = (root) => {
  editHistoricalRootIndex.value = historicalRoots.value.findIndex(item => item === root)
  Object.assign(editingRoot, normalizeRootItem(root))
  editRootDialogVisible.value = true
}

const editStandardRoot = (root) => {
  const normalized = normalizeRootItem(root)
  editingStandardRootId.value = normalized.root_id
  Object.assign(editingStandardRoot, normalized)
  standardRootEditDialogVisible.value = true
}

const showStandardRootHistory = (root) => {
  const normalized = normalizeRootItem(root)
  currentStandardRootTitle.value = `修改记录 - ${normalized.chinese_name || normalized.full_root || '标准词根'}`
  currentStandardRootHistory.value = Array.isArray(normalized.change_history)
    ? [...normalized.change_history].reverse()
    : []
  standardRootHistoryDialogVisible.value = true
}

const saveHistoricalRootEdit = async () => {
  if (!editingRoot.chinese_name) {
    ElMessage.warning('中文名称不能为空')
    return
  }
  const index = editHistoricalRootIndex.value
  if (index !== -1) {
    historicalRoots.value[index] = normalizeRootItem(editingRoot)
    try {
      await axios.post('/api/historical-roots', historicalRoots.value)
      editRootDialogVisible.value = false
      editHistoricalRootIndex.value = -1
      ElMessage.success('保存成功')
    } catch (error) {
      ElMessage.error('保存失败')
    }
  }
}

const saveStandardRootEdit = async () => {
  if (!editingStandardRoot.chinese_name) {
    ElMessage.warning('中文名称不能为空')
    return
  }
  if (!editingStandardRootId.value) {
    ElMessage.error('标准词根标识缺失')
    return
  }
  try {
    const payload = normalizeRootItem(editingStandardRoot)
    const response = await axios.put(`/api/standard-roots/${editingStandardRootId.value}`, payload)
    if (response.data.code === 0) {
      const updated = normalizeRootItem(response.data.data || payload)
      const index = standardRoots.value.findIndex(item => item.root_id === editingStandardRootId.value)
      if (index !== -1) {
        standardRoots.value[index] = updated
      }
      standardRootEditDialogVisible.value = false
      await loadGovernanceData()
      ElMessage.success('标准词根更新成功')
    } else {
      ElMessage.error(response.data.message || '标准词根更新失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || error.response?.data?.message || error.message || '标准词根更新失败')
  }
}

const removeStandardRoot = async (root) => {
  const normalized = normalizeRootItem(root)
  if (!normalized.root_id) {
    ElMessage.error('标准词根标识缺失')
    return
  }
  try {
    await axios.delete(`/api/standard-roots/${normalized.root_id}`)
    await loadGovernanceData()
    ElMessage.success('标准词根删除成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || error.response?.data?.message || error.message || '标准词根删除失败')
  }
}

const clearHistoricalRoots = async () => {
  try {
    await axios.delete('/api/historical-roots')
    historicalRoots.value = []
    ElMessage.success('历史词根已清除')
  } catch (error) {
    ElMessage.error('清除失败')
  }
}

const resetPrompt = async () => {
  try {
    const response = await axios.post('/api/custom-prompt/reset')
    if (response.data.code === 0 && response.data.data) {
      customPrompt.value = response.data.data
      ElMessage.success('已重置为内置默认提示词')
    } else {
      customPrompt.value = DEFAULT_PROMPT
      ElMessage.warning('重置失败，已使用本地默认提示词')
    }
  } catch (error) {
    console.error('重置提示词失败:', error)
    customPrompt.value = DEFAULT_PROMPT
    ElMessage.warning('重置失败，已使用本地默认提示词')
  }
}

const copySQL = async () => {
  if (!generatedSQL.value) return
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(generatedSQL.value)
      ElMessage.success('SQL 已复制到剪贴板')
    } else {
      const textArea = document.createElement('textarea')
      textArea.value = generatedSQL.value
      textArea.style.position = 'fixed'
      textArea.style.left = '-9999px'
      textArea.style.top = '-9999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      try {
        document.execCommand('copy')
        ElMessage.success('SQL 已复制到剪贴板')
      } catch (err) {
        ElMessage.error('复制失败，请手动复制')
      }
      document.body.removeChild(textArea)
    }
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动复制')
  }
}

const generateDDL = async () => {
  if (!llmConfig.apiKey) {
    ElMessage.warning('请先配置 LLM API Key')
    return
  }
  if (!description.value.trim()) {
    ElMessage.warning('请输入建表需求')
    return
  }

  generating.value = true
  generateStartTime.value = Date.now()
  generateDuration.value = 0
  currentDuration.value = 0
  
  if (timerInterval) {
    clearInterval(timerInterval)
  }
  timerInterval = setInterval(() => {
    currentDuration.value = Date.now() - generateStartTime.value
  }, 100)

  try {
    const response = await axios.post('/api/generate-ddl', {
        llm_config: {
          api_key: llmConfig.apiKey,
          api_url: llmConfig.apiUrl,
          model: llmConfig.model,
          temperature: llmConfig.temperature,
          abbr_max_len: llmConfig.abbrMaxLen,
          industry_context: llmConfig.industryContext || ''
        },
      word_roots_input: {
        type: 'text',
        content: ''
      },
      standards_input: {
        type: 'text',
        content: ''
      },
      description: description.value,
      db_type: dbType.value,
      custom_prompt: customPrompt.value,
      root_match_priority: rootMatchPriority.value,
      history_roots: [],
      enable_validation: enableValidation.value
    })

    const responseData = response.data || {}
    console.log('完整响应数据:', responseData)
    
    // 更健壮的DDL内容获取逻辑
    let ddlContent = ''
    if (responseData && typeof responseData === 'object') {
      ddlContent = responseData.data || ''
    }
    if (!ddlContent && responseData && typeof responseData === 'string') {
      ddlContent = responseData
    }
    console.log('提取的DDL内容:', ddlContent)
    generatedSQL.value = ddlContent

    if (responseData.code === 0 || ddlContent) {
      if (responseData.violations && responseData.violations.length > 0) {
        const errorCount = responseData.violations.filter(v => v.level === 'error').length
        const warnCount = responseData.violations.length - errorCount
        let msg = `生成完成，但存在 ${responseData.violations.length} 个违规`
        if (errorCount > 0) msg += `（${errorCount} 个错误`
        if (warnCount > 0) msg += `，${warnCount} 个警告`
        if (errorCount > 0) msg += `）`
        ElMessage.warning(msg)
        
        responseData.violations.forEach((v, i) => {
          console.log(`[${i + 1}] [${v.level}] ${v.rule}: ${v.message}`)
        })
      } else {
        ElMessage.success('DDL 生成成功')
      }

      if (responseData.extracted_roots && responseData.extracted_roots.length > 0) {
        singleNewRoots.value = responseData.extracted_roots
        ElMessage.info(`检测到 ${responseData.extracted_roots.length} 个新词根，请查看下方区域并手动保存`)
      } else {
        singleNewRoots.value = []
      }

      await loadGovernanceData()
    } else {
      singleNewRoots.value = []
      ElMessage.error(responseData.message || '生成失败')
    }
  } catch (error) {
    singleNewRoots.value = []
    ElMessage.error('请求异常: ' + (error.message || '未知错误'))
  } finally {
    generating.value = false
    if (timerInterval) {
      clearInterval(timerInterval)
      timerInterval = null
    }
    generateDuration.value = Date.now() - generateStartTime.value
    currentDuration.value = generateDuration.value
  }
}

watch(activeMenu, (menu) => {
  if (menu === 'governance') {
    loadGovernanceData()
  }
})

onMounted(() => {
  loadConfigs()
  loadStandards()
  loadHistory()
  loadDbConnections()
  loadGovernanceData()
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
}

body {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.app-wrapper {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 220px;
  background: linear-gradient(180deg, #304156 0%, #1a252f 100%);
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
}

.logo {
  padding: 24px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
}

.nav-menu {
  padding: 16px 0;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 14px 24px;
  color: rgba(255,255,255,0.7);
  cursor: pointer;
  transition: all 0.3s;
  gap: 12px;
}

.nav-item:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
}

.nav-item.active {
  background: linear-gradient(90deg, #409EFF 0%, #66b1ff 100%);
  color: #fff;
  border-left: 4px solid #fff;
}

.nav-icon {
  font-size: 18px;
}

.nav-text {
  font-size: 17px;
  font-weight: 500;
}

.main-container {
  flex: 1;
  margin-left: 220px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #F0F2F5;
  padding-bottom: 60px;
}

.header {
  height: 64px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.content {
  flex: 1;
  padding: 24px;
}

.config-view,
.ddl-view,
.governance-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
  animation: fadeIn 0.3s ease;
}

.governance-panels {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.governance-panel {
  flex: 1;
  min-width: 0;
}

.governance-panel-title {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
}

.governance-progress-card {
  margin-bottom: 16px;
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafafa;
}

.governance-progress-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.governance-progress-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
}

.governance-progress-detail {
  margin-bottom: 12px;
  padding: 8px 10px;
  border-radius: 6px;
  background: #f4f4f5;
  color: #303133;
  font-size: 13px;
  line-height: 1.5;
}

.governance-toolbar {
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.governance-search {
  width: 220px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.input-row {
  display: flex;
  gap: 20px;
}

.input-row .input-card {
  flex: 1;
}

.side-by-side-container {
  display: flex;
  gap: 20px;
}

.side-by-side-container .prompt-card {
  flex: 1;
  min-width: 300px;
}

.side-by-side-container .history-card {
  flex: 2;
  min-width: 500px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.timer-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.config-selector {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
}

.llm-form-container {
  display: flex;
  gap: 30px;
}

.llm-form-left {
  flex: 1;
}

.llm-form-left .llm-form {
  max-width: 600px;
}

.llm-form-right {
  flex: 1;
}

.temperature-section {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 10px;
  border: 1px solid #e4e7ed;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.temperature-config-horizontal {
  display: flex;
  align-items: center;
}

.temperature-hint {
  margin-top: 12px;
  font-size: 12px;
  color: #909399;
  line-height: 1.6;
}

.config-divider {
  height: 1px;
  margin: 16px 0;
  background: #dcdfe6;
}

.api-key-input {
  display: flex;
  align-items: center;
}

.api-key-saved {
  display: flex;
  align-items: center;
  gap: 12px;
}

.key-placeholder {
  color: #909399;
  font-size: 14px;
}

.upload-section {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}

.preview-table {
  margin-top: 16px;
}

.preview-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.custom-tabs :deep(.el-tabs__item) {
  font-size: 14px;
}

.ddl-input-section {
  display: flex;
  gap: 20px;
  align-items: stretch;
}

.ddl-input-section .requirement-card {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.ddl-input-section .requirement-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.ddl-input-section .new-roots-card {
  flex: 0 0 420px;
  display: flex;
  flex-direction: column;
}

.ddl-input-section .new-roots-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.ddl-config-row {
  display: flex;
  gap: 40px;
}

.config-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.config-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.requirement-card :deep(.el-textarea__inner) {
  font-size: 14px;
  line-height: 1.8;
}

.generate-action {
  margin-top: 20px;
  text-align: center;
}

.generate-btn {
  min-width: 180px;
  height: 48px;
  font-size: 16px;
  background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
  border: none;
}

.generate-btn:hover {
  background: linear-gradient(135deg, #85ce61 0%, #67C23A 100%);
}

.duration-display {
  margin-left: 20px;
  font-size: 16px;
  color: #909399;
  font-weight: 500;
}

.sql-container-header {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-bottom: 10px;
}

.history-execute-summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  color: #606266;
  font-size: 13px;
}

.execute-record-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.execute-record-text {
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.execute-record-empty {
  color: #909399;
}

.sql-container {
  background: #1e1e1e;
  border-radius: 8px;
  padding: 20px;
  overflow-x: auto;
}

.sql-output {
  color: #d4d4d4;
  font-family: 'Consolas', 'Monaco', 'JetBrains Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}

.sql-keyword {
  color: #569cd6;
  font-weight: 600;
}

.sql-string {
  color: #ce9178;
}

.sql-backtick {
  color: #dcdcaa;
}

.sql-comment {
  color: #6a9955;
  font-style: italic;
}

.sql-number {
  color: #b5cea8;
}

.history-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.root-tag {
  font-size: 13px;
}

.search-input {
  margin-bottom: 16px;
}

.batch-view {
  padding: 20px;
}

.batch-top-section {
  display: flex;
  gap: 20px;
  align-items: stretch;
}

.batch-top-section > .config-card {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.batch-top-section > .config-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.batch-top-section > .new-roots-card {
  flex: 0 0 35%;
  display: flex;
  flex-direction: column;
}

.batch-top-section > .new-roots-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.generation-mode-switch {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.text-input-card {
  margin-bottom: 16px;
}

.standards-view {
  padding: 20px;
  height: calc(100vh - 180px);
}

.standards-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.standards-list-card {
  flex: 0 0 35%;
  margin-bottom: 16px;
}

.standards-list {
  max-height: 200px;
  overflow-y: auto;
}

.standards-content {
  display: flex;
  flex: 1;
  gap: 16px;
}

.standards-editor-card {
  flex: 0 0 50%;
  display: flex;
  flex-direction: column;
}

.standards-editor-card .el-card__body {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.standards-editor-card .standards-edit-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.standards-editor-card .standards-textarea {
  flex: 1;
}

.standards-preview-card {
  flex: 0 0 50%;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 350px);
}

.standards-preview-card .el-card__body {
  flex: 1;
  overflow: hidden;
}

.standards-preview-container {
  height: 100%;
  overflow-y: auto;
  max-height: calc(100vh - 400px);
}

.preview-content {
  white-space: pre-wrap;
  word-break: break-all;
  padding: 10px;
}

.preview-content h1 {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #409EFF;
}

.preview-content h2 {
  font-size: 20px;
  font-weight: bold;
  margin-top: 16px;
  margin-bottom: 8px;
  color: #303133;
}

.preview-content h3 {
  font-size: 16px;
  font-weight: bold;
  margin-top: 12px;
  margin-bottom: 6px;
  color: #606266;
}

.preview-content p {
  margin-bottom: 8px;
  line-height: 1.6;
}

.preview-content ul,
.preview-content ol {
  padding-left: 24px;
  margin-bottom: 8px;
}

.preview-content li {
  margin-bottom: 4px;
}

.preview-content strong,
.preview-content b {
  font-weight: bold;
  color: #303133;
}

.preview-content table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
  font-size: 14px;
}

.preview-content th,
.preview-content td {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
  vertical-align: top;
}

.preview-content th {
  background-color: #f5f7fa;
  font-weight: bold;
  border-bottom: 2px solid #409EFF;
}

.preview-content tr:nth-child(even) {
  background-color: #fafafa;
}

.preview-content tr:hover {
  background-color: #eef5ff;
}

.preview-content .markdown-table {
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.preview-content .markdown-table th {
  color: #303133;
}

.preview-content .markdown-table td {
  color: #606266;
}

.batch-upload-section {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.batch-file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.batch-file-hint {
  color: #909399;
  font-size: 13px;
}

.batch-preview {
  margin-bottom: 16px;
}

.preview-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 12px;
  color: #303133;
}

.batch-config-row {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
}

.config-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-label {
  font-size: 14px;
  color: #606266;
}

.config-hint {
  font-size: 12px;
  color: #909399;
}

.batch-action {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.generate-btn {
  width: 200px;
  height: 44px;
  font-size: 16px;
}

.preview-card {
  margin-top: 16px;
}

.preview-card .sql-container {
  max-height: 400px;
  overflow-y: auto;
}

.result-card {
  margin-top: 20px;
}

.batch-result-stats {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.batch-errors {
  margin-bottom: 16px;
  padding: 12px;
  background: #fef0f0;
  border-radius: 8px;
  margin-bottom: 16px;
}

.error-title {
  color: #f56c6c;
  font-weight: 500;
  margin-bottom: 8px;
}

.error-item {
  color: #f56c6c;
  font-size: 13px;
  padding: 4px 0;
}

.validation-section {
  margin-bottom: 16px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.validation-stats {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
  margin-bottom: 8px;
  color: #374151;
}

.violations-list {
  max-height: 200px;
  overflow-y: auto;
}

.violation-item {
  display: flex;
  gap: 8px;
  padding: 6px 10px;
  margin-bottom: 4px;
  border-radius: 4px;
  font-size: 13px;
}

.violation-item.error {
  background: #fef2f2;
  color: #dc2626;
}

.violation-item.warning {
  background: #fffbeb;
  color: #d97706;
}

.violation-level {
  font-size: 14px;
}

.violations-more {
  text-align: center;
  padding: 8px;
  color: #6b7280;
  font-size: 12px;
}

.loading-spinner {
  animation: spin 1s linear infinite;
  display: inline-block;
  margin-right: 8px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.history-view {
  padding: 20px;
  height: calc(100vh - 180px);
  display: flex;
  flex-direction: column;
}

.history-view .config-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.history-view .config-card .el-card__body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.history-list .el-table {
  height: 100%;
}

.history-list .el-table :deep(.el-scrollbar__view) {
  height: 100%;
}

.history-list .el-table :deep(.el-scrollbar__wrap) {
  overflow-x: auto;
  overflow-y: auto;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.empty-history {
  padding: 40px;
}

.footer {
  position: fixed;
  bottom: 0;
  left: 220px;
  right: 0;
  height: 48px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 13px;
  border-top: 1px solid #ebeef5;
  z-index: 100;
}

.field-stats-section {
  margin-top: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.field-stats-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.field-stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.field-progress-section {
  margin-top: 16px;
  padding: 16px;
  background: linear-gradient(135deg, #f8fbff 0%, #eef6ff 100%);
  border-radius: 10px;
  border: 1px solid #d9ecff;
}

.field-progress-line {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 10px;
  color: #1f4e79;
  font-size: 13px;
}

.field-progress-line span {
  padding: 4px 8px;
  background: #fff;
  border-radius: 999px;
  border: 1px solid #d9ecff;
}

.field-progress-hint {
  margin-top: 8px;
  color: #606266;
  font-size: 12px;
}

.field-stat-item {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s;
}

.field-stat-item:hover {
  transform: translateY(-2px);
}

.field-stat-item.matched {
  border-top: 3px solid #67c23a;
}

.field-stat-item.llm {
  border-top: 3px solid #409eff;
}

.field-stat-item.total {
  border-top: 3px solid #909399;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.field-stat-item.matched .stat-value {
  color: #67c23a;
}

.field-stat-item.llm .stat-value {
  color: #409eff;
}

.field-stat-item.total .stat-value {
  color: #909399;
}

.stat-label {
  font-size: 13px;
  color: #606266;
}

:deep(.el-card) {
  border-radius: 12px;
  border: none;
}

:deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-button) {
  border-radius: 8px;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-tag) {
  border-radius: 6px;
}

.new-roots-card {
  margin-top: 20px;
  background: linear-gradient(135deg, #fff7e6 0%, #fffbf0 100%);
  border: 2px solid #e6a23c;
}

.new-roots-card :deep(.el-card__body) {
  padding: 16px;
}

.new-roots-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #e6a23c;
}

.new-roots-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.save-roots-btn {
  margin-left: auto;
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  border: none;
  color: white;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.3);
  transition: all 0.3s ease;
}

.save-roots-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.4);
}

.new-roots-list {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.milestone-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.milestone-track {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.milestone-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
}

.milestone-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 12px;
  transition: all 0.3s ease;
}

.milestone-circle.completed {
  background: #10b981;
  color: white;
}

.milestone-circle.active {
  background: #3b82f6;
  color: white;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
}

.milestone-circle.pending {
  background: #e5e7eb;
  color: #9ca3af;
}

.milestone-icon {
  font-size: 14px;
  margin-top: 6px;
}

.milestone-title {
  font-size: 11px;
  color: #6b7280;
  margin-top: 3px;
  text-align: center;
}

.milestone-sub {
  font-size: 10px;
  color: #3b82f6;
  margin-top: 2px;
}

.milestone-line {
  position: absolute;
  top: 16px;
  left: 50%;
  width: calc(100% - 32px);
  height: 2px;
  background: #e5e7eb;
  z-index: -1;
}

.line-fill {
  height: 100%;
  background: #10b981;
  width: 0;
  transition: width 0.5s ease;
}

.line-fill.completed {
  width: 100%;
}

</style>





