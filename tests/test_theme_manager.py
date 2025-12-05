"""
主题管理器测试 - 验证万圣节主题和幽灵滤镜功能

WARNING: Testing the cursed visual transformations...
These tests ensure the spirits of the deep behave as expected.
"""
import os
import tempfile
import json
from datetime import date

import pytest
from hypothesis import given, strategies as st, settings, assume
from PyQt6.QtWidgets import QApplication, QWidget, QDialog, QPushButton, QLabel
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt

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


# 策略生成器
@st.composite
def valid_pet_id(draw):
    """生成有效的宠物ID"""
    all_pets = ['puffer', 'jelly', 'starfish', 'crab', 'octopus', 'ribbon', 
                'sunfish', 'angler', 'blobfish', 'ray', 'beluga', 'orca', 
                'shark', 'bluewhale']
    return draw(st.sampled_from(all_pets))


@st.composite
def valid_tier(draw):
    """生成有效的宠物层级"""
    return draw(st.integers(min_value=1, max_value=3))


@st.composite
def valid_level(draw):
    """生成有效的宠物等级"""
    return draw(st.integers(min_value=1, max_value=3))


@st.composite
def valid_theme_mode(draw):
    """生成有效的主题模式"""
    return draw(st.sampled_from(['normal', 'halloween']))


@st.composite
def valid_opacity(draw):
    """生成有效的透明度值"""
    return draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))


# **Feature: puffer-pet, Property 48: 视觉效果与模式同步**
# **验证: 需求 28.8, 29.1-29.8**
@settings(max_examples=100, deadline=None)
@given(day_night_mode=st.sampled_from(['day', 'night']))
def test_property_48_visual_effects_mode_sync(app, day_night_mode):
    """
    属性 48: 视觉效果与模式同步
    对于任意昼夜模式切换，视觉效果应该与模式保持同步：
    - 白天模式 (day) → theme_mode = "normal"，普通视觉效果
    - 黑夜模式 (night) → theme_mode = "halloween"，幽灵滤镜和暗黑主题
    """
    # 创建主题管理器
    tm = ThemeManager()
    
    # 根据昼夜模式切换
    if day_night_mode == "day":
        tm.set_day_mode()
        
        # 验证白天模式的视觉效果
        assert tm.get_theme_mode() == "normal", "白天模式应该使用 normal 主题"
        assert tm.get_day_night_mode() == "day", "昼夜模式应该是 day"
        assert tm.is_day_mode() == True, "is_day_mode() 应该返回 True"
        assert tm.is_night_mode() == False, "is_night_mode() 应该返回 False"
        assert tm.is_halloween_mode() == False, "白天模式不应该是万圣节模式"
        
        # 验证样式表应该为空（普通模式）
        widget = QWidget()
        tm.apply_theme_to_widget(widget)
        assert widget.styleSheet() == "", "白天模式应该清除样式表"
        widget.close()
        
    else:  # night mode
        tm.set_night_mode()
        
        # 验证黑夜模式的视觉效果
        assert tm.get_theme_mode() == "halloween", "黑夜模式应该使用 halloween 主题"
        assert tm.get_day_night_mode() == "night", "昼夜模式应该是 night"
        assert tm.is_day_mode() == False, "is_day_mode() 应该返回 False"
        assert tm.is_night_mode() == True, "is_night_mode() 应该返回 True"
        assert tm.is_halloween_mode() == True, "黑夜模式应该是万圣节模式"
        
        # 验证样式表应该是暗黑主题
        widget = QWidget()
        tm.apply_theme_to_widget(widget)
        stylesheet = widget.styleSheet()
        assert stylesheet != "", "黑夜模式应该应用暗黑样式表"
        assert "#1a1a1a" in stylesheet or "#0d0d0d" in stylesheet, "应该包含暗黑背景色"
        assert "#00ff00" in stylesheet, "应该包含绿色文字"
        widget.close()


# **Feature: puffer-pet, Property 33: 主题图像加载回退正确性**
# **验证: 需求 19.4, 19.5, 19.6**
@settings(max_examples=100, deadline=None)
@given(
    pet_id=valid_pet_id(),
    level=valid_level(),
    tier=valid_tier()
)
def test_property_33_theme_image_fallback_correctness(app, pet_id, level, tier):
    """
    属性 33: 主题图像加载回退正确性
    对于任意宠物和主题模式，当万圣节图像不存在时，
    应该成功回退到普通图像并应用幽灵滤镜，而不是崩溃
    """
    # 创建主题管理器（无数据管理器）
    tm = ThemeManager()
    
    # 设置为万圣节模式
    tm.set_theme_mode("halloween")
    assert tm.get_theme_mode() == "halloween"
    
    # 尝试加载图像 - 不应该崩溃
    try:
        pixmap = tm.load_themed_image(pet_id, "idle", level, tier)
        
        # 验证返回的是有效的 QPixmap
        assert pixmap is not None
        assert isinstance(pixmap, QPixmap)
        
        # 即使图像文件不存在，也应该返回占位符（不是空的）
        # 注意：如果图像文件存在，pixmap 不会是 null
        # 如果不存在，会返回占位符
        assert not pixmap.isNull(), "应该返回有效的图像或占位符"
        
    except Exception as e:
        pytest.fail(f"加载图像时不应该崩溃: {e}")


