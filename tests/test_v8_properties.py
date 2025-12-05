"""V8 Final Polish Property-Based Tests using Hypothesis

This module contains property-based tests for the V8 Final Polish spec.
Tests verify correctness properties defined in the design document.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hypothesis import given, strategies as st, settings
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QApplication

# Ensure QApplication exists for Qt operations
_app = None
def get_app():
    global _app
    if _app is None:
        _app = QApplication.instance() or QApplication([])
    return _app


# **Feature: v8-final-polish, Property 1: Day/Night Toggle Round-Trip**
# **Validates: Requirements 1.2**
@settings(max_examples=100)
@given(
    initial_mode=st.sampled_from(["day", "night"])
)
def test_property_1_day_night_toggle_round_trip(initial_mode):
    """
    Property 1: Day/Night Toggle Round-Trip
    *For any* current theme mode (normal or halloween), calling toggle_day_night() 
    twice shall return to the original mode.
    
    This test verifies:
    1. Starting from any mode (day/night), toggling once switches to the opposite mode
    2. Toggling a second time returns to the original mode
    3. The round-trip is consistent regardless of starting mode
    """
    get_app()  # Ensure QApplication exists
    
    from time_manager import TimeManager
    from theme_manager import ThemeManager
    from main import on_toggle_day_night
    
    # Create fresh instances for each test
    theme_manager = ThemeManager()
    time_manager = TimeManager(theme_manager=theme_manager)
    
    # V8: Disable auto-sync as per V8 requirements
    time_manager.set_auto_sync(False)
    
    # Set initial mode
    if initial_mode == "day":
        time_manager.switch_to_day()
    else:
        time_manager.switch_to_night()
    
    # Record the initial period
    original_period = time_manager.get_current_period()
    assert original_period == initial_mode, (
        f"Initial period should be {initial_mode}, got {original_period}"
    )
    
    # First toggle - should switch to opposite mode
    on_toggle_day_night(time_manager)
    
    after_first_toggle = time_manager.get_current_period()
    expected_after_first = "night" if initial_mode == "day" else "day"
    assert after_first_toggle == expected_after_first, (
        f"After first toggle from {initial_mode}, expected {expected_after_first}, "
        f"got {after_first_toggle}"
    )
    
    # Second toggle - should return to original mode (round-trip)
    on_toggle_day_night(time_manager)
    
    after_second_toggle = time_manager.get_current_period()
    assert after_second_toggle == original_period, (
        f"After second toggle (round-trip), expected {original_period}, "
        f"got {after_second_toggle}. Round-trip property violated!"
    )


# Additional test: Verify theme mode mapping is consistent with day/night toggle
@settings(max_examples=100)
@given(
    initial_mode=st.sampled_from(["day", "night"])
)
def test_day_night_theme_mode_mapping(initial_mode):
    """
    Verify that day/night mode correctly maps to theme modes:
    - day -> normal
    - night -> halloween
    
    This ensures the toggle affects the visual theme correctly.
    """
    get_app()
    
    from time_manager import TimeManager
    from theme_manager import ThemeManager
    
    theme_manager = ThemeManager()
    time_manager = TimeManager(theme_manager=theme_manager)
    time_manager.set_auto_sync(False)
    
    # Set initial mode
    if initial_mode == "day":
        time_manager.switch_to_day()
        expected_theme = "normal"
    else:
        time_manager.switch_to_night()
        expected_theme = "halloween"
    
    # Verify theme mode mapping
    actual_theme = theme_manager.get_theme_mode()
    assert actual_theme == expected_theme, (
        f"For {initial_mode} mode, expected theme '{expected_theme}', "
        f"got '{actual_theme}'"
    )


# Test: Multiple consecutive toggles maintain consistency
@settings(max_examples=100)
@given(
    initial_mode=st.sampled_from(["day", "night"]),
    toggle_count=st.integers(min_value=1, max_value=10)
)
def test_multiple_toggles_consistency(initial_mode, toggle_count):
    """
    Verify that multiple toggles maintain consistency:
    - Even number of toggles returns to original mode
    - Odd number of toggles results in opposite mode
    """
    get_app()
    
    from time_manager import TimeManager
    from theme_manager import ThemeManager
    from main import on_toggle_day_night
    
    theme_manager = ThemeManager()
    time_manager = TimeManager(theme_manager=theme_manager)
    time_manager.set_auto_sync(False)
    
    # Set initial mode
    if initial_mode == "day":
        time_manager.switch_to_day()
    else:
        time_manager.switch_to_night()
    
    original_period = time_manager.get_current_period()
    
    # Perform multiple toggles
    for _ in range(toggle_count):
        on_toggle_day_night(time_manager)
    
    final_period = time_manager.get_current_period()
    
    # Determine expected result based on toggle count parity
    if toggle_count % 2 == 0:
        # Even toggles -> back to original
        expected_period = original_period
    else:
        # Odd toggles -> opposite mode
        expected_period = "night" if original_period == "day" else "day"
    
    assert final_period == expected_period, (
        f"After {toggle_count} toggles from {original_period}, "
        f"expected {expected_period}, got {final_period}"
    )


# **Feature: v8-final-polish, Property 2: Task Requirements Based on Pet Type and State**
# **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**
@settings(max_examples=100)
@given(
    pet_id=st.sampled_from(["puffer", "jelly", "crab", "starfish", "ray"]),
    state=st.integers(min_value=0, max_value=2)
)
def test_property_2_task_requirements_by_pet_type_and_state(pet_id, state):
    """
    Property 2: Task Requirements Based on Pet Type and State
    
    *For any* pet_id and state combination, get_tasks_to_next_state() shall return:
    - Ray in state 0: 2
    - Ray in state 1: 3
    - Non-Ray in state 0: 1
    - Non-Ray in state 1: 2
    - Any pet in state 2: 0
    
    This test verifies:
    1. Ray (SSR) requires more tasks: 2 to awaken, 3 to become adult (total 5)
    2. Non-Ray pets require standard tasks: 1 to awaken, 2 to become adult (total 3)
    3. Adult pets (state 2) require 0 tasks (no further progression)
    """
    import tempfile
    import os
    from logic_growth import GrowthManager
    
    # Create a temporary data file for isolated testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        # Create fresh GrowthManager instance
        gm = GrowthManager(temp_file)
        
        # Add the pet and set its state directly
        gm.add_pet(pet_id)
        gm.pets[pet_id].state = state
        
        # Get tasks to next state
        tasks_needed = gm.get_tasks_to_next_state(pet_id)
        
        # Determine expected value based on pet type and state
        if state == 2:  # Adult state - no more tasks needed
            expected_tasks = 0
        elif pet_id == "ray":  # Ray SSR special requirements
            if state == 0:  # dormant -> baby
                expected_tasks = 2
            else:  # state == 1, baby -> adult
                expected_tasks = 3
        else:  # Non-Ray pets (default requirements)
            if state == 0:  # dormant -> baby
                expected_tasks = 1
            else:  # state == 1, baby -> adult
                expected_tasks = 2
        
        assert tasks_needed == expected_tasks, (
            f"For pet '{pet_id}' in state {state}, expected {expected_tasks} tasks, "
            f"got {tasks_needed}. "
            f"{'Ray requires 2/3 tasks' if pet_id == 'ray' else 'Non-Ray requires 1/2 tasks'}"
        )
    finally:
        # Cleanup temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)


# **Feature: v8-final-polish, Property 3: Gacha Probability Distribution**
# **Validates: Requirements 2.2**
@settings(max_examples=100)
@given(
    num_rolls=st.integers(min_value=1000, max_value=5000)
)
def test_property_3_gacha_probability_distribution(num_rolls):
    """
    Property 3: Gacha Probability Distribution
    
    *For any* large number of gacha rolls (N > 1000), the distribution shall 
    approximate: 22% each for puffer/jelly/crab/starfish, 12% for ray 
    (within ±5% tolerance).
    
    This test verifies:
    1. Common pets (puffer, jelly, crab, starfish) each appear ~22% of the time
    2. SSR pet (ray) appears ~12% of the time
    3. Distribution is within acceptable tolerance (±5%)
    """
    from ui_gacha import roll_gacha
    from pet_config import GACHA_WEIGHTS, V7_PETS
    
    # Perform the rolls
    results = {pet_id: 0 for pet_id in V7_PETS}
    for _ in range(num_rolls):
        pet_id = roll_gacha()
        results[pet_id] += 1
    
    # Calculate actual percentages
    actual_percentages = {pet_id: (count / num_rolls) * 100 for pet_id, count in results.items()}
    
    # Expected percentages from GACHA_WEIGHTS
    expected_percentages = {pet_id: weight for pet_id, weight in GACHA_WEIGHTS.items()}
    
    # Tolerance: ±5% absolute
    tolerance = 5.0
    
    # Verify each pet's distribution is within tolerance
    for pet_id in V7_PETS:
        expected = expected_percentages[pet_id]
        actual = actual_percentages[pet_id]
        diff = abs(actual - expected)
        
        assert diff <= tolerance, (
            f"Gacha distribution for '{pet_id}' is out of tolerance. "
            f"Expected ~{expected}%, got {actual:.2f}% (diff: {diff:.2f}%). "
            f"Tolerance: ±{tolerance}%. "
            f"Total rolls: {num_rolls}, counts: {results}"
        )
    
    # Verify all pets were rolled at least once (sanity check)
    for pet_id in V7_PETS:
        assert results[pet_id] > 0, (
            f"Pet '{pet_id}' was never rolled in {num_rolls} attempts. "
            f"This is statistically improbable and indicates a bug."
        )


# **Feature: v8-final-polish, Property 4: Tutorial Text for Dormant State**
# **Validates: Requirements 4.1**
@settings(max_examples=100, deadline=500)  # Increased deadline for Qt widget creation
@given(
    pet_id=st.sampled_from(["puffer", "jelly", "crab", "starfish", "ray"])
)
def test_property_4_tutorial_text_for_dormant_state(pet_id):
    """
    Property 4: Tutorial Text for Dormant State
    
    *For any* pet in dormant state (state 0), get_tutorial_text() shall return 
    a string containing "右键点击我" or "Right Click Me".
    
    This test verifies:
    1. Dormant pets display the correct tutorial hint
    2. The hint contains the expected text for right-click instruction
    3. The property holds for all V7 pet types
    """
    import tempfile
    import os
    get_app()  # Ensure QApplication exists for Qt widgets
    
    from logic_growth import GrowthManager
    from pet_core import PetWidget, TUTORIAL_BUBBLES
    
    # Create a temporary data file for isolated testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        # Create fresh GrowthManager instance
        gm = GrowthManager(temp_file)
        
        # Add the pet in dormant state (state 0)
        gm.add_pet(pet_id)
        gm.pets[pet_id].state = 0  # Ensure dormant state
        
        # Create PetWidget for this pet
        pet_widget = PetWidget(pet_id, gm)
        
        # Verify the pet is in dormant state
        assert pet_widget.is_dormant, (
            f"Pet '{pet_id}' should be in dormant state (is_dormant=True), "
            f"but is_dormant={pet_widget.is_dormant}"
        )
        
        # Get tutorial text
        tutorial_text = pet_widget.get_tutorial_text()
        
        # Verify tutorial text contains expected content
        # According to Requirements 4.1: "右键点击我！(Right Click Me!)"
        assert "右键点击我" in tutorial_text or "Right Click Me" in tutorial_text, (
            f"For dormant pet '{pet_id}', tutorial text should contain "
            f"'右键点击我' or 'Right Click Me', but got: '{tutorial_text}'"
        )
        
        # Also verify it matches the expected TUTORIAL_BUBBLES constant
        expected_text = TUTORIAL_BUBBLES["dormant"]
        assert tutorial_text == expected_text, (
            f"Tutorial text for dormant pet '{pet_id}' should be '{expected_text}', "
            f"but got '{tutorial_text}'"
        )
        
        # Cleanup widget
        pet_widget.close()
        pet_widget.deleteLater()
        
    finally:
        # Cleanup temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)


# **Feature: v8-final-polish, Property 5: Geometric Fallback Consistency**
# **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
@settings(max_examples=100)
@given(
    pet_id=st.sampled_from(["puffer", "jelly", "crab", "starfish", "ray"]),
    size=st.integers(min_value=10, max_value=500)
)
def test_property_5_geometric_fallback_consistency(pet_id, size):
    """
    Property 5: Geometric Fallback Consistency
    
    *For any* V7 pet_id (puffer, jelly, crab, starfish, ray) and any positive size,
    PetRenderer.draw_placeholder() shall return a non-null QPixmap with the correct
    shape from PET_SHAPES.
    
    This test verifies:
    1. draw_placeholder() returns a non-null QPixmap for all V7 pets
    2. The returned QPixmap has the correct dimensions (size x size)
    3. The correct shape is used based on PET_SHAPES config
    4. The geometric fallback works reliably for any reasonable size
    """
    get_app()  # Ensure QApplication exists for Qt operations
    
    from pet_core import PetRenderer
    from pet_config import PET_SHAPES, V7_PETS
    
    # Verify pet_id is a valid V7 pet
    assert pet_id in V7_PETS, f"Pet '{pet_id}' should be in V7_PETS"
    
    # Verify pet_id has a shape configuration
    assert pet_id in PET_SHAPES, (
        f"Pet '{pet_id}' should have an entry in PET_SHAPES config"
    )
    
    # Get expected shape and color from config
    expected_shape, expected_color = PET_SHAPES[pet_id]
    
    # Call draw_placeholder
    pixmap = PetRenderer.draw_placeholder(pet_id, size)
    
    # Verify non-null QPixmap is returned (Requirements 5.4)
    assert pixmap is not None, (
        f"draw_placeholder('{pet_id}', {size}) returned None"
    )
    assert not pixmap.isNull(), (
        f"draw_placeholder('{pet_id}', {size}) returned a null QPixmap"
    )
    
    # Verify correct dimensions
    assert pixmap.width() == size, (
        f"Pixmap width should be {size}, got {pixmap.width()}"
    )
    assert pixmap.height() == size, (
        f"Pixmap height should be {size}, got {pixmap.height()}"
    )
    
    # Verify the shape mapping is correct (Requirements 5.2)
    # This validates that PET_SHAPES has the expected shape for each pet
    expected_shapes = {
        'puffer': 'circle',
        'jelly': 'triangle',
        'crab': 'rectangle',
        'starfish': 'pentagon',
        'ray': 'diamond',
    }
    assert expected_shape == expected_shapes[pet_id], (
        f"Pet '{pet_id}' should have shape '{expected_shapes[pet_id]}', "
        f"but PET_SHAPES has '{expected_shape}'"
    )


# Additional test: Verify geometric fallback works for all V7 pets at standard sizes
@settings(max_examples=100)
@given(
    pet_id=st.sampled_from(["puffer", "jelly", "crab", "starfish", "ray"]),
    stage=st.sampled_from(["dormant", "baby", "adult"])
)
def test_geometric_fallback_at_calculated_sizes(pet_id, stage):
    """
    Verify geometric fallback works at sizes calculated by PetRenderer.calculate_size().
    
    This ensures the fallback system works correctly with the actual sizes
    used in the application based on pet species and growth stage.
    """
    get_app()
    
    from pet_core import PetRenderer
    from pet_config import PET_SHAPES
    
    # Calculate the size that would be used in the application
    calculated_size = PetRenderer.calculate_size(pet_id, stage)
    
    # Verify size is positive
    assert calculated_size > 0, (
        f"Calculated size for '{pet_id}' at stage '{stage}' should be positive, "
        f"got {calculated_size}"
    )
    
    # Generate placeholder at calculated size
    pixmap = PetRenderer.draw_placeholder(pet_id, calculated_size)
    
    # Verify non-null QPixmap
    assert pixmap is not None and not pixmap.isNull(), (
        f"draw_placeholder('{pet_id}', {calculated_size}) failed for stage '{stage}'"
    )
    
    # Verify dimensions match calculated size
    assert pixmap.width() == calculated_size and pixmap.height() == calculated_size, (
        f"Pixmap dimensions should be {calculated_size}x{calculated_size}, "
        f"got {pixmap.width()}x{pixmap.height()}"
    )
