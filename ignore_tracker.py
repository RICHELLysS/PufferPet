"""忽视追踪器 - 实现"不给糖就捣蛋"机制

WARNING: This module tracks the silence of the deep...
When the creatures are ignored for too long, they shall rise in anger!
"""
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional, Callable
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox

if TYPE_CHECKING:
    from pet_manager import PetManager


class IgnoreTracker:
    """忽视追踪器 - 追踪用户交互并触发捣蛋模式
    
    WARNING: The creatures of the abyss grow restless when ignored...
    After 1 hour of silence, they shall demand attention!
    """
    
    # 默认忽视阈值：1小时（3600秒）
    DEFAULT_IGNORE_THRESHOLD = 3600
    
    # 检查间隔：30秒
    CHECK_INTERVAL_MS = 30000
    
    def __init__(self, pet_manager: 'PetManager', show_notifications: bool = True):
        """初始化忽视追踪器
        
        Args:
            pet_manager: 宠物管理器引用
            show_notifications: 是否显示通知（测试时可禁用）
        """
        self.pet_manager = pet_manager
        self.last_interaction_time: datetime = datetime.now()
        self.ignore_threshold: int = self.DEFAULT_IGNORE_THRESHOLD
        self.mischief_mode: bool = False
        self.check_timer: Optional[QTimer] = None
        self._angry_pets: set = set()  # 追踪愤怒的宠物
        self._show_notifications: bool = show_notifications
        
        # 回调函数（用于测试和扩展）
        self.on_mischief_triggered: Optional[Callable] = None
        self.on_pet_calmed: Optional[Callable[[str], None]] = None
        self.on_mischief_ended: Optional[Callable] = None
    
    def start(self) -> None:
        """启动忽视追踪
        
        WARNING: The watch begins... The creatures await your attention.
        """
        if self.check_timer is None:
            self.check_timer = QTimer()
            self.check_timer.timeout.connect(self.check_ignore_status)
        
        # 重置最后交互时间
        self.last_interaction_time = datetime.now()
        
        # 启动定时器
        self.check_timer.start(self.CHECK_INTERVAL_MS)
    
    def stop(self) -> None:
        """停止忽视追踪
        
        The watch ends... but the creatures remember.
        """
        if self.check_timer is not None:
            self.check_timer.stop()
    
    def on_user_interaction(self) -> None:
        """用户交互时调用，重置计时器
        
        The creatures sense your presence... for now.
        """
        self.last_interaction_time = datetime.now()
        
        # 如果处于捣蛋模式，不自动退出（需要安抚所有宠物）
    
    def check_ignore_status(self) -> None:
        """检查是否被忽视超过阈值
        
        WARNING: Checking if the creatures have been abandoned...
        """
        if self.mischief_mode:
            # 已经在捣蛋模式，不需要再次触发
            return
        
        elapsed = datetime.now() - self.last_interaction_time
        elapsed_seconds = elapsed.total_seconds()
        
        if elapsed_seconds >= self.ignore_threshold:
            self.trigger_mischief_mode()
    
    def is_ignored(self) -> bool:
        """检查当前是否处于被忽视状态（超过阈值）
        
        Returns:
            是否被忽视超过阈值
        """
        elapsed = datetime.now() - self.last_interaction_time
        return elapsed.total_seconds() >= self.ignore_threshold
    
    def get_time_since_interaction(self) -> float:
        """获取自上次交互以来的秒数
        
        Returns:
            秒数
        """
        elapsed = datetime.now() - self.last_interaction_time
        return elapsed.total_seconds()
    
    def trigger_mischief_mode(self) -> None:
        """触发捣蛋模式
        
        WARNING: The creatures rise in anger! "不给糖就捣蛋！"
        """
        if self.mischief_mode:
            return
        
        self.mischief_mode = True
        self._angry_pets.clear()
        
        # 显示通知（如果启用）
        if self._show_notifications:
            self._show_mischief_notification()
        
        # 让所有活跃宠物进入愤怒状态
        if self.pet_manager:
            for pet_id, pet_window in self.pet_manager.active_pet_windows.items():
                self._set_pet_angry(pet_id, pet_window)
                self._angry_pets.add(pet_id)
        
        # 触发回调
        if self.on_mischief_triggered:
            self.on_mischief_triggered()
    
    def _show_mischief_notification(self) -> None:
        """显示捣蛋模式通知"""
        try:
            QMessageBox.warning(
                None,
                "不给糖就捣蛋！",
                "你的宠物们被忽视太久了！\n快点击它们来安抚它们！",
                QMessageBox.StandardButton.Ok
            )
        except Exception as e:
            print(f"警告: 无法显示通知: {e}")
    
    def _set_pet_angry(self, pet_id: str, pet_window) -> None:
        """设置宠物为愤怒状态
        
        Args:
            pet_id: 宠物ID
            pet_window: 宠物窗口实例
        """
        if hasattr(pet_window, 'set_angry'):
            pet_window.set_angry(True)
    
    def calm_pet(self, pet_id: str) -> None:
        """安抚单个宠物
        
        Args:
            pet_id: 宠物ID
        """
        if pet_id in self._angry_pets:
            self._angry_pets.discard(pet_id)
            
            # 恢复宠物正常状态
            if self.pet_manager and pet_id in self.pet_manager.active_pet_windows:
                pet_window = self.pet_manager.active_pet_windows[pet_id]
                if hasattr(pet_window, 'set_angry'):
                    pet_window.set_angry(False)
            
            # 触发回调
            if self.on_pet_calmed:
                self.on_pet_calmed(pet_id)
            
            # 检查是否所有宠物都被安抚
            if len(self._angry_pets) == 0:
                self.exit_mischief_mode()
    
    def exit_mischief_mode(self) -> None:
        """退出捣蛋模式
        
        The creatures are appeased... for now.
        """
        if not self.mischief_mode:
            return
        
        self.mischief_mode = False
        self._angry_pets.clear()
        
        # 重置最后交互时间
        self.last_interaction_time = datetime.now()
        
        # 确保所有宠物恢复正常状态
        if self.pet_manager:
            for pet_id, pet_window in self.pet_manager.active_pet_windows.items():
                if hasattr(pet_window, 'set_angry'):
                    pet_window.set_angry(False)
        
        # 触发回调
        if self.on_mischief_ended:
            self.on_mischief_ended()
    
    def get_angry_pets(self) -> set:
        """获取当前愤怒的宠物集合
        
        Returns:
            愤怒宠物ID的集合
        """
        return self._angry_pets.copy()
    
    def is_pet_angry(self, pet_id: str) -> bool:
        """检查指定宠物是否处于愤怒状态
        
        Args:
            pet_id: 宠物ID
            
        Returns:
            是否愤怒
        """
        return pet_id in self._angry_pets
