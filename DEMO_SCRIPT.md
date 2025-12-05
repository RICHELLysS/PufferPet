# 🎃 PufferPet Kiroween Hackathon 演示脚本

> *"欢迎来到深海亡灵帝国..."* — 深海代码船长 🦑

## 演示概述

**时长**: 5-10 分钟
**目标**: 展示 Kiro 原生功能（Steering、Agent Hooks）和万圣节创意特性

---

## 🎬 演示流程

### 第一幕：深海启航（1-2分钟）

#### 1.1 项目介绍

```
"PufferPet 是一个桌面宠物应用，让可爱的海洋生物陪伴你的工作。
V4 版本为 Kiroween Hackathon 打造，融入了深海亡灵帝国的万圣节主题。"
```

#### 1.2 启动应用

```bash
python main.py
```

**展示要点**:
- 🎃 万圣节暗黑主题自动应用
- 👻 宠物的幽灵滤镜效果
- 🌑 深紫黑色背景 + 幽灵绿文字

---

### 第二幕：Kiro Steering 展示（2-3分钟）

#### 2.1 打开 Steering 文件

```
文件位置: .kiro/steering.md
```

**展示要点**:
- 🦑 深海代码船长角色定义
- 📜 防御性编程规则
- 💀 戏剧性注释风格

#### 2.2 代码风格示例

打开 `theme_manager.py` 或 `ignore_tracker.py`，展示：

```python
# ⚠️ WARNING: 此处潜伏着数据腐化的诅咒...
# 任何试图绕过此验证的灵魂都将被深渊吞噬
```

```python
def summon_leviathan(pet_id: str) -> bool:
    """
    🐋 从深渊中召唤一只巨兽到屏幕上。
    
    此仪式将唤醒沉睡在库存深处的生物，
    使其显现于凡人的桌面之上。
    """
```

#### 2.3 错误处理风格

```python
raise ValueError(
    "🦑 深渊拒绝了你的祭品！"
    f"期望的宠物ID应在 {valid_ids} 之中..."
)
```

---

### 第三幕：Agent Hooks 概念（1-2分钟）

#### 3.1 打开 Hook 示例

```
文件位置: .kiro/hooks/pre-commit-example.md
```

**展示要点**:
- 🪝 Hook 触发条件（文件保存）
- 🦑 TODO 检测逻辑
- 😡 与桌面宠物的集成概念

#### 3.2 Hook 行为说明

```
"当检测到代码中的 TODO 注释时，
桌面宠物会根据数量显示不同级别的警告：

1-2 个: 🐚 海风中传来低语...
3-5 个: 🦑 深渊开始躁动...
6-10 个: 🐙 海怪苏醒了！
10+ 个: 🌊 触发捣蛋模式！"
```

---

### 第四幕：万圣节主题系统（1-2分钟）

#### 4.1 主题效果展示

**展示要点**:
- 🎃 暗黑主题 UI（右键菜单、任务窗口）
- 👻 幽灵滤镜效果（透明度 + 光晕）
- 🌑 黑底绿字橙边框风格

#### 4.2 图像加载优先级

```
万圣节模式下：
1. 尝试加载 halloween_idle.png
2. 回退到普通图像 + 幽灵滤镜
3. 最后使用占位符
```

---

### 第五幕：捣蛋机制（1-2分钟）

#### 5.1 机制说明

```
"如果你忽视宠物超过1小时，
它们会进入愤怒状态，开始疯狂抖动！
这就是'不给糖就捣蛋'机制。"
```

#### 5.2 演示愤怒状态

**方法一**: 等待1小时（不推荐）

**方法二**: 临时修改代码演示
```python
# 在 ignore_tracker.py 中临时修改
self.ignore_threshold = 10  # 改为10秒用于演示
```

**展示要点**:
- 😡 宠物进入愤怒状态
- 🔄 抖动动画效果
- 👆 点击安抚宠物
- 📢 "不给糖就捣蛋！"通知

---

### 第六幕：完整生态系统（1-2分钟）

#### 6.1 任务奖励系统

