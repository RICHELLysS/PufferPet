# 🎃 PufferPet Kiroween Hackathon Demo Script

> *"Welcome to the Deep Sea Undead Empire..."* — Deep Sea Code Captain 🦑

## Demo Overview

**Duration**: 5-10 minutes
**Goal**: Showcase Kiro native features (Steering, Agent Hooks) and Halloween creative features

---

## 🎬 Demo Flow

### Act 1: Setting Sail into the Deep (1-2 minutes)

#### 1.1 Project Introduction

```
"PufferPet is a desktop pet application where cute marine creatures accompany your work.
V4 is built for Kiroween Hackathon, incorporating the Deep Sea Undead Empire Halloween theme."
```

#### 1.2 Launch Application

```bash
python main.py
```

**Key Points**:
- 🎃 Halloween dark theme auto-applies
- 👻 Pet ghost filter effect
- 🌑 Deep purple-black background + ghost green text

---

### Act 2: Kiro Steering Showcase (2-3 minutes)

#### 2.1 Open Steering File

```
File location: .kiro/steering.md
```

**Key Points**:
- 🦑 Deep Sea Code Captain role definition
- 📜 Defensive programming rules
- 💀 Dramatic comment style

#### 2.2 Code Style Examples

Open `theme_manager.py` or `ignore_tracker.py`, show:

```python
# ⚠️ WARNING: Data corruption curse lurks here...
# Any soul attempting to bypass this validation will be swallowed by the abyss
```

```python
def summon_leviathan(pet_id: str) -> bool:
    """
    🐋 Summon a leviathan from the abyss to the screen.
    
    This ritual awakens creatures sleeping deep in inventory,
    making them manifest on mortal desktops.
    """
```

#### 2.3 Error Handling Style

```python
raise ValueError(
    "🦑 The abyss rejected your offering!"
    f"Expected pet ID should be among {valid_ids}..."
)
```

---

### Act 3: Agent Hooks Concept (1-2 minutes)

#### 3.1 Open Hook Example

```
File location: .kiro/hooks/pre-commit-example.md
```

**Key Points**:
- 🪝 Hook trigger conditions (file save)
- 🦑 TODO detection logic
- 😡 Integration concept with desktop pets

#### 3.2 Hook Behavior Description

```
"When TODO comments are detected in code,
desktop pets display different warning levels based on count:

1-2: 🐚 Whispers in the sea breeze...
3-5: 🦑 The abyss begins to stir...
6-10: 🐙 The sea monster awakens!
10+: 🌊 Triggers mischief mode!"
```

---

### Act 4: Halloween Theme System (1-2 minutes)

#### 4.1 Theme Effect Showcase

**Key Points**:
- 🎃 Dark theme UI (right-click menu, task window)
- 👻 Ghost filter effect (opacity + glow)
- 🌑 Black background, green text, orange border style

#### 4.2 Image Loading Priority

```
In Halloween mode:
1. Try to load halloween_idle.png
2. Fall back to normal image + ghost filter
3. Finally use placeholder
```

---

### Act 5: Mischief Mechanism (1-2 minutes)

#### 5.1 Mechanism Description

```
"If you ignore pets for over 1 hour,
they enter angry state and start shaking wildly!
This is the 'Trick or Treat' mechanism."
```

#### 5.2 Demo Angry State

**Method 1**: Wait 1 hour (not recommended)

**Method 2**: Temporarily modify code for demo
```python
# Temporarily modify in ignore_tracker.py
self.ignore_threshold = 10  # Change to 10 seconds for demo
```

**Key Points**:
- 😡 Pet enters angry state
- 🔄 Shaking animation effect
- 👆 Click to soothe pet
- 📢 "Trick or Treat!" notification

---

### Act 6: Complete Ecosystem (1-2 minutes)

#### 6.1 Task Reward System

```
"Every 12 tasks completed triggers reward judgment:
- 70% probability to get Tier 2 rare pet
- 30% probability to get deep sea blind box"
```

