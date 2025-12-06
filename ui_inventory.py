"""
ui_inventory.py - V7 Retro Minesweeper-style Inventory System

WARNING: The depths hold many treasures... manage them wisely.

Windows 95 / Minesweeper retro-style inventory window:
- 2-column grid layout (GRID_COLUMNS = 2)
- 3D raised/sunken effects (Raised/Sunken borders)
- Uses global ui_style stylesheet
- Max inventory 20, max desktop display 5

Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7
Retro UI Requirements: 6.1, 6.2, 6.3
"""

import os
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QWidget, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QPainter, QFont, QCursor

# Import V7 configuration
from pet_config import (
    V7_PETS, MAX_INVENTORY, MAX_ACTIVE, GRID_COLUMNS, PET_SHAPES
)

# Import PetRenderer for geometric placeholders
from pet_core import PetRenderer

# Import pixel-art styling module
import ui_style

# Slot size for MC-style grid
SLOT_SIZE = 80  # Increased to accommodate 64px icon with padding
ICON_SIZE = 64  # V9: Icon size within slot (scaled from 1500x1500px original)

# V7 Pet names mapping
PET_NAMES = {
    'puffer': 'Puffer',
    'jelly': 'Jellyfish',
    'crab': 'Crab',
    'starfish': 'Starfish',
    'ray': 'Ray',
}


