"""
logic_growth.py - V6 Stable Growth State Machine

WARNING: This module governs the lifecycle of creatures from the deep...

Three-stage lifecycle management:
- State 0: Dormant/Weak - Fixed at bottom, grayscale filter
- State 1: Baby - Free floating, normal display
- State 2: Adult - Full form, all features unlocked

State transition rules:
- 0 → 1: Complete 1 task
- 1 → 2: Complete 3 tasks total
- Reset: Any state → 0
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class PetData:
    """Single pet data structure."""
    state: int = 0  # 0=Dormant, 1=Baby, 2=Adult
    tasks_progress: int = 0  # Tasks completed in current cycle


@dataclass 
class Settings:
    """Application settings."""
    auto_time_sync: bool = True
    theme_mode: str = "normal"  # "normal" or "halloween"


# V6.1 Constants
MAX_INVENTORY = 20  # Inventory limit
MAX_ACTIVE = 5      # Desktop display limit
REWARD_THRESHOLD = 12  # Trigger reward every 12 tasks

# V8: Task count config - Ray SSR requires more tasks
TASK_CONFIG = {
    "ray": {
        "dormant_to_baby": 2,  # Awakening requires 2 tasks
        "baby_to_adult": 3,    # Adult requires 3 more tasks (5 total)
    },
    "default": {
        "dormant_to_baby": 1,  # Awakening requires 1 task
        "baby_to_adult": 2,    # Adult requires 2 more tasks (3 total)
    }
}


class GrowthManager:
    """
    Growth State Machine Manager.
    
    WARNING: This manager controls the lifecycle of creatures from the abyss...
    
    Manages pet three-stage lifecycle and task progress.
    Data auto-persists to data.json.
    """
    
    # State constants
    STATE_DORMANT = 0  # Dormant
    STATE_BABY = 1     # Baby
    STATE_ADULT = 2    # Adult
    
    # Evolution thresholds
    THRESHOLD_TO_BABY = 1   # Complete 1 task → Baby
    THRESHOLD_TO_ADULT = 3  # Complete 3 tasks total → Adult
    
    def __init__(self, data_file: str = "data.json"):
        """
        初始化成长管理器
        
        Args:
            data_file: 数据文件路径
        """
        self.data_file = data_file
        self.pets: Dict[str, PetData] = {}
        self.settings = Settings()
        
        # V6.1: 库存和活跃列表
        self.unlocked_pets: list = ['puffer']  # 已解锁宠物
        self.active_pets: list = ['puffer']    # 桌面显示宠物
        self.cumulative_tasks: int = 0         # 累计任务数（用于奖励）
        
        self._load()
    
    def _load(self) -> None:
        """从文件加载数据，失败时使用默认值"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 加载宠物数据
                pets_data = data.get('pets', {})
                for pet_id, pet_info in pets_data.items():
                    self.pets[pet_id] = PetData(
                        state=pet_info.get('state', 0),
                        tasks_progress=pet_info.get('tasks_progress', 0)
                    )
                
                # 加载设置
                settings_data = data.get('settings', {})
                self.settings = Settings(
                    auto_time_sync=settings_data.get('auto_time_sync', True),
                    theme_mode=settings_data.get('theme_mode', 'normal')
                )
                
                # V6.1: 加载库存数据
                self.unlocked_pets = data.get('unlocked_pets', ['puffer'])
                self.active_pets = data.get('active_pets', self.unlocked_pets[:MAX_ACTIVE])
                self.cumulative_tasks = data.get('cumulative_tasks', 0)
                
                # V7.1: 加载自定义任务文本
                self.custom_task_texts = data.get('custom_task_texts', [])
                
        except (json.JSONDecodeError, IOError, KeyError) as e:
            print(f"[GrowthManager] Failed to load data, using defaults: {e}")
            self._init_default()
    
    def _init_default(self) -> None:
        """初始化默认数据"""
        self.pets = {
            'puffer': PetData(state=0, tasks_progress=0)
        }
        self.settings = Settings()
        self.custom_task_texts = []  # V7.1: 自定义任务文本
    
    def save(self) -> None:
        """保存数据到文件"""
        try:
            data = {
                'pets': {
                    pet_id: asdict(pet_data) 
                    for pet_id, pet_data in self.pets.items()
                },
                'settings': asdict(self.settings),
                'unlocked_pets': self.unlocked_pets,
                'active_pets': self.active_pets,
                'cumulative_tasks': self.cumulative_tasks,
                'custom_task_texts': getattr(self, 'custom_task_texts', []),  # V7.1
                'last_saved': datetime.now().isoformat()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"[GrowthManager] Failed to save data: {e}")
    
    def _ensure_pet(self, pet_id: str) -> PetData:
        """确保宠物数据存在，不存在则创建"""
        if pet_id not in self.pets:
            self.pets[pet_id] = PetData()
        return self.pets[pet_id]
    
    def get_state(self, pet_id: str) -> int:
        """
        获取宠物当前状态
        
        Args:
            pet_id: 宠物ID
            
        Returns:
            状态值 (0=休眠, 1=幼年, 2=成年)
        """
        return self._ensure_pet(pet_id).state
    
    def get_progress(self, pet_id: str) -> int:
        """
        获取宠物任务进度
        
        Args:
            pet_id: 宠物ID
            
        Returns:
            已完成任务数
        """
        return self._ensure_pet(pet_id).tasks_progress
    
    def complete_task(self, pet_id: str) -> int:
        """
        完成一个任务，自动处理状态转换
        
        V8: 使用 get_tasks_to_next_state() 获取阈值
        - Ray (SSR): dormant→baby 需要 2 任务, baby→adult 需要 3 任务 (共 5)
        - 其他宠物: dormant→baby 需要 1 任务, baby→adult 需要 2 任务 (共 3)
        
        Args:
            pet_id: 宠物ID
            
        Returns:
            新的状态值
        
        Requirements: 3.1, 3.2, 3.3, 3.4
        """
        pet = self._ensure_pet(pet_id)
        
        # 增加任务进度
        pet.tasks_progress += 1
        
        # V8: 获取当前状态到下一状态需要的任务数
        tasks_needed = self.get_tasks_to_next_state(pet_id)
        
        # 检查状态转换
        if pet.state == self.STATE_DORMANT:
            # 休眠 → 幼年: 使用 TASK_CONFIG 阈值
            if pet.tasks_progress >= tasks_needed:
                pet.state = self.STATE_BABY
                print(f"[GrowthManager] {pet_id} awakened! Dormant → Baby (required {tasks_needed} tasks)")
        
        elif pet.state == self.STATE_BABY:
            # 幼年 → 成年: 使用 TASK_CONFIG 阈值
            # 获取配置来计算总任务数阈值
            config_key = "ray" if pet_id == "ray" else "default"
            config = TASK_CONFIG[config_key]
            total_to_adult = config["dormant_to_baby"] + config["baby_to_adult"]
            
            if pet.tasks_progress >= total_to_adult:
                pet.state = self.STATE_ADULT
                print(f"[GrowthManager] {pet_id} evolved! Baby → Adult (total {total_to_adult} tasks)")
        
        # 自动保存
        self.save()
        
        return pet.state
    
    def reset_cycle(self, pet_id: str) -> None:
        """
        重置宠物周期（回到休眠状态）
        
        Args:
            pet_id: 宠物ID
        """
        pet = self._ensure_pet(pet_id)
        pet.state = self.STATE_DORMANT
        pet.tasks_progress = 0
        self.save()
        print(f"[GrowthManager] {pet_id} cycle reset")
    
    def get_image_stage(self, pet_id: str) -> str:
        """
        根据状态获取应加载的图像阶段名
        
        Args:
            pet_id: 宠物ID
            
        Returns:
            图像阶段名 ("baby" 或 "adult")
        """
        state = self.get_state(pet_id)
        if state == self.STATE_ADULT:
            return "adult"
        else:
            return "baby"  # 休眠和幼年都用 baby 图像
    
    def is_dormant(self, pet_id: str) -> bool:
        """检查宠物是否处于休眠状态"""
        return self.get_state(pet_id) == self.STATE_DORMANT
    
    def get_tasks_to_next_state(self, pet_id: str) -> int:
        """
        V8: 获取到下一状态需要的任务数
        
        Ray (SSR) 需要更多任务：
        - dormant → baby: 2 tasks (vs 1 for others)
        - baby → adult: 3 tasks (vs 2 for others)
        
        Args:
            pet_id: 宠物ID
            
        Returns:
            需要的任务数 (Ray 返回 2/3, 其他返回 1/2, adult 返回 0)
        
        Requirements: 3.5
        """
        state = self.get_state(pet_id)
        
        # 获取配置 (ray 用特殊配置，其他用 default)
        config_key = "ray" if pet_id == "ray" else "default"
        config = TASK_CONFIG[config_key]
        
        if state == self.STATE_DORMANT:  # dormant -> baby
            return config["dormant_to_baby"]
        elif state == self.STATE_BABY:  # baby -> adult
            return config["baby_to_adult"]
        return 0  # adult 状态无需更多任务
    
    def get_all_pets(self) -> list:
        """获取所有宠物ID列表"""
        return list(self.pets.keys())
    
    # 设置相关方法
    def get_theme_mode(self) -> str:
        """获取当前主题模式"""
        return self.settings.theme_mode
    
    def set_theme_mode(self, mode: str) -> None:
        """设置主题模式"""
        self.settings.theme_mode = mode
        self.save()
    
    def get_auto_time_sync(self) -> bool:
        """获取自动时间同步设置"""
        return self.settings.auto_time_sync
    
    def set_auto_time_sync(self, enabled: bool) -> None:
        """设置自动时间同步"""
        self.settings.auto_time_sync = enabled
        self.save()
    
    # ========== V6.1 库存系统 ==========
    
    def get_unlocked_pets(self) -> list:
        """获取已解锁的宠物列表"""
        return self.unlocked_pets.copy()
    
    def get_active_pets(self) -> list:
        """获取当前活跃的宠物列表"""
        return self.active_pets.copy()
    
    def set_active_pets(self, pets: list) -> None:
        """设置活跃宠物列表"""
        # 限制数量
        self.active_pets = pets[:MAX_ACTIVE]
        self.save()
    
    def add_pet(self, pet_id: str) -> bool:
        """
        添加新宠物到库存
        
        V16: New pets from gacha start as Dormant (state=0) and appear on screen.
        User needs to complete tasks to awaken them.
        
        Args:
            pet_id: Pet ID to add
        
        Returns:
            是否添加成功
        """
        if len(self.unlocked_pets) >= MAX_INVENTORY:
            print(f"[GrowthManager] Inventory full, cannot add {pet_id}")
            return False
        
        if pet_id not in self.unlocked_pets:
            # New pet - add to inventory
            self.unlocked_pets.append(pet_id)
            pet = self._ensure_pet(pet_id)
            
            # V16: New pets start as Dormant (need to complete tasks to awaken)
            pet.state = self.STATE_DORMANT
            pet.tasks_progress = 0
            
            # V16: Add to active_pets if not full (so it shows on screen)
            if len(self.active_pets) < MAX_ACTIVE and pet_id not in self.active_pets:
                self.active_pets.append(pet_id)
            
            self.save()
            print(f"[GrowthManager] Added new pet as Dormant: {pet_id}")
            return True
        else:
            # V16: Pet already exists - reset to Dormant state
            pet = self._ensure_pet(pet_id)
            pet.state = self.STATE_DORMANT
            pet.tasks_progress = 0
            
            # V16: Ensure it's in active_pets
            if len(self.active_pets) < MAX_ACTIVE and pet_id not in self.active_pets:
                self.active_pets.append(pet_id)
            
            self.save()
            print(f"[GrowthManager] Reset existing pet to Dormant: {pet_id}")
            return True
    
    def release_pet(self, pet_id: str) -> bool:
        """
        放生宠物
        
        Returns:
            是否放生成功
        """
        if pet_id == 'puffer':
            print("[GrowthManager] Cannot release base pet puffer")
            return False
        
        if pet_id in self.unlocked_pets:
            self.unlocked_pets.remove(pet_id)
        if pet_id in self.active_pets:
            self.active_pets.remove(pet_id)
        if pet_id in self.pets:
            del self.pets[pet_id]
        
        self.save()
        print(f"[GrowthManager] Released pet: {pet_id}")
        return True
    
    def can_add_pet(self) -> bool:
        """检查是否可以添加新宠物"""
        return len(self.unlocked_pets) < MAX_INVENTORY
    
    # ========== V6.1 奖励系统 ==========
    
    def increment_cumulative_tasks(self) -> int:
        """
        增加累计任务数
        
        Returns:
            当前累计任务数
        """
        self.cumulative_tasks += 1
        self.save()
        return self.cumulative_tasks
    
    def check_reward(self) -> bool:
        """
        检查是否触发奖励
        
        Returns:
            是否触发奖励
        """
        return self.cumulative_tasks >= REWARD_THRESHOLD
    
    def reset_cumulative_tasks(self) -> None:
        """重置累计任务数"""
        self.cumulative_tasks = 0
        self.save()
    
    # ========== V7.1 自定义任务文本 ==========
    
    def get_custom_task_texts(self) -> list:
        """
        获取自定义任务文本
        
        Returns:
            自定义任务文本列表，如果没有保存则返回空列表
        
        Requirements: 4.4
        """
        return getattr(self, 'custom_task_texts', []).copy()
    
    def set_custom_task_texts(self, texts: list) -> None:
        """
        设置自定义任务文本
        
        Args:
            texts: 任务文本列表
        
        Requirements: 4.2, 4.4
        """
        # 过滤空文本
        self.custom_task_texts = [t for t in texts if t.strip()]
        self.save()
