"""
Property-based tests for ui_style.py module.

Tests verify correctness properties for the Kiroween pixel-art styling system.
"""

import re
from hypothesis import given, strategies as st, settings

# Import the module under test
import ui_style
from ui_style import get_palette, get_stylesheet, get_font_family, PALETTES


# =============================================================================
# Strategy Generators
# =============================================================================

@st.composite
def valid_mode(draw):
    """Generate valid theme modes."""
    return draw(st.sampled_from(["normal", "halloween"]))


@st.composite
def any_mode_string(draw):
    """Generate any string that could be passed as a mode."""
    return draw(st.one_of(
        st.sampled_from(["normal", "halloween"]),
        st.text(min_size=0, max_size=20)
    ))


# =============================================================================
# Property Tests
# =============================================================================

# **Feature: ui-beautification, Property 2: Stylesheet Mode Consistency**
# **Validates: Requirements 2.1, 2.2, 2.3**
@settings(max_examples=100)
@given(mode=valid_mode())
def test_property_2_stylesheet_mode_consistency(mode):
    """
    Property 2: Stylesheet Mode Consistency
    
    *For any* valid mode ("normal" or "halloween"), calling `get_stylesheet(mode)` 
    shall return a non-empty string containing the correct palette colors for that mode.
    
    Updated for Minesweeper-style retro aesthetic.
    """
    # Get the stylesheet
    stylesheet = get_stylesheet(mode)
    
    # Verify non-empty string returned
    assert isinstance(stylesheet, str), "get_stylesheet should return a string"
    assert len(stylesheet) > 0, "get_stylesheet should return non-empty string"
    
    # Get the expected palette for this mode
    palette = get_palette(mode)
    
    # Verify the stylesheet contains the correct palette colors
    # Check background color
    assert palette["bg"].lower() in stylesheet.lower(), \
        f"Stylesheet should contain background color {palette['bg']} for mode {mode}"
    
    # Check foreground color
    assert palette["fg"].lower() in stylesheet.lower(), \
        f"Stylesheet should contain foreground color {palette['fg']} for mode {mode}"
    
    # Check highlight color
    assert palette["highlight"].lower() in stylesheet.lower(), \
        f"Stylesheet should contain highlight color {palette['highlight']} for mode {mode}"
    
    # Check border color
    assert palette["border"].lower() in stylesheet.lower(), \
        f"Stylesheet should contain border color {palette['border']} for mode {mode}"
    
    # Verify mode-specific colors are present (Minesweeper style)
    if mode == "normal":
        # Normal mode should have classic Windows gray background #C0C0C0
        assert "#c0c0c0" in stylesheet.lower(), \
            "Normal mode should contain Minesweeper gray background color #C0C0C0"
    elif mode == "halloween":
        # Halloween mode should have deep purple-black background #1A0A1A
        assert "#1a0a1a" in stylesheet.lower(), \
            "Halloween mode should contain Kiroween background color #1A0A1A"
        # Should have ghost green text #00FF88
        assert "#00ff88" in stylesheet.lower(), \
            "Halloween mode should contain ghost green #00FF88"


# **Feature: ui-beautification, Property 3: Zero Border-Radius Enforcement**
# **Validates: Requirements 2.4, 4.1, 5.1, 7.3**
@settings(max_examples=100)
@given(mode=valid_mode())
def test_property_3_zero_border_radius_enforcement(mode):
    """
    Property 3: Zero Border-Radius Enforcement
    
    *For any* stylesheet returned by `get_stylesheet()`, all `border-radius` 
    declarations shall have value `0px` to enforce pixel-art sharp edges.
    """
    stylesheet = get_stylesheet(mode)
    
    # Find all border-radius declarations
    # Pattern matches: border-radius: <value>
    border_radius_pattern = r'border-radius\s*:\s*([^;]+)'
    matches = re.findall(border_radius_pattern, stylesheet, re.IGNORECASE)
    
    # Verify we have border-radius declarations
    assert len(matches) > 0, "Stylesheet should contain border-radius declarations"
    
    # Verify all border-radius values are 0px
    for value in matches:
        value = value.strip()
        assert value == "0px", \
            f"All border-radius values should be 0px for pixel-art style, but found: {value}"


