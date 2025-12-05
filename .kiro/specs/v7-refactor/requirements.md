# Requirements Document

## Introduction

本功能实现 PufferPet V7 精简版重构，基于剩余的5只宠物（puffer, jelly, crab, starfish, ray）重新设计代码架构。核心改进包括：几何图形占位符系统（当图片缺失时绘制特定形状）、体型缩放规则、Minecraft风格的背包UI、以及调整后的盲盒概率系统。

## Glossary

- **V7_PETS**: 保留的5只宠物列表 - puffer, jelly, crab, starfish, ray
- **几何占位符**: 当宠物图片缺失时，使用QPainter绘制的特定几何图形替代
- **BASE_SIZE**: 基准尺寸，设为100像素
- **体型缩放**: Adult尺寸 = Baby尺寸 × 1.5
- **种族优势**: ray的基础尺寸是其他宠物的1.5倍
- **MC风格背包**: 模仿Minecraft物品栏的2列网格布局
- **呼吸特效**: 通过Scale缩放实现的动画效果
- **悬浮特效**: 通过Y轴正弦运动实现的漂浮动画

## Requirements

### Requirement 1

**User Story:** As a developer, I want a geometry placeholder system, so that pets display correctly even when image assets are missing.

#### Acceptance Criteria

1. WHEN the system loads a pet image and the file is missing or empty THEN the PetWidget SHALL render a geometric shape placeholder instead of showing an error
2. WHEN rendering jelly placeholder THEN the system SHALL draw a pink triangle (#FFB6C1)
3. WHEN rendering crab placeholder THEN the system SHALL draw a red rectangle (#FF6B6B)
4. WHEN rendering starfish placeholder THEN the system SHALL draw a yellow pentagon (#FFD700)
5. WHEN rendering ray placeholder THEN the system SHALL draw a blue diamond (#4682B4)
6. WHEN rendering puffer placeholder THEN the system SHALL draw a green circle (#90EE90)

### Requirement 2

**User Story:** As a user, I want pets to have appropriate sizes based on their growth stage and species, so that the visual hierarchy is clear.

#### Acceptance Criteria

1. WHEN a pet is in Baby stage THEN the pet size SHALL be BASE_SIZE (100px) for standard pets
2. WHEN a pet is in Adult stage THEN the pet size SHALL be Baby size multiplied by 1.5 (150px for standard pets)
3. WHEN the pet is ray THEN the base size SHALL be 1.5 times larger than other pets (Baby=150px, Adult=225px)
4. WHEN pet size is calculated THEN the system SHALL apply both stage multiplier and species multiplier correctly

### Requirement 3

**User Story:** As a user, I want geometric placeholders to have breathing and floating animations, so that they appear alive.

#### Acceptance Criteria

1. WHEN a geometric placeholder is displayed THEN the system SHALL apply breathing effect (scale oscillation)
2. WHEN a geometric placeholder is displayed THEN the system SHALL apply floating effect (Y-axis sine wave motion)
3. WHEN animations are applied THEN the geometric shapes SHALL animate smoothly without visual glitches

### Requirement 4

**User Story:** As a user, I want a Minecraft-style inventory UI, so that managing pets feels like a game interface.

#### Acceptance Criteria

1. WHEN the inventory window opens THEN the layout SHALL display as a 2-column grid with dynamic rows
2. WHEN inventory slots are rendered THEN each slot SHALL have dark gray background (#8B8B8B) and light gray border (#C6C6C6)
3. WHEN a slot is selected THEN the border SHALL change to white or highlighted color
4. WHEN a pet icon is displayed THEN the slot SHALL show default_icon or a miniature geometric placeholder
5. WHEN inventory capacity is checked THEN the maximum SHALL be 20 slots total
6. WHEN a slot is clicked THEN the system SHALL toggle the pet between desktop display and inventory storage
7. WHEN desktop pet count is checked THEN the maximum SHALL be 5 pets displayed simultaneously

### Requirement 5

**User Story:** As a user, I want the gacha system to only include the 5 remaining pets with adjusted probabilities, so that rewards are balanced.

#### Acceptance Criteria

1. WHEN gacha pool is accessed THEN the pool SHALL contain only puffer, jelly, crab, starfish, and ray
2. WHEN gacha probability is calculated THEN puffer, jelly, crab, and starfish SHALL each have 22% chance
3. WHEN gacha probability is calculated THEN ray (SSR) SHALL have 12% chance
4. WHEN all probabilities are summed THEN the total SHALL equal 100%

### Requirement 6

**User Story:** As a user, I want the dormant-baby-adult lifecycle to continue working, so that pet progression remains meaningful.

#### Acceptance Criteria

1. WHEN a pet is dormant THEN the pet SHALL be positioned at screen bottom and display grayscale filter
2. WHEN a pet transitions from dormant to baby THEN the pet SHALL become draggable and display normal colors
3. WHEN a pet transitions from baby to adult THEN the pet size SHALL increase by 1.5x multiplier
