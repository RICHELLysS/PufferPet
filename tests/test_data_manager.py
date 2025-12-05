"""单元测试 - DataManager 类的具体场景测试"""
import json
import os
import tempfile
from datetime import date
from data_manager import DataManager


def test_default_data_creation():
    """测试默认数据创建（V5.5格式）"""
    # 创建临时文件路径（不存在的文件）
    with tempfile.NamedTemporaryFile(delete=True, suffix='.json') as f:
        temp_file = f.name
    
    # 创建数据管理器（文件不存在）
    dm = DataManager(data_file=temp_file)
    
    # 验证V5.5默认数据
    assert dm.data['version'] == 5.5
    assert dm.data['current_pet_id'] == 'puffer'
    assert dm.get_level() == 1
    assert dm.get_tasks_completed() == 0
    assert dm.data['pets_data']['puffer']['last_login_date'] == date.today().isoformat()
    assert dm.data['pets_data']['puffer']['task_states'] == [False, False, False]
    
    # 清理
    if os.path.exists(temp_file):
        os.remove(temp_file)


def test_corrupted_json_handling():
    """测试 JSON 解析错误处理"""
    # 创建临时文件并写入无效 JSON
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
        f.write("{ invalid json content }")
    
    try:
        # 创建数据管理器（应该处理错误并创建默认数据）
        dm = DataManager(data_file=temp_file)
        
        # 验证创建了V5.5默认数据
        assert dm.data['version'] == 5.5
        assert dm.get_level() == 1
        assert dm.get_tasks_completed() == 0
        
        # 验证备份文件被创建
        backup_file = temp_file + '.backup'
        assert os.path.exists(backup_file)
        
        # 清理备份文件
        if os.path.exists(backup_file):
            os.remove(backup_file)
    finally:
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_increment_task_boundary():
    """测试任务增加的边界条件"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        dm.data['tasks_completed_today'] = 3
        
        # 尝试超过最大值
        dm.increment_task()
        
        # 验证不会超过 3
        assert dm.data['tasks_completed_today'] == 3
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_decrement_task_boundary():
    """测试任务减少的边界条件"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        dm.data['tasks_completed_today'] = 0
        
        # 尝试减少到负数
        dm.decrement_task()
        
        # 验证不会变成负数
        assert dm.data['tasks_completed_today'] == 0
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_level_cap_at_3():
    """测试等级上限为 3"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        dm.data['pets_data']['puffer']['level'] = 3
        dm.data['pets_data']['puffer']['tasks_completed_today'] = 0
        
        # 完成 3 个任务
        for _ in range(3):
            dm.increment_task()
        
        # 验证等级不会超过 3
        assert dm.get_level() == 3
        assert dm.get_tasks_completed() == 3
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)



# V2 版本单元测试

def test_v2_default_data_creation():
    """测试V5.5默认数据创建（更新后的默认格式）"""
    # 创建临时文件路径（不存在的文件）
    with tempfile.NamedTemporaryFile(delete=True, suffix='.json') as f:
        temp_file = f.name
    
    # 创建数据管理器（文件不存在）
    dm = DataManager(data_file=temp_file)
    
    # 验证V5.5数据结构
    assert dm.data['version'] == 5.5
    assert dm.data['current_pet_id'] == 'puffer'
    assert 'puffer' in dm.data['unlocked_pets']
    assert 'pets_data' in dm.data
    assert 'puffer' in dm.data['pets_data']
    assert 'jelly' in dm.data['pets_data']
    
    # 验证河豚默认数据
    puffer_data = dm.data['pets_data']['puffer']
    assert puffer_data['level'] == 1
    assert puffer_data['tasks_completed_today'] == 0
    assert puffer_data['last_login_date'] == date.today().isoformat()
    assert puffer_data['task_states'] == [False, False, False]
    
    # 清理
    if os.path.exists(temp_file):
        os.remove(temp_file)


def test_v1_to_v2_migration():
    """测试V1到V2数据迁移"""
    # 创建临时文件并写入V1格式数据
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
        v1_data = {
            'level': 2,
            'tasks_completed_today': 1,
            'last_login_date': date.today().isoformat(),
            'task_states': [True, False, False]
        }
        json.dump(v1_data, f)
    
    try:
        # 创建数据管理器（应该自动迁移）
        dm = DataManager(data_file=temp_file)
        
        # 验证V2结构
        assert dm.data['version'] == 2
        assert dm.data['current_pet_id'] == 'puffer'
        assert 'puffer' in dm.data['unlocked_pets']
        
        # 验证河豚数据保留
        puffer_data = dm.data['pets_data']['puffer']
        assert puffer_data['level'] == 2
        assert puffer_data['tasks_completed_today'] == 1
        assert puffer_data['task_states'] == [True, False, False]
        
        # 验证水母数据创建
        assert 'jelly' in dm.data['pets_data']
        jelly_data = dm.data['pets_data']['jelly']
        assert jelly_data['level'] == 1
        
        # 验证备份文件创建
        backup_file = temp_file + '.v1.backup'
        assert os.path.exists(backup_file)
        
        # 清理备份文件
        if os.path.exists(backup_file):
            os.remove(backup_file)
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_multi_pet_management():
    """测试多宠物数据管理"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 解锁水母
        dm.unlock_pet('jelly')
        assert dm.is_pet_unlocked('jelly')
        assert 'jelly' in dm.get_unlocked_pets()
        
        # 设置河豚数据
        dm.data['pets_data']['puffer']['level'] = 2
        dm.data['pets_data']['puffer']['tasks_completed_today'] = 1
        
        # 切换到水母
        dm.set_current_pet_id('jelly')
        assert dm.get_current_pet_id() == 'jelly'
        
        # 验证水母数据独立
        assert dm.get_level('jelly') == 1
        assert dm.get_tasks_completed('jelly') == 0
        
        # 验证河豚数据未受影响
        assert dm.get_level('puffer') == 2
        assert dm.get_tasks_completed('puffer') == 1
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_unlock_jelly_when_puffer_reaches_level_3():
    """测试河豚达到等级3时不再自动解锁水母（V3中水母默认解锁）"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # V3中，水母默认已解锁（Tier 1宠物）
        assert dm.is_pet_unlocked('jelly')
        
        # 设置河豚等级为2
        dm.data['pets_data']['puffer']['level'] = 2
        dm.data['pets_data']['puffer']['tasks_completed_today'] = 0
        dm.save_data()
        
        # 完成3个任务（应该升级到等级3）
        for _ in range(3):
            unlocked = dm.increment_task('puffer')
        
        # 验证河豚达到等级3
        assert dm.get_level('puffer') == 3
        
        # V3中不再有自动解锁逻辑
        assert unlocked == False
        # 但水母仍然是解锁状态（因为默认解锁）
        assert dm.is_pet_unlocked('jelly')
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_cannot_switch_to_locked_pet():
    """测试无法切换到未解锁的宠物"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 确保水母未解锁
        if 'jelly' in dm.data['unlocked_pets']:
            dm.data['unlocked_pets'].remove('jelly')
        dm.save_data()
        
        # 尝试切换到水母
        dm.set_current_pet_id('jelly')
        
        # 验证仍然是河豚
        assert dm.get_current_pet_id() == 'puffer'
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_get_unlock_condition():
    """测试获取解锁条件"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 验证V3解锁条件
        assert dm.get_unlock_condition('puffer') == '默认解锁'
        assert dm.get_unlock_condition('jelly') == '默认解锁'  # V3中水母默认解锁
        assert dm.get_unlock_condition('octopus') == '通过奇遇捕获'
        assert dm.get_unlock_condition('angler') == '通过奇遇捕获'
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_v2_image_mapping():
    """测试V3图像映射（新的目录结构）"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 测试河豚图像 - V3使用新的命名格式
        assert dm.get_image_for_level('puffer', 1) == 'assets/puffer/baby_idle.png'
        assert dm.get_image_for_level('puffer', 2) == 'assets/puffer/adult_idle.png'
        assert dm.get_image_for_level('puffer', 3) == 'assets/puffer/adult_idle.png'
        
        # 测试水母图像 - V3使用新的命名格式
        assert dm.get_image_for_level('jelly', 1) == 'assets/jelly/baby_idle.png'
        assert dm.get_image_for_level('jelly', 2) == 'assets/jelly/adult_idle.png'
        assert dm.get_image_for_level('jelly', 3) == 'assets/jelly/adult_idle.png'
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)