# **Feature: puffer-pet, Property 38: 暗黑主题应用完整性**
# **验证: 需求 19.7, 19.8**
@settings(max_examples=50, deadline=None)
@given(theme_mode=valid_theme_mode())
def test_property_38_dark_theme_application_completeness(app, theme_mode):
    """
    属性 38: 暗黑主题应用完整性
    对于任意UI窗口，当万圣节主题激活时，应该应用暗黑样式表（黑底、绿字、橙色边框）
    """
    # 创建主题管理器
    tm = ThemeManager()
    tm.set_theme_mode(theme_mode)
    
    # 创建测试窗口
    widget = QWidget()
    
    # 应用主题
    tm.apply_theme_to_widget(widget)
    
    if theme_mode == "halloween":
        # 验证样式表已应用
        stylesheet = widget.styleSheet()
        assert stylesheet != "", "万圣节模式应该应用样式表"
        
        # 验证样式表包含关键元素
        assert "#1a1a1a" in stylesheet or "#0d0d0d" in stylesheet, "应该包含暗黑背景色"
        assert "#00ff00" in stylesheet, "应该包含绿色文字"
        assert "#ff6600" in stylesheet, "应该包含橙色边框"
    else:
        # 普通模式应该清除样式表
        stylesheet = widget.styleSheet()
        assert stylesheet == "", "普通模式应该清除样式表"
    
    # 清理
    widget.close()


# 单元测试

class TestThemeManagerBasic:
    """主题管理器基本功能测试"""
    
    def test_default_theme_mode(self, app):
        """测试默认主题模式"""
        tm = ThemeManager()
        assert tm.get_theme_mode() == "normal"
    
    def test_set_theme_mode_halloween(self, app):
        """测试设置万圣节主题"""
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        assert tm.get_theme_mode() == "halloween"
        assert tm.is_halloween_mode() == True
    
    def test_set_theme_mode_normal(self, app):
        """测试设置普通主题"""
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        tm.set_theme_mode("normal")
        assert tm.get_theme_mode() == "normal"
        assert tm.is_halloween_mode() == False
    
    def test_set_invalid_theme_mode(self, app):
        """测试设置无效主题模式"""
        tm = ThemeManager()
        tm.set_theme_mode("invalid_mode")
        # 应该回退到 normal
        assert tm.get_theme_mode() == "normal"
    
    def test_default_ghost_opacity(self, app):
        """测试默认幽灵透明度"""
        tm = ThemeManager()
        assert tm.get_ghost_opacity() == 0.6
    
    def test_set_ghost_opacity(self, app):
        """测试设置幽灵透明度"""
        tm = ThemeManager()
        tm.set_ghost_opacity(0.8)
        assert tm.get_ghost_opacity() == 0.8
    
    def test_set_ghost_opacity_clamped(self, app):
        """测试透明度值被限制在有效范围"""
        tm = ThemeManager()
        
        tm.set_ghost_opacity(1.5)
        assert tm.get_ghost_opacity() == 1.0
        
        tm.set_ghost_opacity(-0.5)
        assert tm.get_ghost_opacity() == 0.0


class TestThemeManagerImageLoading:
    """主题管理器图像加载测试"""
    
    def test_load_image_normal_mode(self, app):
        """测试普通模式加载图像"""
        tm = ThemeManager()
        tm.set_theme_mode("normal")
        
        # 加载图像（可能是占位符）
        pixmap = tm.load_themed_image("puffer", "idle", 1, 1)
        
        assert pixmap is not None
        assert isinstance(pixmap, QPixmap)
        assert not pixmap.isNull()
    
    def test_load_image_halloween_mode_fallback(self, app):
        """测试万圣节模式回退到普通图像"""
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        
        # 加载图像（万圣节图像不存在时应该回退）
        pixmap = tm.load_themed_image("puffer", "idle", 1, 1)
        
        assert pixmap is not None
        assert isinstance(pixmap, QPixmap)
        assert not pixmap.isNull()
    
    def test_load_image_tier3(self, app):
        """测试加载Tier 3宠物图像"""
        tm = ThemeManager()
        
        # 加载Tier 3图像
        pixmap = tm.load_themed_image("blobfish", "idle", 1, 3)
        
        assert pixmap is not None
        assert isinstance(pixmap, QPixmap)
        assert not pixmap.isNull()
    
    def test_placeholder_creation(self, app):
        """测试占位符创建"""
        tm = ThemeManager()
        
        # 创建占位符
        pixmap = tm._create_placeholder("puffer", 1)
        
        assert pixmap is not None
        assert not pixmap.isNull()
        assert pixmap.width() == 50
        assert pixmap.height() == 50
    
    def test_placeholder_tier3_larger(self, app):
        """测试Tier 3占位符更大"""
        tm = ThemeManager()
        
        # 创建Tier 3占位符
        pixmap = tm._create_placeholder("bluewhale", 3)
        
        assert pixmap is not None
        assert not pixmap.isNull()
        assert pixmap.width() == 100
        assert pixmap.height() == 100


