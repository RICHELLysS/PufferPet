# Design Document: V8 Final Polish for Hackathon

## Overview

V8 是为 Hackathon 展示优化的最终版本，基于 V7.1 进行关键修改：
1. **简化昼夜系统** - 移除 TimeManager 自动时间检测，仅保留手动切换
2. **优化盲盒触发** - 宠物成年时立即触发盲盒奖励
3. **鳐鱼 SSR 特殊机制** - 更高成长难度（5 任务 vs 3 任务）
4. **新手引导气泡系统** - QPainter.drawText 绘制文字气泡帮助用户理解玩法

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      main.py (Application)                   │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  PufferPetApp                                           ││
│  │  - 移除 TimeManager 自动同步 (auto_sync=False)          ││
│  │  - 简化 settings_menu (移除 Auto Day/Night 选项)        ││
│  │  - 保留手动 _toggle_day_night()                         ││
│  │  - 默认启动 Day Mode ("normal")                         ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ logic_growth.py │ │   pet_core.py   │ │   ui_gacha.py   │
│                 │ │                 │ │                 │
│ - TASK_CONFIG   │ │ - 引导气泡绘制  │ │ - V8概率分布    │
│ - Ray特殊任务数 │ │ - paintEvent    │ │ - 22%/12%       │
│ - get_tasks_to_ │ │ - drawText      │ │                 │
│   next_state()  │ │ - TUTORIAL_     │ │                 │
│                 │ │   BUBBLES       │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Components and Interfaces

### 1. main.py (简化昼夜系统)

**修改点：**
- 移除 `create_settings_menu` 中的 Auto Day/Night 选项
- 简化为仅保留手动切换按钮
- 默认 `auto_sync=False`

```python
def create_settings_menu(app, time_manager, theme_manager):
    """V8: 简化设置菜单，仅保留手动切换"""
    menu = QMenu("⚙️ 设置 / Settings")
    
    # V8: 移除 auto_sync_action，仅保留手动切换
    toggle_action = QAction("🌓 切换 昼/夜 (Toggle Day/Night)", menu)
    toggle_action.triggered.connect(lambda: on_toggle_day_night(time_manager))
    menu.addAction(toggle_action)
    
    return menu

class PufferPetApp:
    def __init__(self):
        # V8: 禁用 TimeManager 自动同步
        self.time_manager = TimeManager(theme_manager=self.theme_manager)
        self.time_manager.set_auto_sync(False)  # 关键：禁用自动同步
        
        # V8: 默认 Day Mode
        self.growth_manager.set_theme_mode("normal")
```

### 2. logic_growth.py (鳐鱼特殊机制)

**新增：**
- `TASK_CONFIG` 常量定义任务数配置
- `get_tasks_to_next_state()` 方法返回到下一状态需要的任务数

```python
class GrowthManager:
    # V8: 任务数配置
    TASK_CONFIG = {
        "ray": {
            "dormant_to_baby": 2,  # 唤醒需要2个任务
            "baby_to_adult": 3,    # 成年需要再3个任务 (共5个)
        },
        "default": {
            "dormant_to_baby": 1,  # 唤醒需要1个任务
            "baby_to_adult": 2,    # 成年需要再2个任务 (共3个)
        }
    }
    
    def get_tasks_to_next_state(self, pet_id: str) -> int:
        """
        V8: 获取到下一状态需要的任务数
        
        Args:
            pet_id: 宠物ID
            
        Returns:
            需要的任务数 (Ray 返回 2/3, 其他返回 1/2)
        """
        state = self.get_state(pet_id)
        
        # 获取配置 (ray 用特殊配置，其他用 default)
        config_key = "ray" if pet_id == "ray" else "default"
        config = self.TASK_CONFIG[config_key]
        
        if state == 0:  # dormant -> baby
            return config["dormant_to_baby"]
        elif state == 1:  # baby -> adult
            return config["baby_to_adult"]
        return 0  # adult 状态无需更多任务
```

### 3. pet_core.py (引导气泡系统)

**新增：**
- `TUTORIAL_BUBBLES` 常量定义引导文字
- `get_tutorial_text()` 方法返回当前应显示的引导文字
- `_draw_tutorial_bubble()` 方法使用 QPainter 绘制气泡
- `paintEvent()` 中调用气泡绘制

