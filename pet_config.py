"""
PufferPet V7 Configuration Module

Contains all V7-specific constants, mappings, and configuration values.
"""

# V7 Pet List - The 5 remaining pets
V7_PETS = ['puffer', 'jelly', 'crab', 'starfish', 'ray']

# Size Constants
BASE_SIZE = 100  # Base size in pixels
ADULT_MULTIPLIER = 1.5  # Adult stage size multiplier
RAY_MULTIPLIER = 1.5  # Ray species size multiplier (racial advantage)

# Shape Mappings (shape_type, color_hex)
# Used for geometric placeholder rendering when images are missing
PET_SHAPES = {
    'puffer': ('circle', '#90EE90'),      # Green circle
    'jelly': ('triangle', '#FFB6C1'),     # Pink triangle
    'crab': ('rectangle', '#FF6B6B'),     # Red rectangle
    'starfish': ('pentagon', '#FFD700'),  # Yellow pentagon
    'ray': ('diamond', '#4682B4'),        # Blue diamond
}

# Gacha Weights (probabilities sum to 100)
GACHA_WEIGHTS = {
    'puffer': 22,    # Common
    'jelly': 22,     # Common
    'crab': 22,      # Common
    'starfish': 22,  # Common
    'ray': 12,       # SSR (rare)
}

# Inventory Constants
MAX_INVENTORY = 20  # Maximum total pets in inventory
MAX_ACTIVE = 5      # Maximum pets displayed on desktop
GRID_COLUMNS = 2    # Inventory grid column count
