"""
🦑 Deep Sea Undead Empire - Task Window Component

WARNING: This module governs the daily task rituals of deep sea creatures...

This module manages:
- Task list: Display three editable daily tasks
- Progress tracking: Show current completion progress
- Evolution trigger: Complete tasks to trigger creature evolution
- Reward system: Cumulative tasks trigger deep sea rewards
- Sound feedback: Play sound on task completion

⚠️ WARNING: Completing tasks is the key ritual for nurturing deep sea creatures!
Every 12 tasks completed, the abyss shall grant you mysterious rewards...

Author: Deep Sea Code Captain
Version: 7.1 (System Audit Edition)
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QLineEdit, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from data_manager import DataManager
from typing import TYPE_CHECKING, Optional, List

# V7.1: Import pixel-art styling (Requirements: 9.1)
from ui_style import get_stylesheet

if TYPE_CHECKING:
    from pet_core import PetWidget


# Default task texts
DEFAULT_TASK_TEXTS = ["Drink water", "Stretch", "Focus 30min"]

# V14: Ray (SSR) requires 5 tasks to reach adult
RAY_TASK_TEXTS = ["Drink water", "Stretch", "Focus 30min", "Take a walk", "Read 10 pages"]


class TaskWindow(QDialog):
    """
    📋 Deep Sea Task Ritual Window
    
    WARNING: This window is the sacred place to connect with deep sea creatures...
    By completing daily tasks, you help creatures grow and evolve.
    
    V7.1 Updates:
    - Editable task text
    - Sound on task completion
    - Custom task text persistence
    """
    
    def __init__(self, data_manager: DataManager, pet_widget: 'PetWidget', growth_manager=None):
        """
        🌊 Initialize task ritual window.
        
        This ritual establishes the task connection with deep sea creatures.
        
        Args:
            data_manager: Abyss data guardian
            pet_widget: Creature display window reference
            growth_manager: Growth manager (optional, for saving custom task texts)
        """
        super().__init__()
        self.data_manager = data_manager
        self.pet_widget = pet_widget
        self.growth_manager = growth_manager
        self.checkboxes: List[QCheckBox] = []
        self.line_edits: List[QLineEdit] = []
        self.progress_label = None
        
        self.setup_ui()
        self.update_progress()
    
    def setup_ui(self) -> None:
        """Create UI elements."""
        self.setWindowTitle("Daily Tasks")
        
        # V7.1: Apply pixel-art QSS styling (Requirements: 9.1)
        # Get theme mode from growth_manager if available
        mode = "normal"
        if self.growth_manager is not None:
            mode = self.growth_manager.get_theme_mode()
        self.setStyleSheet(get_stylesheet(mode))
        
        layout = QVBoxLayout()
        
        # Create progress label
        self.progress_label = QLabel()
        layout.addWidget(self.progress_label)
        
        # V14: Get current pet ID first
        current_pet = self.pet_widget.pet_id
        
        # V14: Get task texts based on pet type (Ray needs 5 tasks)
        task_texts = self._load_task_texts(current_pet)
        
        # V10: Load current progress to show completed tasks
        tasks_completed = 0
        if self.growth_manager is not None:
            tasks_completed = self.growth_manager.get_progress(current_pet)
        
        # Create three task rows (checkbox + editable text)
        for i, task_text in enumerate(task_texts):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            # V11: Check if task is completed
            is_completed = i < tasks_completed
            
            # Checkbox (no text) or blue square for completed
            checkbox = QCheckBox()
            checkbox.setChecked(is_completed)
            if is_completed:
                # V11: Blue square for completed tasks
                checkbox.setStyleSheet("""
                    QCheckBox::indicator {
                        width: 20px;
                        height: 20px;
                        background-color: #4169E1;
                        border: 2px solid #2F4F8F;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #4169E1;
                        border: 2px solid #2F4F8F;
                    }
                """)
                checkbox.setEnabled(False)  # Cannot uncheck completed tasks
            checkbox.stateChanged.connect(lambda state, idx=i: self.on_checkbox_changed(state, idx))
            self.checkboxes.append(checkbox)
            
            # Editable text (disabled for completed tasks)
            line_edit = QLineEdit(task_text)
            if is_completed:
                line_edit.setReadOnly(True)  # V11: Cannot edit completed tasks
                line_edit.setStyleSheet("color: #666666; background-color: #E0E0E0;")
            else:
                line_edit.textChanged.connect(lambda text, idx=i: self._on_task_text_changed(idx, text))
            self.line_edits.append(line_edit)
            
            row_layout.addWidget(checkbox)
            row_layout.addWidget(line_edit, 1)  # stretch factor 1 to fill space
            layout.addWidget(row_widget)
        
        self.setLayout(layout)
    
    def _load_task_texts(self, pet_id: str = None) -> List[str]:
        """
        V14: Load task texts based on pet type.
        
        Ray (SSR) requires 5 tasks, other pets require 3 tasks.
        
        Args:
            pet_id: Pet ID to determine task count
            
        Returns:
            Task text list
        """
        # V14: Ray needs 5 tasks
        if pet_id == 'ray':
            if self.growth_manager is not None:
                texts = self.growth_manager.get_custom_task_texts()
                if texts and len(texts) >= 5:
                    return texts[:5]
            return RAY_TASK_TEXTS.copy()
        
        # Other pets need 3 tasks
        if self.growth_manager is not None:
            texts = self.growth_manager.get_custom_task_texts()
            if texts:
                return texts[:3]
        return DEFAULT_TASK_TEXTS.copy()
    
    def _on_task_text_changed(self, index: int, new_text: str) -> None:
        """
        Save when task text changes.
        
        Args:
            index: Task index
            new_text: New task text
        
        Requirements: 4.2
        """
        # Don't save empty text
        if not new_text.strip():
            return
        
        # Collect all current task texts
        current_texts = [le.text() for le in self.line_edits]
        
        # Save to GrowthManager
        if self.growth_manager is not None:
            self.growth_manager.set_custom_task_texts(current_texts)
    
    def update_progress(self) -> None:
        """V14: Update progress display based on pet type."""
        current_pet = self.pet_widget.pet_id
        if self.growth_manager is not None:
            tasks_completed = self.growth_manager.get_progress(current_pet)
        else:
            tasks_completed = 0
        
        # V14: Ray needs 5 tasks, others need 3
        total_tasks = 5 if current_pet == 'ray' else 3
        progress_text = f"{tasks_completed}/{total_tasks}"
        self.progress_label.setText(progress_text)
    
    def on_checkbox_changed(self, state: int, index: int) -> None:
        """Handle checkbox state change.
        
        Args:
            state: Checkbox state
            index: Checkbox index
        
        Requirements: 4.3 - Play sound on task completion
        
        V8: Trigger blind box when pet evolves to adult
        - Track state before and after task completion
        - If state changes from 1 (baby) to 2 (adult), trigger gacha
        
        V10: Tasks cannot be unchecked once completed (irreversible)
        """
        is_checked = (state == Qt.CheckState.Checked.value)
        
        # V10: Prevent unchecking - tasks are irreversible
        if not is_checked:
            # Get current progress
            current_pet = self.pet_widget.pet_id
            if self.growth_manager is not None:
                tasks_completed = self.growth_manager.get_progress(current_pet)
                # If this checkbox was already completed, re-check it
                if index < tasks_completed:
                    self.checkboxes[index].blockSignals(True)
                    self.checkboxes[index].setChecked(True)
                    self.checkboxes[index].blockSignals(False)
            return
        
        # Update task state
        # V7.1: Use pet_widget.pet_id instead of data_manager.get_current_pet_id()
        current_pet = self.pet_widget.pet_id
        
        # Play task completion sound (Requirements 4.3)
        from sound_manager import get_sound_manager
        get_sound_manager().play_task_complete()
        
        # V8: Track state before task completion for gacha trigger
        old_state = None
        if self.growth_manager is not None:
            old_state = self.growth_manager.get_state(current_pet)
        
        # V7.1: Use growth_manager.complete_task(pet_id) to complete task
        if self.growth_manager is not None:
            new_state = self.growth_manager.complete_task(current_pet)
            
            # V8: Trigger blind box when pet evolves to adult (state 1 -> 2)
            if old_state == 1 and new_state == 2:
                self._trigger_gacha_on_adult()
        
        # Update progress display
        self.update_progress()
        
        # Update main window display
        self.pet_widget.update_display()
        
        # V11: Apply blue square style and disable checkbox after completion
        self.checkboxes[index].setStyleSheet("""
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                background-color: #4169E1;
                border: 2px solid #2F4F8F;
            }
            QCheckBox::indicator:checked {
                background-color: #4169E1;
                border: 2px solid #2F4F8F;
            }
        """)
        self.checkboxes[index].setEnabled(False)
        
        # V11: Disable editing for completed task
        self.line_edits[index].setReadOnly(True)
        self.line_edits[index].setStyleSheet("color: #666666; background-color: #E0E0E0;")
    
    def _trigger_gacha_on_adult(self) -> None:
        """
        Trigger blind box when pet reaches adult stage.
        Opens the gacha system to reward the player with a new pet.
        """
        if self.growth_manager is None:
            return
            
        # Check if inventory is full (20 pets max)
        if not self.growth_manager.can_add_pet():
            QMessageBox.warning(
                self, "Inventory Full",
                "You have reached the maximum number of pets. Please clean up your inventory!"
            )
            return
        
        # Show gacha animation
        from ui_gacha import show_gacha, roll_gacha
        pet_id = roll_gacha()
        mode = self.growth_manager.get_theme_mode()
        self.gacha_overlay = show_gacha(pet_id, self._on_gacha_close, mode=mode)
    
    def _on_gacha_close(self, pet_id: str) -> None:
        """
        V14: Gacha close callback - add pet and show on screen immediately.
        
        Args:
            pet_id: The pet ID obtained from gacha
        """
        if self.growth_manager is not None:
            # V14: Add pet to inventory and ensure it's active (shows on screen)
            success = self.growth_manager.add_pet(pet_id)
            if success:
                # V14: Ensure new pet is in active_pets so it shows on screen
                active_pets = self.growth_manager.get_active_pets()
                if pet_id not in active_pets and len(active_pets) < 5:
                    active_pets.append(pet_id)
                    self.growth_manager.set_active_pets(active_pets)
                
                print(f"🎁 Added {pet_id} to screen!")
                QMessageBox.information(
                    self, "Congratulations!",
                    f"🎉 You got a {pet_id}!\n\n🐟 Now swimming on your screen!"
                )
            else:
                QMessageBox.warning(
                    self, "Inventory Full",
                    "Your inventory is full! Release some pets first."
                )
    
    def closeEvent(self, event) -> None:
        """Save data and close.
        
        Args:
            event: Close event
        """
        # V7.1: Use growth_manager.save() to save data
        if self.growth_manager is not None:
            self.growth_manager.save()
        event.accept()
