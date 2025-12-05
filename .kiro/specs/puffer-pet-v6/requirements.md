# V6 Stable Version Requirements Document

## Introduction

PufferPet V6 is a streamlined, stable desktop pet application. The core gameplay is a "Dormant-Baby-Adult" three-stage life cycle. All complex encounter probabilities, auto-slicing scripts, and 20-pet limit logic have been removed to focus on stability and core experience.

## Glossary

- **PufferPet Application**: The main desktop pet application system
- **Pet State (state)**: Current life stage of the pet (0=Dormant, 1=Baby, 2=Adult)
- **Task Progress (tasks_progress)**: Number of tasks completed in current cycle
- **Dormant Filter**: Grayscale + 60% opacity visual effect
- **Day/Night Mode**: Theme mode that auto-switches based on time

## Requirements

### Requirement 1: Three-Stage Life Cycle

**User Story:** As a user, I want pets to have clear growth stages, so that I can feel a sense of achievement from nurturing them.

#### Acceptance Criteria

1. WHEN pet state is 0 (Dormant) THEN PufferPet Application SHALL fix the pet at the bottom of the screen
2. WHEN pet state is 0 THEN PufferPet Application SHALL apply dormant filter (grayscale + 60% opacity) to baby_idle image
3. WHEN pet state is 0 THEN PufferPet Application SHALL disable dragging and normal click interactions
4. WHEN user right-clicks dormant pet THEN PufferPet Application SHALL display task settings window
5. WHEN user completes 1 task and state is 0 THEN PufferPet Application SHALL switch state to 1 (Baby)
6. WHEN pet state is 1 THEN PufferPet Application SHALL remove filter and play baby_idle animation
7. WHEN pet state is 1 THEN PufferPet Application SHALL allow free swimming and drag interactions
8. WHEN user accumulates 3 completed tasks and state is 1 THEN PufferPet Application SHALL switch state to 2 (Adult)
9. WHEN pet state is 2 THEN PufferPet Application SHALL load adult_idle image

### Requirement 2: Task and Cycle System

**User Story:** As a user, I want to awaken and nurture pets by completing tasks.

#### Acceptance Criteria

1. WHEN task window displays THEN window SHALL show current progress (format: X/3)
2. WHEN user checks a task THEN PufferPet Application SHALL increment tasks_progress count
3. WHEN tasks_progress changes from 0 to 1 THEN PufferPet Application SHALL trigger pet evolution from Dormant to Baby
4. WHEN tasks_progress reaches 3 THEN PufferPet Application SHALL trigger pet evolution from Baby to Adult
5. WHEN user sets cycle reset THEN PufferPet Application SHALL reset tasks_progress to 0 and state to 0

### Requirement 3: Asset Management and Fault Tolerance

**User Story:** As a user, I want the application to never crash under any circumstances.

#### Acceptance Criteria

1. WHEN loading pet image THEN PufferPet Application SHALL first try to load .gif file
2. WHEN .gif doesn't exist THEN PufferPet Application SHALL try to load frame sequence _0.png
3. WHEN frame sequence doesn't exist THEN PufferPet Application SHALL try to load single .png
4. WHEN all images don't exist THEN PufferPet Application SHALL draw colored ellipse placeholder with pet name
5. WHEN any exception occurs THEN PufferPet Application SHALL catch exception and continue running

### Requirement 4: Day/Night Mode (Preserved Feature)

**User Story:** As a user, I want the application to auto-switch visual themes based on time.

#### Acceptance Criteria

1. WHEN system time is between 06:00-18:00 THEN PufferPet Application SHALL use day theme
2. WHEN system time is between 18:00-06:00 THEN PufferPet Application SHALL use night theme
3. WHEN night theme is activated THEN background SHALL apply dark filter effect
