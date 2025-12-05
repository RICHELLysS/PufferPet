# Design Document: Retro Minesweeper UI + Kiroween Horror Theme

## Overview

本设计实现 PufferPet 应用的真正复古扫雷风格UI和Kiroween恐怖主题。核心是更新 `ui_style.py` 模块，提供Windows 95风格的3D凸起/凹陷效果，并在夜晚模式下让宠物变成幽灵形态。

设计目标：
- Windows 95/扫雷游戏的经典3D按钮效果
- 经典灰色调配色方案
- Kiroween模式下的恐怖视觉效果
- 宠物在夜晚模式变成幽灵形态

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      main.py (Application)                   │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  PufferPetApp                                           ││
│  │  - app.setStyleSheet(get_stylesheet(mode))              ││
│  │  - _on_day_night_changed() → 刷新全局样式 + 宠物外观     ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   ui_style.py   │ │ theme_manager.py│ │   pet_core.py   │
│  (3D样式生成)   │ │  (幽灵滤镜)     │ │  (宠物渲染)     │
│                 │ │                 │ │                 │
│ get_stylesheet()│ │apply_ghost_     │ │PetRenderer.     │
│ get_palette()   │ │filter()         │ │draw_placeholder │
│ get_3d_borders()│ │get_spooky_color │ │_colored()       │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Components and Interfaces

### 1. ui_style.py (更新模块)

```python
# 核心接口
def get_palette(mode: str) -> dict:
    """
    获取指定模式的配色方案
    
    Args:
        mode: "normal" (扫雷风格) 或 "halloween" (Kiroween恐怖风格)
    
    Returns:
        包含以下颜色值的字典:
        - bg: 背景色
        - fg: 前景/文字色
        - button_face: 按钮表面色
        - button_light: 按钮高光色 (3D凸起左上)
        - button_dark: 按钮阴影色 (3D凸起右下)
        - accent: 强调色
        - border: 边框色
    """

def get_stylesheet(mode: str) -> str:
    """
    获取完整的QSS样式表，包含3D效果
    
    Args:
        mode: "normal" 或 "halloween"
    
    Returns:
        完整的QSS字符串，所有组件都有3D效果
    """

def get_3d_raised_border(light: str, dark: str) -> str:
    """
    生成3D凸起边框CSS
    
    Args:
        light: 高光色 (左上边框)
        dark: 阴影色 (右下边框)
    
    Returns:
        CSS border 属性字符串
    """

def get_3d_sunken_border(light: str, dark: str) -> str:
    """
    生成3D凹陷边框CSS (与凸起相反)
    """
```

### 2. theme_manager.py (更新模块)

```python
class ThemeManager:
    # 新增Kiroween恐怖颜色
    SPOOKY_COLORS = {
        'ghost_green': '#00FF88',
        'blood_red': '#FF0066',
        'pumpkin_orange': '#FF6600',
        'curse_purple': '#8B00FF',
    }
    
    def apply_ghost_filter(self, pixmap: QPixmap) -> QPixmap:
        """
        应用幽灵滤镜效果 (Kiroween模式)
        
        效果:
        - 降低透明度到60-70%
        - 添加绿色或紫色色调
        - 产生幽灵般的半透明效果
        """
    
    def get_spooky_color(self) -> str:
        """
        获取随机恐怖颜色 (用于宠物占位符)
        
        Returns:
            ghost_green 或 blood_red
        """
```

### 3. pet_core.py (更新模块)

```python
class PetRenderer:
    @staticmethod
    def draw_placeholder_spooky(pet_id: str, size: int) -> QPixmap:
        """
        绘制Kiroween模式的恐怖占位符
        
        使用幽灵绿或血红色，带有发光效果
        """

class PetWidget:
    def refresh_display(self) -> None:
        """
        刷新显示 - 根据主题模式应用不同效果
        
        - normal模式: 正常显示
        - halloween模式: 应用幽灵滤镜
        """
```

## Data Models

### 配色方案数据结构

```python
PALETTES = {
    "normal": {
        # Windows 95 扫雷风格
        "bg": "#C0C0C0",           # 经典灰色背景
        "fg": "#000000",           # 黑色文字
        "button_face": "#C0C0C0",  # 按钮表面
        "button_light": "#FFFFFF", # 3D高光 (白色)
        "button_dark": "#808080",  # 3D阴影 (深灰)
        "accent": "#000080",       # Windows蓝
        "border": "#000000",       # 黑色边框
        "highlight": "#DFDFDF",    # 悬停高亮
    },
    "halloween": {
        # Kiroween 恐怖风格
        "bg": "#1A0A1A",           # 深紫黑背景
        "fg": "#00FF88",           # 幽灵绿文字
        "button_face": "#2A1A2A",  # 暗紫按钮
        "button_light": "#8B00FF", # 紫色高光
        "button_dark": "#0D050D",  # 深黑阴影
        "accent": "#FF0066",       # 血红强调
        "border": "#8B00FF",       # 紫色边框
        "highlight": "#FF6600",    # 南瓜橙悬停
    }
}
```

