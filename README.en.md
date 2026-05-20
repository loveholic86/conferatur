# Conferatur - File/Folder Compare Tool

[Korean](README.md) | [English](README.en.md)

Conferatur is an intuitive file and folder comparison tool built with Python tkinter.

## Latest Updates

- **Notion-style design system**: a calmer modern UI with PretendardStd as the default font.
- **English UI language switch**: switch between Korean and English from the Settings menu, with the selection saved automatically.
- **Enhanced folder tree**: status color tags, sortable columns, difference-count badges, and Expand All / Collapse All buttons.
- **Larger folder file preview**: view left and right file contents in a larger preview area from the folder comparison results.
- **Enhanced file comparison**: line-level hunk background highlights, status bars, and previous/next diff navigation.
- **More discoverable history deletion**: dedicated destructive delete button, right-click context menu, and Delete key support.
- **Full macOS support**: Command-key shortcuts such as Cmd+C/V/X/A.
- **Clipboard actions**: copy, paste, cut, and select all.
- **Right-click context menus**: available across text areas.
- **Synchronized scrolling**: mouse wheel and scrollbar dragging stay synced across paired text views.

## Features

### 1. Folder Compare Mode

- **MD5 checksum comparison**: compare file contents precisely.
- **Date comparison**: compare files by modification time.
- **Combined comparison**: use MD5 and date comparison together.
- **Tree visualization**: display the folder structure hierarchically.
- **Status color tags**: quickly distinguish diff, left_only, and right_only items in the tree.
- **Sortable columns**: click Status, Size, or Modified columns to toggle ascending/descending sort.
- **Difference-count badges**: show child difference counts on folder nodes.
- **Expand/Collapse all**: toggle the whole tree at once.
- **Exclude patterns**: exclude files or folders with `.gitignore`-style patterns such as `node_modules/` or `*.pyc`.
- Copy files in both directions, left to right or right to left.
- Delete selected files.
- **Expanded file preview**: select a file to display larger left/right previews with difference highlighting.
- **Synchronized preview scrolling**: mouse wheel and scrollbar dragging stay synced.
- History and favorites support.

### 2. Direct Text Compare Mode

- Compare two manually entered text blocks.
- **Character-level detailed comparison**: show exactly which characters differ within a line.
- Highlight differences in light red.
- Apply text from one side to the other.
- Edit and compare in place.
- **Copy/Paste shortcuts**: Cmd+C/V on macOS or Ctrl+C/V on Windows/Linux.
- **Right-click menu**: copy, cut, paste, and select all.
- **Synchronized scrolling**: mouse wheel and scrollbar dragging stay synced.
- History and favorites support.

### 3. File Content Compare Mode

- Load and compare two files.
- **Character-level detailed comparison**: show exactly which characters differ within a line.
- **Line-level hunk background highlights**: visually distinguish inserted, deleted, and changed lines.
- **Status bars**: see the current line/column position at the bottom.
- **Diff navigation**: jump between diff blocks with previous/next buttons.
- Edit file contents and save changes.
- UTF-8 encoding support.
- **Copy/Paste shortcuts**: Cmd+C/V on macOS or Ctrl+C/V on Windows/Linux.
- **Right-click menu**: copy, cut, paste, select all, and copy current diff blocks left/right.
- **Synchronized scrolling**: mouse wheel and scrollbar dragging stay synced.
- History and favorites support.

### 4. History and Favorites

- **Automatic history**: stores the latest 20 comparison jobs automatically.
- **Favorites management**: save frequently used comparison settings with custom names.
- **Favorite rename**: rename saved favorites.
- **History/Favorites deletion**: delete items in three ways:
  - Click the dedicated Delete Selected button.
  - Right-click an item and use the context menu.
  - Select an item and press Delete.
- **Search filter**: filter history/favorites instantly from the dialog search box.
- **Persistent storage**: saved in `~/.conferatur/config.json` and retained after restarting the app.

### 5. Language, Font, and Design Settings

- **UI language switch**: use Settings -> Language to switch between Korean and English.
- **Saved language setting**: the selected language is saved in `~/.conferatur/config.json`.
- **PretendardStd default font**: clean rendering for both Korean and English UI.
- **Font selection**: choose from preset fonts via Settings -> Font Settings.
- **Font size control**: preview and apply sizes from 8 to 20 pt.
- **Notion-inspired design system**: subdued colors and consistent widget styling.

## Requirements

- Python 3.7 or later
- tkinter, included with most Python installations
- **ttkbootstrap**, required

### Install Dependencies

```bash
pip install ttkbootstrap
```

If you use `pip3`:

```bash
pip3 install ttkbootstrap
```

### Check tkinter

```bash
python3 -c "import tkinter; print('tkinter available')"
```

If tkinter is missing on Ubuntu/Debian:

```bash
sudo apt-get install python3-tk
```

On macOS:

```bash
# tkinter is usually included when Python is installed through Homebrew.
brew install python-tk@3.11  # Adjust for your Python version.
```

## Usage

### Run the App

```bash
python3 compare_tool.py
```

Or grant execute permission and run directly:

```bash
chmod +x compare_tool.py
./compare_tool.py
```

### Keyboard Shortcuts

#### macOS

- **Cmd+C**: Copy
- **Cmd+V**: Paste
- **Cmd+X**: Cut
- **Cmd+A**: Select all

#### Windows/Linux

