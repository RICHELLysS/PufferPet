# Implementation Plan

- [x] 1. Simplify Day/Night System in main.py





  - [x] 1.1 Disable TimeManager auto-sync on startup


    - Set `time_manager.set_auto_sync(False)` after initialization
    - Ensure default theme is "normal" (Day Mode)
    - _Requirements: 1.1, 1.4_


  - [x] 1.2 Simplify create_settings_menu() to remove Auto Day/Night option

    - Remove `auto_sync_action` checkbox
    - Keep only "🌓 切换 昼/夜 (Toggle Day/Night)" action
    - Connect to `on_toggle_day_night()` method
    - _Requirements: 1.2, 1.5_


  - [x] 1.3 Verify _toggle_day_night() switches theme and refreshes UI

    - Toggle between "normal" and "halloween" modes
    - Call `_apply_global_style()` to update stylesheet
    - Refresh all pet widgets
    - _Requirements: 1.2, 1.3_

  - [x] 1.4 Write property test for day/night toggle round-trip






    - **Property 1: Day/Night Toggle Round-Trip**
    - **Validates: Requirements 1.2**

- [x] 2. Implement Ray Special Task Mechanics in logic_growth.py






  - [x] 2.1 Add TASK_CONFIG constant for ray vs default task requirements

    - ray: dormant_to_baby=2, baby_to_adult=3 (total 5)
    - default: dormant_to_baby=1, baby_to_adult=2 (total 3)
    - _Requirements: 3.1, 3.2, 3.3, 3.4_


  - [x] 2.2 Implement get_tasks_to_next_state() method

    - Return task count based on pet_id and current state
    - Use TASK_CONFIG to determine values
    - Return 0 for adult state (no more tasks needed)
    - _Requirements: 3.5_

  - [x] 2.3 Update complete_task() to use get_tasks_to_next_state() thresholds


    - Check progress against get_tasks_to_next_state()
    - Trigger state transition when threshold reached
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x] 2.4 Write property test for task requirements






    - **Property 2: Task Requirements Based on Pet Type and State**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

- [x] 3. Checkpoint - Ensure day/night and task mechanics work





  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement Gacha Trigger on Adult Transition






  - [x] 4.1 Update TaskWindow._on_task_changed() to trigger gacha on adult transition

    - Detect state transition from 1 (baby) to 2 (adult)
    - Call gacha animation immediately when transition occurs
    - _Requirements: 2.1_


  - [x] 4.2 Verify ui_gacha.py uses correct V8 probability distribution

    - Confirm GACHA_WEIGHTS: puffer/jelly/crab/starfish=22%, ray=12%
    - Verify roll_gacha() uses weighted random selection
    - _Requirements: 2.2_


  - [x] 4.3 Ensure gacha result is added to inventory

    - Callback adds pet to growth_manager
    - Handle inventory full case with warning message
    - _Requirements: 2.3, 2.4_

  - [x] 4.4 Write property test for gacha probability distribution






    - **Property 3: Gacha Probability Distribution**
    - **Validates: Requirements 2.2**

- [x] 5. Implement Tutorial Bubble System in pet_core.py





  - [x] 5.1 Add TUTORIAL_BUBBLES constant and tutorial state variables


    - Define text for dormant, just_awakened, idle_hint states
    - Add just_awakened, just_awakened_timer, show_idle_hint flags
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 5.2 Implement get_tutorial_text() method


    - Return "右键点击我！(Right Click Me!)" for dormant state
    - Return "试试拖拽我！(Try Dragging!)" for just_awakened state
    - Return "连点5下有惊喜！(Click 5x for Anger!)" for idle hint
    - Return empty string otherwise
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 5.3 Implement _draw_tutorial_bubble() method using QPainter.drawText


    - Draw semi-transparent black background (rgba 0,0,0,180)
    - Draw text with black outline (4 offset draws)
    - Draw yellow (#FFFF00) text on top
    - Position bubble above pet widget
    - _Requirements: 4.4, 4.5_

  - [x] 5.4 Update paintEvent() to draw tutorial bubble


    - Call get_tutorial_text() to get current text
    - Call _draw_tutorial_bubble() if text is not empty
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 5.5 Implement just_awakened timer logic (10 seconds)


    - Set just_awakened=True when transitioning from dormant to baby
    - Start 10-second QTimer to clear just_awakened flag
    - Stop existing timer before starting new one
    - _Requirements: 4.2_

  - [x] 5.6 Write property test for tutorial text






    - **Property 4: Tutorial Text for Dormant State**
    - **Validates: Requirements 4.1**

- [x] 6. Checkpoint - Ensure tutorial bubbles display correctly





  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Verify Geometric Fallback System





  - [x] 7.1 Verify all V7 pets have entries in PET_SHAPES config


    - Check puffer, jelly, crab, starfish, ray all have shape/color config
    - _Requirements: 5.2, 5.3_

  - [x] 7.2 Test geometric placeholder generation for all V7 pets


    - Call PetRenderer.draw_placeholder() for each V7 pet
    - Verify non-null QPixmap is returned
    - Verify correct shape is drawn
    - _Requirements: 5.1, 5.4_

  - [x] 7.3 Write property test for geometric fallback






    - **Property 5: Geometric Fallback Consistency**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4**

- [x] 8. Final Checkpoint - Full V8 system verification















  - Ensure all tests pass, ask the user if questions arise.
