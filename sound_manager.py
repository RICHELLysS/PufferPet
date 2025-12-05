"""
Sound Manager Module - V7.1 System Audit

Provides audio feedback using QApplication.beep() as temporary sound effects.
This module implements a singleton pattern for global access to sound functionality.

Requirements: 4.3, 6.5, 10.3
"""

from PyQt6.QtWidgets import QApplication


class SoundManager:
    """
    Sound manager class that provides audio feedback for various game events.
    Uses QApplication.beep() for all sounds as a temporary solution.
    """
    
    def __init__(self):
        """Initialize the sound manager with sounds enabled by default."""
        self.enabled = True
    
    def play_task_complete(self) -> None:
        """
        Play sound when a task is completed.
        Requirements: 4.3
        """
        if self.enabled:
            QApplication.beep()
    
    def play_gacha_open(self) -> None:
        """
        Play sound when opening a gacha box.
        Uses double beep for emphasis.
        Requirements: 6.5
        """
        if self.enabled:
            QApplication.beep()
            QApplication.beep()  # Double beep for gacha
    
    def play_pet_upgrade(self) -> None:
        """
        Play sound when a pet upgrades to a new stage.
        Requirements: 10.3
        """
        if self.enabled:
            QApplication.beep()
    
    def play_pet_angry(self) -> None:
        """
        Play sound when a pet becomes angry.
        Requirements: 10.3
        """
        if self.enabled:
            QApplication.beep()


# Global singleton instance
_sound_manager = None


def get_sound_manager() -> SoundManager:
    """
    Get the global SoundManager instance (singleton pattern).
    
    Returns:
        SoundManager: The global sound manager instance.
    
    Requirements: 10.3
    """
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager
