"""宠物管理窗口的单元测试"""
import pytest

# Skip entire module - pet_management_window.py was removed in V6 cleanup
pytest.skip("V6清理：pet_management_window.py 已移除", allow_module_level=True)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from data_manager import DataManager
from pet_manager import PetManager
from pet_management_window import PetManagementWindow


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
    dm = DataManager(str(data_file))
    # 解锁一些宠物用于测试
    dm.unlock_pet('octopus')
    dm.unlock_pet('blobfish')
    return dm


@pytest.fixture
def pet_manager(data_manager):
    """创建 PetManager 实例"""
    return PetManager(data_manager)


@pytest.fixture
def management_window(qapp, data_manager, pet_manager):
    """创建 PetManagementWindow 实例"""
    window = PetManagementWindow(data_manager, pet_manager)
    yield window
    window.close()


def test_ui_elements_created(management_window):
    """测试UI元素创建"""
    # 验证窗口标题
    assert management_window.windowTitle() == "宠物管理"
    
    # 验证布局存在
    assert management_window.layout() is not None
    
    # 验证库存列表存在
    assert management_window.inventory_list is not None
    
    # 验证活跃列表存在
    assert management_window.active_list is not None
    
    # 验证标签存在
    assert management_window.inventory_label is not None
    assert management_window.active_label is not None


def test_inventory_status_display(management_window, data_manager):
    """测试库存状态显示"""
    # 获取库存状态文本
    status_text = management_window.inventory_label.text()
    
    # 应该包含库存数量和上限
    unlocked_count = len(data_manager.get_unlocked_pets())
    max_inventory = data_manager.MAX_INVENTORY
    
    assert f"{unlocked_count}/{max_inventory}" in status_text
    assert "库存宠物" in status_text


def test_active_status_display(management_window, data_manager):
    """测试活跃状态显示"""
    # 获取活跃状态文本
    status_text = management_window.active_label.text()
    
    # 应该包含活跃数量和上限
    active_count = len(data_manager.get_active_pets())
    max_active = data_manager.MAX_ACTIVE
    
    assert f"{active_count}/{max_active}" in status_text
    assert "活跃宠物" in status_text


def test_refresh_lists_method_exists(management_window):
    """测试 refresh_lists 方法存在"""
    assert hasattr(management_window, 'refresh_lists')
    assert callable(getattr(management_window, 'refresh_lists'))


def test_refresh_lists_populates_inventory(management_window, data_manager):
    """测试刷新列表填充库存"""
    # 刷新列表
    management_window.refresh_lists()
    
    # 获取库存和活跃宠物
    unlocked_pets = data_manager.get_unlocked_pets()
    active_pets = data_manager.get_active_pets()
    
    # 库存列表应该显示不在活跃列表中的宠物
    inventory_count = len(unlocked_pets) - len(active_pets)
    assert management_window.inventory_list.count() == inventory_count


def test_refresh_lists_populates_active(management_window, data_manager):
    """测试刷新列表填充活跃宠物"""
    # 刷新列表
    management_window.refresh_lists()
    
    # 活跃列表应该显示所有活跃宠物
    active_pets = data_manager.get_active_pets()
    assert management_window.active_list.count() == len(active_pets)


def test_summon_pet_success(management_window, data_manager, pet_manager, monkeypatch):
    """测试成功召唤宠物"""
    # Mock QMessageBox to avoid Windows fatal exception
    from PyQt6.QtWidgets import QMessageBox
    monkeypatch.setattr(QMessageBox, 'warning', lambda *args, **kwargs: None)
    
    # 确保有宠物在库存中但不在活跃列表
    # 先清空活跃列表
    data_manager.set_active_pets([])
    management_window.refresh_lists()
    
    # 选择第一个库存宠物
    if management_window.inventory_list.count() > 0:
        management_window.inventory_list.setCurrentRow(0)
        pet_id = management_window.inventory_list.item(0).data(Qt.ItemDataRole.UserRole)
        
        # 记录召唤前的活跃宠物数量
        active_count_before = len(data_manager.get_active_pets())
        
        # 召唤宠物
        management_window.on_summon_pet()
        
        # 活跃宠物数量应该增加
        active_count_after = len(data_manager.get_active_pets())
        assert active_count_after == active_count_before + 1
        
        # 宠物应该在活跃列表中
        assert pet_id in data_manager.get_active_pets()


def test_summon_pet_when_active_full(management_window, data_manager, pet_manager, monkeypatch):
    """测试活跃宠物已满时召唤失败"""
    # Mock QMessageBox
    warning_called = []
    def mock_warning(*args, **kwargs):
        warning_called.append(True)
    
    from PyQt6.QtWidgets import QMessageBox
    monkeypatch.setattr(QMessageBox, 'warning', mock_warning)
    
    # 填满活跃列表
    unlocked_pets = data_manager.get_unlocked_pets()
    active_pets = unlocked_pets[:data_manager.MAX_ACTIVE]
    data_manager.set_active_pets(active_pets)
    
    # 如果还有库存宠物
    if len(unlocked_pets) > data_manager.MAX_ACTIVE:
        management_window.refresh_lists()
        
        # 选择库存中的宠物
        if management_window.inventory_list.count() > 0:
            management_window.inventory_list.setCurrentRow(0)
            
            # 尝试召唤
            management_window.on_summon_pet()
            
            # 应该显示警告
            assert len(warning_called) > 0


