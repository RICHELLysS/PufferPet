"""宠物选择窗口的单元测试"""
import pytest

# Skip entire module - pet_selector_window.py was removed in V6 cleanup
pytest.skip("V6清理：pet_selector_window.py 已移除", allow_module_level=True)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from data_manager import DataManager
from pet_core import PetWidget
from pet_selector_window import PetSelectorWindow


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


@pytest.fixture
def pet_selector(qapp, data_manager, pet_widget):
    """创建 PetSelectorWindow 实例"""
    selector = PetSelectorWindow(data_manager, pet_widget)
    yield selector
    selector.close()


def test_ui_elements_created(pet_selector):
    """测试UI元素创建"""
    # 验证窗口标题
    assert pet_selector.windowTitle() == "选择宠物"
    
    # 验证布局存在
    assert pet_selector.layout() is not None
    
    # 验证宠物按钮字典已创建
    assert hasattr(pet_selector, 'pet_buttons')
    assert isinstance(pet_selector.pet_buttons, dict)


def test_all_pets_displayed(pet_selector):
    """测试所有宠物都被显示"""
    # 应该显示河豚和水母
    assert 'puffer' in pet_selector.pet_buttons
    assert 'jelly' in pet_selector.pet_buttons
    
    # 每个宠物应该有卡片和按钮
    for pet_id in ['puffer', 'jelly']:
        card, button = pet_selector.pet_buttons[pet_id]
        assert card is not None
        assert button is not None


def test_unlocked_pet_display(pet_selector, data_manager):
    """测试已解锁宠物显示"""
    # 河豚默认解锁
    assert data_manager.is_pet_unlocked('puffer')
    
    # 获取河豚的按钮
    card, button = pet_selector.pet_buttons['puffer']
    
    # 按钮应该启用
    assert button.isEnabled()
    
    # 按钮文本应该是"选择"
    assert button.text() == "选择"


def test_locked_pet_display(pet_selector, data_manager):
    """测试未解锁宠物显示"""
    # 确保水母未解锁
    if 'jelly' in data_manager.get_unlocked_pets():
        data_manager.data['unlocked_pets'].remove('jelly')
    
    # 重新创建选择器以反映更新
    selector = PetSelectorWindow(data_manager, pet_selector.pet_widget)
    
    # 获取水母的按钮
    card, button = selector.pet_buttons['jelly']
    
    # 按钮应该禁用
    assert not button.isEnabled()
    
    # 按钮文本应该是"锁定"
    assert button.text() == "锁定"
    
    selector.close()


def test_locked_pet_access_control(pet_selector, data_manager, monkeypatch):
    """测试未解锁宠物访问控制"""
    # 确保水母未解锁
    if 'jelly' in data_manager.get_unlocked_pets():
        data_manager.data['unlocked_pets'].remove('jelly')
    
    # 记录当前宠物
    original_pet = data_manager.get_current_pet_id()
    
    # Mock QMessageBox to avoid Windows fatal exception in test environment
    from PyQt6.QtWidgets import QMessageBox
    monkeypatch.setattr(QMessageBox, 'information', lambda *args, **kwargs: None)
    
    # 尝试选择未解锁的宠物
    pet_selector.on_pet_selected('jelly')
    
    # 当前宠物不应该改变
    assert data_manager.get_current_pet_id() == original_pet


def test_current_pet_highlighted(pet_selector, data_manager):
    """测试当前宠物高亮"""
    # 获取当前宠物
    current_pet = data_manager.get_current_pet_id()
    
    # 更新显示
    pet_selector.update_display()
    
    # 获取当前宠物的卡片
    card, button = pet_selector.pet_buttons[current_pet]
    
    # 验证卡片样式包含高亮颜色
    style = card.styleSheet()
    assert '#4CAF50' in style or '#E8F5E9' in style


def test_selecting_current_pet_closes_window(pet_selector, data_manager):
    """测试选择当前宠物关闭窗口"""
    # 获取当前宠物
    current_pet = data_manager.get_current_pet_id()
    
    # 显示窗口
    pet_selector.show()
    assert pet_selector.isVisible()
    
    # 选择当前宠物
    pet_selector.on_pet_selected(current_pet)
    
    # 窗口应该关闭
    assert not pet_selector.isVisible()


