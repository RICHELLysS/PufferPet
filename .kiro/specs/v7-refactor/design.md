# Design Document: PufferPet V7 Refactor

## Overview

V7精简版重构基于5只保留宠物（puffer, jelly, crab, starfish, ray）重新设计代码架构。核心改进包括：
- 几何图形占位符系统：当图片缺失时绘制特定形状
- 体型缩放规则：基于成长阶段和种族的尺寸计算
- Minecraft风格背包UI：2列网格布局
- 调整后的盲盒概率系统

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      pet_config.py (NEW)                     │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  V7_PETS = ['puffer', 'jelly', 'crab', 'starfish', 'ray']│
│  │  PET_SHAPES = { pet_id: (shape, color) }                ││
│  │  PET_SIZES = { pet_id: base_multiplier }                ││
│  │  GACHA_WEIGHTS = { pet_id: probability }                ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   pet_core.py   │ │ ui_inventory.py │ │   ui_gacha.py   │
│  PetRenderer    │ │  MC-style Grid  │ │  Updated Pool   │
│  GeometryDraw   │ │  2x10 Layout    │ │  New Weights    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Components and Interfaces

### 1. pet_config.py (新建配置模块)

```python
# V7 宠物列表
V7_PETS = ['puffer', 'jelly', 'crab', 'starfish', 'ray']

# 尺寸常量
BASE_SIZE = 100  # 基准尺寸
ADULT_MULTIPLIER = 1.5  # 成年倍率
RAY_MULTIPLIER = 1.5  # 鳐鱼种族优势

# 形状映射 (shape_type, color_hex)
PET_SHAPES = {
    'puffer': ('circle', '#90EE90'),      # 绿色圆形
    'jelly': ('triangle', '#FFB6C1'),     # 粉色三角形
    'crab': ('rectangle', '#FF6B6B'),     # 红色长方形
    'starfish': ('pentagon', '#FFD700'),  # 黄色五边形
    'ray': ('diamond', '#4682B4'),        # 蓝色菱形
}

# 盲盒概率 (总和100)
GACHA_WEIGHTS = {
    'puffer': 22,
    'jelly': 22,
    'crab': 22,
    'starfish': 22,
    'ray': 12,  # SSR
}

# 背包常量
MAX_INVENTORY = 20
MAX_ACTIVE = 5
GRID_COLUMNS = 2
```

### 2. pet_core.py 更新

```python
class PetRenderer:
    """几何图形渲染器"""
    
    @staticmethod
    def calculate_size(pet_id: str, stage: str) -> int:
        """计算宠物尺寸"""
        base = BASE_SIZE
        # 种族优势
        if pet_id == 'ray':
            base *= RAY_MULTIPLIER
        # 成长阶段
        if stage == 'adult':
            base *= ADULT_MULTIPLIER
        return int(base)
    
    @staticmethod
    def draw_placeholder(pet_id: str, size: int) -> QPixmap:
        """绘制几何占位符"""
        shape, color = PET_SHAPES.get(pet_id, ('circle', '#888888'))
        # 根据shape类型绘制对应图形
        ...
    
    @staticmethod
    def draw_circle(painter, rect, color): ...
    @staticmethod
    def draw_triangle(painter, rect, color): ...
    @staticmethod
    def draw_rectangle(painter, rect, color): ...
    @staticmethod
    def draw_pentagon(painter, rect, color): ...
    @staticmethod
    def draw_diamond(painter, rect, color): ...
```

### 3. ui_inventory.py 重写 (MC风格)

```python
class MCInventoryWindow(QDialog):
    """Minecraft风格背包窗口"""
    
    def _setup_ui(self):
        # 2列网格布局
        self.grid = QGridLayout()
        self.grid.setSpacing(4)
        
        # 创建20个格子
        for i in range(MAX_INVENTORY):
            row, col = i // GRID_COLUMNS, i % GRID_COLUMNS
            slot = self._create_slot(i)
            self.grid.addWidget(slot, row, col)
    
    def _create_slot(self, index: int) -> QFrame:
        """创建MC风格格子"""
        slot = QFrame()
        slot.setStyleSheet("""
            QFrame {
                background: #8B8B8B;
                border: 2px solid #C6C6C6;
                min-width: 64px;
                min-height: 64px;
            }
            QFrame:hover {
                border-color: white;
            }
        """)
        return slot
```

