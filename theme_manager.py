"""
Theme Manager Module - Halloween theme and ghost filter effects

WARNING: Disturbing the ancient spirits of the deep...
This module controls the cursed visual transformations of our sea creatures.
Handle with extreme caution - the abyss gazes back.

V5.5 Update: Day/night cycle mode mapping
- Day mode (day) → theme_mode = "normal"
- Night mode (night) → theme_mode = "halloween"
"""
import os
import random
from typing import Optional

from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QImage
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect


class ThemeManager(QObject):
    """
    管理万圣节主题和幽灵滤镜效果的诅咒管理器
    
    WARNING: The spirits of the deep sea are restless...
    This manager controls the visual manifestations of the cursed realm.
    
    V5.5 更新: 支持昼夜循环模式映射
    - set_day_mode(): 切换到白天模式 (theme_mode = "normal")
    - set_night_mode(): 切换到黑夜模式 (theme_mode = "halloween")
    - mode_changed 信号: 当模式切换时发出通知
    """
    
    # 信号：当主题模式切换时发出
    mode_changed = pyqtSignal(str)  # 参数: 新主题模式 ("normal" 或 "halloween")
    
    # 昼夜模式映射
    DAY_NIGHT_MODE_MAP = {
        "day": "normal",
        "night": "halloween"
    }
    
    # 幽灵光晕颜色 - 来自深海的诅咒之光 (Kiroween风格)
    GHOST_COLORS = [
        QColor(0, 255, 136, 255),    # 幽灵绿 #00FF88
        QColor(139, 0, 255, 255),    # 诅咒紫 #8B00FF
    ]
    
    # Kiroween恐怖颜色常量
    SPOOKY_COLORS = {
        'ghost_green': '#00FF88',
        'blood_red': '#FF0066',
        'pumpkin_orange': '#FF6600',
        'curse_purple': '#8B00FF',
    }
    
    # 幽灵滤镜配置
    GHOST_FILTER_CONFIG = {
        'opacity_min': 0.60,        # 最小透明度 60%
        'opacity_max': 0.70,        # 最大透明度 70%
        'color_blend': 0.3,         # 颜色混合强度
    }
    
    # 暗黑主题样式表 - 深海亡灵帝国的视觉诅咒
    DARK_HALLOWEEN_STYLESHEET = """
QMenu {
    background-color: #1a1a1a;
    color: #00ff00;
    border: 2px solid #ff6600;
    border-radius: 5px;
    padding: 5px;
}

QMenu::item:selected {
    background-color: #2a2a2a;
    color: #ffaa00;
}

QDialog {
    background-color: #0d0d0d;
    color: #00ff00;
    border: 3px solid #ff6600;
}

QPushButton {
    background-color: #2a2a2a;
    color: #00ff00;
    border: 2px solid #ff6600;
    border-radius: 3px;
    padding: 5px 10px;
}

QPushButton:hover {
    background-color: #3a3a3a;
    color: #ffaa00;
}

QPushButton:disabled {
    background-color: #1a1a1a;
    color: #666666;
    border: 2px solid #444444;
}

QLabel {
    color: #00ff00;
}

QCheckBox {
    color: #00ff00;
}

QCheckBox::indicator {
    border: 2px solid #ff6600;
    background-color: #1a1a1a;
}

QCheckBox::indicator:checked {
    background-color: #00ff00;
}

QListWidget {
    background-color: #1a1a1a;
    color: #00ff00;
    border: 2px solid #ff6600;
}

QListWidget::item:selected {
    background-color: #2a2a2a;
    color: #ffaa00;
}

QScrollBar:vertical {
    background-color: #1a1a1a;
    width: 12px;
    border: 1px solid #ff6600;
}

QScrollBar::handle:vertical {
    background-color: #ff6600;
    min-height: 20px;
}

QMessageBox {
    background-color: #0d0d0d;
    color: #00ff00;
}

QMessageBox QLabel {
    color: #00ff00;
}

QMessageBox QPushButton {
    background-color: #2a2a2a;
    color: #00ff00;
    border: 2px solid #ff6600;
    padding: 5px 15px;
}
"""
    
    def __init__(self, data_manager=None):
        """
        初始化主题管理器
        
        WARNING: Awakening the cursed theme controller...
        
        Args:
            data_manager: 数据管理器实例（可选，用于持久化主题设置）
        """
        super().__init__()
        
        self.data_manager = data_manager
        self._current_theme = "normal"
        self._ghost_opacity = 0.6
        self._ghost_glow_enabled = True
        self._day_night_mode = "day"  # 当前昼夜模式 ("day" 或 "night")
        
        # 从数据管理器加载主题设置
        if data_manager and hasattr(data_manager, 'data'):
            self._load_theme_settings()
    
    def _load_theme_settings(self) -> None:
        """从数据管理器加载主题设置"""
        if self.data_manager is None:
            return
        
        halloween_settings = self.data_manager.data.get('halloween_settings', {})
        self._current_theme = self.data_manager.data.get('theme_mode', 'normal')
        self._ghost_opacity = halloween_settings.get('ghost_opacity', 0.6)
        self._ghost_glow_enabled = halloween_settings.get('ghost_filter_enabled', True)
        
        # 加载昼夜模式设置
        day_night_settings = self.data_manager.data.get('day_night_settings', {})
        self._day_night_mode = day_night_settings.get('current_mode', 'day')
        
        # 确保主题模式与昼夜模式一致
        expected_theme = self.DAY_NIGHT_MODE_MAP.get(self._day_night_mode, 'normal')
        if self._current_theme != expected_theme:
            # 如果不一致，以昼夜模式为准
            self._current_theme = expected_theme
    
    def _save_theme_settings(self) -> None:
        """保存主题设置到数据管理器"""
        if self.data_manager is None:
            return
        
        self.data_manager.data['theme_mode'] = self._current_theme
        
        if 'halloween_settings' not in self.data_manager.data:
            self.data_manager.data['halloween_settings'] = {}
        
        self.data_manager.data['halloween_settings']['ghost_opacity'] = self._ghost_opacity
        self.data_manager.data['halloween_settings']['ghost_filter_enabled'] = self._ghost_glow_enabled
        self.data_manager.data['halloween_settings']['dark_theme_enabled'] = (self._current_theme == 'halloween')
        
        # 保存昼夜模式设置
        if 'day_night_settings' not in self.data_manager.data:
            self.data_manager.data['day_night_settings'] = {}
        
        self.data_manager.data['day_night_settings']['current_mode'] = self._day_night_mode
        
        self.data_manager.save_data()
    
    def get_theme_mode(self) -> str:
        """
        获取当前主题模式
        
        Returns:
            当前主题模式 ("normal" 或 "halloween")
        """
        return self._current_theme
    
    def set_theme_mode(self, mode: str) -> None:
        """
        设置主题模式
        
        WARNING: Shifting between realms of the living and the cursed...
        
        Args:
            mode: 主题模式 ("normal" 或 "halloween")
        """
        if mode not in ['normal', 'halloween']:
            print(f"警告: 未知的主题模式 '{mode}'，使用默认值 'normal'")
            mode = 'normal'
        
        old_mode = self._current_theme
        self._current_theme = mode
        
        # 更新昼夜模式映射
        if mode == "normal":
            self._day_night_mode = "day"
        else:
            self._day_night_mode = "night"
        
        self._save_theme_settings()
        
        # 如果模式发生变化，发出信号通知其他组件
        if old_mode != mode:
            self.mode_changed.emit(mode)
    
    def set_day_mode(self) -> None:
        """
        ☀️ 切换到白天模式
        
        将主题设置为 "normal"，关闭幽灵滤镜和暗黑主题。
        白天模式复用普通视觉效果。
        
        WARNING: The sun rises over the deep sea...
        The cursed spirits retreat to the shadows.
        """
        self._day_night_mode = "day"
        self.set_theme_mode("normal")
    
    def set_night_mode(self) -> None:
        """
        🌙 切换到黑夜模式
        
        将主题设置为 "halloween"，启用幽灵滤镜和暗黑主题。
        黑夜模式复用所有万圣节视觉效果。
        
        WARNING: Night falls upon the abyss...
        The spirits of the deep awaken from their slumber.
        """
        self._day_night_mode = "night"
        self.set_theme_mode("halloween")
    
    def get_day_night_mode(self) -> str:
        """
        获取当前昼夜模式
        
        Returns:
            当前昼夜模式 ("day" 或 "night")
        """
        return self._day_night_mode
    
    def is_day_mode(self) -> bool:
        """
        检查是否处于白天模式
        
        Returns:
            是否处于白天模式
        """
        return self._day_night_mode == "day"
    
    def is_night_mode(self) -> bool:
        """
        检查是否处于黑夜模式
        
        Returns:
            是否处于黑夜模式
        """
        return self._day_night_mode == "night"
    
    def get_theme_for_day_night(self, day_night_mode: str) -> str:
        """
        获取昼夜模式对应的主题模式
        
        Args:
            day_night_mode: 昼夜模式 ("day" 或 "night")
            
        Returns:
            对应的主题模式 ("normal" 或 "halloween")
        """
        return self.DAY_NIGHT_MODE_MAP.get(day_night_mode, "normal")
    
    def load_themed_image(self, pet_id: str, image_type: str = "idle", 
                          level: int = 1, tier: int = 1) -> QPixmap:
        """
        加载主题图像，支持万圣节图像优先加载和回退逻辑
        
        WARNING: Summoning the visual manifestation of a creature...
        The image loading follows the cursed priority:
        1. Halloween image (if theme is halloween)
        2. Normal image
        3. Ghost filter applied to normal image (if halloween and no halloween image)
        
        Args:
            pet_id: 宠物ID
            image_type: 图像类型 ("idle", "baby_idle", "adult_idle", "angry_idle")
            level: 宠物等级 (1-3)
            tier: 宠物层级 (1, 2, 或 3)
            
        Returns:
            加载的QPixmap，如果加载失败则返回占位符
        """
        # V7.1: Simplified path - all V7 pets use assets/{pet_id}/ (Requirements: 10.2)
        base_dir = f"assets/{pet_id}"
        
        # 确定图像文件名
        if image_type == "idle":
            if level == 1:
                image_name = "baby_idle.png"
            else:
                image_name = "adult_idle.png"
        else:
            image_name = f"{image_type}.png"
        
        pixmap = None
        used_fallback = False
        
        # 如果是万圣节模式，首先尝试加载万圣节图像
        if self._current_theme == "halloween":
            halloween_path = os.path.join(base_dir, "halloween_idle.png")
            if os.path.exists(halloween_path):
                pixmap = QPixmap(halloween_path)
                if not pixmap.isNull():
                    return pixmap
            
            # 万圣节图像不存在，标记需要使用回退
            used_fallback = True
        
        # 加载普通图像
        normal_path = os.path.join(base_dir, image_name)
        if os.path.exists(normal_path):
            pixmap = QPixmap(normal_path)
            if pixmap.isNull():
                pixmap = None
        
        # 如果普通图像也不存在，创建占位符
        if pixmap is None:
            pixmap = self._create_placeholder(pet_id, tier)
            used_fallback = True
        
        # 如果是万圣节模式且使用了回退，应用幽灵滤镜
        if self._current_theme == "halloween" and used_fallback:
            pixmap = self.apply_ghost_filter(pixmap)
        
        return pixmap
    
    def apply_ghost_filter(self, pixmap: QPixmap, tint_color: QColor = None) -> QPixmap:
        """
        应用幽灵滤镜效果 (Kiroween模式)
        
        WARNING: Summoning the spirits of the deep...
        Apply ghostly effects to make creatures look haunted.
        
        效果:
        - 降低透明度到60-70%
        - 添加绿色(#00FF88)或紫色(#8B00FF)色调
        - 颜色混合强度: 0.3
        
        Args:
            pixmap: 原始图像
            tint_color: 可选的色调颜色，如果不指定则随机选择
            
        Returns:
            应用幽灵滤镜后的图像
        """
        if pixmap.isNull():
            return pixmap
        
        # 转换为QImage以便处理
        image = pixmap.toImage()
        if image.isNull():
            return pixmap
        
        # 确保图像格式支持透明度
        image = image.convertToFormat(QImage.Format.Format_ARGB32)
        
        # 选择幽灵光晕颜色 (绿色 #00FF88 或 紫色 #8B00FF)
        if tint_color is None:
            glow_color = random.choice(self.GHOST_COLORS)
        else:
            glow_color = tint_color
        
        # 获取滤镜配置
        opacity_min = self.GHOST_FILTER_CONFIG['opacity_min']
        opacity_max = self.GHOST_FILTER_CONFIG['opacity_max']
        blend_factor = self.GHOST_FILTER_CONFIG['color_blend']
        
        # 计算实际透明度 (在60-70%范围内，使用_ghost_opacity作为基准)
        # 确保透明度在60-70%范围内
        target_opacity = max(opacity_min, min(opacity_max, self._ghost_opacity))
        
        # 应用幽灵效果：透明度 + 颜色叠加
        width = image.width()
        height = image.height()
        
        for y in range(height):
            for x in range(width):
                pixel = image.pixelColor(x, y)
                
                # 只处理非完全透明的像素
                if pixel.alpha() > 0:
                    # 应用透明度 (降低到60-70%)
                    new_alpha = int(pixel.alpha() * target_opacity)
                    
                    # 混合幽灵颜色 (blend_factor = 0.3)
                    new_red = int(pixel.red() * (1 - blend_factor) + glow_color.red() * blend_factor)
                    new_green = int(pixel.green() * (1 - blend_factor) + glow_color.green() * blend_factor)
                    new_blue = int(pixel.blue() * (1 - blend_factor) + glow_color.blue() * blend_factor)
                    
                    # 确保值在有效范围内
                    new_red = max(0, min(255, new_red))
                    new_green = max(0, min(255, new_green))
                    new_blue = max(0, min(255, new_blue))
                    
                    image.setPixelColor(x, y, QColor(new_red, new_green, new_blue, new_alpha))
        
        return QPixmap.fromImage(image)
    
    def get_dark_stylesheet(self) -> str:
        """
        获取暗黑主题样式表
        
        WARNING: Retrieving the visual curse of the deep sea realm...
        
        Returns:
            暗黑主题CSS样式表字符串
        """
        return self.DARK_HALLOWEEN_STYLESHEET
    
    def apply_theme_to_widget(self, widget: QWidget) -> None:
        """
        应用主题到窗口
        
        WARNING: Casting the visual curse upon a widget...
        
        Args:
            widget: 要应用主题的窗口
        """
        if self._current_theme == "halloween":
            widget.setStyleSheet(self.DARK_HALLOWEEN_STYLESHEET)
        else:
            widget.setStyleSheet("")  # 清除样式，使用默认
    
    def _create_placeholder(self, pet_id: str, tier: int = 1) -> QPixmap:
        """
        创建占位符图像
        
        WARNING: Manifesting a placeholder from the void...
        
        Args:
            pet_id: 宠物ID（用于确定颜色）
            tier: 宠物层级
            
        Returns:
            占位符QPixmap
        """
        # V7.1: Only V7 pets are supported (Requirements: 10.2)
        color_map = {
            'puffer': QColor(255, 165, 0),      # 橙色
            'jelly': QColor(138, 43, 226),      # 紫色
            'starfish': QColor(255, 192, 203),  # 粉色
            'crab': QColor(255, 0, 0),          # 红色
            'ray': QColor(70, 130, 180),        # 钢蓝
        }
        
        color = color_map.get(pet_id, QColor(255, 0, 0))  # 默认红色
        
        # 创建占位符
        size = 50
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, size, size)
        painter.end()
        
        return pixmap
    
    def is_halloween_mode(self) -> bool:
        """
        检查是否处于万圣节模式
        
        Returns:
            是否处于万圣节模式
        """
        return self._current_theme == "halloween"
    
    def get_spooky_color(self, color_name: str = None) -> str:
        """
        获取恐怖颜色 (用于Kiroween模式)
        
        如果不指定颜色名称，随机返回 ghost_green 或 blood_red
        
        Args:
            color_name: 可选的颜色名称 ('ghost_green', 'blood_red', 'pumpkin_orange', 'curse_purple')
            
        Returns:
            颜色的十六进制字符串 (如 '#00FF88')
        """
        if color_name is not None and color_name in self.SPOOKY_COLORS:
            return self.SPOOKY_COLORS[color_name]
        
        # 随机返回 ghost_green 或 blood_red
        return random.choice([
            self.SPOOKY_COLORS['ghost_green'],
            self.SPOOKY_COLORS['blood_red']
        ])
    
    def get_spooky_qcolor(self, color_name: str = None) -> QColor:
        """
        获取恐怖颜色作为QColor对象
        
        Args:
            color_name: 可选的颜色名称
            
        Returns:
            QColor对象
        """
        hex_color = self.get_spooky_color(color_name)
        return QColor(hex_color)
    
    def get_ghost_opacity(self) -> float:
        """
        获取幽灵滤镜透明度
        
        Returns:
            透明度值 (0.0-1.0)
        """
        return self._ghost_opacity
    
    def set_ghost_opacity(self, opacity: float) -> None:
        """
        设置幽灵滤镜透明度
        
        Args:
            opacity: 透明度值 (0.0-1.0)
        """
        self._ghost_opacity = max(0.0, min(1.0, opacity))
        self._save_theme_settings()