# **Feature: ui-beautification, Property 4: Border Width Consistency**
# **Validates: Requirements 2.5, 4.1, 5.1**
@settings(max_examples=100)
@given(mode=valid_mode())
def test_property_4_border_width_consistency(mode):
    """
    Property 4: Border Width Consistency
    
    *For any* stylesheet returned by `get_stylesheet()`, all `border-width` or 
    `border` declarations shall specify widths between 2px and 3px.
    """
    stylesheet = get_stylesheet(mode)
    
    # Find all border declarations with pixel widths
    # Pattern matches border: Npx solid ... or border-width: Npx
    # We look for patterns like "border: 2px solid" or "border: 3px solid"
    border_pattern = r'border\s*:\s*(\d+)px\s+solid'
    matches = re.findall(border_pattern, stylesheet, re.IGNORECASE)
    
    # Verify we have border declarations
    assert len(matches) > 0, "Stylesheet should contain border declarations"
    
    # Verify all border widths are between 2px and 3px
    for width_str in matches:
        width = int(width_str)
        assert 2 <= width <= 3, \
            f"Border width should be between 2px and 3px, but found: {width}px"


# =============================================================================
# Additional Unit Tests
# =============================================================================

def test_get_palette_returns_correct_keys():
    """Test that get_palette returns all required color keys."""
    # Updated for Minesweeper-style palette with 3D effect colors
    required_keys = {"bg", "fg", "highlight", "shadow", "border", "accent", 
                     "button_face", "button_light", "button_dark"}
    
    for mode in ["normal", "halloween"]:
        palette = get_palette(mode)
        assert set(palette.keys()) == required_keys, \
            f"Palette for {mode} should contain all required keys"


def test_get_palette_defaults_to_normal():
    """Test that get_palette defaults to normal mode for invalid input."""
    invalid_modes = ["invalid", "", "day", "night", "NORMAL", "Halloween"]
    normal_palette = get_palette("normal")
    
    for invalid_mode in invalid_modes:
        palette = get_palette(invalid_mode)
        assert palette == normal_palette, \
            f"Invalid mode '{invalid_mode}' should default to normal palette"


def test_get_stylesheet_returns_string():
    """Test that get_stylesheet returns a string for all valid modes."""
    for mode in ["normal", "halloween"]:
        stylesheet = get_stylesheet(mode)
        assert isinstance(stylesheet, str)
        assert len(stylesheet) > 100  # Should be substantial


def test_get_font_family_returns_string():
    """Test that get_font_family returns a valid CSS font-family string."""
    font_family = get_font_family()
    assert isinstance(font_family, str)
    assert len(font_family) > 0
    # Should contain at least one fallback font
    assert "Courier" in font_family or "Consolas" in font_family or "monospace" in font_family


def test_stylesheet_contains_qmenu_styling():
    """Test that stylesheet contains QMenu styling."""
    for mode in ["normal", "halloween"]:
        stylesheet = get_stylesheet(mode)
        assert "QMenu" in stylesheet, "Stylesheet should contain QMenu styling"
        assert "QMenu::item" in stylesheet, "Stylesheet should contain QMenu::item styling"
        assert "QMenu::item:selected" in stylesheet, "Stylesheet should contain QMenu::item:selected styling"


def test_stylesheet_contains_qpushbutton_styling():
    """Test that stylesheet contains QPushButton styling."""
    for mode in ["normal", "halloween"]:
        stylesheet = get_stylesheet(mode)
        assert "QPushButton" in stylesheet, "Stylesheet should contain QPushButton styling"
        assert "QPushButton:pressed" in stylesheet, "Stylesheet should contain QPushButton:pressed styling"
        assert "QPushButton:hover" in stylesheet, "Stylesheet should contain QPushButton:hover styling"