def test_selecting_different_pet_switches_and_closes(pet_selector, data_manager, pet_widget):
    """测试选择不同宠物切换并关闭窗口"""
    # 解锁水母
    data_manager.unlock_pet('jelly')
    
    # 确保当前是河豚
    data_manager.set_current_pet_id('puffer')
    
    # 显示窗口
    pet_selector.show()
    assert pet_selector.isVisible()
    
    # 选择水母
    pet_selector.on_pet_selected('jelly')
    
    # 当前宠物应该切换到水母
    assert data_manager.get_current_pet_id() == 'jelly'
    
    # 窗口应该关闭
    assert not pet_selector.isVisible()


def test_create_pet_button_method_exists(pet_selector):
    """测试 create_pet_button 方法存在"""
    assert hasattr(pet_selector, 'create_pet_button')
    assert callable(getattr(pet_selector, 'create_pet_button'))


def test_on_pet_selected_method_exists(pet_selector):
    """测试 on_pet_selected 方法存在"""
    assert hasattr(pet_selector, 'on_pet_selected')
    assert callable(getattr(pet_selector, 'on_pet_selected'))


def test_update_display_method_exists(pet_selector):
    """测试 update_display 方法存在"""
    assert hasattr(pet_selector, 'update_display')
    assert callable(getattr(pet_selector, 'update_display'))


def test_pet_names_displayed(pet_selector):
    """测试宠物名称正确显示"""
    # 验证宠物名称映射
    assert PetSelectorWindow.PET_NAMES['puffer'] == '河豚'
    assert PetSelectorWindow.PET_NAMES['jelly'] == '水母'


def test_unlock_condition_displayed_for_locked_pets(data_manager, pet_widget, qapp):
    """测试未解锁宠物显示解锁条件"""
    # 确保水母未解锁
    if 'jelly' in data_manager.get_unlocked_pets():
        data_manager.data['unlocked_pets'].remove('jelly')
    
    # 创建选择器
    selector = PetSelectorWindow(data_manager, pet_widget)
    
    # 获取水母的卡片
    card, button = selector.pet_buttons['jelly']
    
    # 验证卡片存在（解锁条件应该在卡片中显示）
    assert card is not None
    
    selector.close()


def test_level_displayed_for_unlocked_pets(pet_selector, data_manager):
    """测试已解锁宠物显示等级"""
    # 河豚默认解锁
    assert data_manager.is_pet_unlocked('puffer')
    
    # 获取河豚的等级
    level = data_manager.get_level('puffer')
    
    # 验证等级大于0
    assert level > 0
    
    # 卡片应该存在
    card, button = pet_selector.pet_buttons['puffer']
    assert card is not None



# V3 版本测试：层级分组和8种生物

def test_all_8_pets_displayed_v3(data_manager, pet_widget, qapp):
    """测试所有Tier 1和Tier 2生物都被显示（V3）
    
    注意：Tier 3宠物不在宠物选择器中显示，因为它们通过宠物管理窗口管理
    """
    # 创建选择器
    selector = PetSelectorWindow(data_manager, pet_widget)
    
    # 验证所有Tier 1和Tier 2宠物都有按钮（不包括Tier 3）
    tier1_pets = set(data_manager.data.get('pet_tiers', {}).get('tier1', []))
    tier2_pets = set(data_manager.data.get('pet_tiers', {}).get('tier2', []))
    expected_pets = tier1_pets | tier2_pets
    displayed_pets = set(selector.pet_buttons.keys())
    
    assert displayed_pets == expected_pets, \
        f"应该显示所有Tier 1和Tier 2宠物，期望 {expected_pets}，但得到 {displayed_pets}"
    
    selector.close()


def test_tier_labels_displayed(data_manager, pet_widget, qapp):
    """测试层级标签正确显示（仅Tier 1和Tier 2）"""
    # 创建选择器
    selector = PetSelectorWindow(data_manager, pet_widget)
    
    # 验证每个显示的宠物都有层级标签（仅Tier 1和Tier 2）
    tier1_pets = data_manager.data.get('pet_tiers', {}).get('tier1', [])
    tier2_pets = data_manager.data.get('pet_tiers', {}).get('tier2', [])
    displayed_pets = tier1_pets + tier2_pets
    
    for pet_id in displayed_pets:
        tier = data_manager.get_pet_tier(pet_id)
        card, button = selector.pet_buttons[pet_id]
        
        # 查找层级标签
        from PyQt6.QtWidgets import QLabel
        tier_label_found = False
        expected_text = f"Tier {tier}"
        
        for label in card.findChildren(QLabel):
            if expected_text in label.text():
                tier_label_found = True
                break
        
        assert tier_label_found, f"宠物 {pet_id} 应该有 'Tier {tier}' 标签"
    
    selector.close()