```python
class PetWidget:
    # V8: 引导气泡配置
    TUTORIAL_BUBBLES = {
        "dormant": "右键点击我！\n(Right Click Me!)",
        "just_awakened": "试试拖拽我！\n(Try Dragging!)",
        "idle_hint": "连点5下有惊喜！\n(Click 5x for Anger!)",
    }
    
    def __init__(self, ...):
        # V8: 引导状态
        self.just_awakened = False
        self.just_awakened_timer: Optional[QTimer] = None
        self.idle_hint_timer: Optional[QTimer] = None
        self.show_idle_hint = False
    
    def get_tutorial_text(self) -> str:
        """V8: 获取当前应显示的引导文字"""
        if self.is_dormant:
            return self.TUTORIAL_BUBBLES["dormant"]
        elif self.just_awakened:
            return self.TUTORIAL_BUBBLES["just_awakened"]
        elif self.show_idle_hint:
            return self.TUTORIAL_BUBBLES["idle_hint"]
        return ""
    
    def _draw_tutorial_bubble(self, painter: QPainter, text: str):
        """
        V8: 绘制引导文字气泡
        
        - 位置：宠物头顶上方
        - 背景：半透明黑色圆角矩形
        - 文字：黄色 (#FFFF00) + 黑色描边
        """
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        
        # 计算文字尺寸
        fm = painter.fontMetrics()
        lines = text.split('\n')
        text_width = max(fm.horizontalAdvance(line) for line in lines)
        text_height = fm.height() * len(lines)
        
        # 气泡位置（宠物上方）
        bubble_padding = 8
        bubble_width = text_width + bubble_padding * 2
        bubble_height = text_height + bubble_padding * 2
        bubble_x = (self.width() - bubble_width) // 2
        bubble_y = -bubble_height - 5  # 宠物上方
        
        # 绘制半透明黑色背景
        painter.setBrush(QColor(0, 0, 0, 180))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bubble_x, bubble_y, bubble_width, bubble_height, 5, 5)
        
        # 绘制文字描边（黑色）
        text_x = bubble_x + bubble_padding
        text_y = bubble_y + bubble_padding + fm.ascent()
        
        painter.setPen(QColor(0, 0, 0))
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            for i, line in enumerate(lines):
                painter.drawText(text_x + dx, text_y + i * fm.height() + dy, line)
        
        # 绘制文字（黄色）
        painter.setPen(QColor(255, 255, 0))  # #FFFF00
        for i, line in enumerate(lines):
            painter.drawText(text_x, text_y + i * fm.height(), line)
    
    def paintEvent(self, event):
        """V8: 绘制宠物和引导气泡"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制宠物图像
        if self.current_pixmap:
            # ... 现有绘制逻辑 ...
            pass
        
        # V8: 绘制引导气泡
        tutorial_text = self.get_tutorial_text()
        if tutorial_text:
            self._draw_tutorial_bubble(painter, tutorial_text)
        
        painter.end()
```

### 4. ui_gacha.py (V8 概率分布)

**修改点：**
- 更新 `GACHA_WEIGHTS` 为 V8 概率分布

```python
# V8: 盲盒概率分布
V8_GACHA_WEIGHTS = {
    "puffer": 22,
    "jelly": 22,
    "crab": 22,
    "starfish": 22,
    "ray": 12,  # SSR
}
# 总计: 100%
```

## Data Models

### 任务配置 (TASK_CONFIG)

```python
TASK_CONFIG = {
    "ray": {
        "dormant_to_baby": 2,  # 唤醒需要2个任务
        "baby_to_adult": 3,    # 成年需要再3个任务
        "total": 5,            # 从休眠到成年共5个任务
    },
    "default": {
        "dormant_to_baby": 1,  # 唤醒需要1个任务
        "baby_to_adult": 2,    # 成年需要再2个任务
        "total": 3,            # 从休眠到成年共3个任务
    }
}
```

### 引导气泡配置 (TUTORIAL_BUBBLES)