def test_stylesheet_contains_qcheckbox_styling():
    """Test that stylesheet contains QCheckBox styling."""
    for mode in ["normal", "halloween"]:
        stylesheet = get_stylesheet(mode)
        assert "QCheckBox" in stylesheet, "Stylesheet should contain QCheckBox styling"
        assert "QCheckBox::indicator" in stylesheet, "Stylesheet should contain QCheckBox::indicator styling"


def test_stylesheet_contains_qprogressbar_styling():
    """Test that stylesheet contains QProgressBar styling."""
    for mode in ["normal", "halloween"]:
        stylesheet = get_stylesheet(mode)
        assert "QProgressBar" in stylesheet, "Stylesheet should contain QProgressBar styling"
        assert "QProgressBar::chunk" in stylesheet, "Stylesheet should contain QProgressBar::chunk styling"


def test_stylesheet_contains_qdialog_styling():
    """Test that stylesheet contains QDialog styling."""
    for mode in ["normal", "halloween"]:
        stylesheet = get_stylesheet(mode)
        assert "QDialog" in stylesheet, "Stylesheet should contain QDialog styling"


def test_stylesheet_contains_qframe_styling():
    """Test that stylesheet contains QFrame styling."""
    for mode in ["normal", "halloween"]:
        stylesheet = get_stylesheet(mode)
        assert "QFrame" in stylesheet, "Stylesheet should contain QFrame styling"


# **Feature: ui-beautification, Property 5: Button Press Effect**
# **Validates: Requirements 5.2**
@settings(max_examples=100)
@given(mode=valid_mode())
def test_property_5_button_press_effect(mode):
    """
    Property 5: Button Press Effect
    
    *For any* stylesheet returned by `get_stylesheet()`, the QPushButton:pressed 
    selector shall include padding or margin adjustments that create a 1px offset effect.
    """
    stylesheet = get_stylesheet(mode)
    
    # Find the QPushButton:pressed section
    pressed_pattern = r'QPushButton:pressed\s*\{([^}]+)\}'
    match = re.search(pressed_pattern, stylesheet, re.IGNORECASE | re.DOTALL)
    
    assert match is not None, "Stylesheet should contain QPushButton:pressed styling"
    
    pressed_content = match.group(1)
    
    # Check for padding adjustments that create offset effect
    # The pressed state should have asymmetric padding to simulate press
    assert "padding" in pressed_content.lower(), \
        "QPushButton:pressed should have padding adjustments for offset effect"
    
    # Verify the offset creates asymmetry (different left/right or top/bottom padding)
    # Look for padding-left, padding-top, padding-right, padding-bottom
    padding_left = re.search(r'padding-left\s*:\s*(\d+)px', pressed_content, re.IGNORECASE)
    padding_right = re.search(r'padding-right\s*:\s*(\d+)px', pressed_content, re.IGNORECASE)
    padding_top = re.search(r'padding-top\s*:\s*(\d+)px', pressed_content, re.IGNORECASE)
    padding_bottom = re.search(r'padding-bottom\s*:\s*(\d+)px', pressed_content, re.IGNORECASE)
    
    # At least some padding values should be present
    has_padding_values = any([padding_left, padding_right, padding_top, padding_bottom])
    assert has_padding_values, \
        "QPushButton:pressed should have specific padding values for offset effect"
    
    # Check for asymmetry (offset effect means left != right or top != bottom)
    if padding_left and padding_right:
        left_val = int(padding_left.group(1))
        right_val = int(padding_right.group(1))
        assert left_val != right_val, \
            f"Padding left ({left_val}px) should differ from right ({right_val}px) for offset effect"
    
    if padding_top and padding_bottom:
        top_val = int(padding_top.group(1))
        bottom_val = int(padding_bottom.group(1))
        assert top_val != bottom_val, \
            f"Padding top ({top_val}px) should differ from bottom ({bottom_val}px) for offset effect"


