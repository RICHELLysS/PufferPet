# Requirements Document

## Introduction

V9 资产集成与最终逻辑修正 - 将已完成的美术资产正确集成到 PufferPet 应用中。本次更新涉及资源路径重构、尺寸缩放系统、生命周期交互逻辑修正、以及夜间模式视觉滤镜。

## Glossary

- **PetRenderer**: 负责宠物图像加载、缩放和渲染的核心类
- **PetWidget**: 宠物显示窗口组件，处理动画和交互
- **Stage**: 宠物成长阶段 (0=休眠/Dormant, 1=幼年/Baby, 2=成年/Adult)
- **Action Folder**: 动作文件夹，包含特定动作的序列帧 (如 `swim`, `sleep`, `angry`)
- **Frame Sequence**: 序列帧动画，由多张 PNG 图片组成 (如 `_0.png` 到 `_3.png`)
- **Blindbox**: 盲盒抽卡动画资源
- **Night Filter**: 夜间模式颜色滤镜，根据宠物种类应用不同颜色叠加

## Requirements

### Requirement 1: 资源路径与加载逻辑重构

**User Story:** As a developer, I want the PetRenderer to load assets from the new nested folder structure, so that the application correctly displays all pet animations.

#### Acceptance Criteria

1. WHEN loading pet animation frames THEN the PetRenderer SHALL scan the path `assets/{pet_id}/{action_folder}/{pet_id}_{action_name}_{index}.png`
2. WHEN a pet is in Stage 0 (Dormant) THEN the PetRenderer SHALL load frames from `baby_sleep` folder with filename pattern `{pet_id}_baby_sleep_{0-3}.png`
3. WHEN a pet is in Stage 1 (Baby) THEN the PetRenderer SHALL load frames from `baby_swim` folder with filename pattern `{pet_id}_baby_swim_{0-3}.png`
4. WHEN a pet is in Stage 2 (Adult) and moving THEN the PetRenderer SHALL load frames from `swim` folder with filename pattern `{pet_id}_swim_{0-3}.png`
5. WHEN a pet is in Stage 2 (Adult) and idle THEN the PetRenderer SHALL load frames from `sleep` folder with filename pattern `{pet_id}_sleep_{0-3}.png`
6. WHEN loading interaction animations THEN the PetRenderer SHALL load from `angry`, `drag_h`, `drag_v` folders respectively
7. WHEN loading blindbox animation THEN the ui_gacha module SHALL load frames from `assets/blindbox/box_{0-3}.png`
8. WHEN loading background images THEN the system SHALL load from `assets/environment/seabed_day.png` and `seabed_night.png`
9. WHEN an image file fails to load THEN the PetRenderer SHALL fall back to the V7 geometric placeholder system

### Requirement 2: 尺寸与缩放系统

**User Story:** As a user, I want pets to display at appropriate sizes based on their growth stage and species, so that the visual hierarchy is clear and consistent.

#### Acceptance Criteria

1. WHEN rendering a pet THEN the PetRenderer SHALL scale the original 350x350px frames to the calculated display size
2. WHEN a pet is in Stage 1 (Baby) THEN the PetRenderer SHALL display the pet at 100x100px base size
3. WHEN a pet is in Stage 2 (Adult) THEN the PetRenderer SHALL display the pet at 150x150px (base × 1.5)
4. WHEN the pet_id equals "ray" THEN the PetRenderer SHALL apply an additional 1.5x multiplier to all sizes
5. WHEN displaying icons in ui_inventory THEN the system SHALL scale the 1500x1500px default_icon to 64x64px

### Requirement 3: Stage 1 幼年期交互限制

**User Story:** As a user, I want baby pets to move around but not respond to interactions, so that I understand they need to grow before I can play with them.

#### Acceptance Criteria

1. WHEN a pet is in Stage 1 (Baby) THEN the PetWidget SHALL display the pet using `baby_swim` animation
2. WHEN a pet is in Stage 1 (Baby) THEN the PetWidget SHALL allow the pet to move autonomously
3. WHEN a user clicks on a Stage 1 pet THEN the PetWidget SHALL ignore the click event
4. WHEN a user attempts to drag a Stage 1 pet THEN the PetWidget SHALL ignore the drag event
5. WHEN a user right-clicks on a Stage 1 pet THEN the PetWidget SHALL display the context menu normally

### Requirement 4: Stage 2 成年期完全解锁

**User Story:** As a user, I want adult pets to be fully interactive with all animations, so that I can enjoy playing with my grown pets.

#### Acceptance Criteria

1. WHEN a pet is in Stage 2 (Adult) and moving THEN the PetWidget SHALL display the `swim` animation
2. WHEN a pet is in Stage 2 (Adult) and idle THEN the PetWidget SHALL display the `sleep` animation
3. WHEN a user clicks on a Stage 2 pet 5 times within 2 seconds THEN the PetWidget SHALL trigger the `angry` animation
4. WHEN a user drags a Stage 2 pet horizontally THEN the PetWidget SHALL display the `drag_h` animation
5. WHEN a user drags a Stage 2 pet vertically THEN the PetWidget SHALL display the `drag_v` animation

### Requirement 5: 拖拽翻转逻辑

**User Story:** As a user, I want the pet to face the correct direction when I drag it, so that the animation looks natural.

#### Acceptance Criteria

1. WHEN dragging horizontally with delta_x >= 0 THEN the PetWidget SHALL display `drag_h` frames without transformation
2. WHEN dragging horizontally with delta_x < 0 THEN the PetWidget SHALL display `drag_h` frames with horizontal mirror flip
3. WHEN dragging vertically with delta_y <= 0 THEN the PetWidget SHALL display `drag_v` frames without transformation
4. WHEN dragging vertically with delta_y > 0 THEN the PetWidget SHALL display `drag_v` frames with vertical flip

### Requirement 6: 夜间模式颜色滤镜

**User Story:** As a user, I want pets to have a spooky color overlay at night, so that the visual theme matches the halloween mode.

#### Acceptance Criteria

1. WHEN theme_mode equals "halloween" THEN the PetWidget SHALL apply a color overlay to pet images
2. WHEN applying night filter to puffer or starfish THEN the system SHALL use green color overlay with 0.2 opacity
3. WHEN applying night filter to crab, jelly, or ray THEN the system SHALL use purple color overlay with 0.2 opacity
4. WHEN an image fails to load in night mode THEN the system SHALL apply the color filter to the geometric placeholder

### Requirement 7: 序列帧动画播放

**User Story:** As a developer, I want a frame animation system that cycles through sequence frames, so that pets display smooth animations.

#### Acceptance Criteria

1. WHEN playing a frame sequence THEN the PetWidget SHALL cycle through frames 0-3 at a configurable frame rate
2. WHEN the animation reaches the last frame THEN the PetWidget SHALL loop back to frame 0
3. WHEN switching between animation states THEN the PetWidget SHALL reset the frame counter to 0
4. WHEN the pet is dormant THEN the PetWidget SHALL play the `baby_sleep` animation at a slower frame rate

### Requirement 8: 盲盒动画序列帧

**User Story:** As a user, I want to see an animated blindbox opening sequence, so that the gacha experience feels exciting.

#### Acceptance Criteria

1. WHEN displaying the blindbox THEN the ui_gacha module SHALL load frames from `assets/blindbox/box_{0-3}.png`
2. WHEN the blindbox is shaking THEN the ui_gacha module SHALL cycle through the box frames
3. IF the blindbox frames fail to load THEN the ui_gacha module SHALL fall back to the existing placeholder box
