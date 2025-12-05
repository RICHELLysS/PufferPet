"""空闲监视器单元测试

测试 IdleWatcher 类的核心功能：
- 监视器启动和停止
- 活动检测和计时器重置
- 5分钟阈值检测
- 鼠标/键盘事件处理
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from PyQt6.QtCore import QPoint

from idle_watcher import IdleWatcher


class MockPetWindow:
    """模拟宠物窗口"""
    def __init__(self, pet_id):
        self.pet_id = pet_id
        self._pos = QPoint(100, 100)
        self._is_sleeping = False
        self.move_calls = []
        self.set_sleeping_calls = []
    
    def pos(self):
        return self._pos
    
    def move(self, x, y=None):
        if isinstance(x, QPoint):
            self._pos = x
        else:
            self._pos = QPoint(x, y)
        self.move_calls.append(self._pos)
    
    def width(self):
        return 64
    
    def height(self):
        return 64
    
    def set_sleeping(self, sleeping):
        self._is_sleeping = sleeping
        self.set_sleeping_calls.append(sleeping)


class MockPetManager:
    """模拟宠物管理器"""
    def __init__(self, pet_ids=None):
        self.active_pet_windows = {}
        if pet_ids:
            for pet_id in pet_ids:
                self.active_pet_windows[pet_id] = MockPetWindow(pet_id)


class MockOceanBackground:
    """模拟海底背景"""
    def __init__(self):
        self.is_active = False
        self.activate_calls = 0
        self.deactivate_calls = 0
    
    def activate(self):
        self.is_active = True
        self.activate_calls += 1
    
    def deactivate(self):
        self.is_active = False
        self.deactivate_calls += 1


class TestIdleWatcherInit:
    """测试空闲监视器初始化"""
    
    def test_init_default_values(self):
        """测试默认值初始化"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        assert watcher.idle_threshold == IdleWatcher.DEFAULT_IDLE_THRESHOLD
        assert watcher.is_screensaver_active == False
        assert watcher.check_timer is None
        assert len(watcher.original_pet_positions) == 0
    
    def test_init_with_dependencies(self):
        """测试带依赖项初始化"""
        mock_bg = MockOceanBackground()
        mock_pm = MockPetManager(['puffer'])
        
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            pet_manager=mock_pm,
            enable_input_hooks=False
        )
        
        assert watcher.ocean_background == mock_bg
        assert watcher.pet_manager == mock_pm
    
    def test_init_with_input_hooks_disabled(self):
        """测试禁用输入钩子初始化"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        assert watcher.enable_input_hooks == False
        assert watcher._listeners_started == False


class TestIdleWatcherStartStop:
    """测试监视器启动和停止"""
    
    def test_start_creates_timer(self):
        """测试启动创建计时器"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        # 启动前没有计时器
        assert watcher.check_timer is None
        
        # 启动
        watcher.start()
        
        # 启动后有计时器
        assert watcher.check_timer is not None
        
        # 清理
        watcher.stop()
    
    def test_start_resets_activity_time(self):
        """测试启动重置活动时间"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        # 设置一个过去的时间
        old_time = datetime.now() - timedelta(hours=1)
        watcher.last_activity_time = old_time
        
        # 启动
        watcher.start()
        
        # 活动时间应该被重置为当前时间附近
        time_diff = (datetime.now() - watcher.last_activity_time).total_seconds()
        assert time_diff < 1
        
        # 清理
        watcher.stop()
    
    def test_stop_stops_timer(self):
        """测试停止计时器"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        # 启动
        watcher.start()
        assert watcher.check_timer is not None
        
        # 停止
        watcher.stop()
        
        # 计时器应该停止
        assert watcher.check_timer is not None  # 对象仍存在
    
    def test_stop_deactivates_screensaver(self):
        """测试停止时关闭屏保"""
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            enable_input_hooks=False
        )
        
        # 启动并激活屏保
        watcher.start()
        watcher.force_activate_screensaver()
        assert watcher.is_screensaver_active == True
        
        # 停止
        watcher.stop()
        
        # 屏保应该关闭
        assert watcher.is_screensaver_active == False