def test_button_pressed_has_offset_effect():
    """Test that QPushButton:pressed has padding offset for press effect."""
    for mode in ["normal", "halloween"]:
        stylesheet = get_stylesheet(mode)
        
        # Find the QPushButton:pressed section
        pressed_pattern = r'QPushButton:pressed\s*\{([^}]+)\}'
        match = re.search(pressed_pattern, stylesheet, re.IGNORECASE | re.DOTALL)
        
        assert match is not None, "Stylesheet should contain QPushButton:pressed styling"
        
        pressed_content = match.group(1)
        
        # Check for padding adjustments that create offset effect
        # The pressed state should have asymmetric padding to simulate press
        assert "padding" in pressed_content.lower(), \
            "QPushButton:pressed should have padding adjustments for offset effect"


# **Feature: ui-beautification, Property 6: Checkbox Character Styling**
# **Validates: Requirements 6.1, 6.2**
@settings(max_examples=100)
@given(mode=valid_mode())
def test_property_6_checkbox_character_styling(mode):
    """
    Property 6: Checkbox Character Styling
    
    *For any* stylesheet returned by `get_stylesheet()`, the QCheckBox indicator 
    styling shall use square/rectangular shapes (not circular) to match pixel-art aesthetic.
    """
    stylesheet = get_stylesheet(mode)
    
    # Find the QCheckBox::indicator section
    indicator_pattern = r'QCheckBox::indicator\s*\{([^}]+)\}'
    match = re.search(indicator_pattern, stylesheet, re.IGNORECASE | re.DOTALL)
    
    assert match is not None, "Stylesheet should contain QCheckBox::indicator styling"
    
    indicator_content = match.group(1)
    
    # Check that border-radius is 0px (square, not circular)
    assert "border-radius" in indicator_content.lower(), \
        "QCheckBox::indicator should have border-radius defined"
    
    # Extract border-radius value
    radius_pattern = r'border-radius\s*:\s*([^;]+)'
    radius_match = re.search(radius_pattern, indicator_content, re.IGNORECASE)
    
    assert radius_match is not None, \
        "QCheckBox::indicator should have border-radius value"
    
    radius_value = radius_match.group(1).strip()
    assert radius_value == "0px", \
        f"QCheckBox::indicator border-radius should be 0px for square shape, but found: {radius_value}"
    
    # Verify the indicator has width and height defined (for square shape)
    assert "width" in indicator_content.lower(), \
        "QCheckBox::indicator should have width defined"
    assert "height" in indicator_content.lower(), \
        "QCheckBox::indicator should have height defined"
    
    # Verify checked and unchecked states exist
    checked_pattern = r'QCheckBox::indicator:checked\s*\{([^}]+)\}'
    unchecked_pattern = r'QCheckBox::indicator:unchecked\s*\{([^}]+)\}'
    
    checked_match = re.search(checked_pattern, stylesheet, re.IGNORECASE | re.DOTALL)
    unchecked_match = re.search(unchecked_pattern, stylesheet, re.IGNORECASE | re.DOTALL)
    
    assert checked_match is not None, \
        "Stylesheet should contain QCheckBox::indicator:checked styling"
    assert unchecked_match is not None, \
        "Stylesheet should contain QCheckBox::indicator:unchecked styling"


def test_checkbox_indicator_is_square():
    """Test that QCheckBox indicator uses square styling (not circular)."""
    for mode in ["normal", "halloween"]:
        stylesheet = get_stylesheet(mode)
        
        # Find the QCheckBox::indicator section
        indicator_pattern = r'QCheckBox::indicator\s*\{([^}]+)\}'
        match = re.search(indicator_pattern, stylesheet, re.IGNORECASE | re.DOTALL)
        
        assert match is not None, "Stylesheet should contain QCheckBox::indicator styling"
        
        indicator_content = match.group(1)
        
        # Check that border-radius is 0px (square, not circular)
        assert "border-radius" in indicator_content.lower(), \
            "QCheckBox::indicator should have border-radius defined"
        
        # Extract border-radius value
        radius_pattern = r'border-radius\s*:\s*([^;]+)'
        radius_match = re.search(radius_pattern, indicator_content, re.IGNORECASE)
        
        if radius_match:
            radius_value = radius_match.group(1).strip()
            assert radius_value == "0px", \
                f"QCheckBox::indicator border-radius should be 0px for square shape, but found: {radius_value}"