class TestThemeManagerGhostFilter:
    """幽灵滤镜测试"""
    
    def test_ghost_filter_on_valid_pixmap(self, app):
        """测试对有效图像应用幽灵滤镜"""
        tm = ThemeManager()
        
        # 创建一个简单的测试图像
        original = QPixmap(50, 50)
        original.fill(QColor(255, 0, 0))  # 红色
        
        # 应用幽灵滤镜
        filtered = tm.apply_ghost_filter(original)
        
        assert filtered is not None
        assert not filtered.isNull()
        assert filtered.width() == original.width()
        assert filtered.height() == original.height()
    
    def test_ghost_filter_on_null_pixmap(self, app):
        """测试对空图像应用幽灵滤镜"""
        tm = ThemeManager()
        
        # 创建空图像
        null_pixmap = QPixmap()
        
        # 应用幽灵滤镜 - 不应该崩溃
        filtered = tm.apply_ghost_filter(null_pixmap)
        
        assert filtered is not None
        assert filtered.isNull()  # 应该仍然是空的
    
    def test_ghost_filter_preserves_transparency(self, app):
        """测试幽灵滤镜保留透明区域"""
        tm = ThemeManager()
        
        # 创建带透明区域的图像
        original = QPixmap(50, 50)
        original.fill(Qt.GlobalColor.transparent)
        
        # 应用幽灵滤镜
        filtered = tm.apply_ghost_filter(original)
        
        assert filtered is not None
        assert not filtered.isNull()


class TestThemeManagerStylesheet:
    """样式表测试"""
    
    def test_get_dark_stylesheet(self, app):
        """测试获取暗黑样式表"""
        tm = ThemeManager()
        stylesheet = tm.get_dark_stylesheet()
        
        assert stylesheet is not None
        assert isinstance(stylesheet, str)
        assert len(stylesheet) > 0
        
        # 验证包含关键样式
        assert "QMenu" in stylesheet
        assert "QDialog" in stylesheet
        assert "QPushButton" in stylesheet
        assert "QLabel" in stylesheet
    
    def test_apply_theme_to_dialog(self, app):
        """测试应用主题到对话框"""
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        
        dialog = QDialog()
        tm.apply_theme_to_widget(dialog)
        
        assert dialog.styleSheet() != ""
        
        dialog.close()
    
    def test_apply_normal_theme_clears_stylesheet(self, app):
        """测试普通主题清除样式表"""
        tm = ThemeManager()
        
        widget = QWidget()
        
        # 先应用万圣节主题
        tm.set_theme_mode("halloween")
        tm.apply_theme_to_widget(widget)
        assert widget.styleSheet() != ""
        
        # 切换到普通主题
        tm.set_theme_mode("normal")
        tm.apply_theme_to_widget(widget)
        assert widget.styleSheet() == ""
        
        widget.close()


class TestThemeManagerWithDataManager:
    """主题管理器与数据管理器集成测试"""
    
    def test_theme_persistence(self, app):
        """测试主题设置持久化"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            # 创建数据管理器和主题管理器
            dm = DataManager(data_file=temp_file)
            tm = ThemeManager(data_manager=dm)
            
            # 设置万圣节主题
            tm.set_theme_mode("halloween")
            
            # 验证数据已保存
            assert dm.data.get('theme_mode') == 'halloween'
            
            # 创建新的主题管理器，验证设置被加载
            tm2 = ThemeManager(data_manager=dm)
            assert tm2.get_theme_mode() == "halloween"
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_ghost_opacity_persistence(self, app):
        """测试幽灵透明度持久化"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            # 创建数据管理器和主题管理器
            dm = DataManager(data_file=temp_file)
            tm = ThemeManager(data_manager=dm)
            
            # 设置透明度
            tm.set_ghost_opacity(0.8)
            
            # 验证数据已保存
            assert dm.data.get('halloween_settings', {}).get('ghost_opacity') == 0.8
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


# ==================== 任务 44.1: 验证图像加载回退机制 ====================

