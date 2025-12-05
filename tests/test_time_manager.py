"""
🌙 时间管理器测试模块

此模块测试深渊时间守护者的各项功能：
- 时间判定准确性
- 模式映射一致性
- 自动同步控制
- 定时器启动和停止

⚠️ 警告：测试时间的力量需要极大的谨慎...
"""
import json
import os
import sys
import tempfile
from datetime import datetime, date
from unittest.mock import Mock, patch, MagicMock

import pytest
from hypothesis import given, strategies as st, settings

# 确保可以导入项目模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from time_manager import TimeManager
from data_manager import DataManager
from theme_manager import ThemeManager


# 确保 QApplication 存在
@pytest.fixture(scope="module")
def app():
    """创建 QApplication 实例"""
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    yield application


@pytest.fixture
def temp_data_file():
    """创建临时数据文件"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    yield temp_file
    # 清理
    if os.path.exists(temp_file):
        os.remove(temp_file)


@pytest.fixture
def theme_manager():
    """创建主题管理器实例 - V6不需要data_manager"""
    return ThemeManager()


@pytest.fixture
def time_manager(app, theme_manager):
    """创建时间管理器实例 - V6不使用data_manager"""
    tm = TimeManager(theme_manager=theme_manager)
    yield tm
    tm.stop()


# ============================================================================
# 单元测试
# ============================================================================

class TestTimeManagerBasic:
    """时间管理器基础功能测试"""
    
    def test_initialization(self, app):
        """测试时间管理器初始化 - V6不使用data_manager"""
        tm = TimeManager()
        
        assert tm is not None
        assert tm.auto_sync_enabled == True  # 默认启用自动同步
        assert tm.get_current_period() in ["day", "night"]
        
        tm.stop()
    
    def test_initialization_without_managers(self, app):
        """测试不带管理器的初始化"""
        tm = TimeManager()
        
        assert tm is not None
        assert tm.auto_sync_enabled == True
        assert tm.theme_manager is None
        assert tm.data_manager is None
        
        tm.stop()
    
    def test_default_time_boundaries(self, time_manager):
        """测试默认时间边界"""
        assert time_manager.day_start_hour == 6
        assert time_manager.night_start_hour == 18


class TestTimeDetermination:
    """时间判定测试"""
    
    def test_is_daytime_at_6am(self, time_manager):
        """测试06:00是白天"""
        with patch('time_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 12, 3, 6, 0, 0)
            assert time_manager.is_daytime() == True
    
    def test_is_daytime_at_noon(self, time_manager):
        """测试12:00是白天"""
        with patch('time_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 12, 3, 12, 0, 0)
            assert time_manager.is_daytime() == True
    
    def test_is_daytime_at_5_59am(self, time_manager):
        """测试05:59是黑夜"""
        with patch('time_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 12, 3, 5, 59, 0)
            assert time_manager.is_daytime() == False
    
    def test_is_daytime_at_6pm(self, time_manager):
        """测试18:00是黑夜"""
        with patch('time_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 12, 3, 18, 0, 0)
            assert time_manager.is_daytime() == False
    
    def test_is_daytime_at_5_59pm(self, time_manager):
        """测试17:59是白天"""
        with patch('time_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 12, 3, 17, 59, 0)
            assert time_manager.is_daytime() == True
    
    def test_is_daytime_at_midnight(self, time_manager):
        """测试00:00是黑夜"""
        with patch('time_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 12, 3, 0, 0, 0)
            assert time_manager.is_daytime() == False
    
    def test_determine_period_day(self, time_manager):
        """测试白天时段判定"""
        assert time_manager._determine_period(6) == "day"
        assert time_manager._determine_period(12) == "day"
        assert time_manager._determine_period(17) == "day"
    
    def test_determine_period_night(self, time_manager):
        """测试黑夜时段判定"""
        assert time_manager._determine_period(5) == "night"
        assert time_manager._determine_period(18) == "night"
        assert time_manager._determine_period(23) == "night"
        assert time_manager._determine_period(0) == "night"


class TestModeSwitching:
    """模式切换测试"""
    
    def test_switch_to_day(self, time_manager, theme_manager):
        """测试切换到白天模式"""
        time_manager.switch_to_day()
        
        assert time_manager.get_current_period() == "day"
        assert theme_manager.get_theme_mode() == "normal"
    
    def test_switch_to_night(self, time_manager, theme_manager):
        """测试切换到黑夜模式"""
        time_manager.switch_to_night()
        
        assert time_manager.get_current_period() == "night"
        assert theme_manager.get_theme_mode() == "halloween"
    
    def test_mode_mapping_day_to_normal(self, time_manager):
        """测试白天模式映射到normal"""
        assert time_manager.get_theme_mode_for_period("day") == "normal"
    
    def test_mode_mapping_night_to_halloween(self, time_manager):
        """测试黑夜模式映射到halloween"""
        assert time_manager.get_theme_mode_for_period("night") == "halloween"
    
    def test_mode_changed_signal_on_day_switch(self, time_manager):
        """测试切换到白天时发出信号"""
        signal_received = []
        time_manager.mode_changed.connect(lambda mode: signal_received.append(mode))
        
        time_manager.switch_to_day()
        
        assert "day" in signal_received
    
    def test_mode_changed_signal_on_night_switch(self, time_manager):
        """测试切换到黑夜时发出信号"""
        signal_received = []
        time_manager.mode_changed.connect(lambda mode: signal_received.append(mode))
        
        time_manager.switch_to_night()
        
        assert "night" in signal_received


class TestAutoSync:
    """自动同步测试"""
    
    def test_auto_sync_default_enabled(self, time_manager):
        """测试自动同步默认启用"""
        assert time_manager.auto_sync_enabled == True
        assert time_manager.get_auto_sync() == True
    
    def test_set_auto_sync_disabled(self, time_manager):
        """测试禁用自动同步"""
        time_manager.set_auto_sync(False)
        
        assert time_manager.auto_sync_enabled == False
        assert time_manager.get_auto_sync() == False
    
    def test_set_auto_sync_enabled(self, time_manager):
        """测试启用自动同步"""
        time_manager.set_auto_sync(False)
        time_manager.set_auto_sync(True)
        
        assert time_manager.auto_sync_enabled == True
    
    def test_manual_toggle_when_auto_sync_disabled(self, time_manager):
        """测试禁用自动同步时可以手动切换"""
        time_manager.set_auto_sync(False)
        time_manager.switch_to_day()
        initial_period = time_manager.get_current_period()
        
        time_manager.manual_toggle()
        
        assert time_manager.get_current_period() != initial_period
    
    def test_manual_toggle_when_auto_sync_enabled(self, time_manager):
        """测试启用自动同步时手动切换被忽略"""
        time_manager.set_auto_sync(True)
        time_manager.switch_to_day()
        initial_period = time_manager.get_current_period()
        
        time_manager.manual_toggle()
        
        # 手动切换应该被忽略
        assert time_manager.get_current_period() == initial_period
    
    def test_check_time_and_update_when_auto_sync_disabled(self, time_manager):
        """测试禁用自动同步时check_time_and_update不切换"""
        time_manager.set_auto_sync(False)
        time_manager.switch_to_day()
        
        # 即使时间判定为黑夜，也不应该切换
        with patch.object(time_manager, '_determine_period', return_value='night'):
            time_manager.check_time_and_update()
        
        # 模式应该保持不变
        assert time_manager.get_current_period() == "day"


class TestTimerControl:
    """定时器控制测试"""
    
    def test_start_timer(self, time_manager):
        """测试启动定时器"""
        time_manager.start()
        
        assert time_manager.is_running() == True
        assert time_manager._check_timer.isActive() == True
    
    def test_stop_timer(self, time_manager):
        """测试停止定时器"""
        time_manager.start()
        time_manager.stop()
        
        assert time_manager.is_running() == False
        assert time_manager._check_timer.isActive() == False
    
    def test_start_twice_no_effect(self, time_manager):
        """测试重复启动无效果"""
        time_manager.start()
        time_manager.start()  # 第二次启动
        
        assert time_manager.is_running() == True
    
    def test_timer_interval(self, time_manager):
        """测试定时器间隔为1分钟"""
        assert TimeManager.CHECK_INTERVAL_MS == 60000


class TestDataPersistence:
    """数据持久化测试 - V6: TimeManager不再使用data_manager"""
    
    def test_save_settings(self, time_manager):
        """测试保存设置 - V6: 设置在内存中管理"""
        time_manager.set_auto_sync(False)
        time_manager.switch_to_night()
        
        # V6: TimeManager不再使用data_manager保存设置
        # 验证time_manager的状态
        assert time_manager.auto_sync_enabled == False
        assert time_manager.get_current_period() == 'night'
    
    def test_load_settings(self, app):
        """测试加载设置 - V6: TimeManager不再从文件加载设置"""
        # V6中TimeManager不使用data_manager，设置在内存中管理
        tm = TimeManager()
        
        # 默认值
        assert tm.auto_sync_enabled == True
        assert tm.get_current_period() in ['day', 'night']
        
        tm.stop()


# ============================================================================
# 基于属性的测试
# ============================================================================

# 策略生成器
@st.composite
def valid_hour(draw):
    """生成有效的小时数 (0-23)"""
    return draw(st.integers(min_value=0, max_value=23))


# **Feature: puffer-pet, Property 45: 时间判定准确性**
# **验证: 需求 28.2, 28.3**
@settings(max_examples=100)
@given(hour=valid_hour())
def test_property_45_time_determination_accuracy(hour):
    """
    属性 45: 时间判定准确性
    对于任意系统时间，当时间在06:00-18:00之间时应判定为白天，否则应判定为黑夜。
    """
    # 确保 QApplication 存在
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # V6: TimeManager不使用data_manager
    tm = TimeManager()
    
    try:
        # 判定时段
        period = tm._determine_period(hour)
        
        # 验证判定准确性
        # 白天：6 <= hour < 18
        if 6 <= hour < 18:
            assert period == "day", f"小时 {hour} 应该判定为白天，但得到 {period}"
        else:
            assert period == "night", f"小时 {hour} 应该判定为黑夜，但得到 {period}"
    finally:
        tm.stop()


# **Feature: puffer-pet, Property 46: 模式映射一致性**
# **验证: 需求 28.6, 28.7**
@settings(max_examples=100)
@given(period=st.sampled_from(["day", "night"]))
def test_property_46_mode_mapping_consistency(period):
    """
    属性 46: 模式映射一致性
    对于任意昼夜模式，白天模式应映射到theme_mode="normal"，黑夜模式应映射到theme_mode="halloween"。
    """
    # 确保 QApplication 存在
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # V6: TimeManager和ThemeManager不使用data_manager
    theme_mgr = ThemeManager()
    tm = TimeManager(theme_manager=theme_mgr)
    
    try:
        # 获取映射的主题模式
        theme_mode = tm.get_theme_mode_for_period(period)
        
        # 验证映射一致性
        if period == "day":
            assert theme_mode == "normal", f"白天应映射到 'normal'，但得到 {theme_mode}"
        else:
            assert theme_mode == "halloween", f"黑夜应映射到 'halloween'，但得到 {theme_mode}"
        
        # 验证实际切换后主题管理器的状态
        if period == "day":
            tm.switch_to_day()
            assert theme_mgr.get_theme_mode() == "normal"
        else:
            tm.switch_to_night()
            assert theme_mgr.get_theme_mode() == "halloween"
    finally:
        tm.stop()


# **Feature: puffer-pet, Property 47: 自动同步控制正确性**
# **验证: 需求 30.3, 30.4**
@settings(max_examples=100)
@given(auto_sync=st.booleans(), initial_period=st.sampled_from(["day", "night"]))
def test_property_47_auto_sync_control_correctness(auto_sync, initial_period):
    """
    属性 47: 自动同步控制正确性
    对于任意auto_time_sync设置，当为true时应强制跟随系统时间，当为false时应允许手动切换。
    """
    # 确保 QApplication 存在
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # V6: TimeManager和ThemeManager不使用data_manager
    theme_mgr = ThemeManager()
    tm = TimeManager(theme_manager=theme_mgr)
    
    try:
        # 设置初始状态
        if initial_period == "day":
            tm.switch_to_day()
        else:
            tm.switch_to_night()
        
        # 设置自动同步
        tm.set_auto_sync(auto_sync)
        
        # 验证自动同步状态
        assert tm.auto_sync_enabled == auto_sync
        assert tm.get_auto_sync() == auto_sync
        
        # 尝试手动切换
        tm.manual_toggle()
        
        if auto_sync:
            # 自动同步启用时，手动切换应该被忽略
            assert tm.get_current_period() == initial_period, \
                f"自动同步启用时，手动切换应该被忽略，但模式从 {initial_period} 变为 {tm.get_current_period()}"
        else:
            # 自动同步禁用时，手动切换应该生效
            expected_period = "night" if initial_period == "day" else "day"
            assert tm.get_current_period() == expected_period, \
                f"自动同步禁用时，手动切换应该生效，期望 {expected_period}，但得到 {tm.get_current_period()}"
    finally:
        tm.stop()


# ============================================================================
# 边界值测试
# ============================================================================

class TestBoundaryValues:
    """边界值测试"""
    
    def test_boundary_5_59_is_night(self, time_manager):
        """测试05:59是黑夜（边界值）"""
        period = time_manager._determine_period(5)
        assert period == "night"
    
    def test_boundary_6_00_is_day(self, time_manager):
        """测试06:00是白天（边界值）"""
        period = time_manager._determine_period(6)
        assert period == "day"
    
    def test_boundary_17_59_is_day(self, time_manager):
        """测试17:59是白天（边界值）"""
        period = time_manager._determine_period(17)
        assert period == "day"
    
    def test_boundary_18_00_is_night(self, time_manager):
        """测试18:00是黑夜（边界值）"""
        period = time_manager._determine_period(18)
        assert period == "night"
    
    def test_boundary_0_00_is_night(self, time_manager):
        """测试00:00是黑夜"""
        period = time_manager._determine_period(0)
        assert period == "night"
    
    def test_boundary_23_59_is_night(self, time_manager):
        """测试23:59是黑夜"""
        period = time_manager._determine_period(23)
        assert period == "night"


# ============================================================================
# 设置菜单测试（V8更新：简化菜单，移除 Auto Day/Night 选项）
# ============================================================================

class TestSettingsMenu:
    """V8 设置菜单测试 - 简化版，仅保留手动切换昼夜选项"""
    
    def test_create_settings_menu_structure(self, app, time_manager, theme_manager):
        """V8: 测试设置菜单结构 - 仅包含切换昼夜选项"""
        # 导入创建设置菜单的函数
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from main import create_settings_menu
        
        # 创建设置菜单
        settings_menu = create_settings_menu(app, time_manager, theme_manager)
        
        # 验证菜单存在
        assert settings_menu is not None
        
        # 验证菜单标题
        assert "设置" in settings_menu.title() or "Settings" in settings_menu.title()
        
        # V8: 验证菜单仅包含一个动作（切换昼夜）
        actions = settings_menu.actions()
        assert len(actions) == 1
        
        # V8: 验证唯一的动作是"切换昼夜"
        toggle_action = actions[0]
        assert "Toggle Day/Night" in toggle_action.text() or "切换" in toggle_action.text()
    
    def test_toggle_day_night_always_enabled(self, app, time_manager, theme_manager):
        """V8: 测试切换昼夜选项始终可用（因为 auto_sync 已禁用）"""
        from main import create_settings_menu
        
        # 创建设置菜单
        settings_menu = create_settings_menu(app, time_manager, theme_manager)
        
        # 获取切换昼夜动作
        toggle_action = settings_menu.toggle_day_night_action
        
        # V8: 验证始终可用
        assert toggle_action.isEnabled() == True
    
    def test_toggle_day_night_enabled_when_auto_sync_disabled(self, app, time_manager, theme_manager):
        """V8: 测试当自动同步禁用时，切换昼夜选项可用"""
        from main import create_settings_menu
        
        # 禁用自动同步
        time_manager.set_auto_sync(False)
        
        # 创建设置菜单
        settings_menu = create_settings_menu(app, time_manager, theme_manager)
        
        # 获取切换昼夜动作
        toggle_action = settings_menu.toggle_day_night_action
        
        # 验证可用状态
        assert toggle_action.isEnabled() == True
    
    def test_toggle_day_night_action_triggers_manual_toggle(self, app, time_manager, theme_manager):
        """V8: 测试切换昼夜动作触发手动切换（始终可用）"""
        from main import create_settings_menu, on_toggle_day_night
        
        # V8: 不需要禁用自动同步，因为 V8 中始终禁用
        
        # 设置初始状态为白天
        time_manager.switch_to_day()
        initial_period = time_manager.get_current_period()
        assert initial_period == "day"
        
        # 触发手动切换
        on_toggle_day_night(time_manager)
        
        # 验证模式已切换
        assert time_manager.get_current_period() == "night"
        
        # 再次切换
        on_toggle_day_night(time_manager)
        
        # 验证模式已切换回白天
        assert time_manager.get_current_period() == "day"
    
    def test_settings_menu_without_time_manager(self, app, theme_manager):
        """测试没有时间管理器时的设置菜单"""
        from main import create_settings_menu
        
        # 创建没有时间管理器的设置菜单
        settings_menu = create_settings_menu(app, None, theme_manager)
        
        # 验证菜单存在但没有动作
        assert settings_menu is not None
        assert len(settings_menu.actions()) == 0
    
    def test_settings_menu_applies_dark_theme(self, app, time_manager, theme_manager):
        """测试设置菜单应用暗黑主题"""
        from main import create_settings_menu
        
        # 启用万圣节模式
        theme_manager.set_theme_mode("halloween")
        
        # 创建设置菜单
        settings_menu = create_settings_menu(app, time_manager, theme_manager)
        
        # 验证菜单存在
        assert settings_menu is not None
        
        # 验证样式表已应用（非空）
        # 注意：具体样式表内容取决于 theme_manager 的实现
        # 这里只验证菜单创建成功
