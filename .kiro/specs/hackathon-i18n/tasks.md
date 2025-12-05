# Implementation Plan

- [x] 1. Add resource_path() helper function




  - [ ] 1.1 Create resource_path() function in main.py with sys.frozen detection
    - Implement the function that checks `getattr(sys, 'frozen', False)`
    - Return `os.path.join(sys._MEIPASS, relative_path)` when frozen
    - Return `os.path.join(os.path.abspath("."), relative_path)` in development
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  - [x]* 1.2 Write property test for resource_path()




    - **Property 3: Resource Path Correctness**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**


- [ ] 2. Translate main.py UI text and comments
  - [x] 2.1 Translate all Chinese UI strings in main.py to English




    - Menu items: 任务→Tasks, 背包→Inventory, 设置→Settings, 退出→Quit
    - Dialog text: 确认放生→Confirm Release, 库存已满→Inventory Full

    - Button text: 完成→Done, 重置所有→Reset All
    - _Requirements: 1.1, 1.2, 1.3, 1.5_

  - [ ] 2.2 Translate all Chinese comments and docstrings in main.py to English
    - Keep Spooky/Dramatic style where appropriate



    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 3. Translate pet_core.py UI text and comments

  - [x] 3.1 Translate TUTORIAL_BUBBLES and context menu text to English

    - 右键点击我→Right-click me!, 试试拖拽我→Try dragging me!
    - 连点5下有惊喜→Click 5x for surprise!



    - _Requirements: 1.4_
  - [ ] 3.2 Translate all Chinese comments and docstrings in pet_core.py to English
    - Maintain Spooky/Dramatic deep-sea theme
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 3.3 Wrap asset paths with resource_path() in pet_core.py



    - Update PetLoader.get_frame_path() to use resource_path()
    - _Requirements: 3.1, 3.3_


- [ ] 4. Translate ui_gacha.py UI text and comments
  - [x] 4.1 Translate all Chinese UI strings in ui_gacha.py to English



    - PET_NAMES: 河豚→Puffer, 水母→Jellyfish, 螃蟹→Crab, 海星→Starfish, 鳐鱼→Ray
    - Opening text, result text



    - _Requirements: 1.2, 1.3_
  - [x] 4.2 Translate all Chinese comments and docstrings in ui_gacha.py to English

    - _Requirements: 2.1, 2.2, 2.3, 2.4_


  - [x] 4.3 Wrap asset paths with resource_path() in ui_gacha.py



    - Update blindbox and pet image loading paths
    - _Requirements: 3.1, 3.3_


- [ ] 5. Translate ui_inventory.py UI text and comments
  - [ ] 5.1 Translate all Chinese UI strings in ui_inventory.py to English
    - Window title: 背包→Inventory
    - Labels: 我的宠物→My Pets, 桌面显示中→On Desktop, 在背包中→In Inventory
    - Tooltips and status text
    - _Requirements: 1.2, 1.3, 1.4_

  - [ ] 5.2 Translate all Chinese comments and docstrings in ui_inventory.py to English
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 6. Translate task_window.py UI text and comments
  - [x] 6.1 Translate all Chinese UI strings in task_window.py to English



    - Window title: 每日任务→Daily Tasks
    - Default tasks: 喝一杯水→Drink water, 伸个懒腰→Stretch, 专注工作30分钟→Focus 30min


    - _Requirements: 1.2, 1.3_
  - [ ] 6.2 Translate all Chinese comments and docstrings in task_window.py to English
    - Convert Spooky Chinese comments to Spooky English
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 7. Translate logic_growth.py comments
  - [ ] 7.1 Translate all Chinese comments and docstrings in logic_growth.py to English
    - State names: 休眠→Dormant, 幼年→Baby, 成年→Adult
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 8. Translate theme_manager.py comments
  - [ ] 8.1 Translate all Chinese comments and docstrings in theme_manager.py to English
    - Keep WARNING: dramatic style
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 9. Translate time_manager.py comments
  - [ ] 9.1 Translate all Chinese comments and docstrings in time_manager.py to English
    - Keep 🌙 emoji and dramatic deep-sea style
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 10. Translate ocean_background.py comments
  - [ ] 10.1 Translate all Chinese comments and docstrings in ocean_background.py to English
    - Keep WARNING: dramatic style
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [ ] 10.2 Wrap asset paths with resource_path() in ocean_background.py
    - Update SEABED_DAY_PATH and SEABED_NIGHT_PATH loading
    - _Requirements: 3.1, 3.3_

- [ ] 11. Translate ui_style.py comments
  - [ ] 11.1 Translate all Chinese comments in ui_style.py to English
    - Color palette comments, font fallback messages
    - _Requirements: 2.3, 2.4_

- [ ] 12. Checkpoint - Verify all translations
  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 13. Write property tests for i18n verification
  - [ ]* 13.1 Write property test for no Chinese characters in UI constants
    - **Property 1: No Chinese Characters in UI Text**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**
  - [ ]* 13.2 Write property test for no Chinese characters in source files
    - **Property 2: No Chinese Characters in Code Comments**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

- [ ] 14. Final Checkpoint - Verify all tests pass
  - Ensure all tests pass, ask the user if questions arise.
