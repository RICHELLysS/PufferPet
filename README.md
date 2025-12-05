# PufferPet 🐡🎃

A cute desktop pet application where you nurture and evolve your pets by completing daily tasks!

> *"From the deepest depths of the abyss, we weave the curse of code..."* — Deep Sea Code Captain 🦑

## 🌙 V5.5 New Features - Dynamic Day/Night Cycle

**Day/night cycle synchronized with real time, making your ocean world more vivid!**

- 🌅 **Auto Day/Night Switch**: Automatically switches between day/night mode based on system time (06:00-18:00 day, 18:00-06:00 night)
- 🌙 **Night = Halloween**: Night mode reuses Halloween theme, enjoy ghost filters and dark UI
- ⚙️ **Settings Menu**: New settings submenu to control auto sync and manual switching
- 💾 **Preference Saving**: Day/night settings auto-save, preferences persist after restart
- 🔄 **Smooth Transition**: All visual effects update in real-time when mode switches
- 🎨 **Smart Fallback**: No extra resources needed, night background auto-applies filters

## 🌊 V5 New Features - Deep Dive & Screensaver

**Immersive underwater experience, turn your desktop into a deep sea world!**

- 🌊 **Deep Dive Mode**: Full-screen underwater background, covers desktop icons, creates immersive ocean environment
- 🫧 **Bubble Particle System**: Random rising bubble animations, creating realistic underwater atmosphere
- 😴 **Screensaver Function**: Auto-activates after 5 minutes of inactivity, pets gather to screen center to rest
- 🎃 **Halloween Integration**: Deep dive mode supports Halloween theme, bubbles become ghost flames, background turns dark purple
- 🖱️ **Smart Wake**: Mouse movement or keyboard press immediately exits screensaver, pets return to original positions
- 📋 **Menu Control**: Tray icon right-click menu can manually enable/disable deep dive mode

## 🎃 V4 New Features - Kiroween Hackathon Deep Sea Undead Empire

**Halloween special edition built for Kiroween Hackathon!**

- 🎃 **Halloween Theme System**: Dark UI theme, ghost filters, curse style
- 👻 **Ghost Filter Effect**: Pets without Halloween images auto-apply ghost filter (0.6 opacity + green/purple glow)
- 😡 **Mischief Mechanism**: Ignore pets for over 1 hour, they enter angry state and start shaking!
- 🦑 **Kiro Steering**: Deep Sea Code Captain style code comments and error handling
- 🪝 **Agent Hooks Concept**: Demonstrates automated workflow integration with desktop pets
- 🌑 **Dark Theme**: Black background, green text, orange border Halloween style UI

## ✨ V3.5 New Features - Deep Sea Blind Box & Ecosystem Balance

- 🎁 **Task Reward System**: Every 12 tasks completed earns a reward (70% Tier 2 pet / 30% Deep Sea Blind Box)
- 🐋 **Deep Sea Leviathans**: 6 legendary Tier 3 creatures, obtained through blind boxes (Blobfish, Ray, Beluga, Orca, Shark, Blue Whale)
- 📦 **Inventory Management**: Own up to 20 pets, display up to 5 simultaneously
- 🌊 **Multi-Pet Display**: Show multiple pets on screen at once, create your ocean world
- 🎯 **Pet Management**: Summon, dive, release functions for flexible collection management
- 📏 **Smart Scaling**: Tier 3 leviathans auto-scale based on size (1.5x - 5.0x)

## ✨ V3 Features - Shallow Sea Expansion & Encounter System

- 🌊 **8 Marine Creatures**: Collect Puffer, Jelly, Starfish, Crab, Octopus, Ribbon, Sunfish, Angler
- 🎯 **Two-Tier System**: Tier 1 basic pets (default unlockable) + Tier 2 rare pets (encounter capture)
- ✨ **Encounter System**: Rare creatures randomly appear on screen, click to capture
- 🎣 **Capture Mechanism**: Raise any Tier 1 pet to level 3 to trigger encounter events
- 🏃 **Dynamic Visitors**: Rare creatures swim from left to right side of screen, limited-time capture adds fun
- 📦 **Auto Migration**: Seamless upgrade from V2, data auto-migrates