```
"每完成12个任务，触发奖励判定：
- 70% 概率获得 Tier 2 稀有宠物
- 30% 概率获得深海盲盒"
```

#### 6.2 库存管理

- 打开宠物管理窗口
- 展示召唤/潜水功能
- 展示库存状态（X/20, X/5）

#### 6.3 多宠物显示

- 同时显示多只宠物
- 展示 Tier 3 巨兽的缩放效果

---

## 📊 演示数据准备

### 预设数据文件

创建 `demo_data.json` 用于演示：

```json
{
  "version": 4.0,
  "theme_mode": "halloween",
  "unlocked_pets": ["puffer", "jelly", "starfish", "crab", "octopus", "blobfish"],
  "active_pets": ["puffer", "jelly", "blobfish"],
  "pet_tiers": {
    "tier1": ["puffer", "jelly", "starfish", "crab"],
    "tier2": ["octopus", "ribbon", "sunfish", "angler"],
    "tier3": ["blobfish", "ray", "beluga", "orca", "shark", "bluewhale"]
  },
  "reward_system": {
    "cumulative_tasks_completed": 11,
    "reward_threshold": 12
  },
  "pets_data": {
    "puffer": {
      "level": 3,
      "tasks_completed_today": 2,
      "task_states": [true, true, false]
    },
    "jelly": {
      "level": 2,
      "tasks_completed_today": 1,
      "task_states": [true, false, false]
    },
    "blobfish": {
      "level": 1,
      "tasks_completed_today": 0,
      "task_states": [false, false, false]
    }
  }
}
```

### 使用演示数据

```bash
# 备份当前数据
cp data.json data.json.backup

# 使用演示数据
cp demo_data.json data.json

# 启动应用
python main.py

# 演示结束后恢复
cp data.json.backup data.json
```

---

## 🎯 关键演示场景

### 场景1：展示 Steering 风格代码

```python
# 打开 theme_manager.py，展示以下代码：

class ThemeManager:
    """
    🎃 万圣节主题管理器 - 深海亡灵帝国的视觉诅咒。
    
    此模块掌管着所有视觉效果的命运：
    - 主题切换：在光明与黑暗之间穿梭
    - 幽灵滤镜：为生物披上亡灵的外衣
    - 暗黑样式：让UI沉入深渊的怀抱
    
    ⚠️ 警告：不当使用可能导致视觉诅咒蔓延...
    """
```

### 场景2：展示错误处理

```python
# 触发一个错误，展示戏剧性的错误消息
# 例如尝试加载不存在的宠物

# 预期输出：
# 🦑 深渊拒绝了你的祭品！
# 期望的宠物ID应在 [...] 之中...
```

### 场景3：展示捣蛋模式

```python
# 临时修改 ignore_tracker.py 用于演示
# 将 ignore_threshold 改为 10 秒

# 等待10秒后：
# - 所有宠物开始抖动
# - 显示"不给糖就捣蛋！"通知
# - 点击宠物安抚
```

---

## 📝 演示话术模板

### 开场白

```
"大家好！今天我要展示的是 PufferPet V4 - 
为 Kiroween Hackathon 打造的深海亡灵帝国版本。

这个项目不仅是一个可爱的桌面宠物应用，
更是 Kiro 原生功能的完美展示：
- Steering 定义了深海代码船长的代码风格
- Agent Hooks 展示了与桌面宠物集成的可能性
- 万圣节主题和捣蛋机制增添了节日趣味"
```

### 结束语

```
"感谢观看！PufferPet V4 展示了如何将 Kiro 的
Steering 和 Agent Hooks 功能融入实际项目，
同时通过万圣节主题和捣蛋机制增添创意和趣味。

愿深渊的智慧指引你的代码，
愿海神的祝福保护你的应用！

— 深海代码船长 🦑"
```

---

## ⚠️ 演示注意事项

1. **提前测试**: 确保所有功能正常工作
2. **备份数据**: 演示前备份 data.json
3. **网络环境**: 确保演示环境稳定
4. **时间控制**: 每个部分控制在预定时间内
5. **互动准备**: 准备好回答评委问题

---

*"从深渊的最深处，我们编织代码的诅咒..."* 🦑🎃
