# V6 稳定版设计文档

## 概述

V6 版本的核心目标是**简化和稳定**。将代码整合为三个清晰的模块：
- `pet_core.py` - 宠物显示、动画、滤镜、拖拽
- `logic_growth.py` - 0→1→2 状态机和任务计数
- `main.py` - 程序入口和托盘菜单

## 架构

```
┌─────────────────────────────────────────────────────┐
│                    main.py                          │
│  - QApplication 初始化                              │
│  - 系统托盘菜单                                     │
│  - 昼夜模式切换                                     │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
┌───────▼───────┐         ┌─────────▼─────────┐
│  pet_core.py  │◄────────│  logic_growth.py  │
│               │         │                   │
│ - PetWidget   │         │ - GrowthManager   │
│ - 图像加载    │         │ - 状态机 0→1→2   │
│ - 滤镜效果    │         │ - 任务计数        │
│ - 拖拽交互    │         │ - 数据持久化      │
└───────────────┘         └───────────────────┘
```

## 组件和接口

### 1. PetWidget (pet_core.py)

```python
class PetWidget(QWidget):
    def __init__(self, pet_id: str, growth_manager: GrowthManager)
    def load_image(self) -> None  # 智能加载图像
    def apply_dormant_filter(self) -> None  # 应用休眠滤镜
    def remove_filter(self) -> None  # 移除滤镜
    def set_state(self, state: int) -> None  # 更新显示状态
    def start_floating(self) -> None  # 开始漂浮动画
    def stop_floating(self) -> None  # 停止漂浮
```

### 2. GrowthManager (logic_growth.py)

```python
class GrowthManager:
    def __init__(self, data_file: str = "data.json")
    def get_state(self, pet_id: str) -> int  # 获取宠物状态
    def get_progress(self, pet_id: str) -> int  # 获取任务进度
    def complete_task(self, pet_id: str) -> int  # 完成任务，返回新状态
    def reset_cycle(self, pet_id: str) -> None  # 重置周期
    def save(self) -> None  # 保存数据
```

### 3. 图像加载优先级

```
1. assets/{pet_id}/{stage}_idle.gif
2. assets/{pet_id}/{stage}_idle_0.png (序列帧)
3. assets/{pet_id}/{stage}_idle.png
4. 彩色椭圆占位符（带宠物名称）
```

## 数据模型

### data.json 结构

```json
{
  "pets": {
    "puffer": {
      "state": 0,
      "tasks_progress": 0
    },
    "jelly": {
      "state": 1,
      "tasks_progress": 2
    }
  },
  "settings": {
    "auto_time_sync": true,
    "theme_mode": "normal"
  }
}
```

## 正确性属性

*属性是系统在所有有效执行中应保持为真的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性是人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性 1: 状态转换正确性
*对于任意*宠物，状态只能按 0→1→2 的顺序转换，不能跳跃或倒退（除非重置）
**验证: 需求 1.5, 1.8**

### 属性 2: 任务进度与状态同步
*对于任意*宠物，当 tasks_progress=1 时状态至少为1，当 tasks_progress=3 时状态为2
**验证: 需求 2.3, 2.4**

### 属性 3: 图像加载回退
*对于任意*宠物ID，图像加载函数总是返回有效的可显示对象（图像或占位符）
**验证: 需求 3.1-3.4**

### 属性 4: 数据持久化往返
*对于任意*有效数据，保存后重新加载应得到等价的数据
**验证: 需求 2.5**

## 错误处理

- 所有文件操作使用 try-except 包裹
- 图像加载失败时生成占位符
- JSON 解析失败时使用默认数据
- 任何未捕获异常记录日志但不崩溃

## 测试策略

### 单元测试
- 状态转换逻辑
- 图像加载回退
- 数据持久化

### 属性测试 (Hypothesis)
- 状态机转换正确性
- 数据往返一致性
