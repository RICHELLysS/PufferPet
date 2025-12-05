# Requirements Document

## Introduction

本功能旨在为 PufferPet 桌面宠物应用实现"Kiroween"复古像素风格的全局UI重绘。设计语言基于90年代电子宠物机和复古DOS终端的审美，拒绝圆角，采用粗边框、像素字体，并支持日间模式（复古掌机风）和夜间模式（黑客/万圣节风）的动态配色切换。

## Glossary

- **PetWidget**: 宠物显示窗口组件，负责在桌面上显示宠物
- **ui_style.py**: 新建的样式管理模块，提供全局样式表生成函数
- **Day Mode (日间模式)**: 复古掌机风格，使用浅绿/米色背景和深墨绿前景色
- **Night Mode (夜间模式)**: Kiroween/黑客风格，使用纯黑背景和荧光绿/万圣节橙前景色
- **像素字体**: 优先加载 `assets/fonts/pixel_font.ttf`，回退使用等宽字体
- **QSS**: Qt Style Sheet，用于定义Qt组件的视觉样式
- **theme_mode**: 主题模式标识，"normal"为日间，"halloween"为夜间

## Requirements

### Requirement 1

**User Story:** As a user, I want the pet to appear in the bottom-right corner of the screen, so that it doesn't obstruct my main work area while remaining easily accessible.

#### Acceptance Criteria

1. WHEN the application starts THEN the PetWidget SHALL position itself in the bottom-right area of the screen with at least 80 pixels margin from the right edge and bottom edge
2. WHEN a pet is in dormant state THEN the PetWidget SHALL move to the bottom-right position automatically
3. WHEN a new pet widget is created THEN the PetWidget SHALL initialize its position in the bottom-right area of the screen

### Requirement 2

**User Story:** As a developer, I want a centralized style management module, so that all UI components can share consistent pixel-art styling.

#### Acceptance Criteria

1. WHEN the ui_style module is imported THEN the module SHALL provide a `get_stylesheet(mode)` function that returns complete QSS string
2. WHEN `get_stylesheet` is called with "normal" mode THEN the function SHALL return Day Mode palette (background: #E0F8D0, foreground: #081820, highlight: #88C070)
3. WHEN `get_stylesheet` is called with "halloween" mode THEN the function SHALL return Night Mode palette (background: #101010, foreground: #00FF00 or #FF6600)
4. WHEN the stylesheet is applied THEN all border-radius values SHALL be 0px to enforce sharp pixel edges
5. WHEN the stylesheet is applied THEN all borders SHALL use 2px to 3px solid line style

### Requirement 3

**User Story:** As a user, I want pixel-art styled fonts throughout the application, so that the retro aesthetic is consistent.

#### Acceptance Criteria

1. WHEN the application loads THEN the system SHALL attempt to load pixel font from `assets/fonts/pixel_font.ttf`
2. IF the pixel font file is not found THEN the system SHALL fall back to system monospace fonts ("Courier New", "Consolas", monospace)
3. WHEN text is rendered THEN the font SHALL disable anti-aliasing to maintain sharp pixel edges

### Requirement 4

**User Story:** As a user, I want the right-click context menu to have retro pixel-art styling, so that it feels like a classic game interface.

#### Acceptance Criteria

1. WHEN the user right-clicks on a pet THEN the context menu SHALL display with 0px border-radius and 2-3px solid border
2. WHEN the context menu is displayed THEN the menu SHALL use solid background color from current theme palette
3. WHEN the user hovers over a menu item THEN the menu item SHALL display inverted colors or dashed border highlight
4. WHEN the context menu contains separators THEN the separators SHALL use solid line matching theme foreground color

### Requirement 5

**User Story:** As a user, I want all buttons to have retro pixel-art styling with physical press feedback, so that interactions feel tactile.

#### Acceptance Criteria

1. WHEN a button is displayed THEN the button SHALL have 0px border-radius and 2-3px solid border
2. WHEN a button is pressed THEN the button content SHALL offset 1px to bottom-right to simulate physical press
3. WHEN a button is hovered THEN the button SHALL display color change or border highlight

### Requirement 6

**User Story:** As a user, I want checkboxes to use pixel-art character styling, so that they match the retro theme.

#### Acceptance Criteria

1. WHEN a checkbox is unchecked THEN the checkbox SHALL display as "[ ]" character form or simple square image
2. WHEN a checkbox is checked THEN the checkbox SHALL display as "[x]" character form or filled square image
3. WHEN checkbox state changes THEN the visual change SHALL be immediate without smooth animation

### Requirement 7

**User Story:** As a user, I want progress bars to have chunky pixel-art styling, so that progress feels like classic game loading bars.

#### Acceptance Criteria

1. WHEN a progress bar is displayed THEN the progress bar SHALL use block-style chunks instead of smooth fill
2. WHEN progress updates THEN the progress bar SHALL update in discrete steps without smooth animation
3. WHEN the progress bar is styled THEN the bar SHALL have 0px border-radius and solid borders

### Requirement 8

**User Story:** As a user, I want the inventory window to look like a game inventory screen, so that managing pets feels immersive.

#### Acceptance Criteria

1. WHEN the inventory window opens THEN the window SHALL display with pixel-art styling matching current theme
2. WHEN pet cards are displayed THEN each card SHALL have sharp corners and solid borders
3. WHEN the inventory window is displayed THEN the window SHALL inherit global pixel-art stylesheet

### Requirement 9

**User Story:** As a user, I want the gacha/blind box window to look like a game reward screen, so that the experience feels exciting and retro.

#### Acceptance Criteria

1. WHEN the gacha animation plays THEN the interface SHALL use pixel-art styling matching current theme
2. WHEN text is displayed in gacha window THEN the text SHALL use pixel font with theme-appropriate colors
3. WHEN the gacha window is displayed THEN the window SHALL inherit global pixel-art stylesheet

### Requirement 10

**User Story:** As a user, I want the theme to switch dynamically when day/night mode changes, so that the entire UI updates consistently.

#### Acceptance Criteria

1. WHEN theme_mode changes THEN the application SHALL call `app.setStyleSheet()` with updated stylesheet
2. WHEN theme updates THEN all visible windows and menus SHALL reflect the new color palette immediately
3. WHEN theme updates THEN both background imagery and UI components SHALL update together
