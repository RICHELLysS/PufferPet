"""
pet_core.py - V6.1 Stable Pet Display Core

WARNING: This module controls the visual manifestation of creatures from the deep...

Responsibilities:
- Pet window display (frameless, transparent, always-on-top)
- Smart image loading (gif → sequence frames → png → placeholder)
- Dormant filter (grayscale + 60% opacity)
- State-driven display updates
- Drag and interaction logic
- V6.1: Size limits (128x128 base, Tier3 192px)
"""

import os
import random
import time
from typing import Optional, Callable
from PyQt6.QtWidgets import QWidget, QMenu, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QImage, QFont, 
    QMouseEvent, QContextMenuEvent, QPaintEvent
)

# Import ui_style for pixel-art styling
import ui_style

# Import V7 configuration
from pet_config import (
    V7_PETS, BASE_SIZE as V7_BASE_SIZE, ADULT_MULTIPLIER, RAY_MULTIPLIER,
    PET_SHAPES, MAX_INVENTORY, MAX_ACTIVE, GRID_COLUMNS
)

# V6.1 Size constants (kept for backward compatibility)
BASE_SIZE = 128  # Base size (slightly larger than desktop icons)

# V7.1: TIER3_SIZE and TIER3_PETS removed - V7 uses only V7_PETS from pet_config.py
# Requirements: 10.2

# V8: Tutorial bubble configuration (Requirements 4.1, 4.2, 4.3)
# WARNING: These whispers guide mortals through the abyss...
TUTORIAL_BUBBLES = {
    "dormant": "Right-click me!",
    "just_awakened": "Try dragging me!",
    "idle_hint": "Click 5x for surprise!",
}


# =============================================================================
# V9 PetLoader - 资源加载器
# =============================================================================

class PetLoader:
    """
    V9 资源加载器 - 适配嵌套文件夹结构
    
    负责从新的嵌套文件夹结构加载宠物资源。
    路径格式: assets/{pet_id}/{action}/{pet_id}_{action}_{index}.png
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.9
    """
    
    # 动作映射: (stage, is_moving) -> action_folder
    # Stage 0 = Dormant, Stage 1 = Baby, Stage 2 = Adult
    ACTION_MAP = {
        (0, False): 'baby_sleep',   # Stage 0: 休眠
        (0, True): 'baby_sleep',    # Stage 0: 休眠（即使移动也用sleep）
        (1, True): 'baby_swim',     # Stage 1: 幼年游动
        (1, False): 'baby_swim',    # Stage 1: 幼年静止也用swim
        (2, True): 'swim',          # Stage 2: 成年游动
        (2, False): 'sleep',        # Stage 2: 成年静止
    }
    
    INTERACTION_ACTIONS = ['angry', 'drag_h', 'drag_v']
    FRAME_COUNT = 4  # 每个动作4帧 (0-3)
    
    @staticmethod
    def get_frame_path(pet_id: str, action: str, frame_index: int) -> str:
        """
        构建帧路径
        
        路径格式: assets/{pet_id}/{action}/{pet_id}_{action}_{index}.png
        
        Args:
            pet_id: 宠物ID (e.g., 'puffer', 'crab')
            action: 动作名称 (e.g., 'swim', 'sleep', 'angry')
            frame_index: 帧索引 (0-3)
            
        Returns:
            构建的文件路径字符串
            
        Requirements: 1.1
        """
        # Clamp frame_index to valid range 0-3
        frame_index = max(0, min(frame_index, PetLoader.FRAME_COUNT - 1))
        return f"assets/{pet_id}/{action}/{pet_id}_{action}_{frame_index}.png"
    
    @staticmethod
    def load_action_frames(pet_id: str, action: str) -> list:
        """
        加载指定动作的所有帧
        
        加载 _0.png 到 _3.png，失败时回退到 V7 几何占位符
        
        Args:
            pet_id: 宠物ID
            action: 动作名称
            
        Returns:
            QPixmap 列表，包含4帧图像
            
        Requirements: 1.1, 1.9
        """
        frames = []
        
        for i in range(PetLoader.FRAME_COUNT):
            path = PetLoader.get_frame_path(pet_id, action, i)
            pixmap = None
            
            # 尝试加载图像
            if os.path.exists(path):
                # 检查空文件
                if os.path.getsize(path) > 0:
                    pixmap = QPixmap(path)
                    if pixmap.isNull():
                        pixmap = None
            
            # 加载失败，回退到 V7 几何占位符
            if pixmap is None:
                # 使用 PetRenderer 生成占位符
                # 默认使用 baby 尺寸
                size = PetRenderer.calculate_size(pet_id, 'baby')
                pixmap = PetRenderer.draw_placeholder(pet_id, size)
            
            frames.append(pixmap)
        
        return frames
    
    @staticmethod
    def get_action_for_state(stage: int, is_moving: bool) -> str:
        """
        根据状态获取动作名称
        
        映射规则:
        - Stage 0 → baby_sleep
        - Stage 1 → baby_swim
        - Stage 2 + moving → swim
        - Stage 2 + idle → sleep
        
        Args:
            stage: 成长阶段 (0=Dormant, 1=Baby, 2=Adult)
            is_moving: 是否在移动
            
        Returns:
            动作名称字符串
            
        Requirements: 1.2, 1.3, 1.4, 1.5
        """
        return PetLoader.ACTION_MAP.get((stage, is_moving), 'baby_sleep')


# =============================================================================
# V9 FrameAnimator - 序列帧动画器
# =============================================================================

class FrameAnimator:
    """
    V9 帧动画器 - 管理序列帧动画播放
    
    负责循环播放4帧序列动画，支持不同帧率。
    
    Features:
    - 管理帧列表和当前帧索引
    - 支持 start/stop/reset 方法
    - 可配置帧率 (正常 8fps, 休眠 4fps)
    - 帧循环: 0→1→2→3→0
    
    Requirements: 7.1, 7.2, 7.3
    """
    
    NORMAL_FPS = 8      # 正常帧率 (8fps = 125ms per frame)
    DORMANT_FPS = 4     # 休眠帧率 (4fps = 250ms per frame)
    
    def __init__(self, frames: list = None):
        """
        初始化帧动画器
        
        Args:
            frames: QPixmap 列表，包含动画帧 (默认为空列表)
        """
        self.frames = frames if frames is not None else []
        self.current_frame_index = 0
        self.timer: Optional[QTimer] = None
        self._is_playing = False
        self._on_frame_changed: Optional[Callable] = None
    
    def set_frames(self, frames: list) -> None:
        """
        设置帧列表
        
        Args:
            frames: QPixmap 列表
        """
        self.frames = frames if frames is not None else []
        self.reset()
    
    def set_on_frame_changed(self, callback: Callable) -> None:
        """
        设置帧变化回调
        
        Args:
            callback: 帧变化时调用的函数
        """
        self._on_frame_changed = callback
    
    def start(self, fps: int = None) -> None:
        """
        开始播放动画
        
        Args:
            fps: 帧率 (默认使用 NORMAL_FPS = 8)
            
        Requirements: 7.1
        """
        if fps is None:
            fps = self.NORMAL_FPS
        
        # 停止现有计时器
        self.stop()
        
        if not self.frames:
            return
        
        # 计算帧间隔 (毫秒)
        interval_ms = int(1000 / fps)
        
        # 创建并启动计时器
        self.timer = QTimer()
        self.timer.timeout.connect(self._advance_frame)
        self.timer.start(interval_ms)
        self._is_playing = True
    
    def stop(self) -> None:
        """
        停止动画
        
        Requirements: 7.1
        """
        if self.timer is not None:
            self.timer.stop()
            self.timer = None
        self._is_playing = False
    
    def reset(self) -> None:
        """
        重置到第0帧
        
        Requirements: 7.3
        """
        self.current_frame_index = 0
        if self._on_frame_changed:
            self._on_frame_changed()
    
    def _advance_frame(self) -> None:
        """
        前进到下一帧
        
        循环: 0→1→2→3→0
        
        Requirements: 7.2
        """
        if not self.frames:
            return
        
        # 循环到下一帧
        self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
        
        # 触发回调
        if self._on_frame_changed:
            self._on_frame_changed()
    
    def get_current_frame(self) -> Optional[QPixmap]:
        """
        获取当前帧
        
        Returns:
            当前帧的 QPixmap，如果没有帧则返回 None
        """
        if not self.frames:
            return None
        
        if 0 <= self.current_frame_index < len(self.frames):
            return self.frames[self.current_frame_index]
        
        return None
    
    def get_current_frame_index(self) -> int:
        """
        获取当前帧索引
        
        Returns:
            当前帧索引 (0-3)
        """
        return self.current_frame_index
    
    def is_playing(self) -> bool:
        """
        检查动画是否正在播放
        
        Returns:
            True 如果正在播放，否则 False
        """
        return self._is_playing
    
    def get_frame_count(self) -> int:
        """
        获取帧数量
        
        Returns:
            帧数量
        """
        return len(self.frames)


# =============================================================================
# V9 FlipTransform - 拖拽翻转变换
# =============================================================================

