"""
V6 最终验证测试

验证:
1. 完整流程：启动 → 完成任务 → 进化
2. 图像回退机制
3. 昼夜模式
"""
import os
import sys
import tempfile
import pytest

# 确保可以导入项目模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from logic_growth import GrowthManager
from pet_core import PetWidget
from time_manager import TimeManager
from theme_manager import ThemeManager


@pytest.fixture(scope="module")
def qapp():
    """创建 QApplication 实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestV6CompleteFlow:
    """V6 完整流程测试"""
    
    def test_startup_to_evolution_flow(self, qapp, tmp_path):
        """测试完整流程：启动 → 完成任务 → 进化"""
        data_file = tmp_path / "test_data.json"
        gm = GrowthManager(str(data_file))
        
        # 1. 初始状态：休眠
        assert gm.get_state('puffer') == 0, "初始状态应为休眠(0)"
        assert gm.get_progress('puffer') == 0, "初始进度应为0"
        assert gm.is_dormant('puffer'), "应处于休眠状态"
        
        # 2. 创建宠物窗口
        widget = PetWidget('puffer', gm)
        assert widget.is_dormant, "窗口应显示休眠状态"
        
        # 3. 完成第1个任务 → 进化为幼年
        new_state = gm.complete_task('puffer')
        assert new_state == 1, "完成1个任务后应进化为幼年(1)"
        assert gm.get_progress('puffer') == 1
        
        # 刷新显示
        widget.refresh_display()
        assert not widget.is_dormant, "幼年状态不应显示休眠"
        
        # 4. 完成第2个任务 → 仍为幼年
        new_state = gm.complete_task('puffer')
        assert new_state == 1, "完成2个任务后仍为幼年(1)"
        
        # 5. 完成第3个任务 → 进化为成年
        new_state = gm.complete_task('puffer')
        assert new_state == 2, "完成3个任务后应进化为成年(2)"
        assert gm.get_progress('puffer') == 3
        
        # 6. 验证图像阶段
        assert gm.get_image_stage('puffer') == 'adult', "成年应使用adult图像"
        
        widget.close()
        print("✓ 完整流程测试通过")
    
    def test_reset_cycle(self, qapp, tmp_path):
        """测试周期重置"""
        data_file = tmp_path / "test_data.json"
        gm = GrowthManager(str(data_file))
        
        # 进化到成年
        for _ in range(3):
            gm.complete_task('puffer')
        assert gm.get_state('puffer') == 2
        
        # 重置
        gm.reset_cycle('puffer')
        assert gm.get_state('puffer') == 0, "重置后应回到休眠(0)"
        assert gm.get_progress('puffer') == 0, "重置后进度应为0"
        
        print("✓ 周期重置测试通过")


class TestV6ImageFallback:
    """V6 图像回退机制测试"""
    
    def test_placeholder_for_unknown_pet(self, qapp, tmp_path):
        """测试未知宠物使用占位符"""
        data_file = tmp_path / "test_data.json"
        gm = GrowthManager(str(data_file))
        
        widget = PetWidget('unknown_pet_xyz', gm)
        
        # 应该创建占位符
        assert widget.current_pixmap is not None
        assert not widget.current_pixmap.isNull()
        assert widget.current_pixmap.width() == 128
        assert widget.current_pixmap.height() == 128
        
        widget.close()
        print("✓ 图像回退测试通过")
    
    def test_existing_pet_loads_image(self, qapp, tmp_path):
        """测试已存在的宠物加载图像"""
        data_file = tmp_path / "test_data.json"
        gm = GrowthManager(str(data_file))
        
        widget = PetWidget('puffer', gm)
        
        # 应该加载图像或占位符
        assert widget.current_pixmap is not None
        assert not widget.current_pixmap.isNull()
        
        widget.close()
        print("✓ 图像加载测试通过")


class TestV6DayNightMode:
    """V6 昼夜模式测试"""
    
    def test_time_determination(self, qapp):
        """测试时间判定"""
        tm = TimeManager()
        
        # 白天时段 (6-17)
        for hour in [6, 12, 17]:
            period = tm._determine_period(hour)
            assert period == "day", f"小时{hour}应判定为白天"
        
        # 黑夜时段 (0-5, 18-23)
        for hour in [0, 5, 18, 23]:
            period = tm._determine_period(hour)
            assert period == "night", f"小时{hour}应判定为黑夜"
        
        tm.stop()
        print("✓ 时间判定测试通过")
    
    def test_mode_switching(self, qapp):
        """测试模式切换"""
        theme_mgr = ThemeManager()
        tm = TimeManager(theme_manager=theme_mgr)
        
        # 切换到白天
        tm.switch_to_day()
        assert tm.get_current_period() == "day"
        assert theme_mgr.get_theme_mode() == "normal"
        
        # 切换到黑夜
        tm.switch_to_night()
        assert tm.get_current_period() == "night"
        assert theme_mgr.get_theme_mode() == "halloween"
        
        tm.stop()
        print("✓ 模式切换测试通过")
    
    def test_auto_sync_control(self, qapp):
        """测试自动同步控制"""
        tm = TimeManager()
        
        # 默认启用自动同步
        assert tm.auto_sync_enabled
        
        # 禁用自动同步
        tm.set_auto_sync(False)
        assert not tm.auto_sync_enabled
        
        # 禁用时可以手动切换
        tm.switch_to_day()
        initial = tm.get_current_period()
        tm.manual_toggle()
        assert tm.get_current_period() != initial
        
        # 启用自动同步
        tm.set_auto_sync(True)
        assert tm.auto_sync_enabled
        
        # 启用时手动切换被忽略
        initial = tm.get_current_period()
        tm.manual_toggle()
        assert tm.get_current_period() == initial
        
        tm.stop()
        print("✓ 自动同步控制测试通过")


class TestV6DataPersistence:
    """V6 数据持久化测试"""
    
    def test_save_and_load(self, qapp, tmp_path):
        """测试数据保存和加载"""
        data_file = tmp_path / "test_data.json"
        
        # 创建并修改数据
        gm1 = GrowthManager(str(data_file))
        gm1.complete_task('puffer')
        gm1.complete_task('puffer')
        gm1.save()
        
        # 重新加载
        gm2 = GrowthManager(str(data_file))
        assert gm2.get_state('puffer') == gm1.get_state('puffer')
        assert gm2.get_progress('puffer') == gm1.get_progress('puffer')
        
        print("✓ 数据持久化测试通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
