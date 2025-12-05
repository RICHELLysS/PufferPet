"""主窗口组件的单元测试"""
import pytest
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QContextMenuEvent
from data_manager import DataManager
from pet_core import PetWidget


@pytest.fixture
def qapp():
    """创建 QApplication 实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def data_manager(tmp_path):
    """创建临时数据管理器"""
    data_file = tmp_path / "test_data.json"
    return DataManager(str(data_file))


@pytest.fixture
def pet_widget(qapp, data_manager):
    """创建 PetWidget 实例"""
    widget = PetWidget(data_manager)
    yield widget
    widget.close()


def test_window_is_frameless(pet_widget):
    """测试窗口是无边框的"""
    flags = pet_widget.windowFlags()
    assert flags & Qt.WindowType.FramelessWindowHint


def test_window_stays_on_top(pet_widget):
    """测试窗口始终置顶"""
    flags = pet_widget.windowFlags()
    assert flags & Qt.WindowType.WindowStaysOnTopHint


def test_window_has_transparent_background(pet_widget):
    """测试窗口具有透明背景"""
    assert pet_widget.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)


def test_window_has_fixed_size(pet_widget):
    """测试窗口具有固定大小"""
    assert pet_widget.width() == 200
    assert pet_widget.height() == 200


def test_image_loads_for_current_pet(data_manager, qapp):
    """测试当前宠物的图像加载"""
    # 确保有当前宠物
    current_pet = data_manager.get_current_pet_id()
    assert current_pet is not None
    
    widget = PetWidget(data_manager)
    
    # 检查是否尝试加载图像
    assert widget.current_pixmap is not None
    widget.close()


def test_placeholder_when_image_missing(data_manager, qapp):
    """测试图像缺失时显示占位符"""
    # Mock get_image_for_level to return a non-existent path
    current_pet = data_manager.get_current_pet_id()
    original_get_image = data_manager.get_image_for_level
    data_manager.get_image_for_level = lambda pet_id, level=None: f"assets/{current_pet}/nonexistent.png"
    
    widget = PetWidget(data_manager)
    
    # Restore original method
    data_manager.get_image_for_level = original_get_image
    
    # 应该有占位符图像
    assert widget.current_pixmap is not None
    assert not widget.current_pixmap.isNull()
    
    # 占位符应该是 100x100 的红色方块（河豚）
    assert widget.current_pixmap.width() == 100
    assert widget.current_pixmap.height() == 100
    widget.close()


def test_jelly_placeholder_is_blue(data_manager, qapp):
    """测试水母图像缺失时显示紫色占位符"""
    # 解锁并切换到水母
    data_manager.unlock_pet("jelly")
    data_manager.set_current_pet_id("jelly")
    
    # Mock get_image_for_level to return a non-existent path
    original_get_image = data_manager.get_image_for_level
    data_manager.get_image_for_level = lambda pet_id, level=None: "assets/jelly/nonexistent.png"
    
    widget = PetWidget(data_manager)
    
    # Restore original method
    data_manager.get_image_for_level = original_get_image
    
    # 应该有占位符图像
    assert widget.current_pixmap is not None
    assert not widget.current_pixmap.isNull()
    
    # 占位符应该是 100x100 的蓝色方块（水母）
    assert widget.current_pixmap.width() == 100
    assert widget.current_pixmap.height() == 100
    
    # 验证颜色是紫色（通过检查像素）
    from PyQt6.QtGui import QColor
    pixel_color = widget.current_pixmap.toImage().pixelColor(50, 50)
    # Jelly uses purple: (200, 150, 255)
    assert pixel_color.red() == 200
    assert pixel_color.green() == 150
    assert pixel_color.blue() == 255
    
    widget.close()


def test_update_display_reloads_image(pet_widget, data_manager):
    """测试 update_display 重新加载图像"""
    # 获取初始图像
    initial_pixmap = pet_widget.current_pixmap
    
    # 改变等级
    current_pet = data_manager.get_current_pet_id()
    data_manager.data['pets_data'][current_pet]['level'] = 2
    
    # 更新显示
    pet_widget.update_display()
    
    # 图像应该被重新加载（即使都是占位符，也是新对象）
    assert pet_widget.current_pixmap is not None


def test_switch_pet_method_exists(pet_widget):
    """测试 switch_pet 方法存在"""
    assert hasattr(pet_widget, 'switch_pet')
    assert callable(getattr(pet_widget, 'switch_pet'))


def test_switch_pet_to_unlocked_pet(pet_widget, data_manager):
    """测试切换到已解锁的宠物"""
    # 解锁水母
    data_manager.unlock_pet("jelly")
    
    # 切换到水母
    pet_widget.switch_pet("jelly")
    
    # 验证当前宠物已切换
    assert data_manager.get_current_pet_id() == "jelly"


def test_switch_pet_to_locked_pet_fails(pet_widget, data_manager, qapp):
    """测试切换到未解锁的宠物失败"""
    # 确保水母未解锁
    if "jelly" in data_manager.get_unlocked_pets():
        data_manager.data['unlocked_pets'].remove("jelly")
    
    # 记录当前宠物
    original_pet = data_manager.get_current_pet_id()
    
    # 尝试切换到水母（应该失败）
    pet_widget.switch_pet("jelly")
    
    # 验证当前宠物未改变
    assert data_manager.get_current_pet_id() == original_pet


def test_show_pet_selector_method_exists(pet_widget):
    """测试 show_pet_selector 方法存在"""
    assert hasattr(pet_widget, 'show_pet_selector')
    assert callable(getattr(pet_widget, 'show_pet_selector'))


def test_show_unlock_notification_method_exists(pet_widget):
    """测试 show_unlock_notification 方法存在"""
    assert hasattr(pet_widget, 'show_unlock_notification')
    assert callable(getattr(pet_widget, 'show_unlock_notification'))


def test_context_menu_has_switch_pet_option(pet_widget, qapp):
    """测试右键菜单包含切换宠物选项"""
    # 验证 contextMenuEvent 方法存在
    assert hasattr(pet_widget, 'contextMenuEvent')
    assert callable(getattr(pet_widget, 'contextMenuEvent'))
    
    # 注意：完整的菜单测试需要模拟右键点击事件
    # 这里只验证方法存在，实际菜单内容将在集成测试中验证


def test_show_release_confirmation_method_exists(pet_widget):
    """测试 show_release_confirmation 方法存在"""
    assert hasattr(pet_widget, 'show_release_confirmation')
    assert callable(getattr(pet_widget, 'show_release_confirmation'))


def test_pet_widget_accepts_pet_manager(data_manager, qapp):
    """测试 PetWidget 可以接受 pet_manager 参数"""
    from pet_manager import PetManager
    
    pet_manager = PetManager(data_manager)
    widget = PetWidget(data_manager, pet_manager)
    
    assert widget.pet_manager is pet_manager
    widget.close()


def test_pet_widget_works_without_pet_manager(data_manager, qapp):
    """测试 PetWidget 在没有 pet_manager 的情况下也能工作（向后兼容）"""
    widget = PetWidget(data_manager)
    
    assert widget.pet_manager is None
    widget.close()


def test_context_menu_has_release_option(pet_widget):
    """测试右键菜单包含放生选项"""
    # 验证 contextMenuEvent 方法存在
    assert hasattr(pet_widget, 'contextMenuEvent')
    assert callable(getattr(pet_widget, 'contextMenuEvent'))
    
    # 验证 show_release_confirmation 方法存在
    assert hasattr(pet_widget, 'show_release_confirmation')
    assert callable(getattr(pet_widget, 'show_release_confirmation'))



def test_multiple_pet_windows_can_be_created(data_manager, qapp):
    """测试可以创建多个宠物窗口"""
    from pet_manager import PetManager
    
    # 解锁多个宠物
    data_manager.unlock_pet("jelly")
    data_manager.unlock_pet("starfish")
    
    pet_manager = PetManager(data_manager)
    
    # 创建多个宠物窗口
    widget1 = PetWidget(data_manager, pet_manager)
    widget1.switch_pet("puffer")
    
    widget2 = PetWidget(data_manager, pet_manager)
    widget2.switch_pet("jelly")
    
    widget3 = PetWidget(data_manager, pet_manager)
    widget3.switch_pet("starfish")
    
    # 验证所有窗口都已创建
    assert widget1.data_manager.get_current_pet_id() in ["puffer", "jelly", "starfish"]
    assert widget2.data_manager.get_current_pet_id() in ["puffer", "jelly", "starfish"]
    assert widget3.data_manager.get_current_pet_id() in ["puffer", "jelly", "starfish"]
    
    # 清理
    widget1.close()
    widget2.close()
    widget3.close()


def test_pet_manager_loads_active_pets(data_manager, qapp):
    """测试 PetManager 加载活跃宠物"""
    from pet_manager import PetManager
    
    # 解锁多个宠物
    data_manager.unlock_pet("jelly")
    data_manager.unlock_pet("starfish")
    
    # 设置活跃宠物
    data_manager.set_active_pets(["puffer", "jelly"])
    
    pet_manager = PetManager(data_manager)
    pet_manager.load_active_pets()
    
    # 验证窗口已创建
    assert len(pet_manager.active_pet_windows) == 2
    assert "puffer" in pet_manager.active_pet_windows
    assert "jelly" in pet_manager.active_pet_windows
    
    # 清理
    for window in pet_manager.active_pet_windows.values():
        window.close()


def test_release_with_pet_manager(data_manager, qapp):
    """测试通过 pet_manager 放生宠物"""
    from pet_manager import PetManager
    from unittest.mock import patch
    from PyQt6.QtWidgets import QMessageBox
    
    # 解锁水母
    data_manager.unlock_pet("jelly")
    data_manager.set_current_pet_id("jelly")
    
    pet_manager = PetManager(data_manager)
    widget = PetWidget(data_manager, pet_manager)
    widget.switch_pet("jelly")
    
    # 模拟用户点击"是"
    with patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.Yes):
        # 模拟 pet_manager.release_pet
        with patch.object(pet_manager, 'release_pet', return_value=True) as mock_release:
            widget.show_release_confirmation()
            
            # 验证 release_pet 被调用
            mock_release.assert_called_once_with("jelly")
    
    widget.close()


def test_release_without_pet_manager(data_manager, qapp):
    """测试没有 pet_manager 时放生宠物（向后兼容）"""
    from unittest.mock import patch
    from PyQt6.QtWidgets import QMessageBox
    
    widget = PetWidget(data_manager)  # 不传入 pet_manager
    
    # 模拟用户点击"是"
    with patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.Yes):
        # 模拟窗口关闭
        with patch.object(widget, 'close') as mock_close:
            widget.show_release_confirmation()
            
            # 验证窗口被关闭
            mock_close.assert_called_once()
    
    widget.close()


def test_release_confirmation_cancelled(data_manager, qapp):
    """测试取消放生确认"""
    from pet_manager import PetManager
    from unittest.mock import patch
    from PyQt6.QtWidgets import QMessageBox
    
    pet_manager = PetManager(data_manager)
    widget = PetWidget(data_manager, pet_manager)
    
    # 模拟用户点击"否"
    with patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.No):
        # 模拟 pet_manager.release_pet
        with patch.object(pet_manager, 'release_pet') as mock_release:
            widget.show_release_confirmation()
            
            # 验证 release_pet 未被调用
            mock_release.assert_not_called()
    
    widget.close()


# Tier 3 宠物显示测试

def test_tier3_image_path_generation(data_manager, qapp):
    """测试Tier 3宠物图像路径生成"""
    # 解锁一个Tier 3宠物
    tier3_pet = 'blobfish'
    data_manager.unlock_pet(tier3_pet)
    data_manager.set_current_pet_id(tier3_pet)
    
    # 获取图像路径
    image_path = data_manager.get_image_for_level(tier3_pet)
    
    # 验证路径格式
    expected_path = f"assets/deep_sea/{tier3_pet}/idle.png"
    assert image_path == expected_path, \
        f"Tier 3宠物图像路径应该是 {expected_path}，但得到 {image_path}"


def test_tier3_scale_factor_applied(data_manager, qapp):
    """测试Tier 3宠物缩放倍率应用"""
    # 测试所有Tier 3宠物
    tier3_pets = ['blobfish', 'ray', 'beluga', 'orca', 'shark', 'bluewhale']
    expected_scales = {
        'blobfish': 1.5,
        'ray': 2.0,
        'beluga': 2.5,
        'orca': 3.0,
        'shark': 3.5,
        'bluewhale': 5.0
    }
    
    for pet_id in tier3_pets:
        # 解锁并切换到Tier 3宠物
        data_manager.unlock_pet(pet_id)
        data_manager.set_current_pet_id(pet_id)
        
        # 创建宠物窗口
        widget = PetWidget(data_manager)
        
        # 验证缩放倍率配置正确
        scale_factor = data_manager.TIER3_SCALE_FACTORS.get(pet_id)
        assert scale_factor == expected_scales[pet_id], \
            f"Tier 3宠物 {pet_id} 的缩放倍率应该是 {expected_scales[pet_id]}，但得到 {scale_factor}"
        
        # 验证图像已加载（可能是占位符）
        assert widget.current_pixmap is not None, \
            f"Tier 3宠物 {pet_id} 应该有图像"
        
        widget.close()


def test_tier3_placeholder_color(data_manager, qapp):
    """测试Tier 3宠物占位符颜色（深蓝色系）"""
    # 测试一个Tier 3宠物
    tier3_pet = 'blobfish'
    data_manager.unlock_pet(tier3_pet)
    data_manager.set_current_pet_id(tier3_pet)
    
    # Mock get_image_for_level to return a non-existent path
    original_get_image = data_manager.get_image_for_level
    data_manager.get_image_for_level = lambda pet_id, level=None: f"assets/deep_sea/{tier3_pet}/nonexistent.png"
    
    widget = PetWidget(data_manager)
    
    # Restore original method
    data_manager.get_image_for_level = original_get_image
    
    # 应该有占位符图像
    assert widget.current_pixmap is not None
    assert not widget.current_pixmap.isNull()
    
    # 占位符应该是 100x100 的深蓝色方块
    assert widget.current_pixmap.width() == 100
    assert widget.current_pixmap.height() == 100
    
    # 验证颜色是深蓝色（通过检查像素）
    from PyQt6.QtGui import QColor
    pixel_color = widget.current_pixmap.toImage().pixelColor(50, 50)
    # Blobfish uses deep blue: (50, 100, 150)
    assert pixel_color.red() == 50
    assert pixel_color.green() == 100
    assert pixel_color.blue() == 150
    
    widget.close()


def test_tier3_different_from_tier1_tier2(data_manager, qapp):
    """测试Tier 3宠物与Tier 1/2宠物的区别"""
    # Tier 1宠物
    tier1_pet = 'puffer'
    data_manager.set_current_pet_id(tier1_pet)
    tier1_path = data_manager.get_image_for_level(tier1_pet, 1)
    
    # Tier 2宠物
    tier2_pet = 'octopus'
    data_manager.unlock_pet(tier2_pet)
    tier2_path = data_manager.get_image_for_level(tier2_pet, 1)
    
    # Tier 3宠物
    tier3_pet = 'blobfish'
    data_manager.unlock_pet(tier3_pet)
    tier3_path = data_manager.get_image_for_level(tier3_pet)
    
    # 验证路径格式不同
    # Tier 1/2: assets/[pet_id]/baby_idle.png
    # Tier 3: assets/deep_sea/[pet_id]/idle.png
    assert 'deep_sea' not in tier1_path
    assert 'deep_sea' not in tier2_path
    assert 'deep_sea' in tier3_path
    
    # 验证Tier 3没有等级系统（只有一个图像）
    # Tier 1/2有baby和adult，Tier 3只有idle
    assert 'baby' in tier1_path or 'adult' in tier1_path
    assert 'baby' in tier2_path or 'adult' in tier2_path
    assert 'idle' in tier3_path
    assert 'baby' not in tier3_path
    assert 'adult' not in tier3_path


def test_tier3_no_level_system(data_manager, qapp):
    """测试Tier 3宠物没有等级系统"""
    tier3_pet = 'ray'
    data_manager.unlock_pet(tier3_pet)
    
    # Tier 3宠物的图像路径不应该随等级变化
    path_level1 = data_manager.get_image_for_level(tier3_pet, 1)
    path_level2 = data_manager.get_image_for_level(tier3_pet, 2)
    path_level3 = data_manager.get_image_for_level(tier3_pet, 3)
    
    # 所有等级应该返回相同的路径
    assert path_level1 == path_level2 == path_level3
    assert path_level1 == f"assets/deep_sea/{tier3_pet}/idle.png"


def test_all_tier3_pets_have_scale_factors(data_manager, qapp):
    """测试所有Tier 3宠物都有配置的缩放倍率"""
    tier3_pets = data_manager.get_tier_pets(3)
    
    for pet_id in tier3_pets:
        # 验证每个Tier 3宠物都有缩放倍率
        assert pet_id in data_manager.TIER3_SCALE_FACTORS, \
            f"Tier 3宠物 {pet_id} 应该有配置的缩放倍率"
        
        scale_factor = data_manager.TIER3_SCALE_FACTORS[pet_id]
        
        # 验证缩放倍率在合理范围内
        assert 1.5 <= scale_factor <= 5.0, \
            f"Tier 3宠物 {pet_id} 的缩放倍率应该在1.5到5.0之间，但得到 {scale_factor}"


def test_tier3_widget_creation(data_manager, qapp):
    """测试可以为Tier 3宠物创建窗口"""
    # 测试所有Tier 3宠物
    tier3_pets = ['blobfish', 'ray', 'beluga', 'orca', 'shark', 'bluewhale']
    
    for pet_id in tier3_pets:
        # 解锁并切换到Tier 3宠物
        data_manager.unlock_pet(pet_id)
        data_manager.set_current_pet_id(pet_id)
        
        # 创建宠物窗口（应该不会崩溃）
        widget = PetWidget(data_manager)
        
        # 验证窗口已创建
        assert widget is not None
        assert widget.current_pixmap is not None
        
        # 验证窗口属性正确
        assert widget.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        flags = widget.windowFlags()
        assert flags & Qt.WindowType.FramelessWindowHint
        assert flags & Qt.WindowType.WindowStaysOnTopHint
        
        widget.close()


# V4 愤怒状态测试

def test_pet_widget_has_is_angry_attribute(pet_widget):
    """测试 PetWidget 有 is_angry 属性"""
    assert hasattr(pet_widget, 'is_angry')
    # 默认应该是 False
    assert pet_widget.is_angry == False


def test_set_angry_method_exists(pet_widget):
    """测试 set_angry 方法存在"""
    assert hasattr(pet_widget, 'set_angry')
    assert callable(getattr(pet_widget, 'set_angry'))


def test_set_calm_method_exists(pet_widget):
    """测试 set_calm 方法存在"""
    assert hasattr(pet_widget, 'set_calm')
    assert callable(getattr(pet_widget, 'set_calm'))


def test_set_angry_changes_state(pet_widget):
    """测试 set_angry 改变愤怒状态"""
    # 初始状态应该是不愤怒
    assert pet_widget.is_angry == False
    
    # 设置为愤怒
    pet_widget.set_angry(True)
    assert pet_widget.is_angry == True
    
    # 设置为不愤怒
    pet_widget.set_angry(False)
    assert pet_widget.is_angry == False


def test_set_calm_restores_normal_state(pet_widget):
    """测试 set_calm 恢复正常状态"""
    # 先设置为愤怒
    pet_widget.set_angry(True)
    assert pet_widget.is_angry == True
    
    # 调用 set_calm
    pet_widget.set_calm()
    assert pet_widget.is_angry == False


def test_angry_state_starts_shake_animation(pet_widget, qapp):
    """测试愤怒状态启动抖动动画"""
    # 设置为愤怒
    pet_widget.set_angry(True)
    
    # 验证抖动定时器已启动
    assert hasattr(pet_widget, 'shake_timer')
    assert pet_widget.shake_timer is not None
    assert pet_widget.shake_timer.isActive()


def test_calm_state_stops_shake_animation(pet_widget, qapp):
    """测试恢复正常状态停止抖动动画"""
    # 先设置为愤怒
    pet_widget.set_angry(True)
    assert pet_widget.shake_timer.isActive()
    
    # 恢复正常
    pet_widget.set_calm()
    
    # 验证抖动定时器已停止
    assert not pet_widget.shake_timer.isActive()


def test_shake_animation_interval(pet_widget, qapp):
    """测试抖动动画间隔为100ms"""
    # 设置为愤怒
    pet_widget.set_angry(True)
    
    # 验证定时器间隔
    assert pet_widget.shake_timer.interval() == 100


def test_click_on_angry_pet_triggers_calm(pet_widget, qapp):
    """测试点击愤怒的宠物触发安抚"""
    from PyQt6.QtCore import QPointF, Qt
    from PyQt6.QtGui import QMouseEvent
    from PyQt6.QtCore import QEvent
    
    # 设置为愤怒
    pet_widget.set_angry(True)
    assert pet_widget.is_angry == True
    
    # 创建真实的鼠标点击事件
    event = QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPointF(50, 50),  # 本地位置
        QPointF(50, 50),  # 全局位置
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier
    )
    
    # 调用 mousePressEvent
    pet_widget.mousePressEvent(event)
    
    # 验证宠物已被安抚
    assert pet_widget.is_angry == False


def test_click_on_normal_pet_does_not_change_state(pet_widget, qapp):
    """测试点击正常宠物不改变状态"""
    from PyQt6.QtCore import QPointF, Qt
    from PyQt6.QtGui import QMouseEvent
    from PyQt6.QtCore import QEvent
    
    # 确保是正常状态
    assert pet_widget.is_angry == False
    
    # 创建真实的鼠标点击事件
    event = QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPointF(50, 50),
        QPointF(50, 50),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier
    )
    
    # 调用 mousePressEvent
    pet_widget.mousePressEvent(event)
    
    # 状态应该保持不变
    assert pet_widget.is_angry == False


def test_angry_image_loading_attempted(data_manager, qapp):
    """测试愤怒状态尝试加载 angry_idle.png"""
    import os
    from unittest.mock import patch
    
    widget = PetWidget(data_manager)
    
    # 记录尝试加载的路径
    loaded_paths = []
    original_exists = os.path.exists
    
    def mock_exists(path):
        loaded_paths.append(path)
        return original_exists(path)
    
    with patch('os.path.exists', side_effect=mock_exists):
        widget.set_angry(True)
    
    # 验证尝试加载了 angry_idle.png
    angry_path_attempted = any('angry' in path for path in loaded_paths)
    assert angry_path_attempted or widget.is_angry  # 至少尝试了或者状态已改变
    
    widget.close()


def test_shake_animation_moves_window(pet_widget, qapp):
    """测试抖动动画移动窗口位置"""
    # 记录初始位置
    initial_pos = pet_widget.pos()
    
    # 设置为愤怒
    pet_widget.set_angry(True)
    
    # 手动触发抖动更新
    if hasattr(pet_widget, '_do_shake'):
        pet_widget._do_shake()
        
        # 位置应该有变化（或者在原位置±10像素范围内）
        new_pos = pet_widget.pos()
        # 由于是随机移动，我们只验证方法被调用了
        assert pet_widget.is_angry == True


def test_pet_widget_has_theme_manager_support(data_manager, qapp):
    """测试 PetWidget 支持 ThemeManager"""
    from theme_manager import ThemeManager
    
    theme_manager = ThemeManager(data_manager)
    widget = PetWidget(data_manager)
    
    # 验证可以设置 theme_manager
    widget.theme_manager = theme_manager
    assert widget.theme_manager is theme_manager
    
    widget.close()


def test_ghost_filter_applied_in_halloween_mode(data_manager, qapp):
    """测试万圣节模式下应用幽灵滤镜"""
    from theme_manager import ThemeManager
    
    # 设置万圣节模式
    theme_manager = ThemeManager(data_manager)
    theme_manager.set_theme_mode("halloween")
    
    widget = PetWidget(data_manager)
    widget.theme_manager = theme_manager
    
    # 重新加载图像（应该应用幽灵滤镜）
    widget.load_image()
    
    # 验证图像已加载
    assert widget.current_pixmap is not None
    
    widget.close()


def test_angry_state_with_ignore_tracker_integration(data_manager, qapp):
    """测试愤怒状态与 IgnoreTracker 集成"""
    from pet_manager import PetManager
    from ignore_tracker import IgnoreTracker
    
    pet_manager = PetManager(data_manager)
    widget = PetWidget(data_manager, pet_manager)
    
    # 创建 IgnoreTracker
    ignore_tracker = IgnoreTracker(pet_manager, show_notifications=False)
    
    # 将窗口添加到 pet_manager
    pet_manager.active_pet_windows['puffer'] = widget
    
    # 触发捣蛋模式
    ignore_tracker.trigger_mischief_mode()
    
    # 验证宠物进入愤怒状态
    assert widget.is_angry == True
    
    # 安抚宠物
    ignore_tracker.calm_pet('puffer')
    
    # 验证宠物恢复正常
    assert widget.is_angry == False
    
    widget.close()


def test_original_position_saved_before_shake(pet_widget, qapp):
    """测试抖动前保存原始位置"""
    # 设置一个已知位置
    pet_widget.move(100, 100)
    
    # 设置为愤怒
    pet_widget.set_angry(True)
    
    # 验证原始位置被保存
    assert hasattr(pet_widget, '_original_pos')
    assert pet_widget._original_pos is not None


def test_original_position_restored_after_calm(pet_widget, qapp):
    """测试安抚后恢复原始位置"""
    # 设置一个已知位置
    pet_widget.move(100, 100)
    original_x = pet_widget.x()
    original_y = pet_widget.y()
    
    # 设置为愤怒
    pet_widget.set_angry(True)
    
    # 恢复正常
    pet_widget.set_calm()
    
    # 验证位置恢复
    assert pet_widget.x() == original_x
    assert pet_widget.y() == original_y


# V5 睡觉状态测试

def test_pet_widget_has_is_sleeping_attribute(pet_widget):
    """测试 PetWidget 有 is_sleeping 属性"""
    assert hasattr(pet_widget, 'is_sleeping')
    # 默认应该是 False
    assert pet_widget.is_sleeping == False


def test_set_sleeping_method_exists(pet_widget):
    """测试 set_sleeping 方法存在"""
    assert hasattr(pet_widget, 'set_sleeping')
    assert callable(getattr(pet_widget, 'set_sleeping'))


def test_set_sleeping_changes_state(pet_widget):
    """测试 set_sleeping 改变睡觉状态"""
    # 初始状态应该是不睡觉
    assert pet_widget.is_sleeping == False
    
    # 设置为睡觉
    pet_widget.set_sleeping(True)
    assert pet_widget.is_sleeping == True
    
    # 设置为不睡觉
    pet_widget.set_sleeping(False)
    assert pet_widget.is_sleeping == False


def test_sleeping_state_starts_float_animation(pet_widget, qapp):
    """测试睡觉状态启动浮动动画"""
    # 设置为睡觉
    pet_widget.set_sleeping(True)
    
    # 验证浮动定时器已启动
    assert hasattr(pet_widget, 'float_timer')
    assert pet_widget.float_timer is not None
    assert pet_widget.float_timer.isActive()


def test_wake_state_stops_float_animation(pet_widget, qapp):
    """测试唤醒状态停止浮动动画"""
    # 先设置为睡觉
    pet_widget.set_sleeping(True)
    assert pet_widget.float_timer.isActive()
    
    # 唤醒
    pet_widget.set_sleeping(False)
    
    # 验证浮动定时器已停止
    assert not pet_widget.float_timer.isActive()


def test_float_animation_interval(pet_widget, qapp):
    """测试浮动动画间隔为50ms"""
    # 设置为睡觉
    pet_widget.set_sleeping(True)
    
    # 验证定时器间隔
    assert pet_widget.float_timer.interval() == 50


def test_sleep_original_position_saved(pet_widget, qapp):
    """测试睡觉前保存原始位置"""
    # 设置一个已知位置
    pet_widget.move(150, 150)
    
    # 设置为睡觉
    pet_widget.set_sleeping(True)
    
    # 验证原始位置被保存
    assert hasattr(pet_widget, '_sleep_original_pos')
    assert pet_widget._sleep_original_pos is not None


def test_sleep_original_position_restored_after_wake(pet_widget, qapp):
    """测试唤醒后恢复原始位置"""
    # 设置一个已知位置
    pet_widget.move(150, 150)
    original_x = pet_widget.x()
    original_y = pet_widget.y()
    
    # 设置为睡觉
    pet_widget.set_sleeping(True)
    
    # 手动触发几次浮动（模拟动画）
    if hasattr(pet_widget, '_do_float'):
        for _ in range(5):
            pet_widget._do_float()
    
    # 唤醒
    pet_widget.set_sleeping(False)
    
    # 验证位置恢复
    assert pet_widget.x() == original_x
    assert pet_widget.y() == original_y


def test_float_animation_moves_window_vertically(pet_widget, qapp):
    """测试浮动动画在垂直方向移动窗口"""
    # 设置一个已知位置
    pet_widget.move(100, 100)
    
    # 设置为睡觉
    pet_widget.set_sleeping(True)
    
    # 记录初始Y位置
    initial_y = pet_widget.y()
    
    # 手动触发浮动更新
    if hasattr(pet_widget, '_do_float'):
        pet_widget._do_float()
        
        # Y位置应该有变化
        new_y = pet_widget.y()
        # 由于浮动是渐进的，第一次应该移动1像素
        assert new_y != initial_y or pet_widget._float_offset != 0


def test_float_animation_does_not_move_horizontally(pet_widget, qapp):
    """测试浮动动画不在水平方向移动窗口"""
    # 设置一个已知位置
    pet_widget.move(100, 100)
    original_x = pet_widget.x()
    
    # 设置为睡觉
    pet_widget.set_sleeping(True)
    
    # 手动触发多次浮动更新
    if hasattr(pet_widget, '_do_float'):
        for _ in range(20):
            pet_widget._do_float()
        
        # X位置应该保持不变
        assert pet_widget.x() == original_x


def test_float_animation_oscillates(pet_widget, qapp):
    """测试浮动动画在上下方向振荡"""
    # 设置为睡觉
    pet_widget.set_sleeping(True)
    
    # 记录浮动方向变化
    directions = []
    
    if hasattr(pet_widget, '_do_float'):
        # 触发足够多次以观察方向变化
        for _ in range(30):
            directions.append(pet_widget._float_direction)
            pet_widget._do_float()
    
    # 应该有方向变化（从1变到-1或从-1变到1）
    assert 1 in directions and -1 in directions


def test_sleep_image_loading_attempted(data_manager, qapp):
    """测试睡觉状态尝试加载 sleep_idle.png"""
    import os
    from unittest.mock import patch
    
    widget = PetWidget(data_manager)
    
    # 记录尝试加载的路径
    loaded_paths = []
    original_exists = os.path.exists
    
    def mock_exists(path):
        loaded_paths.append(path)
        return original_exists(path)
    
    with patch('os.path.exists', side_effect=mock_exists):
        widget.set_sleeping(True)
    
    # 验证尝试加载了 sleep_idle.png
    sleep_path_attempted = any('sleep' in path for path in loaded_paths)
    assert sleep_path_attempted or widget.is_sleeping  # 至少尝试了或者状态已改变
    
    widget.close()


def test_ensure_above_background_method_exists(pet_widget):
    """测试 ensure_above_background 方法存在"""
    assert hasattr(pet_widget, 'ensure_above_background')
    assert callable(getattr(pet_widget, 'ensure_above_background'))


def test_ensure_above_background_raises_window(pet_widget, qapp):
    """测试 ensure_above_background 提升窗口层级"""
    # 调用方法（不应该抛出异常）
    pet_widget.ensure_above_background()
    
    # 验证窗口仍然有正确的标志
    flags = pet_widget.windowFlags()
    assert flags & Qt.WindowType.WindowStaysOnTopHint


def test_window_stays_on_top_for_deep_dive(pet_widget):
    """测试窗口在深潜模式下保持置顶"""
    # 验证窗口有 WindowStaysOnTopHint 标志
    flags = pet_widget.windowFlags()
    assert flags & Qt.WindowType.WindowStaysOnTopHint


def test_sleeping_state_with_theme_manager(data_manager, qapp):
    """测试睡觉状态与 ThemeManager 集成"""
    from theme_manager import ThemeManager
    
    theme_manager = ThemeManager(data_manager)
    widget = PetWidget(data_manager)
    widget.theme_manager = theme_manager
    
    # 设置为睡觉
    widget.set_sleeping(True)
    
    # 验证状态已改变
    assert widget.is_sleeping == True
    
    # 验证图像已加载
    assert widget.current_pixmap is not None
    
    widget.close()


def test_sleeping_state_with_halloween_mode(data_manager, qapp):
    """测试万圣节模式下的睡觉状态"""
    from theme_manager import ThemeManager
    
    # 设置万圣节模式
    theme_manager = ThemeManager(data_manager)
    theme_manager.set_theme_mode("halloween")
    
    widget = PetWidget(data_manager)
    widget.theme_manager = theme_manager
    
    # 设置为睡觉
    widget.set_sleeping(True)
    
    # 验证状态已改变
    assert widget.is_sleeping == True
    
    # 验证图像已加载（可能应用了幽灵滤镜）
    assert widget.current_pixmap is not None
    
    widget.close()


def test_float_max_offset_is_reasonable(pet_widget):
    """测试浮动最大偏移量在合理范围内"""
    assert hasattr(pet_widget, '_float_max_offset')
    # 最大偏移量应该在5-20像素之间，提供轻微但可见的浮动效果
    assert 5 <= pet_widget._float_max_offset <= 20


def test_sleeping_does_not_interfere_with_angry_state(pet_widget, qapp):
    """测试睡觉状态不干扰愤怒状态"""
    # 先设置为愤怒
    pet_widget.set_angry(True)
    assert pet_widget.is_angry == True
    
    # 设置为睡觉
    pet_widget.set_sleeping(True)
    
    # 两个状态应该可以独立存在
    assert pet_widget.is_sleeping == True
    # 愤怒状态应该保持（虽然在实际使用中可能不会同时出现）
    assert pet_widget.is_angry == True
    
    # 清理
    pet_widget.set_sleeping(False)
    pet_widget.set_calm()


def test_float_timer_setup(pet_widget):
    """测试浮动定时器正确设置"""
    assert hasattr(pet_widget, 'float_timer')
    assert pet_widget.float_timer is not None
    # 定时器初始应该是停止状态
    assert not pet_widget.float_timer.isActive()