# V3 版本单元测试

def test_v3_default_data_creation():
    """测试V5.5默认数据创建（14种生物）"""
    # 创建临时文件路径（不存在的文件）
    with tempfile.NamedTemporaryFile(delete=True, suffix='.json') as f:
        temp_file = f.name
    
    # 创建数据管理器（文件不存在）
    dm = DataManager(data_file=temp_file)
    
    # 验证V5.5数据结构
    assert dm.data['version'] == 5.5
    assert dm.data['current_pet_id'] == 'puffer'
    assert 'pet_tiers' in dm.data
    assert 'encounter_settings' in dm.data
    
    # 验证层级定义
    assert set(dm.data['pet_tiers']['tier1']) == {'puffer', 'jelly', 'starfish', 'crab'}
    assert set(dm.data['pet_tiers']['tier2']) == {'octopus', 'ribbon', 'sunfish', 'angler'}
    
    # 验证所有Tier 1宠物默认解锁
    assert set(dm.data['unlocked_pets']) == {'puffer', 'jelly', 'starfish', 'crab'}
    
    # 验证所有8种生物都有数据
    all_pets = ['puffer', 'jelly', 'starfish', 'crab', 'octopus', 'ribbon', 'sunfish', 'angler']
    for pet_id in all_pets:
        assert pet_id in dm.data['pets_data']
        pet_data = dm.data['pets_data'][pet_id]
        assert pet_data['level'] == 1
        assert pet_data['tasks_completed_today'] == 0
        assert pet_data['last_login_date'] == date.today().isoformat()
        assert pet_data['task_states'] == [False, False, False]
    
    # 验证encounter_settings
    assert dm.data['encounter_settings']['check_interval_minutes'] == 5
    assert dm.data['encounter_settings']['trigger_probability'] == 0.3
    assert 'last_encounter_check' in dm.data['encounter_settings']
    
    # 清理
    if os.path.exists(temp_file):
        os.remove(temp_file)