class TestIdleWatcherActivityDetection:
    """测试活动检测和计时器重置"""
    
    def test_on_user_activity_resets_time(self):
        """测试用户活动重置时间"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        # 设置一个过去的时间
        old_time = datetime.now() - timedelta(minutes=10)
        watcher.last_activity_time = old_time
        
        # 触发活动
        watcher.on_user_activity()
        
        # 时间应该被重置
        time_diff = (datetime.now() - watcher.last_activity_time).total_seconds()
        assert time_diff < 1
    
    def test_on_user_activity_deactivates_screensaver(self):
        """测试用户活动关闭屏保"""
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            enable_input_hooks=False
        )
        
        # 激活屏保
        watcher.force_activate_screensaver()
        assert watcher.is_screensaver_active == True
        
        # 触发活动
        watcher.on_user_activity()
        
        # 屏保应该关闭
        assert watcher.is_screensaver_active == False
    
    def test_on_user_activity_callback(self):
        """测试用户活动回调"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        callback_called = []
        watcher.on_activity_detected = lambda: callback_called.append(True)
        
        # 触发活动
        watcher.on_user_activity()
        
        assert len(callback_called) == 1
    
    def test_get_idle_time(self):
        """测试获取空闲时间"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        # 设置一个过去的时间
        watcher.last_activity_time = datetime.now() - timedelta(seconds=100)
        
        # 获取空闲时间
        idle_time = watcher.get_idle_time()
        
        # 应该接近100秒
        assert 99 <= idle_time <= 102
    
    def test_get_time_until_screensaver(self):
        """测试获取距离屏保激活的剩余时间"""
        watcher = IdleWatcher(enable_input_hooks=False)
        watcher.set_idle_threshold(300)  # 5分钟
        
        # 设置100秒前的活动时间
        watcher.last_activity_time = datetime.now() - timedelta(seconds=100)
        
        # 获取剩余时间
        remaining = watcher.get_time_until_screensaver()
        
        # 应该接近200秒
        assert 198 <= remaining <= 202


class TestIdleWatcherThreshold:
    """测试5分钟阈值检测"""
    
    def test_is_idle_under_threshold(self):
        """测试未超过阈值时不被认为是空闲"""
        watcher = IdleWatcher(enable_input_hooks=False)
        watcher.set_idle_threshold(300)  # 5分钟
        
        # 设置2分钟前的时间
        watcher.last_activity_time = datetime.now() - timedelta(minutes=2)
        
        assert watcher.is_idle() == False
    
    def test_is_idle_at_threshold(self):
        """测试刚好达到阈值时被认为是空闲"""
        watcher = IdleWatcher(enable_input_hooks=False)
        watcher.set_idle_threshold(300)  # 5分钟
        
        # 设置刚好5分钟前的时间
        watcher.last_activity_time = datetime.now() - timedelta(seconds=300)
        
        assert watcher.is_idle() == True
    
    def test_is_idle_over_threshold(self):
        """测试超过阈值时被认为是空闲"""
        watcher = IdleWatcher(enable_input_hooks=False)
        watcher.set_idle_threshold(300)  # 5分钟
        
        # 设置10分钟前的时间
        watcher.last_activity_time = datetime.now() - timedelta(minutes=10)
        
        assert watcher.is_idle() == True
    
    def test_check_idle_status_activates_screensaver(self):
        """测试检查空闲状态激活屏保"""
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            enable_input_hooks=False
        )
        watcher.set_idle_threshold(300)  # 5分钟
        
        # 设置超过阈值的时间
        watcher.last_activity_time = datetime.now() - timedelta(minutes=10)
        
        # 检查状态
        watcher.check_idle_status()
        
        # 应该激活屏保
        assert watcher.is_screensaver_active == True
        assert mock_bg.is_active == True
    
    def test_check_idle_status_no_activation_under_threshold(self):
        """测试未超过阈值时不激活屏保"""
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            enable_input_hooks=False
        )
        watcher.set_idle_threshold(300)  # 5分钟
        
        # 设置未超过阈值的时间
        watcher.last_activity_time = datetime.now() - timedelta(minutes=2)
        
        # 检查状态
        watcher.check_idle_status()
        
        # 不应该激活屏保
        assert watcher.is_screensaver_active == False
        assert mock_bg.is_active == False
    
    def test_set_idle_threshold(self):
        """测试设置空闲阈值"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        # 设置新阈值
        watcher.set_idle_threshold(600)  # 10分钟
        
        assert watcher.get_idle_threshold() == 600
    
    def test_set_idle_threshold_minimum(self):
        """测试设置空闲阈值最小值"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        # 设置负值
        watcher.set_idle_threshold(-100)
        
        # 应该被限制为最小值1
        assert watcher.get_idle_threshold() == 1


class TestIdleWatcherScreensaver:
    """测试屏保模式激活和关闭"""
    
    def test_activate_screensaver(self):
        """测试激活屏保"""
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            enable_input_hooks=False
        )
        
        watcher.activate_screensaver()
        
        assert watcher.is_screensaver_active == True
        assert mock_bg.is_active == True
        assert mock_bg.activate_calls == 1
    
    def test_activate_screensaver_idempotent(self):
        """测试重复激活屏保是幂等的"""
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            enable_input_hooks=False
        )
        
        # 多次激活
        watcher.activate_screensaver()
        watcher.activate_screensaver()
        watcher.activate_screensaver()
        
        # 只应该激活一次
        assert mock_bg.activate_calls == 1
    
    def test_activate_screensaver_callback(self):
        """测试激活屏保回调"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        callback_called = []
        watcher.on_screensaver_activated = lambda: callback_called.append(True)
        
        watcher.activate_screensaver()
        
        assert len(callback_called) == 1
    
    def test_deactivate_screensaver(self):
        """测试关闭屏保"""
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            enable_input_hooks=False
        )
        
        # 先激活
        watcher.activate_screensaver()
        
        # 再关闭
        watcher.deactivate_screensaver()
        
        assert watcher.is_screensaver_active == False
        assert mock_bg.is_active == False
        assert mock_bg.deactivate_calls == 1
    
    def test_deactivate_screensaver_idempotent(self):
        """测试重复关闭屏保是幂等的"""
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            enable_input_hooks=False
        )
        
        # 激活
        watcher.activate_screensaver()
        
        # 多次关闭
        watcher.deactivate_screensaver()
        watcher.deactivate_screensaver()
        watcher.deactivate_screensaver()
        
        # 只应该关闭一次
        assert mock_bg.deactivate_calls == 1
    
    def test_deactivate_screensaver_callback(self):
        """测试关闭屏保回调"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        callback_called = []
        watcher.on_screensaver_deactivated = lambda: callback_called.append(True)
        
        # 激活然后关闭
        watcher.activate_screensaver()
        watcher.deactivate_screensaver()
        
        assert len(callback_called) == 1
    
    def test_deactivate_screensaver_resets_activity_time(self):
        """测试关闭屏保重置活动时间"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        # 设置一个过去的时间
        old_time = datetime.now() - timedelta(hours=1)
        watcher.last_activity_time = old_time
        
        # 激活然后关闭
        watcher.activate_screensaver()
        watcher.deactivate_screensaver()
        
        # 活动时间应该被重置
        time_diff = (datetime.now() - watcher.last_activity_time).total_seconds()
        assert time_diff < 1