- **Ctrl+C**: Copy
- **Ctrl+V**: Paste
- **Ctrl+X**: Cut
- **Ctrl+A**: Select all
- **Ctrl+Insert**: Copy, alternative shortcut
- **Shift+Insert**: Paste, alternative shortcut
- **Shift+Delete**: Cut, alternative shortcut

### Right-Click Menu

Right-click in any text area to use:

- Copy
- Cut
- Paste
- Select all

### Change UI Language

1. Open Settings -> Language.
2. Select Korean or English.
3. The UI text updates immediately while preserving current folder/file paths and text contents.
4. The selected language is saved automatically and reused on the next launch.

### 1. Folder Compare

1. Open the Folder Compare tab.
2. Select the left and right folders.
   - Or click History to load a previous comparison.
   - Or click Load Favorite to load a saved comparison.
3. Select a comparison method:
   - **MD5 Compare**: precisely compare file contents.
   - **Date Compare**: compare file modification times.
   - **MD5 + Date**: check both content and date.
4. Click Start Compare. The job is saved to history automatically.
5. Review the result tree:
   - Folder nodes can be expanded/collapsed individually or with Expand All / Collapse All.
   - Status colors help distinguish differences and one-sided files quickly.
   - Difference-count badges on folder nodes show the scope of changes.
   - Click column headers to sort by status, size, or modified time.
   - Select a file to preview left/right contents in the expanded lower panels.
6. Copy or delete files as needed.
7. Save frequently used comparisons with Add Favorite.

### 2. Text Compare

1. Open the Text Compare tab.
2. Enter text in the left and right text areas.
   - Use keyboard shortcuts or the right-click menu for copy/paste.
   - Or load text from History or Favorites.
3. Click Compare. The job is saved to history automatically.
4. Review highlighted differences.
5. Apply one side to the other if needed.
6. Save frequently used text comparisons as favorites.

### 3. File Compare

1. Open the File Compare tab.
2. Select the left and right files.
   - Or load a pair from History or Favorites.
3. Click Compare. The job is saved to history automatically.
4. Review and edit differences:
   - Line-level hunk backgrounds distinguish inserted, deleted, and changed lines.
   - Status bars show the current position.
   - Previous/Next diff buttons move between diff blocks.
   - Use copy/paste or the right-click menu to copy current blocks left/right.
5. Save files as needed.
6. Save frequently used file pairs as favorites.

### 4. Manage History and Favorites

#### Manage History

1. Open History from the top menu and choose a mode: Folder, File, or Text.
2. Filter items with the search box at the top of the dialog.
3. Delete items in one of three ways:
   - Click the Delete Selected button.
   - Right-click an item and use the context menu.
   - Select an item and press Delete.

#### Manage Favorites

1. Open Favorites from the top menu and choose a mode.
2. Select an item, then:
   - Click Rename to edit the favorite name.
   - Click Delete Selected, right-click, or press Delete to remove it.

## Details

### Comparison Methods

- **MD5 Compare**: compares file hashes to determine whether contents match exactly. File names or dates can differ while contents remain identical.
- **Date Compare**: compares last modified times to show which side is newer.
- **MD5 + Date**: checks both content differences and date differences.

### File Statuses

- **Same**: files are identical, so they are not shown in the result tree.
- **Content differs (MD5)**: MD5 hashes differ.
- **Left only**: file exists only in the left folder.
- **Right only**: file exists only in the right folder.
- **Left is newer**: left file was modified more recently.
- **Right is newer**: right file was modified more recently.

### Copy Behavior

- **Left -> Right**: copy selected files from the left folder to the right folder.
- **Right -> Left**: copy selected files from the right folder to the left folder.
- Directory structures are created automatically.
- Existing files are overwritten.

### Synchronized Scrolling

Paired text views stay synchronized in text comparison and file preview areas:

- **Mouse wheel**: scrolling one side scrolls the other side too.
- **Scrollbar dragging**: dragging a scrollbar keeps both sides aligned.

### History and Favorites

#### History

- Every comparison job is stored automatically.
- Only the latest 20 jobs are retained.
- Folder, file, and text modes are managed separately.
- Timestamps show when each comparison was run.

#### Favorites

- Save frequently used comparison settings with custom names.
- There is no fixed favorite count limit.
- Favorites can be renamed.
- Favorites are managed separately by mode.
- Examples:
  - Folder: "Project backup compare", "Source vs build"
  - File: "Config file compare", "Version 1 vs version 2"
  - Text: "Template compare", "Translation review"

#### Data Location

- History, favorites, language/font settings, and exclude patterns are stored in `~/.conferatur/config.json`.
- Data remains available after restarting the program.
- The file is JSON and can be edited manually if needed.

## UI Theme

The app uses a custom Notion-style design system based on `design.md`:

- A subdued color palette with semantic accents such as peach, rose, mint, and lavender.
- PretendardStd as the default font for clean Korean and English UI rendering.
- Consistent button roles: primary, secondary, destructive, and ghost.
- Visual elements such as hunk backgrounds and tree status tags derive from the same palette.

`ttkbootstrap` is used as the base widget framework, with additional custom styles applied in `compare_tool.py`.

## Platform Support

- **Windows**: fully supported.
- **macOS**: fully supported with Command-key shortcuts.
- **Linux**: fully supported.

## License

MIT License

## Contributing

Issues and pull requests are welcome.