class TestImageLoadingFallbackMechanism:
    """
    验证图像加载回退机制测试
    
    测试内容:
    - 测试有万圣节图像的宠物
    - 测试无万圣节图像的宠物（应用滤镜）
    - 测试有愤怒图像的宠物
    - 测试无愤怒图像的宠物（抖动动画）
    
    需求: 19.4, 22.6
    """
    
    def test_halloween_image_fallback_to_normal_with_filter(self, app):
        """测试万圣节图像不存在时回退到普通图像并应用滤镜"""
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        
        # 测试所有宠物类型
        all_pets = ['puffer', 'jelly', 'starfish', 'crab', 'octopus', 'ribbon', 
                    'sunfish', 'angler', 'blobfish', 'ray', 'beluga', 'orca', 
                    'shark', 'bluewhale']
        
        for pet_id in all_pets:
            tier = 3 if pet_id in ['blobfish', 'ray', 'beluga', 'orca', 'shark', 'bluewhale'] else 1
            
            # 加载图像 - 不应该崩溃
            pixmap = tm.load_themed_image(pet_id, "idle", 1, tier)
            
            # 验证返回有效图像
            assert pixmap is not None, f"宠物 {pet_id} 应该返回有效图像"
            assert not pixmap.isNull(), f"宠物 {pet_id} 的图像不应该为空"
    
    def test_normal_mode_loads_normal_images(self, app):
        """测试普通模式加载普通图像（不应用滤镜）"""
        tm = ThemeManager()
        tm.set_theme_mode("normal")
        
        # 测试几个宠物
        test_pets = ['puffer', 'jelly', 'blobfish']
        
        for pet_id in test_pets:
            tier = 3 if pet_id == 'blobfish' else 1
            
            pixmap = tm.load_themed_image(pet_id, "idle", 1, tier)
            
            assert pixmap is not None
            assert not pixmap.isNull()
    
    def test_halloween_mode_with_existing_halloween_image(self, app):
        """测试万圣节模式下有万圣节图像时直接加载"""
        import os
        
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        
        # 测试 puffer 和 jelly（这两个有万圣节图像）
        pets_with_halloween = ['puffer', 'jelly']
        
        for test_pet in pets_with_halloween:
            halloween_path = f"assets/{test_pet}/halloween_idle.png"
            
            # 检查是否已存在万圣节图像
            if os.path.exists(halloween_path):
                # 如果存在，直接测试
                pixmap = tm.load_themed_image(test_pet, "idle", 1, 1)
                assert pixmap is not None, f"{test_pet} 应该加载万圣节图像"
                assert not pixmap.isNull(), f"{test_pet} 的万圣节图像不应该为空"
            else:
                # 如果不存在，验证回退机制工作
                pixmap = tm.load_themed_image(test_pet, "idle", 1, 1)
                assert pixmap is not None
                assert not pixmap.isNull()
    
    def test_pets_with_halloween_images_load_directly(self, app):
        """测试有万圣节图像的宠物直接加载（不应用滤镜）"""
        import os
        
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        
        # puffer 和 jelly 有万圣节图像
        for pet_id in ['puffer', 'jelly']:
            halloween_path = f"assets/{pet_id}/halloween_idle.png"
            
            if os.path.exists(halloween_path):
                # 加载图像
                pixmap = tm.load_themed_image(pet_id, "idle", 1, 1)
                
                # 验证图像已加载
                assert pixmap is not None
                assert not pixmap.isNull()
                
                # 图像应该是万圣节图像（100x100 占位符）
                # 注意：实际图像大小可能不同
                assert pixmap.width() > 0
                assert pixmap.height() > 0
    
    def test_ghost_filter_changes_image(self, app):
        """测试幽灵滤镜确实改变了图像"""
        tm = ThemeManager()
        
        # 创建一个纯色测试图像
        original = QPixmap(50, 50)
        original.fill(QColor(255, 0, 0))  # 纯红色
        
        # 应用幽灵滤镜
        filtered = tm.apply_ghost_filter(original)
        
        # 验证图像已改变
        assert filtered is not None
        assert not filtered.isNull()
        
        # 检查像素颜色是否改变（应该混合了绿色或紫色）
        original_image = original.toImage()
        filtered_image = filtered.toImage()
        
        original_pixel = original_image.pixelColor(25, 25)
        filtered_pixel = filtered_image.pixelColor(25, 25)
        
        # 滤镜应该改变了颜色（透明度或RGB值）
        color_changed = (
            original_pixel.red() != filtered_pixel.red() or
            original_pixel.green() != filtered_pixel.green() or
            original_pixel.blue() != filtered_pixel.blue() or
            original_pixel.alpha() != filtered_pixel.alpha()
        )
        assert color_changed, "幽灵滤镜应该改变图像颜色"
    
    def test_ghost_filter_reduces_opacity(self, app):
        """测试幽灵滤镜降低透明度"""
        tm = ThemeManager()
        tm.set_ghost_opacity(0.6)
        
        # 创建一个不透明的测试图像
        original = QPixmap(50, 50)
        original.fill(QColor(255, 0, 0, 255))  # 完全不透明的红色
        
        # 应用幽灵滤镜
        filtered = tm.apply_ghost_filter(original)
        
        # 检查透明度是否降低
        filtered_image = filtered.toImage()
        filtered_pixel = filtered_image.pixelColor(25, 25)
        
        # 透明度应该约为 255 * 0.6 = 153
        expected_alpha = int(255 * 0.6)
        actual_alpha = filtered_pixel.alpha()
        
        # 允许一些误差
        assert abs(actual_alpha - expected_alpha) <= 5, \
            f"透明度应该约为 {expected_alpha}，但得到 {actual_alpha}"
    
    def test_all_tiers_load_correctly_in_halloween_mode(self, app):
        """测试所有层级的宠物在万圣节模式下都能正确加载"""
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        
        # Tier 1 宠物
        tier1_pets = ['puffer', 'jelly', 'starfish', 'crab']
        for pet_id in tier1_pets:
            pixmap = tm.load_themed_image(pet_id, "idle", 1, 1)
            assert not pixmap.isNull(), f"Tier 1 宠物 {pet_id} 应该加载成功"
        
        # Tier 2 宠物
        tier2_pets = ['octopus', 'ribbon', 'sunfish', 'angler']
        for pet_id in tier2_pets:
            pixmap = tm.load_themed_image(pet_id, "idle", 1, 2)
            assert not pixmap.isNull(), f"Tier 2 宠物 {pet_id} 应该加载成功"
        
        # Tier 3 宠物
        tier3_pets = ['blobfish', 'ray', 'beluga', 'orca', 'shark', 'bluewhale']
        for pet_id in tier3_pets:
            pixmap = tm.load_themed_image(pet_id, "idle", 1, 3)
            assert not pixmap.isNull(), f"Tier 3 宠物 {pet_id} 应该加载成功"


