# Requirements Document

## Introduction

This feature aims to implement a true retro Minesweeper-style UI interface for the PufferPet desktop pet application, and transform pets into horror forms during night mode (Kiroween theme). The design language is based on the classic Windows 95/Minesweeper 3D raised/sunken effects. In night mode, pets will display ghost/horror appearances, matching the Kiroween Halloween theme.

## Glossary

- **Minesweeper Style**: Classic Windows 95 UI style, characterized by 3D raised buttons, sunken panels, gray color scheme
- **3D Raised Effect**: Button with white highlight on top-left border and dark gray shadow on bottom-right border, creating depth
- **3D Sunken Effect**: Opposite of raised, used for input fields and panels, creating recessed appearance
- **Kiroween Mode**: Night/Halloween horror theme, pets transform into ghost forms
- **Ghost Pet**: Pet appearance in Kiroween mode, with ghost green/purple glow and transparency effects
- **theme_mode**: Theme mode identifier, "normal" for daytime Minesweeper style, "halloween" for Kiroween horror style

## Requirements

### Requirement 1

**User Story:** As a user, I want the UI to look like classic Windows 95 Minesweeper, so that I feel nostalgic and the interface feels retro.

#### Acceptance Criteria

1. WHEN a button is displayed THEN the button SHALL have 3D raised effect with white/light-gray top-left border and dark-gray bottom-right border
2. WHEN a button is pressed THEN the button SHALL invert to 3D sunken effect with dark top-left border and light bottom-right border
3. WHEN an input field or panel is displayed THEN the element SHALL have 3D sunken effect to appear recessed
4. WHEN any UI element is styled THEN the element SHALL have 0px border-radius to enforce sharp pixel edges

### Requirement 2

**User Story:** As a user, I want the normal mode to use classic gray color scheme, so that it matches the authentic Minesweeper aesthetic.

#### Acceptance Criteria

1. WHEN the application is in normal mode THEN the background color SHALL be classic Windows gray (#C0C0C0)
2. WHEN the application is in normal mode THEN the text color SHALL be black (#000000)
3. WHEN the application is in normal mode THEN the button highlight color SHALL be white (#FFFFFF) and shadow color SHALL be dark gray (#808080)
4. WHEN the application is in normal mode THEN the accent color SHALL be classic Windows blue (#000080)

### Requirement 3

**User Story:** As a user, I want the Kiroween/night mode to have a spooky horror theme, so that the experience feels like Halloween.

#### Acceptance Criteria

1. WHEN the application is in halloween mode THEN the background color SHALL be deep purple-black (#1A0A1A)
2. WHEN the application is in halloween mode THEN the text color SHALL be ghost green (#00FF88)
3. WHEN the application is in halloween mode THEN the accent color SHALL be blood red (#FF0066) or pumpkin orange (#FF6600)
4. WHEN the application is in halloween mode THEN the button borders SHALL use purple (#8B00FF) for a supernatural glow effect

### Requirement 4

**User Story:** As a user, I want my pet to transform into a ghost/spooky version in Kiroween mode, so that it matches the horror theme.

#### Acceptance Criteria

1. WHEN the theme changes to halloween mode THEN the pet widget SHALL apply ghost visual filter to the pet image
2. WHEN the ghost filter is applied THEN the pet SHALL have reduced opacity (60-70%) to appear translucent
3. WHEN the ghost filter is applied THEN the pet SHALL have a green or purple color tint overlay
4. WHEN the ghost filter is applied THEN the pet geometric placeholder SHALL use spooky colors (ghost green #00FF88 or blood red #FF0066)

### Requirement 5

**User Story:** As a user, I want the task window to match the retro Minesweeper style, so that all UI elements are consistent.

#### Acceptance Criteria

1. WHEN the task window opens THEN the window SHALL display with 3D raised border effect
2. WHEN checkboxes are displayed THEN the checkboxes SHALL use square indicators with 3D sunken effect
3. WHEN the progress display is shown THEN the progress bar SHALL use chunky block-style with 3D sunken container
4. WHEN buttons are displayed in task window THEN the buttons SHALL use 3D raised effect matching global style

### Requirement 6

**User Story:** As a user, I want the inventory window to look like a classic game inventory, so that managing pets feels immersive.

#### Acceptance Criteria

1. WHEN the inventory window opens THEN the window SHALL display with 3D raised border and gray background
2. WHEN pet cards are displayed THEN each card SHALL have 3D raised effect with sharp corners
3. WHEN scrolling is needed THEN the scrollbar SHALL use classic Windows 95 style with 3D buttons

### Requirement 7

**User Story:** As a user, I want the context menu to have retro styling, so that right-click interactions feel consistent.

#### Acceptance Criteria

1. WHEN the user right-clicks on a pet THEN the context menu SHALL display with 3D raised border
2. WHEN menu items are hovered THEN the menu item SHALL display with inverted colors (dark background, light text)
3. WHEN menu separators are displayed THEN the separators SHALL use 3D groove effect (dark line above, light line below)

### Requirement 8

**User Story:** As a user, I want the gacha/blind box animation to match the current theme, so that the reward experience is immersive.

#### Acceptance Criteria

1. WHEN gacha animation plays in normal mode THEN the interface SHALL use gray Minesweeper style with 3D box effect
2. WHEN gacha animation plays in halloween mode THEN the interface SHALL use dark spooky colors with glowing effects
3. WHEN the mystery box is displayed THEN the box SHALL have 3D raised effect matching current theme
