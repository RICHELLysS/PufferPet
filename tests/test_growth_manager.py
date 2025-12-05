"""
GrowthManager 单元测试
验证 V6 稳定版成长状态机的核心功能
"""
import json
import os
import tempfile
import pytest
from hypothesis import given, strategies as st, settings, assume
from logic_growth import GrowthManager, PetData


class TestGrowthManagerBasic:
    """基础功能测试"""
    
    def setup_method(self):
        """每个测试前创建临时文件"""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.json'
        )
        self.temp_file.close()
        self.gm = GrowthManager(data_file=self.temp_file.name)
    
    def teardown_method(self):
        """每个测试后清理临时文件"""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
    
    def test_init_creates_default_pet(self):
        """测试初始化时创建默认宠物"""
        assert 'puffer' in self.gm.pets
        assert self.gm.get_state('puffer') == 0
        assert self.gm.get_progress('puffer') == 0
    
    def test_get_state_returns_correct_value(self):
        """测试 get_state 返回正确的状态值"""
        self.gm.pets['puffer'].state = 1
        assert self.gm.get_state('puffer') == 1
    
    def test_get_progress_returns_correct_value(self):
        """测试 get_progress 返回正确的进度值"""
        self.gm.pets['puffer'].tasks_progress = 2
        assert self.gm.get_progress('puffer') == 2
    
    def test_ensure_pet_creates_new_pet(self):
        """测试 _ensure_pet 为新宠物创建数据"""
        assert 'new_pet' not in self.gm.pets
        self.gm._ensure_pet('new_pet')
        assert 'new_pet' in self.gm.pets
        assert self.gm.pets['new_pet'].state == 0
        assert self.gm.pets['new_pet'].tasks_progress == 0


