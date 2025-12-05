# Design Document: V7.1 System Audit & Logic Freeze

## Overview

V7.1 是导入美术素材前的最终代码版本。本阶段专注于：
- 完善核心交互逻辑（愤怒机制、拖拽物理）
- 确保养成系统完整（任务自定义、生命周期）
- 优化经济系统（盲盒动画、背包同步）
- 统一视觉风格（几何占位符、像素风UI）
- 代码清理和音效预留

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        main.py (入口)                            │
│  - 初始化检查 (data.json 不存在时创建默认数据)                      │
│  - 连接所有模块信号                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
    ┌─────────────────────────┼─────────────────────────┐
    ▼                         ▼                         ▼
┌─────────────┐       ┌─────────────┐           ┌─────────────┐
│ pet_core.py │       │logic_growth │           │sound_manager│
│ - PetWidget │       │ - 生命周期   │           │ - beep()    │
│ - 愤怒机制   │       │ - 任务进度   │           │ - 音效反馈   │
│ - 拖拽物理   │       │ - 数据持久化 │           └─────────────┘
│ - 右键菜单   │       └─────────────┘
└─────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      UI 模块                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │task_window  │  │ ui_gacha    │  │ui_inventory │              │
│  │- 可编辑任务  │  │- 盲盒动画    │  │- MC风格背包  │              │
│  │- 音效触发    │  │- 闪光特效    │  │- 实时同步    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. sound_manager.py (新建)

```python
"""音效管理器 - 使用 QApplication.beep() 作为临时反馈"""

class SoundManager:
    def __init__(self):
        self.enabled = True
    
    def play_task_complete(self) -> None:
        """任务完成音效"""
        QApplication.beep()
    
    def play_gacha_open(self) -> None:
        """开盲盒音效"""
        QApplication.beep()
        QApplication.beep()  # 双响
    
    def play_pet_upgrade(self) -> None:
        """宠物升级音效"""
        QApplication.beep()
    
    def play_pet_angry(self) -> None:
        """宠物愤怒音效"""
        QApplication.beep()

# 全局实例
_sound_manager = None

def get_sound_manager() -> SoundManager:
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager
```

### 2. pet_core.py 更新 - 愤怒机制

```python
class PetWidget(QWidget):
    def __init__(self, ...):
        # 愤怒机制状态
        self.click_times = []  # 记录点击时间
        self.is_angry = False
        self.anger_timer = None
        self.shake_timer = None
        self.original_pos = None
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 记录点击时间
            current_time = time.time()
            self.click_times.append(current_time)
            
            # 保留最近2秒内的点击
            self.click_times = [t for t in self.click_times if current_time - t <= 2.0]
            
            # 检查是否触发愤怒 (5次点击在2秒内)
            if len(self.click_times) >= 5 and not self.is_angry:
                self.trigger_anger()
    
    def trigger_anger(self):
        """触发愤怒状态"""
        self.is_angry = True
        self.original_pos = self.pos()
        
        # 播放愤怒音效
        from sound_manager import get_sound_manager
        get_sound_manager().play_pet_angry()
        
        # 变红色
        self.load_image()  # 重新加载，使用红色
        
        # 开始抖动动画
        self._start_shake_animation()
        
        # 5秒后恢复
        self.anger_timer = QTimer()
        self.anger_timer.timeout.connect(self.calm_down)
        self.anger_timer.setSingleShot(True)
        self.anger_timer.start(5000)
    
    def _start_shake_animation(self):
        """开始抖动动画"""
        def shake():
            if not self.is_angry:
                return
            offset_x = random.randint(-10, 10)
            new_pos = self.original_pos + QPoint(offset_x, 0)
            self.move(new_pos)
        
        self.shake_timer = QTimer()
        self.shake_timer.timeout.connect(shake)
        self.shake_timer.start(50)  # 50ms 抖动一次
    
    def calm_down(self):
        """恢复正常状态"""
        self.is_angry = False
        self.click_times.clear()
        
        if self.shake_timer:
            self.shake_timer.stop()
        
        if self.original_pos:
            self.move(self.original_pos)
        
        self.load_image()  # 恢复原色
```

