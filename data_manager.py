"""
data_manager.py - V6 兼容层

此模块为向后兼容保留，实际功能已迁移到 logic_growth.py
新代码应直接使用 GrowthManager
"""

from logic_growth import GrowthManager

# 为向后兼容导出 GrowthManager 作为 DataManager
DataManager = GrowthManager

__all__ = ['DataManager', 'GrowthManager']