def test_summon_pet_no_selection(management_window, monkeypatch):
    """测试未选择宠物时召唤失败"""
    # Mock QMessageBox
    warning_called = []
    def mock_warning(*args, **kwargs):
        warning_called.append(True)
    
    from PyQt6.QtWidgets import QMessageBox
    monkeypatch.setattr(QMessageBox, 'warning', mock_warning)
    
    # 不选择任何宠物
    management_window.inventory_list.clearSelection()
    
    # 尝试召唤
    management_window.on_summon_pet()
    
    # 应该显示警告
    assert len(warning_called) > 0


def test_dive_pet_success(management_window, data_manager, pet_manager, monkeypatch):
    """测试成功让宠物潜水"""
    # Mock QMessageBox
    from PyQt6.QtWidgets import QMessageBox
    monkeypatch.setattr(QMessageBox, 'warning', lambda *args, **kwargs: None)
    
    # 确保有活跃宠物
    active_pets = data_manager.get_active_pets()
    if not active_pets:
        # 激活一只宠物
        unlocked_pets = data_manager.get_unlocked_pets()
        if unlocked_pets:
            data_manager.set_active_pets([unlocked_pets[0]])
            active_pets = data_manager.get_active_pets()
    
    if active_pets:
        management_window.refresh_lists()
        
        # 选择第一个活跃宠物
        management_window.active_list.setCurrentRow(0)
        pet_id = management_window.active_list.item(0).data(Qt.ItemDataRole.UserRole)
        
        # 记录潜水前的活跃宠物数量
        active_count_before = len(data_manager.get_active_pets())
        
        # 让宠物潜水
        management_window.on_dive_pet()
        
        # 活跃宠物数量应该减少
        active_count_after = len(data_manager.get_active_pets())
        assert active_count_after == active_count_before - 1
        
        # 宠物不应该在活跃列表中
        assert pet_id not in data_manager.get_active_pets()
        
        # 宠物应该还在库存中
        assert pet_id in data_manager.get_unlocked_pets()


def test_dive_pet_no_selection(management_window, monkeypatch):
    """测试未选择宠物时潜水失败"""
    # Mock QMessageBox
    warning_called = []
    def mock_warning(*args, **kwargs):
        warning_called.append(True)
    
    from PyQt6.QtWidgets import QMessageBox
    monkeypatch.setattr(QMessageBox, 'warning', mock_warning)
    
    # 不选择任何宠物
    management_window.active_list.clearSelection()
    
    # 尝试潜水
    management_window.on_dive_pet()
    
    # 应该显示警告
    assert len(warning_called) > 0


def test_release_pet_success(management_window, data_manager, pet_manager, monkeypatch):
    """测试成功放生宠物"""
    # Mock QMessageBox
    from PyQt6.QtWidgets import QMessageBox
    
    # Mock question to return Yes
    monkeypatch.setattr(
        QMessageBox, 
        'question', 
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes
    )
    
    # 确保有宠物可以放生（不在活跃列表中）
    unlocked_pets = data_manager.get_unlocked_pets()
    active_pets = data_manager.get_active_pets()
    
    # 找一个不在活跃列表中的宠物
    inventory_pets = [p for p in unlocked_pets if p not in active_pets]
    
    if inventory_pets:
        pet_to_release = inventory_pets[0]
        
        management_window.refresh_lists()
        
        # 在库存列表中找到这个宠物
        for i in range(management_window.inventory_list.count()):
            item = management_window.inventory_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == pet_to_release:
                management_window.inventory_list.setCurrentRow(i)
                break
        
        # 记录放生前的宠物数量
        pet_count_before = len(data_manager.get_unlocked_pets())
        
        # 放生宠物
        management_window.on_release_pet()
        
        # 宠物数量应该减少
        pet_count_after = len(data_manager.get_unlocked_pets())
        assert pet_count_after == pet_count_before - 1
        
        # 宠物不应该在库存中
        assert pet_to_release not in data_manager.get_unlocked_pets()
        
        # 宠物数据应该被删除
        assert pet_to_release not in data_manager.data['pets_data']


