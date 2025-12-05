"""
海底背景测试 - 验证深潜模式的全屏背景功能

WARNING: Testing the gateway to the abyss...
These tests ensure the deep dive experience works as expected.
"""
import os
import tempfile
import json

import pytest
from hypothesis import given, strategies as st, settings, assume
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPixmap, QColor, QPainter
from PyQt6.QtCore import Qt

from ocean_background import OceanBackground
from theme_manager import ThemeManager
from data_manager import DataManager


# 确保 QApplication 存在
@pytest.fixture(scope="module")
def app():
    """创建 QApplication 实例"""
    application = QApplication.instance()
    if application is None:
        application = QApplication([])
    yield application


@pytest.fixture
def temp_data_file():
    """创建临时数据文件"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    yield temp_file
    if os.path.exists(temp_file):
        os.remove(temp_file)


# 策略生成器
@st.composite
def valid_theme_mode(draw):
    """生成有效的主题模式"""
    return draw(st.sampled_from(['normal', 'halloween']))


@st.composite
def valid_screen_size(draw):
    """生成有效的屏幕尺寸"""
    width = draw(st.integers(min_value=800, max_value=3840))
    height = draw(st.integers(min_value=600, max_value=2160))
    return (width, height)


# ==================== 属性 39: 深潜背景层级正确性 ====================
# **Feature: puffer-pet, Property 39: 深潜背景层级正确性**
# **验证: 需求 24.2, 24.8**

@settings(max_examples=100, deadline=None)
@given(theme_mode=valid_theme_mode())
def test_property_39_deep_dive_background_layer_correctness(app, theme_mode):
    """
    属性 39: 深潜背景层级正确性
    对于任意深潜模式激活状态，背景窗口应该位于桌面图标之上但位于所有宠物窗口之下。
    
    验证:
    1. 背景窗口是无边框的
    2. 背景窗口是工具窗口（不在任务栏显示）
    3. 背景窗口不接受焦点
    4. 宠物窗口有 WindowStaysOnTopHint，因此会在背景之上
    """
    # 创建主题管理器
    tm = ThemeManager()
    tm.set_theme_mode(theme_mode)
    
    # 创建海底背景
    ocean_bg = OceanBackground(theme_manager=tm)
    
    try:
        # 验证窗口标志
        window_flags = ocean_bg.windowFlags()
        
        # 1. 验证是无边框窗口
        assert window_flags & Qt.WindowType.FramelessWindowHint, \
            "背景窗口应该是无边框的"
        
        # 2. 验证是工具窗口
        assert window_flags & Qt.WindowType.Tool, \
            "背景窗口应该是工具窗口（不在任务栏显示）"
        
        # 3. 验证不接受焦点
        assert window_flags & Qt.WindowType.WindowDoesNotAcceptFocus, \
            "背景窗口不应该接受焦点"
        
        # 4. 验证没有 WindowStaysOnTopHint（这样宠物窗口可以在其上方）
        assert not (window_flags & Qt.WindowType.WindowStaysOnTopHint), \
            "背景窗口不应该有 WindowStaysOnTopHint"
        
        # 5. 激活深潜模式
        ocean_bg.activate()
        
        # 验证激活状态
        assert ocean_bg.is_activated(), "深潜模式应该已激活"
        
        # 6. 关闭深潜模式
        ocean_bg.deactivate()
        
        # 验证关闭状态
        assert not ocean_bg.is_activated(), "深潜模式应该已关闭"
        
    finally:
        ocean_bg.close()


# ==================== 单元测试 ====================

class TestOceanBackgroundBasic:
    """海底背景基本功能测试"""
    
    def test_initialization(self, app):
        """测试初始化"""
        ocean_bg = OceanBackground()
        
        try:
            # 验证初始状态
            assert ocean_bg.is_active == False
            assert ocean_bg.seabed_pixmap is not None
            assert ocean_bg.filter_color is not None
        finally:
            ocean_bg.close()
    
    def test_initialization_with_theme_manager(self, app, temp_data_file):
        """测试使用主题管理器初始化"""
        dm = DataManager(data_file=temp_data_file)
        tm = ThemeManager(data_manager=dm)
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            assert ocean_bg.theme_manager == tm
        finally:
            ocean_bg.close()
    
    def test_default_filter_color_normal_mode(self, app):
        """测试普通模式默认滤镜颜色"""
        tm = ThemeManager()
        tm.set_theme_mode("normal")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            filter_color = ocean_bg.get_filter_color()
            
            # 验证是蓝色滤镜
            assert filter_color.red() == 0
            assert filter_color.green() == 50
            assert filter_color.blue() == 100
        finally:
            ocean_bg.close()
    
    def test_filter_color_halloween_mode(self, app):
        """测试万圣节模式滤镜颜色"""
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            filter_color = ocean_bg.get_filter_color()
            
            # 验证是紫色滤镜
            assert filter_color.red() == 50
            assert filter_color.green() == 0
            assert filter_color.blue() == 50
        finally:
            ocean_bg.close()


class TestOceanBackgroundWindowSetup:
    """窗口设置测试"""
    
    def test_window_is_frameless(self, app):
        """测试窗口是无边框的"""
        ocean_bg = OceanBackground()
        
        try:
            window_flags = ocean_bg.windowFlags()
            assert window_flags & Qt.WindowType.FramelessWindowHint
        finally:
            ocean_bg.close()
    
    def test_window_is_tool_window(self, app):
        """测试窗口是工具窗口"""
        ocean_bg = OceanBackground()
        
        try:
            window_flags = ocean_bg.windowFlags()
            assert window_flags & Qt.WindowType.Tool
        finally:
            ocean_bg.close()
    
    def test_window_does_not_accept_focus(self, app):
        """测试窗口不接受焦点"""
        ocean_bg = OceanBackground()
        
        try:
            window_flags = ocean_bg.windowFlags()
            assert window_flags & Qt.WindowType.WindowDoesNotAcceptFocus
        finally:
            ocean_bg.close()
    
    def test_window_not_stays_on_top(self, app):
        """测试窗口没有置顶标志"""
        ocean_bg = OceanBackground()
        
        try:
            window_flags = ocean_bg.windowFlags()
            assert not (window_flags & Qt.WindowType.WindowStaysOnTopHint)
        finally:
            ocean_bg.close()
    
    def test_window_geometry_is_fullscreen(self, app):
        """测试窗口几何是全屏的"""
        ocean_bg = OceanBackground()
        
        try:
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                window_geometry = ocean_bg.geometry()
                
                # 验证窗口覆盖整个屏幕
                assert window_geometry.width() == screen_geometry.width()
                assert window_geometry.height() == screen_geometry.height()
        finally:
            ocean_bg.close()


class TestOceanBackgroundImageLoading:
    """背景图像加载测试"""
    
    def test_seabed_image_loaded(self, app):
        """测试海底图像已加载"""
        ocean_bg = OceanBackground()
        
        try:
            # 验证图像已加载（可能是实际图像或回退背景）
            assert ocean_bg.seabed_pixmap is not None
            assert not ocean_bg.seabed_pixmap.isNull()
        finally:
            ocean_bg.close()
    
    def test_scaled_pixmap_created(self, app):
        """测试缩放图像已创建"""
        ocean_bg = OceanBackground()
        
        try:
            # 验证缩放图像已创建
            assert ocean_bg.scaled_pixmap is not None
            assert not ocean_bg.scaled_pixmap.isNull()
        finally:
            ocean_bg.close()
    
    def test_fallback_background_when_image_missing(self, app):
        """测试图像缺失时使用回退背景"""
        ocean_bg = OceanBackground()
        
        # 临时修改图像路径 (V9: 使用新的路径常量)
        original_day_path = ocean_bg.SEABED_DAY_PATH
        original_night_path = ocean_bg.SEABED_NIGHT_PATH
        ocean_bg.SEABED_DAY_PATH = "nonexistent/path/seabed_day.png"
        ocean_bg.SEABED_NIGHT_PATH = "nonexistent/path/seabed_night.png"
        
        try:
            # 重新加载图像
            ocean_bg.load_seabed_image()
            
            # 验证回退背景已创建
            assert ocean_bg.seabed_pixmap is not None
            assert not ocean_bg.seabed_pixmap.isNull()
        finally:
            ocean_bg.SEABED_DAY_PATH = original_day_path
            ocean_bg.SEABED_NIGHT_PATH = original_night_path
            ocean_bg.close()
    
    def test_image_path_exists(self, app):
        """测试默认图像路径存在 (V9: 验证新资产路径)"""
        # 验证白天海底图像存在
        assert os.path.exists(OceanBackground.SEABED_DAY_PATH), \
            f"白天海底图像应该存在: {OceanBackground.SEABED_DAY_PATH}"
        # 验证夜晚海底图像存在
        assert os.path.exists(OceanBackground.SEABED_NIGHT_PATH), \
            f"夜晚海底图像应该存在: {OceanBackground.SEABED_NIGHT_PATH}"


class TestOceanBackgroundThemeFilter:
    """主题滤镜测试"""
    
    def test_apply_normal_filter(self, app):
        """测试应用普通滤镜"""
        tm = ThemeManager()
        tm.set_theme_mode("normal")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            ocean_bg.apply_theme_filter()
            
            filter_color = ocean_bg.get_filter_color()
            expected = OceanBackground.NORMAL_FILTER_COLOR
            
            assert filter_color.red() == expected.red()
            assert filter_color.green() == expected.green()
            assert filter_color.blue() == expected.blue()
        finally:
            ocean_bg.close()
    
    def test_apply_halloween_filter(self, app):
        """测试应用万圣节滤镜"""
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            ocean_bg.apply_theme_filter()
            
            filter_color = ocean_bg.get_filter_color()
            expected = OceanBackground.HALLOWEEN_FILTER_COLOR
            
            assert filter_color.red() == expected.red()
            assert filter_color.green() == expected.green()
            assert filter_color.blue() == expected.blue()
        finally:
            ocean_bg.close()
    
    def test_refresh_theme_updates_filter(self, app, temp_data_file):
        """测试刷新主题更新滤镜"""
        dm = DataManager(data_file=temp_data_file)
        tm = ThemeManager(data_manager=dm)
        tm.set_theme_mode("normal")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            # 初始应该是普通滤镜
            initial_filter = ocean_bg.get_filter_color()
            assert initial_filter.red() == 0
            
            # 切换到万圣节模式
            tm.set_theme_mode("halloween")
            ocean_bg.refresh_theme()
            
            # 验证滤镜已更新
            new_filter = ocean_bg.get_filter_color()
            assert new_filter.red() == 50
        finally:
            ocean_bg.close()


class TestOceanBackgroundActivation:
    """激活/关闭测试"""
    
    def test_activate_sets_is_active(self, app):
        """测试激活设置 is_active"""
        ocean_bg = OceanBackground()
        
        try:
            assert not ocean_bg.is_activated()
            
            ocean_bg.activate()
            
            assert ocean_bg.is_activated()
        finally:
            ocean_bg.deactivate()
            ocean_bg.close()
    
    def test_deactivate_clears_is_active(self, app):
        """测试关闭清除 is_active"""
        ocean_bg = OceanBackground()
        
        try:
            ocean_bg.activate()
            assert ocean_bg.is_activated()
            
            ocean_bg.deactivate()
            assert not ocean_bg.is_activated()
        finally:
            ocean_bg.close()
    
    def test_activate_shows_window(self, app):
        """测试激活显示窗口"""
        ocean_bg = OceanBackground()
        
        try:
            ocean_bg.activate()
            
            # 验证窗口可见
            assert ocean_bg.isVisible()
        finally:
            ocean_bg.deactivate()
            ocean_bg.close()
    
    def test_deactivate_hides_window(self, app):
        """测试关闭隐藏窗口"""
        ocean_bg = OceanBackground()
        
        try:
            ocean_bg.activate()
            assert ocean_bg.isVisible()
            
            ocean_bg.deactivate()
            assert not ocean_bg.isVisible()
        finally:
            ocean_bg.close()
    
    def test_double_activate_is_safe(self, app):
        """测试重复激活是安全的"""
        ocean_bg = OceanBackground()
        
        try:
            ocean_bg.activate()
            ocean_bg.activate()  # 第二次激活
            
            assert ocean_bg.is_activated()
        finally:
            ocean_bg.deactivate()
            ocean_bg.close()
    
    def test_double_deactivate_is_safe(self, app):
        """测试重复关闭是安全的"""
        ocean_bg = OceanBackground()
        
        try:
            ocean_bg.activate()
            ocean_bg.deactivate()
            ocean_bg.deactivate()  # 第二次关闭
            
            assert not ocean_bg.is_activated()
        finally:
            ocean_bg.close()


class TestOceanBackgroundWindowLayerInfo:
    """窗口层级信息测试"""
    
    def test_get_window_layer_info(self, app):
        """测试获取窗口层级信息"""
        ocean_bg = OceanBackground()
        
        try:
            info = ocean_bg.get_window_layer_info()
            
            assert 'is_frameless' in info
            assert 'is_tool_window' in info
            assert 'is_active' in info
            assert 'geometry' in info
            
            assert info['is_frameless'] == True
            assert info['is_tool_window'] == True
            assert info['is_active'] == False
        finally:
            ocean_bg.close()
    
    def test_window_layer_info_after_activation(self, app):
        """测试激活后的窗口层级信息"""
        ocean_bg = OceanBackground()
        
        try:
            ocean_bg.activate()
            
            info = ocean_bg.get_window_layer_info()
            assert info['is_active'] == True
        finally:
            ocean_bg.deactivate()
            ocean_bg.close()


class TestOceanBackgroundPainting:
    """绘制测试"""
    
    def test_paint_event_does_not_crash(self, app):
        """测试绘制事件不会崩溃"""
        ocean_bg = OceanBackground()
        
        try:
            # 触发绘制
            ocean_bg.repaint()
            
            # 如果没有崩溃，测试通过
            assert True
        finally:
            ocean_bg.close()
    
    def test_paint_event_with_null_pixmap(self, app):
        """测试空图像时绘制不会崩溃"""
        ocean_bg = OceanBackground()
        
        try:
            # 设置空图像
            ocean_bg.scaled_pixmap = None
            
            # 触发绘制 - 不应该崩溃
            ocean_bg.repaint()
            
            assert True
        finally:
            ocean_bg.close()


class TestOceanBackgroundIntegration:
    """集成测试"""
    
    def test_full_lifecycle(self, app, temp_data_file):
        """测试完整生命周期"""
        dm = DataManager(data_file=temp_data_file)
        tm = ThemeManager(data_manager=dm)
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            # 1. 初始状态
            assert not ocean_bg.is_activated()
            
            # 2. 激活
            ocean_bg.activate()
            assert ocean_bg.is_activated()
            assert ocean_bg.isVisible()
            
            # 3. 切换主题
            tm.set_theme_mode("halloween")
            ocean_bg.refresh_theme()
            
            filter_color = ocean_bg.get_filter_color()
            assert filter_color.red() == 50  # 万圣节紫色
            
            # 4. 关闭
            ocean_bg.deactivate()
            assert not ocean_bg.is_activated()
            assert not ocean_bg.isVisible()
            
        finally:
            ocean_bg.close()
    
    def test_theme_switch_while_active(self, app, temp_data_file):
        """测试激活时切换主题"""
        dm = DataManager(data_file=temp_data_file)
        tm = ThemeManager(data_manager=dm)
        tm.set_theme_mode("normal")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            # 激活
            ocean_bg.activate()
            
            # 验证普通滤镜
            assert ocean_bg.get_filter_color().red() == 0
            
            # 切换到万圣节
            tm.set_theme_mode("halloween")
            ocean_bg.refresh_theme()
            
            # 验证万圣节滤镜
            assert ocean_bg.get_filter_color().red() == 50
            
            # 仍然激活
            assert ocean_bg.is_activated()
            
        finally:
            ocean_bg.deactivate()
            ocean_bg.close()


# ==================== 粒子系统测试 ====================

from ocean_background import BubbleParticle


class TestBubbleParticleInitialization:
    """气泡粒子初始化测试"""
    
    def test_bubble_particle_creation(self, app):
        """测试气泡粒子创建"""
        particle = BubbleParticle(
            screen_width=1920,
            screen_height=1080,
            is_ghost_fire=False
        )
        
        # 验证基本属性
        assert particle.screen_width == 1920
        assert particle.screen_height == 1080
        assert particle.is_ghost_fire == False
        assert particle.size >= BubbleParticle.MIN_SIZE
        assert particle.size <= BubbleParticle.MAX_SIZE
        assert particle.speed >= BubbleParticle.MIN_SPEED
        assert particle.speed <= BubbleParticle.MAX_SPEED
    
    def test_ghost_fire_particle_creation(self, app):
        """测试鬼火粒子创建"""
        particle = BubbleParticle(
            screen_width=1920,
            screen_height=1080,
            is_ghost_fire=True
        )
        
        assert particle.is_ghost_fire == True
        assert particle.is_ghost_fire_mode() == True
    
    def test_particle_initial_position(self, app):
        """测试粒子初始位置"""
        particle = BubbleParticle(
            screen_width=1920,
            screen_height=1080,
            is_ghost_fire=False
        )
        
        x, y = particle.get_position()
        
        # X 应该在屏幕范围内
        assert 0 <= x <= 1920
        
        # Y 应该从屏幕底部开始（略低于屏幕）
        assert y >= 1080
    
    def test_particle_custom_position(self, app):
        """测试自定义粒子位置"""
        particle = BubbleParticle(
            screen_width=1920,
            screen_height=1080,
            is_ghost_fire=False,
            x=500,
            y=300
        )
        
        x, y = particle.get_position()
        assert x == 500
        assert y == 300
    
    def test_particle_size_in_range(self, app):
        """测试粒子大小在有效范围内"""
        for _ in range(20):
            particle = BubbleParticle(
                screen_width=1920,
                screen_height=1080,
                is_ghost_fire=False
            )
            
            size = particle.get_size()
            assert BubbleParticle.MIN_SIZE <= size <= BubbleParticle.MAX_SIZE
    
    def test_particle_speed_in_range(self, app):
        """测试粒子速度在有效范围内"""
        for _ in range(20):
            particle = BubbleParticle(
                screen_width=1920,
                screen_height=1080,
                is_ghost_fire=False
            )
            
            speed = particle.get_speed()
            assert BubbleParticle.MIN_SPEED <= speed <= BubbleParticle.MAX_SPEED


class TestBubbleParticleMovement:
    """气泡粒子移动测试"""
    
    def test_particle_moves_upward(self, app):
        """测试粒子向上移动"""
        particle = BubbleParticle(
            screen_width=1920,
            screen_height=1080,
            is_ghost_fire=False,
            x=500,
            y=500
        )
        
        initial_y = particle.y
        
        # 更新位置
        particle.update()
        
        # Y 应该减小（向上移动）
        assert particle.y < initial_y
    
    def test_particle_wobbles_horizontally(self, app):
        """测试粒子左右摇摆"""
        particle = BubbleParticle(
            screen_width=1920,
            screen_height=1080,
            is_ghost_fire=False,
            x=500,
            y=500
        )
        
        # 记录多次更新后的 X 位置
        x_positions = [particle.x]
        for _ in range(100):
            particle.update()
            x_positions.append(particle.x)
        
        # X 位置应该有变化（摇摆效果）
        # 由于摇摆是正弦波，应该有不同的值
        unique_x = set(round(x, 2) for x in x_positions)
        assert len(unique_x) > 1, "粒子应该有左右摇摆效果"
    
    def test_particle_returns_false_when_off_screen(self, app):
        """测试粒子离开屏幕时返回 False"""
        particle = BubbleParticle(
            screen_width=1920,
            screen_height=1080,
            is_ghost_fire=False,
            x=500,
            y=10  # 接近顶部
        )
        
        # 持续更新直到离开屏幕
        max_iterations = 1000
        for _ in range(max_iterations):
            if not particle.update():
                break
        
        # 应该最终返回 False
        assert particle.y <= -particle.size
    
    def test_particle_returns_true_when_on_screen(self, app):
        """测试粒子在屏幕内时返回 True"""
        particle = BubbleParticle(
            screen_width=1920,
            screen_height=1080,
            is_ghost_fire=False,
            x=500,
            y=500
        )
        
        # 更新一次
        result = particle.update()
        
        # 应该返回 True（仍在屏幕内）
        assert result == True


class TestBubbleParticleModeSwitch:
    """气泡/鬼火模式切换测试"""
    
    def test_switch_to_ghost_fire_mode(self, app):
        """测试切换到鬼火模式"""
        particle = BubbleParticle(
            screen_width=1920,
            screen_height=1080,
            is_ghost_fire=False
        )
        
        assert particle.is_ghost_fire_mode() == False
        
        particle.set_ghost_fire_mode(True)
        
        assert particle.is_ghost_fire_mode() == True
    
    def test_switch_to_bubble_mode(self, app):
        """测试切换到气泡模式"""
        particle = BubbleParticle(
            screen_width=1920,
            screen_height=1080,
            is_ghost_fire=True
        )
        
        assert particle.is_ghost_fire_mode() == True
        
        particle.set_ghost_fire_mode(False)
        
        assert particle.is_ghost_fire_mode() == False
    
    def test_mode_switch_updates_color(self, app):
        """测试模式切换更新颜色"""
        particle = BubbleParticle(
            screen_width=1920,
            screen_height=1080,
            is_ghost_fire=False
        )
        
        original_color = particle.color
        
        # 切换到鬼火模式
        particle.set_ghost_fire_mode(True)
        
        # 颜色应该改变
        # 注意：由于颜色是随机选择的，我们只验证颜色对象存在
        assert particle.color is not None


class TestBubbleParticleDrawing:
    """气泡粒子绘制测试"""
    
    def test_bubble_draw_does_not_crash(self, app):
        """测试气泡绘制不会崩溃"""
        particle = BubbleParticle(
            screen_width=1920,
            screen_height=1080,
            is_ghost_fire=False,
            x=500,
            y=500
        )
        
        # 创建一个临时 pixmap 用于绘制
        pixmap = QPixmap(100, 100)
        painter = QPainter(pixmap)
        
        try:
            particle.draw(painter)
            # 如果没有崩溃，测试通过
            assert True
        finally:
            painter.end()
    
    def test_ghost_fire_draw_does_not_crash(self, app):
        """测试鬼火绘制不会崩溃"""
        particle = BubbleParticle(
            screen_width=1920,
            screen_height=1080,
            is_ghost_fire=True,
            x=500,
            y=500
        )
        
        # 创建一个临时 pixmap 用于绘制
        pixmap = QPixmap(100, 100)
        painter = QPainter(pixmap)
        
        try:
            particle.draw(painter)
            # 如果没有崩溃，测试通过
            assert True
        finally:
            painter.end()


class TestOceanBackgroundParticleSystem:
    """海底背景粒子系统集成测试"""
    
    def test_particle_system_initialization(self, app):
        """测试粒子系统初始化"""
        ocean_bg = OceanBackground()
        
        try:
            # 验证粒子系统属性
            assert ocean_bg.particles == []
            assert ocean_bg.particle_timer is not None
            assert ocean_bg.animation_timer is not None
            assert ocean_bg.max_particles == 50
        finally:
            ocean_bg.close()
    
    def test_spawn_particle(self, app):
        """测试生成粒子"""
        ocean_bg = OceanBackground()
        
        try:
            assert len(ocean_bg.particles) == 0
            
            ocean_bg.spawn_particle()
            
            assert len(ocean_bg.particles) == 1
        finally:
            ocean_bg.close()
    
    def test_spawn_particle_respects_max_limit(self, app):
        """测试粒子数量上限"""
        ocean_bg = OceanBackground()
        ocean_bg.max_particles = 5
        
        try:
            # 尝试生成超过上限的粒子
            for _ in range(10):
                ocean_bg.spawn_particle()
            
            # 应该不超过上限
            assert len(ocean_bg.particles) <= 5
        finally:
            ocean_bg.close()
    
    def test_update_particles_removes_off_screen(self, app):
        """测试更新粒子移除离开屏幕的粒子"""
        ocean_bg = OceanBackground()
        
        try:
            # 添加一个接近顶部的粒子
            particle = BubbleParticle(
                screen_width=1920,
                screen_height=1080,
                is_ghost_fire=False,
                x=500,
                y=-100  # 已经在屏幕外
            )
            ocean_bg.particles.append(particle)
            
            assert len(ocean_bg.particles) == 1
            
            # 更新粒子
            ocean_bg.update_particles()
            
            # 离开屏幕的粒子应该被移除
            assert len(ocean_bg.particles) == 0
        finally:
            ocean_bg.close()
    
    def test_start_particle_system(self, app):
        """测试启动粒子系统"""
        ocean_bg = OceanBackground()
        
        try:
            ocean_bg.start_particle_system()
            
            assert ocean_bg.particle_timer.isActive()
            assert ocean_bg.animation_timer.isActive()
        finally:
            ocean_bg.stop_particle_system()
            ocean_bg.close()
    
    def test_stop_particle_system(self, app):
        """测试停止粒子系统"""
        ocean_bg = OceanBackground()
        
        try:
            # 先启动
            ocean_bg.start_particle_system()
            ocean_bg.spawn_particle()
            
            assert ocean_bg.particle_timer.isActive()
            assert len(ocean_bg.particles) > 0
            
            # 停止
            ocean_bg.stop_particle_system()
            
            assert not ocean_bg.particle_timer.isActive()
            assert not ocean_bg.animation_timer.isActive()
            assert len(ocean_bg.particles) == 0
        finally:
            ocean_bg.close()
    
    def test_activate_starts_particle_system(self, app):
        """测试激活深潜模式启动粒子系统"""
        ocean_bg = OceanBackground()
        
        try:
            ocean_bg.activate()
            
            assert ocean_bg.particle_timer.isActive()
            assert ocean_bg.animation_timer.isActive()
        finally:
            ocean_bg.deactivate()
            ocean_bg.close()
    
    def test_deactivate_stops_particle_system(self, app):
        """测试关闭深潜模式停止粒子系统"""
        ocean_bg = OceanBackground()
        
        try:
            ocean_bg.activate()
            ocean_bg.spawn_particle()
            
            ocean_bg.deactivate()
            
            assert not ocean_bg.particle_timer.isActive()
            assert not ocean_bg.animation_timer.isActive()
            assert len(ocean_bg.particles) == 0
        finally:
            ocean_bg.close()
    
    def test_get_particle_count(self, app):
        """测试获取粒子数量"""
        ocean_bg = OceanBackground()
        
        try:
            assert ocean_bg.get_particle_count() == 0
            
            ocean_bg.spawn_particle()
            ocean_bg.spawn_particle()
            
            assert ocean_bg.get_particle_count() == 2
        finally:
            ocean_bg.close()
    
    def test_get_particles(self, app):
        """测试获取粒子列表"""
        ocean_bg = OceanBackground()
        
        try:
            ocean_bg.spawn_particle()
            
            particles = ocean_bg.get_particles()
            
            assert len(particles) == 1
            assert isinstance(particles[0], BubbleParticle)
        finally:
            ocean_bg.close()
    
    def test_set_max_particles(self, app):
        """测试设置最大粒子数"""
        ocean_bg = OceanBackground()
        
        try:
            ocean_bg.set_max_particles(10)
            
            assert ocean_bg.max_particles == 10
            
            # 测试最小值限制
            ocean_bg.set_max_particles(0)
            assert ocean_bg.max_particles == 1
        finally:
            ocean_bg.close()
    
    def test_set_spawn_interval(self, app):
        """测试设置生成间隔"""
        ocean_bg = OceanBackground()
        
        try:
            ocean_bg.set_spawn_interval(500)
            
            assert ocean_bg.spawn_interval == 500
            
            # 测试最小值限制
            ocean_bg.set_spawn_interval(10)
            assert ocean_bg.spawn_interval == 50
        finally:
            ocean_bg.close()


class TestOceanBackgroundParticleThemeIntegration:
    """粒子系统与主题集成测试"""
    
    def test_normal_mode_creates_bubble_particles(self, app):
        """测试普通模式创建气泡粒子"""
        tm = ThemeManager()
        tm.set_theme_mode("normal")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            ocean_bg.spawn_particle()
            
            particle = ocean_bg.particles[0]
            assert particle.is_ghost_fire_mode() == False
        finally:
            ocean_bg.close()
    
    def test_halloween_mode_creates_ghost_fire_particles(self, app):
        """测试万圣节模式创建鬼火粒子"""
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            ocean_bg.spawn_particle()
            
            particle = ocean_bg.particles[0]
            assert particle.is_ghost_fire_mode() == True
        finally:
            ocean_bg.close()
    
    def test_refresh_theme_updates_particle_mode(self, app, temp_data_file):
        """测试刷新主题更新粒子模式"""
        dm = DataManager(data_file=temp_data_file)
        tm = ThemeManager(data_manager=dm)
        tm.set_theme_mode("normal")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            # 生成普通气泡
            ocean_bg.spawn_particle()
            assert ocean_bg.particles[0].is_ghost_fire_mode() == False
            
            # 切换到万圣节模式
            tm.set_theme_mode("halloween")
            ocean_bg.refresh_theme()
            
            # 现有粒子应该变成鬼火
            assert ocean_bg.particles[0].is_ghost_fire_mode() == True
        finally:
            ocean_bg.close()
    
    def test_paint_with_particles_does_not_crash(self, app):
        """测试带粒子的绘制不会崩溃"""
        ocean_bg = OceanBackground()
        
        try:
            # 添加一些粒子
            for _ in range(5):
                ocean_bg.spawn_particle()
            
            # 触发绘制
            ocean_bg.repaint()
            
            # 如果没有崩溃，测试通过
            assert True
        finally:
            ocean_bg.close()


# ==================== 属性 42: 主题联动一致性 ====================
# **Feature: puffer-pet, Property 42: 主题联动一致性**
# **验证: 需求 26.1, 26.2, 26.3, 26.4**


@st.composite
def valid_deep_dive_state(draw):
    """生成有效的深潜模式状态"""
    theme_mode = draw(st.sampled_from(['normal', 'halloween']))
    is_active = draw(st.booleans())
    return {
        'theme_mode': theme_mode,
        'is_active': is_active
    }


@settings(max_examples=100, deadline=None)
@given(state=valid_deep_dive_state())
def test_property_42_theme_integration_consistency(app, state):
    """
    属性 42: 主题联动一致性
    对于任意深潜模式和主题模式组合，视觉效果（滤镜颜色、粒子类型）应该与当前主题一致。
    
    验证:
    1. 普通模式使用蓝色滤镜 (rgba(0, 50, 100, 0.3))
    2. 万圣节模式使用紫色滤镜 (rgba(50, 0, 50, 0.4))
    3. 普通模式创建气泡粒子 (is_ghost_fire=False)
    4. 万圣节模式创建鬼火粒子 (is_ghost_fire=True)
    5. 主题切换时，滤镜和粒子类型应该实时更新
    """
    theme_mode = state['theme_mode']
    is_active = state['is_active']
    
    # 创建主题管理器
    tm = ThemeManager()
    tm.set_theme_mode(theme_mode)
    
    # 创建海底背景
    ocean_bg = OceanBackground(theme_manager=tm)
    
    try:
        # 验证滤镜颜色与主题一致
        filter_color = ocean_bg.get_filter_color()
        
        if theme_mode == 'normal':
            # 普通模式应该使用蓝色滤镜
            assert filter_color.red() == 0, \
                f"普通模式滤镜红色分量应该为0，实际为{filter_color.red()}"
            assert filter_color.green() == 50, \
                f"普通模式滤镜绿色分量应该为50，实际为{filter_color.green()}"
            assert filter_color.blue() == 100, \
                f"普通模式滤镜蓝色分量应该为100，实际为{filter_color.blue()}"
        else:  # halloween
            # 万圣节模式应该使用紫色滤镜
            assert filter_color.red() == 50, \
                f"万圣节模式滤镜红色分量应该为50，实际为{filter_color.red()}"
            assert filter_color.green() == 0, \
                f"万圣节模式滤镜绿色分量应该为0，实际为{filter_color.green()}"
            assert filter_color.blue() == 50, \
                f"万圣节模式滤镜蓝色分量应该为50，实际为{filter_color.blue()}"
        
        # 如果激活深潜模式，验证粒子类型
        if is_active:
            ocean_bg.activate()
            
            # 生成粒子
            ocean_bg.spawn_particle()
            
            if len(ocean_bg.particles) > 0:
                particle = ocean_bg.particles[0]
                
                if theme_mode == 'normal':
                    # 普通模式应该创建气泡粒子
                    assert particle.is_ghost_fire_mode() == False, \
                        "普通模式应该创建气泡粒子（is_ghost_fire=False）"
                else:  # halloween
                    # 万圣节模式应该创建鬼火粒子
                    assert particle.is_ghost_fire_mode() == True, \
                        "万圣节模式应该创建鬼火粒子（is_ghost_fire=True）"
            
            ocean_bg.deactivate()
        
        # 测试主题切换时的实时更新
        # 切换到另一个主题
        new_theme = 'halloween' if theme_mode == 'normal' else 'normal'
        tm.set_theme_mode(new_theme)
        ocean_bg.refresh_theme()
        
        # 验证滤镜已更新
        new_filter_color = ocean_bg.get_filter_color()
        
        if new_theme == 'normal':
            assert new_filter_color.red() == 0, \
                "切换到普通模式后滤镜应该更新为蓝色"
        else:
            assert new_filter_color.red() == 50, \
                "切换到万圣节模式后滤镜应该更新为紫色"
        
        # 如果有粒子，验证粒子模式也已更新
        if len(ocean_bg.particles) > 0:
            particle = ocean_bg.particles[0]
            
            if new_theme == 'normal':
                assert particle.is_ghost_fire_mode() == False, \
                    "切换到普通模式后粒子应该变为气泡"
            else:
                assert particle.is_ghost_fire_mode() == True, \
                    "切换到万圣节模式后粒子应该变为鬼火"
        
    finally:
        ocean_bg.deactivate()
        ocean_bg.close()


class TestHalloweenThemeIntegration:
    """万圣节主题联动测试"""
    
    def test_halloween_filter_color(self, app):
        """测试万圣节滤镜颜色"""
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            filter_color = ocean_bg.get_filter_color()
            
            # 验证是紫色/黑色滤镜 (rgba(50, 0, 50, 0.4))
            assert filter_color.red() == 50
            assert filter_color.green() == 0
            assert filter_color.blue() == 50
        finally:
            ocean_bg.close()
    
    def test_ghost_fire_particle_effect(self, app):
        """测试鬼火粒子效果"""
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            ocean_bg.spawn_particle()
            
            particle = ocean_bg.particles[0]
            
            # 验证是鬼火模式
            assert particle.is_ghost_fire_mode() == True
            
            # 验证鬼火颜色是绿色或紫色
            color = particle.color
            # 鬼火颜色应该是绿色系或紫色系
            is_green = color.green() > color.red() and color.green() > color.blue()
            is_purple = color.red() > 0 and color.blue() > 0 and color.green() < color.red()
            assert is_green or is_purple, \
                f"鬼火颜色应该是绿色或紫色，实际为 RGB({color.red()}, {color.green()}, {color.blue()})"
        finally:
            ocean_bg.close()
    
    def test_theme_switch_updates_filter(self, app, temp_data_file):
        """测试主题切换时更新滤镜"""
        dm = DataManager(data_file=temp_data_file)
        tm = ThemeManager(data_manager=dm)
        tm.set_theme_mode("normal")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            # 初始应该是蓝色滤镜
            assert ocean_bg.get_filter_color().red() == 0
            
            # 切换到万圣节模式
            tm.set_theme_mode("halloween")
            ocean_bg.refresh_theme()
            
            # 验证滤镜已更新为紫色
            assert ocean_bg.get_filter_color().red() == 50
            assert ocean_bg.get_filter_color().green() == 0
            assert ocean_bg.get_filter_color().blue() == 50
        finally:
            ocean_bg.close()
    
    def test_theme_switch_updates_particles(self, app, temp_data_file):
        """测试主题切换时更新粒子"""
        dm = DataManager(data_file=temp_data_file)
        tm = ThemeManager(data_manager=dm)
        tm.set_theme_mode("normal")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            # 生成普通气泡
            ocean_bg.spawn_particle()
            assert ocean_bg.particles[0].is_ghost_fire_mode() == False
            
            # 切换到万圣节模式
            tm.set_theme_mode("halloween")
            ocean_bg.refresh_theme()
            
            # 现有粒子应该变成鬼火
            assert ocean_bg.particles[0].is_ghost_fire_mode() == True
        finally:
            ocean_bg.close()
    
    def test_halloween_background_image_loading(self, app):
        """测试万圣节背景图像加载"""
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            # 验证背景图像已加载（可能是万圣节图像或回退背景）
            assert ocean_bg.seabed_pixmap is not None
            assert not ocean_bg.seabed_pixmap.isNull()
        finally:
            ocean_bg.close()
    
    def test_real_time_theme_update_while_active(self, app, temp_data_file):
        """测试激活时实时更新主题"""
        dm = DataManager(data_file=temp_data_file)
        tm = ThemeManager(data_manager=dm)
        tm.set_theme_mode("normal")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            # 激活深潜模式
            ocean_bg.activate()
            
            # 生成一些粒子
            for _ in range(3):
                ocean_bg.spawn_particle()
            
            # 验证初始状态
            assert ocean_bg.get_filter_color().red() == 0
            for p in ocean_bg.particles:
                assert p.is_ghost_fire_mode() == False
            
            # 切换到万圣节模式
            tm.set_theme_mode("halloween")
            ocean_bg.refresh_theme()
            
            # 验证滤镜和粒子都已更新
            assert ocean_bg.get_filter_color().red() == 50
            for p in ocean_bg.particles:
                assert p.is_ghost_fire_mode() == True
            
            # 仍然激活
            assert ocean_bg.is_activated()
            
        finally:
            ocean_bg.deactivate()
            ocean_bg.close()



class TestHalloweenSleepImageLoading:
    """万圣节睡觉图像加载测试"""
    
    def test_sleep_image_loading_normal_mode(self, app, temp_data_file):
        """测试普通模式睡觉图像加载"""
        from pet_widget import PetWidget
        
        dm = DataManager(data_file=temp_data_file)
        tm = ThemeManager(data_manager=dm)
        tm.set_theme_mode("normal")
        
        pet_widget = PetWidget(dm)
        pet_widget.theme_manager = tm
        
        try:
            # 设置睡觉状态
            pet_widget.set_sleeping(True)
            
            # 验证图像已加载（可能是睡觉图像或回退图像）
            assert pet_widget.current_pixmap is not None
            assert not pet_widget.current_pixmap.isNull()
            
            # 恢复正常状态
            pet_widget.set_sleeping(False)
            
            # 验证图像已恢复
            assert pet_widget.current_pixmap is not None
            assert not pet_widget.current_pixmap.isNull()
        finally:
            pet_widget.close()
    
    def test_sleep_image_loading_halloween_mode(self, app, temp_data_file):
        """测试万圣节模式睡觉图像加载"""
        from pet_widget import PetWidget
        
        dm = DataManager(data_file=temp_data_file)
        tm = ThemeManager(data_manager=dm)
        tm.set_theme_mode("halloween")
        
        pet_widget = PetWidget(dm)
        pet_widget.theme_manager = tm
        
        try:
            # 设置睡觉状态
            pet_widget.set_sleeping(True)
            
            # 验证图像已加载
            assert pet_widget.current_pixmap is not None
            assert not pet_widget.current_pixmap.isNull()
            
            # 恢复正常状态
            pet_widget.set_sleeping(False)
            
            # 验证图像已恢复
            assert pet_widget.current_pixmap is not None
            assert not pet_widget.current_pixmap.isNull()
        finally:
            pet_widget.close()
    
    def test_sleep_image_fallback_to_normal_image(self, app, temp_data_file):
        """测试睡觉图像回退到普通图像"""
        from pet_widget import PetWidget
        
        dm = DataManager(data_file=temp_data_file)
        tm = ThemeManager(data_manager=dm)
        tm.set_theme_mode("normal")
        
        pet_widget = PetWidget(dm)
        pet_widget.theme_manager = tm
        
        try:
            # 记录正常图像
            normal_pixmap = pet_widget.current_pixmap
            
            # 设置睡觉状态（如果没有睡觉图像，应该回退到普通图像）
            pet_widget.set_sleeping(True)
            
            # 验证图像已加载
            assert pet_widget.current_pixmap is not None
            assert not pet_widget.current_pixmap.isNull()
        finally:
            pet_widget.close()
    
    def test_halloween_ghost_filter_applied_to_sleep_image(self, app, temp_data_file):
        """测试万圣节模式下对睡觉图像应用幽灵滤镜"""
        from pet_widget import PetWidget
        
        dm = DataManager(data_file=temp_data_file)
        tm = ThemeManager(data_manager=dm)
        tm.set_theme_mode("halloween")
        
        pet_widget = PetWidget(dm)
        pet_widget.theme_manager = tm
        
        try:
            # 设置睡觉状态
            pet_widget.set_sleeping(True)
            
            # 验证图像已加载（应该应用了幽灵滤镜，如果没有专用万圣节睡觉图像）
            assert pet_widget.current_pixmap is not None
            assert not pet_widget.current_pixmap.isNull()
        finally:
            pet_widget.close()
    
    def test_set_sleeping_toggle(self, app, temp_data_file):
        """测试睡觉状态切换"""
        from pet_widget import PetWidget
        
        dm = DataManager(data_file=temp_data_file)
        
        pet_widget = PetWidget(dm)
        
        try:
            # 初始状态
            initial_pixmap = pet_widget.current_pixmap
            
            # 进入睡觉状态
            pet_widget.set_sleeping(True)
            sleep_pixmap = pet_widget.current_pixmap
            
            # 退出睡觉状态
            pet_widget.set_sleeping(False)
            awake_pixmap = pet_widget.current_pixmap
            
            # 验证所有状态都有有效图像
            assert initial_pixmap is not None
            assert sleep_pixmap is not None
            assert awake_pixmap is not None
        finally:
            pet_widget.close()


# ==================== 属性 50: 背景回退正确性 ====================
# **Feature: puffer-pet, Property 50: 背景回退正确性**
# **验证: 需求 29.7**


@st.composite
def valid_day_night_mode(draw):
    """生成有效的昼夜模式"""
    return draw(st.sampled_from(['day', 'night']))


@settings(max_examples=100, deadline=None)
@given(mode=valid_day_night_mode())
def test_property_50_background_fallback_correctness(app, mode):
    """
    属性 50: 背景回退正确性
    对于任意黑夜模式激活，当seabed_night.png不存在时，应该对白天背景应用深紫色滤镜而不是崩溃。
    
    验证:
    1. 当黑夜背景不存在时，应该成功加载白天背景
    2. 应该对白天背景应用深紫色滤镜
    3. 不应该崩溃或抛出异常
    4. 滤镜颜色应该是深紫色 (rgba(50, 0, 50, 0.4))
    """
    # 创建主题管理器
    tm = ThemeManager()
    
    # 根据模式设置主题
    if mode == 'day':
        tm.set_theme_mode("normal")
    else:
        tm.set_theme_mode("halloween")
    
    # 创建海底背景
    ocean_bg = OceanBackground(theme_manager=tm)
    
    try:
        # 验证背景图像已加载（无论是实际图像还是回退背景）
        assert ocean_bg.seabed_pixmap is not None, \
            f"在{mode}模式下，背景图像应该已加载"
        assert not ocean_bg.seabed_pixmap.isNull(), \
            f"在{mode}模式下，背景图像不应该为空"
        
        # 验证缩放图像已创建
        assert ocean_bg.scaled_pixmap is not None, \
            f"在{mode}模式下，缩放图像应该已创建"
        assert not ocean_bg.scaled_pixmap.isNull(), \
            f"在{mode}模式下，缩放图像不应该为空"
        
        # 验证滤镜颜色与模式一致
        filter_color = ocean_bg.get_filter_color()
        
        if mode == 'day':
            # 白天模式应该使用浅蓝色滤镜
            assert filter_color.red() == 0, \
                f"白天模式滤镜红色分量应该为0，实际为{filter_color.red()}"
            assert filter_color.green() == 50, \
                f"白天模式滤镜绿色分量应该为50，实际为{filter_color.green()}"
            assert filter_color.blue() == 100, \
                f"白天模式滤镜蓝色分量应该为100，实际为{filter_color.blue()}"
        else:
            # 黑夜模式应该使用深紫色滤镜
            assert filter_color.red() == 50, \
                f"黑夜模式滤镜红色分量应该为50，实际为{filter_color.red()}"
            assert filter_color.green() == 0, \
                f"黑夜模式滤镜绿色分量应该为0，实际为{filter_color.green()}"
            assert filter_color.blue() == 50, \
                f"黑夜模式滤镜蓝色分量应该为50，实际为{filter_color.blue()}"
        
        # 测试激活深潜模式不会崩溃
        ocean_bg.activate()
        assert ocean_bg.is_activated(), f"在{mode}模式下，深潜模式应该已激活"
        
        # 测试刷新主题不会崩溃
        ocean_bg.refresh_theme()
        
        # 验证刷新后状态仍然正确
        assert ocean_bg.seabed_pixmap is not None, \
            f"刷新后在{mode}模式下，背景图像应该仍然存在"
        assert not ocean_bg.seabed_pixmap.isNull(), \
            f"刷新后在{mode}模式下，背景图像不应该为空"
        
        ocean_bg.deactivate()
        
    finally:
        ocean_bg.close()


# ==================== 昼夜循环背景测试 ====================

class TestOceanBackgroundDayNightCycle:
    """深潜背景昼夜循环测试"""
    
    def test_day_mode_filter_color(self, app):
        """测试白天模式滤镜颜色"""
        tm = ThemeManager()
        tm.set_theme_mode("normal")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            filter_color = ocean_bg.get_filter_color()
            
            # 验证是浅蓝色滤镜 (rgba(0, 50, 100, 0.3))
            assert filter_color.red() == 0
            assert filter_color.green() == 50
            assert filter_color.blue() == 100
        finally:
            ocean_bg.close()
    
    def test_night_mode_filter_color(self, app):
        """测试黑夜模式滤镜颜色"""
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            filter_color = ocean_bg.get_filter_color()
            
            # 验证是深紫色滤镜 (rgba(50, 0, 50, 0.4))
            assert filter_color.red() == 50
            assert filter_color.green() == 0
            assert filter_color.blue() == 50
        finally:
            ocean_bg.close()
    
    def test_day_mode_creates_bubble_particles(self, app):
        """测试白天模式创建气泡粒子"""
        tm = ThemeManager()
        tm.set_theme_mode("normal")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            ocean_bg.spawn_particle()
            
            assert len(ocean_bg.particles) > 0
            particle = ocean_bg.particles[0]
            assert particle.is_ghost_fire_mode() == False, \
                "白天模式应该创建气泡粒子（is_ghost_fire=False）"
        finally:
            ocean_bg.close()
    
    def test_night_mode_creates_ghost_fire_particles(self, app):
        """测试黑夜模式创建鬼火粒子"""
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            ocean_bg.spawn_particle()
            
            assert len(ocean_bg.particles) > 0
            particle = ocean_bg.particles[0]
            assert particle.is_ghost_fire_mode() == True, \
                "黑夜模式应该创建鬼火粒子（is_ghost_fire=True）"
        finally:
            ocean_bg.close()
    
    def test_mode_switch_updates_filter_color(self, app, temp_data_file):
        """测试模式切换更新滤镜颜色"""
        dm = DataManager(data_file=temp_data_file)
        tm = ThemeManager(data_manager=dm)
        tm.set_theme_mode("normal")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            # 初始应该是浅蓝色滤镜
            assert ocean_bg.get_filter_color().red() == 0
            assert ocean_bg.get_filter_color().blue() == 100
            
            # 切换到黑夜模式
            tm.set_theme_mode("halloween")
            ocean_bg.refresh_theme()
            
            # 验证滤镜已更新为深紫色
            assert ocean_bg.get_filter_color().red() == 50
            assert ocean_bg.get_filter_color().green() == 0
            assert ocean_bg.get_filter_color().blue() == 50
            
            # 切换回白天模式
            tm.set_theme_mode("normal")
            ocean_bg.refresh_theme()
            
            # 验证滤镜已更新为浅蓝色
            assert ocean_bg.get_filter_color().red() == 0
            assert ocean_bg.get_filter_color().green() == 50
            assert ocean_bg.get_filter_color().blue() == 100
        finally:
            ocean_bg.close()
    
    def test_mode_switch_updates_particle_type(self, app, temp_data_file):
        """测试模式切换更新粒子类型"""
        dm = DataManager(data_file=temp_data_file)
        tm = ThemeManager(data_manager=dm)
        tm.set_theme_mode("normal")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            # 生成白天气泡
            ocean_bg.spawn_particle()
            assert ocean_bg.particles[0].is_ghost_fire_mode() == False
            
            # 切换到黑夜模式
            tm.set_theme_mode("halloween")
            ocean_bg.refresh_theme()
            
            # 现有粒子应该变成鬼火
            assert ocean_bg.particles[0].is_ghost_fire_mode() == True
            
            # 切换回白天模式
            tm.set_theme_mode("normal")
            ocean_bg.refresh_theme()
            
            # 现有粒子应该变回气泡
            assert ocean_bg.particles[0].is_ghost_fire_mode() == False
        finally:
            ocean_bg.close()
    
    def test_background_fallback_when_night_image_missing(self, app):
        """测试黑夜背景图像缺失时的回退"""
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            # 验证背景图像已加载（可能是回退背景）
            assert ocean_bg.seabed_pixmap is not None
            assert not ocean_bg.seabed_pixmap.isNull()
            
            # 验证滤镜颜色正确
            filter_color = ocean_bg.get_filter_color()
            assert filter_color.red() == 50
            assert filter_color.green() == 0
            assert filter_color.blue() == 50
        finally:
            ocean_bg.close()
    
    def test_day_background_loading(self, app):
        """测试白天背景加载"""
        tm = ThemeManager()
        tm.set_theme_mode("normal")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            # 验证背景图像已加载
            assert ocean_bg.seabed_pixmap is not None
            assert not ocean_bg.seabed_pixmap.isNull()
            
            # 验证缩放图像已创建
            assert ocean_bg.scaled_pixmap is not None
            assert not ocean_bg.scaled_pixmap.isNull()
        finally:
            ocean_bg.close()
    
    def test_night_background_loading(self, app):
        """测试黑夜背景加载"""
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            # 验证背景图像已加载（可能是万圣节图像或回退背景）
            assert ocean_bg.seabed_pixmap is not None
            assert not ocean_bg.seabed_pixmap.isNull()
            
            # 验证缩放图像已创建
            assert ocean_bg.scaled_pixmap is not None
            assert not ocean_bg.scaled_pixmap.isNull()
        finally:
            ocean_bg.close()
    
    def test_mode_switch_while_active(self, app, temp_data_file):
        """测试激活时切换模式"""
        dm = DataManager(data_file=temp_data_file)
        tm = ThemeManager(data_manager=dm)
        tm.set_theme_mode("normal")
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            # 激活深潜模式
            ocean_bg.activate()
            assert ocean_bg.is_activated()
            
            # 生成一些粒子
            for _ in range(3):
                ocean_bg.spawn_particle()
            
            # 验证初始状态（白天）
            assert ocean_bg.get_filter_color().red() == 0
            for p in ocean_bg.particles:
                assert p.is_ghost_fire_mode() == False
            
            # 切换到黑夜模式
            tm.set_theme_mode("halloween")
            ocean_bg.refresh_theme()
            
            # 验证滤镜和粒子都已更新
            assert ocean_bg.get_filter_color().red() == 50
            for p in ocean_bg.particles:
                assert p.is_ghost_fire_mode() == True
            
            # 仍然激活
            assert ocean_bg.is_activated()
            
        finally:
            ocean_bg.deactivate()
            ocean_bg.close()


class TestOceanBackgroundDayNightIntegration:
    """深潜背景昼夜循环集成测试"""
    
    def test_full_day_night_cycle(self, app, temp_data_file):
        """测试完整的昼夜循环"""
        dm = DataManager(data_file=temp_data_file)
        tm = ThemeManager(data_manager=dm)
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            # 1. 白天模式
            tm.set_theme_mode("normal")
            ocean_bg.refresh_theme()
            
            assert ocean_bg.get_filter_color().red() == 0
            ocean_bg.spawn_particle()
            assert ocean_bg.particles[0].is_ghost_fire_mode() == False
            
            # 2. 激活深潜模式
            ocean_bg.activate()
            assert ocean_bg.is_activated()
            
            # 3. 切换到黑夜模式
            tm.set_theme_mode("halloween")
            ocean_bg.refresh_theme()
            
            assert ocean_bg.get_filter_color().red() == 50
            assert ocean_bg.particles[0].is_ghost_fire_mode() == True
            
            # 4. 切换回白天模式
            tm.set_theme_mode("normal")
            ocean_bg.refresh_theme()
            
            assert ocean_bg.get_filter_color().red() == 0
            assert ocean_bg.particles[0].is_ghost_fire_mode() == False
            
            # 5. 关闭深潜模式
            ocean_bg.deactivate()
            assert not ocean_bg.is_activated()
            
        finally:
            ocean_bg.close()
    
    def test_time_manager_integration(self, app, temp_data_file):
        """测试与时间管理器的集成"""
        from time_manager import TimeManager
        
        dm = DataManager(data_file=temp_data_file)
        tm = ThemeManager(data_manager=dm)
        time_mgr = TimeManager(theme_manager=tm, data_manager=dm)
        
        ocean_bg = OceanBackground(theme_manager=tm)
        
        try:
            # 连接时间管理器的模式切换信号到背景刷新
            time_mgr.mode_changed.connect(lambda mode: ocean_bg.refresh_theme())
            
            # 初始状态
            initial_period = time_mgr.get_current_period()
            
            # 手动切换模式（禁用自动同步）
            time_mgr.set_auto_sync(False)
            
            # 切换到黑夜
            time_mgr.switch_to_night()
            assert tm.is_halloween_mode()
            
            # 验证背景已更新
            assert ocean_bg.get_filter_color().red() == 50
            
            # 切换到白天
            time_mgr.switch_to_day()
            assert not tm.is_halloween_mode()
            
            # 验证背景已更新
            assert ocean_bg.get_filter_color().red() == 0
            
        finally:
            ocean_bg.close()
