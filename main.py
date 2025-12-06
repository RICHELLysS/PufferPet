"""
main.py - PufferPet V8 Entry Point

🐡 PufferPet V8 - Hackathon Demo Edition 🐡
Core gameplay: Dormant-Revive-Growth + Inventory System + Gacha

Features:
- System tray menu
- Task window
- V8: Simplified day/night toggle (TimeManager auto-sync disabled, manual only)
- V7: 5 pets (puffer, jelly, crab, starfish, ray)
- V7: Geometric placeholder system
- V7: Size scaling rules (PetRenderer.calculate_size)
- V7: MC-style inventory UI

WARNING: The depths of the abyss await those who dare to run this code...
"""

import sys
import os


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and PyInstaller.
    
    When running as a PyInstaller bundle, sys._MEIPASS contains
    the path to the temporary folder where assets are extracted.
    
    Args:
        relative_path: Path relative to project root (e.g., "assets/puffer/swim/puffer_swim_0.png")
        
    Returns:
        Absolute path to the resource
        
    WARNING: The spirits guide the path through frozen darkness...
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - the abyss is frozen
        base_path = sys._MEIPASS
    else:
        # Running in development - the waters flow freely
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)
import json
import random
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QDialog, 
    QVBoxLayout, QLabel, QCheckBox, QPushButton, QWidget, QMessageBox
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction
from PyQt6.QtCore import Qt, QTimer

from logic_growth import GrowthManager
from pet_core import PetWidget, PetRenderer
from ui_inventory import InventoryWindow
from ui_gacha import show_gacha, roll_gacha
from time_manager import TimeManager
from theme_manager import ThemeManager
from ui_style import get_stylesheet
from pet_config import V7_PETS


# ========== Settings Menu Helper Functions ==========

def create_settings_menu(app, time_manager, theme_manager):
    """
    V8: Create simplified settings menu - only manual day/night toggle.
    
    Args:
        app: QApplication instance
        time_manager: TimeManager instance (can be None)
        theme_manager: ThemeManager instance
        
    Returns:
        QMenu: Settings menu
        
    Requirements: 1.2, 1.5
    WARNING: The settings control the very fabric of day and night...
    """
    menu = QMenu("⚙️ Settings")
    
    if time_manager is None:
        return menu
    
    # V8: Only manual day/night toggle (Auto Day/Night checkbox removed)
    toggle_action = QAction("🌓 Toggle Day/Night", menu)
    toggle_action.triggered.connect(
        lambda: on_toggle_day_night(time_manager)
    )
    menu.addAction(toggle_action)
    
    # Store reference for later access
    menu.toggle_day_night_action = toggle_action
    
    # Apply theme
    if theme_manager and theme_manager.is_halloween_mode():
        menu.setStyleSheet(theme_manager.get_dark_stylesheet())
    
    return menu


def on_toggle_day_night(time_manager):
    """
    V8: Manually toggle day/night mode (always available since auto_sync is disabled).
    
    Args:
        time_manager: TimeManager instance
        
    Requirements: 1.2
    WARNING: Mortals dare to control the cycle of day and night...
    """
    # V8: Direct toggle, no auto_sync check (always disabled in V8)
    if time_manager.get_current_period() == "day":
        time_manager.switch_to_night()
    else:
        time_manager.switch_to_day()