### 幽灵滤镜参数

```python
GHOST_FILTER_CONFIG = {
    "opacity": 0.65,           # 透明度 (60-70%)
    "color_blend": 0.3,        # 颜色混合强度
    "colors": [
        QColor(0, 255, 136),   # 幽灵绿
        QColor(139, 0, 255),   # 诅咒紫
    ]
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: 3D Raised Button Effect
*For any* stylesheet returned by `get_stylesheet()`, the QPushButton selector shall have border-top and border-left using light color, and border-bottom and border-right using dark color, creating a 3D raised effect.
**Validates: Requirements 1.1**

### Property 2: 3D Sunken Pressed Effect
*For any* stylesheet returned by `get_stylesheet()`, the QPushButton:pressed selector shall have inverted border colors compared to the normal state (dark top-left, light bottom-right).
**Validates: Requirements 1.2**

### Property 3: 3D Sunken Input Fields
*For any* stylesheet returned by `get_stylesheet()`, the QLineEdit and QFrame selectors shall have 3D sunken border effect (dark top-left, light bottom-right).
**Validates: Requirements 1.3**

### Property 4: Zero Border-Radius Enforcement
*For any* stylesheet returned by `get_stylesheet()`, all border-radius declarations shall have value 0px to enforce sharp pixel edges.
**Validates: Requirements 1.4**

### Property 5: Normal Mode Palette Consistency
*For any* call to `get_palette("normal")`, the returned dictionary shall contain: bg=#C0C0C0, fg=#000000, button_light=#FFFFFF, button_dark=#808080, accent=#000080.
**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

### Property 6: Halloween Mode Palette Consistency
*For any* call to `get_palette("halloween")`, the returned dictionary shall contain: bg=#1A0A1A, fg=#00FF88, accent in [#FF0066, #FF6600], border=#8B00FF.
**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

### Property 7: Ghost Filter Opacity Reduction
*For any* non-transparent pixel in an image, after applying `apply_ghost_filter()`, the pixel's alpha value shall be between 60% and 70% of the original alpha value.
**Validates: Requirements 4.2**

### Property 8: Ghost Filter Color Tint
*For any* non-transparent pixel in an image, after applying `apply_ghost_filter()`, the pixel shall have increased green or purple color component compared to the original.
**Validates: Requirements 4.3**

### Property 9: Checkbox Square Indicator
*For any* stylesheet returned by `get_stylesheet()`, the QCheckBox::indicator selector shall have border-radius: 0px and 3D sunken border effect.
**Validates: Requirements 5.2**

### Property 10: Menu 3D Raised Border
*For any* stylesheet returned by `get_stylesheet()`, the QMenu selector shall have 3D raised border effect (light top-left, dark bottom-right).
**Validates: Requirements 7.1**

### Property 11: Menu Item Hover Inversion
*For any* stylesheet returned by `get_stylesheet()`, the QMenu::item:selected selector shall have background-color set to a dark/accent color and color set to a light/contrasting color.
**Validates: Requirements 7.2**

## Error Handling

| Error Scenario | Handling Strategy |
|----------------|-------------------|
| Invalid mode parameter | Default to "normal" mode |
| Missing palette key | Return default gray color |
| Ghost filter on null pixmap | Return original pixmap unchanged |
| QSS parsing error | Log warning, use minimal fallback style |

## Testing Strategy

### Unit Tests
- Test `get_palette()` returns correct colors for each mode
- Test `get_stylesheet()` returns non-empty string
- Test `apply_ghost_filter()` handles null pixmap gracefully
- Test 3D border generation functions

### Property-Based Tests
使用 `hypothesis` 库进行属性测试：

1. **Property 1-4 Tests**: 解析样式表，验证3D边框效果和零圆角
2. **Property 5-6 Tests**: 验证配色方案包含正确的颜色值
3. **Property 7-8 Tests**: 生成随机图像，应用幽灵滤镜，验证透明度和颜色变化
4. **Property 9-11 Tests**: 解析样式表，验证特定组件样式

每个属性测试配置运行至少 100 次迭代。

测试文件格式：
```python
# tests/test_retro_ui_properties.py
# **Feature: retro-kiroween-ui, Property 1: 3D Raised Button Effect**
@given(mode=st.sampled_from(["normal", "halloween"]))
def test_3d_raised_button_effect(mode):
    stylesheet = get_stylesheet(mode)
    # Parse and verify QPushButton has correct 3D borders
    ...
```

### Integration Tests
- Test theme switching updates all UI components
- Test pet widget applies ghost filter in halloween mode
- Test gacha animation uses correct theme colors