# =============================================================================
# V9 NightFilter - 夜间模式颜色滤镜
# =============================================================================

class NightFilter:
    """
    V9 夜间滤镜 - 分类颜色叠加
    
    根据宠物种类应用不同颜色的夜间滤镜效果。
    
    Features:
    - 绿色组 (puffer, starfish): 绿色 #00FF88 叠加
    - 紫色组 (crab, jelly, ray): 紫色 #8B00FF 叠加
    - 透明度: 0.2 (20%)
    
    Requirements: 6.1, 6.2, 6.3
    """
    
    # 颜色分组 (Requirements 6.2, 6.3)
    GREEN_GROUP = ['puffer', 'starfish']  # 绿色组
    PURPLE_GROUP = ['crab', 'jelly', 'ray']  # 紫色组
    
    # 滤镜颜色 (Requirements 6.2, 6.3)
    # 绿色 #00FF88, 透明度 0.2 (alpha = 51 = 255 * 0.2)
    GREEN_OVERLAY = QColor(0, 255, 136, 51)
    # 紫色 #8B00FF, 透明度 0.2 (alpha = 51 = 255 * 0.2)
    PURPLE_OVERLAY = QColor(139, 0, 255, 51)
    
    # 滤镜透明度
    OVERLAY_OPACITY = 0.2
    
    @staticmethod
    def get_overlay_color(pet_id: str) -> QColor:
        """
        根据宠物ID获取叠加颜色
        
        颜色分组规则:
        - puffer, starfish → 绿色 #00FF88
        - crab, jelly, ray → 紫色 #8B00FF
        
        Args:
            pet_id: 宠物ID (e.g., 'puffer', 'crab')
            
        Returns:
            对应的叠加颜色 QColor (带 0.2 透明度)
            
        Requirements: 6.2, 6.3
        """
        if pet_id in NightFilter.GREEN_GROUP:
            return NightFilter.GREEN_OVERLAY
        elif pet_id in NightFilter.PURPLE_GROUP:
            return NightFilter.PURPLE_OVERLAY
        else:
            # 默认使用绿色
            return NightFilter.GREEN_OVERLAY
    
    @staticmethod
    def apply_filter(pixmap: QPixmap, pet_id: str) -> QPixmap:
        """
        应用夜间滤镜
        
        使用 QPainter CompositionMode 叠加颜色到图像上。
        
        Args:
            pixmap: 原始图像
            pet_id: 宠物ID (用于确定叠加颜色)
            
        Returns:
            应用夜间滤镜后的图像
            
        Requirements: 6.1
        """
        if pixmap.isNull():
            return pixmap
        
        # 获取叠加颜色
        overlay_color = NightFilter.get_overlay_color(pet_id)
        
        # 创建结果图像
        result = QPixmap(pixmap.size())
        result.fill(Qt.GlobalColor.transparent)
        
        # 使用 QPainter 叠加颜色
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 先绘制原始图像
        painter.drawPixmap(0, 0, pixmap)
        
        # 使用 CompositionMode_SourceAtop 叠加颜色
        # 这会在原图像的非透明区域上叠加颜色
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceAtop)
        painter.fillRect(result.rect(), overlay_color)
        
        painter.end()
        
        return result