class TaskWindow(QDialog):
    """Simplified task window - Retro Minesweeper Style (Requirements: 5.1, 5.4)
    
    WARNING: Complete these rituals to awaken the creatures of the deep...
    """
    
    # V16: Default tasks for most pets (3 tasks)
    TASKS = [
        "💧 Drink water",
        "🧘 Stretch",
        "⏱️ Focus 30min"
    ]
    
    # V16: Ray (SSR) requires 5 tasks
    RAY_TASKS = [
        "💧 Drink water",
        "🧘 Stretch",
        "⏱️ Focus 30min",
        "🚶 Take a walk",
        "📖 Read 10 pages"
    ]
    
    def __init__(self, pet_id: str, growth_manager: GrowthManager, pet_widget: PetWidget, 
                 on_pet_added: callable = None, parent=None):
        super().__init__(parent)
        self.pet_id = pet_id
        self.growth_manager = growth_manager
        self.pet_widget = pet_widget
        self.checkboxes = []
        self._on_pet_added = on_pet_added  # V15: Callback to refresh pet widgets
        
        self._setup_ui()
        self._load_state()
    
    def _setup_ui(self):
        """Setup UI - Retro Minesweeper Style (Requirements: 5.1, 5.4)"""
        self.setWindowTitle(f"📋 Tasks - {self.pet_id}")
        # V16: Larger window for Ray (5 tasks)
        window_height = 380 if self.pet_id == 'ray' else 300
        self.setFixedSize(320, window_height)
        
        # Apply global retro stylesheet from ui_style (Requirements: 5.1, 5.4)
        mode = self.growth_manager.get_theme_mode()
        self.setStyleSheet(get_stylesheet(mode))
        
        # Get palette for theme-appropriate colors (Requirements: 5.1)
        from ui_style import get_palette
        palette = get_palette(mode)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Progress label - Theme-appropriate title styling (Requirements: 5.1)
        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Use theme accent color for title
        self.progress_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {palette['accent']};")
        layout.addWidget(self.progress_label)
        
        # 3D Sunken Frame for task list (Requirements: 5.1)
        from PyQt6.QtWidgets import QFrame
        task_frame = QFrame()
        task_frame.setFrameShape(QFrame.Shape.StyledPanel)
        task_frame.setFrameShadow(QFrame.Shadow.Sunken)
        # Apply 3D sunken border effect
        task_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {palette['bg']};
                border-top: 2px solid {palette['button_dark']};
                border-left: 2px solid {palette['button_dark']};
                border-bottom: 2px solid {palette['button_light']};
                border-right: 2px solid {palette['button_light']};
                border-radius: 0px;
                padding: 4px;
            }}
        """)
        task_layout = QVBoxLayout(task_frame)
        task_layout.setSpacing(4)
        task_layout.setContentsMargins(8, 8, 8, 8)
        
        # V16: Use RAY_TASKS for ray, TASKS for others
        tasks = self.RAY_TASKS if self.pet_id == 'ray' else self.TASKS
        
        # Task checkboxes - inside 3D sunken frame
        for task in tasks:
            cb = QCheckBox(task)
            cb.stateChanged.connect(self._on_task_changed)
            self.checkboxes.append(cb)
            task_layout.addWidget(cb)
        
        layout.addWidget(task_frame)
        
        # Status label - Theme-appropriate styling (Requirements: 5.1)
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Use theme foreground color
        self.status_label.setStyleSheet(f"color: {palette['fg']}; margin-top: 5px; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Close button - Uses global 3D raised button style (Requirements: 5.4)
        close_btn = QPushButton("✓ Done")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self._update_display()
    
    def _load_state(self):
        """Load task state from growth manager."""
        progress = self.growth_manager.get_progress(self.pet_id)
        # Check boxes based on progress
        for i, cb in enumerate(self.checkboxes):
            cb.blockSignals(True)
            cb.setChecked(i < progress)
            cb.blockSignals(False)
    
    def _on_task_changed(self, state):
        """Handle task checkbox state change."""
        # Count currently checked boxes
        checked_count = sum(1 for cb in self.checkboxes if cb.isChecked())
        current_progress = self.growth_manager.get_progress(self.pet_id)
        
        # If checked count increased, complete task
        if checked_count > current_progress:
            old_state = self.growth_manager.get_state(self.pet_id)
            new_state = self.growth_manager.complete_task(self.pet_id)
            
            # V16: Debug output for state transition
            print(f"[TaskWindow] {self.pet_id}: old_state={old_state}, new_state={new_state}, progress={self.growth_manager.get_progress(self.pet_id)}")
            
            self.pet_widget.refresh_display()
            
            # V7.1: Increment cumulative task count
            self.growth_manager.increment_cumulative_tasks()
            
            # V16: When pet evolves from baby to adult, trigger gacha
            if old_state == 1 and new_state == 2:
                print(f"[TaskWindow] Triggering gacha for {self.pet_id} (Baby -> Adult)")
                self._trigger_gacha_on_adult()
            # V6.1: Every 12 tasks also triggers reward
            elif self.growth_manager.check_reward():
                self._trigger_reward()
        
        self._update_display()
    
    def _trigger_gacha_on_adult(self):
        """V7.1: Trigger gacha when pet reaches adult stage."""
        if not self.growth_manager.can_add_pet():
            QMessageBox.information(
                self, "Inventory Full",
                "🐟 The tank is full! Release some pets first."
            )
            return
        
        # V16: Close task window before showing gacha
        self.close()
        
        # Show gacha animation
        pet_id = roll_gacha()
        mode = self.growth_manager.get_theme_mode()
        self.gacha_overlay = show_gacha(pet_id, self._on_gacha_close, mode=mode)
    
    def _trigger_reward(self):
        """V6.1: Trigger reward gacha."""
        self.growth_manager.reset_cumulative_tasks()
        
        if not self.growth_manager.can_add_pet():
            QMessageBox.information(
                self, "Inventory Full",
                "🐟 The tank is full! Release some pets first."
            )
            return
        
        # V16: Close task window before showing gacha
        self.close()
        
        # Show gacha animation
        pet_id = roll_gacha()
        mode = self.growth_manager.get_theme_mode()
        self.gacha_overlay = show_gacha(pet_id, self._on_gacha_close, mode=mode)
    
    def _on_gacha_close(self, pet_id: str):
        """V15: Gacha close callback - add pet as Baby and show on screen immediately."""
        self.growth_manager.add_pet(pet_id)  # V15: add_pet now sets Baby state by default
        # V15: Refresh pet widgets to show new pet on screen immediately
        if self._on_pet_added:
            self._on_pet_added()
        QMessageBox.information(
            self, "Congratulations!",
            f"🎉 You got a new {pet_id}!\nNow swimming on your screen!"
        )
    
    def _update_display(self):
        """V16: Update progress and status display based on pet type."""
        progress = self.growth_manager.get_progress(self.pet_id)
        state = self.growth_manager.get_state(self.pet_id)
        
        # V16: Ray needs 5 tasks, others need 3
        total_tasks = 5 if self.pet_id == 'ray' else 3
        self.progress_label.setText(f"Progress: {progress}/{total_tasks}")
        
        state_names = {0: "💤 Dormant", 1: "🐣 Baby", 2: "🐟 Adult"}
        self.status_label.setText(state_names.get(state, "???"))


class PufferPetApp:
    """V7 Main Application - Uses V7_PETS and PetRenderer.
    
    WARNING: The main vessel that summons creatures from the deep...
    """
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # V12: Set application icon using puffer_default_icon
        icon_path = resource_path("assets/puffer/puffer_default_icon.png")
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.app.setWindowIcon(app_icon)
            print(f"[PufferPetApp] App icon loaded: {icon_path}")
        else:
            print(f"[PufferPetApp] App icon not found: {icon_path}")
        
        # V7.1: Ensure data.json exists with default dormant puffer
        # Requirements: 10.1
        self._ensure_data_file_exists()
        
        # Initialize managers
        self.growth_manager = GrowthManager(resource_path("data.json"))
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # Apply global pixel-art stylesheet on startup
        self._apply_global_style()
        
        # Initialize time manager (day/night mode)
        self.time_manager = TimeManager(theme_manager=self.theme_manager)
        self.time_manager.mode_changed.connect(self._on_day_night_changed)
        
        # Create pet windows
        self.pet_widgets = {}
        self._create_pets()
        
        # Create system tray
        self._create_tray()
        
        # Start time manager (day/night auto-sync)
        self._setup_day_night_mode()
        
        # V6.1: Encounter system timer
        self._setup_encounter_timer()
    
    def _ensure_data_file_exists(self):
        """
        V7.1: Ensure data.json exists with default dormant puffer.
        
        If data.json does not exist, creates it with:
        - One pet (puffer) in dormant state (0)
        - Default settings
        
        Requirements: 10.1
        WARNING: The ancient records must exist for the creatures to persist...
        """
        data_file = resource_path("data.json")
        
        if not os.path.exists(data_file):
            print(f"[PufferPetApp] data.json not found, creating default data file")
            
            default_data = {
                "pets": {
                    "puffer": {
                        "state": 0,  # Dormant state
                        "tasks_progress": 0
                    }
                },
                "settings": {
                    "auto_time_sync": True,
                    "theme_mode": "normal"
                },
                "unlocked_pets": ["puffer"],
                "active_pets": ["puffer"],
                "cumulative_tasks": 0,
                "custom_task_texts": []
            }
            
            try:
                with open(data_file, 'w', encoding='utf-8') as f:
                    json.dump(default_data, f, indent=2, ensure_ascii=False)
                print(f"[PufferPetApp] Created default data.json with dormant puffer")
            except IOError as e:
                print(f"[PufferPetApp] Failed to create data.json: {e}")
    
    def _create_pets(self):
        """Create pet windows for all active pets."""
        # V6.1: Only create windows for active pets
        active_pets = self.growth_manager.get_active_pets()
        
        for pet_id in active_pets:
            self._create_pet_widget(pet_id)
        
        # If no pets, create default puffer
        if not self.pet_widgets:
            self._create_pet_widget("puffer")
    
    def _create_pet_widget(self, pet_id: str):
        """Create a single pet window."""
        if pet_id in self.pet_widgets:
            return
        
        widget = PetWidget(pet_id, self.growth_manager)
        widget.task_window_requested.connect(
            lambda pid=pet_id: self._show_task_window(pid)
        )
        widget.inventory_requested.connect(self._show_inventory)
        widget.release_requested.connect(self._release_pet)
        widget.show()
        self.pet_widgets[pet_id] = widget
    
    def _create_tray(self):
        """Create system tray icon and menu."""
        self.tray = QSystemTrayIcon(self.app)
        
        # Create icon
        icon = self._create_tray_icon()
        self.tray.setIcon(icon)
        
        # Create menu
        menu = QMenu()
        
        # Tasks window
        task_action = menu.addAction("📋 Tasks")
        task_action.triggered.connect(lambda: self._show_task_window("puffer"))
        
        # V6.1: Inventory
        inventory_action = menu.addAction("🎒 Inventory")
        inventory_action.triggered.connect(self._show_inventory)
        
        menu.addSeparator()
        
        # Settings submenu (day/night mode)
        self.settings_menu = create_settings_menu(
            self.app, self.time_manager, self.theme_manager
        )
        menu.addMenu(self.settings_menu)
        
        menu.addSeparator()
        
        # V6.1: Test gacha (debug)
        gacha_action = menu.addAction("🎁 Test Gacha")
        gacha_action.triggered.connect(self._test_gacha)
        
        # Reset
        reset_action = menu.addAction("🔄 Reset All")
        reset_action.triggered.connect(self._reset_all)
        
        menu.addSeparator()
        
        # Quit
        quit_action = menu.addAction("❌ Quit")
        quit_action.triggered.connect(self._quit)
        
        self.tray.setContextMenu(menu)
        self.tray.show()
    
    def _create_tray_icon(self) -> QIcon:
        """Create tray icon - a simple orange circle."""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor('#FFB347'))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 24, 24)
        painter.end()
        
        return QIcon(pixmap)
    
    def _apply_global_style(self):
        """Apply global pixel-art stylesheet based on current theme mode."""
        mode = self.growth_manager.get_theme_mode()
        stylesheet = get_stylesheet(mode)
        self.app.setStyleSheet(stylesheet)
    
    def _show_task_window(self, pet_id: str):
        """Show task window for the specified pet."""
        if pet_id in self.pet_widgets:
            dialog = TaskWindow(
                pet_id, 
                self.growth_manager, 
                self.pet_widgets[pet_id],
                on_pet_added=self._refresh_pet_widgets  # V15: Pass refresh callback
            )
            dialog.exec()
    
    def _setup_day_night_mode(self):
        """
        V8: Setup day/night mode - disable auto-sync, default to Day Mode.
        
        Requirements: 1.1, 1.4
        WARNING: The cycle of day and night is now under mortal control...
        """
        # V8: Disable TimeManager auto-sync
        self.time_manager.set_auto_sync(False)
        
        # V8: Ensure default theme is "normal" (Day Mode)
        self.growth_manager.set_theme_mode("normal")
        self.time_manager.switch_to_day()
        
        # Start time manager (manual toggle only, no auto-sync)
        self.time_manager.start()
        
        print(f"[App] V8: Day/night mode started, auto-sync disabled, default Day Mode")
    
    def _on_day_night_changed(self, mode: str):
        """
        V8: Day/night mode change callback - update theme and refresh all UI.
        
        Args:
            mode: New mode ("day" or "night")
            
        Requirements: 1.2, 1.3
        """
        # Sync to GrowthManager
        theme_mode = "normal" if mode == "day" else "halloween"
        self.growth_manager.set_theme_mode(theme_mode)
        
        # V8: Refresh global stylesheet to apply new theme colors
        self._apply_global_style()
        
        # V8: Refresh all pet widgets to update their appearance
        for pet_widget in self.pet_widgets.values():
            pet_widget.refresh_display()
        
        print(f"[App] V8: Day/night mode changed: {mode} (theme: {theme_mode})")
    
    def _reset_all(self):
        """Reset all pets to dormant state."""
        for pet_id in self.pet_widgets:
            self.growth_manager.reset_cycle(pet_id)
            self.pet_widgets[pet_id].refresh_display()
    
    def _quit(self):
        """Quit the application gracefully."""
        # Stop time manager
        if hasattr(self, 'time_manager'):
            self.time_manager.stop()
        
        self.growth_manager.save()
        self.app.quit()
    
    # ========== V6.1 New Features ==========
    
    def _show_inventory(self):
        """Show inventory window."""
        dialog = InventoryWindow(self.growth_manager)
        dialog.pets_changed.connect(self._on_active_pets_changed)
        dialog.exec()
    
    def _on_active_pets_changed(self, active_pets: list):
        """Handle active pets list change."""
        self.growth_manager.set_active_pets(active_pets)
        self._refresh_pet_widgets()
    
    def _refresh_pet_widgets(self):
        """Refresh pet windows based on active pets list."""
        active_pets = self.growth_manager.get_active_pets()
        
        # Close windows for pets no longer active
        for pet_id in list(self.pet_widgets.keys()):
            if pet_id not in active_pets:
                self.pet_widgets[pet_id].close()
                del self.pet_widgets[pet_id]
        
        # Create windows for newly active pets
        for pet_id in active_pets:
            if pet_id not in self.pet_widgets:
                self._create_pet_widget(pet_id)
    
    def _release_pet(self, pet_id: str):
        """Release a pet back to the ocean."""
        reply = QMessageBox.question(
            None, "Confirm Release",
            f"Are you sure you want to release {pet_id}?\nThis cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.growth_manager.release_pet(pet_id):
                if pet_id in self.pet_widgets:
                    self.pet_widgets[pet_id].close()
                    del self.pet_widgets[pet_id]
                QMessageBox.information(None, "Released", f"🌊 {pet_id} returned to the ocean...")
    
    def _test_gacha(self):
        """Test gacha (debug feature)."""
        if not self.growth_manager.can_add_pet():
            QMessageBox.warning(None, "Inventory Full", "🐟 The tank is full! Release some pets first.")
            return
        
        pet_id = roll_gacha()
        mode = self.growth_manager.get_theme_mode()
        self.gacha_overlay = show_gacha(pet_id, self._on_gacha_complete, mode=mode)
    
    def _on_gacha_complete(self, pet_id: str):
        """V14: Gacha complete callback - add pet and show on screen immediately."""
        self.growth_manager.add_pet(pet_id)
        # V14: Ensure new pet is in active_pets so it shows on screen
        active_pets = self.growth_manager.get_active_pets()
        if pet_id not in active_pets and len(active_pets) < 5:
            active_pets.append(pet_id)
            self.growth_manager.set_active_pets(active_pets)
        self._refresh_pet_widgets()
    
    def _setup_encounter_timer(self):
        """V6.1: Setup encounter system timer."""
        self.encounter_timer = QTimer()
        self.encounter_timer.timeout.connect(self._check_encounter)
        self.encounter_timer.start(300000)  # Check every 5 minutes
    
    def _check_encounter(self):
        """Check for random encounter - V7: Uses V7_PETS."""
        # 30% chance to trigger
        if random.random() < 0.3:
            # V7: Use V7_PETS list instead of old tier2_pets
            available = [p for p in V7_PETS if p not in self.growth_manager.get_unlocked_pets()]
            
            if available and self.growth_manager.can_add_pet():
                pet_id = random.choice(available)
                reply = QMessageBox.question(
                    None, "🌊 Encounter!",
                    f"You found a wild {pet_id}!\nDo you want to catch it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.growth_manager.add_pet(pet_id)
                    self._refresh_pet_widgets()
                    QMessageBox.information(None, "Caught!", f"🎉 {pet_id} joined your team!")
    
    def run(self) -> int:
        """Run the application event loop."""
        return self.app.exec()


def main():
    """Application entry point.
    
    WARNING: The gateway to the abyss opens here...
    """
    print("=" * 50)
    print("  PufferPet V8 - Hackathon Edition")
    print("  5 Pets + Geometric Placeholders + Size Scaling")
    print("=" * 50)
    
    app = PufferPetApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
