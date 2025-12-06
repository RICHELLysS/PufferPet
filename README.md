# PufferPet 🐡

A simple desktop pet application built with PyQt6. Complete daily tasks to grow your pet!

> **Note**: This is a beta version developed for Kiro Hackathon. Some features may have bugs.

## Features

### Core Gameplay
- 🐡 **5 Collectible Pets**: Puffer, Jelly, Crab, Starfish, Ray(special)
- 📈 **Growth System**: Dormant → Baby → Adult (complete tasks to evolve)
- 🎁 **Blindbox System**: Get new pets when your pet reaches adult stage
- 🌓 **Day/Night Mode**: Manual toggle between light and dark themes

### Interactions
- 🖱️ **Drag**: Drag adult pets around the screen
- 😡 **Anger**: Click adult pets 5 times quickly to trigger anger animation
- 📋 **Tasks**: Right-click to open task window

### Pet Requirements
| Pet | Tasks to Awaken | Tasks to Adult |
|-----|-----------------|----------------|
| Puffer, Jelly, Crab, Starfish | 1 | 3 |
| Ray (SSR) | 2 | 5 |

## Quick Start

### Download & Run
1. Download `PufferPet.exe` from [Releases](../../releases)
2. Run the executable
3. Right-click the pet to open task window
4. Complete tasks to grow your pet!

### Build from Source
```bash
# Install dependencies
pip install -r requirements.txt

# Run
python main.py

# Build executable
pyinstaller PufferPet.spec
```

## How to Play

1. **Start**: A dormant puffer appears on your screen
2. **Awaken**: Complete 1 task to awaken (Baby stage)
3. **Grow**: Complete 3 tasks total to reach Adult stage
4. **Gacha**: When pet becomes Adult, you get a new pet from gacha!
5. **Interact**: Drag adult pets or click 5 times for anger animation

## Controls

| Action | How |
|--------|-----|
| Open Tasks | Right-click pet |
| Drag Pet | Left-click and drag (Adult only) |
| Trigger Anger | Click 5 times quickly (Adult only) |
| Toggle Day/Night | Right-click → Environment → Toggle Mode |

## Known Issues

- Animation system may occasionally get stuck after interactions
- Some UI elements may not display correctly in certain scenarios

## Tech Stack

- Python 3.8+
- PyQt6
- PyInstaller (for building)

## License

MIT License

---

*Built with 🐡 for Kiro Hackathon*