class FlipTransform:
    """
    V9 翻转变换 - 拖拽方向翻转逻辑
    
    负责根据拖拽方向判断是否需要翻转图像，并应用翻转变换。
    
    Features:
    - 水平拖拽翻转: delta_x < 0 时水平镜像
    - 垂直拖拽翻转: delta_y > 0 时垂直翻转
    
    Requirements: 5.1, 5.2, 5.3, 5.4
    """
    
    @staticmethod
    def should_flip_horizontal(delta_x: int) -> bool:
        """
        判断是否需要水平翻转
        
        规则:
        - delta_x >= 0 (向右拖拽): 不翻转
        - delta_x < 0 (向左拖拽): 水平镜像翻转
        
        Args:
            delta_x: 水平拖拽增量
            
        Returns:
            True 如果需要水平翻转，否则 False
            
        Requirements: 5.1, 5.2
        """
        return delta_x < 0
    
    @staticmethod
    def should_flip_vertical(delta_y: int) -> bool:
        """
        判断是否需要垂直翻转
        
        规则:
        - delta_y <= 0 (向上拖拽): 不翻转
        - delta_y > 0 (向下拖拽): 垂直翻转
        
        Args:
            delta_y: 垂直拖拽增量
            
        Returns:
            True 如果需要垂直翻转，否则 False
            
        Requirements: 5.3, 5.4
        """
        return delta_y > 0
    
    @staticmethod
    def apply_horizontal_flip(pixmap: QPixmap) -> QPixmap:
        """
        应用水平镜像翻转
        
        使用 QImage.mirrored(True, False) 实现水平镜像
        
        Args:
            pixmap: 原始图像
            
        Returns:
            水平镜像后的图像
            
        Requirements: 5.2
        """
        if pixmap.isNull():
            return pixmap
        
        # 转换为 QImage，应用水平镜像，再转回 QPixmap
        image = pixmap.toImage()
        mirrored_image = image.mirrored(True, False)  # horizontal=True, vertical=False
        return QPixmap.fromImage(mirrored_image)
    
    @staticmethod
    def apply_vertical_flip(pixmap: QPixmap) -> QPixmap:
        """
        应用垂直翻转
        
        使用 QImage.mirrored(False, True) 实现垂直翻转
        
        Args:
            pixmap: 原始图像
            
        Returns:
            垂直翻转后的图像
            
        Requirements: 5.4
        """
        if pixmap.isNull():
            return pixmap
        
        # 转换为 QImage，应用垂直翻转，再转回 QPixmap
        image = pixmap.toImage()
        mirrored_image = image.mirrored(False, True)  # horizontal=False, vertical=True
        return QPixmap.fromImage(mirrored_image)
    
    @staticmethod
    def apply_flip_for_drag(pixmap: QPixmap, delta_x: int, delta_y: int, is_horizontal_drag: bool) -> QPixmap:
        """
        根据拖拽方向应用翻转
        
        便捷方法，根据拖拽类型和方向自动应用正确的翻转。
        
        Args:
            pixmap: 原始图像
            delta_x: 水平拖拽增量
            delta_y: 垂直拖拽增量
            is_horizontal_drag: True 表示水平拖拽，False 表示垂直拖拽
            
        Returns:
            翻转后的图像（如果需要翻转），否则返回原图
            
        Requirements: 5.1, 5.2, 5.3, 5.4
        """
        if pixmap.isNull():
            return pixmap
        
        if is_horizontal_drag:
            # 水平拖拽: 检查是否需要水平翻转
            if FlipTransform.should_flip_horizontal(delta_x):
                return FlipTransform.apply_horizontal_flip(pixmap)
        else:
            # 垂直拖拽: 检查是否需要垂直翻转
            if FlipTransform.should_flip_vertical(delta_y):
                return FlipTransform.apply_vertical_flip(pixmap)
        
        return pixmap


TUTORIAL_CONFIG = {
    "awakened_duration": 10000,  # 10秒
    "text_color": "#FFFF00",      # 黄色
    "outline_color": "#000000",   # 黑色描边
    "bg_alpha": 180,              # 半透明黑色背景 alpha
}