## ✨ V2 Features

- 🎭 **Multi-Pet System**: Collect and switch between different pets
- 🔓 **Unlock Mechanism**: Unlock new companions by raising pets
- 🔄 **Independent Progress**: Each pet has its own growth progress

## Features

- 🎨 **Transparent Desktop Pet**: Pet displays on desktop with transparent background, always on top
- 📈 **Growth System**: Complete daily tasks to evolve your pet (3 growth stages)
- ✅ **Daily Tasks**: Three simple health tasks help you maintain good habits
- 💾 **Auto Save**: Progress auto-saves, tasks auto-reset daily
- 🎯 **Simple Interface**: Right-click pet to view and manage tasks
- 🐙 **Pet Collection**: Unlock and switch between different pet types
- 🎁 **Task Rewards**: Accumulate completed tasks to earn rare pets and deep sea blind boxes
- 🏠 **Inventory Management**: Manage your pet collection, summon and release pets

## System Requirements

- Python 3.8 or higher
- Windows / macOS / Linux

## Installation

1. **Clone or download the project**
   ```bash
   cd PufferPet
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare image assets**
   
   V3.5 uses a layered directory structure:
   
   ```
   assets/
   ├── puffer/      (Puffer - Tier 1)
   ├── jelly/       (Jelly - Tier 1)
   ├── starfish/    (Starfish - Tier 1)
   ├── crab/        (Crab - Tier 1)
   ├── octopus/     (Octopus - Tier 2)
   ├── ribbon/      (Ribbon Fish - Tier 2)
   ├── sunfish/     (Sunfish - Tier 2)
   ├── angler/      (Anglerfish - Tier 2)
   └── deep_sea/    (Deep Sea Leviathans - Tier 3)
       ├── blobfish/   (Blobfish)
       ├── ray/        (Ray)
       ├── beluga/     (Beluga)
       ├── orca/       (Orca)
       ├── shark/      (Shark)
       └── bluewhale/  (Blue Whale)
   ```

   **Tier 1 & Tier 2** folders need to contain:
   - `baby_idle.png` - Level 1 image
   - `adult_idle.png` - Level 2-3 image
   
   **Tier 3** folders need to contain:
   - `idle.png` - Single image (Tier 3 has no level system)
   
   If image files are missing, the app displays colored placeholders (different color for each creature).

## Usage

### Start the Application

```bash
python main.py
```

### Basic Operations

1. **View Tasks**: Right-click on pet window, select "View Tasks"
2. **Complete Tasks**: Check completed tasks in the task window
3. **Pet Evolution**: After completing all 3 tasks, pet auto-upgrades
4. **Switch Pet**: Right-click pet, select "Switch Pet"
5. **Manage Pets**: Right-click pet, select "Manage Pets" (summon, dive, release)
6. **Release Pet**: Right-click pet, select "Release" (permanent deletion)
7. **Close App**: Close pet window or task window

### Pet Switching Guide

#### How to Switch Pets

1. **Right-click** on the pet window
2. Select **"Switch Pet"** from the menu
3. In the pet selection window, view all available pets
4. Click on an unlocked pet card to switch
5. Currently active pet will be highlighted

#### Pet Selection Window Description

- **Unlocked Pets**: Shows pet icon, name and current level, clickable to switch
- **Locked Pets**: Shows lock icon and unlock conditions, cannot be selected
- **Current Pet**: Has special highlight border

### Daily Tasks

- 💧 Drink a glass of water
- 🤸 Do some stretches
- 💼 Focus on work for 30 minutes

## 🎁 Task Reward System Details (V3.5 New)

V3.5 introduces a task reward system to make your efforts more rewarding!

### 📊 Reward Mechanism

- **Cumulative Count**: System tracks your **total cumulative tasks completed** (across all pets and all days)
- **Trigger Condition**: Every **12 tasks** completed triggers a reward judgment
- **Auto Reset**: After receiving reward, cumulative count resets to zero

### 🎲 Reward Types

Each time a reward is triggered, the system randomly determines the reward type:

| Reward Type | Probability | Description |
|-------------|-------------|-------------|
| 🐙 **Tier 2 Pet** | 70% | Randomly unlock an unowned Tier 2 rare pet |
| 🎁 **Deep Sea Blind Box** | 30% | Immediately open blind box, get a Tier 3 deep sea leviathan |

### 🎁 Deep Sea Blind Box Draw Rules

When you get a deep sea blind box, the system randomly draws a Tier 3 pet with these weights:

| Creature | Rarity | Weight | Scale Factor |
|----------|--------|--------|--------------|
| 🐡 Blobfish | Most Common | 40% | 1.5x |
| 🦈 Ray | Common | 25% | 2.0x |
| 🐋 Beluga | Uncommon | 15% | 2.5x |
| 🐬 Orca | Rare | 10% | 3.0x |
| 🦈 Shark | Very Rare | 8% | 3.5x |
| 🐳 Blue Whale | Legendary | 2% | 5.0x |

### 💡 Reward Tips

- **Keep Completing Tasks**: Complete tasks daily, cumulative count keeps growing
- **Multi-Pet Raising**: Switch between pets to complete tasks, all tasks count toward cumulative
- **Inventory Management**: Ensure inventory isn't full (max 20), otherwise can't get new pets
- **Patient Collection**: Tier 3 pets are completely random, collecting all requires luck and time

### 📝 Reward Notifications

- **Tier 2 Unlock**: Shows "Unlocked [pet name]!" notification
- **Blind Box Open**: Shows "You caught a [creature name]!" notification
- **Inventory Full**: Shows "Tank is full, please release some pets" prompt

## 🏠 Inventory Management System (V3.5 New)

V3.5 introduces an inventory management system for collecting more pets and flexible display management!

### 📦 Inventory Limits

- **Total Inventory Cap**: Own up to **20** pets maximum
- **Active Pet Cap**: Display up to **5** pets on screen simultaneously
- **Inventory Status**: Real-time display in pet management window (e.g., Inventory 15/20, Active 3/5)

### 🎯 Pet States

Each pet can be in one of two states:

1. **Active State**
   - Pets displayed on screen
   - Can complete tasks, level up, switch
   - Maximum 5 at once

2. **Inventory State**
   - Stored in inventory, not displayed on screen
   - Retains all data (level, task progress)
   - Can be summoned to screen anytime

### 🔧 Pet Management Operations

#### 📱 Open Pet Management Window

1. Right-click any pet
2. Select "Manage Pets" option
3. Opens pet management window

#### 🌊 Summon Pet

Summon a pet from inventory to screen:

1. Select a pet from the **Inventory List** in pet management window
2. Click "Summon" button
3. If active pets are less than 5, pet appears on screen
4. If already 5 active pets, shows "Already 5 pets on screen" prompt

#### 🏊 Dive

Return a screen pet to inventory:

1. Select a pet from the **Active List** in pet management window
2. Click "Dive" button
3. Pet window closes, pet returns to inventory
4. All pet data (level, task progress) is preserved

#### 🌊 Release

Permanently delete unwanted pets:

**Method 1: Via Right-Click Menu**
1. Right-click the pet window to release
2. Select "Release" option
3. Click "OK" in confirmation dialog

**Method 2: Via Management Window**
1. Select a pet in pet management window (inventory or active list)
2. Click "Release" button
3. Click "OK" in confirmation dialog

**⚠️ Note**: Release operation is irreversible! All pet data will be permanently deleted.

### 💡 Inventory Management Tips

- **Prioritize Releasing Low Level**: If inventory is full, consider releasing lower level duplicate pets
- **Keep Rare Pets**: Tier 2 and Tier 3 pets are harder to obtain, recommend keeping
- **Rotate Active Pets**: Regularly rotate active pets so different pets have chances to level up
- **Inventory Planning**: Reserve inventory space for newly obtained Tier 3 leviathans

### 📊 Behavior When Getting New Pets

When you get a new pet through rewards or encounters:

1. **Check Inventory**: If already 20 pets, shows "Tank is full, please release some pets"
2. **Add to Inventory**: New pet added to unlocked_pets list
3. **Auto Activate**: If active pets less than 5, new pet auto-displays on screen
4. **Inventory Only**: If already 5 active pets, new pet only stored in inventory

## 🌊 Tier System Explanation

PufferPet V3.5 has a three-tier system providing rich collection experience:

### 🏖️ Tier 1 - Basic Pets (Shallow Sea Creatures)

These pets are unlockable by default, with complete three-stage growth system:

| Creature | Unlock Condition | Growth Stages |
|----------|------------------|---------------|
| 🐡 Puffer | Default Unlocked | Baby → Adult (3 stages) |
| 🪼 Jelly | Default Unlocked | Baby → Adult (3 stages) |
| ⭐ Starfish | Default Unlocked | Baby → Adult (3 stages) |
| 🦀 Crab | Default Unlocked | Baby → Adult (3 stages) |

### 🌑 Tier 2 - Rare Pets (Deep Sea Creatures)

These pets can be captured through **Encounter System** or obtained via **Task Rewards**, also with complete growth system:

| Creature | Unlock Condition | Growth Stages |
|----------|------------------|---------------|
| 🐙 Octopus | Encounter Capture / Task Reward | Baby → Adult (3 stages) |
| 🐍 Ribbon | Encounter Capture / Task Reward | Baby → Adult (3 stages) |
| 🐟 Sunfish | Encounter Capture / Task Reward | Baby → Adult (3 stages) |
| 🔦 Angler | Encounter Capture / Task Reward | Baby → Adult (3 stages) |

### 🐋 Tier 3 - Deep Sea Leviathans (Legendary Creatures)

These pets can only be obtained through **Deep Sea Blind Box**, huge in size, no level system:

| Creature | Unlock Condition | Rarity | Scale Factor |
|----------|------------------|--------|--------------|
| 🐡 Blobfish | Deep Sea Blind Box | Most Common (40%) | 1.5x |
| 🦈 Ray | Deep Sea Blind Box | Common (25%) | 2.0x |
| 🐋 Beluga | Deep Sea Blind Box | Uncommon (15%) | 2.5x |
| 🐬 Orca | Deep Sea Blind Box | Rare (10%) | 3.0x |
| 🦈 Shark | Deep Sea Blind Box | Very Rare (8%) | 3.5x |
| 🐳 Blue Whale | Deep Sea Blind Box | Legendary (2%) | 5.0x |

### 📊 Growth System

**Tier 1 & Tier 2** creatures follow the same growth rules:

| Level | Tasks Required | Image File |
|-------|----------------|------------|
| 1 | Initial State | baby_idle.png |
| 2 | Complete 3 tasks | adult_idle.png |
| 3 | Complete 3 more tasks | adult_idle.png |

**Tier 3** Deep Sea Leviathan characteristics:

- ❌ **No Level System**: Tier 3 creatures have no growth stages, always maintain adult form
- ❌ **No Task System**: Cannot level up by completing tasks
- ✅ **Decorative**: Mainly for desktop decoration, showcasing collection achievements
- ✅ **Smart Scaling**: Auto-scales based on creature size (1.5x - 5.0x)
- ✅ **Multi-Pet Display**: Can display simultaneously with other pets on screen

## ✨ Encounter System Details

The encounter system is V3's core gameplay, letting you discover and capture rare deep sea creatures!

### 🎯 How to Trigger Encounters

1. **Unlock Condition**: Raise **any** Tier 1 pet to **Level 3**
2. **Auto Trigger**: After meeting conditions, system auto-enables encounter mechanism
3. **Timed Check**: Every **5 minutes** performs an encounter check
4. **Trigger Probability**: Each check has **30%** chance to trigger encounter event

### 🏃 Rare Creature Appearance

When an encounter event triggers:

1. **Random Selection**: System randomly selects one from **unlocked** Tier 2 pets
2. **Horizontal Movement**: Rare creature appears from screen **left**, swims to **right**
3. **Limited Time Capture**: Creature crosses screen in **15-20 seconds**
4. **Auto Disappear**: If not captured, creature disappears after reaching right edge

### 🎣 How to Capture Rare Creatures

Capturing is simple:

1. **Watch Screen**: Notice rare creatures swimming from the left
2. **Click to Capture**: **Left-click** on the swimming creature
3. **Instant Unlock**: After successful capture, creature immediately joins your collection
4. **Show Notification**: App displays capture success notification

### 📝 Encounter System Features

- ✅ **Background Running**: Encounter system runs automatically in background, no manual operation needed
- ✅ **Non-Intrusive**: Visitor window doesn't block your other operations
- ✅ **Transparent Display**: Rare creatures display with transparent background, blending into desktop
- ✅ **Complete Collection**: After capturing all 4 Tier 2 pets, encounter events auto-stop
- ⚠️ **Requires Level 3**: If all Tier 1 pets are below level 3, encounter system pauses

### 💡 Capture Tips

- **Keep App Running**: Encounters only trigger while app is running
- **Raise Multiple Pets**: Level multiple Tier 1 pets to level 3 to ensure encounter system keeps running
- **Watch Screen Edges**: Rare creatures appear from left, watch the left side of screen
- **Quick Reaction**: Creatures move fast, click promptly when you see them

## 🎯 How to Get Deep Sea Leviathans - Complete Guide

Want to collect legendary Tier 3 deep sea leviathans? Follow this complete guide!

### 📋 Prerequisites

Before starting to collect deep sea leviathans, you need:

1. ✅ Own at least 1 pet (default is puffer)
2. ✅ Able to complete daily tasks
3. ✅ Have patience and luck!

### 🎯 Acquisition Process

#### Step 1: Accumulate Completed Tasks

1. **Complete Tasks Daily**: Open task window, complete three daily tasks
2. **Rotate Pet Raising**: Can switch different pets to complete tasks, all tasks count toward cumulative
3. **View Progress**: System auto-tracks your cumulative task completion count

#### Step 2: Trigger Reward Judgment

1. **Reach 12 Tasks**: Every 12 cumulative tasks triggers one reward judgment
2. **Auto Trigger**: When completing the 12th task, system auto-performs reward judgment
3. **Reset Count**: After receiving reward, cumulative count resets to zero

#### Step 3: Get Deep Sea Blind Box

Reward judgment has two possible outcomes:

- **70% Probability**: Get Tier 2 rare pet (Octopus, Ribbon, Sunfish, Angler)
- **30% Probability**: Get Deep Sea Blind Box ⭐

**If you get a blind box**:
1. System immediately opens the blind box
2. Randomly draws one Tier 3 deep sea leviathan by weight
3. Shows "You caught a [creature name]!" notification

#### Step 4: Blind Box Draw Results

After opening blind box, you'll get one of these creatures:

| Creature | Probability | Size |
|----------|-------------|------|
| 🐡 Blobfish | 40% | Small (1.5x) |
| 🦈 Ray | 25% | Medium (2.0x) |
| 🐋 Beluga | 15% | Large (2.5x) |
| 🐬 Orca | 10% | Large (3.0x) |
| 🦈 Shark | 8% | Giant (3.5x) |
| 🐳 Blue Whale | 2% | Super Giant (5.0x) |

### 📊 Expected Value Calculation

Want to know how long to collect all 6 deep sea leviathans?

- **Trigger One Blind Box**: Average need to complete 12 ÷ 0.3 = **40 tasks**
- **3 Tasks Per Day**: About **13-14 days** to trigger one blind box
- **Collect All 6 Types**: Considering duplicates, average need **15-20 blind boxes**
- **Total Time Estimate**: About **6-9 months** to collect all (if completing daily)

### 💡 Speed Up Collection Tips

#### 1. Multi-Pet Rotation Strategy

- Raise multiple pets to level 3
- Rotate different pets daily to complete tasks
- All tasks count toward cumulative, speeds up reward triggering

#### 2. Inventory Management

- **Keep Inventory Space**: Ensure inventory isn't full (max 20)
- **Release Promptly**: Release duplicate or low-level pets to make space
- **Reserve Slots**: Reserve at least 5 inventory slots for Tier 3 leviathans

#### 3. Active Pet Management

- **Display Multiple**: Can display up to 5 pets simultaneously
- **Rotate Raising**: Summon different pets to screen to complete tasks
- **Dive to Rest**: Max level pets can dive, making room for new pets

#### 4. Keep Completing Tasks

- **Login Daily**: Complete at least 3 tasks daily
- **Continuous Accumulation**: Cumulative task count saves across days
- **Patient Waiting**: Collecting Tier 3 requires time and luck

### ⚠️ FAQ

**Q: I completed 12 tasks but didn't get a blind box?**

A: Reward judgment has 70% probability to get Tier 2 pet, only 30% probability for blind box. Keep completing tasks, next time might get a blind box!

**Q: After opening blind box, I don't see the new pet?**

A: Check these situations:
- Is inventory full (20 max)? If full, shows "Tank is full" prompt
- Are active pets full (5 max)? If full, new pet goes to inventory
- Open pet management window, look for new pet in inventory list

**Q: What if I get duplicate Tier 3 pets?**

A: Tier 3 pets can be obtained repeatedly. You can:
- Keep multiple identical leviathans (e.g., 5 blue whales)
- Release duplicates to make room for new pets
- Display multiple identical leviathans simultaneously for spectacular scenes

**Q: Blue whale only has 2% probability, too hard to get!**

A: Blue whale is a legendary creature, indeed very rare. Suggestions:
- Stay patient, keep completing tasks
- Average need 50 blind boxes to get 1 blue whale
- Enjoy the collection process, don't obsess over single targets

### 🎉 Collection Achievements

Deep sea leviathan collection milestones:

- 🥉 **First Encounter**: Get 1st Tier 3 creature
- 🥈 **Deep Sea Explorer**: Get 3 different Tier 3 creatures
- 🥇 **Ocean Collector**: Get all 6 Tier 3 creatures
- 👑 **Legend Hunter**: Get Blue Whale (2% probability)
- 🌟 **Perfect Collection**: Own all 14 creatures (Tier 1-3)

## 🐾 Complete Creature Encyclopedia

### Tier 1 - Shallow Sea Creatures

#### 🐡 Puffer
- **Unlock**: Default Unlocked
- **Features**: Round body, cute expression
- **Images**: `assets/puffer/baby_idle.png`, `assets/puffer/adult_idle.png`

#### 🪼 Jelly
- **Unlock**: Default Unlocked
- **Features**: Elegant tentacles, transparent body
- **Images**: `assets/jelly/baby_idle.png`, `assets/jelly/adult_idle.png`

#### ⭐ Starfish
- **Unlock**: Default Unlocked
- **Features**: Five-pointed star shape, vibrant colors
- **Images**: `assets/starfish/baby_idle.png`, `assets/starfish/adult_idle.png`

#### 🦀 Crab
- **Unlock**: Default Unlocked
- **Features**: Walks sideways, powerful claws
- **Images**: `assets/crab/baby_idle.png`, `assets/crab/adult_idle.png`

### Tier 2 - Deep Sea Creatures (Rare)

#### 🐙 Octopus
- **Unlock**: Via Encounter Capture
- **Features**: Eight tentacles, smart and agile
- **Images**: `assets/octopus/baby_idle.png`, `assets/octopus/adult_idle.png`

#### 🐍 Ribbon
- **Unlock**: Via Encounter Capture
- **Features**: Long slender body, elegant swimming
- **Images**: `assets/ribbon/baby_idle.png`, `assets/ribbon/adult_idle.png`

#### 🐟 Sunfish
- **Unlock**: Via Encounter Capture
- **Features**: Huge and flat, adorably clumsy
- **Images**: `assets/sunfish/baby_idle.png`, `assets/sunfish/adult_idle.png`

#### 🔦 Angler
- **Unlock**: Via Encounter Capture
- **Features**: Head-mounted light, deep sea hunter
- **Images**: `assets/angler/baby_idle.png`, `assets/angler/adult_idle.png`

### Tier 3 - Deep Sea Leviathans (Legendary)

#### 🐡 Blobfish
- **Unlock**: Deep Sea Blind Box (40% probability)
- **Features**: Adorably clumsy, most common deep sea leviathan
- **Scale**: 1.5x
- **Image**: `assets/deep_sea/blobfish/idle.png`

#### 🦈 Ray
- **Unlock**: Deep Sea Blind Box (25% probability)
- **Features**: Flat body, elegant gliding
- **Scale**: 2.0x
- **Image**: `assets/deep_sea/ray/idle.png`

#### 🐋 Beluga
- **Unlock**: Deep Sea Blind Box (15% probability)
- **Features**: White body, gentle and friendly
- **Scale**: 2.5x
- **Image**: `assets/deep_sea/beluga/idle.png`

#### 🐬 Orca
- **Unlock**: Deep Sea Blind Box (10% probability)
- **Features**: Black and white pattern, ocean apex
- **Scale**: 3.0x
- **Image**: `assets/deep_sea/orca/idle.png`

#### 🦈 Shark
- **Unlock**: Deep Sea Blind Box (8% probability)
- **Features**: Streamlined body, apex predator
- **Scale**: 3.5x
- **Image**: `assets/deep_sea/shark/idle.png`

#### 🐳 Blue Whale
- **Unlock**: Deep Sea Blind Box (2% probability)
- **Features**: Earth's largest creature, legendary existence
- **Scale**: 5.0x
- **Image**: `assets/deep_sea/bluewhale/idle.png`

## Data Storage

The app creates a `data.json` file in the project directory to save:
- Current displayed pet ID (deprecated, V3.5 uses active_pets)
- Unlocked pets list (inventory, max 20)
- Active pets list (pets displayed on screen, max 5)
- Pet tier definitions (Tier 1 / Tier 2 / Tier 3)
- Tier 3 scale factor configuration
- Tier 3 blind box draw weights
- Each pet's independent data:
  - Current level (Tier 3 has no level)
  - Tasks completed today
  - Task completion states
  - Last login date
- Encounter system settings:
  - Check interval
  - Trigger probability
  - Last check time
- Task reward system:
  - Cumulative completed tasks
  - Reward trigger threshold (12)
  - Tier 2 unlock probability (70%)
  - Blind box probability (30%)
- Inventory limit configuration:
  - Max inventory (20)
  - Max active (5)

Tasks auto-reset for all pets on first launch each day.

### Data Migration Notes

#### Upgrading from V3 to V3.5

If upgrading from V3 to V3.5, the app will **auto-migrate** your data:

1. **Auto Detection**: App detects V3 data format on startup
2. **Data Migration**: 
   - Preserves all your existing pet data (8 creatures)
   - Adds Tier 3 deep sea leviathan configuration (6 new creatures)
   - Creates active_pets list (migrates current_pet_id to active pets)
   - Initializes task reward system (cumulative_tasks_completed)
   - Adds inventory limit configuration (max_inventory: 20, max_active: 5)
   - Adds Tier 3 scale factors and draw weights
3. **Backup Created**: V3 data backed up as `data.json.v3.backup`
4. **Seamless Experience**: Migration is fully automatic, no manual operation needed

#### V5.5 Data Format (Latest)

V5.5 adds day/night cycle related configuration on top of V5:

```json
{
  "version": 5.5,
  "day_night_settings": {
    "auto_time_sync": true,
    "current_mode": "day"
  },
  "deep_dive_settings": {
    "enabled": false,
    "auto_screensaver": true,
    "idle_timeout_minutes": 5,
    "bubble_density": "normal"
  },
  "screensaver_settings": {
    "gather_pets_to_center": true,
    "saved_pet_positions": {}
  }
}
```

**V5.5 New Fields:**
- `day_night_settings`: Day/night cycle configuration
  - `auto_time_sync`: Whether to auto-switch based on system time (default true)
  - `current_mode`: Current mode ("day" or "night")

**V5 Fields:**
- `deep_dive_settings`: Deep dive mode configuration
  - `enabled`: Whether deep dive mode is enabled
  - `auto_screensaver`: Whether auto screensaver is enabled
  - `idle_timeout_minutes`: Idle timeout in minutes
  - `bubble_density`: Bubble density (low/normal/high)
- `screensaver_settings`: Screensaver configuration
  - `gather_pets_to_center`: Whether to gather pets to center during screensaver
  - `saved_pet_positions`: Saved original pet positions

## Development and Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_properties.py -v

# View test coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Project Structure

```
PufferPet/
├── main.py                      # Application entry point
├── data_manager.py              # Data management module
├── pet_widget.py                # Main window component
├── task_window.py               # Task window component
├── pet_selector_window.py       # Pet selection window
├── pet_management_window.py     # Pet management window (V3.5 new)
├── pet_manager.py               # Pet manager (V3.5 new)
├── reward_manager.py            # Task reward manager (V3.5 new)
├── encounter_manager.py         # Encounter manager (V3 new)
├── visitor_window.py            # Visitor window (V3 new)
├── theme_manager.py             # Theme manager (V4 new)
├── ignore_tracker.py            # Ignore tracker (V4 new)
├── ocean_background.py          # Deep dive background window (V5 new)
├── idle_watcher.py              # Idle watcher (V5 new)
├── time_manager.py              # Time manager (V5.5 new)
├── assets/                      # Image assets (V3.5 new structure)
├── tests/                       # Test files
├── data.json                    # User data (generated at runtime)
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Tech Stack

