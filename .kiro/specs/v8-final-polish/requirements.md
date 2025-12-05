# Requirements Document

## Introduction

V8 是为 Hackathon 展示特意优化的版本，重点在于**稳定性**和**用户体验**。基于 V7.1 代码进行关键修改：简化昼夜系统（移除 TimeManager 自动检测）、优化盲盒触发机制（成年即送盲盒）、鳐鱼 SSR 特殊成长难度、新增新手引导气泡系统，确保评委能一眼看懂游戏玩法。

## Glossary

- **Day/Night Toggle**: 手动切换昼夜模式的菜单选项，移除自动时间检测
- **TimeManager**: V7.1 中的自动时间检测组件，V8 中禁用其自动同步功能
- **Gacha Trigger**: 盲盒触发机制，当任意宠物成年时立即触发
- **Ray (鳐鱼)**: SSR 稀有宠物，成长难度更高（需 5 个任务而非 3 个）
- **Tutorial Bubble (引导气泡)**: 在宠物头顶显示的文字提示气泡，使用 QPainter.drawText 绘制
- **Onboarding**: 新手引导系统，帮助用户理解游戏玩法
- **Dormant State (休眠态)**: 宠物状态 0，需完成任务才能唤醒
- **Baby State (幼年态)**: 宠物状态 1，可拖拽和交互
- **Adult State (成年态)**: 宠物状态 2，完全体，触发盲盒奖励

## Requirements

### Requirement 1

**User Story:** As a demo presenter, I want a simplified day/night toggle, so that I can manually control the theme without automatic time detection.

#### Acceptance Criteria

1. WHEN the application starts THEN the system SHALL default to "Day Mode" (normal theme)
2. WHEN the user clicks "🌓 切换 昼/夜 (Toggle Day/Night)" in the context menu THEN the system SHALL immediately switch between "normal" and "halloween" modes
3. WHEN the theme switches THEN the UI stylesheet and ocean background SHALL update immediately without restart
4. WHEN the application initializes THEN the system SHALL disable TimeManager auto-sync (set auto_sync to False)
5. WHEN the settings menu is created THEN the system SHALL remove the "Auto Day/Night" checkbox option

### Requirement 2

**User Story:** As a player, I want to receive a gacha reward when my pet grows to adult, so that the reward feels immediate and satisfying.

#### Acceptance Criteria

1. WHEN any pet on desktop transitions from Baby (state 1) to Adult (state 2) THEN the system SHALL immediately trigger a gacha animation
2. WHEN gacha is triggered THEN the system SHALL use the following probability distribution:
   - 22% each: Puffer, Jelly, Crab, Starfish (common)
   - 12%: Ray (SSR rare)
3. WHEN a new pet is obtained from gacha THEN the pet SHALL be added to the inventory immediately
4. WHEN the inventory is full THEN the system SHALL display a warning message instead of triggering gacha

### Requirement 3

**User Story:** As a player who obtains a Ray, I want it to have higher growth difficulty, so that it feels special and rewarding.

#### Acceptance Criteria

1. WHEN a Ray pet is in dormant state (0) THEN the Ray SHALL require 2 tasks to awaken (transition to state 1)
2. WHEN a Ray pet is in baby state (1) THEN the Ray SHALL require 3 additional tasks to become adult (total 5 tasks from dormant)
3. WHEN a non-Ray pet is in dormant state THEN the pet SHALL require 1 task to awaken (standard behavior)
4. WHEN a non-Ray pet is in baby state THEN the pet SHALL require 2 additional tasks to become adult (total 3 tasks from dormant)
5. WHEN get_tasks_to_next_state() is called THEN the system SHALL return the correct task count based on pet_id and current state

### Requirement 4

**User Story:** As a first-time user, I want to see tutorial hints on the pet, so that I understand how to interact with the game.

#### Acceptance Criteria

1. WHEN a pet is in dormant state (state 0) THEN the pet SHALL display a bubble saying "右键点击我！(Right Click Me!)" above the pet
2. WHEN a pet just awakened to baby state (state 0 → 1) THEN the pet SHALL display a bubble saying "试试拖拽我！(Try Dragging!)" for 10 seconds
3. WHEN a pet is idle for a period THEN the pet SHALL occasionally display "连点5下有惊喜！(Click 5x for Anger!)"
4. WHEN tutorial text is displayed THEN the text SHALL use high-contrast colors (yellow #FFFF00 text with black #000000 outline)
5. WHEN tutorial bubble is drawn THEN the system SHALL use QPainter.drawText with semi-transparent black background

### Requirement 5

**User Story:** As a developer, I want geometric placeholder fallback to always work, so that the demo is stable even without image assets.

#### Acceptance Criteria

1. WHEN an image file is missing or has 0 bytes THEN the system SHALL fall back to geometric placeholder rendering
2. WHEN geometric placeholder is rendered THEN the placeholder SHALL use the correct shape and color from PET_SHAPES config
3. WHEN the application runs THEN all V7 pets (puffer, jelly, crab, starfish, ray) SHALL have working geometric fallbacks
4. WHEN PetRenderer.draw_placeholder() is called THEN the system SHALL return a non-null QPixmap

