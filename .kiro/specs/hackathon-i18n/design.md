# Design Document: Hackathon i18n & Packaging

## Overview

This design covers the internationalization (i18n) of PufferPet for Hackathon submission and PyInstaller packaging preparation. The implementation involves:

1. Translating all Chinese UI text to English across all Python modules
2. Converting Chinese code comments to English with Spooky/Dramatic style
3. Implementing `resource_path()` helper for PyInstaller compatibility
4. Providing the PyInstaller build command

## Architecture

The translation is a one-time refactoring task affecting multiple modules:

```
┌─────────────────────────────────────────────────────────────┐
│                    Translation Scope                         │
├─────────────────────────────────────────────────────────────┤
│  UI Text Files:                                              │
│  - main.py (menus, dialogs, messages)                       │
│  - ui_gacha.py (gacha overlay text)                         │
│  - ui_inventory.py (inventory window text)                  │
│  - task_window.py (task dialog text)                        │
│  - pet_core.py (tutorial bubbles, context menu)             │
├─────────────────────────────────────────────────────────────┤
│  Comment Translation Files:                                  │
│  - All *.py files with Chinese docstrings/comments          │
│  - logic_growth.py, theme_manager.py, time_manager.py       │
│  - ocean_background.py, pet_manager.py                      │
├─────────────────────────────────────────────────────────────┤
│  Resource Path:                                              │
│  - main.py (add resource_path() function)                   │
│  - pet_core.py (wrap asset paths)                           │
│  - ui_gacha.py (wrap asset paths)                           │
│  - ocean_background.py (wrap asset paths)                   │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Translation Mapping

Key Chinese → English translations:

| Chinese | English |
|---------|---------|
| 任务 | Tasks |
| 背包 | Inventory |
| 设置 | Settings |
| 退出 | Quit |
| 切换 昼/夜 | Toggle Day/Night |
| 测试抽卡 | Test Gacha |
| 重置所有 | Reset All |
| 放生 | Release |
| 确认放生 | Confirm Release |
| 库存已满 | Inventory Full |
| 恭喜 | Congratulations |
| 进度 | Progress |
| 完成 | Done |
| 我的宠物 | My Pets |
| 休眠中 | Dormant |
| 幼年期 | Baby |
| 成年期 | Adult |
| 右键点击我 | Right-click me! |
| 试试拖拽我 | Try dragging me! |
| 连点5下有惊喜 | Click 5x for surprise! |

### 2. resource_path() Function

```python
import sys
import os

def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and PyInstaller.
    
    When running as a PyInstaller bundle, sys._MEIPASS contains
    the path to the temporary folder where assets are extracted.
    
    Args:
        relative_path: Path relative to project root (e.g., "assets/puffer/swim/puffer_swim_0.png")
        
    Returns:
        Absolute path to the resource
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = sys._MEIPASS
    else:
        # Running in development
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)
```

### 3. PyInstaller Command

```powershell
pyinstaller --noconsole --onefile --add-data "assets;assets" --name "PufferPet" main.py
```

Optional with icon (if exists):
```powershell
pyinstaller --noconsole --onefile --add-data "assets;assets" --icon "assets/puffer/default_icon.png" --name "PufferPet" main.py
```

## Data Models

No new data models required. This is a text refactoring task.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: No Chinese Characters in UI Text

*For any* string displayed in the UI (menus, dialogs, buttons, tooltips, messages), the string should contain no Chinese characters (Unicode range U+4E00-U+9FFF).

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**

### Property 2: No Chinese Characters in Code Comments

*For any* Python source file in the project, all docstrings and comments should contain no Chinese characters (Unicode range U+4E00-U+9FFF).

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

### Property 3: Resource Path Correctness

*For any* relative asset path, `resource_path()` should return a valid absolute path that:
- In development mode: equals `os.path.join(os.path.abspath("."), relative_path)`
- In frozen mode: equals `os.path.join(sys._MEIPASS, relative_path)`

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

## Error Handling

- If `resource_path()` is called with a non-existent path, it still returns the constructed path (existence check is caller's responsibility)
- Translation should preserve emoji characters (🎒, 📋, ⚙️, etc.) as they are universal

## Testing Strategy

### Property-Based Testing

Use **Hypothesis** (already in project) for property-based tests:

1. **Property 1 & 2 Test**: Generate random strings from UI text constants and verify no Chinese characters
2. **Property 3 Test**: Generate random relative paths and verify `resource_path()` behavior

### Unit Tests

- Verify specific UI strings are in English
- Verify `resource_path()` returns correct paths in both modes
- Verify PyInstaller command format

### Test Configuration

- Minimum 100 iterations per property test
- Tag format: `**Feature: hackathon-i18n, Property {number}: {property_text}**`