def test_tier1_pets_displayed(data_manager, pet_widget, qapp):
    """测试Tier 1宠物正确显示"""
    # 创建选择器
    selector = PetSelectorWindow(data_manager, pet_widget)
    
    # 获取Tier 1宠物
    tier1_pets = data_manager.get_tier_pets(1)
    
    # 验证所有Tier 1宠物都被显示
    for pet_id in tier1_pets:
        assert pet_id in selector.pet_buttons, f"Tier 1宠物 {pet_id} 应该被显示"
        
        # 验证Tier 1宠物默认已解锁
        assert data_manager.is_pet_unlocked(pet_id), f"Tier 1宠物 {pet_id} 应该默认解锁"
    
    selector.close()


def test_tier2_pets_displayed(data_manager, pet_widget, qapp):
    """测试Tier 2宠物正确显示"""
    # 创建选择器
    selector = PetSelectorWindow(data_manager, pet_widget)
    
    # 获取Tier 2宠物
    tier2_pets = data_manager.get_tier_pets(2)
    
    # 验证所有Tier 2宠物都被显示
    for pet_id in tier2_pets:
        assert pet_id in selector.pet_buttons, f"Tier 2宠物 {pet_id} 应该被显示"
    
    selector.close()


def test_tier2_unlock_hint_displayed(data_manager, pet_widget, qapp):
    """测试Tier 2宠物显示"通过奇遇捕获"提示"""
    # 创建选择器
    selector = PetSelectorWindow(data_manager, pet_widget)
    
    # 获取Tier 2宠物
    tier2_pets = data_manager.get_tier_pets(2)
    
    for pet_id in tier2_pets:
        # 确保宠物未解锁
        if data_manager.is_pet_unlocked(pet_id):
            continue
        
        card, button = selector.pet_buttons[pet_id]
        
        # 查找解锁条件文本
        from PyQt6.QtWidgets import QLabel
        unlock_hint_found = False
        expected_hints = ["通过奇遇捕获", "奇遇", "捕获"]
        
        for label in card.findChildren(QLabel):
            text = label.text()
            if any(hint in text for hint in expected_hints):
                unlock_hint_found = True
                break
        
        assert unlock_hint_found, \
            f"未解锁的Tier 2宠物 {pet_id} 应该显示'通过奇遇捕获'提示"
    
    selector.close()


def test_pet_names_v3(pet_selector):
    """测试V3版本所有宠物名称正确映射"""
    # 验证所有8种宠物的名称映射
    expected_names = {
        'puffer': '河豚',
        'jelly': '水母',
        'starfish': '海星',
        'crab': '螃蟹',
        'octopus': '八爪鱼',
        'ribbon': '带鱼',
        'sunfish': '翻车鱼',
        'angler': '灯笼鱼'
    }
    
    for pet_id, expected_name in expected_names.items():
        assert PetSelectorWindow.PET_NAMES[pet_id] == expected_name, \
            f"宠物 {pet_id} 的名称应该是 {expected_name}"


def test_tier_grouping_layout(data_manager, pet_widget, qapp):
    """测试层级分组布局"""
    # 创建选择器
    selector = PetSelectorWindow(data_manager, pet_widget)
    
    # 验证布局中包含层级标签
    from PyQt6.QtWidgets import QLabel
    layout = selector.layout()
    
    tier1_label_found = False
    tier2_label_found = False
    
    # 遍历布局中的所有widget
    for i in range(layout.count()):
        widget = layout.itemAt(i).widget()
        if isinstance(widget, QLabel):
            text = widget.text()
            if "Tier 1" in text:
                tier1_label_found = True
            if "Tier 2" in text:
                tier2_label_found = True
    
    assert tier1_label_found, "应该有Tier 1分组标签"
    assert tier2_label_found, "应该有Tier 2分组标签"
    
    selector.close()


def test_tier2_pet_locked_by_default(data_manager, pet_widget, qapp):
    """测试Tier 2宠物默认未解锁"""
    # 创建选择器
    selector = PetSelectorWindow(data_manager, pet_widget)
    
    # 获取Tier 2宠物
    tier2_pets = data_manager.get_tier_pets(2)
    
    for pet_id in tier2_pets:
        # Tier 2宠物默认应该未解锁
        card, button = selector.pet_buttons[pet_id]
        
        # 按钮应该禁用
        assert not button.isEnabled(), f"Tier 2宠物 {pet_id} 的按钮应该禁用"
        
        # 按钮文本应该是"锁定"
        assert button.text() == "锁定", f"Tier 2宠物 {pet_id} 的按钮文本应该是'锁定'"
    
    selector.close()
