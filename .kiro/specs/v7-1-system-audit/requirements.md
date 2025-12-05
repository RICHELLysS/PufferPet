# Requirements Document

## Introduction

V7.1 全系统逻辑验收 (System Audit & Logic Freeze) 是在导入美术素材前的最终代码版本。本阶段暂停所有新功能开发，专注于确保所有模块的代码逻辑严密、无 Bug，并能通过"几何占位符"完美演示所有功能。

## Glossary

- **愤怒机制 (Anger Logic)**: 2秒内连续点击5次触发的宠物状态，表现为红色几何图形剧烈抖动
- **拖拽物理 (Drag Physics)**: 拖拽时的挤压拉伸 (Squash & Stretch) 效果
- **休眠状态 (Dormant)**: 宠物位于屏幕底部，灰色半透明，不可拖拽
- **生命周期 (Lifecycle)**: 休眠 → 幼年 → 成年的三阶段成长系统
- **盲盒 (Gacha)**: 累计12个任务后触发的抽奖系统
- **几何占位符 (Geometry Placeholder)**: 使用 QPainter 绘制的带描边和高光的几何图形
- **像素风 QSS**: V6.5 定义的直角、粗边框、等宽字体的 UI 风格
- **SoundManager**: 音效管理器，使用 QApplication.beep() 作为临时反馈

## Requirements

### Requirement 1: 愤怒机制

**User Story:** As a user, I want my pet to react when I click it too many times, so that the interaction feels more alive and responsive.

#### Acceptance Criteria

