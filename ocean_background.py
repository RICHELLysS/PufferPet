"""
🌊 Deep Sea Undead Empire - Ocean Background Module

WARNING: This module governs the immersive deep dive background...

This module manages:
- Fullscreen frameless window: Cover desktop icons, create immersion
- Seabed background image: Load and display ocean floor scene
- Theme filter: Apply blue/purple filter based on theme
- Window layer management: Ensure background above desktop, below pets
- Bubble/ghost fire particle system: Dynamic particle effects for immersion

⚠️ WARNING: The journey into the abyss is about to begin...
When deep dive mode activates, you will be immersed in the underwater world!

Author: Deep Sea Code Captain
Version: 5.0 (Deep Dive Edition)
"""
import os
import ctypes
import random
import math
from typing import Optional, List, TYPE_CHECKING

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, QRect, QPointF
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPaintEvent, QScreen, QBrush, QPen, QRadialGradient

if TYPE_CHECKING:
    from theme_manager import ThemeManager


class BubbleParticle:
    """
    🫧 气泡/鬼火粒子
    
    A soul rising from the depths... or just a bubble.
    These ethereal particles drift upward through the abyss,
    creating an immersive underwater atmosphere.
    
    ⚠️ 警告：深渊中的灵魂正在上升...
    """
    
    # 粒子大小范围
    MIN_SIZE = 5
    MAX_SIZE = 20
    
    # 速度范围（像素/帧）
    MIN_SPEED = 1.0
    MAX_SPEED = 3.0
    
    # 透明度范围
    MIN_OPACITY = 0.3
    MAX_OPACITY = 0.8
    
    # 摇摆范围
    MIN_WOBBLE = -0.5
    MAX_WOBBLE = 0.5
    
    # 摇摆周期（帧数）
    WOBBLE_PERIOD = 60
    
    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        is_ghost_fire: bool = False,
        x: Optional[float] = None,
        y: Optional[float] = None
    ):
        """
        初始化粒子
        
        WARNING: Summoning a spirit from the deep...
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            is_ghost_fire: 是否为鬼火模式
            x: 初始X坐标（可选，默认随机）
            y: 初始Y坐标（可选，默认从底部开始）
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_ghost_fire = is_ghost_fire
        
        # 位置
        self.x = x if x is not None else random.randint(0, screen_width)
        self.y = y if y is not None else screen_height + 20  # 从屏幕底部开始
        
        # 大小
        self.size = random.randint(self.MIN_SIZE, self.MAX_SIZE)
        
        # 速度
        self.speed = random.uniform(self.MIN_SPEED, self.MAX_SPEED)
        
        # 透明度
        self.opacity = random.uniform(self.MIN_OPACITY, self.MAX_OPACITY)
        
        # 摇摆参数
        self.wobble_amplitude = random.uniform(self.MIN_WOBBLE, self.MAX_WOBBLE)
        self.wobble_offset = random.uniform(0, 2 * math.pi)  # 随机相位
        self.frame_count = 0
        
        # 颜色
        self._init_color()
    
    def _init_color(self) -> None:
        """
        初始化粒子颜色
        
        WARNING: The spirits choose their own hue...
        """
        alpha = int(self.opacity * 255)
        
        if self.is_ghost_fire:
            # 鬼火使用绿色/紫色
            ghost_colors = [
                QColor(0, 255, 100, alpha),      # 绿色鬼火
                QColor(180, 0, 255, alpha),      # 紫色鬼火
                QColor(100, 255, 150, alpha),    # 浅绿色
                QColor(200, 100, 255, alpha),    # 浅紫色
            ]
            self.color = random.choice(ghost_colors)
        else:
            # 普通气泡使用蓝白色
            bubble_colors = [
                QColor(200, 230, 255, alpha),    # 蓝白色
                QColor(180, 220, 255, alpha),    # 浅蓝色
                QColor(220, 240, 255, alpha),    # 更白的蓝色
            ]
            self.color = random.choice(bubble_colors)
    
    def update(self) -> bool:
        """
        更新粒子位置
        
        WARNING: The spirit ascends through the darkness...
        
        Returns:
            bool: 如果粒子仍在屏幕内返回 True，否则返回 False
        """
        # 上升
        self.y -= self.speed
        
        # 左右摇摆（正弦波动）
        self.frame_count += 1
        wobble = self.wobble_amplitude * math.sin(
            (self.frame_count / self.WOBBLE_PERIOD) * 2 * math.pi + self.wobble_offset
        )
        self.x += wobble
        
        # 边界检查
        return self.y > -self.size
    
    def draw(self, painter: QPainter) -> None:
        """
        绘制粒子
        
        WARNING: Manifesting the ethereal form...
        
        Args:
            painter: QPainter 实例
        """
        if self.is_ghost_fire:
            self._draw_ghost_fire(painter)
        else:
            self._draw_bubble(painter)
    
    def _draw_bubble(self, painter: QPainter) -> None:
        """
        绘制普通气泡
        
        WARNING: A simple bubble rises from the deep...
        """
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # 绘制圆形气泡
        painter.drawEllipse(
            int(self.x - self.size / 2),
            int(self.y - self.size / 2),
            self.size,
            self.size
        )
        
        # 添加高光效果
        highlight_size = self.size // 3
        highlight_x = int(self.x - self.size / 4)
        highlight_y = int(self.y - self.size / 4)
        highlight_color = QColor(255, 255, 255, int(self.opacity * 150))
        painter.setBrush(QBrush(highlight_color))
        painter.drawEllipse(
            highlight_x,
            highlight_y,
            highlight_size,
            highlight_size
        )
    
    def _draw_ghost_fire(self, painter: QPainter) -> None:
        """
        绘制鬼火效果
        
        WARNING: The will-o'-wisp beckons from the darkness...
        """
        # 鬼火有发光效果
        glow_size = self.size * 2
        
        # 创建径向渐变
        gradient = QRadialGradient(self.x, self.y, glow_size)
        gradient.setColorAt(0, self.color)
        gradient.setColorAt(0.5, QColor(
            self.color.red(),
            self.color.green(),
            self.color.blue(),
            int(self.opacity * 128)
        ))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # 绘制发光圆
        painter.drawEllipse(
            int(self.x - glow_size),
            int(self.y - glow_size),
            int(glow_size * 2),
            int(glow_size * 2)
        )
        
        # 绘制核心亮点
        core_size = self.size // 2
        core_color = QColor(255, 255, 255, int(self.opacity * 200))
        painter.setBrush(QBrush(core_color))
        painter.drawEllipse(
            int(self.x - core_size / 2),
            int(self.y - core_size / 2),
            core_size,
            core_size
        )
    
    def get_position(self) -> tuple:
        """
        获取粒子位置
        
        Returns:
            (x, y) 坐标元组
        """
        return (self.x, self.y)
    
    def get_size(self) -> int:
        """
        获取粒子大小
        
        Returns:
            粒子大小
        """
        return self.size
    
    def get_speed(self) -> float:
        """
        获取粒子速度
        
        Returns:
            粒子速度
        """
        return self.speed
    
    def is_ghost_fire_mode(self) -> bool:
        """
        检查是否为鬼火模式
        
        Returns:
            是否为鬼火模式
        """
        return self.is_ghost_fire
    
    def set_ghost_fire_mode(self, is_ghost_fire: bool) -> None:
        """
        设置鬼火模式
        
        WARNING: The spirit transforms...
        
        Args:
            is_ghost_fire: 是否为鬼火模式
        """
        if self.is_ghost_fire != is_ghost_fire:
            self.is_ghost_fire = is_ghost_fire
            self._init_color()


class OceanBackground(QWidget):
    """
    🌊 深海背景窗口
    
    此窗口创造沉浸式的海底环境，覆盖桌面图标但位于宠物窗口之下。
    支持普通模式（蓝色滤镜）和万圣节模式（紫色滤镜）。
    支持昼夜循环：白天使用浅蓝色滤镜和气泡，黑夜使用深紫色滤镜和鬼火。
    
    ⚠️ 警告：深渊的入口已经打开...
    时间的轮回在此交汇，白昼与黑夜在深海中交替。
    """
    
    # 滤镜颜色配置
    # 白天模式：浅蓝色滤镜 (rgba(0, 50, 100, 0.3))
    NORMAL_FILTER_COLOR = QColor(0, 50, 100, 77)
    DAY_FILTER_COLOR = QColor(0, 50, 100, 77)         # 白天滤镜（与普通模式相同）
    
    # 黑夜模式：深紫色滤镜 (rgba(50, 0, 50, 0.4))
    HALLOWEEN_FILTER_COLOR = QColor(50, 0, 50, 102)
    NIGHT_FILTER_COLOR = QColor(50, 0, 50, 102)       # 黑夜滤镜（与万圣节模式相同）
    
    # 海底背景图像路径 (V9: 使用新的资产路径)
    SEABED_DAY_PATH = "assets/environment/seabed_day.png"      # 白天背景
    SEABED_NIGHT_PATH = "assets/environment/seabed_night.png"  # 黑夜背景
    
    def __init__(self, theme_manager: Optional['ThemeManager'] = None):
        """
        初始化海底背景窗口
        
        WARNING: Opening the gateway to the abyss...
        
        Args:
            theme_manager: 主题管理器实例（可选）
        """
        super().__init__()
        self.theme_manager = theme_manager
        self.seabed_pixmap: Optional[QPixmap] = None
        self.scaled_pixmap: Optional[QPixmap] = None
        self.filter_color: QColor = self.NORMAL_FILTER_COLOR
        self.is_active: bool = False
        
        # 粒子系统
        self.particles: List[BubbleParticle] = []
        self.particle_timer: Optional[QTimer] = None
        self.animation_timer: Optional[QTimer] = None
        self.max_particles: int = 50  # 最大粒子数
        self.spawn_interval: int = 200  # 粒子生成间隔（毫秒）
        self.animation_interval: int = 33  # 动画更新间隔（约30fps）
        
        # 设置窗口
        self.setup_window()
        
        # 加载海底背景
        self.load_seabed_image()
        
        # 应用主题滤镜
        self.apply_theme_filter()
        
        # 初始化粒子系统定时器
        self._init_particle_timers()
    
    def setup_window(self) -> None:
        """
        配置全屏无边框窗口
        
        WARNING: Manifesting the abyss portal...
        """
        # 设置窗口标志：无边框 + 工具窗口（不在任务栏显示）
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        
        # 设置窗口属性
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        
        # 获取主屏幕尺寸并设置全屏
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            self.setGeometry(geometry)
        else:
            # 回退到默认尺寸
            self.setGeometry(0, 0, 1920, 1080)
    
    def set_window_layer(self) -> None:
        """
        设置窗口层级（桌面之上，宠物之下）
        
        WARNING: Descending into the abyss between worlds...
        This places the window above desktop icons but below normal windows.
        
        On Windows, we use SetWindowPos to position the window just above the desktop.
        """
        try:
            # Windows API 常量
            HWND_BOTTOM = 1
            SWP_NOACTIVATE = 0x0010
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_SHOWWINDOW = 0x0040
            
            # 获取窗口句柄
            hwnd = int(self.winId())
            
            # 设置窗口位置到底层（但仍在桌面之上）
            # 这会将窗口放在 Z 顺序的底部，但仍然可见
            ctypes.windll.user32.SetWindowPos(
                hwnd,
                HWND_BOTTOM,
                0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW
            )
            
        except Exception as e:
            # If Windows API call fails, log warning but continue
            print(f"Warning: Failed to set window layer - {e}")
            print("Abyss layer setup failed, but the journey continues...")
    
    def load_seabed_image(self) -> None:
        """
        加载海底背景图像
        
        WARNING: Summoning the visage of the deep sea floor...
        The abyss reveals different faces for day and night...
        """
        # 确定当前模式（白天/黑夜）
        is_night_mode = self._is_halloween_mode()
        
        # 根据模式加载对应背景
        self.seabed_pixmap = self.load_background_for_mode("night" if is_night_mode else "day")
        
        # 缩放图像以适应屏幕
        self._scale_background_to_screen()
    
    def load_background_for_mode(self, mode: str) -> QPixmap:
        """
        根据昼夜模式加载对应的背景图像 (V9: 使用新资产路径)
        
        WARNING: The abyss changes its face with the turning of time...
        Load appropriate background based on day/night mode.
        
        V9 资产路径:
        - 白天: assets/environment/seabed_day.png
        - 夜晚: assets/environment/seabed_night.png
        
        Args:
            mode: 模式 ("day" 或 "night")
            
        Returns:
            加载的背景图像
        """
        if mode == "day":
            # 白天模式：加载白天背景
            path = self.SEABED_DAY_PATH
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    return pixmap
            
            # If loading fails, create fallback background
            print("Warning: Day seabed image not found, using fallback...")
            return self._create_fallback_background_pixmap(is_night=False)
        else:
            # 黑夜模式：加载黑夜背景
            path = self.SEABED_NIGHT_PATH
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    return pixmap
            
            # If night background doesn't exist, apply purple filter to day background
            print("Warning: Night seabed image not found, applying purple filter...")
            day_pixmap = self.load_background_for_mode("day")
            return self.apply_night_filter(day_pixmap)
    
    def apply_night_filter(self, pixmap: QPixmap) -> QPixmap:
        """
        对白天背景应用黑夜滤镜
        
        WARNING: The sun sets, and darkness claims the deep...
        Apply night filter to day background when night background is missing.
        
        Args:
            pixmap: 白天背景图像
            
        Returns:
            应用滤镜后的图像
        """
        if pixmap.isNull():
            return pixmap
        
        # 创建一个新的 pixmap 用于绘制
        result = QPixmap(pixmap.size())
        result.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(result)
        
        # 绘制原始图像
        painter.drawPixmap(0, 0, pixmap)
        
        # 应用深紫色/黑色滤镜叠加
        # 使用较深的紫色滤镜来模拟黑夜效果
        night_overlay = QColor(30, 0, 40, 100)  # 深紫色半透明叠加
        painter.fillRect(result.rect(), night_overlay)
        
        painter.end()
        
        return result
    
    def _create_fallback_background_pixmap(self, is_night: bool = False) -> QPixmap:
        """
        创建回退背景图像
        
        WARNING: The abyss provides its own darkness...
        
        Args:
            is_night: 是否为黑夜模式
            
        Returns:
            回退背景图像
        """
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            width, height = geometry.width(), geometry.height()
        else:
            width, height = 1920, 1080
        
        # 创建背景
        pixmap = QPixmap(width, height)
        
        if is_night:
            # 黑夜模式：深紫色背景
            pixmap.fill(QColor(15, 0, 25))
        else:
            # 白天模式：深蓝色背景
            pixmap.fill(QColor(0, 20, 40))
        
        return pixmap
    
    def _create_fallback_background(self) -> None:
        """
        创建回退背景（深蓝色渐变）
        
        WARNING: The abyss provides its own darkness...
        """
        is_night = self._is_halloween_mode()
        self.seabed_pixmap = self._create_fallback_background_pixmap(is_night=is_night)
    
    def _scale_background_to_screen(self) -> None:
        """
        缩放背景图像以适应屏幕
        
        WARNING: Stretching the fabric of the deep...
        """
        if self.seabed_pixmap is None or self.seabed_pixmap.isNull():
            return
        
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            target_width, target_height = geometry.width(), geometry.height()
        else:
            target_width, target_height = self.width(), self.height()
        
        # 缩放图像以填充屏幕
        self.scaled_pixmap = self.seabed_pixmap.scaled(
            target_width,
            target_height,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
    
    def apply_theme_filter(self) -> None:
        """
        应用主题滤镜（白天浅蓝色/黑夜深紫色）
        
        WARNING: The colors of the abyss shift with the turning of time...
        Day brings the calm blue of shallow waters,
        Night summons the deep purple of the haunted depths.
        """
        if self._is_halloween_mode():
            # 黑夜模式：深紫色滤镜
            self.filter_color = self.NIGHT_FILTER_COLOR
        else:
            # 白天模式：浅蓝色滤镜
            self.filter_color = self.DAY_FILTER_COLOR
        
        # 触发重绘
        self.update()
    
    def activate(self) -> None:
        """
        激活深潜模式
        
        WARNING: Descending into the depths...
        The journey to the abyss begins!
        """
        if self.is_active:
            return
        
        self.is_active = True
        
        # 重新加载背景（可能主题已改变）
        self.load_seabed_image()
        self.apply_theme_filter()
        
        # 启动粒子系统
        self.start_particle_system()
        
        # 显示窗口
        self.show()
        
        # 设置窗口层级
        self.set_window_layer()
        
        print("🌊 Deep dive mode activated - Welcome to the abyss...")
    
    def deactivate(self) -> None:
        """
        关闭深潜模式
        
        WARNING: Ascending from the depths...
        The surface world awaits!
        """
        if not self.is_active:
            return
        
        self.is_active = False
        
        # 停止粒子系统
        self.stop_particle_system()
        
        # 隐藏窗口
        self.hide()
        
        print("🌊 Deep dive mode deactivated - Returning to surface...")
    
    def paintEvent(self, event: QPaintEvent) -> None:
        """
        绘制背景和滤镜
        
        WARNING: Rendering the visage of the abyss...
        
        Args:
            event: 绘制事件
        """
        painter = QPainter(self)
        
        # 绘制背景图像
        if self.scaled_pixmap and not self.scaled_pixmap.isNull():
            # 居中绘制（如果图像比屏幕大）
            x = (self.width() - self.scaled_pixmap.width()) // 2
            y = (self.height() - self.scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, self.scaled_pixmap)
        else:
            # 如果没有背景图像，填充深蓝色
            painter.fillRect(self.rect(), QColor(0, 20, 40))
        
        # 绘制滤镜叠加层
        painter.fillRect(self.rect(), self.filter_color)
        
        # 绘制粒子
        self._draw_particles(painter)
        
        painter.end()
    
    def _draw_particles(self, painter: QPainter) -> None:
        """
        绘制所有粒子
        
        WARNING: The spirits manifest before your eyes...
        
        Args:
            painter: QPainter 实例
        """
        # 启用抗锯齿
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        for particle in self.particles:
            particle.draw(painter)
    
    def _init_particle_timers(self) -> None:
        """
        初始化粒子系统定时器
        
        WARNING: Preparing the spirit summoning rituals...
        """
        # 粒子生成定时器
        self.particle_timer = QTimer(self)
        self.particle_timer.timeout.connect(self.spawn_particle)
        
        # 动画更新定时器
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_particles)
    
    def spawn_particle(self) -> None:
        """
        生成新的气泡/鬼火粒子
        
        WARNING: A new spirit emerges from the depths...
        """
        if len(self.particles) >= self.max_particles:
            return
        
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            width, height = geometry.width(), geometry.height()
        else:
            width, height = self.width(), self.height()
        
        # 确定是否为鬼火模式
        is_ghost_fire = self._is_halloween_mode()
        
        # 创建新粒子
        particle = BubbleParticle(
            screen_width=width,
            screen_height=height,
            is_ghost_fire=is_ghost_fire
        )
        
        self.particles.append(particle)
    
    def update_particles(self) -> None:
        """
        更新所有粒子位置并移除离开屏幕的粒子
        
        WARNING: The spirits drift through the abyss...
        """
        # 更新粒子并移除离开屏幕的
        self.particles = [p for p in self.particles if p.update()]
        
        # 触发重绘
        self.update()
    
    def start_particle_system(self) -> None:
        """
        启动粒子系统
        
        WARNING: The spirit summoning begins...
        """
        if self.particle_timer and not self.particle_timer.isActive():
            self.particle_timer.start(self.spawn_interval)
        
        if self.animation_timer and not self.animation_timer.isActive():
            self.animation_timer.start(self.animation_interval)
    
    def stop_particle_system(self) -> None:
        """
        停止粒子系统
        
        WARNING: The spirits return to their slumber...
        """
        if self.particle_timer and self.particle_timer.isActive():
            self.particle_timer.stop()
        
        if self.animation_timer and self.animation_timer.isActive():
            self.animation_timer.stop()
        
        # 清空粒子
        self.particles.clear()
    
    def _is_halloween_mode(self) -> bool:
        """
        检查是否为万圣节模式
        
        Returns:
            是否为万圣节模式
        """
        if self.theme_manager:
            return self.theme_manager.is_halloween_mode()
        return False
    
    def get_particles(self) -> List[BubbleParticle]:
        """
        获取当前所有粒子
        
        Returns:
            粒子列表
        """
        return self.particles
    
    def get_particle_count(self) -> int:
        """
        获取当前粒子数量
        
        Returns:
            粒子数量
        """
        return len(self.particles)
    
    def set_max_particles(self, max_count: int) -> None:
        """
        设置最大粒子数
        
        Args:
            max_count: 最大粒子数
        """
        self.max_particles = max(1, max_count)
    
    def set_spawn_interval(self, interval_ms: int) -> None:
        """
        设置粒子生成间隔
        
        Args:
            interval_ms: 间隔（毫秒）
        """
        self.spawn_interval = max(50, interval_ms)
        if self.particle_timer and self.particle_timer.isActive():
            self.particle_timer.setInterval(self.spawn_interval)
    
    def get_filter_color(self) -> QColor:
        """
        获取当前滤镜颜色
        
        Returns:
            当前滤镜颜色
        """
        return self.filter_color
    
    def is_activated(self) -> bool:
        """
        检查深潜模式是否激活
        
        Returns:
            是否激活
        """
        return self.is_active
    
    def refresh_theme(self) -> None:
        """
        刷新主题（当主题切换时调用）
        
        WARNING: The spirits of the deep shift their colors...
        Day and night exchange their dominion over the abyss.
        
        此方法在昼夜模式切换时被调用，更新：
        1. 背景图像（白天/黑夜背景）
        2. 滤镜颜色（浅蓝色/深紫色）
        3. 粒子类型（气泡/鬼火）
        """
        # 重新加载背景图像（根据当前模式）
        self.load_seabed_image()
        
        # 更新滤镜颜色
        self.apply_theme_filter()
        
        # 更新现有粒子的模式（白天气泡/黑夜鬼火）
        is_ghost_fire = self._is_halloween_mode()
        for particle in self.particles:
            particle.set_ghost_fire_mode(is_ghost_fire)
        
        if self.is_active:
            self.update()
    
    def get_window_layer_info(self) -> dict:
        """
        获取窗口层级信息（用于测试）
        
        Returns:
            包含窗口层级信息的字典
        """
        return {
            'is_frameless': bool(self.windowFlags() & Qt.WindowType.FramelessWindowHint),
            'is_tool_window': bool(self.windowFlags() & Qt.WindowType.Tool),
            'is_active': self.is_active,
            'geometry': self.geometry(),
        }
    
    def get_current_mode(self) -> str:
        """
        获取当前昼夜模式
        
        Returns:
            "day" 或 "night"
        """
        return "night" if self._is_halloween_mode() else "day"
    
    def is_day_mode(self) -> bool:
        """
        检查是否为白天模式
        
        Returns:
            是否为白天模式
        """
        return not self._is_halloween_mode()
    
    def is_night_mode(self) -> bool:
        """
        检查是否为黑夜模式
        
        Returns:
            是否为黑夜模式
        """
        return self._is_halloween_mode()
