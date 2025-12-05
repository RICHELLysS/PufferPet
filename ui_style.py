"""
ui_style.py - Centralized pixel-art style management module for PufferPet

Provides global QSS stylesheets and color palettes for the Kiroween retro aesthetic.
Supports Day Mode (retro handheld) and Night Mode (hacker/Halloween).

V7 Enhancements:
- Font crash prevention: Auto-fallback to system monospace fonts
- DOS terminal style: Black background, green text retro aesthetic
"""

import os
import sys
from typing import Dict, Optional

# Try to import PyQt6 for font loading
try:
    from PyQt6.QtGui import QFont, QFontDatabase
    from PyQt6.QtWidgets import QApplication
    HAS_PYQT = True
except ImportError:
    HAS_PYQT = False


# =============================================================================
# Color Palettes
# =============================================================================

PALETTES: Dict[str, Dict[str, str]] = {
    "normal": {
        # Minesweeper/Windows 95 retro style - Minesweeper Classic
        "bg": "#C0C0C0",           # Classic Windows gray background
        "fg": "#000000",           # Black text
        "highlight": "#DFDFDF",    # Highlight (light gray)
        "shadow": "#808080",       # Shadow (dark gray)
        "border": "#000000",       # Black border
        "accent": "#000080",       # Deep blue accent (Windows blue)
        "button_face": "#C0C0C0",  # Button face
        "button_light": "#FFFFFF", # 3D highlight (white - top-left border)
        "button_dark": "#808080",  # 3D shadow (dark gray - bottom-right border)
    },
    "halloween": {
        # Kiroween horror theme - Deep sea ghost style
        "bg": "#1A0A1A",           # Deep purple-black background
        "fg": "#00FF88",           # Ghost green text
        "highlight": "#FF6600",    # Pumpkin orange highlight
        "shadow": "#0D050D",       # Deeper shadow
        "border": "#8B00FF",       # Purple border
        "accent": "#FF0066",       # Blood red accent
        "button_face": "#2A1A2A",  # Dark purple button
        "button_light": "#8B00FF", # Purple highlight (3D top-left border)
        "button_dark": "#0D050D",  # Dark shadow (3D bottom-right border)
    }
}


# =============================================================================
# Font Configuration - V7 Font Crash Prevention System
# =============================================================================

FONT_CONFIG = {
    "pixel_font_path": "assets/fonts/pixel_font.ttf",
    # Platform-specific fallback fonts
    "fallback_fonts_windows": ["Consolas", "Courier New", "Lucida Console"],
    "fallback_fonts_mac": ["Menlo", "Monaco", "Courier"],
    "fallback_fonts_linux": ["DejaVu Sans Mono", "Liberation Mono", "Courier"],
    "base_size": 10,  # Smaller font size for retro feel
}

# Cache for loaded font
_loaded_font: Optional[QFont] = None
_font_family: Optional[str] = None
_using_fallback: bool = False  # Flag for fallback font usage


def _get_platform_fallback_fonts() -> list:
    """
    Get fallback font list for current platform.
    
    Returns:
        Monospace font list suitable for current OS
    """
    if sys.platform == 'win32':
        return FONT_CONFIG["fallback_fonts_windows"]
    elif sys.platform == 'darwin':
        return FONT_CONFIG["fallback_fonts_mac"]
    else:
        return FONT_CONFIG["fallback_fonts_linux"]


# =============================================================================
# Public API Functions
# =============================================================================

def get_palette(mode: str) -> Dict[str, str]:
    """
    Get the color palette for the specified mode.
    
    Args:
        mode: "normal" (Day Mode / Minesweeper style) or "halloween" (Kiroween Night Mode)
    
    Returns:
        Dictionary containing:
        - bg: Background color
        - fg: Foreground/text color
        - highlight: Highlight color
        - shadow: Shadow color
        - border: Border color
        - accent: Accent color
        - button_face: Button face color
        - button_light: Button highlight color (3D raised top-left)
        - button_dark: Button shadow color (3D raised bottom-right)
        
        Defaults to "normal" if invalid mode is provided.
    """
    if mode not in PALETTES:
        mode = "normal"
    return PALETTES[mode].copy()