def test_v2_to_v3_migration():
    """测试V2到V3数据迁移"""
    # 创建临时文件并写入V2格式数据
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
        v2_data = {
            'version': 2,
            'current_pet_id': 'puffer',
            'unlocked_pets': ['puffer', 'jelly'],
            'pets_data': {
                'puffer': {
                    'level': 3,
                    'tasks_completed_today': 2,
                    'last_login_date': date.today().isoformat(),
                    'task_states': [True, True, False]
                },
                'jelly': {
                    'level': 2,
                    'tasks_completed_today': 1,
                    'last_login_date': date.today().isoformat(),
                    'task_states': [True, False, False]
                }
            }
        }
        json.dump(v2_data, f)
    
    try:
        # 创建数据管理器（应该自动迁移）
        dm = DataManager(data_file=temp_file)
        
        # 验证V3结构
        assert dm.data['version'] == 3
        assert 'pet_tiers' in dm.data
        assert 'encounter_settings' in dm.data
        
        # 验证原有宠物数据保留
        puffer_data = dm.data['pets_data']['puffer']
        assert puffer_data['level'] == 3
        assert puffer_data['tasks_completed_today'] == 2
        assert puffer_data['task_states'] == [True, True, False]
        
        jelly_data = dm.data['pets_data']['jelly']
        assert jelly_data['level'] == 2
        assert jelly_data['tasks_completed_today'] == 1
        assert jelly_data['task_states'] == [True, False, False]
        
        # 验证新的Tier 1宠物被添加到unlocked_pets
        assert 'starfish' in dm.data['unlocked_pets']
        assert 'crab' in dm.data['unlocked_pets']
        assert 'puffer' in dm.data['unlocked_pets']
        assert 'jelly' in dm.data['unlocked_pets']
        
        # 验证所有8种生物都有数据
        all_pets = ['puffer', 'jelly', 'starfish', 'crab', 'octopus', 'ribbon', 'sunfish', 'angler']
        for pet_id in all_pets:
            assert pet_id in dm.data['pets_data']
        
        # 验证备份文件创建
        backup_file = temp_file + '.v2.backup'
        assert os.path.exists(backup_file)
        
        # 清理备份文件
        if os.path.exists(backup_file):
            os.remove(backup_file)
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_get_pet_tier():
    """测试获取宠物层级"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 测试Tier 1宠物
        assert dm.get_pet_tier('puffer') == 1
        assert dm.get_pet_tier('jelly') == 1
        assert dm.get_pet_tier('starfish') == 1
        assert dm.get_pet_tier('crab') == 1
        
        # 测试Tier 2宠物
        assert dm.get_pet_tier('octopus') == 2
        assert dm.get_pet_tier('ribbon') == 2
        assert dm.get_pet_tier('sunfish') == 2
        assert dm.get_pet_tier('angler') == 2
        
        # 测试不存在的宠物
        assert dm.get_pet_tier('unknown') == 0
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_get_tier_pets():
    """测试获取指定层级的宠物列表"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 测试Tier 1
        tier1_pets = dm.get_tier_pets(1)
        assert set(tier1_pets) == {'puffer', 'jelly', 'starfish', 'crab'}
        
        # 测试Tier 2
        tier2_pets = dm.get_tier_pets(2)
        assert set(tier2_pets) == {'octopus', 'ribbon', 'sunfish', 'angler'}
        
        # 测试Tier 3（V3.5新增）
        tier3_pets = dm.get_tier_pets(3)
        assert set(tier3_pets) == {'blobfish', 'ray', 'beluga', 'orca', 'shark', 'bluewhale'}
        
        # 测试无效层级
        assert dm.get_tier_pets(0) == []
        assert dm.get_tier_pets(4) == []
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_v3_image_path_format():
    """测试V3图像路径格式（新目录结构）"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 测试所有宠物的图像路径
        all_pets = ['puffer', 'jelly', 'starfish', 'crab', 'octopus', 'ribbon', 'sunfish', 'angler']
        
        for pet_id in all_pets:
            # Level 1 使用 baby_idle.png
            assert dm.get_image_for_level(pet_id, 1) == f'assets/{pet_id}/baby_idle.png'
            
            # Level 2-3 使用 adult_idle.png
            assert dm.get_image_for_level(pet_id, 2) == f'assets/{pet_id}/adult_idle.png'
            assert dm.get_image_for_level(pet_id, 3) == f'assets/{pet_id}/adult_idle.png'
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_v3_unlock_conditions():
    """测试V3解锁条件"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 测试Tier 1宠物解锁条件
        assert dm.get_unlock_condition('puffer') == '默认解锁'
        assert dm.get_unlock_condition('jelly') == '默认解锁'
        assert dm.get_unlock_condition('starfish') == '默认解锁'
        assert dm.get_unlock_condition('crab') == '默认解锁'
        
        # 测试Tier 2宠物解锁条件
        assert dm.get_unlock_condition('octopus') == '通过奇遇捕获'
        assert dm.get_unlock_condition('ribbon') == '通过奇遇捕获'
        assert dm.get_unlock_condition('sunfish') == '通过奇遇捕获'
        assert dm.get_unlock_condition('angler') == '通过奇遇捕获'
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_v3_no_auto_unlock():
    """测试V3不再有自动解锁逻辑"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 设置河豚等级为2
        dm.data['pets_data']['puffer']['level'] = 2
        dm.data['pets_data']['puffer']['tasks_completed_today'] = 0
        dm.save_data()
        
        # 完成3个任务（应该升级到等级3）
        for _ in range(3):
            unlocked = dm.increment_task('puffer')
        
        # 验证河豚达到等级3
        assert dm.get_level('puffer') == 3
        
        # 验证没有自动解锁任何宠物（V3中Tier 1默认解锁，Tier 2通过奇遇解锁）
        assert unlocked == False
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


# V3 捕获系统单元测试

def test_capture_rare_pet_basic():
    """测试捕获稀有宠物的基本功能"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # 创建数据管理器（V3格式）
        dm = DataManager(data_file=temp_file)
        
        # 确保octopus未解锁
        if 'octopus' in dm.data['unlocked_pets']:
            dm.data['unlocked_pets'].remove('octopus')
        if 'octopus' in dm.data['pets_data']:
            del dm.data['pets_data']['octopus']
        dm.save_data()
        
        # 验证初始状态
        assert not dm.is_pet_unlocked('octopus')
        
        # 捕获octopus
        dm.capture_rare_pet('octopus')
        
        # 验证捕获后状态
        assert dm.is_pet_unlocked('octopus')
        assert 'octopus' in dm.data['unlocked_pets']
        assert 'octopus' in dm.data['pets_data']
        
        # 验证初始数据
        pet_data = dm.data['pets_data']['octopus']
        assert pet_data['level'] == 1
        assert pet_data['tasks_completed_today'] == 0
        assert pet_data['task_states'] == [False, False, False]
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_capture_rare_pet_data_persistence():
    """测试捕获后数据持久化"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # 创建数据管理器（V3格式）
        dm = DataManager(data_file=temp_file)
        
        # 确保ribbon未解锁
        if 'ribbon' in dm.data['unlocked_pets']:
            dm.data['unlocked_pets'].remove('ribbon')
        dm.save_data()
        
        # 捕获ribbon
        dm.capture_rare_pet('ribbon')
        
        # 创建新的数据管理器实例验证数据已保存
        dm2 = DataManager(data_file=temp_file)
        
        assert dm2.is_pet_unlocked('ribbon')
        assert 'ribbon' in dm2.data['unlocked_pets']
        assert 'ribbon' in dm2.data['pets_data']
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_capture_already_unlocked_pet():
    """测试捕获已解锁的宠物（应该不产生副作用）"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # 创建数据管理器（V3格式）
        dm = DataManager(data_file=temp_file)
        
        # 先解锁sunfish
        dm.capture_rare_pet('sunfish')
        
        # 记录解锁后的状态
        unlocked_count_before = len(dm.data['unlocked_pets'])
        
        # 再次尝试捕获sunfish
        dm.capture_rare_pet('sunfish')
        
        # 验证没有重复添加
        unlocked_count_after = len(dm.data['unlocked_pets'])
        assert unlocked_count_after == unlocked_count_before
        
        # 验证sunfish只出现一次
        assert dm.data['unlocked_pets'].count('sunfish') == 1
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_capture_tier1_pet_should_warn():
    """测试尝试捕获Tier 1宠物（应该被拒绝）"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # 创建数据管理器（V3格式）
        dm = DataManager(data_file=temp_file)
        
        # 移除puffer的解锁状态（模拟未解锁）
        if 'puffer' in dm.data['unlocked_pets']:
            dm.data['unlocked_pets'].remove('puffer')
        dm.save_data()
        
        # 记录初始状态
        unlocked_count_before = len(dm.data['unlocked_pets'])
        
        # 尝试捕获Tier 1宠物puffer
        dm.capture_rare_pet('puffer')
        
        # 验证puffer没有被添加到unlocked_pets（因为它是Tier 1）
        # capture_rare_pet应该拒绝Tier 1宠物
        unlocked_count_after = len(dm.data['unlocked_pets'])
        
        # 由于capture_rare_pet会检查tier，Tier 1宠物不应该被添加
        assert unlocked_count_after == unlocked_count_before
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_capture_all_tier2_pets():
    """测试捕获所有Tier 2宠物"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # 创建数据管理器（V3格式）
        dm = DataManager(data_file=temp_file)
        
        # 获取所有Tier 2宠物
        tier2_pets = dm.get_tier_pets(2)
        
        # 确保所有Tier 2宠物未解锁
        for pet_id in tier2_pets:
            if pet_id in dm.data['unlocked_pets']:
                dm.data['unlocked_pets'].remove(pet_id)
        dm.save_data()
        
        # 捕获所有Tier 2宠物
        for pet_id in tier2_pets:
            dm.capture_rare_pet(pet_id)
        
        # 验证所有Tier 2宠物都已解锁
        for pet_id in tier2_pets:
            assert dm.is_pet_unlocked(pet_id), f"{pet_id} 应该已解锁"
            assert pet_id in dm.data['unlocked_pets']
            assert pet_id in dm.data['pets_data']
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)



