# Project Agent Notes

## 项目定位
数仓建表 AI 助手，基于 FastAPI + Vue 3 + Element Plus 的 DDL 生成工作台。

## 当前核心边界
- 单表生成只输出 DDL 和校验结果，不直接执行数据库写入。
- 历史记录中的 DDL 才允许绑定数据库连接并执行。
- 批量生成走字段级处理流程，不是简单逐表整包 LLM 调用。

## 技术栈
- 后端：Python, FastAPI, Pydantic, requests, openpyxl, jieba
- 前端：Vue 3, Vite, Element Plus, Axios, xlsx
- 打包：PyInstaller 相关 spec 和 `Package-AI-WarHouse.ps1`

## 关键入口
- 后端主入口：`backend/app/main.py`
- 批量字段处理：`backend/app/processors/field_processor.py`
- 数据模型：`backend/app/models.py`
- 前端主界面：`frontend/src/App.vue`
- 前端构建配置：`frontend/package.json`

## 关键能力
- LLM 配置与连接测试
- 单表 DDL 生成
- Excel 批量建表
- 词根库管理
- 开发规范管理
- 自定义提示词管理
- 数据库连接管理
- DDL 历史查询、下载、执行
- 任务进度查询与取消

## 关键数据文件
- `backend/word_roots.json`
- `backend/custom_prompt.txt`
- `backend/dev_standards.json`
- `backend/standards/`
- `backend/ddl_history.json`
- `backend/db_connections.json`
- `backend/db_secret.key`
- `backend/builtin/default_prompt.txt`
- `backend/builtin/default_standards.md`

## 关键 API
- `/api/generate-ddl`
- `/api/batch-generate-ddl`
- `/api/word-roots`
- `/api/history-fields`
- `/api/standards`
- `/api/custom-prompt`
- `/api/db-connections`
- `/api/ddl-history`
- `/api/ddl-history/{record_id}/execute`
- `/api/progress/{task_id}`

## 生成链路要点
- 单表链路会加载系统规范、自定义提示词、词根库和数据库示例。
- 批量链路先做字段分组，再按命中程度分层处理。
- 新词根会在生成后回写，供后续复用。
- 校验失败时会走统一修正逻辑。

## 实施注意
- 先确认当前是单表还是批量链路，再改提示词或规范加载。
- 改默认提示词时，要同时关注后端文件、内置 fallback 和前端默认文案。
- 改命名规则时，要同步检查词根优先级和表名修复逻辑。
- 改历史执行时，要保留“生成”和“执行”两条流程的边界。

## 常用验证
- 后端接口与生成链路优先看 `backend/app/main.py`
- 批量字段命名与修复优先看 `backend/app/processors/field_processor.py`
- UI 入口和配置项优先看 `frontend/src/App.vue`

## 后续默认工作方式
- 新需求先查这份笔记，再决定是否需要全仓扫描。
- 如果只改文档、说明或产品边界，优先补充这里，不动业务代码。


--------------------------------------------------------------
# 全局代理规则

## 启动前必做

目的：把全局约束从“知道”变成“每次任务开始前都执行”的固定动作。

### 强制要求

- 每一次新任务开启之前，必须先读取本文件并按本文件执行，不得跳过。
- 如果当前线程或项目里还存在额外的 `AGENTS.md`、系统消息、开发者消息或工具 schema 约束，必须在读取本文件后继续读取并同时遵守。
- 任何时候如果发现本文件规则与当前线程真实暴露的工具 schema 不一致，以当前线程真实工具列表和 schema 为最终准绳。
- 在尚未确认当前线程工具名、字段名、可用性之前，不得凭记忆直接调用工具。
- 如果某条规则在当前线程无法执行，必须立即降级到更保守、确定可行的做法，而不是继续试错。

## 所有任务核心原则

- 一定要阅读，并按照  [$karpathy-guidelines] skill 执行，路径是：(C:\\Users\\XGKK\\.codex\\skills\\karpathy-guidelines\\SKILL.md) 
## 并行工具使用规范

目的：避免在任意项目或线程里再次把 `multi_tool_use.parallel` 调错。

### 结论

常见错误不是“并行工具不稳定”，而是调用契约错误：

1. `recipient_name` 写错
2. 目标工具不存在
3. `parameters` 为空或字段名不匹配
4. 把某个环境的旧字段名或旧工具名硬套到当前线程，例如混用 `exec_command/cmd` 与 `shell_command/command`

### 全局优先原则

并行读取文件、搜索文本、查看状态时，优先使用：

- `multi_tool_use.parallel`
- 当前线程真实暴露、且可被 `multi_tool_use.parallel` 调用的读取类工具

不要把任意工具名写死为全局唯一选择。每个线程调用前必须以当前可用工具列表和该工具 schema 为准。

### 当前线程示例

如果当前线程暴露的是 `functions.exec_command`，它的命令字段是 `cmd`，正确模板如下：

```json
{
  "tool_uses": [
    {
      "recipient_name": "functions.exec_command",
      "parameters": {
        "cmd": "Get-Content backend\\app\\main.py -Encoding UTF8 -TotalCount 20",
        "workdir": "D:\\Data\\Trae\\AutoDW-Trae1.0",
        "shell": "powershell",
        "login": false,
        "yield_time_ms": 10000,
        "max_output_tokens": 12000
      }
    },
    {
      "recipient_name": "functions.exec_command",
      "parameters": {
        "cmd": "Get-Content backend\\app\\models.py -Encoding UTF8 -TotalCount 60",
        "workdir": "D:\\Data\\Trae\\AutoDW-Trae1.0",
        "shell": "powershell",
        "login": false,
        "yield_time_ms": 10000,
        "max_output_tokens": 12000
      }
    }
  ]
}
```

