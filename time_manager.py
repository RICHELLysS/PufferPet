"""
🌙 Deep Sea Time Guardian - Day/Night Cycle Management Module

WARNING: This module governs the flow of time in the abyss...

This module manages:
- Day/night detection: Determine day (06:00-18:00) or night based on system time
- Auto sync: Check time every minute and auto-switch modes
- Mode mapping: Day → normal, Night → halloween

⚠️ WARNING: Time is the most ancient power in the abyss...
Even the mightiest sea monsters cannot escape its grasp.

Author: Deep Sea Code Captain
Version: 5.5 (Day/Night Cycle Edition)
"""
from datetime import datetime
from typing import Optional, Callable

from PyQt6.QtCore import QTimer, QObject, pyqtSignal


class TimeManager(QObject):
    """
    🌊 深渊时间守护者 - 管理昼夜循环和模式切换
    
    此类掌管着深海世界中时间的流转。
    当太阳升起，海洋变得明亮；当夜幕降临，幽灵开始游荡。
    
    ⚠️ 警告：时间的力量不可小觑...
    每一次模式切换都是深渊与凡间的交汇。
    """
    
    # 信号：当模式切换时发出
    mode_changed = pyqtSignal(str)  # 参数: 新模式 ("day" 或 "night")
    
    # 默认时间配置
    DEFAULT_DAY_START_HOUR = 6    # 白天开始时间（06:00）
    DEFAULT_NIGHT_START_HOUR = 18  # 黑夜开始时间（18:00）
    CHECK_INTERVAL_MS = 60000      # 检查间隔（1分钟 = 60000毫秒）
    
    def __init__(self, theme_manager=None, data_manager=None):
        """
        🌅 唤醒时间守护者
        
        初始化时间管理器并建立与深渊的时间连接。
        
        Args:
            theme_manager: 主题管理器实例（用于切换视觉效果）
            data_manager: 数据管理器实例（用于持久化设置）
        """
        super().__init__()
        
        self.theme_manager = theme_manager
        self.data_manager = data_manager
        
        # 时间配置
        self._day_start_hour = self.DEFAULT_DAY_START_HOUR
        self._night_start_hour = self.DEFAULT_NIGHT_START_HOUR
        
        # 状态
        self._current_period = "day"  # "day" 或 "night"
        self._auto_sync_enabled = True
        self._is_running = False
        
        # 定时器
        self._check_timer = QTimer(self)
        self._check_timer.timeout.connect(self.check_time_and_update)
        
        # 从数据管理器加载设置
        self._load_settings()
        
        # 初始化当前时段
        self._current_period = self._determine_period()
    
    def _load_settings(self) -> None:
        """
        📜 从深渊记忆中加载时间设置
        
        从数据管理器加载昼夜循环的配置。
        """
        if self.data_manager is None:
            return
        
        day_night_settings = self.data_manager.data.get('day_night_settings', {})
        self._auto_sync_enabled = day_night_settings.get('auto_time_sync', True)
        self._current_period = day_night_settings.get('current_mode', 'day')
        self._day_start_hour = day_night_settings.get('day_start_hour', self.DEFAULT_DAY_START_HOUR)
        self._night_start_hour = day_night_settings.get('night_start_hour', self.DEFAULT_NIGHT_START_HOUR)
    
    def _save_settings(self) -> None:
        """
        ⚓ 将时间设置封印回深渊
        
        保存昼夜循环配置到数据管理器。
        """
        if self.data_manager is None:
            return
        
        if 'day_night_settings' not in self.data_manager.data:
            self.data_manager.data['day_night_settings'] = {}
        
        self.data_manager.data['day_night_settings']['auto_time_sync'] = self._auto_sync_enabled
        self.data_manager.data['day_night_settings']['current_mode'] = self._current_period
        self.data_manager.data['day_night_settings']['day_start_hour'] = self._day_start_hour
        self.data_manager.data['day_night_settings']['night_start_hour'] = self._night_start_hour
        self.data_manager.data['day_night_settings']['last_mode_change'] = datetime.now().isoformat()
        
        self.data_manager.save_data()
    
    def _determine_period(self, hour: Optional[int] = None) -> str:
        """
        🔮 判定当前时段
        
        根据小时数判断是白天还是黑夜。
        
        Args:
            hour: 小时数（0-23），如果为None则使用当前系统时间
            
        Returns:
            "day" 或 "night"
        """
        if hour is None:
            hour = datetime.now().hour
        
        # 白天：day_start_hour <= hour < night_start_hour
        if self._day_start_hour <= hour < self._night_start_hour:
            return "day"
        else:
            return "night"
    
    def get_current_period(self) -> str:
        """
        🌓 获取当前时段
        
        Returns:
            当前时段 ("day" 或 "night")
        """
        return self._current_period
    
    def is_daytime(self) -> bool:
        """
        ☀️ 判断当前是否为白天
        
        根据系统时间判断是否在白天时段（06:00-18:00）。
        
        Returns:
            是否为白天
        """
        current_hour = datetime.now().hour
        return self._day_start_hour <= current_hour < self._night_start_hour
    
    def check_time_and_update(self) -> None:
        """
        ⏰ 检查时间并更新模式
        
        此仪式每分钟执行一次，检查系统时间并在需要时切换模式。
        只有在自动同步启用时才会自动切换。
        """
        if not self._auto_sync_enabled:
            return
        
        # 判定当前应该是什么时段
        new_period = self._determine_period()
        
        # 如果时段发生变化，执行切换
        if new_period != self._current_period:
            if new_period == "day":
                self.switch_to_day()
            else:
                self.switch_to_night()
    
    def start(self) -> None:
        """
        🌅 启动时间监视
        
        开始每分钟检查系统时间。
        """
        if self._is_running:
            return
        
        self._is_running = True
        
        # 立即执行一次检查
        if self._auto_sync_enabled:
            self.check_time_and_update()
        
        # 启动定时器
        self._check_timer.start(self.CHECK_INTERVAL_MS)
    
    def stop(self) -> None:
        """
        🌙 停止时间监视
        
        停止定时检查。
        """
        self._is_running = False
        self._check_timer.stop()
    
    def switch_to_day(self) -> None:
        """
        ☀️ 切换到白天模式
        
        将主题切换为 "normal"，更新所有视觉效果。
        """
        self._current_period = "day"
        
        # 更新主题管理器
        if self.theme_manager is not None:
            self.theme_manager.set_theme_mode("normal")
        
        # 保存设置
        self._save_settings()
        
        # 发出模式切换信号
        self.mode_changed.emit("day")
    
    def switch_to_night(self) -> None:
        """
        🌙 切换到黑夜模式
        
        将主题切换为 "halloween"，启用幽灵滤镜和暗黑主题。
        """
        self._current_period = "night"
        
        # 更新主题管理器
        if self.theme_manager is not None:
            self.theme_manager.set_theme_mode("halloween")
        
        # 保存设置
        self._save_settings()
        
        # 发出模式切换信号
        self.mode_changed.emit("night")
    
    def set_auto_sync(self, enabled: bool) -> None:
        """
        🔄 设置自动同步开关
        
        当启用时，应用将跟随系统时间自动切换昼夜模式。
        当禁用时，允许用户手动切换。
        
        Args:
            enabled: 是否启用自动同步
        """
        self._auto_sync_enabled = enabled
        self._save_settings()
        
        # 如果启用自动同步，立即同步到当前时间
        if enabled and self._is_running:
            self.check_time_and_update()
    
    def get_auto_sync(self) -> bool:
        """
        获取自动同步状态
        
        Returns:
            是否启用自动同步
        """
        return self._auto_sync_enabled
    
    @property
    def auto_sync_enabled(self) -> bool:
        """自动同步是否启用"""
        return self._auto_sync_enabled
    
    def manual_toggle(self) -> None:
        """
        🔀 手动切换昼夜模式
        
        在白天和黑夜模式之间切换。
        只有在自动同步禁用时才有效。
        
        ⚠️ 警告：凡人竟敢控制昼夜的轮回...
        """
        if self._auto_sync_enabled:
            # 自动同步启用时，忽略手动切换
            return
        
        if self._current_period == "day":
            self.switch_to_night()
        else:
            self.switch_to_day()
    
    def get_theme_mode_for_period(self, period: str) -> str:
        """
        获取时段对应的主题模式
        
        Args:
            period: 时段 ("day" 或 "night")
            
        Returns:
            主题模式 ("normal" 或 "halloween")
        """
        if period == "day":
            return "normal"
        else:
            return "halloween"
    
    @property
    def day_start_hour(self) -> int:
        """白天开始时间（小时）"""
        return self._day_start_hour
    
    @property
    def night_start_hour(self) -> int:
        """黑夜开始时间（小时）"""
        return self._night_start_hour
    
    def is_running(self) -> bool:
        """检查时间管理器是否正在运行"""
        return self._is_running