def test_tier2_pet_growth_system():
    """测试Tier 2宠物的成长系统"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # 创建数据管理器（V3格式）
        dm = DataManager(data_file=temp_file)
        
        # 解锁一个Tier 2宠物
        tier2_pet_id = 'octopus'
        dm.unlock_pet(tier2_pet_id)
        dm.set_current_pet_id(tier2_pet_id)
        
        # 验证初始状态
        assert dm.get_level(tier2_pet_id) == 1
        assert dm.get_tasks_completed(tier2_pet_id) == 0
        
        # 完成任务并验证升级
        for i in range(3):
            dm.increment_task(tier2_pet_id)
            assert dm.get_tasks_completed(tier2_pet_id) == i + 1
        
        # 验证升级到等级2
        assert dm.get_level(tier2_pet_id) == 2
        
        # 重置任务数（模拟新的一天）
        dm.data['pets_data'][tier2_pet_id]['tasks_completed_today'] = 0
        dm.save_data()
        
        # 再次完成任务
        for i in range(3):
            dm.increment_task(tier2_pet_id)
        
        # 验证升级到等级3
        assert dm.get_level(tier2_pet_id) == 3
        
        # 验证不会超过等级3
        dm.data['pets_data'][tier2_pet_id]['tasks_completed_today'] = 0
        for i in range(3):
            dm.increment_task(tier2_pet_id)
        
        assert dm.get_level(tier2_pet_id) == 3  # 仍然是等级3
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_tier2_pet_image_loading():
    """测试Tier 2宠物的图像加载"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # 创建数据管理器（V3格式）
        dm = DataManager(data_file=temp_file)
        
        # 测试所有Tier 2宠物的图像路径
        tier2_pets = ['octopus', 'ribbon', 'sunfish', 'angler']
        
        for pet_id in tier2_pets:
            # 解锁宠物
            dm.unlock_pet(pet_id)
            
            # 测试等级1的图像（baby_idle.png）
            dm.data['pets_data'][pet_id]['level'] = 1
            image_path = dm.get_image_for_level(pet_id, 1)
            expected_path = f"assets/{pet_id}/baby_idle.png"
            assert image_path == expected_path, \
                f"{pet_id} 等级1的图像路径应该是 {expected_path}，但得到 {image_path}"
            
            # 测试等级2的图像（adult_idle.png）
            dm.data['pets_data'][pet_id]['level'] = 2
            image_path = dm.get_image_for_level(pet_id, 2)
            expected_path = f"assets/{pet_id}/adult_idle.png"
            assert image_path == expected_path, \
                f"{pet_id} 等级2的图像路径应该是 {expected_path}，但得到 {image_path}"
            
            # 测试等级3的图像（adult_idle.png）
            dm.data['pets_data'][pet_id]['level'] = 3
            image_path = dm.get_image_for_level(pet_id, 3)
            expected_path = f"assets/{pet_id}/adult_idle.png"
            assert image_path == expected_path, \
                f"{pet_id} 等级3的图像路径应该是 {expected_path}，但得到 {image_path}"
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_tier2_pet_switching():
    """测试Tier 2宠物的切换显示"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # 创建数据管理器（V3格式）
        dm = DataManager(data_file=temp_file)
        
        # 解锁多个Tier 2宠物
        tier2_pets = ['octopus', 'ribbon']
        for pet_id in tier2_pets:
            dm.unlock_pet(pet_id)
        
        # 设置不同的等级
        dm.data['pets_data']['octopus']['level'] = 2
        dm.data['pets_data']['octopus']['tasks_completed_today'] = 1
        dm.data['pets_data']['ribbon']['level'] = 3
        dm.data['pets_data']['ribbon']['tasks_completed_today'] = 2
        dm.save_data()
        
        # 切换到octopus
        dm.set_current_pet_id('octopus')
        assert dm.get_current_pet_id() == 'octopus'
        assert dm.get_level() == 2
        assert dm.get_tasks_completed() == 1
        
        # 切换到ribbon
        dm.set_current_pet_id('ribbon')
        assert dm.get_current_pet_id() == 'ribbon'
        assert dm.get_level() == 3
        assert dm.get_tasks_completed() == 2
        
        # 切换回octopus，验证数据保持不变
        dm.set_current_pet_id('octopus')
        assert dm.get_current_pet_id() == 'octopus'
        assert dm.get_level() == 2
        assert dm.get_tasks_completed() == 1
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_tier2_pet_task_decrement():
    """测试Tier 2宠物的任务减少功能"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # 创建数据管理器（V3格式）
        dm = DataManager(data_file=temp_file)
        
        # 解锁Tier 2宠物
        tier2_pet_id = 'sunfish'
        dm.unlock_pet(tier2_pet_id)
        dm.set_current_pet_id(tier2_pet_id)
        
        # 完成2个任务
        dm.increment_task(tier2_pet_id)
        dm.increment_task(tier2_pet_id)
        assert dm.get_tasks_completed(tier2_pet_id) == 2
        
        # 减少1个任务
        dm.decrement_task(tier2_pet_id)
        assert dm.get_tasks_completed(tier2_pet_id) == 1
        
        # 减少到0
        dm.decrement_task(tier2_pet_id)
        assert dm.get_tasks_completed(tier2_pet_id) == 0
        
        # 验证不会变成负数
        dm.decrement_task(tier2_pet_id)
        assert dm.get_tasks_completed(tier2_pet_id) == 0
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_tier2_pet_data_persistence():
    """测试Tier 2宠物的数据持久化"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # 创建数据管理器（V3格式）
        dm = DataManager(data_file=temp_file)
        
        # 解锁并设置Tier 2宠物
        tier2_pet_id = 'angler'
        dm.unlock_pet(tier2_pet_id)
        dm.set_current_pet_id(tier2_pet_id)
        
        # 设置状态
        dm.data['pets_data'][tier2_pet_id]['level'] = 2
        dm.data['pets_data'][tier2_pet_id]['tasks_completed_today'] = 2
        dm.save_data()
        
        # 创建新的数据管理器实例加载数据
        dm2 = DataManager(data_file=temp_file)
        
        # 验证数据正确持久化
        assert dm2.is_pet_unlocked(tier2_pet_id)
        assert dm2.get_level(tier2_pet_id) == 2
        assert dm2.get_tasks_completed(tier2_pet_id) == 2
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_tier1_and_tier2_pets_independent():
    """测试Tier 1和Tier 2宠物的数据独立性"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # 创建数据管理器（V3格式）
        dm = DataManager(data_file=temp_file)
        
        # 设置Tier 1宠物
        tier1_pet_id = 'puffer'
        dm.data['pets_data'][tier1_pet_id]['level'] = 2
        dm.data['pets_data'][tier1_pet_id]['tasks_completed_today'] = 1
        
        # 解锁并设置Tier 2宠物
        tier2_pet_id = 'octopus'
        dm.unlock_pet(tier2_pet_id)
        dm.data['pets_data'][tier2_pet_id]['level'] = 3
        dm.data['pets_data'][tier2_pet_id]['tasks_completed_today'] = 2
        dm.save_data()
        
        # 修改Tier 2宠物
        dm.set_current_pet_id(tier2_pet_id)
        dm.increment_task(tier2_pet_id)
        
        # 验证Tier 1宠物数据未受影响
        assert dm.get_level(tier1_pet_id) == 2
        assert dm.get_tasks_completed(tier1_pet_id) == 1
        
        # 验证Tier 2宠物数据已更新
        assert dm.get_tasks_completed(tier2_pet_id) == 3
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


