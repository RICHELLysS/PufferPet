# 🦑 深海 TODO 追踪 Hook

> *"未完成的任务如同沉船中的幽灵，终将回来纠缠你..."*

## Hook 概述

此 Agent Hook 示例展示了如何在代码提交前检查 TODO 注释，并通过桌面宠物发出警告。当检测到未完成的任务时，你的深海宠物将会愤怒地提醒你！

## 触发条件

- **事件类型**: 文件保存 (on-file-save)
- **文件模式**: `*.py` (Python 文件)
- **检查内容**: TODO、FIXME、HACK、XXX 注释

## Hook 配置示例

```json
{
  "name": "deep-sea-todo-tracker",
  "description": "🦑 深海 TODO 追踪器 - 让你的宠物监视未完成的任务",
  "trigger": {
    "event": "on-file-save",
    "filePattern": "*.py"
  },
  "action": {
    "type": "agent-message",
    "message": "检查文件中的 TODO 注释，如果发现未完成任务，触发宠物警告"
  }
}
```

## 行为说明

### 1. 检测阶段 🔍

当用户保存 Python 文件时，Hook 将扫描文件内容，寻找以下标记：

```python
# TODO: 这是一个待办事项
# FIXME: 这里需要修复
# HACK: 临时解决方案
# XXX: 需要注意的问题
```

### 2. 警告阶段 ⚠️

如果检测到 TODO 注释，桌面宠物将显示警告气泡：

```
🦑 "深渊的低语..."

"船长发现了 {count} 个未完成的诅咒！"
"这些 TODO 如同沉船中的幽灵，"
"终将回来纠缠你的代码..."

[查看详情] [稍后提醒] [忽略]
```

### 3. 诅咒消息示例 💀

根据 TODO 数量，宠物会显示不同级别的警告：

| TODO 数量 | 警告级别 | 消息 |
|-----------|----------|------|
| 1-2 | 轻微 | "🐚 海风中传来低语...有 {n} 个任务等待完成" |
| 3-5 | 中等 | "🦑 深渊开始躁动...{n} 个未完成的诅咒正在积累" |
| 6-10 | 严重 | "🐙 海怪苏醒了！{n} 个 TODO 正在威胁你的代码！" |
| 10+ | 危险 | "🌊 灾难降临！{n} 个未完成任务将把你的项目拖入深渊！" |

## 与桌面宠物的集成

### 宠物反应

当 Hook 触发时，桌面宠物可以表现出以下行为：

1. **轻微警告**: 宠物轻轻摇晃，显示思考表情
2. **中等警告**: 宠物开始游动，显示担忧表情
3. **严重警告**: 宠物快速抖动，显示愤怒表情
4. **危险警告**: 触发"捣蛋模式"，所有宠物进入愤怒状态

### 代码集成示例

```python
# 在 pet_widget.py 中添加 Hook 响应方法

def on_todo_detected(self, todo_count: int, todos: list):
    """
    🦑 当检测到 TODO 时触发的深渊警告。
    
    此方法响应 Agent Hook 的调用，
    让桌面宠物对未完成的任务发出警告。
    
    Args:
        todo_count: 检测到的 TODO 数量
        todos: TODO 详情列表
    """
    if todo_count >= 10:
        # 触发捣蛋模式
        self.trigger_mischief_mode()
        self.show_warning_bubble(
            "🌊 灾难降临！\n"
            f"{todo_count} 个未完成任务\n"
            "将把你的项目拖入深渊！"
        )
    elif todo_count >= 6:
        self.set_angry(True)
        self.show_warning_bubble(
            "🐙 海怪苏醒了！\n"
            f"{todo_count} 个 TODO\n"
            "正在威胁你的代码！"
        )
    elif todo_count >= 3:
        self.show_warning_bubble(
            "🦑 深渊开始躁动...\n"
            f"{todo_count} 个未完成的诅咒\n"
            "正在积累"
        )
    else:
        self.show_warning_bubble(
            "🐚 海风中传来低语...\n"
            f"有 {todo_count} 个任务\n"
            "等待完成"
        )
```

## 扩展可能性

### 其他 Hook 创意

1. **深海代码审查 Hook**
   - 触发：Pull Request 创建
   - 行为：宠物检查代码质量，给出深海风格的建议

2. **测试守护者 Hook**
   - 触发：测试失败
   - 行为：宠物显示悲伤表情，鼓励修复测试

3. **构建监视者 Hook**
   - 触发：构建完成
   - 行为：成功时宠物庆祝，失败时宠物警告

4. **深夜编码警告 Hook**
   - 触发：深夜时段保存文件
   - 行为：宠物提醒开发者注意休息

## 配置说明

### 启用 Hook

1. 确保 `.kiro/hooks/` 目录存在
2. 创建 Hook 配置文件（JSON 格式）
3. 在 Kiro 设置中启用 Agent Hooks
4. 重启应用以加载新的 Hook

### 自定义消息

可以在配置文件中自定义警告消息：

```json
{
  "messages": {
    "mild": "🐚 {count} 个小任务在等你...",
    "moderate": "🦑 {count} 个诅咒正在积累...",
    "severe": "🐙 {count} 个海怪正在苏醒！",
    "critical": "🌊 {count} 个灾难即将降临！"
  }
}
```

---

## 注意事项

⚠️ **此文件是 Hook 功能的概念展示文档**

实际的 Hook 实现需要：
1. Kiro IDE 的 Agent Hooks 功能支持
2. 桌面宠物应用的 API 接口
3. 进程间通信机制

本文档旨在展示 Kiro Agent Hooks 与桌面宠物集成的可能性，
为 Kiroween Hackathon 提供创意参考。

---

*"让你的深海宠物成为代码质量的守护者..."*

— 深海代码船长 🦑
