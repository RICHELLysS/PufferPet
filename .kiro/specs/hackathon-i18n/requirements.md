# Requirements Document

## Introduction

This feature prepares PufferPet for Hackathon submission by implementing global English translation (i18n) and PyInstaller packaging readiness. The judges cannot read Chinese, so all user-visible text, comments, and logs must be translated to idiomatic English while maintaining the "Spooky/Dramatic" code comment style for the Costume Contest.

## Glossary

- **i18n**: Internationalization - the process of adapting software for different languages
- **PyInstaller**: A tool that bundles Python applications into standalone executables
- **resource_path**: A helper function that resolves asset paths correctly in both development and packaged environments
- **UI Text**: Any text visible to users in menus, dialogs, buttons, labels, and tooltips
- **Spooky Style**: Dramatic, horror-themed code comments using deep-sea/ghost metaphors

## Requirements

### Requirement 1: UI Text Translation

**User Story:** As a Hackathon judge, I want all UI text in English, so that I can understand and evaluate the application.

#### Acceptance Criteria

1. WHEN the application displays menu items THEN the System SHALL show English text (e.g., "Tasks", "Inventory", "Settings", "Quit")
2. WHEN the application displays dialog titles and labels THEN the System SHALL use English text (e.g., "Daily Tasks", "Progress", "My Pets")
3. WHEN the application displays button text THEN the System SHALL use English labels (e.g., "OK", "Done", "Release", "Toggle Day/Night")
4. WHEN the application displays tooltips and status messages THEN the System SHALL use English text
5. WHEN the application displays message boxes THEN the System SHALL use English titles and content (e.g., "Confirm Release", "Inventory Full", "Congratulations!")

### Requirement 2: Code Comment Translation

**User Story:** As a code reviewer, I want all code comments in English with Spooky/Dramatic style, so that I can understand the code while appreciating the Costume Contest theme.

#### Acceptance Criteria

1. WHEN reviewing module docstrings THEN the System SHALL contain English text with dramatic deep-sea/ghost metaphors
2. WHEN reviewing function docstrings THEN the System SHALL contain English descriptions with optional spooky flavor
3. WHEN reviewing inline comments THEN the System SHALL use English text
4. WHEN reviewing print/log statements THEN the System SHALL output English messages

### Requirement 3: PyInstaller Resource Path Handling

**User Story:** As a user running the packaged executable, I want the application to find all assets correctly, so that the application does not crash.

#### Acceptance Criteria

1. WHEN the application loads assets THEN the System SHALL use resource_path() function to resolve paths
2. WHEN the application runs as a frozen executable THEN the System SHALL detect frozen state using sys.frozen attribute
3. WHEN the application loads images from assets/ folder THEN the System SHALL prepend the correct base path
4. WHEN the application runs in development mode THEN the System SHALL use relative paths normally

### Requirement 4: PyInstaller Build Configuration

**User Story:** As a developer, I want a working PyInstaller command, so that I can build a distributable executable.

#### Acceptance Criteria

1. WHEN building the executable THEN the build command SHALL include --noconsole flag for no terminal window
2. WHEN building the executable THEN the build command SHALL include --onefile flag for single-file output
3. WHEN building the executable THEN the build command SHALL include --add-data for assets folder
4. WHEN an icon file exists THEN the build command SHALL attempt to include it with --icon flag