class TestStateTransitions:
    """状态转换测试 - 验证需求 1.5, 1.8"""
    
    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.json'
        )
        self.temp_file.close()
        self.gm = GrowthManager(data_file=self.temp_file.name)
        self.gm.reset_cycle('puffer')  # 确保从休眠状态开始
    
    def teardown_method(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
    
    def test_dormant_to_baby_transition(self):
        """需求 1.5: 完成1个任务从休眠变为幼年"""
        assert self.gm.get_state('puffer') == 0  # 休眠
        new_state = self.gm.complete_task('puffer')
        assert new_state == 1  # 幼年
        assert self.gm.get_progress('puffer') == 1
    
    def test_baby_to_adult_transition(self):
        """需求 1.8: 累计完成3个任务从幼年变为成年"""
        # 先完成1个任务进入幼年
        self.gm.complete_task('puffer')
        assert self.gm.get_state('puffer') == 1
        
        # 完成第2个任务，仍为幼年
        self.gm.complete_task('puffer')
        assert self.gm.get_state('puffer') == 1
        
        # 完成第3个任务，进化为成年
        new_state = self.gm.complete_task('puffer')
        assert new_state == 2  # 成年
        assert self.gm.get_progress('puffer') == 3
    
    def test_adult_state_remains_adult(self):
        """成年状态下继续完成任务不会改变状态"""
        # 快速进入成年状态
        for _ in range(3):
            self.gm.complete_task('puffer')
        assert self.gm.get_state('puffer') == 2
        
        # 继续完成任务
        new_state = self.gm.complete_task('puffer')
        assert new_state == 2  # 仍为成年
        assert self.gm.get_progress('puffer') == 4


class TestResetCycle:
    """周期重置测试 - 验证需求 2.5"""
    
    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.json'
        )
        self.temp_file.close()
        self.gm = GrowthManager(data_file=self.temp_file.name)
    
    def teardown_method(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
    
    def test_reset_from_baby(self):
        """从幼年状态重置"""
        self.gm.complete_task('puffer')  # 进入幼年
        assert self.gm.get_state('puffer') == 1
        
        self.gm.reset_cycle('puffer')
        assert self.gm.get_state('puffer') == 0
        assert self.gm.get_progress('puffer') == 0
    
    def test_reset_from_adult(self):
        """从成年状态重置"""
        for _ in range(3):
            self.gm.complete_task('puffer')
        assert self.gm.get_state('puffer') == 2
        
        self.gm.reset_cycle('puffer')
        assert self.gm.get_state('puffer') == 0
        assert self.gm.get_progress('puffer') == 0


class TestDataPersistence:
    """数据持久化测试"""
    
    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.json'
        )
        self.temp_file.close()
    
    def teardown_method(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
    
    def test_save_and_load(self):
        """测试数据保存和加载"""
        gm1 = GrowthManager(data_file=self.temp_file.name)
        gm1.complete_task('puffer')
        gm1.complete_task('puffer')
        gm1.save()
        
        # 创建新实例加载数据
        gm2 = GrowthManager(data_file=self.temp_file.name)
        assert gm2.get_state('puffer') == gm1.get_state('puffer')
        assert gm2.get_progress('puffer') == gm1.get_progress('puffer')
    
    def test_load_corrupted_file_uses_defaults(self):
        """测试加载损坏文件时使用默认值"""
        # 写入无效 JSON
        with open(self.temp_file.name, 'w') as f:
            f.write('invalid json')
        
        gm = GrowthManager(data_file=self.temp_file.name)
        assert 'puffer' in gm.pets
        assert gm.get_state('puffer') == 0


class TestHelperMethods:
    """辅助方法测试"""
    
    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.json'
        )
        self.temp_file.close()
        self.gm = GrowthManager(data_file=self.temp_file.name)
    
    def teardown_method(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
    
    def test_get_image_stage_dormant(self):
        """休眠状态返回 baby 图像"""
        self.gm.reset_cycle('puffer')
        assert self.gm.get_image_stage('puffer') == 'baby'
    
    def test_get_image_stage_baby(self):
        """幼年状态返回 baby 图像"""
        self.gm.reset_cycle('puffer')
        self.gm.complete_task('puffer')
        assert self.gm.get_image_stage('puffer') == 'baby'
    
    def test_get_image_stage_adult(self):
        """成年状态返回 adult 图像"""
        self.gm.reset_cycle('puffer')
        for _ in range(3):
            self.gm.complete_task('puffer')
        assert self.gm.get_image_stage('puffer') == 'adult'
    
    def test_is_dormant(self):
        """测试 is_dormant 方法"""
        self.gm.reset_cycle('puffer')
        assert self.gm.is_dormant('puffer') is True
        
        self.gm.complete_task('puffer')
        assert self.gm.is_dormant('puffer') is False


# ============================================================================
# Property-Based Tests for V6 GrowthManager
# ============================================================================

# Custom strategies for GrowthManager
@st.composite
def valid_pet_id_v6(draw):
    """Generate valid pet IDs"""
    return draw(st.sampled_from(['puffer', 'jelly', 'starfish', 'crab', 'octopus']))


@st.composite
def task_sequence(draw):
    """Generate a sequence of task completions (0-10 tasks)"""
    num_tasks = draw(st.integers(min_value=0, max_value=10))
    return num_tasks


@st.composite
def action_sequence(draw):
    """Generate a sequence of actions: 'task' or 'reset'"""
    num_actions = draw(st.integers(min_value=1, max_value=15))
    actions = []
    for _ in range(num_actions):
        action = draw(st.sampled_from(['task', 'task', 'task', 'reset']))  # Bias towards tasks
        actions.append(action)
    return actions


# **Feature: puffer-pet-v6, Property 1: State Transition Correctness**
# **Validates: Requirements 1.5, 1.8**
@settings(max_examples=100)
@given(
    pet_id=valid_pet_id_v6(),
    actions=action_sequence()
)
def test_property_1_state_transition_correctness(pet_id, actions):
    """
    Property 1: State Transition Correctness
    
    For any pet, states can only transition in order 0→1→2, no skipping or going backwards
    (except via reset which returns to state 0).
    
    This property verifies:
    - State transitions only happen in forward order: 0→1→2
    - State never skips (e.g., 0→2 is not allowed)
    - State never goes backwards (e.g., 2→1 is not allowed) except via reset
    - Reset always returns to state 0
    
    **Feature: puffer-pet-v6, Property 1: State Transition Correctness**
    **Validates: Requirements 1.5, 1.8**
    """
    # Create temporary file for test isolation
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # Initialize GrowthManager
        gm = GrowthManager(data_file=temp_file)
        gm.reset_cycle(pet_id)  # Start from dormant state
        
        # Track state history
        previous_state = gm.get_state(pet_id)
        assert previous_state == 0, "Initial state should be 0 (dormant)"
        
        for action in actions:
            if action == 'task':
                # Complete a task
                new_state = gm.complete_task(pet_id)
                
                # Verify state transition rules:
                # 1. State can only increase by at most 1
                # 2. State can never decrease (without reset)
                # 3. State is bounded [0, 2]
                
                assert new_state >= previous_state, \
                    f"State should not decrease without reset: {previous_state} -> {new_state}"
                
                assert new_state - previous_state <= 1, \
                    f"State should not skip levels: {previous_state} -> {new_state}"
                
                assert 0 <= new_state <= 2, \
                    f"State should be in valid range [0, 2]: {new_state}"
                
                previous_state = new_state
                
            elif action == 'reset':
                # Reset cycle
                gm.reset_cycle(pet_id)
                new_state = gm.get_state(pet_id)
                
                # Verify reset always returns to state 0
                assert new_state == 0, \
                    f"Reset should return to state 0, got: {new_state}"
                
                # Verify progress is also reset
                assert gm.get_progress(pet_id) == 0, \
                    f"Reset should clear progress, got: {gm.get_progress(pet_id)}"
                
                previous_state = new_state
        
        # Final verification: state is always valid
        final_state = gm.get_state(pet_id)
        assert final_state in [0, 1, 2], f"Final state should be valid: {final_state}"
        
    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)