class MCInventorySlot(QFrame):
    """
    Windows 95 / Minesweeper风格背包格子
    
    Requirements 4.2, 4.3: Retro-style slot with 3D raised effect
    Requirements 6.2: Sharp corners (0px radius), 3D raised border effect
    """
    
    clicked = pyqtSignal(str)  # Emits pet_id when clicked
    
    def __init__(self, index: int, mode: str = "normal", parent=None):
        super().__init__(parent)
        self.index = index
        self.pet_id: Optional[str] = None
        self.is_active = False  # Whether pet is on desktop
        self.is_selected = False
        self._mode = mode  # Theme mode for styling
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup slot UI with retro Minesweeper styling"""
        self.setFixedSize(SLOT_SIZE, SLOT_SIZE)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._update_style()
        
        # Layout for content
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)  # V9: Increased margins for 64px icon
        layout.setSpacing(0)
        
        # Icon label - V9: 64x64px icon size
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(ICON_SIZE, ICON_SIZE)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def set_mode(self, mode: str):
        """Update theme mode and refresh styling"""
        self._mode = mode
        self._update_style()
    
    def _update_style(self):
        """
        Update slot style based on state with 3D raised effect
        
        Requirements 6.2: Sharp corners (0px radius), 3D raised border effect
        """
        # Get palette colors based on mode
        palette = ui_style.get_palette(self._mode)
        bg = palette["button_face"]
        button_light = palette["button_light"]
        button_dark = palette["button_dark"]
        accent = palette["accent"]
        
        if self.is_selected or self.is_active:
            # Accent border for selected/active - 3D raised with accent highlight
            self.setStyleSheet(f"""
                MCInventorySlot {{
                    background-color: {bg};
                    border-top: 3px solid {accent};
                    border-left: 3px solid {accent};
                    border-bottom: 3px solid {button_dark};
                    border-right: 3px solid {button_dark};
                    border-radius: 0px;
                }}
                MCInventorySlot:hover {{
                    border-top: 3px solid {accent};
                    border-left: 3px solid {accent};
                    border-bottom: 3px solid {button_dark};
                    border-right: 3px solid {button_dark};
                }}
            """)
        else:
            # Normal 3D raised effect
            self.setStyleSheet(f"""
                MCInventorySlot {{
                    background-color: {bg};
                    border-top: 2px solid {button_light};
                    border-left: 2px solid {button_light};
                    border-bottom: 2px solid {button_dark};
                    border-right: 2px solid {button_dark};
                    border-radius: 0px;
                }}
                MCInventorySlot:hover {{
                    border-top: 3px solid {button_light};
                    border-left: 3px solid {button_light};
                    border-bottom: 3px solid {button_dark};
                    border-right: 3px solid {button_dark};
                }}
            """)
    
    def set_pet(self, pet_id: Optional[str], is_active: bool = False, mode: str = None):
        """
        Set pet in this slot.
        
        Args:
            pet_id: Pet identifier or None for empty slot
            is_active: Whether pet is currently on desktop
            mode: Theme mode (optional, updates slot styling if provided)
        """
        self.pet_id = pet_id
        self.is_active = is_active
        if mode is not None:
            self._mode = mode
        self._update_style()
        
        if pet_id:
            # Load pet icon
            pixmap = self._load_pet_icon(pet_id)
            self.icon_label.setPixmap(pixmap)
            self.icon_label.setToolTip(f"{PET_NAMES.get(pet_id, pet_id)}\n{'[On Desktop]' if is_active else '[In Inventory]'}")
        else:
            # Empty slot
            self.icon_label.clear()
            self.icon_label.setToolTip("")
    
    def _load_pet_icon(self, pet_id: str) -> QPixmap:
        """
        Load pet icon or generate mini placeholder
        
        V9: Scale 1500x1500px default_icon to 64x64px
        Requirements 2.5, 4.4: Show default_icon or miniature geometric placeholder
        """
        # Try to load pet-specific default_icon first (V9: original is 1500x1500px)
        # New naming convention: [pet_id]_default_icon.png
        # Special case: jelly uses jellyfish_default_icon.png
        icon_paths = [
            f"assets/{pet_id}/{pet_id}_default_icon.png",
            f"assets/{pet_id}/jellyfish_default_icon.png" if pet_id == "jelly" else None,
            f"assets/{pet_id}/default_icon.png",  # Legacy fallback
        ]
        for icon_path in icon_paths:
            if icon_path and os.path.exists(icon_path) and os.path.getsize(icon_path) > 0:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    # V9: Scale from 1500x1500px to 64x64px
                    return PetRenderer.scale_frame(pixmap, ICON_SIZE)
        
        # Try baby_idle as fallback
        fallback_paths = [
            f"assets/{pet_id}/baby_idle.png",
            f"assets/{pet_id}/idle.png",
        ]
        for path in fallback_paths:
            if os.path.exists(path) and os.path.getsize(path) > 0:
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    return PetRenderer.scale_frame(pixmap, ICON_SIZE)
        
        # Generate miniature geometric placeholder using PetRenderer
        return PetRenderer.draw_placeholder(pet_id, ICON_SIZE)
    
    def mousePressEvent(self, event):
        """Handle click on slot"""
        if event.button() == Qt.MouseButton.LeftButton and self.pet_id:
            self.clicked.emit(self.pet_id)
        super().mousePressEvent(event)
    
    def set_selected(self, selected: bool):
        """Set selection state"""
        self.is_selected = selected
        self._update_style()


class MCInventoryWindow(QDialog):
    """
    Minecraft风格背包窗口
    
    Requirements 4.1: 2-column grid layout with dynamic rows
    Requirements 4.5, 4.7: Capacity enforcement (MAX_INVENTORY=20, MAX_ACTIVE=5)
    """
    
    # Signals
    pets_changed = pyqtSignal(list)  # Emitted when active_pets changes
    
    def __init__(self, growth_manager, parent=None):
        super().__init__(parent)
        self.growth_manager = growth_manager
        self.slots: List[MCInventorySlot] = []
        self._active_pets: List[str] = []
        self._stored_pets: List[str] = []
        
        self._setup_ui()
        self._apply_pixel_font()
        self._load_data()
    
    def _apply_pixel_font(self):
        """
        Apply pixel font and stylesheet for retro Minesweeper aesthetic
        
        Requirements 6.1: 3D raised border and gray background
        Requirements 6.3: Classic Windows 95 scrollbar style with 3D buttons
        """
        # Get current theme mode
        mode = "normal"
        if self.growth_manager is not None:
            mode = self.growth_manager.get_theme_mode()
        
        # Get palette for 3D border colors
        palette = ui_style.get_palette(mode)
        button_light = palette["button_light"]
        button_dark = palette["button_dark"]
        bg = palette["bg"]
        fg = palette["fg"]
        shadow = palette.get("shadow", "#808080")
        
        # Apply global stylesheet plus window-specific 3D raised border
        # Requirements 6.1: 3D raised border to window
        # Requirements 6.3: Windows 95 scrollbar style with 3D buttons
        window_style = f"""
            MCInventoryWindow {{
                background-color: {bg};
                border-top: 3px solid {button_light};
                border-left: 3px solid {button_light};
                border-bottom: 3px solid {button_dark};
                border-right: 3px solid {button_dark};
                border-radius: 0px;
            }}
            
            /* Windows 95 style scrollbar with 3D buttons */
            #inventoryScrollArea QScrollBar:vertical {{
                background-color: {bg};
                width: 18px;
                border: none;
                border-radius: 0px;
                margin: 18px 0 18px 0;
            }}
            
            #inventoryScrollArea QScrollBar::handle:vertical {{
                background-color: {bg};
                border-top: 2px solid {button_light};
                border-left: 2px solid {button_light};
                border-bottom: 2px solid {button_dark};
                border-right: 2px solid {button_dark};
                border-radius: 0px;
                min-height: 20px;
            }}
            
            #inventoryScrollArea QScrollBar::add-line:vertical {{
                background-color: {bg};
                border-top: 2px solid {button_light};
                border-left: 2px solid {button_light};
                border-bottom: 2px solid {button_dark};
                border-right: 2px solid {button_dark};
                height: 18px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                border-radius: 0px;
            }}
            
            #inventoryScrollArea QScrollBar::sub-line:vertical {{
                background-color: {bg};
                border-top: 2px solid {button_light};
                border-left: 2px solid {button_light};
                border-bottom: 2px solid {button_dark};
                border-right: 2px solid {button_dark};
                height: 18px;
                subcontrol-position: top;
                subcontrol-origin: margin;
                border-radius: 0px;
            }}
            
            #inventoryScrollArea QScrollBar::add-page:vertical,
            #inventoryScrollArea QScrollBar::sub-page:vertical {{
                background-color: {shadow};
            }}
            
            #inventoryGridWidget {{
                background-color: transparent;
                border: none;
            }}
        """
        
        # Combine global stylesheet with window-specific styles
        global_style = ui_style.get_stylesheet(mode)
        self.setStyleSheet(global_style + window_style)
        
        # Apply pixel font
        pixel_font = ui_style.load_pixel_font()
        if pixel_font:
            self.setFont(pixel_font)
    
    def _setup_ui(self):
        """
        Setup UI with retro Minesweeper-style grid layout.
        
        Requirements 6.1: 3D raised border and gray background
        Requirements 6.3: Classic Windows 95 scrollbar style
        """
        self.setWindowTitle("🎒 Inventory")
        self.setMinimumSize(200, 400)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header with title and status
        header = QHBoxLayout()
        title = QLabel("[ My Pets ]")
        # Title styling will be handled by global stylesheet
        header.addWidget(title)
        
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        header.addWidget(self.status_label)
        layout.addLayout(header)
        
        # Hint label - use theme-appropriate color
        hint = QLabel("Click to toggle: Desktop <-> Inventory")
        # Hint styling will be handled by global stylesheet
        layout.addWidget(hint)
        
        # Scroll area for grid with Windows 95 style scrollbar
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setObjectName("inventoryScrollArea")
        
        # Grid container
        self.grid_widget = QWidget()
        self.grid_widget.setObjectName("inventoryGridWidget")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(4)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create slots (MAX_INVENTORY slots in 2-column grid)
        self._create_slots()
        
        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll)
        
        # Bottom buttons - styling handled by global stylesheet
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("[ OK ]")
        close_btn.clicked.connect(self.close)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
    
    def _create_slots(self):
        """
        Create retro Minesweeper-style inventory slots
        
        Requirements 4.1: 2-column grid with GRID_COLUMNS = 2
        Requirements 6.2: Sharp corners (0px radius), 3D raised border effect
        """
        # Get current theme mode
        mode = "normal"
        if self.growth_manager is not None:
            mode = self.growth_manager.get_theme_mode()
        
        for i in range(MAX_INVENTORY):
            row = i // GRID_COLUMNS
            col = i % GRID_COLUMNS
            
            slot = MCInventorySlot(i, mode=mode)
            slot.clicked.connect(self._on_slot_clicked)
            
            self.grid_layout.addWidget(slot, row, col)
            self.slots.append(slot)
    
    def _load_data(self):
        """Load pet data and populate slots"""
        # V10: Load from growth_manager's unlocked and active pets
        if self.growth_manager:
            unlocked = self.growth_manager.get_unlocked_pets()
            active = self.growth_manager.get_active_pets()
            
            self._active_pets = [p for p in active if p in unlocked]
            self._stored_pets = [p for p in unlocked if p not in active]
        else:
            self._active_pets = ['puffer']
            self._stored_pets = []
        
        self._refresh_slots()
        self._update_status()
    
    def _refresh_slots(self):
        """Refresh all slot displays with current theme mode"""
        # Get current theme mode
        mode = "normal"
        if self.growth_manager is not None:
            mode = self.growth_manager.get_theme_mode()
        
        # Combine active and stored pets
        all_pets = self._active_pets + self._stored_pets
        
        for i, slot in enumerate(self.slots):
            if i < len(all_pets):
                pet_id = all_pets[i]
                is_active = pet_id in self._active_pets
                slot.set_pet(pet_id, is_active, mode=mode)
            else:
                slot.set_pet(None, mode=mode)
    
    def _on_slot_clicked(self, pet_id: str):
        """
        Handle slot click - show pet options menu.
        
        Requirements 4.6: Toggle pet between active and stored state
        Requirements 4.5, 4.7: Enforce capacity limits
        V10: Add release option (except for default pet 'puffer')
        """
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QCursor
        
        menu = QMenu(self)
        
        # Toggle desktop/inventory option
        if pet_id in self._active_pets:
            toggle_action = menu.addAction("📦 Move to Inventory")
        else:
            toggle_action = menu.addAction("🖥️ Move to Desktop")
        
        # Release option (not available for default pet 'puffer')
        release_action = None
        if pet_id != 'puffer':
            menu.addSeparator()
            release_action = menu.addAction("🌊 Release to Ocean")
        
        # Show menu and handle selection
        action = menu.exec(QCursor.pos())
        
        if action == toggle_action:
            self._toggle_pet(pet_id)
        elif action == release_action and release_action is not None:
            self._release_pet(pet_id)
    
    def _toggle_pet(self, pet_id: str):
        """Toggle pet between desktop and inventory."""
        if pet_id in self._active_pets:
            # Move from desktop to inventory
            self._active_pets.remove(pet_id)
            self._stored_pets.append(pet_id)
            self.pets_changed.emit(self._active_pets.copy())
        else:
            # Try to move from inventory to desktop
            if not self.can_add_to_desktop():
                QMessageBox.warning(
                    self,
                    "Limit Reached",
                    f"Desktop can show max {MAX_ACTIVE} pets!\nMove some pets to inventory first."
                )
                return
            
            self._stored_pets.remove(pet_id)
            self._active_pets.append(pet_id)
            self.pets_changed.emit(self._active_pets.copy())
        
        self._refresh_slots()
        self._update_status()
    
    def _release_pet(self, pet_id: str):
        """
        V10: Release a pet back to the ocean.
        V11: Bonus gacha when releasing at full inventory (20 pets).
        
        Cannot release the default pet 'puffer'.
        """
        if pet_id == 'puffer':
            QMessageBox.warning(
                self,
                "Cannot Release",
                "You cannot release your first companion!"
            )
            return
        
        # V11: Check if inventory is full before release (for bonus gacha)
        was_full = len(self._active_pets) + len(self._stored_pets) >= MAX_INVENTORY
        
        # Confirm release
        bonus_text = "\n\n🎁 Bonus: You'll get a free gacha roll!" if was_full else ""
        reply = QMessageBox.question(
            self,
            "Confirm Release",
            f"Are you sure you want to release {PET_NAMES.get(pet_id, pet_id)}?\nThis cannot be undone!{bonus_text}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove from lists
            if pet_id in self._active_pets:
                self._active_pets.remove(pet_id)
            if pet_id in self._stored_pets:
                self._stored_pets.remove(pet_id)
            
            # Remove from growth manager
            if self.growth_manager:
                self.growth_manager.release_pet(pet_id)
            
            self._refresh_slots()
            self._update_status()
            self.pets_changed.emit(self._active_pets.copy())
            
            QMessageBox.information(
                self,
                "Released",
                f"🌊 {PET_NAMES.get(pet_id, pet_id)} returned to the ocean..."
            )
            
            # V11: Trigger bonus gacha if inventory was full
            if was_full:
                self._trigger_bonus_gacha()
    
    def _trigger_bonus_gacha(self):
        """V11: Trigger bonus gacha when releasing pet at full inventory."""
        from ui_gacha import show_gacha, roll_gacha
        
        pet_id = roll_gacha()
        mode = "normal"
        if self.growth_manager:
            mode = self.growth_manager.get_theme_mode()
        
        # Store reference to prevent garbage collection
        self._gacha_overlay = show_gacha(pet_id, self._on_bonus_gacha_close, mode=mode)
    
    def _on_bonus_gacha_close(self, pet_id: str):
        """V11: Handle bonus gacha result."""
        if self.growth_manager:
            success = self.growth_manager.add_pet(pet_id)
            if success:
                # Refresh inventory display
                self._active_pets = self.growth_manager.get_active_pets()
                self._stored_pets = [p for p in self.growth_manager.get_unlocked_pets() 
                                    if p not in self._active_pets]
                self._refresh_slots()
                self._update_status()
                self.pets_changed.emit(self._active_pets.copy())
                
                QMessageBox.information(
                    self,
                    "Bonus Reward!",
                    f"🎉 You got a {PET_NAMES.get(pet_id, pet_id)} as a bonus!"
                )
    
    def _update_status(self):
        """Update status display."""
        total = len(self._active_pets) + len(self._stored_pets)
        active = len(self._active_pets)
        self.status_label.setText(f"[{total}/{MAX_INVENTORY}] Desktop:{active}/{MAX_ACTIVE}")
    
    # ========== Public API for capacity enforcement ==========
    
    def can_add_to_inventory(self) -> bool:
        """
        Check if a new pet can be added to inventory
        
        Requirements 4.5: MAX_INVENTORY = 20
        """
        total = len(self._active_pets) + len(self._stored_pets)
        return total < MAX_INVENTORY
    
    def can_add_to_desktop(self) -> bool:
        """
        Check if a pet can be added to desktop
        
        Requirements 4.7: MAX_ACTIVE = 5
        """
        return len(self._active_pets) < MAX_ACTIVE
    
    def get_active_pets(self) -> List[str]:
        """Get list of pets currently on desktop"""
        return self._active_pets.copy()
    
    def get_stored_pets(self) -> List[str]:
        """Get list of pets currently in inventory storage"""
        return self._stored_pets.copy()
    
    def get_total_pets(self) -> int:
        """Get total number of pets"""
        return len(self._active_pets) + len(self._stored_pets)
    
    def add_pet(self, pet_id: str, to_desktop: bool = True) -> bool:
        """
        Add a new pet to inventory
        
        Args:
            pet_id: Pet identifier
            to_desktop: If True, add to desktop; if False, add to storage
            
        Returns:
            True if added successfully, False if capacity exceeded
        """
        if not self.can_add_to_inventory():
            return False
        
        if to_desktop:
            if not self.can_add_to_desktop():
                # Desktop full, add to storage instead
                self._stored_pets.append(pet_id)
            else:
                self._active_pets.append(pet_id)
        else:
            self._stored_pets.append(pet_id)
        
        self._refresh_slots()
        self._update_status()
        self.pets_changed.emit(self._active_pets.copy())
        return True
    
    def remove_pet(self, pet_id: str) -> bool:
        """
        Remove a pet from inventory
        
        Args:
            pet_id: Pet identifier
            
        Returns:
            True if removed, False if not found
        """
        if pet_id in self._active_pets:
            self._active_pets.remove(pet_id)
            self._refresh_slots()
            self._update_status()
            self.pets_changed.emit(self._active_pets.copy())
            return True
        elif pet_id in self._stored_pets:
            self._stored_pets.remove(pet_id)
            self._refresh_slots()
            self._update_status()
            return True
        return False
    
    def toggle_pet_desktop(self, pet_id: str) -> bool:
        """
        Toggle a pet between desktop and storage
        
        Requirements 4.6: Toggle pet between active and stored state
        
        Args:
            pet_id: Pet identifier
            
        Returns:
            True if toggled successfully, False if operation failed
        """
        if pet_id in self._active_pets:
            # Move to storage
            self._active_pets.remove(pet_id)
            self._stored_pets.append(pet_id)
            self._refresh_slots()
            self._update_status()
            self.pets_changed.emit(self._active_pets.copy())
            return True
        elif pet_id in self._stored_pets:
            # Try to move to desktop
            if not self.can_add_to_desktop():
                return False
            self._stored_pets.remove(pet_id)
            self._active_pets.append(pet_id)
            self._refresh_slots()
            self._update_status()
            self.pets_changed.emit(self._active_pets.copy())
            return True
        return False
    
    def refresh_theme(self):
        """
        Refresh the window styling when theme changes
        
        Requirements 6.1, 6.2, 6.3: Update all styling for current theme
        """
        self._apply_pixel_font()
        self._refresh_slots()


# Backward compatibility alias
InventoryWindow = MCInventoryWindow