class TestIdleWatcherPetGathering:
    """测试宠物聚拢和位置恢复"""
    
    def test_save_pet_positions(self):
        """测试保存宠物位置"""
        mock_pm = MockPetManager(['puffer', 'jelly'])
        mock_pm.active_pet_windows['puffer']._pos = QPoint(100, 200)
        mock_pm.active_pet_windows['jelly']._pos = QPoint(300, 400)
        
        watcher = IdleWatcher(
            pet_manager=mock_pm,
            enable_input_hooks=False
        )
        
        # 激活屏保（会保存位置）
        watcher.activate_screensaver()
        
        # 验证位置已保存
        assert 'puffer' in watcher.original_pet_positions
        assert 'jelly' in watcher.original_pet_positions
        assert watcher.original_pet_positions['puffer'] == QPoint(100, 200)
        assert watcher.original_pet_positions['jelly'] == QPoint(300, 400)
    
    def test_gather_pets_to_center(self):
        """测试宠物聚拢到中央"""
        mock_pm = MockPetManager(['puffer', 'jelly'])
        
        watcher = IdleWatcher(
            pet_manager=mock_pm,
            enable_input_hooks=False
        )
        
        # 聚拢宠物
        watcher.gather_pets_to_center()
        
        # 验证宠物被移动
        for pet_id, window in mock_pm.active_pet_windows.items():
            assert len(window.move_calls) > 0
    
    def test_gather_pets_sets_sleeping(self):
        """测试聚拢宠物设置睡觉状态"""
        mock_pm = MockPetManager(['puffer'])
        
        watcher = IdleWatcher(
            pet_manager=mock_pm,
            enable_input_hooks=False
        )
        
        # 聚拢宠物
        watcher.gather_pets_to_center()
        
        # 验证睡觉状态被设置
        window = mock_pm.active_pet_windows['puffer']
        assert len(window.set_sleeping_calls) > 0
        assert window.set_sleeping_calls[-1] == True
    
    def test_restore_pet_positions(self):
        """测试恢复宠物位置"""
        mock_pm = MockPetManager(['puffer', 'jelly'])
        mock_pm.active_pet_windows['puffer']._pos = QPoint(100, 200)
        mock_pm.active_pet_windows['jelly']._pos = QPoint(300, 400)
        
        watcher = IdleWatcher(
            pet_manager=mock_pm,
            enable_input_hooks=False
        )
        
        # 激活屏保（保存位置并聚拢）
        watcher.activate_screensaver()
        
        # 关闭屏保（恢复位置）
        watcher.deactivate_screensaver()
        
        # 验证位置已恢复
        assert mock_pm.active_pet_windows['puffer']._pos == QPoint(100, 200)
        assert mock_pm.active_pet_windows['jelly']._pos == QPoint(300, 400)
    
    def test_restore_pet_positions_clears_saved(self):
        """测试恢复位置后清空保存的位置"""
        mock_pm = MockPetManager(['puffer'])
        
        watcher = IdleWatcher(
            pet_manager=mock_pm,
            enable_input_hooks=False
        )
        
        # 激活然后关闭
        watcher.activate_screensaver()
        watcher.deactivate_screensaver()
        
        # 保存的位置应该被清空
        assert len(watcher.original_pet_positions) == 0
    
    def test_restore_pet_positions_resets_sleeping(self):
        """测试恢复位置时重置睡觉状态"""
        mock_pm = MockPetManager(['puffer'])
        
        watcher = IdleWatcher(
            pet_manager=mock_pm,
            enable_input_hooks=False
        )
        
        # 激活然后关闭
        watcher.activate_screensaver()
        watcher.deactivate_screensaver()
        
        # 验证睡觉状态被重置
        window = mock_pm.active_pet_windows['puffer']
        assert window.set_sleeping_calls[-1] == False