如果当前线程暴露的是 `functions.shell_command`，且它的 schema 使用 `command` 字段，则使用 `functions.shell_command` + `command`。不要在没有该工具时调用它。

### 调用前检查清单

每次用 `multi_tool_use.parallel` 前，先检查：

- `recipient_name` 是否是当前线程真实可用的工具名
- 目标工具是否允许被 `multi_tool_use.parallel` 调用
- `parameters` 是否不是空对象
- `parameters` 字段名是否严格匹配目标工具 schema，例如 `exec_command` 用 `cmd`，`shell_command` 用 `command`
- 每个并行项是否都是独立、可并行、互不依赖的读取或查询操作
- 不要把多个命令硬塞进一个假工具字段
- 不要调用 `functions.unknown_tool` 或任何当前线程不存在的工具

### 常见错误示例

错误 1：工具名不存在

```json
{
  "recipient_name": "functions.unknown_tool",
  "parameters": {
    "command": "Get-Content backend\\app\\main.py"
  }
}
```

错误 2：参数为空

```json
{
  "recipient_name": "functions.exec_command",
  "parameters": {}
}
```

错误 3：字段名错了

```json
{
  "recipient_name": "functions.exec_command",
  "parameters": {
    "command": "Get-Content backend\\app\\main.py"
  }
}
```

错误 4：把另一个环境的工具名硬套到当前线程

```json
{
  "recipient_name": "functions.shell_command",
  "parameters": {
    "command": "Get-Content backend\\app\\main.py"
  }
}
```

当当前线程并没有暴露 `functions.shell_command` 时，上述调用就是错误的；应改用当前线程真实可用的工具和字段。

### 适用范围

这份规范约束所有后续仓库、线程和人工/代理调用习惯，不改业务代码逻辑。

## 全局工具调用范式

### 统一原则

- 调用任何工具前，先以当前线程真实暴露的工具列表和 schema 为准，不沿用其他线程、其他环境或旧版本提示里的字段名。
- `functions.exec_command` 的命令字段固定使用 `cmd`，不要写成 `command`、`shell_command` 或其他变体。
- 当前环境如果已经明确禁止传 `sandbox_permissions`，就不要在任何调用里附带这个字段。
- 只把互不依赖、只读或纯查询的操作放进 `multi_tool_use.parallel`；有先后依赖、会改状态、或需要共享中间结果的步骤必须串行执行。

### 并行前校验

- `recipient_name` 是否是当前线程真实可用的工具名。
- `parameters` 是否非空，且字段名与目标工具 schema 完全一致。
- 每个并行项是否彼此独立，不会因顺序变化而影响结果。
- 是否存在写入、删除、状态变更或对上一步输出的依赖。

### 并行失败后的强制策略

- `multi_tool_use.parallel` 只要首次失败，就先停止继续拼新的并行调用。
- 首次失败后，必须先回到当前线程真实可用工具和 schema，逐项复核 `recipient_name`、字段名、`parameters` 非空、步骤独立性。
- 如果复核后仍需并行，下一次只允许发送“最小合法样例”：2 个独立只读并行项，不得一次提交复杂大批量并行。
- 禁止在失败后继续猜测不存在的工具名、伪造包装字段、传空参数对象，或把多条命令塞进一个伪字段。

### 最小合法样例原则

- 第一次在一个线程里使用 `multi_tool_use.parallel`，优先从 2 个独立只读操作开始验证。
- 只有最小样例成功后，才允许扩展到更多并行项。
- 读取文件、搜索文本、查看状态适合最小样例验证；编辑、写入、删除、依赖上一步结果的步骤不适合。
- 如果串行已经足够快或上下文很小，不必为了并行而并行。

### 失败优先排查

- 先检查工具名。
- 再检查字段名。
- 再检查权限字段。
- 再判断是否适合并行。
- 只有这些都正确时，再怀疑业务逻辑。

### 参考示例

- 当前线程如果暴露的是 `functions.exec_command`，正确参数名是 `cmd`，示例：

```json
{
  "tool_uses": [
    {
      "recipient_name": "functions.exec_command",
      "parameters": {
        "cmd": "Get-Content backend\\app\\main.py -Encoding UTF8 -TotalCount 20",
        "workdir": "D:\\Data\\Trae\\AutoDW-Trae1.0",
        "shell": "powershell",
        "login": false,
        "yield_time_ms": 10000,
        "max_output_tokens": 12000
      }
    },
    {
      "recipient_name": "functions.exec_command",
      "parameters": {
        "cmd": "Get-Content backend\\app\\models.py -Encoding UTF8 -TotalCount 60",
        "workdir": "D:\\Data\\Trae\\AutoDW-Trae1.0",
        "shell": "powershell",
        "login": false,
        "yield_time_ms": 10000,
        "max_output_tokens": 12000
      }
    }
  ]
}
```

- 如果某个环境实际暴露的是 `functions.shell_command`，且它的 schema 使用 `command` 字段，只能在那个环境里按那个 schema 调用，不能把它硬套到当前线程。

### 常见误用

- 把旧环境里的 `shell_command/command` 写法硬套到当前线程。
- 把需要顺序执行的操作放进并行包装器。
- 给并行项塞空参数或不完整参数。
- 在没有确认工具可用时，直接猜测 `recipient_name`。
