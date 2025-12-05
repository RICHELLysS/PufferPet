# Implementation Plan

- [x] 1. Create sound_manager.py module





  - [x] 1.1 Create SoundManager class with enabled flag and beep methods


    - Implement play_task_complete(), play_gacha_open(), play_pet_upgrade(), play_pet_angry()
    - Use QApplication.beep() for all sounds
    - _Requirements: 4.3, 6.5, 10.3_

  - [x] 1.2 Add global instance getter get_sound_manager()
    - Singleton pattern for global access
    - _Requirements: 10.3_
  - [x] 1.3 Write property test for sound trigger


    - **Property 9: Task Completion Sound Trigger**
    - **Validates: Requirements 4.3**

- [x] 2. Update pet_core.py with anger mechanism





  - [x] 2.1 Add anger state variables to PetWidget


    - click_times list, is_angry flag, anger_timer, shake_timer, original_pos
    - _Requirements: 1.1_

  - [x] 2.2 Implement click tracking in mousePressEvent

    - Record timestamps, filter to 2-second window, check for 5+ clicks
    - _Requirements: 1.1_
  - [x] 2.3 Implement trigger_anger() method


    - Set is_angry=True, play sound, change color to red, start shake
    - _Requirements: 1.2, 1.3_

  - [x] 2.4 Implement _start_shake_animation() method
    - QTimer at 50ms interval, random x offset ±10px
    - _Requirements: 1.3_

  - [x] 2.5 Implement calm_down() method
    - Reset is_angry, stop timers, restore position and color
    - _Requirements: 1.4, 1.5_
  - [x] 2.6 Write property test for anger trigger threshold


    - **Property 1: Anger Trigger Threshold**
    - **Validates: Requirements 1.1**
  - [x] 2.7 Write property test for anger state color change

    - **Property 2: Anger State Color Change and Restoration**
    - **Validates: Requirements 1.2, 1.5**
  - [x] 2.8 Write property test for anger auto-recovery

    - **Property 4: Anger State Auto-Recovery**
    - **Validates: Requirements 1.4**

- [x] 3. Update pet_core.py with drag physics





  - [x] 3.1 Add drag physics state variables


    - is_dragging flag, squash_factor (default 1.0)
    - _Requirements: 2.1_
  - [x] 3.2 Update mousePressEvent for squash effect


    - Set squash_factor to 0.8 when drag starts (non-dormant only)
    - _Requirements: 2.1, 2.4_
  - [x] 3.3 Update mouseMoveEvent for speed-based squash


    - Calculate speed, adjust squash_factor (min 0.6)
    - _Requirements: 2.2_
  - [x] 3.4 Implement _animate_stretch_back() method


    - Gradually restore squash_factor to 1.0 on release
    - _Requirements: 2.3_
  - [x] 3.5 Update paintEvent to apply squash transform


    - Scale transform based on squash_factor
    - _Requirements: 2.1_
  - [x] 3.6 Write property test for dormant drag prevention


    - **Property 5: Dormant Pets Cannot Be Dragged**
    - **Validates: Requirements 2.4, 5.2**
  - [x] 3.7 Write property test for squash effect


    - **Property 6: Squash Effect During Drag**
    - **Validates: Requirements 2.1, 2.3**

- [x] 4. Checkpoint - Ensure anger and drag physics work





  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Update pet_core.py with PetRenderer colored placeholder





  - [x] 5.1 Add draw_placeholder_colored() static method


    - Accept custom color parameter for angry state
    - _Requirements: 1.2_

  - [x] 5.2 Update load_image() to use red color when angry
    - Check is_angry flag, use #FF0000 if true

    - _Requirements: 1.2_
  - [x] 5.3 Write property test for placeholder styling

    - **Property 16: Placeholder Styling Consistency**
    - **Validates: Requirements 8.6, 8.7**

- [x] 6. Update pet_core.py context menu





  - [x] 6.1 Verify context menu includes all required options


    - 任务设置, 打开背包, 环境设置(昼夜), 放生(非puffer)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 6.2 Add inventory_requested signal and connect to menu

    - Emit signal when "打开背包" clicked
    - _Requirements: 3.3_

  - [x] 6.3 Add environment_requested signal and connect to menu

    - Emit signal when "环境设置" clicked
    - _Requirements: 3.4_