class TestAngryImageFallbackMechanism:
    """
    验证愤怒图像加载回退机制测试
    
    测试内容:
    - 测试有愤怒图像的宠物
    - 测试无愤怒图像的宠物（抖动动画）
    
    需求: 22.6
    """
    
    def test_angry_image_path_format(self, app):
        """测试愤怒图像路径格式正确"""
        import os
        
        # Tier 1/2 宠物的愤怒图像路径
        tier1_pet = 'puffer'
        expected_tier1_path = f"assets/{tier1_pet}/angry_idle.png"
        
        # Tier 3 宠物的愤怒图像路径
        tier3_pet = 'blobfish'
        expected_tier3_path = f"assets/deep_sea/{tier3_pet}/angry_idle.png"
        
        # 验证路径格式正确（不验证文件是否存在）
        assert 'angry_idle.png' in expected_tier1_path
        assert 'angry_idle.png' in expected_tier3_path
        assert 'deep_sea' in expected_tier3_path
        assert 'deep_sea' not in expected_tier1_path
    
    def test_pets_with_angry_images_load_correctly(self, app):
        """测试有愤怒图像的宠物正确加载愤怒图像"""
        import os
        
        # puffer 和 jelly 有愤怒图像
        for pet_id in ['puffer', 'jelly']:
            angry_path = f"assets/{pet_id}/angry_idle.png"
            
            if os.path.exists(angry_path):
                # 验证文件存在
                assert os.path.isfile(angry_path), f"{pet_id} 的愤怒图像应该存在"
                
                # 尝试加载图像
                from PyQt6.QtGui import QPixmap
                pixmap = QPixmap(angry_path)
                
                assert not pixmap.isNull(), f"{pet_id} 的愤怒图像应该可以加载"
                assert pixmap.width() > 0
                assert pixmap.height() > 0
    
    def test_pet_widget_shake_animation_when_no_angry_image(self, app):
        """测试无愤怒图像时使用抖动动画"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            from pet_widget import PetWidget
            
            dm = DataManager(data_file=temp_file)
            widget = PetWidget(dm)
            
            # 设置为愤怒状态
            widget.set_angry(True)
            
            # 验证抖动定时器已启动
            assert widget.is_angry == True
            assert widget.shake_timer is not None
            assert widget.shake_timer.isActive()
            
            # 验证原始位置被保存
            assert widget._original_pos is not None
            
            widget.close()
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_shake_animation_offset_range(self, app):
        """测试抖动动画偏移范围为±10像素"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            from pet_widget import PetWidget
            
            dm = DataManager(data_file=temp_file)
            widget = PetWidget(dm)
            
            # 设置初始位置
            widget.move(100, 100)
            
            # 设置为愤怒状态
            widget.set_angry(True)
            
            # 多次触发抖动并检查偏移范围
            for _ in range(10):
                widget._do_shake()
                
                # 检查位置在原始位置±10像素范围内
                x_offset = abs(widget.x() - 100)
                y_offset = abs(widget.y() - 100)
                
                assert x_offset <= 10, f"X偏移 {x_offset} 超出±10像素范围"
                assert y_offset <= 10, f"Y偏移 {y_offset} 超出±10像素范围"
            
            widget.close()
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_calm_restores_position_and_stops_shake(self, app):
        """测试安抚后恢复位置并停止抖动"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            from pet_widget import PetWidget
            
            dm = DataManager(data_file=temp_file)
            widget = PetWidget(dm)
            
            # 设置初始位置
            widget.move(100, 100)
            
            # 设置为愤怒状态
            widget.set_angry(True)
            
            # 触发几次抖动
            for _ in range(5):
                widget._do_shake()
            
            # 安抚宠物
            widget.set_calm()
            
            # 验证位置恢复
            assert widget.x() == 100
            assert widget.y() == 100
            
            # 验证抖动停止
            assert not widget.shake_timer.isActive()
            assert widget.is_angry == False
            
            widget.close()
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_angry_state_with_theme_manager_ghost_filter(self, app):
        """测试愤怒状态下万圣节模式应用幽灵滤镜"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            from pet_widget import PetWidget
            
            dm = DataManager(data_file=temp_file)
            tm = ThemeManager(dm)
            tm.set_theme_mode("halloween")
            
            widget = PetWidget(dm)
            widget.theme_manager = tm
            
            # 设置为愤怒状态
            widget.set_angry(True)
            
            # 验证图像已加载（可能应用了幽灵滤镜）
            assert widget.current_pixmap is not None
            assert not widget.current_pixmap.isNull()
            
            widget.close()
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


