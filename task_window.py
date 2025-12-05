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
        
        # Get custom task texts (from GrowthManager or use defaults)
        task_texts = self._load_task_texts()
        
        # Get current pet's task state
        # V7.1: Use pet_widget.pet_id instead of data_manager.get_current_pet_id()
        current_pet = self.pet_widget.pet_id
        
        # Get task states (default to [False, False, False])
        # V7.1: Simplified data structure, no longer using pets_data nesting
        task_states = [False, False, False]
        
        # Create three task rows (checkbox + editable text)
        for i, task_text in enumerate(task_texts):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            # Checkbox (no text)
            checkbox = QCheckBox()
            checkbox.setChecked(task_states[i])
            checkbox.stateChanged.connect(lambda state, idx=i: self.on_checkbox_changed(state, idx))
            self.checkboxes.append(checkbox)
            
            # Editable text
            line_edit = QLineEdit(task_text)
            line_edit.textChanged.connect(lambda text, idx=i: self._on_task_text_changed(idx, text))
            self.line_edits.append(line_edit)
            
            row_layout.addWidget(checkbox)
            row_layout.addWidget(line_edit, 1)  # stretch factor 1 to fill space
            layout.addWidget(row_widget)
        
        self.setLayout(layout)
    
    def _load_task_texts(self) -> List[str]:
        """
        Load custom task texts.
        
        Returns:
            Task text list, returns defaults if no saved texts
        """
        if self.growth_manager is not None:
            texts = self.growth_manager.get_custom_task_texts()
            if texts:
                return texts
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
        """Update progress display."""
        # V7.1: Use growth_manager.get_progress(pet_id) to get task progress
        current_pet = self.pet_widget.pet_id
        if self.growth_manager is not None:
            tasks_completed = self.growth_manager.get_progress(current_pet)
        else:
            tasks_completed = 0
        progress_text = f"{tasks_completed}/3"
        self.progress_label.setText(progress_text)
    
    def on_checkbox_changed(self, state: int, index: int) -> None:
        """Handle checkbox state change.
        
        Args:
            state: Checkbox state
            index: Checkbox index
        
        Requirements: 4.3 - Play sound on task completion
        """
        is_checked = (state == Qt.CheckState.Checked.value)
        
        # Update task state
        # V7.1: Use pet_widget.pet_id instead of data_manager.get_current_pet_id()
        current_pet = self.pet_widget.pet_id
        
        # Update task completion count
        if is_checked:
            # Play task completion sound (Requirements 4.3)
            from sound_manager import get_sound_manager
            get_sound_manager().play_task_complete()
            
            # V7.1: Use growth_manager.complete_task(pet_id) to complete task
            if self.growth_manager is not None:
                self.growth_manager.complete_task(current_pet)
        # Note: V7.1 does not support task cancellation (decrement), tasks are irreversible
        
        # Update progress display
        self.update_progress()
        
        # Update main window display
        self.pet_widget.update_display()
    
    def closeEvent(self, event) -> None:
        """Save data and close.
        
        Args:
            event: Close event
        """
        # V7.1: Use growth_manager.save() to save data
        if self.growth_manager is not None:
            self.growth_manager.save()
        event.accept()