def test_release_pet_cancelled(management_window, data_manager, monkeypatch):
    """测试取消放生宠物"""
    # Mock QMessageBox question to return No
    from PyQt6.QtWidgets import QMessageBox
    monkeypatch.setattr(
        QMessageBox, 
        'question', 
        lambda *args, **kwargs: QMessageBox.StandardButton.No
    )
    
    # 确保有宠物可以选择
    unlocked_pets = data_manager.get_unlocked_pets()
    if unlocked_pets:
        management_window.refresh_lists()
        
        # 选择第一个库存宠物
        if management_window.inventory_list.count() > 0:
            management_window.inventory_list.setCurrentRow(0)
            pet_id = management_window.inventory_list.item(0).data(Qt.ItemDataRole.UserRole)
            
            # 记录放生前的宠物数量
            pet_count_before = len(data_manager.get_unlocked_pets())
            
            # 尝试放生但取消
            management_window.on_release_pet()
            
            # 宠物数量不应该改变
            pet_count_after = len(data_manager.get_unlocked_pets())
            assert pet_count_after == pet_count_before
            
            # 宠物应该还在库存中
            assert pet_id in data_manager.get_unlocked_pets()


def test_release_pet_no_selection(management_window, monkeypatch):
    """测试未选择宠物时放生失败"""
    # Mock QMessageBox
    warning_called = []
    def mock_warning(*args, **kwargs):
        warning_called.append(True)
    
    from PyQt6.QtWidgets import QMessageBox
    monkeypatch.setattr(QMessageBox, 'warning', mock_warning)
    
    # 不选择任何宠物
    management_window.inventory_list.clearSelection()
    management_window.active_list.clearSelection()
    
    # 尝试放生
    management_window.on_release_pet()
    
    # 应该显示警告
    assert len(warning_called) > 0


def test_pet_display_with_tier_and_level(management_window, data_manager):
    """测试宠物显示包含层级和等级信息"""
    management_window.refresh_lists()
    
    # 检查库存列表中的宠物
    for i in range(management_window.inventory_list.count()):
        item = management_window.inventory_list.item(i)
        text = item.text()
        
        # 应该包含 Tier 和 Lv. 信息
        assert "Tier" in text
        assert "Lv." in text


def test_active_list_updates_after_summon(management_window, data_manager, pet_manager, monkeypatch):
    """测试召唤后活跃列表更新"""
    # Mock QMessageBox
    from PyQt6.QtWidgets import QMessageBox
    monkeypatch.setattr(QMessageBox, 'warning', lambda *args, **kwargs: None)
    
    # 清空活跃列表
    data_manager.set_active_pets([])
    management_window.refresh_lists()
    
    # 记录初始活跃列表数量
    initial_active_count = management_window.active_list.count()
    
    # 召唤一只宠物
    if management_window.inventory_list.count() > 0:
        management_window.inventory_list.setCurrentRow(0)
        management_window.on_summon_pet()
        
        # 活跃列表数量应该增加
        assert management_window.active_list.count() == initial_active_count + 1


def test_inventory_list_updates_after_dive(management_window, data_manager, pet_manager, monkeypatch):
    """测试潜水后库存列表更新"""
    # Mock QMessageBox
    from PyQt6.QtWidgets import QMessageBox
    monkeypatch.setattr(QMessageBox, 'warning', lambda *args, **kwargs: None)
    
    # 确保有活跃宠物
    unlocked_pets = data_manager.get_unlocked_pets()
    if unlocked_pets:
        data_manager.set_active_pets([unlocked_pets[0]])
        management_window.refresh_lists()
        
        # 记录初始库存列表数量
        initial_inventory_count = management_window.inventory_list.count()
        
        # 让宠物潜水
        if management_window.active_list.count() > 0:
            management_window.active_list.setCurrentRow(0)
            management_window.on_dive_pet()
            
            # 库存列表数量应该增加
            assert management_window.inventory_list.count() == initial_inventory_count + 1


def test_status_labels_update_after_operations(management_window, data_manager, pet_manager, monkeypatch):
    """测试操作后状态标签更新"""
    # Mock QMessageBox
    from PyQt6.QtWidgets import QMessageBox
    monkeypatch.setattr(QMessageBox, 'warning', lambda *args, **kwargs: None)
    
    # 清空活跃列表
    data_manager.set_active_pets([])
    management_window.refresh_lists()
    
    # 获取初始状态文本
    initial_active_text = management_window.active_label.text()
    
    # 召唤一只宠物
    if management_window.inventory_list.count() > 0:
        management_window.inventory_list.setCurrentRow(0)
        management_window.on_summon_pet()
        
        # 状态文本应该更新
        updated_active_text = management_window.active_label.text()
        assert updated_active_text != initial_active_text


def test_on_summon_pet_method_exists(management_window):
    """测试 on_summon_pet 方法存在"""
    assert hasattr(management_window, 'on_summon_pet')
    assert callable(getattr(management_window, 'on_summon_pet'))


def test_on_dive_pet_method_exists(management_window):
    """测试 on_dive_pet 方法存在"""
    assert hasattr(management_window, 'on_dive_pet')
    assert callable(getattr(management_window, 'on_dive_pet'))


def test_on_release_pet_method_exists(management_window):
    """测试 on_release_pet 方法存在"""
    assert hasattr(management_window, 'on_release_pet')
    assert callable(getattr(management_window, 'on_release_pet'))