def load_font() -> Optional[QFont]:
    """
    V7 Font Crash Prevention - Smart font loading
    
    Loading priority:
    1. Try to load assets/fonts/pixel_font.ttf
    2. If file doesn't exist or fails to load, auto-fallback to system monospace
    3. Use bold weight for retro feel
    
    Returns:
        QFont object configured for pixel-art display, or None if PyQt6 not available.
    """
    global _loaded_font, _using_fallback
    
    if not HAS_PYQT:
        return None
    
    if _loaded_font is not None:
        return _loaded_font
    
    font_path = FONT_CONFIG["pixel_font_path"]
    base_size = FONT_CONFIG["base_size"]
    
    # Try to load custom pixel font
    if os.path.exists(font_path):
        # Check if file is empty
        if os.path.getsize(font_path) > 0:
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    _loaded_font = QFont(font_families[0], base_size)
                    _loaded_font.setStyleStrategy(QFont.StyleStrategy.NoAntialias)
                    _using_fallback = False
                    print(f"[ui_style] Loaded pixel font: {font_families[0]}")
                    return _loaded_font
    
    # Fallback to system monospace font
    fallback_fonts = _get_platform_fallback_fonts()
    
    for fallback in fallback_fonts:
        font = QFont(fallback, base_size)
        # PyQt6 uses families() to check if font exists
        available_families = QFontDatabase.families()
        if fallback in available_families or font.exactMatch():
            font.setStyleStrategy(QFont.StyleStrategy.NoAntialias)
            font.setBold(True)  # Use bold for retro feel
            _loaded_font = font
            _using_fallback = True
            print(f"[ui_style] Using fallback font: {fallback} (bold)")
            return _loaded_font
    
    # Last resort: use system default monospace
    font = QFont("monospace", base_size)
    font.setStyleHint(QFont.StyleHint.Monospace)
    font.setBold(True)
    _loaded_font = font
    _using_fallback = True
    print("[ui_style] Using system default monospace font")
    return _loaded_font


# Backward compatibility
load_pixel_font = load_font


def is_using_fallback_font() -> bool:
    """
    Check if using fallback font.
    
    Returns:
        True if using fallback font, False if using custom pixel font
    """
    return _using_fallback


def get_font_family() -> str:
    """
    Get the font-family CSS string for use in stylesheets.
    
    V7: If using fallback font, returns platform-specific monospace font
    
    Returns:
        CSS font-family string, prioritizing pixel font with monospace fallbacks.
    """
    global _font_family
    
    if _font_family is not None:
        return _font_family
    
    font_path = FONT_CONFIG["pixel_font_path"]
    fallbacks = _get_platform_fallback_fonts()
    
    # Check if pixel font exists and is valid
    if os.path.exists(font_path) and os.path.getsize(font_path) > 0 and HAS_PYQT:
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                _font_family = f'"{font_families[0]}", ' + ", ".join(f'"{f}"' for f in fallbacks)
                return _font_family
    
    # Use fallback fonts
    _font_family = ", ".join(f'"{f}"' for f in fallbacks)
    return _font_family