- [x] 7. Update task_window.py with editable tasks



  - [x] 7.1 Replace QCheckBox text with QLineEdit


    - Create row with checkbox + line_edit for each task
    - _Requirements: 4.1_

  - [x] 7.2 Implement _on_task_text_changed() handler
    - Save task texts when modified

    - _Requirements: 4.2_
  - [x] 7.3 Add get_custom_task_texts() and set_custom_task_texts() to GrowthManager

    - Store custom texts in data.json
    - _Requirements: 4.2, 4.4_

  - [x] 7.4 Load saved task texts on window open
    - Read from data.json, use defaults if not found
    - _Requirements: 4.4_

  - [x] 7.5 Add sound trigger on task completion
    - Call SoundManager.play_task_complete() when checkbox checked
    - _Requirements: 4.3_
  - [x] 7.6 Write property test for task text round-trip



    - **Property 8: Task Text Persistence Round-Trip**
    - **Validates: Requirements 4.2, 4.4**

- [x] 8. Checkpoint - Ensure task system works





  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Update lifecycle transitions





  - [x] 9.1 Implement float-up animation for dormant→baby transition


    - Animate from bottom to center position
    - _Requirements: 5.3_

  - [x] 9.2 Ensure baby stage enables dragging and restores colors

    - Set is_dormant=False, reload normal color image
    - _Requirements: 5.4_

  - [x] 9.3 Implement size increase animation for baby→adult transition

    - Call PetRenderer.calculate_size() with 'adult' stage
    - _Requirements: 5.6_


  - [x] 9.4 Write property test for lifecycle transitions
    - **Property 10: Lifecycle State Transitions**
    - **Validates: Requirements 5.3, 5.5**

  - [x] 9.5 Write property test for baby stage dragging

    - **Property 11: Baby Stage Enables Dragging**
    - **Validates: Requirements 5.4**

- [x] 10. Update ui_gacha.py with complete animation




  - [x] 10.1 Verify shake animation in stage 0

    - Box shakes for 1.5 seconds
    - _Requirements: 6.2_

  - [x] 10.2 Verify flash effect in stage 1
    - Opacity 0→255 over 0.5 seconds
    - _Requirements: 6.3_

  - [x] 10.3 Verify result display in stage 2
    - Show pet name and geometric shape

    - _Requirements: 6.4_
  - [x] 10.4 Add sound trigger on gacha open
    - Call SoundManager.play_gacha_open() at animation start
    - _Requirements: 6.5_
  - [x] 10.5 Write property test for gacha trigger threshold


    - **Property 12: Gacha Trigger Threshold**
    - **Validates: Requirements 6.1**

  - [x] 10.6 Write property test for gacha sound trigger


    - **Property 13: Gacha Sound Trigger**
    - **Validates: Requirements 6.5**

- [x] 11. Update ui_inventory.py with real-time sync





  - [x] 11.1 Verify pets_changed signal is emitted on toggle


    - Signal emitted with updated active_pets list
    - _Requirements: 7.4_

  - [x] 11.2 Verify miniature placeholder icons in slots

    - Use PetRenderer.draw_placeholder() for icons
    - _Requirements: 7.2_
  - [x] 11.3 Write property test for inventory slot icons


    - **Property 14: Inventory Slot Icon Generation**
    - **Validates: Requirements 7.2**
  - [x] 11.4 Write property test for change signal emission

    - **Property 15: Inventory Change Signal Emission**
    - **Validates: Requirements 7.4**

- [x] 12. Checkpoint - Ensure gacha and inventory work





  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Update main.py initialization





  - [x] 13.1 Add data.json existence check on startup


    - If not exists, create with default dormant puffer
    - _Requirements: 10.1_


  - [x] 13.2 Connect inventory pets_changed signal to update desktop
    - Refresh pet widgets when active_pets changes

    - _Requirements: 7.4_
  - [x] 13.3 Remove any references to deleted pets or deep_sea assets

    - Clean up unused imports and code paths
    - _Requirements: 10.2_

  - [x] 13.4 Write property test for default initialization

    - **Property 17: Default Data Initialization**
    - **Validates: Requirements 10.1**

- [x] 14. Code cleanup and verification










  - [x] 14.1 Remove unused old slice code and deep_sea references


    - Search and remove dead code
    - _Requirements: 10.2_
  - [x] 14.2 Verify all geometric placeholders have stroke and highlight


    - Check PetRenderer draw methods
    - _Requirements: 8.6, 8.7_
  - [x] 14.3 Verify pixel-art QSS is applied to all windows


    - Check ui_style usage in all UI modules
    - _Requirements: 9.1_

- [x] 15. Final Checkpoint - Full system verification





  - Ensure all tests pass, ask the user if questions arise.