### 3. pet_core.py 更新 - 拖拽物理

```python
class PetWidget(QWidget):
    def __init__(self, ...):
        # 拖拽物理状态
        self.is_dragging = False
        self.squash_factor = 1.0  # 1.0 = 正常, <1.0 = 挤压
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.is_dormant:
                self.is_dragging = True
                self.squash_factor = 0.8  # 开始挤压
                self.update()
    
    def mouseMoveEvent(self, event):
        if self.is_dragging:
            # 根据速度调整挤压程度
            speed = abs(delta.x()) + abs(delta.y())
            self.squash_factor = max(0.6, 1.0 - speed * 0.01)
            self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self._animate_stretch_back()
    
    def _animate_stretch_back(self):
        """动画恢复正常形状"""
        def restore():
            if self.squash_factor < 1.0:
                self.squash_factor = min(1.0, self.squash_factor + 0.1)
                self.update()
                if self.squash_factor < 1.0:
                    QTimer.singleShot(16, restore)
        restore()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        if self.squash_factor != 1.0:
            # 应用挤压变换
            transform = painter.transform()
            transform.scale(self.squash_factor, 2.0 - self.squash_factor)
            painter.setTransform(transform)
        painter.drawPixmap(0, 0, self.pixmap)
```

### 4. PetRenderer 更新 - 彩色占位符

```python
class PetRenderer:
    @staticmethod
    def draw_placeholder_colored(pet_id: str, size: int, color: str) -> QPixmap:
        """绘制指定颜色的几何占位符（用于愤怒状态）"""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        shape, _ = PET_SHAPES.get(pet_id, ('circle', '#888888'))
        rect = pixmap.rect()
        
        # 使用传入的颜色而非配置颜色
        if shape == 'circle':
            PetRenderer.draw_circle(painter, rect, color)
        # ... 其他形状
        
        painter.end()
        return pixmap
```

### 5. task_window.py 更新 - 可编辑任务

```python
class TaskWindow(QDialog):
    def _create_ui(self):
        # 每个任务使用 QLineEdit 而非 QCheckBox 文本
        for i, task_text in enumerate(task_texts):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            
            # 复选框
            checkbox = QCheckBox()
            checkbox.setChecked(task_states[i])
            
            # 可编辑文本
            line_edit = QLineEdit(task_text)
            line_edit.textChanged.connect(
                lambda text, idx=i: self._on_task_text_changed(idx, text)
            )
            
            row_layout.addWidget(checkbox)
            row_layout.addWidget(line_edit)
            self.task_layout.addWidget(row_widget)
    
    def _on_task_text_changed(self, index: int, new_text: str):
        """任务文本变更时保存"""
        self._save_task_texts()
    
    def _on_task_completed(self, index: int, completed: bool):
        """任务完成时播放音效"""
        if completed:
            from sound_manager import get_sound_manager
            get_sound_manager().play_task_complete()
```

### 6. ui_gacha.py 更新 - 完整动画

```python
class GachaOverlay(QWidget):
    def __init__(self, pet_id: str, mode: str = "normal"):
        self.stage = 0  # 0=抖动, 1=闪光, 2=展示
        self.flash_alpha = 0
        self.shake_offset = 0
        
        self._start_animation()
    
    def _start_animation(self):
        # 阶段1: 盲盒抖动 (1.5秒)
        self.shake_timer = QTimer()
        self.shake_timer.timeout.connect(self._update_shake)
        self.shake_timer.start(50)
        
        # 播放开盲盒音效
        from sound_manager import get_sound_manager
        get_sound_manager().play_gacha_open()
        
        QTimer.singleShot(1500, self._start_flash)
    
    def _start_flash(self):
        # 阶段2: 闪光特效 (0.5秒)
        self.stage = 1
        self.shake_timer.stop()
        
        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self._update_flash)
        self.flash_timer.start(30)
    
    def _update_flash(self):
        self.flash_alpha += 20
        if self.flash_alpha >= 255:
            self.flash_timer.stop()
            QTimer.singleShot(200, self._show_result)
        self.update()
    
    def _show_result(self):
        # 阶段3: 展示宠物
        self.stage = 2
        self.flash_alpha = 0
        self.update()
```