def get_stylesheet(mode: str) -> str:
    """
    Get the complete QSS stylesheet for the specified mode.
    
    Args:
        mode: "normal" (Day Mode) or "halloween" (Night Mode)
    
    Returns:
        Complete QSS string covering all UI components with pixel-art styling.
    """
    palette = get_palette(mode)
    font_family = get_font_family()
    
    bg = palette["bg"]
    fg = palette["fg"]
    highlight = palette["highlight"]
    border = palette["border"]
    accent = palette["accent"]
    
    # Check if using fallback font, add bold if so
    font_weight = "bold" if is_using_fallback_font() else "normal"
    
    # Get Minesweeper-style extra colors
    shadow = palette.get("shadow", "#808080")
    button_face = palette.get("button_face", bg)
    button_light = palette.get("button_light", "#FFFFFF")
    button_dark = palette.get("button_dark", "#808080")
    
    stylesheet = f"""
/* ==========================================================================
   Global Pixel-Art Stylesheet - {mode.upper()} MODE
   V7: Windows 95 / Minesweeper Retro Aesthetic
   ========================================================================== */

/* Global font settings */
* {{
    font-family: {font_family};
    font-size: 11px;
    font-weight: {font_weight};
}}

/* ==========================================================================
   QMenu - Context Menu Styling (Windows 95 Style)
   ========================================================================== */
QMenu {{
    background-color: {button_face};
    color: {fg};
    border-top: 2px solid {button_light};
    border-left: 2px solid {button_light};
    border-bottom: 2px solid {button_dark};
    border-right: 2px solid {button_dark};
    border-radius: 0px;
    padding: 2px;
}}

QMenu::item {{
    background-color: transparent;
    padding: 4px 24px 4px 24px;
    border-radius: 0px;
}}

QMenu::item:selected {{
    background-color: {accent};
    color: #FFFFFF;
}}

QMenu::separator {{
    height: 2px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
        stop:0 {button_dark}, stop:0.5 {button_dark}, 
        stop:0.5 {button_light}, stop:1 {button_light});
    margin: 2px 2px;
}}

/* ==========================================================================
   QPushButton - Button Styling (3D Raised Effect like Minesweeper)
   ========================================================================== */
QPushButton {{
    background-color: {button_face};
    color: {fg};
    border-top: 2px solid {button_light};
    border-left: 2px solid {button_light};
    border-bottom: 2px solid {button_dark};
    border-right: 2px solid {button_dark};
    border-radius: 0px;
    padding: 4px 12px;
    min-height: 20px;
}}

QPushButton:hover {{
    background-color: {highlight};
    color: {fg};
}}

QPushButton:pressed {{
    background-color: {button_face};
    color: {fg};
    border-top: 2px solid {button_dark};
    border-left: 2px solid {button_dark};
    border-bottom: 2px solid {button_light};
    border-right: 2px solid {button_light};
    padding-left: 13px;
    padding-top: 5px;
}}

QPushButton:disabled {{
    background-color: {button_face};
    color: {shadow};
    border-top: 2px solid {button_light};
    border-left: 2px solid {button_light};
    border-bottom: 2px solid {button_dark};
    border-right: 2px solid {button_dark};
}}

/* ==========================================================================
   QCheckBox - Checkbox Styling (3D Sunken Indicator)
   ========================================================================== */
QCheckBox {{
    color: {fg};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-top: 2px solid {button_dark};
    border-left: 2px solid {button_dark};
    border-bottom: 2px solid {button_light};
    border-right: 2px solid {button_light};
    border-radius: 0px;
    background-color: {bg};
}}

QCheckBox::indicator:unchecked {{
    background-color: {bg};
}}

QCheckBox::indicator:checked {{
    background-color: {fg};
    border-top: 2px solid {button_dark};
    border-left: 2px solid {button_dark};
    border-bottom: 2px solid {button_light};
    border-right: 2px solid {button_light};
}}

QCheckBox::indicator:hover {{
    border-top: 2px solid {accent};
    border-left: 2px solid {accent};
    border-bottom: 2px solid {button_light};
    border-right: 2px solid {button_light};
}}

/* ==========================================================================
   QProgressBar - Progress Bar Styling (3D Sunken Container, Chunky Block)
   ========================================================================== */
QProgressBar {{
    background-color: {bg};
    border-top: 2px solid {button_dark};
    border-left: 2px solid {button_dark};
    border-bottom: 2px solid {button_light};
    border-right: 2px solid {button_light};
    border-radius: 0px;
    text-align: center;
    color: {fg};
    min-height: 20px;
}}

QProgressBar::chunk {{
    background-color: {fg};
    border-radius: 0px;
    margin: 2px;
    width: 10px;
}}

/* ==========================================================================
   QDialog - Dialog Window Styling
   ========================================================================== */
QDialog {{
    background-color: {bg};
    color: {fg};
    border: 3px solid {border};
    border-radius: 0px;
}}

/* ==========================================================================
   QFrame - Frame Styling (3D Sunken Effect)
   ========================================================================== */
QFrame {{
    background-color: {bg};
    color: {fg};
    border-top: 2px solid {button_dark};
    border-left: 2px solid {button_dark};
    border-bottom: 2px solid {button_light};
    border-right: 2px solid {button_light};
    border-radius: 0px;
}}

QFrame[frameShape="4"] {{
    /* HLine */
    background-color: {border};
    border: none;
    max-height: 2px;
}}

QFrame[frameShape="5"] {{
    /* VLine */
    background-color: {border};
    border: none;
    max-width: 2px;
}}

/* ==========================================================================
   QLabel - Label Styling
   ========================================================================== */
QLabel {{
    color: {fg};
    background-color: transparent;
    border: none;
}}

/* ==========================================================================
   QLineEdit - Text Input Styling (3D Sunken Effect)
   ========================================================================== */
QLineEdit {{
    background-color: {bg};
    color: {fg};
    border-top: 2px solid {button_dark};
    border-left: 2px solid {button_dark};
    border-bottom: 2px solid {button_light};
    border-right: 2px solid {button_light};
    border-radius: 0px;
    padding: 4px;
}}

QLineEdit:focus {{
    border-top: 2px solid {accent};
    border-left: 2px solid {accent};
    border-bottom: 2px solid {button_light};
    border-right: 2px solid {button_light};
}}

/* ==========================================================================
   QScrollBar - Scrollbar Styling
   ========================================================================== */
QScrollBar:vertical {{
    background-color: {bg};
    width: 16px;
    border: 2px solid {border};
    border-radius: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: {fg};
    border-radius: 0px;
    min-height: 20px;
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {bg};
    height: 16px;
    border: 2px solid {border};
    border-radius: 0px;
}}

QScrollBar::handle:horizontal {{
    background-color: {fg};
    border-radius: 0px;
    min-width: 20px;
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ==========================================================================
   QListWidget - List Widget Styling
   ========================================================================== */
QListWidget {{
    background-color: {bg};
    color: {fg};
    border: 2px solid {border};
    border-radius: 0px;
}}

QListWidget::item {{
    padding: 4px;
    border-radius: 0px;
}}

QListWidget::item:selected {{
    background-color: {fg};
    color: {bg};
}}

QListWidget::item:hover {{
    background-color: {highlight};
}}

/* ==========================================================================
   QToolTip - Tooltip Styling
   ========================================================================== */
QToolTip {{
    background-color: {bg};
    color: {fg};
    border: 2px solid {border};
    border-radius: 0px;
    padding: 4px;
}}
"""
    
    return stylesheet


def get_menu_stylesheet(mode: str) -> str:
    """
    Get a minimal QSS stylesheet specifically for QMenu styling.
    Useful when only menu styling is needed without full global styles.
    
    Args:
        mode: "normal" (Day Mode) or "halloween" (Night Mode)
    
    Returns:
        QSS string for QMenu styling only.
    """
    palette = get_palette(mode)
    
    bg = palette["bg"]
    fg = palette["fg"]
    border = palette["border"]
    
    return f"""
QMenu {{
    background-color: {bg};
    color: {fg};
    border: 2px solid {border};
    border-radius: 0px;
    padding: 2px;
}}

QMenu::item {{
    background-color: transparent;
    padding: 4px 20px 4px 10px;
    border-radius: 0px;
}}

QMenu::item:selected {{
    background-color: {fg};
    color: {bg};
}}

QMenu::separator {{
    height: 2px;
    background-color: {border};
    margin: 2px 4px;
}}
"""
