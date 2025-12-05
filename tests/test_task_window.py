"""任务窗口单元测试"""
import os
import sys
import tempfile
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from data_manager import DataManager
from pet_core import PetWidget
from task_window import TaskWindow


@pytest.fixture(scope="module")
def qapp():
    """创建 QApplication 实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
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


def test_ui_elements_creation(qapp, temp_data_file):
    """测试 UI 元素创建
    
    验证任务窗口创建了所有必需的 UI 元素：
    - 进度标签
    - 三个任务复选框
    """
    # 创建数据管理器
    dm = DataManager(data_file=temp_data_file)
    
    # 创建主窗口和任务窗口
    pet_widget = PetWidget(dm)
    task_window = TaskWindow(dm, pet_widget)
    
    # 验证进度标签存在
    assert task_window.progress_label is not None
    assert task_window.progress_label.text() == "0/3"
    
    # 验证三个复选框存在
    assert len(task_window.checkboxes) == 3
    
    # 验证复选框文本
    expected_texts = ["喝一杯水", "伸个懒腰", "专注工作30分钟"]
    for i, checkbox in enumerate(task_window.checkboxes):
        assert checkbox.text() == expected_texts[i]
    
    # 清理
    task_window.close()
    pet_widget.close()


def test_checkbox_interaction_check(qapp, temp_data_file):
    """测试复选框交互 - 勾选
    
    验证勾选复选框时：
    - 任务完成数增加
    - 进度标签更新
    - 任务状态保存
    """
    # 创建数据管理器
    dm = DataManager(data_file=temp_data_file)
    
    # 创建主窗口和任务窗口
    pet_widget = PetWidget(dm)
    task_window = TaskWindow(dm, pet_widget)
    
    # 初始状态
    assert dm.get_tasks_completed() == 0
    assert task_window.progress_label.text() == "0/3"
    
    # 勾选第一个复选框
    task_window.checkboxes[0].setChecked(True)
    
    # 验证任务完成数增加
    assert dm.get_tasks_completed() == 1
    assert task_window.progress_label.text() == "1/3"
    current_pet = dm.get_current_pet_id()
    assert dm.data['pets_data'][current_pet]['task_states'][0] is True
    
    # 清理
    task_window.close()
    pet_widget.close()


def test_checkbox_interaction_uncheck(qapp, temp_data_file):
    """测试复选框交互 - 取消勾选
    
    验证取消勾选复选框时：
    - 任务完成数减少
    - 进度标签更新
    - 任务状态保存
    """
    # 创建数据管理器
    dm = DataManager(data_file=temp_data_file)
    current_pet = dm.get_current_pet_id()
    dm.data['pets_data'][current_pet]['tasks_completed_today'] = 2
    dm.data['pets_data'][current_pet]['task_states'] = [True, True, False]
    
    # 创建主窗口和任务窗口
    pet_widget = PetWidget(dm)
    task_window = TaskWindow(dm, pet_widget)
    
    # 初始状态
    assert dm.get_tasks_completed() == 2
    assert task_window.progress_label.text() == "2/3"
    
    # 取消勾选第一个复选框
    task_window.checkboxes[0].setChecked(False)
    
    # 验证任务完成数减少
    assert dm.get_tasks_completed() == 1
    assert task_window.progress_label.text() == "1/3"
    assert dm.data['pets_data'][current_pet]['task_states'][0] is False
    
    # 清理
    task_window.close()
    pet_widget.close()


def test_checkbox_state_initialization(qapp, temp_data_file):
    """测试复选框状态初始化
    
    验证任务窗口打开时，复选框状态与保存的任务状态一致
    """
    # 创建数据管理器，设置已完成的任务
    dm = DataManager(data_file=temp_data_file)
    current_pet = dm.get_current_pet_id()
    dm.data['pets_data'][current_pet]['tasks_completed_today'] = 2
    dm.data['pets_data'][current_pet]['task_states'] = [True, False, True]
    
    # 创建主窗口和任务窗口
    pet_widget = PetWidget(dm)
    task_window = TaskWindow(dm, pet_widget)
    
    # 验证复选框状态与保存的状态一致
    assert task_window.checkboxes[0].isChecked() is True
    assert task_window.checkboxes[1].isChecked() is False
    assert task_window.checkboxes[2].isChecked() is True
    
    # 清理
    task_window.close()
    pet_widget.close()


def test_window_close_saves_data(qapp, temp_data_file):
    """测试窗口关闭时保存数据
    
    验证关闭任务窗口时，数据被保存到文件
    """
    # 创建数据管理器
    dm = DataManager(data_file=temp_data_file)
    
    # 创建主窗口和任务窗口
    pet_widget = PetWidget(dm)
    task_window = TaskWindow(dm, pet_widget)
    
    # 勾选一个任务
    task_window.checkboxes[0].setChecked(True)
    
    # 关闭窗口
    task_window.close()
    
    # 创建新的数据管理器，验证数据已保存
    dm2 = DataManager(data_file=temp_data_file)
    assert dm2.get_tasks_completed() == 1
    current_pet = dm2.get_current_pet_id()
    assert dm2.data['pets_data'][current_pet]['task_states'][0] is True
    
    # 清理
    pet_widget.close()


def test_tasks_only_affect_current_pet(qapp, temp_data_file):
    """测试任务只影响当前宠物
    
    验证需求 8.1：当用户完成任务时，只更新当前显示宠物的任务完成数
    
    测试场景：
    1. 解锁水母
    2. 为河豚和水母设置不同的初始状态
    3. 切换到河豚并完成任务
    4. 验证只有河豚的数据被更新，水母的数据保持不变
    5. 切换到水母并完成任务
    6. 验证只有水母的数据被更新，河豚的数据保持不变
    """
    # 创建数据管理器
    dm = DataManager(data_file=temp_data_file)
    
    # 解锁水母
    dm.unlock_pet('jelly')
    
    # 设置河豚的初始状态：等级2，完成1个任务
    dm.data['pets_data']['puffer']['level'] = 2
    dm.data['pets_data']['puffer']['tasks_completed_today'] = 1
    dm.data['pets_data']['puffer']['task_states'] = [True, False, False]
    
    # 设置水母的初始状态：等级1，完成0个任务
    dm.data['pets_data']['jelly']['level'] = 1
    dm.data['pets_data']['jelly']['tasks_completed_today'] = 0
    dm.data['pets_data']['jelly']['task_states'] = [False, False, False]
    
    # 设置当前宠物为河豚
    dm.set_current_pet_id('puffer')
    
    # 创建主窗口和任务窗口
    pet_widget = PetWidget(dm)
    task_window = TaskWindow(dm, pet_widget)
    
    # 验证初始状态
    assert dm.get_current_pet_id() == 'puffer'
    assert dm.get_tasks_completed('puffer') == 1
    assert dm.get_tasks_completed('jelly') == 0
    assert dm.get_level('puffer') == 2
    assert dm.get_level('jelly') == 1
    
    # 为河豚完成第二个任务
    task_window.checkboxes[1].setChecked(True)
    
    # 验证只有河豚的数据被更新
    assert dm.get_tasks_completed('puffer') == 2
    assert dm.get_tasks_completed('jelly') == 0  # 水母数据不变
    assert dm.data['pets_data']['puffer']['task_states'] == [True, True, False]
    assert dm.data['pets_data']['jelly']['task_states'] == [False, False, False]  # 水母任务状态不变
    
    # 关闭任务窗口
    task_window.close()
    
    # 切换到水母
    pet_widget.switch_pet('jelly')
    
    # 创建新的任务窗口（针对水母）
    task_window2 = TaskWindow(dm, pet_widget)
    
    # 验证当前宠物是水母
    assert dm.get_current_pet_id() == 'jelly'
    
    # 验证任务窗口显示水母的状态
    assert task_window2.checkboxes[0].isChecked() is False
    assert task_window2.checkboxes[1].isChecked() is False
    assert task_window2.checkboxes[2].isChecked() is False
    assert task_window2.progress_label.text() == "0/3"
    
    # 为水母完成第一个任务
    task_window2.checkboxes[0].setChecked(True)
    
    # 验证只有水母的数据被更新，河豚的数据保持不变
    assert dm.get_tasks_completed('jelly') == 1
    assert dm.get_tasks_completed('puffer') == 2  # 河豚数据不变
    assert dm.data['pets_data']['jelly']['task_states'] == [True, False, False]
    assert dm.data['pets_data']['puffer']['task_states'] == [True, True, False]  # 河豚任务状态不变
    
    # 清理
    task_window2.close()
    pet_widget.close()


def test_task_completion_triggers_reward_check(qapp, temp_data_file):
    """测试任务完成触发奖励检查
    
    验证需求 14.2, 14.3：
    - 当用户完成任务时，调用 RewardManager.on_task_completed()
    - 当累计任务数达到12时，触发奖励判定
    """
    from reward_manager import RewardManager
    from unittest.mock import patch
    
    # 创建数据管理器
    dm = DataManager(data_file=temp_data_file)
    
    # 设置累计任务数为11（下一个任务将触发奖励）
    if 'reward_system' not in dm.data:
        dm.data['reward_system'] = {
            'cumulative_tasks_completed': 11,
            'reward_threshold': 12,
            'tier2_unlock_probability': 0.7,
            'lootbox_probability': 0.3
        }
    else:
        dm.data['reward_system']['cumulative_tasks_completed'] = 11
    
    dm.save_data()
    
    # 创建奖励管理器
    reward_manager = RewardManager(dm)
    
    # 创建主窗口和任务窗口（带奖励管理器）
    pet_widget = PetWidget(dm)
    task_window = TaskWindow(dm, pet_widget, reward_manager)
    
    # 验证初始累计任务数
    assert dm.get_cumulative_tasks() == 11
    
    # 模拟消息框以避免GUI崩溃
    with patch('task_window.QMessageBox.information'):
        with patch('task_window.QMessageBox.warning'):
            # 完成一个任务
            task_window.checkboxes[0].setChecked(True)
    
    # 验证累计任务数被重置（因为触发了奖励）
    assert dm.get_cumulative_tasks() == 0
    
    # 清理
    task_window.close()
    pet_widget.close()


def test_reward_notification_display(qapp, temp_data_file):
    """测试奖励通知显示
    
    验证需求 14.2, 14.3：
    - 当触发奖励时，显示相应的通知
    - Tier 2解锁显示"恭喜！你解锁了稀有生物"
    - 盲盒显示"你钓到了"
    """
    from reward_manager import RewardManager
    from unittest.mock import patch
    
    # 创建数据管理器
    dm = DataManager(data_file=temp_data_file)
    
    # 设置累计任务数为11
    if 'reward_system' not in dm.data:
        dm.data['reward_system'] = {
            'cumulative_tasks_completed': 11,
            'reward_threshold': 12,
            'tier2_unlock_probability': 0.7,
            'lootbox_probability': 0.3
        }
    else:
        dm.data['reward_system']['cumulative_tasks_completed'] = 11
    
    dm.save_data()
    
    # 创建奖励管理器
    reward_manager = RewardManager(dm)
    
    # 创建主窗口和任务窗口
    pet_widget = PetWidget(dm)
    task_window = TaskWindow(dm, pet_widget, reward_manager)
    
    # 模拟奖励触发，强制返回Tier 2奖励
    with patch.object(reward_manager, 'trigger_reward', return_value={'type': 'tier2', 'pet_id': 'octopus'}):
        with patch('task_window.QMessageBox.information') as mock_info:
            # 完成任务触发奖励
            task_window.checkboxes[0].setChecked(True)
            
            # 验证显示了通知
            mock_info.assert_called_once()
            call_args = mock_info.call_args
            assert "解锁稀有生物" in call_args[0][1]  # 标题
            assert "octopus" in call_args[0][2]  # 消息内容
    
    # 清理
    task_window.close()
    pet_widget.close()


def test_inventory_full_handling(qapp, temp_data_file):
    """测试库存已满的情况处理
    
    验证需求 16.4：
    - 当库存已满时，显示"鱼缸满了，请先放生"提示
    - 不添加新宠物
    """
    from reward_manager import RewardManager
    from unittest.mock import patch
    
    # 创建数据管理器
    dm = DataManager(data_file=temp_data_file)
    
    # 填满库存（添加20只宠物）
    # 需要添加20只不同的宠物ID
    all_pets = ['puffer', 'jelly', 'starfish', 'crab', 'octopus', 'ribbon', 'sunfish', 'angler',
                'blobfish', 'ray', 'beluga', 'orca', 'shark', 'bluewhale',
                'pet15', 'pet16', 'pet17', 'pet18', 'pet19', 'pet20']
    
    # 清空现有的unlocked_pets并添加20只
    dm.data['unlocked_pets'] = []
    for i in range(20):
        dm.data['unlocked_pets'].append(all_pets[i])
        # 为每个宠物创建数据
        if all_pets[i] not in dm.data['pets_data']:
            dm.data['pets_data'][all_pets[i]] = {
                'level': 1,
                'tasks_completed_today': 0,
                'last_login_date': dm.data['pets_data']['puffer']['last_login_date'],
                'task_states': [False, False, False]
            }
    
    # 设置累计任务数为11
    if 'reward_system' not in dm.data:
        dm.data['reward_system'] = {
            'cumulative_tasks_completed': 11,
            'reward_threshold': 12,
            'tier2_unlock_probability': 0.7,
            'lootbox_probability': 0.3
        }
    else:
        dm.data['reward_system']['cumulative_tasks_completed'] = 11
    
    dm.save_data()
    
    # 验证库存已满
    assert not dm.can_add_to_inventory(), f"库存应该已满，但实际有 {len(dm.get_unlocked_pets())} 只宠物"
    
    # 创建奖励管理器
    reward_manager = RewardManager(dm)
    
    # 创建主窗口和任务窗口
    pet_widget = PetWidget(dm)
    task_window = TaskWindow(dm, pet_widget, reward_manager)
    
    # 模拟奖励触发
    with patch.object(reward_manager, 'trigger_reward', return_value={'type': 'lootbox', 'pet_id': 'bluewhale'}):
        with patch('task_window.QMessageBox.warning') as mock_warning:
            # 完成任务触发奖励
            task_window.checkboxes[0].setChecked(True)
            
            # 验证显示了警告
            mock_warning.assert_called_once()
            call_args = mock_warning.call_args
            assert "鱼缸满了" in call_args[0][1]  # 标题
            assert "请先放生" in call_args[0][2]  # 消息内容
    
    # 清理
    task_window.close()
    pet_widget.close()