### 7. ui_inventory.py 更新 - 实时同步

```python
class MCInventoryWindow(QDialog):
    pets_changed = pyqtSignal(list)  # 当 active_pets 变化时发出
    
    def _on_slot_clicked(self, pet_id: str):
        """点击格子切换宠物状态"""
        if pet_id in self._active_pets:
            # 从桌面移到背包
            self._active_pets.remove(pet_id)
            self._stored_pets.append(pet_id)
        else:
            # 从背包移到桌面
            if len(self._active_pets) >= MAX_ACTIVE:
                QMessageBox.warning(self, "提示", f"桌面最多显示 {MAX_ACTIVE} 只宠物！")
                return
            self._stored_pets.remove(pet_id)
            self._active_pets.append(pet_id)
        
        # 发出信号，通知主程序更新桌面显示
        self.pets_changed.emit(self._active_pets.copy())
        self._refresh_slots()
```

## Data Models

### 愤怒机制状态

| 属性 | 类型 | 描述 |
|------|------|------|
| click_times | list[float] | 最近2秒内的点击时间戳 |
| is_angry | bool | 是否处于愤怒状态 |
| anger_timer | QTimer | 5秒冷却计时器 |
| shake_timer | QTimer | 抖动动画计时器 |
| original_pos | QPoint | 抖动前的原始位置 |

### 拖拽物理状态

| 属性 | 类型 | 描述 |
|------|------|------|
| is_dragging | bool | 是否正在拖拽 |
| squash_factor | float | 挤压系数 (0.6-1.0) |
| drag_offset | QPoint | 拖拽偏移量 |

### 任务数据扩展

```python
# data.json 结构扩展
{
    "pets": {...},
    "settings": {...},
    "custom_task_texts": [  # 新增
        "完成一项工作任务",
        "锻炼30分钟",
        "阅读或学习新知识"
    ],
    "task_states": [False, False, False]
}
```



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Anger Trigger Threshold
*For any* sequence of click timestamps, if exactly 5 or more clicks occur within a 2-second window, the pet SHALL transition to angry state; if fewer than 5 clicks occur within any 2-second window, the pet SHALL remain in normal state.
**Validates: Requirements 1.1**

