"""宠物管理器单元测试 - V6 简化版"""
import os
import tempfile
import pytest
from PyQt6.QtWidgets import QApplication
from logic_growth import GrowthManager
from pet_manager import PetManager


@pytest.fixture
def app():
    """创建 QApplication 实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


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
def growth_manager(temp_data_file):
    """创建成长管理器实例"""
    return GrowthManager(data_file=temp_data_file)


@pytest.fixture
def pet_manager(growth_manager):
    """创建宠物管理器实例"""
    return PetManager(growth_manager)


def test_pet_manager_initialization(pet_manager, growth_manager):
    """测试宠物管理器初始化"""
    assert pet_manager.growth_manager == growth_manager
    assert pet_manager.widgets == {}


def test_create_pet(app, pet_manager):
    """测试创建宠物窗口"""
    widget = pet_manager.create_pet("puffer")
    
    assert widget is not None
    assert "puffer" in pet_manager.widgets
    assert pet_manager.widgets["puffer"] == widget
    
    # 清理
    widget.close()


def test_create_pet_returns_existing(app, pet_manager):
    """测试创建已存在的宠物返回现有窗口"""
    widget1 = pet_manager.create_pet("puffer")
    widget2 = pet_manager.create_pet("puffer")
    
    assert widget1 == widget2
    assert len(pet_manager.widgets) == 1
    
    # 清理
    widget1.close()


def test_get_pet(app, pet_manager):
    """测试获取宠物窗口"""
    # 未创建时返回 None
    assert pet_manager.get_pet("puffer") is None
    
    # 创建后返回窗口
    widget = pet_manager.create_pet("puffer")
    assert pet_manager.get_pet("puffer") == widget
    
    # 清理
    widget.close()


def test_show_all(app, pet_manager):
    """测试显示所有宠物"""
    widget1 = pet_manager.create_pet("puffer")
    widget2 = pet_manager.create_pet("jelly")
    
    pet_manager.show_all()
    
    assert widget1.isVisible()
    assert widget2.isVisible()
    
    # 清理
    widget1.close()
    widget2.close()


def test_hide_all(app, pet_manager):
    """测试隐藏所有宠物"""
    widget1 = pet_manager.create_pet("puffer")
    widget2 = pet_manager.create_pet("jelly")
    
    pet_manager.show_all()
    pet_manager.hide_all()
    
    assert not widget1.isVisible()
    assert not widget2.isVisible()
    
    # 清理
    widget1.close()
    widget2.close()


def test_refresh_all(app, pet_manager):
    """测试刷新所有宠物显示"""
    widget = pet_manager.create_pet("puffer")
    
    # 调用 refresh_all 不应抛出异常
    pet_manager.refresh_all()
    
    # 清理
    widget.close()