# =============================================================================
# Retro Kiroween UI Property Tests
# =============================================================================

# **Feature: retro-kiroween-ui, Property 1: 3D Raised Button Effect**
# **Validates: Requirements 1.1**
@settings(max_examples=100)
@given(mode=valid_mode())
def test_property_1_3d_raised_button_effect(mode):
    """
    Property 1: 3D Raised Button Effect
    
    *For any* stylesheet returned by `get_stylesheet()`, the QPushButton selector 
    shall have border-top and border-left using light color, and border-bottom 
    and border-right using dark color, creating a 3D raised effect.
    """
    stylesheet = get_stylesheet(mode)
    palette = get_palette(mode)
    
    # Find the QPushButton section (not :pressed, :hover, :disabled)
    button_pattern = r'QPushButton\s*\{([^}]+)\}'
    match = re.search(button_pattern, stylesheet, re.IGNORECASE | re.DOTALL)
    
    assert match is not None, "Stylesheet should contain QPushButton styling"
    
    button_content = match.group(1)
    
    # Check for 3D raised effect: light color on top-left, dark on bottom-right
    light_color = palette["button_light"].lower()
    dark_color = palette["button_dark"].lower()
    
    # Verify border-top uses light color
    assert f"border-top" in button_content.lower(), \
        "QPushButton should have border-top defined"
    assert light_color in button_content.lower(), \
        f"QPushButton should use light color {light_color} for 3D raised effect"
    
    # Verify border-bottom uses dark color
    assert f"border-bottom" in button_content.lower(), \
        "QPushButton should have border-bottom defined"
    assert dark_color in button_content.lower(), \
        f"QPushButton should use dark color {dark_color} for 3D raised effect"


# **Feature: retro-kiroween-ui, Property 2: 3D Sunken Pressed Effect**
# **Validates: Requirements 1.2**
@settings(max_examples=100)
@given(mode=valid_mode())
def test_property_2_3d_sunken_pressed_effect(mode):
    """
    Property 2: 3D Sunken Pressed Effect
    
    *For any* stylesheet returned by `get_stylesheet()`, the QPushButton:pressed 
    selector shall have inverted border colors compared to the normal state 
    (dark top-left, light bottom-right).
    """
    stylesheet = get_stylesheet(mode)
    palette = get_palette(mode)
    
    # Find the QPushButton:pressed section
    pressed_pattern = r'QPushButton:pressed\s*\{([^}]+)\}'
    match = re.search(pressed_pattern, stylesheet, re.IGNORECASE | re.DOTALL)
    
    assert match is not None, "Stylesheet should contain QPushButton:pressed styling"
    
    pressed_content = match.group(1)
    
    light_color = palette["button_light"].lower()
    dark_color = palette["button_dark"].lower()
    
    # For sunken effect, border-top should use dark color (inverted from raised)
    assert "border-top" in pressed_content.lower(), \
        "QPushButton:pressed should have border-top defined"
    
    # Check that dark color appears before light in the pressed section
    # (indicating dark is used for top/left borders)
    top_border_match = re.search(r'border-top[^;]*', pressed_content, re.IGNORECASE)
    assert top_border_match is not None, "QPushButton:pressed should have border-top"
    assert dark_color in top_border_match.group(0).lower(), \
        f"QPushButton:pressed border-top should use dark color {dark_color} for sunken effect"
    
    # Check border-bottom uses light color
    bottom_border_match = re.search(r'border-bottom[^;]*', pressed_content, re.IGNORECASE)
    assert bottom_border_match is not None, "QPushButton:pressed should have border-bottom"
    assert light_color in bottom_border_match.group(0).lower(), \
        f"QPushButton:pressed border-bottom should use light color {light_color} for sunken effect"