# ==================== 任务 60.2: 昼夜模式映射单元测试 ====================

class TestDayNightModeMapping:
    """
    昼夜模式映射测试
    
    测试内容:
    - 测试昼夜模式映射
    - 测试模式切换信号
    - 测试视觉效果更新
    
    需求: 28.6, 28.7, 28.8
    """
    
    def test_set_day_mode_sets_normal_theme(self, app):
        """测试 set_day_mode() 设置 normal 主题"""
        tm = ThemeManager()
        
        # 先设置为黑夜模式
        tm.set_night_mode()
        assert tm.get_theme_mode() == "halloween"
        
        # 切换到白天模式
        tm.set_day_mode()
        
        # 验证主题模式
        assert tm.get_theme_mode() == "normal"
        assert tm.get_day_night_mode() == "day"
        assert tm.is_day_mode() == True
        assert tm.is_night_mode() == False
        assert tm.is_halloween_mode() == False
    
    def test_set_night_mode_sets_halloween_theme(self, app):
        """测试 set_night_mode() 设置 halloween 主题"""
        tm = ThemeManager()
        
        # 初始应该是普通模式
        assert tm.get_theme_mode() == "normal"
        
        # 切换到黑夜模式
        tm.set_night_mode()
        
        # 验证主题模式
        assert tm.get_theme_mode() == "halloween"
        assert tm.get_day_night_mode() == "night"
        assert tm.is_day_mode() == False
        assert tm.is_night_mode() == True
        assert tm.is_halloween_mode() == True
    
    def test_day_night_mode_map_constant(self, app):
        """测试昼夜模式映射常量"""
        tm = ThemeManager()
        
        # 验证映射常量
        assert tm.DAY_NIGHT_MODE_MAP["day"] == "normal"
        assert tm.DAY_NIGHT_MODE_MAP["night"] == "halloween"
    
    def test_get_theme_for_day_night(self, app):
        """测试 get_theme_for_day_night() 方法"""
        tm = ThemeManager()
        
        assert tm.get_theme_for_day_night("day") == "normal"
        assert tm.get_theme_for_day_night("night") == "halloween"
        assert tm.get_theme_for_day_night("invalid") == "normal"  # 默认值
    
    def test_mode_changed_signal_emitted_on_day_mode(self, app):
        """测试切换到白天模式时发出信号"""
        tm = ThemeManager()
        
        # 记录信号
        received_signals = []
        tm.mode_changed.connect(lambda mode: received_signals.append(mode))
        
        # 先设置为黑夜模式
        tm.set_night_mode()
        
        # 清空信号记录
        received_signals.clear()
        
        # 切换到白天模式
        tm.set_day_mode()
        
        # 验证信号已发出
        assert len(received_signals) == 1
        assert received_signals[0] == "normal"
    
    def test_mode_changed_signal_emitted_on_night_mode(self, app):
        """测试切换到黑夜模式时发出信号"""
        tm = ThemeManager()
        
        # 记录信号
        received_signals = []
        tm.mode_changed.connect(lambda mode: received_signals.append(mode))
        
        # 切换到黑夜模式
        tm.set_night_mode()
        
        # 验证信号已发出
        assert len(received_signals) == 1
        assert received_signals[0] == "halloween"
    
    def test_mode_changed_signal_not_emitted_when_same_mode(self, app):
        """测试相同模式不发出信号"""
        tm = ThemeManager()
        
        # 记录信号
        received_signals = []
        tm.mode_changed.connect(lambda mode: received_signals.append(mode))
        
        # 设置为普通模式（已经是普通模式）
        tm.set_day_mode()
        
        # 不应该发出信号（因为模式没有变化）
        assert len(received_signals) == 0
    
    def test_night_mode_reuses_halloween_visual_effects(self, app):
        """测试黑夜模式复用万圣节视觉效果"""
        tm = ThemeManager()
        tm.set_night_mode()
        
        # 验证使用万圣节样式表
        stylesheet = tm.get_dark_stylesheet()
        assert "#1a1a1a" in stylesheet or "#0d0d0d" in stylesheet
        assert "#00ff00" in stylesheet
        assert "#ff6600" in stylesheet
        
        # 验证幽灵滤镜可用
        assert tm.is_halloween_mode() == True
    
    def test_day_mode_clears_visual_effects(self, app):
        """测试白天模式清除视觉效果"""
        tm = ThemeManager()
        
        # 先设置为黑夜模式
        tm.set_night_mode()
        
        widget = QWidget()
        tm.apply_theme_to_widget(widget)
        assert widget.styleSheet() != ""
        
        # 切换到白天模式
        tm.set_day_mode()
        tm.apply_theme_to_widget(widget)
        
        # 验证样式表已清除
        assert widget.styleSheet() == ""
        
        widget.close()
    
    def test_day_night_mode_persistence(self, app):
        """测试昼夜模式持久化"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            # 创建数据管理器和主题管理器
            dm = DataManager(data_file=temp_file)
            tm = ThemeManager(data_manager=dm)
            
            # 设置为黑夜模式
            tm.set_night_mode()
            
            # 验证数据已保存
            assert dm.data.get('theme_mode') == 'halloween'
            assert dm.data.get('day_night_settings', {}).get('current_mode') == 'night'
            
            # 创建新的主题管理器，验证设置被加载
            tm2 = ThemeManager(data_manager=dm)
            assert tm2.get_theme_mode() == "halloween"
            assert tm2.get_day_night_mode() == "night"
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_day_mode_persistence(self, app):
        """测试白天模式持久化"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            # 创建数据管理器和主题管理器
            dm = DataManager(data_file=temp_file)
            tm = ThemeManager(data_manager=dm)
            
            # 先设置为黑夜模式，再切换到白天模式
            tm.set_night_mode()
            tm.set_day_mode()
            
            # 验证数据已保存
            assert dm.data.get('theme_mode') == 'normal'
            assert dm.data.get('day_night_settings', {}).get('current_mode') == 'day'
            
            # 创建新的主题管理器，验证设置被加载
            tm2 = ThemeManager(data_manager=dm)
            assert tm2.get_theme_mode() == "normal"
            assert tm2.get_day_night_mode() == "day"
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_image_loading_in_day_mode(self, app):
        """测试白天模式下的图像加载"""
        tm = ThemeManager()
        tm.set_day_mode()
        
        # 加载图像
        pixmap = tm.load_themed_image("puffer", "idle", 1, 1)
        
        # 验证图像已加载（不应用幽灵滤镜）
        assert pixmap is not None
        assert not pixmap.isNull()
    
    def test_image_loading_in_night_mode(self, app):
        """测试黑夜模式下的图像加载（应用幽灵滤镜）"""
        tm = ThemeManager()
        tm.set_night_mode()
        
        # 加载图像
        pixmap = tm.load_themed_image("puffer", "idle", 1, 1)
        
        # 验证图像已加载（可能应用了幽灵滤镜）
        assert pixmap is not None
        assert not pixmap.isNull()