class PetRenderer:
    """
    V7 几何图形渲染器 - 增强版
    
    Provides:
    - Size calculation based on species and growth stage
    - Geometric placeholder generation when images are missing
    - V7 增强: 描边、高光、阴影效果，让几何图形看起来像精心设计的像素道具
    """
    
    # 描边宽度
    STROKE_WIDTH = 2
    # 高光大小（相对于图形大小的比例）
    HIGHLIGHT_SIZE_RATIO = 0.08
    # 阴影偏移（相对于图形大小的比例）
    SHADOW_OFFSET_RATIO = 0.05
    
    # V9 Size Constants
    ORIGINAL_SIZE = 350      # Original frame size (350x350px)
    BASE_SIZE = 100          # Baby base size (100px)
    ADULT_MULTIPLIER = 1.5   # Adult stage multiplier
    RAY_MULTIPLIER = 1.5     # Ray species multiplier
    ICON_SIZE = 64           # Inventory icon size
    ICON_ORIGINAL = 1500     # Original icon size (1500x1500px)
    
    @staticmethod
    def calculate_size(pet_id: str, stage: str) -> int:
        """
        Calculate pet size based on species and growth stage.
        
        Formula: BASE_SIZE × species_multiplier × stage_multiplier
        - species_multiplier: 1.5 for ray, 1.0 for others
        - stage_multiplier: 1.5 for adult, 1.0 for baby/dormant
        
        Args:
            pet_id: Pet identifier (e.g., 'puffer', 'ray')
            stage: Growth stage ('dormant', 'baby', 'adult')
            
        Returns:
            Calculated size in pixels
            
        Requirements: 2.1, 2.2, 2.3, 2.4
        """
        base = V7_BASE_SIZE  # 100px
        
        # Species multiplier (ray has racial advantage)
        if pet_id == 'ray':
            base *= RAY_MULTIPLIER
        
        # Stage multiplier (adult is 1.5x larger)
        if stage == 'adult':
            base *= ADULT_MULTIPLIER
        
        return int(base)
    
    @staticmethod
    def scale_frame(pixmap: QPixmap, target_size: int) -> QPixmap:
        """
        Scale a frame from original 350x350px to target size.
        
        Maintains aspect ratio during scaling.
        
        Args:
            pixmap: Original QPixmap (typically 350x350px)
            target_size: Target size in pixels
            
        Returns:
            Scaled QPixmap
            
        Requirements: 2.1
        """
        if pixmap.isNull():
            return pixmap
        
        # Scale while keeping aspect ratio
        return pixmap.scaled(
            target_size, target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
    
    @staticmethod
    def _draw_highlight(painter: QPainter, x: int, y: int, size: int) -> None:
        """
        绘制高光效果 - 左上角的白色圆点，模拟像素光泽
        
        Args:
            painter: QPainter 实例
            x: 高光 X 坐标
            y: 高光 Y 坐标
            size: 高光大小
        """
        # 主高光 - 白色
        painter.setBrush(QColor(255, 255, 255, 200))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(x, y, size, size)
        
        # 次高光 - 更小更亮
        if size > 4:
            painter.setBrush(QColor(255, 255, 255, 255))
            painter.drawEllipse(x + 1, y + 1, size // 2, size // 2)
    
    @staticmethod
    def _draw_shadow(painter: QPainter, x: int, y: int, w: int, h: int) -> None:
        """
        绘制阴影效果 - 右下角的深色区域
        
        Args:
            painter: QPainter 实例
            x: 阴影 X 坐标
            y: 阴影 Y 坐标
            w: 阴影宽度
            h: 阴影高度
        """
        painter.setBrush(QColor(0, 0, 0, 60))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(x, y, w, h)
    
    @staticmethod
    def _setup_stroke(painter: QPainter) -> None:
        """设置描边画笔 - 2px 黑色描边"""
        from PyQt6.QtGui import QPen
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(PetRenderer.STROKE_WIDTH)
        painter.setPen(pen)
    
    @staticmethod
    def draw_circle(painter: QPainter, rect, color: str) -> None:
        """Draw a circle (puffer placeholder) with stroke, highlight, and shadow."""
        from PyQt6.QtGui import QPen
        
        padding = int(rect.width() * 0.15)  # 增加 padding 为描边留空间
        cx = rect.x() + padding
        cy = rect.y() + padding
        diameter = rect.width() - 2 * padding
        
        # 1. 绘制阴影（右下偏移）
        shadow_offset = int(diameter * PetRenderer.SHADOW_OFFSET_RATIO)
        PetRenderer._draw_shadow(painter, cx + shadow_offset, cy + shadow_offset, diameter, diameter)
        
        # 2. 绘制主体 + 描边
        painter.setBrush(QColor(color))
        PetRenderer._setup_stroke(painter)
        painter.drawEllipse(cx, cy, diameter, diameter)
        
        # 3. 绘制高光（左上角）
        highlight_size = int(diameter * PetRenderer.HIGHLIGHT_SIZE_RATIO)
        highlight_x = cx + int(diameter * 0.2)
        highlight_y = cy + int(diameter * 0.15)
        PetRenderer._draw_highlight(painter, highlight_x, highlight_y, max(highlight_size, 4))
    
    @staticmethod
    def draw_triangle(painter: QPainter, rect, color: str) -> None:
        """Draw a triangle (jelly placeholder) with stroke, highlight, and shadow."""
        from PyQt6.QtGui import QPolygon, QPen
        from PyQt6.QtCore import QPoint as QP
        
        padding = int(rect.width() * 0.15)
        w = rect.width() - 2 * padding
        h = rect.height() - 2 * padding
        x = rect.x() + padding
        y = rect.y() + padding
        
        # Triangle points: top center, bottom left, bottom right
        points = QPolygon([
            QP(x + w // 2, y),           # Top center
            QP(x, y + h),                 # Bottom left
            QP(x + w, y + h)              # Bottom right
        ])
        
        # 1. 绘制阴影
        shadow_offset = int(w * PetRenderer.SHADOW_OFFSET_RATIO)
        shadow_points = QPolygon([
            QP(x + w // 2 + shadow_offset, y + shadow_offset),
            QP(x + shadow_offset, y + h + shadow_offset),
            QP(x + w + shadow_offset, y + h + shadow_offset)
        ])
        painter.setBrush(QColor(0, 0, 0, 60))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(shadow_points)
        
        # 2. 绘制主体 + 描边
        painter.setBrush(QColor(color))
        PetRenderer._setup_stroke(painter)
        painter.drawPolygon(points)
        
        # 3. 绘制高光（顶部附近）
        highlight_size = int(w * PetRenderer.HIGHLIGHT_SIZE_RATIO)
        highlight_x = x + w // 2 - highlight_size
        highlight_y = y + int(h * 0.25)
        PetRenderer._draw_highlight(painter, highlight_x, highlight_y, max(highlight_size, 4))
    
    @staticmethod
    def draw_rectangle(painter: QPainter, rect, color: str) -> None:
        """Draw a rectangle (crab placeholder) with stroke, highlight, and shadow."""
        from PyQt6.QtGui import QPen
        
        padding = int(rect.width() * 0.15)
        # Wider than tall for crab shape
        w = rect.width() - 2 * padding
        h = int((rect.height() - 2 * padding) * 0.7)
        x = rect.x() + padding
        y = rect.y() + padding + (rect.height() - 2 * padding - h) // 2
        
        # 1. 绘制阴影
        shadow_offset = int(w * PetRenderer.SHADOW_OFFSET_RATIO)
        painter.setBrush(QColor(0, 0, 0, 60))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(x + shadow_offset, y + shadow_offset, w, h)
        
        # 2. 绘制主体 + 描边
        painter.setBrush(QColor(color))
        PetRenderer._setup_stroke(painter)
        painter.drawRect(x, y, w, h)
        
        # 3. 绘制高光（左上角）
        highlight_size = int(w * PetRenderer.HIGHLIGHT_SIZE_RATIO)
        highlight_x = x + int(w * 0.15)
        highlight_y = y + int(h * 0.15)
        PetRenderer._draw_highlight(painter, highlight_x, highlight_y, max(highlight_size, 4))
    
    @staticmethod
    def draw_pentagon(painter: QPainter, rect, color: str) -> None:
        """Draw a pentagon (starfish placeholder) with stroke, highlight, and shadow."""
        from PyQt6.QtGui import QPolygon, QPen
        from PyQt6.QtCore import QPoint as QP
        import math
        
        padding = int(rect.width() * 0.15)
        cx = rect.x() + rect.width() // 2
        cy = rect.y() + rect.height() // 2
        radius = (min(rect.width(), rect.height()) - 2 * padding) // 2
        
        # Pentagon with 5 vertices, starting from top
        points = []
        for i in range(5):
            angle = math.radians(-90 + i * 72)  # Start from top (-90°)
            px = int(cx + radius * math.cos(angle))
            py = int(cy + radius * math.sin(angle))
            points.append(QP(px, py))
        
        # 1. 绘制阴影
        shadow_offset = int(radius * PetRenderer.SHADOW_OFFSET_RATIO * 2)
        shadow_points = [QP(p.x() + shadow_offset, p.y() + shadow_offset) for p in points]
        painter.setBrush(QColor(0, 0, 0, 60))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(QPolygon(shadow_points))
        
        # 2. 绘制主体 + 描边
        painter.setBrush(QColor(color))
        PetRenderer._setup_stroke(painter)
        painter.drawPolygon(QPolygon(points))
        
        # 3. 绘制高光（中心偏上）
        highlight_size = int(radius * PetRenderer.HIGHLIGHT_SIZE_RATIO * 2)
        highlight_x = cx - highlight_size // 2
        highlight_y = cy - int(radius * 0.3)
        PetRenderer._draw_highlight(painter, highlight_x, highlight_y, max(highlight_size, 4))
    
    @staticmethod
    def draw_diamond(painter: QPainter, rect, color: str) -> None:
        """Draw a diamond (ray placeholder) with stroke, highlight, and shadow."""
        from PyQt6.QtGui import QPolygon, QPen
        from PyQt6.QtCore import QPoint as QP
        
        padding = int(rect.width() * 0.15)
        cx = rect.x() + rect.width() // 2
        cy = rect.y() + rect.height() // 2
        hw = (rect.width() - 2 * padding) // 2   # Half width
        hh = (rect.height() - 2 * padding) // 2  # Half height
        
        # Diamond: 4 points (top, right, bottom, left)
        points = QPolygon([
            QP(cx, cy - hh),      # Top
            QP(cx + hw, cy),      # Right
            QP(cx, cy + hh),      # Bottom
            QP(cx - hw, cy)       # Left
        ])
        
        # 1. 绘制阴影
        shadow_offset = int(hw * PetRenderer.SHADOW_OFFSET_RATIO * 2)
        shadow_points = QPolygon([
            QP(cx + shadow_offset, cy - hh + shadow_offset),
            QP(cx + hw + shadow_offset, cy + shadow_offset),
            QP(cx + shadow_offset, cy + hh + shadow_offset),
            QP(cx - hw + shadow_offset, cy + shadow_offset)
        ])
        painter.setBrush(QColor(0, 0, 0, 60))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(shadow_points)
        
        # 2. 绘制主体 + 描边
        painter.setBrush(QColor(color))
        PetRenderer._setup_stroke(painter)
        painter.drawPolygon(points)
        
        # 3. 绘制高光（左上区域）
        highlight_size = int(hw * PetRenderer.HIGHLIGHT_SIZE_RATIO * 2)
        highlight_x = cx - int(hw * 0.3)
        highlight_y = cy - int(hh * 0.4)
        PetRenderer._draw_highlight(painter, highlight_x, highlight_y, max(highlight_size, 4))
    
    @staticmethod
    def draw_placeholder(pet_id: str, size: int) -> QPixmap:
        """
        Draw a geometric placeholder for a pet.
        
        V7 增强: 每个几何图形都有描边、高光和阴影效果
        
        Routes to the correct shape drawing method based on pet_id.
        
        Args:
            pet_id: Pet identifier
            size: Size of the placeholder in pixels
            
        Returns:
            QPixmap with the geometric shape
        """
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get shape and color from config, default to circle/gray
        shape, color = PET_SHAPES.get(pet_id, ('circle', '#888888'))
        
        rect = pixmap.rect()
        
        # Route to correct drawing method
        if shape == 'circle':
            PetRenderer.draw_circle(painter, rect, color)
        elif shape == 'triangle':
            PetRenderer.draw_triangle(painter, rect, color)
        elif shape == 'rectangle':
            PetRenderer.draw_rectangle(painter, rect, color)
        elif shape == 'pentagon':
            PetRenderer.draw_pentagon(painter, rect, color)
        elif shape == 'diamond':
            PetRenderer.draw_diamond(painter, rect, color)
        else:
            # Fallback to circle
            PetRenderer.draw_circle(painter, rect, color)
        
        painter.end()
        return pixmap
    
    @staticmethod
    def draw_placeholder_colored(pet_id: str, size: int, color: str) -> QPixmap:
        """
        Draw a geometric placeholder with a custom color (V7.1 愤怒状态用).
        
        Used for angry state where the pet turns red (#FF0000).
        
        Args:
            pet_id: Pet identifier (determines shape)
            size: Size of the placeholder in pixels
            color: Custom color to use (e.g., '#FF0000' for angry)
            
        Returns:
            QPixmap with the geometric shape in the specified color
        """
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get shape from config, but use custom color
        shape, _ = PET_SHAPES.get(pet_id, ('circle', '#888888'))
        
        rect = pixmap.rect()
        
        # Route to correct drawing method with custom color
        if shape == 'circle':
            PetRenderer.draw_circle(painter, rect, color)
        elif shape == 'triangle':
            PetRenderer.draw_triangle(painter, rect, color)
        elif shape == 'rectangle':
            PetRenderer.draw_rectangle(painter, rect, color)
        elif shape == 'pentagon':
            PetRenderer.draw_pentagon(painter, rect, color)
        elif shape == 'diamond':
            PetRenderer.draw_diamond(painter, rect, color)
        else:
            # Fallback to circle
            PetRenderer.draw_circle(painter, rect, color)
        
        painter.end()
        return pixmap
    
    @staticmethod
    def draw_placeholder_spooky(pet_id: str, size: int) -> QPixmap:
        """
        Draw a geometric placeholder with spooky Kiroween colors and glow effect.
        
        Used for halloween mode to give pets a ghostly appearance.
        Uses spooky colors (ghost green #00FF88 or blood red #FF0066) and
        adds a glow effect around the geometric shapes.
        
        Args:
            pet_id: Pet identifier (determines shape)
            size: Size of the placeholder in pixels
            
        Returns:
            QPixmap with the spooky geometric shape with glow effect
            
        Requirements: 4.4
        """
        import random
        from PyQt6.QtGui import QPen, QRadialGradient
        
        # Spooky colors from ThemeManager.SPOOKY_COLORS
        spooky_colors = ['#00FF88', '#FF0066']  # ghost_green, blood_red
        spooky_color = random.choice(spooky_colors)
        
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get shape from config
        shape, _ = PET_SHAPES.get(pet_id, ('circle', '#888888'))
        
        rect = pixmap.rect()
        
        # Draw glow effect first (larger, semi-transparent version behind)
        glow_color = QColor(spooky_color)
        glow_color.setAlpha(80)  # Semi-transparent glow
        
        # Create glow by drawing multiple expanding shapes
        for glow_offset in [8, 5, 3]:
            glow_rect = rect.adjusted(
                -glow_offset, -glow_offset, 
                glow_offset, glow_offset
            )
            # Adjust alpha based on distance (outer = more transparent)
            alpha = int(40 + (8 - glow_offset) * 15)
            glow_color.setAlpha(alpha)
            painter.setBrush(glow_color)
            painter.setPen(Qt.PenStyle.NoPen)
            
            # Draw glow shape based on pet shape
            if shape == 'circle':
                padding = int(glow_rect.width() * 0.15)
                painter.drawEllipse(
                    glow_rect.x() + padding, 
                    glow_rect.y() + padding,
                    glow_rect.width() - 2 * padding,
                    glow_rect.height() - 2 * padding
                )
            elif shape == 'triangle':
                from PyQt6.QtGui import QPolygon
                from PyQt6.QtCore import QPoint as QP
                padding = int(glow_rect.width() * 0.15)
                w = glow_rect.width() - 2 * padding
                h = glow_rect.height() - 2 * padding
                x = glow_rect.x() + padding
                y = glow_rect.y() + padding
                points = QPolygon([
                    QP(x + w // 2, y),
                    QP(x, y + h),
                    QP(x + w, y + h)
                ])
                painter.drawPolygon(points)
            elif shape == 'rectangle':
                padding = int(glow_rect.width() * 0.15)
                w = glow_rect.width() - 2 * padding
                h = int((glow_rect.height() - 2 * padding) * 0.7)
                x = glow_rect.x() + padding
                y = glow_rect.y() + padding + (glow_rect.height() - 2 * padding - h) // 2
                painter.drawRect(x, y, w, h)
            elif shape == 'pentagon':
                from PyQt6.QtGui import QPolygon
                from PyQt6.QtCore import QPoint as QP
                import math
                padding = int(glow_rect.width() * 0.15)
                cx = glow_rect.x() + glow_rect.width() // 2
                cy = glow_rect.y() + glow_rect.height() // 2
                radius = (min(glow_rect.width(), glow_rect.height()) - 2 * padding) // 2
                points = []
                for i in range(5):
                    angle = math.radians(-90 + i * 72)
                    px = int(cx + radius * math.cos(angle))
                    py = int(cy + radius * math.sin(angle))
                    points.append(QP(px, py))
                painter.drawPolygon(QPolygon(points))
            elif shape == 'diamond':
                from PyQt6.QtGui import QPolygon
                from PyQt6.QtCore import QPoint as QP
                padding = int(glow_rect.width() * 0.15)
                cx = glow_rect.x() + glow_rect.width() // 2
                cy = glow_rect.y() + glow_rect.height() // 2
                hw = (glow_rect.width() - 2 * padding) // 2
                hh = (glow_rect.height() - 2 * padding) // 2
                points = QPolygon([
                    QP(cx, cy - hh),
                    QP(cx + hw, cy),
                    QP(cx, cy + hh),
                    QP(cx - hw, cy)
                ])
                painter.drawPolygon(points)
        
        # Now draw the main shape with spooky color
        if shape == 'circle':
            PetRenderer.draw_circle(painter, rect, spooky_color)
        elif shape == 'triangle':
            PetRenderer.draw_triangle(painter, rect, spooky_color)
        elif shape == 'rectangle':
            PetRenderer.draw_rectangle(painter, rect, spooky_color)
        elif shape == 'pentagon':
            PetRenderer.draw_pentagon(painter, rect, spooky_color)
        elif shape == 'diamond':
            PetRenderer.draw_diamond(painter, rect, spooky_color)
        else:
            # Fallback to circle
            PetRenderer.draw_circle(painter, rect, spooky_color)
        
        painter.end()
        return pixmap


class PetWidget(QWidget):
    """
    Pet Display Window
    
    WARNING: This window is the portal through which creatures manifest...
    
    Supports three-stage lifecycle visual representation:
    - Dormant: Fixed at bottom, grayscale filter, drag disabled
    - Baby: Free floating, normal display, draggable
    - Adult: Full form, all features unlocked
    """
    
    # Signals
    task_window_requested = pyqtSignal()  # Request to open task window
    inventory_requested = pyqtSignal()    # V6.1: Request to open inventory
    release_requested = pyqtSignal(str)   # V6.1: Request to release pet
    environment_requested = pyqtSignal()  # V7.1: Request to open environment settings
    
    # Pet color mapping (for placeholders)
    PET_COLORS = {
        'puffer': '#FFB347',   # Orange
        'jelly': '#87CEEB',    # Sky blue
        'starfish': '#FFD700', # Gold
        'crab': '#FF6B6B',     # Red
        'octopus': '#9B59B6',  # Purple
        'ribbon': '#3498DB',   # Blue
        'sunfish': '#F39C12',  # Yellow
        'angler': '#2C3E50',   # Dark blue
    }
    
    def __init__(self, pet_id: str, growth_manager, parent=None):
        """
        初始化宠物窗口
        
        Args:
            pet_id: 宠物ID
            growth_manager: GrowthManager 实例
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.pet_id = pet_id
        self.growth_manager = growth_manager
        
        # 显示状态
        self.current_pixmap: Optional[QPixmap] = None
        self.is_dormant = False
        self.is_dragging = False
        self.drag_offset = QPoint()
        
        # 动画相关
        self.float_timer: Optional[QTimer] = None
        self.float_offset = 0
        self.original_pos: Optional[QPoint] = None
        
        # V7.1 愤怒机制状态 (Requirements 1.1)
        self.click_times: list = []  # 记录点击时间戳
        self.is_angry: bool = False  # 是否处于愤怒状态
        self.anger_timer: Optional[QTimer] = None  # 5秒冷却计时器
        self.shake_timer: Optional[QTimer] = None  # 抖动动画计时器
        self.anger_original_pos: Optional[QPoint] = None  # 抖动前的原始位置
        
        # V7.1 拖拽物理状态 (Requirements 2.1)
        self.squash_factor: float = 1.0  # 挤压系数 (0.6-1.0), 1.0 = 正常
        self.last_drag_pos: Optional[QPoint] = None  # 上一次拖拽位置，用于计算速度
        
        # V8: 引导气泡状态 (Requirements 4.1, 4.2, 4.3)
        self.just_awakened: bool = False  # 是否刚唤醒
        self.just_awakened_timer: Optional[QTimer] = None  # 唤醒提示计时器
        self.show_idle_hint: bool = False  # 是否显示空闲提示
        
        # V9: 序列帧动画器 (Requirements 7.1, 7.2, 7.3, 7.4)
        self.frame_animator: Optional[FrameAnimator] = None
        self.current_action: str = ''  # 当前动作名称
        self.is_moving: bool = False  # 是否在移动
        
        # 设置窗口属性
        self._setup_window()
        
        # 加载图像并更新显示
        self.refresh_display()
    
    def _setup_window(self) -> None:
        """设置窗口属性"""
        # 无边框、透明背景、始终置顶
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 默认大小
        self.setFixedSize(128, 128)
    
    def refresh_display(self) -> None:
        """根据当前状态刷新显示
        
        Kiroween模式 (Requirements 4.1):
        - 检查主题模式
        - 在halloween模式下应用幽灵滤镜
        
        V9: 序列帧动画 (Requirements 7.1, 7.2, 7.3, 7.4)
        - 使用 FrameAnimator 播放序列帧
        - 正常帧率 8fps，休眠帧率 4fps
        """
        # 获取状态
        self.is_dormant = self.growth_manager.is_dormant(self.pet_id)
        stage = self.growth_manager.get_image_stage(self.pet_id)
        
        # 检查主题模式 (Requirements 4.1)
        theme_mode = self.growth_manager.get_theme_mode()
        is_halloween = theme_mode == "halloween"
        
        # V9: 获取当前动作 (Requirements 7.1)
        state_num = self.growth_manager.get_state(self.pet_id)
        new_action = PetLoader.get_action_for_state(state_num, self.is_moving)
        
        # V9: 检查是否需要切换动画 (Requirements 7.3)
        if new_action != self.current_action:
            self._switch_animation(new_action, stage, is_halloween)
        
        # 如果没有动画器，使用静态图像加载
        if self.frame_animator is None or not self.frame_animator.frames:
            # 加载图像 (fallback to static image)
            self.current_pixmap = self._load_image(stage)
        else:
            # V9: 从动画器获取当前帧
            self.current_pixmap = self.frame_animator.get_current_frame()
        
        # 应用滤镜
        if self.is_dormant and self.current_pixmap:
            # 休眠状态：灰度滤镜
            self.current_pixmap = self._apply_dormant_filter(self.current_pixmap)
        elif is_halloween and self.current_pixmap:
            # Kiroween模式：应用幽灵滤镜 (Requirements 4.1)
            self.current_pixmap = self._apply_ghost_filter_kiroween(self.current_pixmap)
        
        # 更新位置
        if self.is_dormant:
            self._move_to_bottom()
            self.stop_floating()
        else:
            self.start_floating()
        
        # 调整窗口大小
        if self.current_pixmap:
            self.setFixedSize(self.current_pixmap.size())
        
        self.update()
    
    def _switch_animation(self, new_action: str, stage: str, is_halloween: bool = False) -> None:
        """
        V9: 切换动画状态 (Requirements 7.3)
        
        - 加载新动作的帧序列
        - 重置帧计数器
        - 根据状态设置帧率
        
        Args:
            new_action: 新动作名称
            stage: 成长阶段
            is_halloween: 是否为万圣节模式
        """
        self.current_action = new_action
        
        # 加载新动作的帧序列
        frames = PetLoader.load_action_frames(self.pet_id, new_action)
        
        # 缩放帧到正确尺寸
        target_size = PetRenderer.calculate_size(self.pet_id, stage)
        scaled_frames = []
        for frame in frames:
            if frame and not frame.isNull():
                scaled_frame = PetRenderer.scale_frame(frame, target_size)
                scaled_frames.append(scaled_frame)
            else:
                # 使用占位符
                placeholder = PetRenderer.draw_placeholder(self.pet_id, target_size)
                scaled_frames.append(placeholder)
        
        # 创建或更新动画器
        if self.frame_animator is None:
            self.frame_animator = FrameAnimator(scaled_frames)
            self.frame_animator.set_on_frame_changed(self._on_frame_changed)
        else:
            self.frame_animator.set_frames(scaled_frames)
        
        # 根据状态设置帧率 (Requirements 7.4)
        if self.is_dormant:
            fps = FrameAnimator.DORMANT_FPS  # 4fps for dormant
        else:
            fps = FrameAnimator.NORMAL_FPS   # 8fps for normal
        
        # 启动动画
        self.frame_animator.start(fps)
    
    def _on_frame_changed(self) -> None:
        """
        V9: 帧变化回调 (Requirements 7.1)
        
        当动画帧变化时更新显示
        """
        if self.frame_animator:
            self.current_pixmap = self.frame_animator.get_current_frame()
            
            # 应用滤镜
            theme_mode = self.growth_manager.get_theme_mode()
            is_halloween = theme_mode == "halloween"
            
            if self.is_dormant and self.current_pixmap:
                self.current_pixmap = self._apply_dormant_filter(self.current_pixmap)
            elif is_halloween and self.current_pixmap:
                self.current_pixmap = self._apply_ghost_filter_kiroween(self.current_pixmap)
            
            self.update()
    
    def update_display(self) -> None:
        """
        更新显示（带状态转换动画支持）
        
        V7.1: 检测状态转换并触发相应动画
        - 休眠→幼年: 浮起动画 (Requirements 5.3)
        - 幼年→成年: 尺寸增大动画 (Requirements 5.6)
        """
        # 记录旧状态 (0=dormant, 1=baby, 2=adult)
        old_dormant = self.is_dormant
        
        # 获取新状态
        new_state = self.growth_manager.get_state(self.pet_id)
        new_dormant = self.growth_manager.is_dormant(self.pet_id)
        
        # 检测休眠→幼年转换 (Requirements 5.3)
        if old_dormant and not new_dormant:
            self._animate_dormant_to_baby()
        # 检测幼年→成年转换 (Requirements 5.6)
        # State 1 = baby, State 2 = adult
        elif not old_dormant and new_state == 2:
            self._animate_baby_to_adult()
        else:
            # 无动画，直接刷新
            self.refresh_display()
    
    def _animate_dormant_to_baby(self) -> None:
        """
        休眠→幼年转换动画 (Requirements 5.3)
        
        动画效果：从屏幕底部浮起到中心位置
        - 先刷新显示（恢复正常颜色，启用拖拽）
        - 然后执行浮起动画
        
        V8: 设置 just_awakened 状态并启动 10 秒计时器 (Requirements 4.2)
        """
        # 先刷新显示状态（恢复颜色，设置 is_dormant=False）
        self.refresh_display()
        
        # V8: 设置 just_awakened 状态 (Requirements 4.2)
        self._start_just_awakened_timer()
        
        # 获取屏幕信息
        screen = QApplication.primaryScreen()
        if not screen:
            return
        
        geometry = screen.availableGeometry()
        
        # 起始位置：屏幕底部
        start_x = geometry.width() - self.width() - 100
        start_y = geometry.height()  # 从屏幕底部外开始
        
        # 目标位置：屏幕中心偏右下
        end_x = geometry.width() - self.width() - 100
        end_y = geometry.height() - self.height() - 100
        
        # 移动到起始位置
        self.move(start_x, start_y)
        
        # 创建浮起动画
        self.float_up_animation = QPropertyAnimation(self, b"pos")
        self.float_up_animation.setDuration(800)  # 800ms 动画
        self.float_up_animation.setStartValue(QPoint(start_x, start_y))
        self.float_up_animation.setEndValue(QPoint(end_x, end_y))
        self.float_up_animation.setEasingCurve(QEasingCurve.Type.OutBack)  # 弹性效果
        
        # 动画完成后更新 original_pos
        def on_finished():
            self.original_pos = self.pos()
            # 播放升级音效
            from sound_manager import get_sound_manager
            get_sound_manager().play_pet_upgrade()
        
        self.float_up_animation.finished.connect(on_finished)
        self.float_up_animation.start()
    
    def _start_just_awakened_timer(self) -> None:
        """
        V8: 启动 just_awakened 计时器 (Requirements 4.2)
        
        - 设置 just_awakened=True
        - 启动 10 秒计时器
        - 计时器结束后清除 just_awakened 标志
        """
        # 停止现有计时器（如果有）
        if self.just_awakened_timer is not None:
            self.just_awakened_timer.stop()
            self.just_awakened_timer = None
        
        # 设置 just_awakened 状态
        self.just_awakened = True
        self.update()  # 触发重绘以显示气泡
        
        # 启动 10 秒计时器
        self.just_awakened_timer = QTimer()
        self.just_awakened_timer.setSingleShot(True)
        self.just_awakened_timer.timeout.connect(self._clear_just_awakened)
        self.just_awakened_timer.start(TUTORIAL_CONFIG["awakened_duration"])
    
    def _clear_just_awakened(self) -> None:
        """
        V8: 清除 just_awakened 状态 (Requirements 4.2)
        """
        self.just_awakened = False
        self.just_awakened_timer = None
        self.update()  # 触发重绘以隐藏气泡
    
    def _animate_baby_to_adult(self) -> None:
        """
        幼年→成年转换动画 (Requirements 5.6)
        
        动画效果：尺寸增大 1.5x
        - 先刷新显示（加载成年图像）
        - 然后执行尺寸增大动画
        """
        # 记录当前位置
        current_pos = self.pos()
        
        # 刷新显示（加载成年图像，尺寸会自动变大）
        self.refresh_display()
        
        # 播放升级音效
        from sound_manager import get_sound_manager
        get_sound_manager().play_pet_upgrade()
        
        # 保持位置不变（尺寸变化可能导致位置偏移）
        self.move(current_pos)
        self.original_pos = current_pos
    
    def _load_image(self, stage: str) -> QPixmap:
        """
        智能加载图像
        
        优先级：
        1. .gif 文件
        2. 序列帧 _0.png
        3. 单张 .png
        4. V7 几何占位符 (PetRenderer)
        
        Args:
            stage: 图像阶段 ("baby" 或 "adult")
            
        Returns:
            加载的 QPixmap
        """
        base_path = f"assets/{self.pet_id}"
        base_name = f"{stage}_idle"
        
        # 尝试加载顺序
        paths_to_try = [
            f"{base_path}/{base_name}.gif",
            f"{base_path}/{base_name}_0.png",
            f"{base_path}/{base_name}.png",
            f"{base_path}/idle.gif",
            f"{base_path}/idle_0.png", 
            f"{base_path}/idle.png",
        ]
        
        for path in paths_to_try:
            if os.path.exists(path):
                # V7: Check for empty files (0 bytes)
                if os.path.getsize(path) == 0:
                    print(f"[PetCore] Empty file, skipping: {path}")
                    continue
                    
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    print(f"[PetCore] Loaded image: {path}")
                    # V7: Use PetRenderer for size calculation
                    return self._scale_to_v7_size(pixmap, stage)
        
        # All attempts failed, generate V7 geometric placeholder
        print(f"[PetCore] Image not found, generating V7 placeholder: {self.pet_id}")
        return self._create_placeholder(stage)
    
    def _scale_to_limit(self, pixmap: QPixmap) -> QPixmap:
        """
        V6.1: 将图像缩放到限制尺寸内
        
        V7.1: Simplified to use BASE_SIZE for all V7 pets
        Requirements: 10.2
        """
        # V7.1: Use BASE_SIZE for all pets (ray uses RAY_MULTIPLIER in PetRenderer)
        max_size = BASE_SIZE
        
        if pixmap.width() <= max_size and pixmap.height() <= max_size:
            return pixmap
        
        # 保持宽高比缩放
        return pixmap.scaled(
            max_size, max_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
    
    def _scale_to_v7_size(self, pixmap: QPixmap, stage: str) -> QPixmap:
        """
        V7: 使用 PetRenderer 计算尺寸并缩放图像
        
        Args:
            pixmap: 原始图像
            stage: 成长阶段 ('baby', 'adult', 'dormant')
            
        Returns:
            缩放后的图像
        """
        # V7 pets use PetRenderer for size calculation
        if self.pet_id in V7_PETS:
            target_size = PetRenderer.calculate_size(self.pet_id, stage)
        else:
            # V7.1: Legacy pets use BASE_SIZE (Requirements: 10.2)
            target_size = BASE_SIZE
        
        if pixmap.width() <= target_size and pixmap.height() <= target_size:
            return pixmap
        
        # 保持宽高比缩放
        return pixmap.scaled(
            target_size, target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
    
    def _create_placeholder(self, stage: str = 'baby') -> QPixmap:
        """
        创建占位符
        
        V7宠物使用几何图形占位符 (PetRenderer)
        其他宠物使用彩色椭圆占位符
        
        Args:
            stage: 成长阶段，用于计算V7宠物尺寸
            
        Returns:
            占位符 QPixmap
        """
        # V7 pets use geometric placeholders
        if self.pet_id in V7_PETS:
            size = PetRenderer.calculate_size(self.pet_id, stage)
            return PetRenderer.draw_placeholder(self.pet_id, size)
        
        # Legacy pets use colored ellipse placeholder
        size = 128
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 获取宠物颜色
        color_hex = self.PET_COLORS.get(self.pet_id, '#888888')
        color = QColor(color_hex)
        
        # 绘制椭圆
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(10, 20, size - 20, size - 40)
        
        # 绘制名称
        painter.setPen(QColor('white'))
        font = QFont('Arial', 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, self.pet_id)
        
        painter.end()
        return pixmap
    
    def _apply_dormant_filter(self, pixmap: QPixmap) -> QPixmap:
        """
        应用休眠滤镜（灰度 + 60%透明度）
        
        Args:
            pixmap: 原始图像
            
        Returns:
            处理后的图像
        """
        image = pixmap.toImage()
        
        # 转换为灰度并降低透明度
        for y in range(image.height()):
            for x in range(image.width()):
                pixel = image.pixelColor(x, y)
                if pixel.alpha() > 0:
                    # 灰度化
                    gray = int(0.299 * pixel.red() + 0.587 * pixel.green() + 0.114 * pixel.blue())
                    # 降低透明度到60%
                    new_alpha = int(pixel.alpha() * 0.6)
                    image.setPixelColor(x, y, QColor(gray, gray, gray, new_alpha))
        
        return QPixmap.fromImage(image)
    
    def _apply_ghost_filter_kiroween(self, pixmap: QPixmap) -> QPixmap:
        """
        应用Kiroween幽灵滤镜 (Requirements 4.1, 6.1, 6.4)
        
        V9: 使用 NightFilter 根据宠物种类应用不同颜色滤镜
        
        颜色分组:
        - puffer, starfish → 绿色 #00FF88 (0.2 透明度)
        - crab, jelly, ray → 紫色 #8B00FF (0.2 透明度)
        
        Args:
            pixmap: 原始图像
            
        Returns:
            应用夜间滤镜后的图像
            
        Requirements: 6.1, 6.4
        """
        from theme_manager import NightFilter
        
        # V9: 使用 NightFilter 应用分类颜色滤镜 (Requirements 6.1, 6.2, 6.3)
        # 对几何占位符也应用滤镜 (Requirements 6.4)
        return NightFilter.apply_filter(pixmap, self.pet_id)
    
    def _move_to_bottom(self) -> None:
        """将宠物移动到屏幕右下方（休眠状态位置）
        
        Requirements 1.1, 1.2: At least 80px margin from right and bottom edges
        """
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            # 右下方位置，距离边缘至少80像素
            x = geometry.width() - self.width() - 80  # 距右边80像素
            y = geometry.height() - self.height() - 80  # 距底部80像素
            self.move(x, y)
    
    def _move_to_right_bottom(self) -> None:
        """将宠物移动到屏幕右下方（非休眠状态初始位置）
        
        Requirements 1.3: Consistent bottom-right positioning with at least 80px margin
        """
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            # 非休眠状态初始位置，距离边缘至少80像素（稍微靠内一些以区分休眠位置）
            x = geometry.width() - self.width() - 100  # 距右边100像素
            y = geometry.height() - self.height() - 100  # 距底部100像素
            self.move(x, y)
            self.original_pos = self.pos()
    
    def start_floating(self) -> None:
        """开始漂浮动画"""
        if self.float_timer is None:
            self.float_timer = QTimer(self)
            self.float_timer.timeout.connect(self._update_float)
            self.float_timer.start(100)  # 100ms 更新一次
            # 如果没有位置，移动到右下方
            if self.original_pos is None or self.original_pos == QPoint(0, 0):
                self._move_to_right_bottom()
            else:
                self.original_pos = self.pos()
    
    def stop_floating(self) -> None:
        """停止漂浮动画"""
        if self.float_timer:
            self.float_timer.stop()
            self.float_timer = None
        if self.original_pos:
            self.move(self.original_pos)
    
    def _update_float(self) -> None:
        """更新漂浮位置"""
        if self.is_dragging or self.is_dormant:
            return
        
        import math
        self.float_offset += 0.1
        offset_y = int(math.sin(self.float_offset) * 5)  # 上下浮动5像素
        
        if self.original_pos:
            self.move(self.original_pos.x(), self.original_pos.y() + offset_y)
    
    def set_moving(self, moving: bool) -> None:
        """
        V9: 设置移动状态 (Requirements 7.3)
        
        当移动状态改变时，触发动画切换
        - 成年期移动时使用 swim 动画
        - 成年期静止时使用 sleep 动画
        
        Args:
            moving: 是否在移动
        """
        if self.is_moving != moving:
            self.is_moving = moving
            # 触发动画切换
            self.refresh_display()
    
    # ========== V7.1 愤怒机制 ==========
    
    def trigger_anger(self) -> None:
        """
        触发愤怒状态 (Requirements 1.2, 1.3)
        
        - 设置 is_angry = True
        - 播放愤怒音效
        - 变红色（重新加载图像）
        - 开始抖动动画
        - 5秒后自动恢复
        """
        self.is_angry = True
        self.anger_original_pos = self.pos()
        
        # 播放愤怒音效
        from sound_manager import get_sound_manager
        get_sound_manager().play_pet_angry()
        
        # 变红色 - 重新加载图像
        self._reload_with_anger_color()
        
        # 开始抖动动画
        self._start_shake_animation()
        
        # 5秒后恢复
        self.anger_timer = QTimer()
        self.anger_timer.timeout.connect(self.calm_down)
        self.anger_timer.setSingleShot(True)
        self.anger_timer.start(5000)
    
    def _reload_with_anger_color(self) -> None:
        """
        重新加载图像，使用愤怒动画 (Requirements 4.3)
        
        V9: 加载 angry 动作的序列帧动画
        - 尝试加载 assets/{pet_id}/angry/{pet_id}_angry_{0-3}.png
        - 失败时回退到红色几何占位符
        """
        stage = self.growth_manager.get_image_stage(self.pet_id)
        target_size = PetRenderer.calculate_size(self.pet_id, stage)
        
        # V9: 尝试加载 angry 动画帧 (Requirements 4.3)
        frames = PetLoader.load_action_frames(self.pet_id, 'angry')
        
        # 检查是否成功加载了真实的 angry 动画（非占位符）
        has_real_frames = False
        for frame in frames:
            if frame and not frame.isNull():
                # 检查是否是真实图像（非占位符）
                angry_path = PetLoader.get_frame_path(self.pet_id, 'angry', 0)
                if os.path.exists(angry_path) and os.path.getsize(angry_path) > 0:
                    has_real_frames = True
                    break
        
        if has_real_frames:
            # 缩放帧到正确尺寸
            scaled_frames = []
            for frame in frames:
                if frame and not frame.isNull():
                    scaled_frame = PetRenderer.scale_frame(frame, target_size)
                    scaled_frames.append(scaled_frame)
                else:
                    # 使用红色占位符作为回退
                    placeholder = PetRenderer.draw_placeholder_colored(
                        self.pet_id, target_size, '#FF0000'
                    )
                    scaled_frames.append(placeholder)
            
            # 更新动画器使用 angry 帧
            if self.frame_animator is None:
                self.frame_animator = FrameAnimator(scaled_frames)
                self.frame_animator.set_on_frame_changed(self._on_frame_changed)
            else:
                self.frame_animator.set_frames(scaled_frames)
            
            # 启动动画（使用正常帧率）
            self.frame_animator.start(FrameAnimator.NORMAL_FPS)
            self.current_action = 'angry'
            
            # 获取当前帧
            self.current_pixmap = self.frame_animator.get_current_frame()
        else:
            # 回退到红色几何占位符
            if self.pet_id in V7_PETS:
                self.current_pixmap = PetRenderer.draw_placeholder_colored(
                    self.pet_id, target_size, '#FF0000'
                )
            else:
                # Legacy pets - apply red tint
                self.current_pixmap = self._load_image(stage)
                self.current_pixmap = self._apply_red_tint(self.current_pixmap)
        
        if self.current_pixmap:
            self.setFixedSize(self.current_pixmap.size())
        self.update()
    
    def _apply_red_tint(self, pixmap: QPixmap) -> QPixmap:
        """应用红色滤镜（用于非V7宠物的愤怒状态）"""
        image = pixmap.toImage()
        
        for y in range(image.height()):
            for x in range(image.width()):
                pixel = image.pixelColor(x, y)
                if pixel.alpha() > 0:
                    # 增加红色分量
                    new_red = min(255, pixel.red() + 100)
                    image.setPixelColor(x, y, QColor(new_red, pixel.green() // 2, pixel.blue() // 2, pixel.alpha()))
        
        return QPixmap.fromImage(image)
    
    def _start_shake_animation(self) -> None:
        """
        开始抖动动画 (Requirements 1.3)
        
        QTimer at 50ms interval, random x offset ±10px
        """
        def shake():
            if not self.is_angry:
                return
            offset_x = random.randint(-10, 10)
            if self.anger_original_pos:
                new_pos = QPoint(
                    self.anger_original_pos.x() + offset_x,
                    self.anger_original_pos.y()
                )
                self.move(new_pos)
        
        self.shake_timer = QTimer()
        self.shake_timer.timeout.connect(shake)
        self.shake_timer.start(50)  # 50ms 抖动一次
    
    def calm_down(self) -> None:
        """
        恢复正常状态 (Requirements 1.4, 1.5)
        
        - 重置 is_angry
        - 停止计时器
        - 恢复位置和颜色
        """
        self.is_angry = False
        self.click_times.clear()
        
        # 停止抖动计时器
        if self.shake_timer:
            self.shake_timer.stop()
            self.shake_timer = None
        
        # 停止愤怒计时器
        if self.anger_timer:
            self.anger_timer.stop()
            self.anger_timer = None
        
        # 恢复位置
        if self.anger_original_pos:
            self.move(self.anger_original_pos)
            self.anger_original_pos = None
        
        # 恢复原色 - 重新加载图像
        self.refresh_display()
    
    # ========== V8 引导气泡系统 ==========
    
    def get_tutorial_text(self) -> str:
        """
        V8: 获取当前应显示的引导文字 (Requirements 4.1, 4.2, 4.3)
        
        Returns:
            - "右键点击我！(Right Click Me!)" for dormant state
            - "试试拖拽我！(Try Dragging!)" for just_awakened state
            - "连点5下有惊喜！(Click 5x for Anger!)" for idle hint
            - Empty string otherwise
        """
        if self.is_dormant:
            return TUTORIAL_BUBBLES["dormant"]
        elif self.just_awakened:
            return TUTORIAL_BUBBLES["just_awakened"]
        elif self.show_idle_hint:
            return TUTORIAL_BUBBLES["idle_hint"]
        return ""
    
    def _draw_tutorial_bubble(self, painter: QPainter, text: str) -> None:
        """
        V8: 绘制引导文字气泡 (Requirements 4.4, 4.5)
        
        - 位置：宠物头顶上方
        - 背景：半透明黑色圆角矩形 (rgba 0,0,0,180)
        - 文字：黄色 (#FFFF00) + 黑色描边 (4 offset draws)
        
        Args:
            painter: QPainter 实例
            text: 要显示的文字
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
        
        # 绘制半透明黑色背景 (Requirements 4.5)
        painter.setBrush(QColor(0, 0, 0, TUTORIAL_CONFIG["bg_alpha"]))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bubble_x, bubble_y, bubble_width, bubble_height, 5, 5)
        
        # 文字起始位置
        text_x = bubble_x + bubble_padding
        text_y = bubble_y + bubble_padding + fm.ascent()
        
        # 绘制文字描边（黑色，4个方向偏移）(Requirements 4.4)
        painter.setPen(QColor(TUTORIAL_CONFIG["outline_color"]))
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            for i, line in enumerate(lines):
                painter.drawText(text_x + dx, text_y + i * fm.height() + dy, line)
        
        # 绘制文字（黄色）(Requirements 4.4)
        painter.setPen(QColor(TUTORIAL_CONFIG["text_color"]))
        for i, line in enumerate(lines):
            painter.drawText(text_x, text_y + i * fm.height(), line)
    
    # ========== 绘制 ==========
    
    def paintEvent(self, event: QPaintEvent) -> None:
        """绘制宠物
        
        V7.1: 应用挤压变换 (Requirements 2.1)
        - 当 squash_factor != 1.0 时，应用缩放变换
        - 水平挤压，垂直拉伸（保持体积感）
        
        V8: 绘制引导气泡 (Requirements 4.1, 4.2, 4.3)
        - 调用 get_tutorial_text() 获取当前文字
        - 调用 _draw_tutorial_bubble() 绘制气泡
        """
        if self.current_pixmap:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # V7.1: 应用挤压变换 (Requirements 2.1)
            if self.squash_factor != 1.0:
                # 计算中心点
                cx = self.width() / 2
                cy = self.height() / 2
                
                # 移动到中心，应用缩放，再移回
                painter.translate(cx, cy)
                # 水平挤压，垂直拉伸（保持体积感）
                painter.scale(self.squash_factor, 2.0 - self.squash_factor)
                painter.translate(-cx, -cy)
            
            painter.drawPixmap(0, 0, self.current_pixmap)
            
            # V8: 绘制引导气泡 (Requirements 4.1, 4.2, 4.3)
            # 重置变换以正确绘制气泡
            painter.resetTransform()
            tutorial_text = self.get_tutorial_text()
            if tutorial_text:
                self._draw_tutorial_bubble(painter, tutorial_text)
            
            painter.end()
    
    # ========== 交互 ==========
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """鼠标按下事件
        
        V7.1: 实现愤怒机制点击追踪 (Requirements 1.1)
        - 记录点击时间戳
        - 过滤保留2秒内的点击
        - 检查是否达到5次触发愤怒
        
        V7.1: 实现拖拽物理 (Requirements 2.1, 2.4)
        - 非休眠状态开始拖拽时设置 squash_factor = 0.8
        - 休眠状态禁止所有互动（拖拽和愤怒机制）
        
        V9: Stage 1 幼年期交互限制 (Requirements 3.3, 3.5)
        - Stage 1 时忽略左键点击
        - 保留右键菜单功能
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # V7.1: 休眠状态禁止所有互动 (Requirements 2.4, 5.2)
            # 用户必须完成至少一个任务才能与宠物互动
            if self.is_dormant:
                return
            
            # V9: Stage 1 (Baby) 禁止左键点击 (Requirements 3.3)
            # 幼年期宠物不响应点击，但可以自主移动
            current_state = self.growth_manager.get_state(self.pet_id)
            if current_state == 1:  # Stage 1 = Baby
                return
            
            # V7.1: 愤怒机制点击追踪（仅非休眠状态）
            current_time = time.time()
            self.click_times.append(current_time)
            
            # 保留最近2秒内的点击
            self.click_times = [t for t in self.click_times if current_time - t <= 2.0]
            
            # 检查是否触发愤怒 (5次点击在2秒内)
            if len(self.click_times) >= 5 and not self.is_angry:
                self.trigger_anger()
            
            self.is_dragging = True
            self.drag_offset = event.pos()
            self.original_pos = self.pos()
            self.last_drag_pos = event.globalPosition().toPoint()
            
            # V7.1: 开始拖拽时应用挤压效果 (Requirements 2.1)
            self.squash_factor = 0.8
            
            # V9: 设置移动状态以切换动画 (Requirements 7.3)
            self.set_moving(True)
            
            self.update()
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """鼠标移动事件（拖拽）
        
        V7.1: 实现速度相关的挤压效果 (Requirements 2.2)
        - 根据拖拽速度调整 squash_factor
        - 速度越快，挤压越明显（最小 0.6）
        
        V9: Stage 1 幼年期交互限制 (Requirements 3.4)
        - Stage 1 时忽略拖拽事件
        
        V9: 拖拽动画切换 (Requirements 4.4, 4.5)
        - 水平拖拽使用 drag_h 动画
        - 垂直拖拽使用 drag_v 动画
        """
        if self.is_dragging and not self.is_dormant:
            # V9: Stage 1 (Baby) 禁止拖拽 (Requirements 3.4)
            # 幼年期宠物不响应拖拽，但可以自主移动
            current_state = self.growth_manager.get_state(self.pet_id)
            if current_state == 1:  # Stage 1 = Baby
                return
            
            current_global_pos = event.globalPosition().toPoint()
            new_pos = current_global_pos - self.drag_offset
            
            # V7.1: 计算拖拽速度并调整挤压系数 (Requirements 2.2)
            if self.last_drag_pos is not None:
                delta = current_global_pos - self.last_drag_pos
                delta_x = delta.x()
                delta_y = delta.y()
                speed = abs(delta_x) + abs(delta_y)
                # 速度越快，squash_factor 越小（最小 0.6）
                self.squash_factor = max(0.6, 1.0 - speed * 0.01)
                
                # V9: 拖拽动画切换 (Requirements 4.4, 4.5)
                # 只有 Stage 2 (Adult) 才使用拖拽动画
                if current_state == 2 and not self.is_angry:
                    # 判断拖拽方向：水平 vs 垂直
                    if abs(delta_x) > abs(delta_y) and abs(delta_x) > 2:
                        # 水平拖拽 - 使用 drag_h 动画
                        self._switch_to_drag_animation('drag_h', delta_x)
                    elif abs(delta_y) > abs(delta_x) and abs(delta_y) > 2:
                        # 垂直拖拽 - 使用 drag_v 动画
                        self._switch_to_drag_animation('drag_v', delta_y)
                
                self.update()
            
            self.last_drag_pos = current_global_pos
            self.move(new_pos)
            self.original_pos = new_pos
    
    def _switch_to_drag_animation(self, drag_action: str, delta: int) -> None:
        """
        V9: 切换到拖拽动画 (Requirements 4.4, 4.5, 5.1, 5.2, 5.3, 5.4)
        
        Args:
            drag_action: 'drag_h' 或 'drag_v'
            delta: 拖拽增量（用于判断翻转方向）
            
        V9 翻转逻辑 (Requirements 5.1, 5.2, 5.3, 5.4):
        - 水平拖拽 (drag_h): delta_x < 0 时水平镜像
        - 垂直拖拽 (drag_v): delta_y > 0 时垂直翻转
        """
        # 判断是否需要翻转
        is_horizontal_drag = (drag_action == 'drag_h')
        if is_horizontal_drag:
            need_flip = FlipTransform.should_flip_horizontal(delta)
        else:
            need_flip = FlipTransform.should_flip_vertical(delta)
        
        # 检查是否需要更新动画（动作改变或翻转状态改变）
        flip_state_key = f"{drag_action}_{need_flip}"
        if hasattr(self, '_current_flip_state') and self._current_flip_state == flip_state_key:
            return
        
        # 如果只是翻转状态改变，但动作相同，只需要更新帧的翻转
        if self.current_action == drag_action and hasattr(self, '_current_flip_state'):
            # 只更新翻转状态
            self._update_drag_flip(drag_action, delta)
            self._current_flip_state = flip_state_key
            return
        
        stage = self.growth_manager.get_image_stage(self.pet_id)
        target_size = PetRenderer.calculate_size(self.pet_id, stage)
        
        # 加载拖拽动画帧
        frames = PetLoader.load_action_frames(self.pet_id, drag_action)
        
        # 缩放帧到正确尺寸，并应用翻转
        scaled_frames = []
        for frame in frames:
            if frame and not frame.isNull():
                scaled_frame = PetRenderer.scale_frame(frame, target_size)
                # V9: 应用翻转变换 (Requirements 5.1, 5.2, 5.3, 5.4)
                scaled_frame = FlipTransform.apply_flip_for_drag(
                    scaled_frame, delta, delta, is_horizontal_drag
                )
                scaled_frames.append(scaled_frame)
            else:
                # 使用占位符作为回退
                placeholder = PetRenderer.draw_placeholder(self.pet_id, target_size)
                # 也对占位符应用翻转
                placeholder = FlipTransform.apply_flip_for_drag(
                    placeholder, delta, delta, is_horizontal_drag
                )
                scaled_frames.append(placeholder)
        
        # 更新动画器
        if self.frame_animator is None:
            self.frame_animator = FrameAnimator(scaled_frames)
            self.frame_animator.set_on_frame_changed(self._on_frame_changed)
        else:
            self.frame_animator.set_frames(scaled_frames)
        
        # 启动动画
        self.frame_animator.start(FrameAnimator.NORMAL_FPS)
        self.current_action = drag_action
        self._current_flip_state = flip_state_key
    
    def _update_drag_flip(self, drag_action: str, delta: int) -> None:
        """
        V9: 更新拖拽动画的翻转状态 (Requirements 5.1, 5.2, 5.3, 5.4)
        
        当拖拽方向改变时，重新加载帧并应用新的翻转。
        
        Args:
            drag_action: 'drag_h' 或 'drag_v'
            delta: 拖拽增量
        """
        stage = self.growth_manager.get_image_stage(self.pet_id)
        target_size = PetRenderer.calculate_size(self.pet_id, stage)
        is_horizontal_drag = (drag_action == 'drag_h')
        
        # 重新加载并应用翻转
        frames = PetLoader.load_action_frames(self.pet_id, drag_action)
        
        scaled_frames = []
        for frame in frames:
            if frame and not frame.isNull():
                scaled_frame = PetRenderer.scale_frame(frame, target_size)
                scaled_frame = FlipTransform.apply_flip_for_drag(
                    scaled_frame, delta, delta, is_horizontal_drag
                )
                scaled_frames.append(scaled_frame)
            else:
                placeholder = PetRenderer.draw_placeholder(self.pet_id, target_size)
                placeholder = FlipTransform.apply_flip_for_drag(
                    placeholder, delta, delta, is_horizontal_drag
                )
                scaled_frames.append(placeholder)
        
        # 更新动画器帧
        if self.frame_animator:
            self.frame_animator.set_frames(scaled_frames)
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """鼠标释放事件
        
        V7.1: 释放时触发拉伸恢复动画 (Requirements 2.3)
        V9: 停止移动状态以切换回静止动画 (Requirements 7.3)
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.last_drag_pos = None
            
            # V9: 停止移动状态以切换回静止动画 (Requirements 7.3)
            self.set_moving(False)
            
            # V7.1: 触发拉伸恢复动画 (Requirements 2.3)
            if self.squash_factor < 1.0:
                self._animate_stretch_back()
    
    def _animate_stretch_back(self) -> None:
        """
        动画恢复正常形状 (Requirements 2.3)
        
        逐渐将 squash_factor 从当前值恢复到 1.0
        """
        def restore():
            if self.squash_factor < 1.0:
                self.squash_factor = min(1.0, self.squash_factor + 0.1)
                self.update()
                if self.squash_factor < 1.0:
                    QTimer.singleShot(16, restore)  # ~60fps
        restore()
    
    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """Right-click context menu - Kiroween pixel style.
        
        Requirements 4.1, 4.2, 4.3, 4.4: Use ui_style for pixel-art menu styling
        WARNING: The menu of the deep reveals its secrets...
        """
        menu = QMenu(self)
        
        # Use ui_style to get current theme's menu style
        current_mode = self.growth_manager.get_theme_mode()
        menu.setStyleSheet(ui_style.get_menu_stylesheet(current_mode))
        
        # 1. Tasks & Cycle
        task_action = menu.addAction("📋 Tasks")
        task_action.triggered.connect(self.task_window_requested.emit)
        
        # 2. Open Inventory
        inventory_action = menu.addAction("🎒 Inventory")
        inventory_action.triggered.connect(self.inventory_requested.emit)
        
        menu.addSeparator()
        
        # 3. Environment Settings submenu
        env_menu = menu.addMenu("🌍 Environment")
        env_menu.setStyleSheet(menu.styleSheet())
        
        # Auto day/night cycle
        auto_sync = env_menu.addAction("⏰ Auto Day/Night")
        auto_sync.setCheckable(True)
        auto_sync.setChecked(self.growth_manager.get_auto_time_sync())
        auto_sync.triggered.connect(self._toggle_auto_sync)
        
        # Toggle day/night
        toggle_mode = env_menu.addAction("🌙 Toggle Mode")
        toggle_mode.triggered.connect(self._toggle_day_night)
        
        # V7.1: Environment settings window (Requirements 3.4)
        env_window_action = env_menu.addAction("⚙️ Settings")
        env_window_action.triggered.connect(self.environment_requested.emit)
        
        menu.addSeparator()
        
        # 4. Release (only for non-base pets)
        if self.pet_id != 'puffer':
            release_action = menu.addAction("🌊 Release")
            release_action.triggered.connect(lambda: self.release_requested.emit(self.pet_id))
            menu.addSeparator()
        
        # Status info
        state = self.growth_manager.get_state(self.pet_id)
        progress = self.growth_manager.get_progress(self.pet_id)
        state_names = {0: "💤Dormant", 1: "🐣Baby", 2: "🐟Adult"}
        info_action = menu.addAction(f"{state_names.get(state, '?')} | ⭐{progress}/3")
        info_action.setEnabled(False)
        
        menu.exec(event.globalPos())
    
    def _toggle_auto_sync(self, checked: bool) -> None:
        """Toggle auto time sync."""
        self.growth_manager.set_auto_time_sync(checked)
    
    def _toggle_day_night(self) -> None:
        """Toggle day/night mode."""
        current = self.growth_manager.get_theme_mode()
        new_mode = "halloween" if current == "normal" else "normal"
        self.growth_manager.set_theme_mode(new_mode)
    
    def _on_reset_cycle(self) -> None:
        """Reset growth cycle."""
        self.growth_manager.reset_cycle(self.pet_id)
        self.refresh_display()