# **Feature: retro-kiroween-ui, Property 3: 3D Sunken Input Fields**
# **Validates: Requirements 1.3**
@settings(max_examples=100)
@given(mode=valid_mode())
def test_property_3_3d_sunken_input_fields(mode):
    """
    Property 3: 3D Sunken Input Fields
    
    *For any* stylesheet returned by `get_stylesheet()`, the QLineEdit and QFrame 
    selectors shall have 3D sunken border effect (dark top-left, light bottom-right).
    """
    stylesheet = get_stylesheet(mode)
    palette = get_palette(mode)
    
    light_color = palette["button_light"].lower()
    dark_color = palette["button_dark"].lower()
    
    # Check QLineEdit has sunken effect
    lineedit_pattern = r'QLineEdit\s*\{([^}]+)\}'
    lineedit_match = re.search(lineedit_pattern, stylesheet, re.IGNORECASE | re.DOTALL)
    
    assert lineedit_match is not None, "Stylesheet should contain QLineEdit styling"
    lineedit_content = lineedit_match.group(1)
    
    # Sunken effect: dark on top-left, light on bottom-right
    top_match = re.search(r'border-top[^;]*', lineedit_content, re.IGNORECASE)
    assert top_match is not None, "QLineEdit should have border-top"
    assert dark_color in top_match.group(0).lower(), \
        f"QLineEdit border-top should use dark color {dark_color} for sunken effect"
    
    # Check QFrame has sunken effect
    frame_pattern = r'QFrame\s*\{([^}]+)\}'
    frame_match = re.search(frame_pattern, stylesheet, re.IGNORECASE | re.DOTALL)
    
    assert frame_match is not None, "Stylesheet should contain QFrame styling"
    frame_content = frame_match.group(1)
    
    frame_top_match = re.search(r'border-top[^;]*', frame_content, re.IGNORECASE)
    assert frame_top_match is not None, "QFrame should have border-top"
    assert dark_color in frame_top_match.group(0).lower(), \
        f"QFrame border-top should use dark color {dark_color} for sunken effect"


# **Feature: retro-kiroween-ui, Property 4: Zero Border-Radius Enforcement**
# **Validates: Requirements 1.4**
@settings(max_examples=100)
@given(mode=valid_mode())
def test_property_4_zero_border_radius_enforcement(mode):
    """
    Property 4: Zero Border-Radius Enforcement
    
    *For any* stylesheet returned by `get_stylesheet()`, all border-radius 
    declarations shall have value 0px to enforce sharp pixel edges.
    """
    stylesheet = get_stylesheet(mode)
    
    # Find all border-radius declarations
    border_radius_pattern = r'border-radius\s*:\s*([^;]+)'
    matches = re.findall(border_radius_pattern, stylesheet, re.IGNORECASE)
    
    # Verify we have border-radius declarations
    assert len(matches) > 0, "Stylesheet should contain border-radius declarations"
    
    # Verify all border-radius values are 0px
    for value in matches:
        value = value.strip()
        assert value == "0px", \
            f"All border-radius values should be 0px for pixel-art style, but found: {value}"


# **Feature: retro-kiroween-ui, Property 5: Normal Mode Palette Consistency**
# **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
@settings(max_examples=100)
@given(st.just("normal"))
def test_property_5_normal_mode_palette_consistency(mode):
    """
    Property 5: Normal Mode Palette Consistency
    
    *For any* call to `get_palette("normal")`, the returned dictionary shall contain:
    bg=#C0C0C0, fg=#000000, button_light=#FFFFFF, button_dark=#808080, accent=#000080.
    """
    palette = get_palette(mode)
    
    # Verify required keys exist
    required_keys = ["bg", "fg", "button_light", "button_dark", "accent"]
    for key in required_keys:
        assert key in palette, f"Normal palette should contain key '{key}'"
    
    # Verify exact color values (case-insensitive comparison)
    assert palette["bg"].upper() == "#C0C0C0", \
        f"Normal mode bg should be #C0C0C0, got {palette['bg']}"
    assert palette["fg"].upper() == "#000000", \
        f"Normal mode fg should be #000000, got {palette['fg']}"
    assert palette["button_light"].upper() == "#FFFFFF", \
        f"Normal mode button_light should be #FFFFFF, got {palette['button_light']}"
    assert palette["button_dark"].upper() == "#808080", \
        f"Normal mode button_dark should be #808080, got {palette['button_dark']}"
    assert palette["accent"].upper() == "#000080", \
        f"Normal mode accent should be #000080, got {palette['accent']}"