- **GUI Framework**: PyQt6
- **Data Format**: JSON
- **Testing Framework**: pytest + Hypothesis (property-based testing)
- **Input Monitoring**: pynput (V5 new, for screensaver idle detection)

## Troubleshooting

### Issue: Pet displays as colored block

**Cause**: Image file missing or path error

**Solution**: 
- Check if `assets/puffer/` and `assets/jelly/` folders exist
- Confirm image filenames are correct

### Issue: Data not saving

**Cause**: File permission issue

**Solution**: 
- Ensure app has write permission to current directory
- Check if `data.json` is being used by another program

### Issue: Task window won't open

**Cause**: Possibly incomplete PyQt6 installation

**Solution**: 
```bash
pip uninstall PyQt6
pip install PyQt6
```

## FAQ

### Basic Questions

#### Q: Can I display multiple pets simultaneously?

A: Yes! V3.5 supports displaying up to **5** pets on screen simultaneously. Use the pet management window to summon and dive pets.

#### Q: Will switching pets lose progress?

A: No! Each pet has independent progress saved. When switching back, previous level and task progress are preserved.

#### Q: When do daily tasks reset?

A: Tasks auto-reset to incomplete state for all pets on first app launch each day.

#### Q: Can I customize task content?

A: Current version has fixed tasks (drink water, stretch, focus work). Future versions may add customization.

