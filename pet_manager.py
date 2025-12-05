"""
pet_manager.py - V6 兼容层

此模块为向后兼容保留。
V6 版本简化为单宠物模式，复杂的多宠物管理已移除。
"""

from typing import Dict, Optional
from pet_core import PetWidget
from logic_growth import GrowthManager


class PetManager:
    """
    简化版宠物管理器
    
    V6 版本移除了：
    - 20只上限逻辑
    - 复杂的库存管理
    - 多窗口管理
    
    保留基本的宠物创建和管理功能。
    """
    
    def __init__(self, growth_manager: GrowthManager):
        self.growth_manager = growth_manager
        self.widgets: Dict[str, PetWidget] = {}
    
    def create_pet(self, pet_id: str) -> PetWidget:
        """创建宠物窗口"""
        if pet_id in self.widgets:
            return self.widgets[pet_id]
        
        widget = PetWidget(pet_id, self.growth_manager)
        self.widgets[pet_id] = widget
        return widget
    
    def get_pet(self, pet_id: str) -> Optional[PetWidget]:
        """获取宠物窗口"""
        return self.widgets.get(pet_id)
    
    def show_all(self):
        """显示所有宠物"""
        for widget in self.widgets.values():
            widget.show()
    
    def hide_all(self):
        """隐藏所有宠物"""
        for widget in self.widgets.values():
            widget.hide()
    
    def refresh_all(self):
        """刷新所有宠物显示"""
        for widget in self.widgets.values():
            widget.refresh_display()


__all__ = ['PetManager']