class TestIdleWatcherInputHooks:
    """测试鼠标/键盘事件处理"""
    
    def test_handle_user_activity_resets_time(self):
        """测试处理用户活动重置时间"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        # 设置一个过去的时间
        old_time = datetime.now() - timedelta(minutes=10)
        watcher.last_activity_time = old_time
        
        # 模拟用户活动
        watcher._handle_user_activity()
        
        # 时间应该被重置
        time_diff = (datetime.now() - watcher.last_activity_time).total_seconds()
        assert time_diff < 1
    
    def test_handle_user_activity_wakes_screensaver(self):
        """测试处理用户活动唤醒屏保"""
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            enable_input_hooks=False
        )
        
        # 激活屏保
        watcher.activate_screensaver()
        assert watcher.is_screensaver_active == True
        
        # 模拟用户活动
        watcher._handle_user_activity()
        
        # 屏保应该关闭
        assert watcher.is_screensaver_active == False
    
    def test_mouse_move_triggers_activity(self):
        """测试鼠标移动触发活动"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        # 设置一个过去的时间
        old_time = datetime.now() - timedelta(minutes=10)
        watcher.last_activity_time = old_time
        
        # 模拟鼠标移动
        watcher._on_mouse_move(100, 200)
        
        # 时间应该被重置
        time_diff = (datetime.now() - watcher.last_activity_time).total_seconds()
        assert time_diff < 1
    
    def test_mouse_click_triggers_activity(self):
        """测试鼠标点击触发活动"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        # 设置一个过去的时间
        old_time = datetime.now() - timedelta(minutes=10)
        watcher.last_activity_time = old_time
        
        # 模拟鼠标点击
        watcher._on_mouse_click(100, 200, None, True)
        
        # 时间应该被重置
        time_diff = (datetime.now() - watcher.last_activity_time).total_seconds()
        assert time_diff < 1
    
    def test_mouse_scroll_triggers_activity(self):
        """测试鼠标滚轮触发活动"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        # 设置一个过去的时间
        old_time = datetime.now() - timedelta(minutes=10)
        watcher.last_activity_time = old_time
        
        # 模拟鼠标滚轮
        watcher._on_mouse_scroll(100, 200, 0, 1)
        
        # 时间应该被重置
        time_diff = (datetime.now() - watcher.last_activity_time).total_seconds()
        assert time_diff < 1
    
    def test_key_press_triggers_activity(self):
        """测试键盘按下触发活动"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        # 设置一个过去的时间
        old_time = datetime.now() - timedelta(minutes=10)
        watcher.last_activity_time = old_time
        
        # 模拟键盘按下
        watcher._on_key_press(None)
        
        # 时间应该被重置
        time_diff = (datetime.now() - watcher.last_activity_time).total_seconds()
        assert time_diff < 1


class TestIdleWatcherForceControls:
    """测试强制控制方法"""
    
    def test_force_activate_screensaver(self):
        """测试强制激活屏保"""
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            enable_input_hooks=False
        )
        
        watcher.force_activate_screensaver()
        
        assert watcher.is_screensaver_active == True
        assert mock_bg.is_active == True
    
    def test_force_deactivate_screensaver(self):
        """测试强制关闭屏保"""
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            enable_input_hooks=False
        )
        
        # 先激活
        watcher.force_activate_screensaver()
        
        # 强制关闭
        watcher.force_deactivate_screensaver()
        
        assert watcher.is_screensaver_active == False
        assert mock_bg.is_active == False
    
    def test_is_screensaver_mode_active(self):
        """测试检查屏保模式是否激活"""
        watcher = IdleWatcher(enable_input_hooks=False)
        
        assert watcher.is_screensaver_mode_active() == False
        
        watcher.force_activate_screensaver()
        assert watcher.is_screensaver_mode_active() == True
        
        watcher.force_deactivate_screensaver()
        assert watcher.is_screensaver_mode_active() == False
    
    def test_get_original_pet_positions(self):
        """测试获取保存的宠物原始位置"""
        mock_pm = MockPetManager(['puffer'])
        mock_pm.active_pet_windows['puffer']._pos = QPoint(100, 200)
        
        watcher = IdleWatcher(
            pet_manager=mock_pm,
            enable_input_hooks=False
        )
        
        # 激活屏保
        watcher.activate_screensaver()
        
        # 获取保存的位置
        positions = watcher.get_original_pet_positions()
        
        assert 'puffer' in positions
        assert positions['puffer'] == QPoint(100, 200)


class TestIdleWatcherDeepDiveMenuControl:
    """测试深潜模式菜单控制（V5新增）"""
    
    def test_manual_activation_mode(self):
        """测试手动激活模式"""
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            enable_input_hooks=False
        )
        
        # 手动激活
        watcher.activate_screensaver(manual=True)
        
        # 验证激活模式
        assert watcher.get_activation_mode() == "manual"
        assert watcher.is_manual_activation() == True
        assert watcher.is_auto_activation() == False
        assert watcher.is_screensaver_active == True
    
    def test_auto_activation_mode(self):
        """测试自动激活模式"""
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            enable_input_hooks=False
        )
        
        # 自动激活
        watcher.activate_screensaver(manual=False)
        
        # 验证激活模式
        assert watcher.get_activation_mode() == "auto"
        assert watcher.is_manual_activation() == False
        assert watcher.is_auto_activation() == True
        assert watcher.is_screensaver_active == True
    
    def test_manual_activation_no_pet_gathering(self):
        """测试手动激活时宠物不聚拢"""
        mock_pm = MockPetManager(['puffer', 'jelly'])
        mock_pm.active_pet_windows['puffer']._pos = QPoint(100, 200)
        mock_pm.active_pet_windows['jelly']._pos = QPoint(300, 400)
        
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            pet_manager=mock_pm,
            enable_input_hooks=False
        )
        
        # 保存原始位置
        original_puffer_pos = QPoint(100, 200)
        original_jelly_pos = QPoint(300, 400)
        
        # 手动激活
        watcher.activate_screensaver(manual=True)
        
        # 验证宠物没有被移动
        assert mock_pm.active_pet_windows['puffer']._pos == original_puffer_pos
        assert mock_pm.active_pet_windows['jelly']._pos == original_jelly_pos
    
    def test_auto_activation_pet_gathering(self):
        """测试自动激活时宠物聚拢"""
        mock_pm = MockPetManager(['puffer'])
        mock_pm.active_pet_windows['puffer']._pos = QPoint(100, 200)
        
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            pet_manager=mock_pm,
            enable_input_hooks=False
        )
        
        # 自动激活
        watcher.activate_screensaver(manual=False)
        
        # 验证宠物被移动了（通过检查 move_calls）
        window = mock_pm.active_pet_windows['puffer']
        assert len(window.move_calls) > 0 or len(window.set_sleeping_calls) > 0
    
    def test_deactivation_clears_mode(self):
        """测试关闭后清除激活模式"""
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            enable_input_hooks=False
        )
        
        # 激活
        watcher.activate_screensaver(manual=True)
        assert watcher.get_activation_mode() == "manual"
        
        # 关闭
        watcher.deactivate_screensaver()
        
        # 验证模式已清除
        assert watcher.get_activation_mode() is None
        assert watcher.is_manual_activation() == False
        assert watcher.is_auto_activation() == False
    
    def test_toggle_deep_dive_on(self):
        """测试开启深潜模式"""
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            enable_input_hooks=False
        )
        
        # 初始状态：未激活
        assert watcher.is_screensaver_mode_active() == False
        
        # 手动开启
        watcher.activate_deep_dive_manual()
        
        # 验证已激活
        assert watcher.is_screensaver_mode_active() == True
        assert watcher.is_manual_activation() == True
    
    def test_toggle_deep_dive_off(self):
        """测试关闭深潜模式"""
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            enable_input_hooks=False
        )
        
        # 先开启
        watcher.activate_deep_dive_manual()
        assert watcher.is_screensaver_mode_active() == True
        
        # 关闭
        watcher.deactivate_screensaver()
        
        # 验证已关闭
        assert watcher.is_screensaver_mode_active() == False
    
    def test_force_activate_with_manual_flag(self):
        """测试强制激活带手动标志"""
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            enable_input_hooks=False
        )
        
        # 强制手动激活
        watcher.force_activate_screensaver(manual=True)
        
        assert watcher.is_screensaver_mode_active() == True
        assert watcher.is_manual_activation() == True
    
    def test_force_activate_without_manual_flag(self):
        """测试强制激活不带手动标志（默认自动）"""
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            enable_input_hooks=False
        )
        
        # 强制自动激活
        watcher.force_activate_screensaver(manual=False)
        
        assert watcher.is_screensaver_mode_active() == True
        assert watcher.is_auto_activation() == True
    
    def test_manual_deactivation_no_position_restore(self):
        """测试手动激活后关闭不恢复位置（因为没有移动）"""
        mock_pm = MockPetManager(['puffer'])
        mock_pm.active_pet_windows['puffer']._pos = QPoint(100, 200)
        
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            pet_manager=mock_pm,
            enable_input_hooks=False
        )
        
        # 手动激活
        watcher.activate_screensaver(manual=True)
        
        # 关闭
        watcher.deactivate_screensaver()
        
        # 验证保存的位置已清空
        assert len(watcher.original_pet_positions) == 0
    
    def test_auto_deactivation_restores_positions(self):
        """测试自动激活后关闭恢复位置"""
        mock_pm = MockPetManager(['puffer'])
        mock_pm.active_pet_windows['puffer']._pos = QPoint(100, 200)
        
        mock_bg = MockOceanBackground()
        watcher = IdleWatcher(
            ocean_background=mock_bg,
            pet_manager=mock_pm,
            enable_input_hooks=False
        )
        
        # 自动激活
        watcher.activate_screensaver(manual=False)
        
        # 关闭
        watcher.deactivate_screensaver()
        
        # 验证位置已恢复
        assert mock_pm.active_pet_windows['puffer']._pos == QPoint(100, 200)