### Property 2: Anger State Color Change and Restoration
*For any* pet in angry state, the rendered placeholder SHALL use red color (#FF0000); when the pet returns to normal state, the placeholder SHALL use the pet's original configured color.
**Validates: Requirements 1.2, 1.5**

### Property 3: Anger State Shake Animation
*For any* pet in angry state, the shake_timer SHALL be active and the pet position SHALL oscillate from its original position.
**Validates: Requirements 1.3**

### Property 4: Anger State Auto-Recovery
*For any* pet that enters angry state, after exactly 5 seconds, the pet SHALL automatically return to normal state (is_angry = False).
**Validates: Requirements 1.4**

### Property 5: Dormant Pets Cannot Be Dragged
*For any* pet in dormant state (state = 0), all drag operations SHALL be prevented and the pet position SHALL remain fixed.
**Validates: Requirements 2.4, 5.2**

### Property 6: Squash Effect During Drag
*For any* non-dormant pet being dragged, the squash_factor SHALL be less than 1.0 during the drag operation and SHALL return to 1.0 after release.
**Validates: Requirements 2.1, 2.3**

### Property 7: Squash Factor Speed Relationship
*For any* drag operation with speed S, the squash_factor SHALL decrease as S increases (inverse relationship), with a minimum bound of 0.6.
**Validates: Requirements 2.2**

### Property 8: Task Text Persistence Round-Trip
*For any* custom task text saved to data.json, reopening the task window SHALL display the exact same text that was saved.
**Validates: Requirements 4.2, 4.4**

### Property 9: Task Completion Sound Trigger
*For any* task that transitions from incomplete to complete, the SoundManager.play_task_complete() SHALL be called exactly once.
**Validates: Requirements 4.3**

### Property 10: Lifecycle State Transitions
*For any* pet starting in dormant state (0), completing 1 task SHALL transition to baby state (1), and completing 3 total tasks SHALL transition to adult state (2).
**Validates: Requirements 5.3, 5.5**

### Property 11: Baby Stage Enables Dragging
*For any* pet that transitions from dormant to baby stage, the pet SHALL become draggable (is_dormant = False) and display normal colors.
**Validates: Requirements 5.4**

### Property 12: Gacha Trigger Threshold
*For any* cumulative task count, the gacha button SHALL be enabled if and only if the count is >= 12.
**Validates: Requirements 6.1**

### Property 13: Gacha Sound Trigger
*For any* gacha opening action, the SoundManager.play_gacha_open() SHALL be called exactly once.
**Validates: Requirements 6.5**

### Property 14: Inventory Slot Icon Generation
*For any* pet in the inventory, the slot SHALL display a valid miniature geometric placeholder generated by PetRenderer.draw_placeholder().
**Validates: Requirements 7.2**

### Property 15: Inventory Change Signal Emission
*For any* toggle action that changes active_pets, the pets_changed signal SHALL be emitted with the updated list.
**Validates: Requirements 7.4**

### Property 16: Placeholder Styling Consistency
*For any* geometric placeholder rendered by PetRenderer, the shape SHALL have a 2px black stroke and a white highlight point in the top-left quadrant.
**Validates: Requirements 8.6, 8.7**

### Property 17: Default Data Initialization
*For any* application start without existing data.json, the system SHALL create a data file containing exactly one pet (puffer) in dormant state (0).
**Validates: Requirements 10.1**

## Error Handling

| Error Scenario | Handling Strategy |
|----------------|-------------------|
| Click detection overflow | Clear click_times array when exceeding 10 entries |
| Anger timer already running | Ignore new anger triggers until current anger ends |
| Drag on dormant pet | Silently ignore drag events |
| Task text empty | Preserve previous text, don't save empty strings |
| data.json corrupted | Reset to default state with dormant puffer |
| Sound playback failure | Log error, continue without sound |

## Testing Strategy

### Unit Tests
- Test anger trigger with exactly 5 clicks in 2 seconds
- Test anger trigger rejection with 4 clicks in 2 seconds
- Test anger trigger rejection with 5 clicks in 3 seconds
- Test squash factor bounds (0.6 to 1.0)
- Test task text save/load cycle
- Test gacha button enable/disable threshold

### Property-Based Tests
使用 `hypothesis` 库进行属性测试：

1. **Property 1 Test**: 生成随机点击时间序列，验证愤怒触发阈值
2. **Property 5 Test**: 对所有休眠状态宠物，验证拖拽被阻止
3. **Property 6 Test**: 模拟拖拽操作，验证 squash_factor 变化
4. **Property 8 Test**: 生成随机任务文本，验证保存/加载一致性
5. **Property 10 Test**: 模拟任务完成序列，验证状态转换
6. **Property 12 Test**: 生成随机任务计数，验证盲盒按钮状态
7. **Property 16 Test**: 对所有V7宠物，验证占位符包含描边和高光
8. **Property 17 Test**: 删除 data.json，验证初始化创建正确数据

每个属性测试配置运行至少100次迭代。

测试文件格式：
```python
# tests/test_v7_1_system_audit.py
# **Feature: v7-1-system-audit, Property 1: Anger Trigger Threshold**
@given(click_times=st.lists(st.floats(min_value=0, max_value=10), min_size=0, max_size=20))
def test_anger_trigger_threshold(click_times):
    # Filter clicks within 2-second windows
    # Verify anger triggers iff 5+ clicks in any 2-second window
    ...
```