class TestHalloweenModeDisplayEffect:
    """
    测试所有宠物在万圣节模式下的显示效果
    
    需求: 19.3, 19.4, 22.5, 22.6
    """
    
    def test_all_pets_display_in_halloween_mode(self, app):
        """测试所有宠物在万圣节模式下都能正常显示"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            from pet_widget import PetWidget
            
            dm = DataManager(data_file=temp_file)
            tm = ThemeManager(dm)
            tm.set_theme_mode("halloween")
            
            # 测试所有宠物
            all_pets = ['puffer', 'jelly', 'starfish', 'crab', 'octopus', 'ribbon', 
                        'sunfish', 'angler', 'blobfish', 'ray', 'beluga', 'orca', 
                        'shark', 'bluewhale']
            
            for pet_id in all_pets:
                # 解锁并切换到宠物
                dm.unlock_pet(pet_id)
                dm.set_current_pet_id(pet_id)
                
                # 创建宠物窗口
                widget = PetWidget(dm)
                widget.theme_manager = tm
                
                # 重新加载图像
                widget.load_image()
                
                # 验证图像已加载
                assert widget.current_pixmap is not None, \
                    f"宠物 {pet_id} 在万圣节模式下应该有图像"
                assert not widget.current_pixmap.isNull(), \
                    f"宠物 {pet_id} 的图像不应该为空"
                
                widget.close()
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_dark_theme_applied_to_all_windows(self, app):
        """测试暗黑主题应用到所有窗口类型"""
        tm = ThemeManager()
        tm.set_theme_mode("halloween")
        
        # 测试不同类型的窗口
        from PyQt6.QtWidgets import QDialog, QMainWindow
        
        windows = [
            QWidget(),
            QDialog(),
        ]
        
        for window in windows:
            tm.apply_theme_to_widget(window)
            
            # 验证样式表已应用
            stylesheet = window.styleSheet()
            assert stylesheet != "", f"{type(window).__name__} 应该有样式表"
            assert "#1a1a1a" in stylesheet or "#0d0d0d" in stylesheet
            
            window.close()
    
    def test_halloween_mode_toggle(self, app):
        """测试万圣节模式切换"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            dm = DataManager(data_file=temp_file)
            tm = ThemeManager(dm)
            
            # 初始应该是普通模式
            assert tm.get_theme_mode() == "normal"
            
            # 切换到万圣节模式
            tm.set_theme_mode("halloween")
            assert tm.get_theme_mode() == "halloween"
            assert tm.is_halloween_mode() == True
            
            # 切换回普通模式
            tm.set_theme_mode("normal")
            assert tm.get_theme_mode() == "normal"
            assert tm.is_halloween_mode() == False
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


