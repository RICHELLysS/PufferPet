# Implementation Plan

- [x] 1. Update ui_style.py with 3D Minesweeper effects





  - [x] 1.1 Update PALETTES with correct colors for normal and halloween modes


    - Normal: bg=#C0C0C0, fg=#000000, button_light=#FFFFFF, button_dark=#808080, accent=#000080
    - Halloween: bg=#1A0A1A, fg=#00FF88, button_light=#8B00FF, button_dark=#0D050D, accent=#FF0066
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4_


  - [x] 1.2 Write property test for palette consistency

    - **Property 5: Normal Mode Palette Consistency**
    - **Property 6: Halloween Mode Palette Consistency**
    - **Validates: Requirements 2.1-2.4, 3.1-3.4**

  - [x] 1.3 Implement get_stylesheet() with 3D raised/sunken effects


    - QPushButton: 3D raised effect (white top-left, gray bottom-right)
    - QPushButton:pressed: 3D sunken effect (inverted borders)
    - QLineEdit, QFrame: 3D sunken effect
    - All elements: border-radius: 0px
    - _Requirements: 1.1, 1.2, 1.3, 1.4_


  - [x] 1.4 Write property tests for 3D effects

    - **Property 1: 3D Raised Button Effect**
    - **Property 2: 3D Sunken Pressed Effect**
    - **Property 3: 3D Sunken Input Fields**
    - **Property 4: Zero Border-Radius Enforcement**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

  - [x] 1.5 Update QMenu styling with 3D raised border and hover inversion


    - QMenu: 3D raised border
    - QMenu::item:selected: inverted colors (dark bg, light text)
    - QMenu::separator: 3D groove effect
    - _Requirements: 7.1, 7.2, 7.3_


  - [x] 1.6 Write property tests for menu styling

    - **Property 10: Menu 3D Raised Border**
    - **Property 11: Menu Item Hover Inversion**
    - **Validates: Requirements 7.1, 7.2**

  - [x] 1.7 Update QCheckBox and QProgressBar styling


    - QCheckBox::indicator: square (0px radius), 3D sunken effect
    - QProgressBar: 3D sunken container, chunky block style
    - _Requirements: 5.2, 5.3_

  - [x] 1.8 Write property test for checkbox styling


    - **Property 9: Checkbox Square Indicator**
    - **Validates: Requirements 5.2**

- [x] 2. Checkpoint - Ensure all ui_style tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Update theme_manager.py with enhanced ghost filter





  - [x] 3.1 Update apply_ghost_filter() with opacity reduction and color tint


    - Reduce opacity to 60-70% of original
    - Add green (#00FF88) or purple (#8B00FF) color tint overlay
    - Blend factor: 0.3 for color mixing
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 3.2 Write property tests for ghost filter


    - **Property 7: Ghost Filter Opacity Reduction**
    - **Property 8: Ghost Filter Color Tint**
    - **Validates: Requirements 4.2, 4.3**


  - [x] 3.3 Add SPOOKY_COLORS constant and get_spooky_color() method

    - ghost_green: #00FF88
    - blood_red: #FF0066
    - pumpkin_orange: #FF6600
    - curse_purple: #8B00FF
    - _Requirements: 4.4_

- [x] 4. Update pet_core.py for Kiroween pet rendering





  - [x] 4.1 Add draw_placeholder_spooky() method to PetRenderer


    - Use spooky colors (ghost green or blood red) for halloween mode
    - Add glow effect to geometric shapes
    - _Requirements: 4.4_


  - [x] 4.2 Update PetWidget.refresh_display() to apply ghost filter in halloween mode

    - Check theme mode from growth_manager
    - Apply ghost filter when mode is "halloween"
    - _Requirements: 4.1_

- [x] 5. Checkpoint - Ensure pet rendering tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Update main.py TaskWindow with retro styling






  - [x] 6.1 Remove inline cute styling from TaskWindow

    - Remove the hardcoded cute stylesheet
    - Apply global stylesheet from ui_style.get_stylesheet()
    - _Requirements: 5.1, 5.4_


  - [x] 6.2 Update TaskWindow layout for retro look

    - Use 3D sunken frame for task list
    - Apply theme-appropriate title styling
    - _Requirements: 5.1_

- [x] 7. Update ui_inventory.py with retro styling






  - [x] 7.1 Update InventoryWindow to use global stylesheet

    - Remove any inline styling
    - Apply 3D raised border to window
    - _Requirements: 6.1_


  - [x] 7.2 Update pet card styling with 3D raised effect

    - Sharp corners (0px radius)
    - 3D raised border effect
    - _Requirements: 6.2_


  - [x] 7.3 Update scrollbar styling

    - Classic Windows 95 scrollbar style
    - 3D buttons for scroll arrows
    - _Requirements: 6.3_

- [x] 8. Update ui_gacha.py with theme-aware styling





  - [x] 8.1 Update GachaOverlay to use theme palette colors


    - Normal mode: gray Minesweeper style
    - Halloween mode: dark spooky colors
    - _Requirements: 8.1, 8.2_


  - [x] 8.2 Update mystery box drawing with 3D effect

    - 3D raised border effect for the box
    - Theme-appropriate colors
    - _Requirements: 8.3_

- [x] 9. Final Checkpoint - Full system verification





  - Ensure all tests pass, ask the user if questions arise.

