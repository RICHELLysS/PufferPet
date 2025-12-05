"""忽视追踪器单元测试"""
import pytest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from data_manager import DataManager
from ignore_tracker import IgnoreTracker


class MockPetWindow:
    """模拟宠物窗口"""
    def __init__(self, pet_id):
        self.pet_id = pet_id
        self.is_angry = False
        self.set_angry_calls = []
    
    def set_angry(self, angry):
        self.is_angry = angry
        self.set_angry_calls.append(angry)


class MockPetManager:
    """模拟宠物管理器"""
    def __init__(self, pet_ids=None):
        self.active_pet_windows = {}
        if pet_ids:
            for pet_id in pet_ids:
                self.active_pet_windows[pet_id] = MockPetWindow(pet_id)


@pytest.fixture
def temp_data_file():
    """创建临时数据文件"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    yield temp_file
    if os.path.exists(temp_file):
        os.remove(temp_file)


@pytest.fixture
def data_manager(temp_data_file):
    """创建数据管理器"""
    return DataManager(data_file=temp_data_file)


class TestIgnoreTrackerInit:
    """测试忽视追踪器初始化"""
    
    def test_init_default_values(self):
        """测试默认值初始化"""
        mock_pm = MockPetManager()
        tracker = IgnoreTracker(mock_pm, show_notifications=False)

        assert tracker.pet_manager == mock_pm
        assert tracker.ignore_threshold == IgnoreTracker.DEFAULT_IGNORE_THRESHOLD
        assert tracker.mischief_mode == False
        assert tracker.check_timer is None
        assert len(tracker._angry_pets) == 0
    
    def test_init_with_notifications_disabled(self):
        """测试禁用通知初始化"""
        mock_pm = MockPetManager()
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        assert tracker._show_notifications == False


class TestIgnoreTrackerStartStop:
    """测试计时器启动和停止"""
    
    def test_start_creates_timer(self):
        """测试启动创建计时器"""
        mock_pm = MockPetManager()
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        # 启动前没有计时器
        assert tracker.check_timer is None
        
        # 启动
        tracker.start()
        
        # 启动后有计时器
        assert tracker.check_timer is not None
        
        # 清理
        tracker.stop()
    
    def test_start_resets_interaction_time(self):
        """测试启动重置交互时间"""
        mock_pm = MockPetManager()
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        # 设置一个过去的时间
        old_time = datetime.now() - timedelta(hours=2)
        tracker.last_interaction_time = old_time
        
        # 启动
        tracker.start()
        
        # 交互时间应该被重置为当前时间附近
        time_diff = (datetime.now() - tracker.last_interaction_time).total_seconds()
        assert time_diff < 1  # 应该在1秒内
        
        # 清理
        tracker.stop()
    
    def test_stop_stops_timer(self):
        """测试停止计时器"""
        mock_pm = MockPetManager()
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        # 启动
        tracker.start()
        assert tracker.check_timer is not None
        
        # 停止
        tracker.stop()
        
        # 计时器应该停止（但对象仍存在）
        assert tracker.check_timer is not None


class TestIgnoreTrackerInteraction:
    """测试交互重置逻辑"""
    
    def test_on_user_interaction_resets_time(self):
        """测试用户交互重置时间"""
        mock_pm = MockPetManager()
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        # 设置一个过去的时间
        old_time = datetime.now() - timedelta(hours=1)
        tracker.last_interaction_time = old_time
        
        # 触发交互
        tracker.on_user_interaction()
        
        # 时间应该被重置
        time_diff = (datetime.now() - tracker.last_interaction_time).total_seconds()
        assert time_diff < 1
    
    def test_get_time_since_interaction(self):
        """测试获取自上次交互以来的时间"""
        mock_pm = MockPetManager()
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        # 设置一个过去的时间
        tracker.last_interaction_time = datetime.now() - timedelta(seconds=100)
        
        # 获取时间差
        elapsed = tracker.get_time_since_interaction()
        
        # 应该接近100秒
        assert 99 <= elapsed <= 101


class TestIgnoreTrackerThreshold:
    """测试1小时阈值检测"""
    
    def test_is_ignored_under_threshold(self):
        """测试未超过阈值时不被认为是忽视"""
        mock_pm = MockPetManager()
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        # 设置30分钟前的时间
        tracker.last_interaction_time = datetime.now() - timedelta(minutes=30)
        
        assert tracker.is_ignored() == False
    
    def test_is_ignored_at_threshold(self):
        """测试刚好达到阈值时被认为是忽视"""
        mock_pm = MockPetManager()
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        # 设置刚好1小时前的时间
        tracker.last_interaction_time = datetime.now() - timedelta(seconds=3600)
        
        assert tracker.is_ignored() == True
    
    def test_is_ignored_over_threshold(self):
        """测试超过阈值时被认为是忽视"""
        mock_pm = MockPetManager()
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        # 设置2小时前的时间
        tracker.last_interaction_time = datetime.now() - timedelta(hours=2)
        
        assert tracker.is_ignored() == True
    
    def test_check_ignore_status_triggers_mischief(self):
        """测试检查忽视状态触发捣蛋模式"""
        mock_pm = MockPetManager(['puffer'])
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        # 设置超过阈值的时间
        tracker.last_interaction_time = datetime.now() - timedelta(hours=2)
        
        # 检查状态
        tracker.check_ignore_status()
        
        # 应该触发捣蛋模式
        assert tracker.mischief_mode == True
    
    def test_check_ignore_status_no_trigger_under_threshold(self):
        """测试未超过阈值时不触发捣蛋模式"""
        mock_pm = MockPetManager(['puffer'])
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        # 设置未超过阈值的时间
        tracker.last_interaction_time = datetime.now() - timedelta(minutes=30)
        
        # 检查状态
        tracker.check_ignore_status()
        
        # 不应该触发捣蛋模式
        assert tracker.mischief_mode == False


class TestIgnoreTrackerMischiefMode:
    """测试捣蛋模式触发和退出"""
    
    def test_trigger_mischief_mode_sets_flag(self):
        """测试触发捣蛋模式设置标志"""
        mock_pm = MockPetManager()
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        tracker.trigger_mischief_mode()
        
        assert tracker.mischief_mode == True
    
    def test_trigger_mischief_mode_sets_pets_angry(self):
        """测试触发捣蛋模式让所有宠物愤怒"""
        mock_pm = MockPetManager(['puffer', 'jelly', 'starfish'])
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        tracker.trigger_mischief_mode()
        
        # 所有宠物应该愤怒
        for pet_id, window in mock_pm.active_pet_windows.items():
            assert window.is_angry == True
            assert pet_id in tracker.get_angry_pets()
    
    def test_trigger_mischief_mode_idempotent(self):
        """测试重复触发捣蛋模式是幂等的"""
        mock_pm = MockPetManager(['puffer'])
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        # 第一次触发
        tracker.trigger_mischief_mode()
        angry_count_1 = len(tracker.get_angry_pets())
        
        # 第二次触发
        tracker.trigger_mischief_mode()
        angry_count_2 = len(tracker.get_angry_pets())
        
        # 愤怒宠物数量应该相同
        assert angry_count_1 == angry_count_2
    
    def test_trigger_mischief_mode_callback(self):
        """测试触发捣蛋模式回调"""
        mock_pm = MockPetManager()
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        callback_called = []
        tracker.on_mischief_triggered = lambda: callback_called.append(True)
        
        tracker.trigger_mischief_mode()
        
        assert len(callback_called) == 1
    
    def test_calm_pet_removes_from_angry(self):
        """测试安抚宠物从愤怒集合中移除"""
        mock_pm = MockPetManager(['puffer', 'jelly'])
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        # 触发捣蛋模式
        tracker.trigger_mischief_mode()
        assert 'puffer' in tracker.get_angry_pets()
        
        # 安抚河豚
        tracker.calm_pet('puffer')
        
        # 河豚不应该在愤怒集合中
        assert 'puffer' not in tracker.get_angry_pets()
        # 水母仍然愤怒
        assert 'jelly' in tracker.get_angry_pets()
    
    def test_calm_pet_restores_window_state(self):
        """测试安抚宠物恢复窗口状态"""
        mock_pm = MockPetManager(['puffer'])
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        # 触发捣蛋模式
        tracker.trigger_mischief_mode()
        assert mock_pm.active_pet_windows['puffer'].is_angry == True
        
        # 安抚
        tracker.calm_pet('puffer')
        
        # 窗口状态应该恢复
        assert mock_pm.active_pet_windows['puffer'].is_angry == False
    
    def test_calm_pet_callback(self):
        """测试安抚宠物回调"""
        mock_pm = MockPetManager(['puffer'])
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        calmed_pets = []
        tracker.on_pet_calmed = lambda pet_id: calmed_pets.append(pet_id)
        
        # 触发捣蛋模式
        tracker.trigger_mischief_mode()
        
        # 安抚
        tracker.calm_pet('puffer')
        
        assert 'puffer' in calmed_pets
    
    def test_calm_all_pets_exits_mischief_mode(self):
        """测试安抚所有宠物退出捣蛋模式"""
        mock_pm = MockPetManager(['puffer', 'jelly'])
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        # 触发捣蛋模式
        tracker.trigger_mischief_mode()
        assert tracker.mischief_mode == True
        
        # 安抚所有宠物
        tracker.calm_pet('puffer')
        tracker.calm_pet('jelly')
        
        # 应该退出捣蛋模式
        assert tracker.mischief_mode == False
    
    def test_exit_mischief_mode_resets_state(self):
        """测试退出捣蛋模式重置状态"""
        mock_pm = MockPetManager(['puffer', 'jelly'])
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        # 触发捣蛋模式
        tracker.trigger_mischief_mode()
        
        # 手动退出
        tracker.exit_mischief_mode()
        
        # 状态应该重置
        assert tracker.mischief_mode == False
        assert len(tracker.get_angry_pets()) == 0
        
        # 所有宠物应该恢复正常
        for window in mock_pm.active_pet_windows.values():
            assert window.is_angry == False
    
    def test_exit_mischief_mode_resets_interaction_time(self):
        """测试退出捣蛋模式重置交互时间"""
        mock_pm = MockPetManager()
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        # 设置一个过去的时间
        old_time = datetime.now() - timedelta(hours=2)
        tracker.last_interaction_time = old_time
        
        # 触发并退出捣蛋模式
        tracker.trigger_mischief_mode()
        tracker.exit_mischief_mode()
        
        # 交互时间应该被重置
        time_diff = (datetime.now() - tracker.last_interaction_time).total_seconds()
        assert time_diff < 1
    
    def test_exit_mischief_mode_callback(self):
        """测试退出捣蛋模式回调"""
        mock_pm = MockPetManager()
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        callback_called = []
        tracker.on_mischief_ended = lambda: callback_called.append(True)
        
        # 触发并退出
        tracker.trigger_mischief_mode()
        tracker.exit_mischief_mode()
        
        assert len(callback_called) == 1
    
    def test_is_pet_angry(self):
        """测试检查宠物是否愤怒"""
        mock_pm = MockPetManager(['puffer', 'jelly'])
        tracker = IgnoreTracker(mock_pm, show_notifications=False)
        
        # 初始状态
        assert tracker.is_pet_angry('puffer') == False
        
        # 触发捣蛋模式
        tracker.trigger_mischief_mode()
        assert tracker.is_pet_angry('puffer') == True
        assert tracker.is_pet_angry('jelly') == True
        
        # 安抚河豚
        tracker.calm_pet('puffer')
        assert tracker.is_pet_angry('puffer') == False
        assert tracker.is_pet_angry('jelly') == True
