# Implementation Plan

- [x] 1. Create ui_style.py module with core styling functions




  - [x] 1.1 Create ui_style.py with PALETTES dictionary containing Day and Night mode colors

    - Define "normal" palette: bg=#E0F8D0, fg=#081820, highlight=#88C070, border=#081820
    - Define "halloween" palette: bg=#101010, fg=#00FF00, highlight=#00AA00, accent=#FF6600
    - _Requirements: 2.2, 2.3_

  - [x] 1.2 Implement get_palette(mode) function
    - Return palette dict for given mode
    - Default to "normal" if invalid mode
    - _Requirements: 2.1_
  - [x] 1.3 Implement load_pixel_font() and get_font_family() functions
    - Attempt to load assets/fonts/pixel_font.ttf
    - Fall back to "Courier New", "Consolas", monospace
    - _Requirements: 3.1, 3.2_
  - [x] 1.4 Implement get_stylesheet(mode) function with QMenu styling
    - 0px border-radius, 2-3px solid borders
    - Solid background from palette
    - Inverted colors on hover (::item:selected)
    - _Requirements: 2.4, 2.5, 4.1, 4.2, 4.3, 4.4_
  - [x] 1.5 Add QPushButton styling to get_stylesheet()

    - 0px border-radius, 2-3px solid border
    - :pressed state with 1px offset effect
    - :hover state with color change
    - _Requirements: 5.1, 5.2, 5.3_
  - [x] 1.6 Add QCheckBox styling to get_stylesheet()
    - Square indicator (not circular)
    - Unchecked: empty square, Checked: filled square or [x] style
    - _Requirements: 6.1, 6.2_
  - [x] 1.7 Add QProgressBar styling to get_stylesheet()
    - Block-style chunks
    - 0px border-radius, solid borders
    - _Requirements: 7.1, 7.3_
  - [x] 1.8 Add QDialog and QFrame styling to get_stylesheet()
    - Sharp corners, solid borders
    - Theme-appropriate colors
    - _Requirements: 8.1, 8.2_
  - [x] 1.9 Write property test for stylesheet mode consistency


    - **Property 2: Stylesheet Mode Consistency**
    - **Validates: Requirements 2.1, 2.2, 2.3**

  - [x] 1.10 Write property test for zero border-radius enforcement
    - **Property 3: Zero Border-Radius Enforcement**
    - **Validates: Requirements 2.4, 4.1, 5.1, 7.3**
  - [x] 1.11 Write property test for border width consistency

    - **Property 4: Border Width Consistency**
    - **Validates: Requirements 2.5, 4.1, 5.1**

- [x] 2. Update main.py to apply global stylesheet





  - [x] 2.1 Import ui_style module and add _apply_global_style() method


    - Call get_stylesheet(mode) and app.setStyleSheet()
    - _Requirements: 10.1_

  - [x] 2.2 Call _apply_global_style() in __init__ after creating app

    - Apply initial theme on startup
    - _Requirements: 10.1_

  - [x] 2.3 Update _toggle_day_night() to refresh global stylesheet

    - Call _apply_global_style() after mode change
    - _Requirements: 10.1, 10.2, 10.3_

  - [x] 2.4 Update _check_day_night() to refresh global stylesheet on auto-switch

    - Call _apply_global_style() when theme changes automatically
    - _Requirements: 10.1, 10.2_

- [x] 3. Update pet_core.py for pixel-art styling



  - [x] 3.1 Update _move_to_bottom() to position pet in bottom-right area


    - At least 80px margin from right and bottom edges
    - _Requirements: 1.1, 1.2_

  - [x] 3.2 Update _move_to_right_bottom() for non-dormant initial position

    - Consistent bottom-right positioning
    - _Requirements: 1.3_

  - [x] 3.3 Update contextMenuEvent() to use ui_style for menu styling

    - Remove inline QSS, use get_stylesheet() or get_menu_stylesheet()
    - _Requirements: 4.1, 4.2, 4.3, 4.4_


  - [x] 3.4 Write property test for pet position in bottom-right area

    - **Property 1: Pet Position in Bottom-Right Area**
    - **Validates: Requirements 1.1, 1.2, 1.3**

- [x] 4. Checkpoint - Ensure all tests pass











  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Update ui_inventory.py for pixel-art styling





  - [x] 5.1 Remove inline stylesheet from _setup_ui()


    - Let window inherit global stylesheet
    - _Requirements: 8.3_

  - [x] 5.2 Update _create_pet_card() to use pixel-art card styling

    - Sharp corners, solid borders
    - _Requirements: 8.2_

  - [x] 5.3 Ensure inventory window looks like game inventory screen

    - Pixel font, theme colors, retro aesthetic
    - _Requirements: 8.1_

- [x] 6. Update ui_gacha.py for pixel-art styling



  - [x] 6.1 Import ui_style and use get_palette() for colors


    - Use theme-appropriate colors in paintEvent
    - _Requirements: 9.1_
  - [x] 6.2 Update text rendering to use pixel font


    - Use get_font_family() for font selection
    - _Requirements: 9.2_

  - [x] 6.3 Update placeholder creation to use pixel-art style

    - Sharp corners, solid colors
    - _Requirements: 9.3_
  - [x] 6.4 Write property test for button press effect


    - **Property 5: Button Press Effect**
    - **Validates: Requirements 5.2**

  - [x] 6.5 Write property test for checkbox character styling

    - **Property 6: Checkbox Character Styling**
    - **Validates: Requirements 6.1, 6.2**

- [x] 7. Final Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.