1. WHEN a user clicks the pet 5 times within 2 seconds THEN the PetWidget SHALL transition to ANGRY state
2. WHEN the pet enters ANGRY state THEN the geometric placeholder SHALL change to red color (#FF0000)
3. WHEN the pet is in ANGRY state THEN the PetWidget SHALL display a shake animation (left-right oscillation)
4. WHEN the pet has been in ANGRY state for 5 seconds THEN the PetWidget SHALL automatically return to normal state
5. WHEN the pet returns to normal state THEN the geometric placeholder SHALL restore its original color

### Requirement 2: 拖拽物理

**User Story:** As a user, I want dragging the pet to feel responsive with squash and stretch effects, so that the interaction feels more natural.

#### Acceptance Criteria

1. WHEN a user starts dragging a non-dormant pet THEN the PetWidget SHALL apply a squash effect (horizontal compression)
2. WHEN a user is dragging the pet THEN the squash factor SHALL vary based on drag speed
3. WHEN a user releases the pet after dragging THEN the PetWidget SHALL animate back to normal shape (stretch recovery)
4. WHEN a pet is in dormant state THEN the PetWidget SHALL prevent all drag operations

### Requirement 3: 右键菜单

**User Story:** As a user, I want a context menu with all pet management options, so that I can easily access pet features.

#### Acceptance Criteria

1. WHEN a user right-clicks on the pet THEN the PetWidget SHALL display a context menu
2. WHEN the context menu is displayed THEN the menu SHALL include "任务设置" option
3. WHEN the context menu is displayed THEN the menu SHALL include "打开背包" option
4. WHEN the context menu is displayed THEN the menu SHALL include "环境设置(昼夜)" option
5. WHEN the pet is not the basic puffer THEN the context menu SHALL include "放生" option

### Requirement 4: 任务自定义

**User Story:** As a user, I want to customize my task descriptions, so that I can track my own personal goals.

#### Acceptance Criteria

1. WHEN the task window is displayed THEN each task SHALL have an editable text field
2. WHEN a user modifies a task description THEN the TaskWindow SHALL save the new text to data.json
3. WHEN a task is completed THEN the SoundManager SHALL play a completion sound
4. WHEN the task window is reopened THEN the TaskWindow SHALL display the previously saved custom task texts

### Requirement 5: 生命周期

**User Story:** As a user, I want my pet to visually progress through growth stages, so that I feel rewarded for completing tasks.

#### Acceptance Criteria

1. WHEN a pet is in dormant state (Stage 0) THEN the PetWidget SHALL position at screen bottom with gray semi-transparent appearance
2. WHEN a pet is in dormant state THEN the PetWidget SHALL prevent drag operations
3. WHEN a user completes 1 task THEN the pet SHALL transition from dormant to baby stage with float-up animation
4. WHEN a pet transitions to baby stage THEN the PetWidget SHALL restore normal colors and enable dragging
5. WHEN a user completes 3 tasks total THEN the pet SHALL transition from baby to adult stage
6. WHEN a pet transitions to adult stage THEN the pet size SHALL increase by 1.5x multiplier

### Requirement 6: 盲盒系统

**User Story:** As a user, I want an exciting gacha experience with animations, so that earning new pets feels rewarding.

#### Acceptance Criteria

1. WHEN cumulative tasks reach 12 THEN the GachaWindow SHALL enable the gacha button
2. WHEN the user clicks the gacha button THEN the GachaWindow SHALL display a box shake animation
3. WHEN the box animation completes THEN the GachaWindow SHALL display a flash effect (opacity 0→1)
4. WHEN the flash effect completes THEN the GachaWindow SHALL display the obtained pet name and geometric shape
5. WHEN a gacha is opened THEN the SoundManager SHALL play a gacha sound

### Requirement 7: 背包系统

**User Story:** As a user, I want a Minecraft-style inventory to manage my pets, so that the interface feels familiar and intuitive.

#### Acceptance Criteria

1. WHEN the inventory window opens THEN the layout SHALL display as 2 columns with dynamic rows
2. WHEN a pet slot is displayed THEN the slot SHALL show a miniature geometric placeholder as icon
3. WHEN a user clicks a pet slot THEN the InventoryWindow SHALL toggle the pet between desktop and storage
4. WHEN active_pets changes THEN the InventoryWindow SHALL immediately update the desktop display
5. WHEN desktop pet count reaches 5 THEN the InventoryWindow SHALL prevent adding more pets to desktop

### Requirement 8: 几何占位符视觉

**User Story:** As a developer, I want all geometric placeholders to have consistent styling, so that the demo looks polished without image assets.

#### Acceptance Criteria

1. WHEN rendering puffer placeholder THEN the PetRenderer SHALL draw a green circle (#90EE90)
2. WHEN rendering jelly placeholder THEN the PetRenderer SHALL draw a pink triangle (#FFB6C1)
3. WHEN rendering crab placeholder THEN the PetRenderer SHALL draw a red rectangle (#FF6B6B)
4. WHEN rendering starfish placeholder THEN the PetRenderer SHALL draw a yellow pentagon (#FFD700)
5. WHEN rendering ray placeholder THEN the PetRenderer SHALL draw a blue diamond (#4682B4) at 1.5x base size
6. WHEN rendering any geometric placeholder THEN the PetRenderer SHALL apply 2px black stroke
7. WHEN rendering any geometric placeholder THEN the PetRenderer SHALL add a white highlight point at top-left

### Requirement 9: UI 风格

**User Story:** As a user, I want a consistent pixel-art UI style, so that the application feels cohesive and retro.

#### Acceptance Criteria

1. WHEN any UI window is displayed THEN the window SHALL use pixel-art QSS (sharp corners, thick borders, monospace font)
2. WHEN day mode is active THEN the background color SHALL be light green (#E0F8D0)
3. WHEN night mode is active THEN the background color SHALL be dark (#081820)
4. WHEN the user toggles day/night mode THEN the UI SHALL immediately update colors

### Requirement 10: 代码清理与初始化

**User Story:** As a developer, I want clean code without unused references, so that the codebase is maintainable.

#### Acceptance Criteria

1. WHEN the application starts without data.json THEN the system SHALL create a default data file with one dormant puffer
2. WHEN the application starts THEN the system SHALL not reference any deleted pets or unused deep_sea assets
3. WHEN SoundManager is called THEN the SoundManager SHALL use QApplication.beep() for audio feedback