#### Q: Where is data stored?

A: Data is stored in `data.json` file in the app directory. You can manually backup this file to save progress.

### Pet Collection Questions

#### Q: How to unlock more pets?

A: V3.5 has three unlock methods:
- **Tier 1 pets** (4 types): Default unlocked (Puffer, Jelly, Starfish, Crab)
- **Tier 2 pets** (4 types): Via encounter capture or task rewards
- **Tier 3 pets** (6 types): Via deep sea blind box (need to complete 12 tasks to trigger reward)

#### Q: What's the maximum number of pets I can own?

A: Inventory cap is **20** pets. If inventory is full, need to release some pets to get new ones.

### Deep Dive Mode Questions (V5)

#### Q: Deep dive mode not showing underwater background?

A: Check these situations:
- Confirm `assets/environment/seabed.png` file exists
- If file doesn't exist, shows deep blue gradient placeholder
- Check if window is blocked by other fullscreen apps

#### Q: Screensaver not auto-activating?

A: Check these situations:
- Confirm pynput library is correctly installed (`pip install pynput`)
- On macOS, need to authorize in "System Preferences > Security & Privacy > Accessibility"
- On Linux, may need to add user to `input` group
- Confirm no other programs are continuously generating mouse/keyboard events

## License

This project is for learning and personal use only.

## Contributing

Welcome to submit issue reports and improvement suggestions!

---

Enjoy spending Halloween time with your deep sea pets! 🐡🪼🎃👻

*"May the wisdom of the abyss guide your code, may the blessing of the sea god protect your application."* — Deep Sea Code Captain 🦑