# V3.5 版本单元测试

def test_v35_default_data_creation():
    """测试V5.5默认数据创建"""
    with tempfile.NamedTemporaryFile(delete=True, suffix='.json') as f:
        temp_file = f.name
    
    dm = DataManager(data_file=temp_file)
    
    # 验证V5.5数据结构
    assert dm.data['version'] == 5.5
    assert dm.data['current_pet_id'] == 'puffer'
    assert 'active_pets' in dm.data
    assert dm.data['active_pets'] == ['puffer']
    assert 'reward_system' in dm.data
    assert 'inventory_limits' in dm.data
    assert 'tier3_scale_factors' in dm.data
    assert 'tier3_weights' in dm.data
    
    # 验证Tier 3配置
    assert 'tier3' in dm.data['pet_tiers']
    assert len(dm.data['pet_tiers']['tier3']) == 6
    assert 'blobfish' in dm.data['pet_tiers']['tier3']
    
    # 验证所有14种生物的数据
    assert len(dm.data['pets_data']) == 14
    for pet_id in dm.ALL_PETS:
        assert pet_id in dm.data['pets_data']
    
    # 清理
    if os.path.exists(temp_file):
        os.remove(temp_file)


def test_v3_to_v35_migration():
    """测试V3到V3.5数据迁移"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
        v3_data = {
            'version': 3,
            'current_pet_id': 'puffer',
            'unlocked_pets': ['puffer', 'jelly', 'starfish', 'crab', 'octopus'],
            'pet_tiers': {
                'tier1': ['puffer', 'jelly', 'starfish', 'crab'],
                'tier2': ['octopus', 'ribbon', 'sunfish', 'angler']
            },
            'pets_data': {
                'puffer': {
                    'level': 3,
                    'tasks_completed_today': 2,
                    'last_login_date': date.today().isoformat(),
                    'task_states': [True, True, False]
                },
                'jelly': {
                    'level': 1,
                    'tasks_completed_today': 0,
                    'last_login_date': date.today().isoformat(),
                    'task_states': [False, False, False]
                },
                'starfish': {
                    'level': 1,
                    'tasks_completed_today': 0,
                    'last_login_date': date.today().isoformat(),
                    'task_states': [False, False, False]
                },
                'crab': {
                    'level': 1,
                    'tasks_completed_today': 0,
                    'last_login_date': date.today().isoformat(),
                    'task_states': [False, False, False]
                },
                'octopus': {
                    'level': 2,
                    'tasks_completed_today': 1,
                    'last_login_date': date.today().isoformat(),
                    'task_states': [True, False, False]
                },
                'ribbon': {
                    'level': 1,
                    'tasks_completed_today': 0,
                    'last_login_date': date.today().isoformat(),
                    'task_states': [False, False, False]
                },
                'sunfish': {
                    'level': 1,
                    'tasks_completed_today': 0,
                    'last_login_date': date.today().isoformat(),
                    'task_states': [False, False, False]
                },
                'angler': {
                    'level': 1,
                    'tasks_completed_today': 0,
                    'last_login_date': date.today().isoformat(),
                    'task_states': [False, False, False]
                }
            },
            'encounter_settings': {
                'check_interval_minutes': 5,
                'trigger_probability': 0.3,
                'last_encounter_check': date.today().isoformat()
            }
        }
        json.dump(v3_data, f)
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 验证V3.5结构
        assert dm.data['version'] == 3.5
        assert 'active_pets' in dm.data
        assert 'reward_system' in dm.data
        assert 'inventory_limits' in dm.data
        assert 'tier3' in dm.data['pet_tiers']
        
        # 验证原有数据保留
        assert dm.data['current_pet_id'] == 'puffer'
        assert 'octopus' in dm.data['unlocked_pets']
        assert dm.data['pets_data']['puffer']['level'] == 3
        assert dm.data['pets_data']['octopus']['level'] == 2
        
        # 验证活跃宠物初始化
        assert 'puffer' in dm.data['active_pets']
        
        # 验证Tier 3宠物数据创建
        assert 'blobfish' in dm.data['pets_data']
        assert 'bluewhale' in dm.data['pets_data']
        
        # 验证备份文件创建
        backup_file = temp_file + '.v3.backup'
        assert os.path.exists(backup_file)
        
        if os.path.exists(backup_file):
            os.remove(backup_file)
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_active_pets_management():
    """测试活跃宠物列表管理"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 测试获取活跃宠物
        active = dm.get_active_pets()
        assert isinstance(active, list)
        assert 'puffer' in active
        
        # 测试设置活跃宠物
        dm.set_active_pets(['puffer', 'jelly', 'starfish'])
        assert len(dm.get_active_pets()) == 3
        assert 'jelly' in dm.get_active_pets()
        
        # 测试超过上限（应该截断）
        dm.set_active_pets(['puffer', 'jelly', 'starfish', 'crab', 'octopus', 'ribbon'])
        assert len(dm.get_active_pets()) <= dm.MAX_ACTIVE
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_inventory_checks():
    """测试库存检查方法"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 测试库存未满
        assert dm.can_add_to_inventory() == True
        
        # 测试活跃宠物未满
        assert dm.can_activate_pet() == True
        
        # 模拟库存已满
        dm.data['unlocked_pets'] = ['pet' + str(i) for i in range(20)]
        assert dm.can_add_to_inventory() == False
        
        # 模拟活跃宠物已满
        dm.data['active_pets'] = ['pet' + str(i) for i in range(5)]
        assert dm.can_activate_pet() == False
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_cumulative_tasks():
    """测试累计任务计数"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 测试初始值
        assert dm.get_cumulative_tasks() == 0
        
        # 测试增加
        dm.increment_cumulative_tasks()
        assert dm.get_cumulative_tasks() == 1
        
        dm.increment_cumulative_tasks()
        dm.increment_cumulative_tasks()
        assert dm.get_cumulative_tasks() == 3
        
        # 测试重置
        dm.reset_cumulative_tasks()
        assert dm.get_cumulative_tasks() == 0
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_tier3_pet_tier():
    """测试Tier 3宠物层级识别"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 测试Tier 1
        assert dm.get_pet_tier('puffer') == 1
        assert dm.get_pet_tier('jelly') == 1
        
        # 测试Tier 2
        assert dm.get_pet_tier('octopus') == 2
        assert dm.get_pet_tier('angler') == 2
        
        # 测试Tier 3
        assert dm.get_pet_tier('blobfish') == 3
        assert dm.get_pet_tier('bluewhale') == 3
        
        # 测试获取Tier 3宠物列表
        tier3_pets = dm.get_tier_pets(3)
        assert len(tier3_pets) == 6
        assert 'blobfish' in tier3_pets
        assert 'bluewhale' in tier3_pets
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_tier3_image_path():
    """测试Tier 3宠物图像路径"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 测试Tier 1/2宠物图像路径
        assert dm.get_image_for_level('puffer', 1) == 'assets/puffer/baby_idle.png'
        assert dm.get_image_for_level('puffer', 2) == 'assets/puffer/adult_idle.png'
        assert dm.get_image_for_level('octopus', 1) == 'assets/octopus/baby_idle.png'
        
        # 测试Tier 3宠物图像路径（无等级区分）
        assert dm.get_image_for_level('blobfish', 1) == 'assets/deep_sea/blobfish/idle.png'
        assert dm.get_image_for_level('bluewhale', 1) == 'assets/deep_sea/bluewhale/idle.png'
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_tier3_unlock_conditions():
    """测试Tier 3宠物解锁条件"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 测试Tier 3解锁条件
        assert dm.get_unlock_condition('blobfish') == '通过深海盲盒获得'
        assert dm.get_unlock_condition('bluewhale') == '通过深海盲盒获得'
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


# V5.5 版本单元测试 - 昼夜设置

def test_day_night_settings_default():
    """测试昼夜设置的默认值"""
    with tempfile.NamedTemporaryFile(delete=True, suffix='.json') as f:
        temp_file = f.name
    
    dm = DataManager(data_file=temp_file)
    
    # 验证默认值
    assert dm.get_auto_time_sync() == True, "auto_time_sync 默认应该为 True"
    assert dm.get_current_day_night_mode() == 'day', "current_mode 默认应该为 'day'"
    
    # 验证数据结构
    assert 'day_night_settings' in dm.data
    assert dm.data['day_night_settings']['auto_time_sync'] == True
    assert dm.data['day_night_settings']['current_mode'] == 'day'
    
    # 清理
    if os.path.exists(temp_file):
        os.remove(temp_file)


def test_day_night_settings_read_write():
    """测试昼夜设置的读写功能"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 测试设置 auto_time_sync
        dm.set_auto_time_sync(False)
        assert dm.get_auto_time_sync() == False
        
        dm.set_auto_time_sync(True)
        assert dm.get_auto_time_sync() == True
        
        # 测试设置 current_mode
        dm.set_current_day_night_mode('night')
        assert dm.get_current_day_night_mode() == 'night'
        
        dm.set_current_day_night_mode('day')
        assert dm.get_current_day_night_mode() == 'day'
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_day_night_settings_invalid_mode():
    """测试设置无效的昼夜模式"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 设置有效模式
        dm.set_current_day_night_mode('night')
        assert dm.get_current_day_night_mode() == 'night'
        
        # 尝试设置无效模式（应该被拒绝）
        dm.set_current_day_night_mode('invalid')
        assert dm.get_current_day_night_mode() == 'night', "无效模式应该被拒绝"
        
        dm.set_current_day_night_mode('')
        assert dm.get_current_day_night_mode() == 'night', "空字符串应该被拒绝"
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_day_night_settings_persistence():
    """测试昼夜设置的持久化"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # 创建并设置
        dm = DataManager(data_file=temp_file)
        dm.set_auto_time_sync(False)
        dm.set_current_day_night_mode('night')
        
        # 创建新实例验证持久化
        dm2 = DataManager(data_file=temp_file)
        assert dm2.get_auto_time_sync() == False
        assert dm2.get_current_day_night_mode() == 'night'
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_v35_to_v55_migration():
    """测试V3.5到V5.5数据迁移"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
        # 创建V3.5格式数据（不包含day_night_settings）
        v35_data = {
            'version': 3.5,
            'current_pet_id': 'puffer',
            'unlocked_pets': ['puffer', 'jelly', 'starfish', 'crab'],
            'active_pets': ['puffer'],
            'pet_tiers': {
                'tier1': ['puffer', 'jelly', 'starfish', 'crab'],
                'tier2': ['octopus', 'ribbon', 'sunfish', 'angler'],
                'tier3': ['blobfish', 'ray', 'beluga', 'orca', 'shark', 'bluewhale']
            },
            'tier3_scale_factors': {
                'blobfish': 1.5, 'ray': 2.0, 'beluga': 2.5,
                'orca': 3.0, 'shark': 3.5, 'bluewhale': 5.0
            },
            'tier3_weights': {
                'blobfish': 0.40, 'ray': 0.25, 'beluga': 0.15,
                'orca': 0.10, 'shark': 0.08, 'bluewhale': 0.02
            },
            'reward_system': {
                'cumulative_tasks_completed': 5,
                'reward_threshold': 12,
                'tier2_unlock_probability': 0.7,
                'lootbox_probability': 0.3
            },
            'inventory_limits': {
                'max_inventory': 20,
                'max_active': 5
            },
            'pets_data': {
                'puffer': {
                    'level': 2,
                    'tasks_completed_today': 1,
                    'last_login_date': date.today().isoformat(),
                    'task_states': [True, False, False]
                }
            },
            'encounter_settings': {
                'check_interval_minutes': 5,
                'trigger_probability': 0.3,
                'last_encounter_check': date.today().isoformat()
            }
        }
        json.dump(v35_data, f)
    
    try:
        # 创建数据管理器（应该自动迁移）
        dm = DataManager(data_file=temp_file)
        
        # 验证版本升级
        assert dm.data['version'] == 5.5
        
        # 验证昼夜设置已添加
        assert 'day_night_settings' in dm.data
        assert dm.data['day_night_settings']['auto_time_sync'] == True
        assert dm.data['day_night_settings']['current_mode'] == 'day'
        
        # 验证原有数据保留
        assert dm.data['current_pet_id'] == 'puffer'
        assert dm.data['reward_system']['cumulative_tasks_completed'] == 5
        assert dm.data['pets_data']['puffer']['level'] == 2
        
        # 验证备份文件创建
        backup_file = temp_file + '.v3.5.backup'
        assert os.path.exists(backup_file)
        
        # 清理备份文件
        if os.path.exists(backup_file):
            os.remove(backup_file)
            
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_day_night_settings_startup_load():
    """测试启动时加载昼夜设置"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # 第一次启动，设置为夜间模式
        dm1 = DataManager(data_file=temp_file)
        dm1.set_auto_time_sync(False)
        dm1.set_current_day_night_mode('night')
        
        # 模拟重启应用
        dm2 = DataManager(data_file=temp_file)
        
        # 验证启动时正确加载设置
        assert dm2.get_auto_time_sync() == False, "启动时应该加载保存的 auto_time_sync"
        assert dm2.get_current_day_night_mode() == 'night', "启动时应该加载保存的 current_mode"
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_day_night_settings_missing_field():
    """测试缺少昼夜设置字段时的默认值处理"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        dm = DataManager(data_file=temp_file)
        
        # 手动删除day_night_settings字段
        del dm.data['day_night_settings']
        
        # 验证get方法返回默认值
        assert dm.get_auto_time_sync() == True, "缺少字段时应该返回默认值 True"
        assert dm.get_current_day_night_mode() == 'day', "缺少字段时应该返回默认值 'day'"
        
        # 验证set方法会创建字段
        dm.set_auto_time_sync(False)
        assert 'day_night_settings' in dm.data
        assert dm.data['day_night_settings']['auto_time_sync'] == False
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