```python
TUTORIAL_BUBBLES = {
    "dormant": "右键点击我！\n(Right Click Me!)",
    "just_awakened": "试试拖拽我！\n(Try Dragging!)",
    "idle_hint": "连点5下有惊喜！\n(Click 5x for Anger!)",
}

TUTORIAL_CONFIG = {
    "awakened_duration": 10000,  # 10秒
    "idle_hint_interval": 30000,  # 30秒间隔
    "text_color": "#FFFF00",      # 黄色
    "outline_color": "#000000",   # 黑色描边
    "bg_color": "rgba(0,0,0,180)", # 半透明黑色背景
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Day/Night Toggle Round-Trip
*For any* current theme mode (normal or halloween), calling toggle_day_night() twice shall return to the original mode.
**Validates: Requirements 1.2**

### Property 2: Task Requirements Based on Pet Type and State
*For any* pet_id and state combination, get_tasks_to_next_state() shall return:
- Ray in state 0: 2
- Ray in state 1: 3
- Non-Ray in state 0: 1
- Non-Ray in state 1: 2
- Any pet in state 2: 0
**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

### Property 3: Gacha Probability Distribution
*For any* large number of gacha rolls (N > 1000), the distribution shall approximate: 22% each for puffer/jelly/crab/starfish, 12% for ray (within ±5% tolerance).
**Validates: Requirements 2.2**

### Property 4: Tutorial Text for Dormant State
*For any* pet in dormant state (state 0), get_tutorial_text() shall return a string containing "右键点击我" or "Right Click Me".
**Validates: Requirements 4.1**

### Property 5: Geometric Fallback Consistency
*For any* V7 pet_id (puffer, jelly, crab, starfish, ray) and any positive size, PetRenderer.draw_placeholder() shall return a non-null QPixmap with the correct shape from PET_SHAPES.
**Validates: Requirements 5.1, 5.2, 5.3, 5.4**

## Error Handling

| Error Scenario | Handling Strategy |
|----------------|-------------------|
| Invalid pet_id for task config | Use "default" config |
| Gacha roll out of range | Return "puffer" as fallback |
| Tutorial timer already running | Stop existing timer before starting new one |
| Missing image assets | Fall back to geometric placeholder |
| Inventory full on gacha | Display warning message, skip gacha |

## Testing Strategy

### Unit Tests
- Test toggle_day_night() switches modes correctly
- Test get_tasks_to_next_state() returns correct values for ray vs non-ray
- Test roll_gacha() returns valid pet IDs
- Test get_tutorial_text() returns correct strings for each state
- Test _draw_tutorial_bubble() draws with correct colors

### Property-Based Tests
使用 `hypothesis` 库进行属性测试：

1. **Property 1 Test**: 验证 toggle 切换逻辑（round-trip）
2. **Property 2 Test**: 验证 ray vs non-ray 任务数
3. **Property 3 Test**: 大量 roll 验证概率分布
4. **Property 4 Test**: 验证休眠状态引导文字内容
5. **Property 5 Test**: 验证所有 V7 宠物的几何回退

每个属性测试配置运行至少 100 次迭代。

测试文件格式：
```python
# tests/test_v8_properties.py
from hypothesis import given, settings
from hypothesis import strategies as st

# **Feature: v8-final-polish, Property 2: Task Requirements Based on Pet Type and State**
@given(state=st.integers(0, 2))
@settings(max_examples=100)
def test_ray_task_requirements(state):
    """Ray should require 2 tasks for awakening, 3 for adult"""
    gm = GrowthManager("test.json")
    gm.add_pet("ray")
    gm.pets["ray"].state = state
    tasks = gm.get_tasks_to_next_state("ray")
    
    if state == 0:
        assert tasks == 2
    elif state == 1:
        assert tasks == 3
    else:
        assert tasks == 0

# **Feature: v8-final-polish, Property 4: Tutorial Text for Dormant State**
@given(pet_id=st.sampled_from(["puffer", "jelly", "crab", "starfish", "ray"]))
@settings(max_examples=100)
def test_dormant_tutorial_text(pet_id):
    """Dormant pets should show 'Right Click Me' tutorial"""
    # Create pet widget in dormant state
    # Verify get_tutorial_text() contains expected text
    pass
```
