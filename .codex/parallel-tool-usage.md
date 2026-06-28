# 并行工具使用规范

目的：避免在当前仓库/线程里再次把 `multi_tool_use.parallel` 调错。

## 结论

当前常见错误不是“并行工具不稳定”，而是调用契约错误：

1. `recipient_name` 写错
2. 目标工具不存在
3. `parameters` 为空或字段名不匹配
4. 把 `exec_command/cmd` 的旧写法混到 `shell_command/command`

## 当前线程优先用法

并行读取文件、搜索文本时，优先使用：

- `multi_tool_use.parallel`
- `functions.shell_command`

不要混用以下旧写法：

- `functions.exec_command`
- `cmd`
- `functions.unknown_tool`

## 正确调用模板

```json
{
  "tool_uses": [
    {
      "recipient_name": "functions.shell_command",
      "parameters": {
        "command": "Get-Content backend\\app\\main.py -Encoding UTF8 -TotalCount 20",
        "workdir": "D:\\Data\\Trae\\AutoDW-Trae1.0",
        "timeout_ms": 10000,
        "justification": "读取后端入口文件"
      }
    },
    {
      "recipient_name": "functions.shell_command",
      "parameters": {
        "command": "Get-Content backend\\app\\models.py -Encoding UTF8 -TotalCount 60",
        "workdir": "D:\\Data\\Trae\\AutoDW-Trae1.0",
        "timeout_ms": 10000,
        "justification": "读取数据模型定义"
      }
    }
  ]
}
```

## 调用前检查清单

每次用 `multi_tool_use.parallel` 前，先检查：

- `recipient_name` 是否是当前线程真实可用的工具名
- `parameters` 是否不是空对象
- `shell_command` 是否使用 `command` 字段，而不是 `cmd`
- 每个并行项是否都是独立、可并行、互不依赖的读取操作
- 不要把多个命令硬塞进一个假工具字段

## 常见错误示例

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
  "recipient_name": "functions.shell_command",
  "parameters": {}
}
```

错误 3：字段名错了

```json
{
  "recipient_name": "functions.shell_command",
  "parameters": {
    "cmd": "Get-Content backend\\app\\main.py"
  }
}
```

## 适用范围

这份规范只约束当前仓库里后续的人工/代理调用习惯，不改业务代码逻辑。
