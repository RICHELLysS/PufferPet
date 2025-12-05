"""V7 Refactor Property-Based Tests using Hypothesis"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hypothesis import given, strategies as st, settings
from pet_config import V7_PETS, GACHA_WEIGHTS, BASE_SIZE, ADULT_MULTIPLIER, RAY_MULTIPLIER, PET_SHAPES
from pet_core import PetRenderer
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap

# Ensure QApplication exists for Qt operations
_app = None
def get_app():
    global _app
    if _app is None:
        _app = QApplication.instance() or QApplication([])
    return _app


# **Feature: v7-refactor, Property 3: Gacha Probability Sum**
# **Validates: Requirements 5.2, 5.3, 5.4**
@settings(max_examples=100)
@given(dummy=st.just(None))
def test_property_3_gacha_probability_sum(dummy):
    """
    Property 3: Gacha Probability Sum
    *For any* gacha pool configuration, the sum of all pet probabilities 
    shall equal exactly 100%.
    
    This test verifies:
    1. All V7_PETS are present in GACHA_WEIGHTS
    2. The sum of all weights equals exactly 100
    3. Each weight is a positive integer
    """
    # Verify all V7 pets are in the gacha weights
    for pet_id in V7_PETS:
        assert pet_id in GACHA_WEIGHTS, f"Pet {pet_id} missing from GACHA_WEIGHTS"
    
    # Verify no extra pets in gacha weights
    for pet_id in GACHA_WEIGHTS:
        assert pet_id in V7_PETS, f"Unknown pet {pet_id} in GACHA_WEIGHTS"
    
    # Verify each weight is a positive integer
    for pet_id, weight in GACHA_WEIGHTS.items():
        assert isinstance(weight, int), f"Weight for {pet_id} should be int, got {type(weight)}"
        assert weight > 0, f"Weight for {pet_id} should be positive, got {weight}"
    
    # Verify total sum equals 100
    total = sum(GACHA_WEIGHTS.values())
    assert total == 100, f"Gacha weights should sum to 100, got {total}"


# Additional verification: specific probability values per requirements
@settings(max_examples=100)
@given(dummy=st.just(None))
def test_gacha_specific_probabilities(dummy):
    """
    Verify specific probability values as per Requirements 5.2, 5.3:
    - puffer, jelly, crab, starfish: 22% each
    - ray (SSR): 12%
    """
    # Common pets should have 22% each
    common_pets = ['puffer', 'jelly', 'crab', 'starfish']
    for pet_id in common_pets:
        assert GACHA_WEIGHTS[pet_id] == 22, f"{pet_id} should have 22% probability"
    
    # Ray (SSR) should have 12%
    assert GACHA_WEIGHTS['ray'] == 12, "ray should have 12% probability"


# **Feature: v7-refactor, Property 2: Pet Size Calculation Correctness**
# **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
@settings(max_examples=100)
@given(
    pet_id=st.sampled_from(V7_PETS),
    stage=st.sampled_from(['dormant', 'baby', 'adult'])
)
def test_property_2_pet_size_calculation(pet_id, stage):
    """
    Property 2: Pet Size Calculation Correctness
    *For any* pet_id and stage combination, the calculated size shall equal 
    BASE_SIZE × species_multiplier × stage_multiplier, where:
    - species_multiplier is 1.5 for ray and 1.0 for others
    - stage_multiplier is 1.5 for adult and 1.0 for baby/dormant
    """
    # Calculate expected size
    expected = BASE_SIZE  # 100px
    
    # Apply species multiplier (ray has racial advantage)
    species_multiplier = RAY_MULTIPLIER if pet_id == 'ray' else 1.0
    expected *= species_multiplier
    
    # Apply stage multiplier (adult is 1.5x larger)
    stage_multiplier = ADULT_MULTIPLIER if stage == 'adult' else 1.0
    expected *= stage_multiplier
    
    expected = int(expected)
    
    # Get actual calculated size
    actual = PetRenderer.calculate_size(pet_id, stage)
    
    assert actual == expected, (
        f"Size mismatch for {pet_id}/{stage}: "
        f"expected {expected}, got {actual}"
    )


# Verify specific size values per requirements
@settings(max_examples=100)
@given(dummy=st.just(None))
def test_size_specific_values(dummy):
    """
    Verify specific size values as per Requirements 2.1, 2.2, 2.3:
    - Standard pets: Baby=100px, Adult=150px
    - Ray: Baby=150px, Adult=225px
    """
    standard_pets = ['puffer', 'jelly', 'crab', 'starfish']
    
    # Standard pets baby size = 100px
    for pet_id in standard_pets:
        size = PetRenderer.calculate_size(pet_id, 'baby')
        assert size == 100, f"{pet_id} baby should be 100px, got {size}"
    
    # Standard pets adult size = 150px
    for pet_id in standard_pets:
        size = PetRenderer.calculate_size(pet_id, 'adult')
        assert size == 150, f"{pet_id} adult should be 150px, got {size}"
    
    # Ray baby size = 150px (1.5x base)
    ray_baby = PetRenderer.calculate_size('ray', 'baby')
    assert ray_baby == 150, f"ray baby should be 150px, got {ray_baby}"
    
    # Ray adult size = 225px (1.5x base × 1.5x adult)
    ray_adult = PetRenderer.calculate_size('ray', 'adult')
    assert ray_adult == 225, f"ray adult should be 225px, got {ray_adult}"


# **Feature: v7-refactor, Property 1: Placeholder Generation for Missing Images**
# **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6**
@settings(max_examples=100)
@given(
    pet_id=st.sampled_from(V7_PETS),
    stage=st.sampled_from(['dormant', 'baby', 'adult'])
)
def test_property_1_placeholder_generation(pet_id, stage):
    """
    Property 1: Placeholder Generation for Missing Images
    *For any* pet_id in V7_PETS, when image loading fails, the system shall 
    return a valid QPixmap with the correct geometric shape and color for that pet.
    """
    get_app()  # Ensure QApplication exists
    
    # Calculate expected size
    expected_size = PetRenderer.calculate_size(pet_id, stage)
    
    # Generate placeholder
    pixmap = PetRenderer.draw_placeholder(pet_id, expected_size)
    
    # Verify pixmap is valid
    assert pixmap is not None, f"Placeholder for {pet_id} should not be None"
    assert isinstance(pixmap, QPixmap), f"Placeholder should be QPixmap, got {type(pixmap)}"
    assert not pixmap.isNull(), f"Placeholder for {pet_id} should not be null"
    
    # Verify size matches expected
    assert pixmap.width() == expected_size, (
        f"Placeholder width for {pet_id}/{stage} should be {expected_size}, "
        f"got {pixmap.width()}"
    )
    assert pixmap.height() == expected_size, (
        f"Placeholder height for {pet_id}/{stage} should be {expected_size}, "
        f"got {pixmap.height()}"
    )


# Verify shape and color mapping per requirements
@settings(max_examples=100)
@given(dummy=st.just(None))
def test_placeholder_shape_color_mapping(dummy):
    """
    Verify shape and color mapping as per Requirements 1.2-1.6:
    - puffer: green circle (#90EE90)
    - jelly: pink triangle (#FFB6C1)
    - crab: red rectangle (#FF6B6B)
    - starfish: yellow pentagon (#FFD700)
    - ray: blue diamond (#4682B4)
    """
    expected_mappings = {
        'puffer': ('circle', '#90EE90'),
        'jelly': ('triangle', '#FFB6C1'),
        'crab': ('rectangle', '#FF6B6B'),
        'starfish': ('pentagon', '#FFD700'),
        'ray': ('diamond', '#4682B4'),
    }
    
    for pet_id, (expected_shape, expected_color) in expected_mappings.items():
        shape, color = PET_SHAPES.get(pet_id, (None, None))
        assert shape == expected_shape, (
            f"{pet_id} should have shape '{expected_shape}', got '{shape}'"
        )
        assert color == expected_color, (
            f"{pet_id} should have color '{expected_color}', got '{color}'"
        )


# **Feature: v7-refactor, Property 4: Inventory Capacity Enforcement**
# **Validates: Requirements 4.5, 4.7**
@settings(max_examples=100, deadline=None)
@given(
    num_pets=st.integers(min_value=0, max_value=30),
    num_to_desktop=st.integers(min_value=0, max_value=10)
)
def test_property_4_inventory_capacity_enforcement(num_pets, num_to_desktop):
    """
    Property 4: Inventory Capacity Enforcement
    *For any* inventory state, the number of stored pets shall not exceed 
    MAX_INVENTORY (20), and the number of active desktop pets shall not 
    exceed MAX_ACTIVE (5).
    """
    from pet_config import MAX_INVENTORY, MAX_ACTIVE, V7_PETS
    from ui_inventory import MCInventoryWindow
    
    get_app()  # Ensure QApplication exists
    
    # Create a mock growth_manager
    class MockGrowthManager:
        def get_all_pets(self):
            return []
        def get_theme_mode(self):
            return 'normal'
    
    # Create inventory window
    inventory = MCInventoryWindow(MockGrowthManager())
    
    # Try to add pets up to num_pets
    added_count = 0
    for i in range(num_pets):
        pet_id = V7_PETS[i % len(V7_PETS)]  # Cycle through V7 pets
        # Add with unique suffix to allow duplicates
        unique_pet_id = f"{pet_id}_{i}"
        
        # Manually add to internal lists to test capacity
        if inventory.can_add_to_inventory():
            if added_count < num_to_desktop and inventory.can_add_to_desktop():
                inventory._active_pets.append(unique_pet_id)
            else:
                inventory._stored_pets.append(unique_pet_id)
            added_count += 1
    
    # Verify capacity constraints
    total_pets = len(inventory._active_pets) + len(inventory._stored_pets)
    active_count = len(inventory._active_pets)
    
    # Property: Total pets should never exceed MAX_INVENTORY
    assert total_pets <= MAX_INVENTORY, (
        f"Total pets ({total_pets}) exceeds MAX_INVENTORY ({MAX_INVENTORY})"
    )
    
    # Property: Active pets should never exceed MAX_ACTIVE
    assert active_count <= MAX_ACTIVE, (
        f"Active pets ({active_count}) exceeds MAX_ACTIVE ({MAX_ACTIVE})"
    )
    
    # Verify can_add methods work correctly
    if total_pets >= MAX_INVENTORY:
        assert not inventory.can_add_to_inventory(), (
            "can_add_to_inventory should return False when at capacity"
        )
    
    if active_count >= MAX_ACTIVE:
        assert not inventory.can_add_to_desktop(), (
            "can_add_to_desktop should return False when at capacity"
        )
    
    inventory.close()


# **Feature: v7-refactor, Property 5: Desktop Toggle Consistency**
# **Validates: Requirements 4.6**
@settings(max_examples=100)
@given(
    initial_active=st.integers(min_value=0, max_value=5),
    initial_stored=st.integers(min_value=0, max_value=15),
    toggle_index=st.integers(min_value=0, max_value=19)
)
def test_property_5_desktop_toggle_consistency(initial_active, initial_stored, toggle_index):
    """
    Property 5: Desktop Toggle Consistency
    *For any* pet toggle action, if a pet is toggled to desktop and desktop 
    count is below MAX_ACTIVE, the pet shall appear on desktop; if toggled 
    to inventory, the pet shall be removed from desktop.
    """
    from pet_config import MAX_ACTIVE, V7_PETS
    from ui_inventory import MCInventoryWindow
    
    get_app()  # Ensure QApplication exists
    
    # Create a mock growth_manager
    class MockGrowthManager:
        def get_all_pets(self):
            return []
        def get_theme_mode(self):
            return 'normal'
    
    # Create inventory window
    inventory = MCInventoryWindow(MockGrowthManager())
    
    # Setup initial state
    for i in range(initial_active):
        pet_id = f"active_pet_{i}"
        inventory._active_pets.append(pet_id)
    
    for i in range(initial_stored):
        pet_id = f"stored_pet_{i}"
        inventory._stored_pets.append(pet_id)
    
    total_pets = initial_active + initial_stored
    
    # Skip if no pets to toggle
    if total_pets == 0:
        inventory.close()
        return
    
    # Select a pet to toggle (within bounds)
    all_pets = inventory._active_pets + inventory._stored_pets
    pet_index = toggle_index % len(all_pets)
    pet_to_toggle = all_pets[pet_index]
    
    was_active = pet_to_toggle in inventory._active_pets
    active_count_before = len(inventory._active_pets)
    
    # Perform toggle
    result = inventory.toggle_pet_desktop(pet_to_toggle)
    
    is_active_after = pet_to_toggle in inventory._active_pets
    is_stored_after = pet_to_toggle in inventory._stored_pets
    
    if was_active:
        # Pet was on desktop, should now be in storage
        assert result == True, "Toggle from desktop should succeed"
        assert not is_active_after, "Pet should not be on desktop after toggle"
        assert is_stored_after, "Pet should be in storage after toggle"
    else:
        # Pet was in storage, try to move to desktop
        if active_count_before < MAX_ACTIVE:
            # Should succeed
            assert result == True, "Toggle to desktop should succeed when below MAX_ACTIVE"
            assert is_active_after, "Pet should be on desktop after toggle"
            assert not is_stored_after, "Pet should not be in storage after toggle"
        else:
            # Should fail (desktop full)
            assert result == False, "Toggle to desktop should fail when at MAX_ACTIVE"
            assert not is_active_after, "Pet should not be on desktop when toggle fails"
            assert is_stored_after, "Pet should remain in storage when toggle fails"
    
    # Verify pet is in exactly one location
    assert is_active_after != is_stored_after, (
        f"Pet should be in exactly one location: active={is_active_after}, stored={is_stored_after}"
    )
    
    inventory.close()


# **Feature: v7-refactor, Property 6: Lifecycle Stage Size Transition**
# **Validates: Requirements 6.3**
@settings(max_examples=100)
@given(pet_id=st.sampled_from(V7_PETS))
def test_property_6_lifecycle_stage_size_transition(pet_id):
    """
    Property 6: Lifecycle Stage Size Transition
    *For any* pet transitioning from baby to adult stage, the pet size 
    shall increase by exactly 1.5x multiplier.
    
    This test verifies:
    1. Adult size is exactly 1.5x the baby size for all V7 pets
    2. The multiplier is consistent across all species
    """
    # Get baby size
    baby_size = PetRenderer.calculate_size(pet_id, 'baby')
    
    # Get adult size
    adult_size = PetRenderer.calculate_size(pet_id, 'adult')
    
    # Verify adult is exactly 1.5x baby
    expected_adult_size = int(baby_size * ADULT_MULTIPLIER)
    
    assert adult_size == expected_adult_size, (
        f"Adult size for {pet_id} should be {expected_adult_size} "
        f"(baby {baby_size} × 1.5), got {adult_size}"
    )
    
    # Verify the ratio is exactly 1.5
    ratio = adult_size / baby_size
    assert abs(ratio - 1.5) < 0.01, (
        f"Size ratio for {pet_id} should be 1.5, got {ratio}"
    )


# Additional verification: dormant to baby has no size change
@settings(max_examples=100)
@given(pet_id=st.sampled_from(V7_PETS))
def test_dormant_to_baby_size_unchanged(pet_id):
    """
    Verify that dormant and baby stages have the same size.
    The size increase only happens when transitioning to adult.
    """
    dormant_size = PetRenderer.calculate_size(pet_id, 'dormant')
    baby_size = PetRenderer.calculate_size(pet_id, 'baby')
    
    assert dormant_size == baby_size, (
        f"Dormant and baby size for {pet_id} should be equal: "
        f"dormant={dormant_size}, baby={baby_size}"
    )