#### 6.2 Inventory Management

- Open pet management window
- Show summon/dive functions
- Show inventory status (X/20, X/5)

#### 6.3 Multi-Pet Display

- Display multiple pets simultaneously
- Show Tier 3 leviathan scaling effect

---

## 📊 Demo Data Preparation

### Preset Data File

Create `demo_data.json` for demo:

```json
{
  "version": 4.0,
  "theme_mode": "halloween",
  "unlocked_pets": ["puffer", "jelly", "starfish", "crab", "octopus", "blobfish"],
  "active_pets": ["puffer", "jelly", "blobfish"],
  "pet_tiers": {
    "tier1": ["puffer", "jelly", "starfish", "crab"],
    "tier2": ["octopus", "ribbon", "sunfish", "angler"],
    "tier3": ["blobfish", "ray", "beluga", "orca", "shark", "bluewhale"]
  },
  "reward_system": {
    "cumulative_tasks_completed": 11,
    "reward_threshold": 12
  },
  "pets_data": {
    "puffer": {
      "level": 3,
      "tasks_completed_today": 2,
      "task_states": [true, true, false]
    },
    "jelly": {
      "level": 2,
      "tasks_completed_today": 1,
      "task_states": [true, false, false]
    },
    "blobfish": {
      "level": 1,
      "tasks_completed_today": 0,
      "task_states": [false, false, false]
    }
  }
}
```

### Using Demo Data

```bash
# Backup current data
cp data.json data.json.backup

# Use demo data
cp demo_data.json data.json

# Launch app
python main.py

# Restore after demo
cp data.json.backup data.json
```

---

## 🎯 Key Demo Scenarios

### Scenario 1: Show Steering Style Code

```python
# Open theme_manager.py, show this code:

class ThemeManager:
    """
    🎃 Halloween Theme Manager - Visual curse of the Deep Sea Undead Empire.
    
    This module controls the fate of all visual effects:
    - Theme switching: Travel between light and darkness
    - Ghost filter: Dress creatures in undead garments
    - Dark style: Let UI sink into the embrace of the abyss
    
    ⚠️ Warning: Improper use may cause visual curses to spread...
    """
```

### Scenario 2: Show Error Handling

```python
# Trigger an error, show dramatic error message
# e.g., try to load non-existent pet

# Expected output:
# 🦑 The abyss rejected your offering!
# Expected pet ID should be among [...]...
```

### Scenario 3: Show Mischief Mode

```python
# Temporarily modify ignore_tracker.py for demo
# Change ignore_threshold to 10 seconds

# After 10 seconds:
# - All pets start shaking
# - Shows "Trick or Treat!" notification
# - Click pet to soothe
```

---

## 📝 Demo Script Templates

### Opening

```
"Hello everyone! Today I'm presenting PufferPet V4 - 
the Deep Sea Undead Empire edition built for Kiroween Hackathon.

This project is not just a cute desktop pet application,
but a perfect showcase of Kiro native features:
- Steering defines the Deep Sea Code Captain's code style
- Agent Hooks demonstrates integration possibilities with desktop pets
- Halloween theme and mischief mechanism add festive fun"
```

### Closing

```
"Thank you for watching! PufferPet V4 demonstrates how to integrate
Kiro's Steering and Agent Hooks features into real projects,
while adding creativity and fun through Halloween theme and mischief mechanism.

May the wisdom of the abyss guide your code,
May the blessing of the sea god protect your application!

— Deep Sea Code Captain 🦑"
```

---

## ⚠️ Demo Notes

1. **Test in Advance**: Ensure all features work properly
2. **Backup Data**: Backup data.json before demo
3. **Network Environment**: Ensure stable demo environment
4. **Time Control**: Keep each section within scheduled time
5. **Interaction Prep**: Prepare to answer judge questions

---

*"From the deepest depths of the abyss, we weave the curse of code..."* 🦑🎃