### 4. ui_gacha.py 更新

```python
# 使用新的概率配置
from pet_config import GACHA_WEIGHTS, V7_PETS

def roll_gacha() -> str:
    """按V7概率抽取宠物"""
    total = sum(GACHA_WEIGHTS.values())  # 100
    roll = random.randint(1, total)
    
    cumulative = 0
    for pet_id in V7_PETS:
        cumulative += GACHA_WEIGHTS[pet_id]
        if roll <= cumulative:
            return pet_id
    return 'puffer'
```

## Data Models

### 宠物尺寸计算

| Pet ID | Base Size | Baby Size | Adult Size |
|--------|-----------|-----------|------------|
| puffer | 100px | 100px | 150px |
| jelly | 100px | 100px | 150px |
| crab | 100px | 100px | 150px |
| starfish | 100px | 100px | 150px |
| ray | 150px | 150px | 225px |

### 盲盒概率分布

| Pet ID | Probability | Rarity |
|--------|-------------|--------|
| puffer | 22% | Common |
| jelly | 22% | Common |
| crab | 22% | Common |
| starfish | 22% | Common |
| ray | 12% | SSR |

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Placeholder Generation for Missing Images
*For any* pet_id in V7_PETS, when image loading fails, the system shall return a valid QPixmap with the correct geometric shape and color for that pet.
**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6**

### Property 2: Pet Size Calculation Correctness
*For any* pet_id and stage combination, the calculated size shall equal BASE_SIZE × species_multiplier × stage_multiplier, where species_multiplier is 1.5 for ray and 1.0 for others, and stage_multiplier is 1.5 for adult and 1.0 for baby.
**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

### Property 3: Gacha Probability Sum
*For any* gacha pool configuration, the sum of all pet probabilities shall equal exactly 100%.
**Validates: Requirements 5.2, 5.3, 5.4**

### Property 4: Inventory Capacity Enforcement
*For any* inventory state, the number of stored pets shall not exceed MAX_INVENTORY (20), and the number of active desktop pets shall not exceed MAX_ACTIVE (5).
**Validates: Requirements 4.5, 4.7**

### Property 5: Desktop Toggle Consistency
*For any* pet toggle action, if a pet is toggled to desktop and desktop count is below MAX_ACTIVE, the pet shall appear on desktop; if toggled to inventory, the pet shall be removed from desktop.
**Validates: Requirements 4.6**

### Property 6: Lifecycle Stage Size Transition
*For any* pet transitioning from baby to adult stage, the pet size shall increase by exactly 1.5x multiplier.
**Validates: Requirements 6.3**

## Error Handling

| Error Scenario | Handling Strategy |
|----------------|-------------------|
| Image file missing | Generate geometric placeholder |
| Image file empty (0 bytes) | Generate geometric placeholder |
| Invalid pet_id | Default to puffer shape/color |
| Inventory full | Reject add operation, show message |
| Desktop full | Reject toggle, show message |

## Testing Strategy

### Unit Tests
- Test shape/color mapping for each pet
- Test size calculation for all pet/stage combinations
- Test gacha probability values
- Test inventory slot creation

### Property-Based Tests
使用 `hypothesis` 库进行属性测试：

1. **Property 1 Test**: 对所有V7_PETS，验证占位符生成返回有效QPixmap
2. **Property 2 Test**: 对所有pet_id和stage组合，验证尺寸计算公式正确
3. **Property 3 Test**: 验证GACHA_WEIGHTS总和为100
4. **Property 4 Test**: 模拟添加宠物操作，验证容量限制
5. **Property 5 Test**: 模拟toggle操作，验证状态一致性
6. **Property 6 Test**: 模拟阶段转换，验证尺寸变化

每个属性测试配置运行至少100次迭代。

测试文件格式：
```python
# tests/test_v7_refactor.py
# **Feature: v7-refactor, Property 2: Pet Size Calculation Correctness**
@given(pet_id=st.sampled_from(V7_PETS), stage=st.sampled_from(['baby', 'adult']))
def test_pet_size_calculation(pet_id, stage):
    size = PetRenderer.calculate_size(pet_id, stage)
    expected = BASE_SIZE
    if pet_id == 'ray':
        expected *= RAY_MULTIPLIER
    if stage == 'adult':
        expected *= ADULT_MULTIPLIER
    assert size == int(expected)
```