# **Feature: puffer-pet-v6, Property 2: Task Progress and State Synchronization**
# **Validates: Requirements 2.3, 2.4**
@settings(max_examples=100)
@given(
    pet_id=valid_pet_id_v6(),
    num_tasks=st.integers(min_value=0, max_value=10)
)
def test_property_2_task_progress_state_synchronization(pet_id, num_tasks):
    """
    Property 2: Task Progress and State Synchronization
    
    For any pet, when tasks_progress=1 the state should be at least 1,
    and when tasks_progress=3 the state should be 2.
    
    This property verifies:
    - tasks_progress >= 1 implies state >= 1 (baby or adult)
    - tasks_progress >= 3 implies state == 2 (adult)
    - The state is always consistent with the task progress
    
    **Feature: puffer-pet-v6, Property 2: Task Progress and State Synchronization**
    **Validates: Requirements 2.3, 2.4**
    """
    # Create temporary file for test isolation
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # Initialize GrowthManager
        gm = GrowthManager(data_file=temp_file)
        gm.reset_cycle(pet_id)  # Start from dormant state (state=0, progress=0)
        
        # Complete the specified number of tasks
        for _ in range(num_tasks):
            gm.complete_task(pet_id)
        
        # Get current state and progress
        state = gm.get_state(pet_id)
        progress = gm.get_progress(pet_id)
        
        # Verify progress matches expected value
        assert progress == num_tasks, \
            f"Progress should be {num_tasks}, got {progress}"
        
        # Property: tasks_progress >= 1 implies state >= 1 (Requirements 2.3)
        # When tasks_progress changes from 0 to 1, pet evolves from dormant to baby
        if progress >= 1:
            assert state >= GrowthManager.STATE_BABY, \
                f"With progress={progress}, state should be >= 1 (baby), got {state}"
        
        # Property: tasks_progress >= 3 implies state == 2 (Requirements 2.4)
        # When tasks_progress reaches 3, pet evolves to adult
        if progress >= 3:
            assert state == GrowthManager.STATE_ADULT, \
                f"With progress={progress}, state should be 2 (adult), got {state}"
        
        # Additional invariant: state should be consistent with progress thresholds
        if progress == 0:
            assert state == GrowthManager.STATE_DORMANT, \
                f"With progress=0, state should be 0 (dormant), got {state}"
        elif progress >= 1 and progress < 3:
            assert state == GrowthManager.STATE_BABY, \
                f"With progress={progress} (1-2), state should be 1 (baby), got {state}"
        else:  # progress >= 3
            assert state == GrowthManager.STATE_ADULT, \
                f"With progress={progress} (>=3), state should be 2 (adult), got {state}"
        
    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)