# **Feature: retro-kiroween-ui, Property 6: Halloween Mode Palette Consistency**
# **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
@settings(max_examples=100)
@given(st.just("halloween"))
def test_property_6_halloween_mode_palette_consistency(mode):
    """
    Property 6: Halloween Mode Palette Consistency
    
    *For any* call to `get_palette("halloween")`, the returned dictionary shall contain:
    bg=#1A0A1A, fg=#00FF88, accent in [#FF0066, #FF6600], border=#8B00FF.
    """
    palette = get_palette(mode)
    
    # Verify required keys exist
    required_keys = ["bg", "fg", "accent", "border", "button_light"]
    for key in required_keys:
        assert key in palette, f"Halloween palette should contain key '{key}'"
    
    # Verify exact color values (case-insensitive comparison)
    assert palette["bg"].upper() == "#1A0A1A", \
        f"Halloween mode bg should be #1A0A1A, got {palette['bg']}"
    assert palette["fg"].upper() == "#00FF88", \
        f"Halloween mode fg should be #00FF88, got {palette['fg']}"
    
    # Accent can be blood red or pumpkin orange
    valid_accents = ["#FF0066", "#FF6600"]
    assert palette["accent"].upper() in valid_accents, \
        f"Halloween mode accent should be in {valid_accents}, got {palette['accent']}"
    
    # Border should be purple for supernatural glow
    assert palette["border"].upper() == "#8B00FF", \
        f"Halloween mode border should be #8B00FF, got {palette['border']}"
    
    # Button light should also be purple
    assert palette["button_light"].upper() == "#8B00FF", \
        f"Halloween mode button_light should be #8B00FF, got {palette['button_light']}"


# **Feature: retro-kiroween-ui, Property 10: Menu 3D Raised Border**
# **Validates: Requirements 7.1**
@settings(max_examples=100)
@given(mode=valid_mode())
def test_property_10_menu_3d_raised_border(mode):
    """
    Property 10: Menu 3D Raised Border
    
    *For any* stylesheet returned by `get_stylesheet()`, the QMenu selector 
    shall have 3D raised border effect (light top-left, dark bottom-right).
    """
    stylesheet = get_stylesheet(mode)
    palette = get_palette(mode)
    
    # Find the QMenu section
    menu_pattern = r'QMenu\s*\{([^}]+)\}'
    match = re.search(menu_pattern, stylesheet, re.IGNORECASE | re.DOTALL)
    
    assert match is not None, "Stylesheet should contain QMenu styling"
    
    menu_content = match.group(1)
    light_color = palette["button_light"].lower()
    dark_color = palette["button_dark"].lower()
    
    # Check for 3D raised effect: light on top-left, dark on bottom-right
    top_match = re.search(r'border-top[^;]*', menu_content, re.IGNORECASE)
    assert top_match is not None, "QMenu should have border-top"
    assert light_color in top_match.group(0).lower(), \
        f"QMenu border-top should use light color {light_color} for raised effect"
    
    bottom_match = re.search(r'border-bottom[^;]*', menu_content, re.IGNORECASE)
    assert bottom_match is not None, "QMenu should have border-bottom"
    assert dark_color in bottom_match.group(0).lower(), \
        f"QMenu border-bottom should use dark color {dark_color} for raised effect"


