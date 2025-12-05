"""
🌊 深海亡灵帝国 - 空闲监视器模块

此模块掌管着屏保模式的空闲检测：
- 监听鼠标和键盘活动
- 检测用户是否空闲超过5分钟
- 自动激活深潜模式（屏保）
- 检测到用户活动时立即唤醒

⚠️ 警告：深渊正在监视你的沉默...
当你停止活动时，深海将召唤你！

作者：深海代码船长
版本：5.0 (Deep Dive Edition)
"""
import threading
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional, Callable, Dict

from PyQt6.QtCore import QTimer, QPoint, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QApplication

if TYPE_CHECKING:
    from ocean_background import OceanBackground
    from pet_manager import PetManager


class IdleWatcher:
    """
    🌊 空闲监视器 - 检测用户活动并触发屏保模式
    
    WARNING: The abyss watches your silence...
    After 5 minutes of inactivity, the deep sea shall summon you!
    
    此类使用 pynput 监听鼠标和键盘活动，当用户空闲超过阈值时
    自动激活深潜模式（屏保），并在检测到用户活动时立即唤醒。
    """
    
    # 默认空闲阈值：5分钟（300秒）
    DEFAULT_IDLE_THRESHOLD = 300
    
    # 检查间隔：10秒
    CHECK_INTERVAL_MS = 10000
    
    # 唤醒响应时间阈值：500毫秒
    WAKE_RESPONSE_THRESHOLD_MS = 500
    
    def __init__(
        self,
        ocean_background: Optional['OceanBackground'] = None,
        pet_manager: Optional['PetManager'] = None,
        enable_input_hooks: bool = True
    ):
        """
        初始化空闲监视器
        
        WARNING: The watcher awakens from its slumber...
        
        Args:
            ocean_background: 海底背景管理器引用
            pet_manager: 宠物管理器引用
            enable_input_hooks: 是否启用输入钩子（测试时可禁用）
        """
        self.ocean_background = ocean_background
        self.pet_manager = pet_manager
        self.enable_input_hooks = enable_input_hooks
        
        # 空闲检测状态
        self.idle_threshold: int = self.DEFAULT_IDLE_THRESHOLD
        self.last_activity_time: datetime = datetime.now()
        self.check_timer: Optional[QTimer] = None
        self.is_screensaver_active: bool = False
        
        # V5: 深潜模式激活类型（manual 或 auto）
        self._activation_mode: Optional[str] = None  # "manual" or "auto"
        
        # 宠物原始位置（用于恢复）
        self.original_pet_positions: Dict[str, QPoint] = {}
        
        # pynput 监听器
        self._mouse_listener = None
        self._keyboard_listener = None
        self._listeners_started = False
        
        # 回调函数（用于测试和扩展）
        self.on_screensaver_activated: Optional[Callable] = None
        self.on_screensaver_deactivated: Optional[Callable] = None
        self.on_activity_detected: Optional[Callable] = None
        
        # 唤醒时间戳（用于测试响应时间）
        self._wake_request_time: Optional[datetime] = None
        self._wake_complete_time: Optional[datetime] = None
    
    def start(self) -> None:
        """
        启动空闲监视
        
        WARNING: The watch begins... The abyss awaits your silence.
        """
        # 重置最后活动时间
        self.last_activity_time = datetime.now()
        
        # 创建并启动检查定时器
        if self.check_timer is None:
            self.check_timer = QTimer()
            self.check_timer.timeout.connect(self.check_idle_status)
        
        self.check_timer.start(self.CHECK_INTERVAL_MS)
        
        # 设置输入钩子
        if self.enable_input_hooks:
            self.setup_input_hooks()
    
    def stop(self) -> None:
        """
        停止空闲监视
        
        The watch ends... but the abyss remembers.
        """
        # 停止检查定时器
        if self.check_timer is not None:
            self.check_timer.stop()
        
        # 停止输入监听器
        self._stop_input_listeners()
        
        # 如果屏保激活，关闭它
        if self.is_screensaver_active:
            self.deactivate_screensaver()
    
    def setup_input_hooks(self) -> None:
        """
        设置鼠标/键盘监听钩子
        
        WARNING: The abyss extends its tendrils to sense your presence...
        
        使用 pynput 库监听鼠标移动和键盘敲击。
        注意：pynput 在单独的线程中运行，需要处理线程安全问题。
        """
        if self._listeners_started:
            return
        
        try:
            from pynput import mouse, keyboard
            
            # 创建鼠标监听器
            self._mouse_listener = mouse.Listener(
                on_move=self._on_mouse_move,
                on_click=self._on_mouse_click,
                on_scroll=self._on_mouse_scroll
            )
            
            # 创建键盘监听器
            self._keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            
            # 启动监听器（在后台线程中运行）
            self._mouse_listener.start()
            self._keyboard_listener.start()
            self._listeners_started = True
            
        except ImportError as e:
            print(f"⚠️ 警告：无法导入 pynput - {e}")
            print("深渊的感知能力受限，但监视仍将继续...")
        except Exception as e:
            print(f"⚠️ 警告：设置输入钩子失败 - {e}")
    
    def _stop_input_listeners(self) -> None:
        """
        停止输入监听器
        
        WARNING: The tendrils retract into the darkness...
        """
        if self._mouse_listener is not None:
            try:
                self._mouse_listener.stop()
            except Exception:
                pass
            self._mouse_listener = None
        
        if self._keyboard_listener is not None:
            try:
                self._keyboard_listener.stop()
            except Exception:
                pass
            self._keyboard_listener = None
        
        self._listeners_started = False
    
    def _on_mouse_move(self, x: int, y: int) -> None:
        """
        鼠标移动事件处理
        
        WARNING: Movement detected in the darkness...
        """
        self._handle_user_activity()
    
    def _on_mouse_click(self, x: int, y: int, button, pressed: bool) -> None:
        """
        鼠标点击事件处理
        
        WARNING: A disturbance in the deep...
        """
        self._handle_user_activity()
    
    def _on_mouse_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        """
        鼠标滚轮事件处理
        
        WARNING: The currents shift...
        """
        self._handle_user_activity()
    
    def _on_key_press(self, key) -> None:
        """
        键盘按下事件处理
        
        WARNING: A signal from the surface...
        """
        self._handle_user_activity()
    
    def _on_key_release(self, key) -> None:
        """
        键盘释放事件处理
        
        WARNING: The echo fades...
        """
        # 不需要在释放时处理，按下时已经处理了
        pass
    
    def _handle_user_activity(self) -> None:
        """
        处理用户活动（线程安全）
        
        WARNING: The sleeper awakens...
        
        此方法从 pynput 的后台线程调用，需要确保线程安全。
        使用 Qt 的信号机制或直接调用（Qt 会处理线程安全）。
        """
        # 记录唤醒请求时间（用于测试响应时间）
        if self.is_screensaver_active:
            self._wake_request_time = datetime.now()
        
        # 调用主线程的活动处理方法
        # 注意：这里直接调用，因为 on_user_activity 是线程安全的
        self.on_user_activity()
    
    def on_user_activity(self) -> None:
        """
        用户活动时调用，重置空闲计时器
        
        WARNING: The abyss senses your presence...
        """
        self.last_activity_time = datetime.now()
        
        # 触发回调
        if self.on_activity_detected:
            self.on_activity_detected()
        
        # 如果屏保激活，立即关闭
        if self.is_screensaver_active:
            self.deactivate_screensaver()
    
    def check_idle_status(self) -> None:
        """
        检查空闲状态
        
        WARNING: Measuring the silence of the deep...
        """
        if self.is_screensaver_active:
            # 已经在屏保模式，不需要再次检查
            return
        
        elapsed = datetime.now() - self.last_activity_time
        elapsed_seconds = elapsed.total_seconds()
        
        if elapsed_seconds >= self.idle_threshold:
            self.activate_screensaver()
    
    def is_idle(self) -> bool:
        """
        检查当前是否处于空闲状态（超过阈值）
        
        Returns:
            是否空闲超过阈值
        """
        elapsed = datetime.now() - self.last_activity_time
        return elapsed.total_seconds() >= self.idle_threshold
    
    def get_idle_time(self) -> float:
        """
        获取当前空闲时间（秒）
        
        Returns:
            空闲秒数
        """
        elapsed = datetime.now() - self.last_activity_time
        return elapsed.total_seconds()
    
    def get_time_until_screensaver(self) -> float:
        """
        获取距离屏保激活的剩余时间（秒）
        
        Returns:
            剩余秒数（如果已激活或已超过阈值，返回0）
        """
        if self.is_screensaver_active:
            return 0.0
        
        elapsed = self.get_idle_time()
        remaining = self.idle_threshold - elapsed
        return max(0.0, remaining)
    
    def activate_screensaver(self, manual: bool = False) -> None:
        """
        激活屏保模式（自动触发，宠物聚拢到中央）
        
        WARNING: The deep sea summons you to its embrace...
        
        Args:
            manual: 是否为手动激活（手动激活时宠物不聚拢）
        """
        if self.is_screensaver_active:
            return
        
        self.is_screensaver_active = True
        self._activation_mode = "manual" if manual else "auto"
        
        # 保存宠物原始位置
        self._save_pet_positions()
        
        # 激活深潜背景
        if self.ocean_background:
            self.ocean_background.activate()
        
        # 只有自动激活时才将宠物聚拢到中央
        # 手动激活时宠物保持原位
        if not manual:
            self.gather_pets_to_center()
        
        # 触发回调
        if self.on_screensaver_activated:
            self.on_screensaver_activated()
        
        mode_str = "手动" if manual else "自动"
        print(f"🌊 屏保模式已激活（{mode_str}） - 深渊召唤你...")
    
    def deactivate_screensaver(self) -> None:
        """
        关闭屏保模式
        
        WARNING: Ascending from the depths...
        """
        if not self.is_screensaver_active:
            return
        
        was_manual = self._activation_mode == "manual"
        self.is_screensaver_active = False
        self._activation_mode = None
        
        # 关闭深潜背景
        if self.ocean_background:
            self.ocean_background.deactivate()
        
        # 只有自动激活时才恢复宠物位置（因为手动激活时宠物没有移动）
        if not was_manual:
            self.restore_pet_positions()
        else:
            # 手动模式下清空保存的位置
            self.original_pet_positions.clear()
        
        # 重置最后活动时间
        self.last_activity_time = datetime.now()
        
        # 记录唤醒完成时间
        self._wake_complete_time = datetime.now()
        
        # 触发回调
        if self.on_screensaver_deactivated:
            self.on_screensaver_deactivated()
        
        print("🌊 屏保模式已关闭 - 返回水面...")
    
    def _save_pet_positions(self) -> None:
        """
        保存所有宠物的当前位置
        
        WARNING: Recording the positions of the creatures...
        """
        self.original_pet_positions.clear()
        
        if self.pet_manager is None:
            return
        
        for pet_id, pet_window in self.pet_manager.active_pet_windows.items():
            if hasattr(pet_window, 'pos'):
                self.original_pet_positions[pet_id] = QPoint(pet_window.pos())
    
    def gather_pets_to_center(self) -> None:
        """
        将宠物聚拢到屏幕中央
        
        WARNING: The creatures of the deep gather for their slumber...
        Uses QPropertyAnimation for smooth movement.
        """
        if self.pet_manager is None:
            return
        
        # 获取屏幕中心
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            center_x = geometry.width() // 2
            center_y = geometry.height() // 2
        else:
            center_x, center_y = 960, 540  # 默认值
        
        # 计算聚拢区域（中央 400x300 区域）
        import math
        
        active_pets = list(self.pet_manager.active_pet_windows.items())
        num_pets = len(active_pets)
        
        if num_pets == 0:
            return
        
        # 存储动画引用以防止被垃圾回收
        if not hasattr(self, '_gather_animations'):
            self._gather_animations = []
        self._gather_animations.clear()
        
        for i, (pet_id, widget) in enumerate(active_pets):
            # 计算聚拢位置（环形排列）
            if num_pets == 1:
                target_x = center_x - widget.width() // 2
                target_y = center_y - widget.height() // 2
            else:
                angle = (2 * math.pi * i) / num_pets
                radius = 100
                target_x = center_x + int(radius * math.cos(angle)) - widget.width() // 2
                target_y = center_y + int(radius * math.sin(angle)) - widget.height() // 2
            
            # 使用 QPropertyAnimation 进行平滑移动
            if hasattr(widget, 'pos') and hasattr(widget, 'move'):
                try:
                    animation = QPropertyAnimation(widget, b"pos")
                    animation.setDuration(1000)  # 1秒动画
                    animation.setStartValue(widget.pos())
                    animation.setEndValue(QPoint(target_x, target_y))
                    animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
                    animation.start()
                    self._gather_animations.append(animation)
                except Exception:
                    # 如果动画失败，回退到直接移动
                    widget.move(target_x, target_y)
            
            # 设置睡觉状态（如果支持）
            if hasattr(widget, 'set_sleeping'):
                widget.set_sleeping(True)
    
    def restore_pet_positions(self) -> None:
        """
        恢复宠物到原始位置
        
        WARNING: The creatures return to their domains...
        Uses QPropertyAnimation for smooth movement.
        """
        if self.pet_manager is None:
            return
        
        # 存储动画引用以防止被垃圾回收
        if not hasattr(self, '_restore_animations'):
            self._restore_animations = []
        self._restore_animations.clear()
        
        for pet_id, original_pos in self.original_pet_positions.items():
            if pet_id in self.pet_manager.active_pet_windows:
                widget = self.pet_manager.active_pet_windows[pet_id]
                
                # 使用 QPropertyAnimation 进行平滑恢复
                if hasattr(widget, 'pos') and hasattr(widget, 'move'):
                    try:
                        animation = QPropertyAnimation(widget, b"pos")
                        animation.setDuration(500)  # 0.5秒动画（恢复更快）
                        animation.setStartValue(widget.pos())
                        animation.setEndValue(original_pos)
                        animation.setEasingCurve(QEasingCurve.Type.OutQuad)
                        animation.start()
                        self._restore_animations.append(animation)
                    except Exception:
                        # 如果动画失败，回退到直接移动
                        widget.move(original_pos)
                
                # 恢复正常状态（如果支持）
                if hasattr(widget, 'set_sleeping'):
                    widget.set_sleeping(False)
        
        # 清空保存的位置
        self.original_pet_positions.clear()
    
    def get_wake_response_time(self) -> Optional[float]:
        """
        获取最近一次唤醒的响应时间（毫秒）
        
        Returns:
            响应时间（毫秒），如果没有记录则返回 None
        """
        if self._wake_request_time is None or self._wake_complete_time is None:
            return None
        
        delta = self._wake_complete_time - self._wake_request_time
        return delta.total_seconds() * 1000
    
    def set_idle_threshold(self, seconds: int) -> None:
        """
        设置空闲阈值
        
        Args:
            seconds: 空闲阈值（秒）
        """
        self.idle_threshold = max(1, seconds)
    
    def get_idle_threshold(self) -> int:
        """
        获取空闲阈值
        
        Returns:
            空闲阈值（秒）
        """
        return self.idle_threshold
    
    def is_screensaver_mode_active(self) -> bool:
        """
        检查屏保模式是否激活
        
        Returns:
            是否激活
        """
        return self.is_screensaver_active
    
    def get_original_pet_positions(self) -> Dict[str, QPoint]:
        """
        获取保存的宠物原始位置
        
        Returns:
            宠物ID到位置的映射
        """
        return self.original_pet_positions.copy()
    
    def force_activate_screensaver(self, manual: bool = False) -> None:
        """
        强制激活屏保（用于测试）
        
        WARNING: Forcing descent into the abyss...
        
        Args:
            manual: 是否为手动激活
        """
        self.activate_screensaver(manual=manual)
    
    def force_deactivate_screensaver(self) -> None:
        """
        强制关闭屏保（用于测试）
        
        WARNING: Forcing ascent from the depths...
        """
        self.deactivate_screensaver()
    
    def get_activation_mode(self) -> Optional[str]:
        """
        获取当前激活模式
        
        Returns:
            "manual" 表示手动激活，"auto" 表示自动激活，None 表示未激活
        """
        return self._activation_mode
    
    def is_manual_activation(self) -> bool:
        """
        检查是否为手动激活
        
        Returns:
            是否为手动激活
        """
        return self._activation_mode == "manual"
    
    def is_auto_activation(self) -> bool:
        """
        检查是否为自动激活
        
        Returns:
            是否为自动激活
        """
        return self._activation_mode == "auto"
    
    def activate_deep_dive_manual(self) -> None:
        """
        手动激活深潜模式（宠物不聚拢）
        
        WARNING: Manually descending into the abyss...
        """
        self.activate_screensaver(manual=True)
    
    def activate_deep_dive_auto(self) -> None:
        """
        自动激活深潜模式（宠物聚拢到中央）
        
        WARNING: The abyss calls you automatically...
        """
        self.activate_screensaver(manual=False)