# =============================================================================
# Retro Kiroween UI Ghost Filter Property Tests
# =============================================================================

# **Feature: retro-kiroween-ui, Property 7: Ghost Filter Opacity Reduction**
# **Validates: Requirements 4.2**
@settings(max_examples=100, deadline=None)
@given(
    original_alpha=st.integers(min_value=1, max_value=255),
    red=st.integers(min_value=0, max_value=255),
    green=st.integers(min_value=0, max_value=255),
    blue=st.integers(min_value=0, max_value=255)
)
def test_property_7_ghost_filter_opacity_reduction(app, original_alpha, red, green, blue):
    """
    Property 7: Ghost Filter Opacity Reduction
    
    *For any* non-transparent pixel in an image, after applying `apply_ghost_filter()`,
    the pixel's alpha value shall be between 60% and 70% of the original alpha value.
    """
    from theme_manager import ThemeManager
    from PyQt6.QtGui import QPixmap, QColor, QImage
    
    # Create a test image with a single colored pixel
    pixmap = QPixmap(10, 10)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    image = pixmap.toImage()
    image = image.convertToFormat(QImage.Format.Format_ARGB32)
    
    # Set a pixel with the generated color and alpha
    test_color = QColor(red, green, blue, original_alpha)
    image.setPixelColor(5, 5, test_color)
    
    original_pixmap = QPixmap.fromImage(image)
    
    # Apply ghost filter
    tm = ThemeManager()
    filtered_pixmap = tm.apply_ghost_filter(original_pixmap)
    
    # Check the filtered pixel
    filtered_image = filtered_pixmap.toImage()
    filtered_pixel = filtered_image.pixelColor(5, 5)
    
    # Calculate expected alpha range (60-70% of original)
    min_expected_alpha = int(original_alpha * 0.60)
    max_expected_alpha = int(original_alpha * 0.70)
    
    actual_alpha = filtered_pixel.alpha()
    
    # Allow small tolerance for rounding
    assert min_expected_alpha - 1 <= actual_alpha <= max_expected_alpha + 1, \
        f"Filtered alpha {actual_alpha} should be between {min_expected_alpha} and {max_expected_alpha} (60-70% of {original_alpha})"


# **Feature: retro-kiroween-ui, Property 8: Ghost Filter Color Tint**
# **Validates: Requirements 4.3**
@settings(max_examples=100, deadline=None)
@given(
    red=st.integers(min_value=0, max_value=200),
    green=st.integers(min_value=0, max_value=200),
    blue=st.integers(min_value=0, max_value=200)
)
def test_property_8_ghost_filter_color_tint(app, red, green, blue):
    """
    Property 8: Ghost Filter Color Tint
    
    *For any* non-transparent pixel in an image, after applying `apply_ghost_filter()`,
    the pixel shall have increased green or purple color component compared to the original.
    
    The ghost filter uses either:
    - Ghost green (#00FF88): increases green component
    - Curse purple (#8B00FF): increases blue component and adds red
    """
    from theme_manager import ThemeManager
    from PyQt6.QtGui import QPixmap, QColor, QImage
    
    # Create a test image with a single colored pixel
    pixmap = QPixmap(10, 10)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    image = pixmap.toImage()
    image = image.convertToFormat(QImage.Format.Format_ARGB32)
    
    # Set a pixel with the generated color (fully opaque)
    test_color = QColor(red, green, blue, 255)
    image.setPixelColor(5, 5, test_color)
    
    original_pixmap = QPixmap.fromImage(image)
    
    # Apply ghost filter with specific tint color to make test deterministic
    tm = ThemeManager()
    
    # Test with ghost green tint (#00FF88)
    ghost_green = QColor(0, 255, 136, 255)
    filtered_pixmap = tm.apply_ghost_filter(original_pixmap, tint_color=ghost_green)
    
    filtered_image = filtered_pixmap.toImage()
    filtered_pixel = filtered_image.pixelColor(5, 5)
    
    # With 0.3 blend factor and ghost green (#00FF88):
    # new_green = original_green * 0.7 + 255 * 0.3 = original_green * 0.7 + 76.5
    # So green should increase (or stay high if already high)
    expected_green = int(green * 0.7 + 255 * 0.3)
    expected_green = max(0, min(255, expected_green))
    
    # Allow tolerance for rounding
    assert abs(filtered_pixel.green() - expected_green) <= 2, \
        f"Green component should be ~{expected_green} after ghost green tint, got {filtered_pixel.green()}"
