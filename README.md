
# 数仓建表AI助手 v1.0

## 项目概述

数仓建表AI助手是一款基于大语言模型（LLM）的智能数仓表结构生成工具，帮助数据工程师快速生成符合命名规范的数据库表结构定义（DDL）。

### 核心特性

- 🚀 **智能DDL生成**: 基于业务描述自动生成规范化的表结构
- 📋 **三层校验机制**: 生成 → 校验 → 自动修正的闭环流程
- 🔧 **多数据库支持**: MySQL / PostgreSQL / Oracle
- 📁 **批量建表功能**: 支持Excel/Word批量文件处理
- 📊 **词根匹配优化**: 71条业务词根智能匹配
- 📝 **规范管理**: 支持自定义开发规范
- 🔌 **零依赖部署**: 单EXE文件，开箱即用

## 项目架构

```
数仓AI助手-Trae1.0/
├── backend/              # 后端服务
│   ├── app/             # 核心应用
│   │   ├── main.py      # FastAPI主入口
│   │   ├── models.py    # 数据模型定义
│   │   ├── config/      # 配置模块
│   │   └── validators/  # DDL校验模块
│   ├── start.py         # 启动脚本
│   ├── requirements.txt # 依赖声明
│   └── logs/            # 日志目录
├── frontend/            # 前端应用
│   ├── src/
│   │   └── App.vue      # 主界面
│   └── dist/            # 构建产物
├── standards/           # 规范文件
├── custom_prompt.txt    # 自定义提示词
├── word_roots.json      # 词根数据
├── dev_standards.json   # 开发规范
└── dist/                # 打包输出
    └── DW_Backend_Service/
```

## 启动方式

### 1. 本地开发模式（推荐）

使用 `SmartLauncher.bat` 同时启动前后端：

```bash
# 双击运行
SmartLauncher.bat
```

访问地址: `http://localhost:5173` (Vite开发服务器)

### 2. 快速启动模式

使用 `启动助手.bat` 直接启动后端：

```bash
# 双击运行
启动助手.bat
```

访问地址: `http://localhost:8000`

### 3. 首次环境配置

使用 `EnvSetup.bat` 检查并配置环境：

```bash
# 双击运行
EnvSetup.bat
```

### 4. 独立部署模式

使用打包后的可执行文件：

```bash
# 进入目录
cd dist/DW_Backend_Service

# 双击运行
DW_AI_Backend.exe
```

访问地址: `http://localhost:8000`

## 功能介绍

### 1. 单一建表

**功能说明**: 根据业务描述生成单个表的DDL语句

**配置参数**:
- 数据库类型: MySQL / PostgreSQL / Oracle
- 三层校验: 开启/关闭（关闭可提升速度）
- 词根匹配优先级: 完整匹配 / 缩写匹配
- 历史词根选择: 复用历史生成的词根

**输入示例**:
```
业务描述: 用户订单表，存储用户下单信息，包含订单号、用户ID、商品ID、下单时间、订单金额等字段
```

**输出示例**:
```sql
CREATE TABLE t_order (
