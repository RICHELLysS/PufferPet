"""
ui_gacha.py - V7 Gacha System

WARNING: The blind box contains mysteries from the deep...

Gacha visual feedback:
- Phase 1: Box shaking
- Phase 2: Flash effect
- Phase 3: Reveal obtained pet

V7 Pet pool: puffer, jelly, crab, starfish, ray
Probability: puffer/jelly/crab/starfish 22% each, ray 12% (SSR)

Pixel-art styling using ui_style module.
"""

import os
import random
from typing import Optional, Callable
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, pyqtSignal, QEasingCurve
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPaintEvent, QMouseEvent

# Import ui_style for pixel-art styling
import ui_style
from ui_style import get_palette, get_font_family

# Import V7 configuration
from pet_config import GACHA_WEIGHTS, V7_PETS, PET_SHAPES

# V7 Pet names
PET_NAMES = {
    'puffer': 'Puffer',
    'jelly': 'Jellyfish',
    'crab': 'Crab',
    'starfish': 'Starfish',
    'ray': 'Ray',
}

# V7 Pet colors (derived from PET_SHAPES)
PET_COLORS = {pet_id: color for pet_id, (_, color) in PET_SHAPES.items()}


class GachaOverlay(QWidget):
    """
    Fullscreen gacha overlay.
    
    WARNING: The blind box trembles with anticipation...
    
    Three-phase animation:
    1. Box shaking (1.5s) - V9: Loop box_0 to box_3 sequence frames
    2. Flash effect (0.5s)
    3. Reveal pet (click to close)
    
    Uses pixel-art styling from ui_style module.
    """
    
    # Signals
    closed = pyqtSignal(str)  # Emitted on close, parameter is obtained pet ID
    
    # V9: Blindbox frame animation constants
    BLINDBOX_FRAME_COUNT = 4  # 4-frame sequence (box_0 to box_3)
    BLINDBOX_FPS = 8  # Frame rate
    
    def __init__(self, pet_id: str, mode: str = "normal", parent=None):
        super().__init__(parent)
        self.pet_id = pet_id
        self.mode = mode  # Theme mode for pixel-art styling
        self.palette = get_palette(mode)  # Get theme-appropriate colors
        self.stage = 0  # 0=抖动, 1=闪光, 2=展示
        self.flash_alpha = 0
        self.shake_offset = 0
        
        # V9: 盲盒帧动画状态
        self.box_frames = []  # 盲盒序列帧列表
        self.current_box_frame = 0  # 当前帧索引
        self.box_frame_timer = None  # 帧动画定时器
        
        self._setup_window()
        self._load_assets()
        self._start_animation()
    
    def _setup_window(self):
        """Setup fullscreen window."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Fullscreen
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())
    
    def _load_assets(self):
        """Load assets for gacha animation."""
        # V9: Load blindbox sequence frames (Requirements 8.1)
        self.box_frames = self._load_blindbox_frames()
        
        # Set initial blindbox image (first frame or placeholder)
        if self.box_frames:
            self.box_pixmap = self.box_frames[0]
        else:
            self.box_pixmap = self._create_box_placeholder()
        
        # V7.1: Simplified paths - all V7 pets use assets/{pet_id}/ (Requirements: 10.2)
        pet_paths = [
            f"assets/{self.pet_id}/adult_idle.png",
            f"assets/{self.pet_id}/baby_idle.png",
        ]
        self.pet_pixmap = None
        for path in pet_paths:
            if os.path.exists(path):
                self.pet_pixmap = QPixmap(path)
                break
        
        if self.pet_pixmap is None:
            self.pet_pixmap = self._create_pet_placeholder()
    
    def _load_blindbox_frames(self) -> list:
        """
        V9: Load blindbox sequence frames.
        
        Path: assets/blindbox/box_{0-3}.png
        Requirements 8.1, 8.3: Return empty list on failure, fallback to placeholder
        """
        frames = []
        for i in range(self.BLINDBOX_FRAME_COUNT):
            frame_path = f"assets/blindbox/box_{i}.png"
            if os.path.exists(frame_path):
                pixmap = QPixmap(frame_path)
                # 检查图像是否有效 (非空且非null)
                if not pixmap.isNull() and pixmap.width() > 0:
                    frames.append(pixmap)
                else:
                    # 无效图像，回退到占位符
                    return []
            else:
                # 文件不存在，回退到占位符
                return []
        return frames
    
    def _create_box_placeholder(self) -> QPixmap:
        """
        Create blindbox placeholder - pixel-art style with 3D raised effect.
        
        Requirements 8.1, 8.2, 8.3:
        - Normal mode: gray Minesweeper style with 3D box effect
        - Halloween mode: dark spooky colors with glowing effects
        - 3D raised border effect for the box
        """
        size = 150
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        # No antialiasing for pixel-art sharp edges
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        # Use theme-appropriate colors from palette
        button_face = QColor(self.palette["button_face"])
        button_light = QColor(self.palette["button_light"])
        button_dark = QColor(self.palette["button_dark"])
        text_color = QColor(self.palette["fg"])
        accent_color = QColor(self.palette["accent"])
        
        # Box dimensions
        box_x, box_y = 10, 30
        box_w, box_h = size - 20, size - 40
        
        # Draw 3D raised box effect (Minesweeper style)
        # Main box face
        painter.setBrush(button_face)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(box_x, box_y, box_w, box_h)
        
        # 3D raised border - light on top-left, dark on bottom-right
        border_width = 3
        
        # Top border (light)
        painter.setBrush(button_light)
        painter.drawRect(box_x, box_y, box_w, border_width)
        
        # Left border (light)
        painter.drawRect(box_x, box_y, border_width, box_h)
        
        # Bottom border (dark)
        painter.setBrush(button_dark)
        painter.drawRect(box_x, box_y + box_h - border_width, box_w, border_width)
        
        # Right border (dark)
        painter.drawRect(box_x + box_w - border_width, box_y, border_width, box_h)
        
        # Inner accent line for halloween mode (glowing effect)
        if self.mode == "halloween":
            painter.setPen(accent_color)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(box_x + border_width + 2, box_y + border_width + 2, 
                           box_w - 2 * border_width - 4, box_h - 2 * border_width - 4)
        
        # Question mark - use pixel font with theme color
        painter.setPen(text_color)
        font_family = get_font_family().split(',')[0].strip('"')
        font = QFont(font_family, 48, QFont.Weight.Bold)
        font.setStyleStrategy(QFont.StyleStrategy.NoAntialias)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "?")
        
        painter.end()
        return pixmap
    
    def _create_pet_placeholder(self) -> QPixmap:
        """
        Create pet placeholder - pixel-art style with 3D raised effect.
        
        Requirements 8.1, 8.2:
        - Normal mode: gray Minesweeper style
        - Halloween mode: dark spooky colors with glowing effects
        """
        size = 200
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        # No antialiasing for pixel-art sharp edges
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        # Use pet-specific color with theme-appropriate border
        pet_color = QColor(PET_COLORS.get(self.pet_id, '#4682B4'))
        button_light = QColor(self.palette["button_light"])
        button_dark = QColor(self.palette["button_dark"])
        accent_color = QColor(self.palette["accent"])
        
        # Pet card dimensions
        card_x, card_y = 20, 30
        card_w, card_h = size - 40, size - 60
        
        # Draw 3D raised card effect
        border_width = 3
        
        # Main card face with pet color
        painter.setBrush(pet_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(card_x, card_y, card_w, card_h)
        
        # 3D raised border - light on top-left, dark on bottom-right
        # Top border (light)
        painter.setBrush(button_light)
        painter.drawRect(card_x, card_y, card_w, border_width)
        
        # Left border (light)
        painter.drawRect(card_x, card_y, border_width, card_h)
        
        # Bottom border (dark)
        painter.setBrush(button_dark)
        painter.drawRect(card_x, card_y + card_h - border_width, card_w, border_width)
        
        # Right border (dark)
        painter.drawRect(card_x + card_w - border_width, card_y, border_width, card_h)
        
        # Add glow effect for halloween mode
        if self.mode == "halloween":
            painter.setPen(accent_color)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(card_x - 2, card_y - 2, card_w + 4, card_h + 4)
        
        painter.end()
        return pixmap
    
    def _start_animation(self):
        """Start gacha animation."""
        # Play gacha open sound at animation start (Requirements 6.5)
        from sound_manager import get_sound_manager
        get_sound_manager().play_gacha_open()
        
        # Shake timer
        self.shake_timer = QTimer(self)
        self.shake_timer.timeout.connect(self._update_shake)
        self.shake_timer.start(50)
        
        # V9: Blindbox frame animation timer (Requirements 8.2)
        if self.box_frames:
            self.box_frame_timer = QTimer(self)
            self.box_frame_timer.timeout.connect(self._update_box_frame)
            frame_interval = 1000 // self.BLINDBOX_FPS  # 8fps = 125ms per frame
            self.box_frame_timer.start(frame_interval)
        
        # Enter flash phase after 1.5 seconds
        QTimer.singleShot(1500, self._start_flash)
    
    def _update_shake(self):
        """Update shake animation."""
        if self.stage == 0:
            self.shake_offset = random.randint(-10, 10)
            self.update()
    
    def _update_box_frame(self):
        """
        V9: Update blindbox frame animation.
        
        Requirements 8.2: Loop box_0 to box_3 during shake phase
        """
        if self.stage == 0 and self.box_frames:
            # Cycle to next frame (0 -> 1 -> 2 -> 3 -> 0)
            self.current_box_frame = (self.current_box_frame + 1) % len(self.box_frames)
            self.box_pixmap = self.box_frames[self.current_box_frame]
            self.update()
    
    def _start_flash(self):
        """Start flash effect."""
        self.stage = 1
        self.shake_timer.stop()
        self.shake_offset = 0
        
        # V9: Stop blindbox frame animation
        if self.box_frame_timer:
            self.box_frame_timer.stop()
        
        # Flash animation
        self.flash_timer = QTimer(self)
        self.flash_timer.timeout.connect(self._update_flash)
        self.flash_timer.start(30)
    
    def _update_flash(self):
        """Update flash effect."""
        if self.stage == 1:
            self.flash_alpha += 20
            if self.flash_alpha >= 255:
                self.flash_alpha = 255
                self.flash_timer.stop()
                QTimer.singleShot(200, self._show_result)
            self.update()
    
    def _show_result(self):
        """Show result phase."""
        self.stage = 2
        self.flash_alpha = 0
        self.update()
    
    def paintEvent(self, event: QPaintEvent):
        """
        绘制 - using pixel-art styling from ui_style
        
        Requirements 8.1, 8.2:
        - Normal mode: gray Minesweeper style
        - Halloween mode: dark spooky colors with glowing effects
        """
        painter = QPainter(self)
        # No antialiasing for pixel-art sharp edges
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        # Get theme colors from palette
        bg_color = QColor(self.palette["bg"])
        fg_color = QColor(self.palette["fg"])
        highlight_color = QColor(self.palette["highlight"])
        accent_color = QColor(self.palette["accent"])
        button_light = QColor(self.palette["button_light"])
        
        # 半透明背景 - use theme-appropriate overlay
        if self.mode == "halloween":
            # Dark spooky overlay with purple tint
            overlay = QColor(26, 10, 26, 220)  # Deep purple-black
            painter.fillRect(self.rect(), overlay)
        else:
            # Gray Minesweeper style overlay
            overlay = QColor(0, 0, 0, 180)
            painter.fillRect(self.rect(), overlay)
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # Get pixel font family
        font_family = get_font_family().split(',')[0].strip('"')
        
        if self.stage == 0:
            # 阶段1: 盲盒抖动
            box_x = center_x - self.box_pixmap.width() // 2 + self.shake_offset
            box_y = center_y - self.box_pixmap.height() // 2
            painter.drawPixmap(box_x, box_y, self.box_pixmap)
            
            # Hint text - use theme colors and pixel font
            if self.mode == "halloween":
                painter.setPen(fg_color)  # Ghost green for halloween
            else:
                painter.setPen(button_light)  # White for normal mode
            font = QFont(font_family, 24, QFont.Weight.Bold)
            font.setStyleStrategy(QFont.StyleStrategy.NoAntialias)
            painter.setFont(font)
            painter.drawText(
                self.rect().adjusted(0, center_y + 100, 0, 0),
                Qt.AlignmentFlag.AlignHCenter,
                "Opening..."
            )
        
        elif self.stage == 1:
            # 阶段2: 闪光 - use theme-appropriate flash color
            if self.mode == "halloween":
                # Purple/green flash for spooky effect
                flash_color = QColor(accent_color)  # Blood red flash
            else:
                # White flash for Minesweeper style
                flash_color = QColor(button_light)
            flash_color.setAlpha(self.flash_alpha)
            painter.fillRect(self.rect(), flash_color)
        
        elif self.stage == 2:
            # 阶段3: 展示宠物
            # 宠物图像
            pet_x = center_x - self.pet_pixmap.width() // 2
            pet_y = center_y - self.pet_pixmap.height() // 2 - 50
            painter.drawPixmap(pet_x, pet_y, self.pet_pixmap)
            
            # 文字 - use theme colors and pixel font
            if self.mode == "halloween":
                title_color = accent_color  # Blood red for halloween
            else:
                title_color = button_light  # White for normal mode
            
            painter.setPen(title_color)
            font = QFont(font_family, 28, QFont.Weight.Bold)
            font.setStyleStrategy(QFont.StyleStrategy.NoAntialias)
            painter.setFont(font)
            
            name = PET_NAMES.get(self.pet_id, self.pet_id)
            painter.drawText(
                self.rect().adjusted(0, center_y + 80, 0, 0),
                Qt.AlignmentFlag.AlignHCenter,
                "New Partner Found!"
            )
            
            # Pet name - use foreground color
            painter.setPen(fg_color)
            font.setPointSize(22)
            painter.setFont(font)
            painter.drawText(
                self.rect().adjusted(0, center_y + 130, 0, 0),
                Qt.AlignmentFlag.AlignHCenter,
                name
            )
            
            # 点击提示 - use theme highlight color
            painter.setPen(highlight_color)
            font.setPointSize(14)
            painter.setFont(font)
            painter.drawText(
                self.rect().adjusted(0, center_y + 200, 0, 0),
                Qt.AlignmentFlag.AlignHCenter,
                "Click anywhere to continue..."
            )
    
    def mousePressEvent(self, event: QMouseEvent):
        """Click to close."""
        if self.stage == 2:
            self.closed.emit(self.pet_id)
            self.close()


def roll_gacha() -> str:
    """Roll gacha with V7 weights."""
    total = sum(GACHA_WEIGHTS.values())  # 100
    roll = random.randint(1, total)
    
    cumulative = 0
    for pet_id in V7_PETS:
        cumulative += GACHA_WEIGHTS[pet_id]
        if roll <= cumulative:
            return pet_id
    
    return 'puffer'  # 默认


# V7.1: roll_tier3 alias removed - use roll_gacha directly
# Requirements: 10.2


def show_gacha(pet_id: str = None, on_close: Callable[[str], None] = None, mode: str = "normal"):
    """
    Show gacha animation.
    
    Args:
        pet_id: Specific pet ID, None for random roll
        on_close: Close callback
        mode: Theme mode ("normal" or "halloween") for pixel-art styling
    """
    if pet_id is None:
        pet_id = roll_gacha()
    
    overlay = GachaOverlay(pet_id, mode=mode)
    if on_close:
        overlay.closed.connect(on_close)
    overlay.show()
    
    return overlay
