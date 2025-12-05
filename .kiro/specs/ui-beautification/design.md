# Design Document: Kiroween Pixel-Art UI Restyling

## Overview

本设计实现 PufferPet 应用的"Kiroween"复古像素风格全局UI重绘。核心是创建一个集中式样式管理模块 `ui_style.py`，提供动态配色方案和统一的像素风格组件样式，并更新所有UI模块以应用这些样式。

设计目标：
- 90年代电子宠物机/复古掌机的视觉感受
- 拒绝圆角，强调锐利的像素边缘
- 支持日间/夜间模式动态切换
- 所有UI组件风格统一

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      main.py (Application)                   │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  PufferPetApp                                           ││
│  │  - app.setStyleSheet(get_stylesheet(mode))              ││
│  │  - update_theme() → 刷新全局样式                         ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    ui_style.py (NEW)                         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  PALETTES = {                                           ││
│  │    "normal": { bg, fg, highlight, ... },                ││
│  │    "halloween": { bg, fg, highlight, ... }              ││
│  │  }                                                      ││
│  │                                                         ││
│  │  get_stylesheet(mode) → QSS string                      ││
│  │  load_pixel_font() → QFont                              ││
│  │  get_palette(mode) → dict                               ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   pet_core.py   │ │ ui_inventory.py │ │   ui_gacha.py   │
│   (QMenu样式)   │ │  (窗口样式)     │ │  (覆盖层样式)   │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Components and Interfaces

### 1. ui_style.py (新建模块)

```python
# 核心接口
def get_stylesheet(mode: str) -> str:
    """
    获取指定模式的完整QSS样式表
    
    Args:
        mode: "normal" (日间) 或 "halloween" (夜间)
    
    Returns:
        完整的QSS字符串，覆盖所有组件样式
    """

def get_palette(mode: str) -> dict:
    """
    获取指定模式的配色方案
    
    Args:
        mode: "normal" 或 "halloween"
    
    Returns:
        包含 bg, fg, highlight, border 等颜色值的字典
    """

def load_pixel_font() -> QFont:
    """
    加载像素字体
    
    Returns:
        QFont对象，优先使用pixel_font.ttf，回退到等宽字体
    """

def get_font_family() -> str:
    """
    获取字体族字符串
    
    Returns:
        CSS font-family 字符串
    """
```

### 2. main.py 更新

```python
class PufferPetApp:
    def __init__(self):
        # 初始化时应用全局样式
        self._apply_global_style()
    
    def _apply_global_style(self):
        """应用全局像素风格样式"""
        mode = self.growth_manager.get_theme_mode()
        stylesheet = get_stylesheet(mode)
        self.app.setStyleSheet(stylesheet)
    
    def _toggle_day_night(self):
        """切换昼夜模式时刷新样式"""
        # ... 切换逻辑 ...
        self._apply_global_style()  # 刷新全局样式
```

### 3. pet_core.py 更新

```python
def contextMenuEvent(self, event):
    menu = QMenu(self)
    # 移除内联样式，使用全局样式
    # 或从 ui_style 获取菜单专用样式
    menu.setStyleSheet(get_menu_stylesheet(mode))
```

### 4. ui_inventory.py 更新

```python
class InventoryWindow(QDialog):
    def _setup_ui(self):
        # 移除内联样式，继承全局样式
        # 仅设置布局和组件
```

### 5. ui_gacha.py 更新

```python
class GachaOverlay(QWidget):
    def paintEvent(self, event):
        # 使用 ui_style 的配色方案
        palette = get_palette(current_mode)
        # 使用 palette['fg'], palette['bg'] 等
```

## Data Models

### 配色方案数据结构

```python
PALETTES = {
    "normal": {
        "bg": "#E0F8D0",        # 浅绿/米色背景
        "fg": "#081820",        # 深墨绿前景
        "highlight": "#88C070", # 按钮高亮
        "border": "#081820",    # 边框色
        "accent": "#306230",    # 强调色
    },
    "halloween": {
        "bg": "#101010",        # 纯黑背景
        "fg": "#00FF00",        # 黑客绿前景
        "highlight": "#00AA00", # 按钮高亮
        "border": "#00FF00",    # 边框色
        "accent": "#FF6600",    # 万圣节橙强调
    }
}
```

### 字体配置

```python
FONT_CONFIG = {
    "pixel_font_path": "assets/fonts/pixel_font.ttf",
    "fallback_fonts": ["Courier New", "Consolas", "monospace"],
    "base_size": 12,
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Pet Position in Bottom-Right Area
*For any* screen geometry and pet widget, when the widget is created or enters dormant state, its position shall be within the bottom-right quadrant with at least 80px margin from edges.
**Validates: Requirements 1.1, 1.2, 1.3**

### Property 2: Stylesheet Mode Consistency
*For any* valid mode ("normal" or "halloween"), calling `get_stylesheet(mode)` shall return a non-empty string containing the correct palette colors for that mode.
**Validates: Requirements 2.1, 2.2, 2.3**

### Property 3: Zero Border-Radius Enforcement
*For any* stylesheet returned by `get_stylesheet()`, all `border-radius` declarations shall have value `0px` to enforce pixel-art sharp edges.
**Validates: Requirements 2.4, 4.1, 5.1, 7.3**

### Property 4: Border Width Consistency
*For any* stylesheet returned by `get_stylesheet()`, all `border-width` or `border` declarations shall specify widths between 2px and 3px.
**Validates: Requirements 2.5, 4.1, 5.1**

### Property 5: Button Press Effect
*For any* stylesheet returned by `get_stylesheet()`, the QPushButton:pressed selector shall include padding or margin adjustments that create a 1px offset effect.
**Validates: Requirements 5.2**

### Property 6: Checkbox Character Styling
*For any* stylesheet returned by `get_stylesheet()`, the QCheckBox indicator styling shall use square/rectangular shapes (not circular) to match pixel-art aesthetic.
**Validates: Requirements 6.1, 6.2**

## Error Handling

| Error Scenario | Handling Strategy |
|----------------|-------------------|
| Pixel font file not found | Fall back to system monospace fonts |
| Invalid mode parameter | Default to "normal" mode |
| QSS parsing error | Log warning, use minimal fallback style |
| Screen geometry unavailable | Use default position (100, 100) |

## Testing Strategy

### Unit Tests
- Test `get_stylesheet()` returns non-empty string for valid modes
- Test `get_palette()` returns correct color values
- Test `load_pixel_font()` handles missing font file gracefully
- Test pet widget positioning calculations

### Property-Based Tests
使用 `hypothesis` 库进行属性测试：

1. **Property 1 Test**: 生成随机屏幕尺寸，验证宠物位置始终在右下区域
2. **Property 2 Test**: 对所有有效模式，验证返回的样式表包含正确的配色
3. **Property 3 Test**: 解析样式表，验证所有 border-radius 值为 0px
4. **Property 4 Test**: 解析样式表，验证所有 border 宽度在 2-3px 范围
5. **Property 5 Test**: 验证 :pressed 选择器包含偏移效果
6. **Property 6 Test**: 验证 checkbox 指示器使用方形样式

每个属性测试配置运行至少 100 次迭代。

测试文件格式：
```python
# tests/test_ui_style.py
# **Feature: ui-beautification, Property 1: Pet Position in Bottom-Right Area**
@given(screen_width=st.integers(800, 3840), screen_height=st.integers(600, 2160))
def test_pet_position_bottom_right(screen_width, screen_height):
    ...
```
