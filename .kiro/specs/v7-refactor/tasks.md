# Implementation Plan

- [x] 1. Create pet_config.py with V7 constants and mappings






  - [x] 1.1 Create pet_config.py with V7_PETS list and size constants

    - Define V7_PETS = ['puffer', 'jelly', 'crab', 'starfish', 'ray']
    - Define BASE_SIZE = 100, ADULT_MULTIPLIER = 1.5, RAY_MULTIPLIER = 1.5
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 1.2 Add PET_SHAPES mapping with shape types and colors

    - puffer: ('circle', '#90EE90'), jelly: ('triangle', '#FFB6C1')
    - crab: ('rectangle', '#FF6B6B'), starfish: ('pentagon', '#FFD700')
    - ray: ('diamond', '#4682B4')
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6_


  - [x] 1.3 Add GACHA_WEIGHTS with V7 probabilities
    - puffer/jelly/crab/starfish: 22 each, ray: 12
    - _Requirements: 5.2, 5.3_

  - [x] 1.4 Add inventory constants
    - MAX_INVENTORY = 20, MAX_ACTIVE = 5, GRID_COLUMNS = 2
    - _Requirements: 4.5, 4.7_
  - [x] 1.5 Write property test for gacha probability sum


    - **Property 3: Gacha Probability Sum**
    - **Validates: Requirements 5.2, 5.3, 5.4**

- [x] 2. Update pet_core.py with PetRenderer and geometry drawing



  - [x] 2.1 Add PetRenderer class with calculate_size() method


    - Apply BASE_SIZE × species_multiplier × stage_multiplier
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [x] 2.2 Implement draw_circle() for puffer placeholder

    - Green circle (#90EE90)
    - _Requirements: 1.6_
  - [x] 2.3 Implement draw_triangle() for jelly placeholder

    - Pink triangle (#FFB6C1)
    - _Requirements: 1.2_

  - [x] 2.4 Implement draw_rectangle() for crab placeholder
    - Red rectangle (#FF6B6B)

    - _Requirements: 1.3_
  - [x] 2.5 Implement draw_pentagon() for starfish placeholder

    - Yellow pentagon (#FFD700)
    - _Requirements: 1.4_

  - [x] 2.6 Implement draw_diamond() for ray placeholder
    - Blue diamond (#4682B4)

    - _Requirements: 1.5_
  - [x] 2.7 Implement draw_placeholder() dispatcher method

    - Route to correct shape based on pet_id
    - _Requirements: 1.1_
  - [x] 2.8 Update _load_image() to use PetRenderer for fallback
    - Check for missing/empty files, use draw_placeholder()
    - _Requirements: 1.1_
  - [x] 2.9 Update size calculation in PetWidget to use PetRenderer
    - Replace hardcoded sizes with calculate_size()
    - _Requirements: 2.4_
  - [x] 2.10 Write property test for pet size calculation


    - **Property 2: Pet Size Calculation Correctness**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

  - [x] 2.11 Write property test for placeholder generation


    - **Property 1: Placeholder Generation for Missing Images**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6**

- [x] 3. Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Rewrite ui_inventory.py with MC-style grid





  - [x] 4.1 Create MCInventoryWindow class with 2-column grid layout


    - Use QGridLayout with GRID_COLUMNS = 2
    - _Requirements: 4.1_

  - [x] 4.2 Implement _create_slot() with MC-style styling
    - Dark gray background (#8B8B8B), light gray border (#C6C6C6)
    - White border on hover/selection
    - _Requirements: 4.2, 4.3_
  - [x] 4.3 Implement slot content display with pet icon or mini placeholder

    - Load default_icon or draw miniature geometric shape
    - _Requirements: 4.4_

  - [x] 4.4 Implement click handler for desktop/inventory toggle
    - Toggle pet between active and stored state
    - _Requirements: 4.6_

  - [x] 4.5 Add capacity enforcement for MAX_INVENTORY and MAX_ACTIVE
    - Reject operations that exceed limits
    - _Requirements: 4.5, 4.7_
  - [x] 4.6 Write property test for inventory capacity enforcement


    - **Property 4: Inventory Capacity Enforcement**
    - **Validates: Requirements 4.5, 4.7**
  - [x] 4.7 Write property test for desktop toggle consistency

    - **Property 5: Desktop Toggle Consistency**
    - **Validates: Requirements 4.6**

- [x] 5. Update ui_gacha.py with V7 pet pool





  - [x] 5.1 Import GACHA_WEIGHTS and V7_PETS from pet_config


    - Remove old TIER3_WEIGHTS
    - _Requirements: 5.1_
  - [x] 5.2 Update roll_gacha() to use new weights


    - Use V7 probability distribution
    - _Requirements: 5.2, 5.3_

  - [x] 5.3 Update PET_NAMES and PET_COLORS for V7 pets only
    - Remove deleted pets from mappings
    - _Requirements: 5.1_

- [x] 6. Update main.py for V7 compatibility





  - [x] 6.1 Import pet_config and use V7_PETS


    - Replace hardcoded pet lists
    - _Requirements: 5.1_
  - [x] 6.2 Update _check_encounter() to use V7 pets only


    - Remove references to deleted pets
    - _Requirements: 5.1_
  - [x] 6.3 Ensure lifecycle transitions update pet size correctly


    - Call PetRenderer.calculate_size() on stage change
    - _Requirements: 6.3_
  - [x] 6.4 Write property test for lifecycle stage size transition


    - **Property 6: Lifecycle Stage Size Transition**
    - **Validates: Requirements 6.3**

- [x] 7. Final Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.