# **Feature: retro-kiroween-ui, Property 11: Menu Item Hover Inversion**
# **Validates: Requirements 7.2**
@settings(max_examples=100)
@given(mode=valid_mode())
def test_property_11_menu_item_hover_inversion(mode):
    """
    Property 11: Menu Item Hover Inversion
    
    *For any* stylesheet returned by `get_stylesheet()`, the QMenu::item:selected 
    selector shall have background-color set to a dark/accent color and color 
    set to a light/contrasting color.
    """
    stylesheet = get_stylesheet(mode)
    palette = get_palette(mode)
    
    # Find the QMenu::item:selected section
    selected_pattern = r'QMenu::item:selected\s*\{([^}]+)\}'
    match = re.search(selected_pattern, stylesheet, re.IGNORECASE | re.DOTALL)
    
    assert match is not None, "Stylesheet should contain QMenu::item:selected styling"
    
    selected_content = match.group(1)
    
    # Check that background-color is set to accent or dark color
    bg_match = re.search(r'background-color\s*:\s*([^;]+)', selected_content, re.IGNORECASE)
    assert bg_match is not None, "QMenu::item:selected should have background-color"
    
    bg_value = bg_match.group(1).strip().lower()
    accent_color = palette["accent"].lower()
    
    # Background should be accent color or a dark color
    assert accent_color in bg_value or bg_value != palette["bg"].lower(), \
        f"QMenu::item:selected background should be accent ({accent_color}) or dark, got {bg_value}"
    
    # Check that text color is light/contrasting
    color_match = re.search(r'(?<!background-)color\s*:\s*([^;]+)', selected_content, re.IGNORECASE)
    assert color_match is not None, "QMenu::item:selected should have color"
    
    text_color = color_match.group(1).strip().lower()
    # Text should be white or light color (contrasting with dark background)
    assert "#ffffff" in text_color or "#fff" in text_color or text_color != palette["fg"].lower(), \
        f"QMenu::item:selected text color should be light/contrasting, got {text_color}"


# **Feature: retro-kiroween-ui, Property 9: Checkbox Square Indicator**
# **Validates: Requirements 5.2**
@settings(max_examples=100)
@given(mode=valid_mode())
def test_property_9_checkbox_square_indicator(mode):
    """
    Property 9: Checkbox Square Indicator
    
    *For any* stylesheet returned by `get_stylesheet()`, the QCheckBox::indicator 
    selector shall have border-radius: 0px and 3D sunken border effect.
    """
    stylesheet = get_stylesheet(mode)
    palette = get_palette(mode)
    
    # Find the QCheckBox::indicator section
    indicator_pattern = r'QCheckBox::indicator\s*\{([^}]+)\}'
    match = re.search(indicator_pattern, stylesheet, re.IGNORECASE | re.DOTALL)
    
    assert match is not None, "Stylesheet should contain QCheckBox::indicator styling"
    
    indicator_content = match.group(1)
    
    # Check border-radius is 0px (square, not circular)
    radius_match = re.search(r'border-radius\s*:\s*([^;]+)', indicator_content, re.IGNORECASE)
    assert radius_match is not None, "QCheckBox::indicator should have border-radius"
    assert radius_match.group(1).strip() == "0px", \
        f"QCheckBox::indicator border-radius should be 0px, got {radius_match.group(1).strip()}"
    
    # Check for 3D sunken effect (dark top-left, light bottom-right)
    dark_color = palette["button_dark"].lower()
    light_color = palette["button_light"].lower()
    
    top_match = re.search(r'border-top[^;]*', indicator_content, re.IGNORECASE)
    assert top_match is not None, "QCheckBox::indicator should have border-top"
    assert dark_color in top_match.group(0).lower(), \
        f"QCheckBox::indicator border-top should use dark color {dark_color} for sunken effect"
    
    bottom_match = re.search(r'border-bottom[^;]*', indicator_content, re.IGNORECASE)
    assert bottom_match is not None, "QCheckBox::indicator should have border-bottom"
    assert light_color in bottom_match.group(0).lower(), \
        f"QCheckBox::indicator border-bottom should use light color {light_color} for sunken effect"
