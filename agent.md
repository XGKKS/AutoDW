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
