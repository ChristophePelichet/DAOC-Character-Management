# Theme System - Technical Documentation

Complete technical documentation for the theme management system in DAOC Character Manager.

**Version**: 0.108  
**Last Updated**: November 17, 2025  
**Module**: `Functions/theme_manager.py`

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Theme File Format](#theme-file-format)
4. [Available Themes](#available-themes)
5. [Qt Palette System](#qt-palette-system)
6. [Stylesheet Customization](#stylesheet-customization)
7. [Font Scaling](#font-scaling)
8. [Creating a New Theme](#creating-a-new-theme)
9. [Theme Application Flow](#theme-application-flow)
10. [API Reference](#api-reference)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The theme system provides a flexible, JSON-based approach to customize the entire application's appearance. Themes control:

- **Qt Palette**: Base colors for all Qt widgets (window, text, buttons, highlights, etc.)
- **Qt Style**: Platform-specific rendering style (WindowsVista, Fusion, etc.)
- **Custom Stylesheets**: CSS-like rules for fine-grained control over specific widgets
- **Font Scaling**: Dynamic font size adjustment independent of theme selection

### Key Features

✅ **Hot-Reload**: Theme changes apply immediately without restart  
✅ **Modular Design**: Themes are separate JSON files in `Themes/` folder  
✅ **Localized Names**: Theme names use translation keys (e.g., `theme_light` → "Clair")  
✅ **Font Scaling**: Independent font size control (75%-150%) compatible with all themes  
✅ **Fallback Safety**: If a theme fails to load, system defaults to `default.json`

---

## Architecture

```
DAOC-Character-Management/
├── Functions/
│   └── theme_manager.py        # Core theme management logic
├── Themes/
│   ├── default.json            # Light theme (Windows Vista style)
│   ├── dark.json               # Dark theme (Fusion style)
│   └── purple.json             # Purple/Dracula theme (Fusion style)
├── Language/
│   ├── fr.json                 # Theme name translations
│   ├── en.json
│   └── de.json
└── UI/
    └── settings_dialog.py      # Theme selection UI (Page 1)
```

### Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `theme_manager.py` | Load/apply themes, manage font scaling, stylesheet parsing |
| `settings_dialog.py` | Theme selection UI (QComboBox with radio buttons) |
| `config_manager.py` | Persist selected theme and font_scale in `config.json` |
| `language_manager.py` | Translate theme names (e.g., `theme_light` → "Light") |

---

## Theme File Format

Themes are JSON files stored in `Themes/` folder with the following structure:

```json
{
  "name": "theme_light",
  "style": "windowsvista",
  "palette": {
    "Window": "#F0F0F0",
    "WindowText": "#000000",
    "Base": "#FFFFFF",
    "AlternateBase": "#F5F5F5",
    "ToolTipBase": "#FFFFDC",
    "ToolTipText": "#000000",
    "Text": "#000000",
    "Button": "#F0F0F0",
    "ButtonText": "#000000",
    "BrightText": "#FF0000",
    "Link": "#0000FF",
    "Highlight": "#0078D7",
    "HighlightedText": "#FFFFFF",
    "Disabled_WindowText": "#7F7F7F",
    "Disabled_Text": "#7F7F7F",
    "Disabled_ButtonText": "#7F7F7F"
  },
  "stylesheet": "QMenuBar { background-color: palette(window); }"
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ Yes | Translation key (e.g., `theme_light`) or display name |
| `style` | string | ✅ Yes | Qt style name (`windowsvista`, `Fusion`, `Windows`, etc.) |
| `palette` | object | ⚠️ Optional | QPalette color roles (see [Qt Palette System](#qt-palette-system)) |
| `stylesheet` | string | ⚠️ Optional | Custom CSS stylesheet (see [Stylesheet Customization](#stylesheet-customization)) |

### Valid Qt Styles

The `style` field must match one of the available Qt styles on the platform:

- **Windows**: `windowsvista`, `Windows`, `Fusion`
- **Linux**: `Fusion`, `Windows` (basic)
- **macOS**: `macOS`, `Fusion`

⚠️ **Best Practice**: Use `Fusion` for dark themes (cross-platform consistency) and `windowsvista` for light themes (native Windows look).

---

## Available Themes

### 1. Light Theme (`default.json`)

**Translation Key**: `theme_light`  
**Qt Style**: `windowsvista` (native Windows appearance)  
**Color Scheme**: Light gray background (#F0F0F0), white base (#FFFFFF), black text  
**Use Case**: Default theme, professional appearance, optimal readability in bright environments

**Key Colors**:
- Window: `#F0F0F0` (light gray)
- Base: `#FFFFFF` (white)
- Highlight: `#0078D7` (Windows blue)

---

### 2. Dark Theme (`dark.json`)

**Translation Key**: `theme_dark`  
**Qt Style**: `Fusion` (flat, modern rendering)  
**Color Scheme**: Dark gray background (#2D2D30), very dark base (#1E1E1E), light gray text (#DCDCDC)  
**Use Case**: Reduced eye strain in low-light environments, modern aesthetic

**Key Colors**:
- Window: `#2D2D30` (dark gray)
- Base: `#1E1E1E` (almost black)
- Text: `#DCDCDC` (light gray)
- Highlight: `#0078D7` (blue)

**Disabled Colors**:
- Disabled text: `#7F7F7F` (medium gray, 50% opacity effect)

---

### 3. Purple Theme (`purple.json`)

**Translation Key**: `theme_purple`  
**Qt Style**: `Fusion`  
**Color Scheme**: Dracula-inspired palette with purple accents (#BD93F9)  
**Use Case**: Developer-friendly dark theme, vibrant highlights, reduced blue light

**Key Colors**:
- Window: `#282A36` (dark blue-gray)
- Base: `#1E1E1E` (very dark gray)
- Text: `#F8F8F2` (off-white)
- Highlight: `#BD93F9` (purple)
- Link: `#8BE9FD` (cyan)
- BrightText: `#FF79C6` (pink)

**Custom Stylesheets** (v0.108 fixes):
```css
/* QLineEdit styling for placeholder visibility */
QLineEdit { 
  color: #F8F8F2; 
  background-color: #1E1E1E; 
  border: 1px solid #6272A4; 
}
QLineEdit:focus { 
  border: 1px solid #BD93F9; 
}
QLineEdit::placeholder { 
  color: #6272A4;  /* Gray placeholder text */
}
```

**Recent Fixes** (Branch `108_Fix_Purple_Theme`):
- ✅ Progress dialog status label: `background-color: transparent` (was `#f5f5f5`)
- ✅ QLineEdit placeholder text: `color: #6272A4` (was invisible/black)

---

## Qt Palette System

Qt uses a **palette** system with predefined color roles. Each role controls a specific UI element category.

### Standard Color Roles

| Role | Description | Example Usage |
|------|-------------|---------------|
| `Window` | Background of widgets (windows, dialogs) | Main window background |
| `WindowText` | Text in windows | Labels, titles |
| `Base` | Background of text entry widgets | QLineEdit, QTextEdit, QTableWidget |
| `AlternateBase` | Alternate row color in tables/lists | QTableWidget alternating rows |
| `ToolTipBase` | Tooltip background | Hover tooltips |
| `ToolTipText` | Tooltip text | Hover tooltip text |
| `Text` | Foreground text in entry widgets | QLineEdit text, table cell text |
| `Button` | Button background | QPushButton, QComboBox |
| `ButtonText` | Button text | QPushButton label |
| `BrightText` | Highlighted/emphasized text | Error messages, warnings |
| `Link` | Hyperlink color | QLabel with links |
| `Highlight` | Selection background | Selected table row, selected text |
| `HighlightedText` | Text on highlighted background | Text in selected row |

### Disabled State Colors

Disabled state colors use the prefix `Disabled_` in the JSON file:

```json
{
  "palette": {
    "Text": "#DCDCDC",             // Normal text color
    "Disabled_Text": "#7F7F7F"     // Text color when widget is disabled
  }
}
```

**Supported Disabled Roles**:
- `Disabled_WindowText`
- `Disabled_Text`
- `Disabled_ButtonText`

### Color Format

All colors must be **hexadecimal RGB** format:

✅ Valid: `"#FFFFFF"`, `"#0078D7"`, `"#282A36"`  
❌ Invalid: `"white"`, `"rgb(255,255,255)"`, `"#FFF"` (short form)

---

## Stylesheet Customization

The `stylesheet` field allows CSS-like customization for specific Qt widgets.

### Syntax

Qt stylesheets use CSS syntax with Qt-specific selectors:

```css
QWidget { property: value; }
QWidget:state { property: value; }
QWidget::sub-control { property: value; }
```

### Common Selectors

| Selector | Description | Example |
|----------|-------------|---------|
| `QMenuBar` | Menu bar widget | `QMenuBar { background-color: #2D2D30; }` |
| `QMenuBar::item` | Individual menu item | `QMenuBar::item:selected { background-color: #3C3C3C; }` |
| `QMenu` | Dropdown menu | `QMenu { border: 1px solid #5C5C5C; }` |
| `QMenu::separator` | Menu separator line | `QMenu::separator { height: 1px; }` |
| `QComboBox QAbstractItemView` | Dropdown list in combobox | `QComboBox QAbstractItemView { background-color: #3C3C3C; }` |
| `QLineEdit` | Text input field | `QLineEdit { border: 1px solid #6272A4; }` |
| `QLineEdit::placeholder` | Placeholder text | `QLineEdit::placeholder { color: #6272A4; }` |
| `QToolTip` | Hover tooltip | `QToolTip { background-color: #44475A; }` |

### Common States

| State | Description | Example |
|-------|-------------|---------|
| `:hover` | Mouse over element | `QPushButton:hover { background-color: #4C4C4C; }` |
| `:pressed` | Element being clicked | `QPushButton:pressed { background-color: #0078D7; }` |
| `:selected` | Selected item | `QMenu::item:selected { background-color: #BD93F9; }` |
| `:focus` | Element has keyboard focus | `QLineEdit:focus { border: 1px solid #BD93F9; }` |
| `:disabled` | Element is disabled | `QPushButton:disabled { color: #7F7F7F; }` |

### Palette References

You can reference palette colors in stylesheets using `palette(role-name)`:

```css
QMenuBar {
  background-color: palette(window);
  color: palette(window-text);
}
```

**Available Palette References**:
- `palette(window)` → Window color
- `palette(window-text)` → WindowText color
- `palette(base)` → Base color
- `palette(text)` → Text color
- `palette(button)` → Button color
- `palette(highlight)` → Highlight color
- `palette(highlighted-text)` → HighlightedText color

### Example: Purple Theme Stylesheet (Full)

```css
QToolTip { 
  color: #F8F8F2; 
  background-color: #44475A; 
  border: 1px solid #6272A4; 
} 

QMenuBar { 
  background-color: #282A36; 
  color: #F8F8F2; 
} 

QMenuBar::item { 
  background-color: transparent; 
  padding: 4px 8px; 
} 

QMenuBar::item:selected { 
  background-color: #44475A; 
} 

QMenuBar::item:pressed { 
  background-color: #BD93F9; 
  color: #282A36; 
} 

QMenu { 
  background-color: #44475A; 
  color: #F8F8F2; 
  border: 1px solid #6272A4; 
} 

QMenu::item { 
  padding: 4px 24px 4px 8px; 
} 

QMenu::item:selected { 
  background-color: #BD93F9; 
  color: #282A36; 
} 

QMenu::separator { 
  height: 1px; 
  background-color: #6272A4; 
  margin: 4px 0px; 
} 

QComboBox QAbstractItemView { 
  background-color: #44475A; 
  color: #F8F8F2; 
  selection-background-color: #BD93F9; 
  selection-color: #282A36; 
  border: 1px solid #6272A4; 
} 

QLineEdit { 
  color: #F8F8F2; 
  background-color: #1E1E1E; 
  border: 1px solid #6272A4; 
  padding: 4px; 
} 

QLineEdit:focus { 
  border: 1px solid #BD93F9; 
} 

QLineEdit::placeholder { 
  color: #6272A4; 
}
```

---

## Font Scaling

Font scaling is **independent** of theme selection and controlled by `font_scale` in `config.json`.

### Configuration

**Range**: `0.75` (75%) to `1.5` (150%)  
**Default**: `1.0` (100%)  
**Storage**: `config.json` → `font_scale` field

### How It Works

1. **Base Font**: Application uses Segoe UI 9pt as base font (Windows default)
2. **Scaling Factor**: User selects percentage in Settings (75%, 90%, 100%, 110%, 125%, 150%)
3. **Application**: `apply_font_scale()` multiplies base size by factor
4. **Stylesheet Adjustment**: Font sizes in stylesheets are also scaled using regex

### Scaling Functions

#### `apply_font_scale(app, scale=1.0)`

Applies font scaling to the entire application.

```python
from Functions.theme_manager import apply_font_scale
from PySide6.QtWidgets import QApplication

app = QApplication.instance()
apply_font_scale(app, 1.25)  # 125% scaling
```

**Process**:
1. Sets base font to `9pt × scale`
2. Applies `setFont()` to QApplication
3. Re-scales existing stylesheet fonts using regex

#### `scale_stylesheet_fonts(stylesheet, scale)`

Scales all font sizes in a CSS stylesheet.

```python
from Functions.theme_manager import scale_stylesheet_fonts

css = "QLabel { font-size: 10pt; } QPushButton { font-size: 12px; }"
scaled_css = scale_stylesheet_fonts(css, 1.25)
# Result: "QLabel { font-size: 12.5pt; } QPushButton { font-size: 15.0px; }"
```

**Supported Units**:
- `pt` (points) - e.g., `10pt` → `12.5pt`
- `px` (pixels in `font-size` property) - e.g., `12px` → `15.0px`

#### `get_scaled_size(base_size_pt)`

Helper function for dynamic font sizing in code.

```python
from Functions.theme_manager import get_scaled_size

label = QLabel("Text")
label.setStyleSheet(f"font-size: {get_scaled_size(10):.1f}pt;")
# With 125% scaling: font-size: 12.5pt;
```

**Use Case**: Character sheet labels, achievement displays, dynamically created widgets

---

## Creating a New Theme

### Step 1: Create JSON File

Create `Themes/mytheme.json`:

```json
{
  "name": "theme_mytheme",
  "style": "Fusion",
  "palette": {
    "Window": "#1A1A1A",
    "WindowText": "#E0E0E0",
    "Base": "#0D0D0D",
    "Text": "#E0E0E0",
    "Button": "#2A2A2A",
    "ButtonText": "#E0E0E0",
    "Highlight": "#FF6600",
    "HighlightedText": "#FFFFFF"
  },
  "stylesheet": "QMenuBar { background-color: #1A1A1A; }"
}
```

### Step 2: Add Translations

Edit `Language/fr.json`, `en.json`, `de.json`:

```json
{
  "themes": {
    "theme_mytheme": "Mon Thème"  // FR
    // "My Theme"  // EN
    // "Mein Thema"  // DE
  }
}
```

### Step 3: Test Theme

1. Restart application
2. Go to **Settings** → **Themes**
3. Select "Mon Thème" from dropdown
4. Click "Apply"

### Step 4: Refinement

Common issues to check:

- ✅ **Contrast**: Ensure text is readable on backgrounds (use contrast checker)
- ✅ **Disabled State**: Test disabled buttons/inputs (should be visibly different)
- ✅ **Tooltips**: Verify tooltip background contrasts with text
- ✅ **Placeholders**: Check QLineEdit placeholder visibility
- ✅ **Progress Dialogs**: Test with `background-color: transparent` on status labels
- ✅ **Tables**: Verify alternating row colors work well

### Best Practices

1. **Use Fusion for Dark Themes**: Better rendering for dark color schemes
2. **Define Disabled Colors**: Always include `Disabled_Text`, `Disabled_ButtonText`, `Disabled_WindowText`
3. **Test All UI Elements**: Open every dialog, check every input field
4. **Transparent Backgrounds**: For overlays, use `background-color: transparent` instead of fixed colors
5. **Consistent Highlights**: Use the same `Highlight` color across all widgets for UX consistency

---

## Theme Application Flow

### Startup Sequence

```
main.py
├─ Load config.json
│  └─ Read "theme" field (default: "default")
├─ QApplication.instance()
├─ apply_theme(app, theme_id)
│  ├─ load_theme(theme_id) → JSON data
│  ├─ app.setStyle(style_name)
│  ├─ app.setPalette(palette)
│  └─ app.setStyleSheet(stylesheet)
└─ Show MainWindow
```

### Runtime Theme Change (Settings Dialog)

```
Settings Dialog (Page 1)
├─ User selects theme from QComboBox
├─ "Apply" button clicked
├─ save_settings()
│  ├─ config.set("theme", new_theme_id)
│  ├─ config.save()
│  └─ apply_theme(QApplication.instance(), new_theme_id)
└─ UI updates immediately (no restart)
```

### Code Example: Apply Theme

```python
from PySide6.QtWidgets import QApplication
from Functions.theme_manager import apply_theme
from Functions.config_manager import config

# Get current theme from config
current_theme = config.get("theme", "default")

# Apply theme
app = QApplication.instance()
apply_theme(app, current_theme)
```

---

## API Reference

### `get_themes_dir() -> Path`

Returns the path to the `Themes/` folder.

**Returns**: `pathlib.Path` object

**Example**:
```python
from Functions.theme_manager import get_themes_dir
themes_dir = get_themes_dir()
print(themes_dir)  # C:\...\DAOC-Character-Management\Themes
```

---

### `get_available_themes() -> dict`

Returns a dictionary of all available themes.

**Returns**: `dict[str, str]` - `{theme_id: translated_name}`

**Example**:
```python
from Functions.theme_manager import get_available_themes

themes = get_available_themes()
# {'default': 'Clair', 'dark': 'Sombre', 'purple': 'Purple'}
```

**Note**: Theme names are automatically translated using `language_manager.lang.get()`.

---

### `load_theme(theme_id: str) -> dict | None`

Loads theme data from JSON file.

**Parameters**:
- `theme_id` (str): Theme identifier (filename without `.json`)

**Returns**: `dict` with theme data, or `None` if error

**Example**:
```python
from Functions.theme_manager import load_theme

theme_data = load_theme("purple")
print(theme_data["name"])  # "theme_purple"
print(theme_data["style"])  # "Fusion"
```

---

### `apply_theme(app: QApplication, theme_id: str = "default")`

Applies a theme to the application.

**Parameters**:
- `app` (QApplication): Application instance
- `theme_id` (str): Theme to apply (default: `"default"`)

**Example**:
```python
from PySide6.QtWidgets import QApplication
from Functions.theme_manager import apply_theme

app = QApplication.instance()
apply_theme(app, "dark")
```

**Side Effects**:
- Sets Qt style (`app.setStyle()`)
- Sets color palette (`app.setPalette()`)
- Sets custom stylesheet (`app.setStyleSheet()`)
- Applies font scaling if configured

---

### `apply_font_scale(app: QApplication, scale: float = 1.0)`

Applies font scaling factor to the application.

**Parameters**:
- `app` (QApplication): Application instance
- `scale` (float): Scaling factor (0.75 to 1.5)

**Example**:
```python
from PySide6.QtWidgets import QApplication
from Functions.theme_manager import apply_font_scale

app = QApplication.instance()
apply_font_scale(app, 1.25)  # 125% font size
```

**Base Font**: 9pt Segoe UI (Windows default)

---

### `scale_stylesheet_fonts(stylesheet: str, scale: float) -> str`

Scales all font sizes in a CSS stylesheet.

**Parameters**:
- `stylesheet` (str): CSS stylesheet string
- `scale` (float): Scaling factor

**Returns**: Modified stylesheet string

**Example**:
```python
from Functions.theme_manager import scale_stylesheet_fonts

css = "QLabel { font-size: 10pt; }"
scaled = scale_stylesheet_fonts(css, 1.5)
# Result: "QLabel { font-size: 15.0pt; }"
```

**Regex Patterns**:
- `(\d+(?:\.\d+)?)pt` → Matches font sizes in points
- `font-size:\s*(\d+(?:\.\d+)?)px` → Matches font-size in pixels

---

### `get_scaled_size(base_size_pt: float) -> float`

Returns scaled font size based on current config.

**Parameters**:
- `base_size_pt` (float): Base size in points

**Returns**: Scaled size in points

**Example**:
```python
from Functions.theme_manager import get_scaled_size

label = QLabel("Achievement")
label.setStyleSheet(f"font-size: {get_scaled_size(9):.1f}pt;")
# With 125% scaling: font-size: 11.2pt;
```

**Use Case**: Dynamic UI elements (character sheets, tables, progress dialogs)

---

### `get_scaled_stylesheet(stylesheet: str) -> str`

Returns stylesheet with scaled font sizes.

**Parameters**:
- `stylesheet` (str): CSS stylesheet

**Returns**: Scaled stylesheet

**Example**:
```python
from Functions.theme_manager import get_scaled_stylesheet

css = "QLabel { font-size: 12pt; }"
scaled_css = get_scaled_stylesheet(css)
# With 110% scaling: "QLabel { font-size: 13.2pt; }"
```

---

## Troubleshooting

### Theme Not Loading

**Symptom**: Application uses default system style instead of selected theme.

**Causes**:
1. Invalid JSON syntax in theme file
2. Missing `name` or `style` field
3. Theme file not in `Themes/` folder

**Solution**:
```python
# Check logs for error messages
import logging
logging.basicConfig(level=logging.DEBUG)

# Verify theme file exists
from Functions.theme_manager import get_themes_dir
themes_dir = get_themes_dir()
print(list(themes_dir.glob("*.json")))
```

---

### Colors Not Applying

**Symptom**: Some widgets have incorrect colors.

**Causes**:
1. Invalid color role name (typo in palette key)
2. Invalid hex color format (e.g., `#FFF` instead of `#FFFFFF`)
3. Stylesheet overrides palette colors

**Solution**:
1. Verify color role names match Qt's QPalette roles exactly
2. Use full 6-digit hex codes: `#RRGGBB`
3. Check stylesheet for conflicting `background-color` or `color` properties

---

### Placeholder Text Invisible

**Symptom**: QLineEdit placeholder text appears black/invisible in dark themes.

**Cause**: Missing `QLineEdit::placeholder` stylesheet rule.

**Solution** (v0.108):
```json
{
  "stylesheet": "QLineEdit::placeholder { color: #6272A4; }"
}
```

**Fixed in**: Purple theme (`purple.json`)

---

### Progress Dialog White Background

**Symptom**: Status label at bottom of progress dialog has white square background.

**Cause**: Fixed `background-color: #f5f5f5` in `progress_dialog_base.py`.

**Solution** (v0.108):
```python
# UI/progress_dialog_base.py
self.status_label.setStyleSheet(
    "padding: 10px; "
    "border: 1px solid #ccc; "
    "border-radius: 5px; "
    "background-color: transparent;"  # Changed from #f5f5f5
)
```

**Fixed in**: Branch `108_Fix_Purple_Theme`

---

### Font Scaling Not Working

**Symptom**: Font size doesn't change when adjusting scale in settings.

**Causes**:
1. `font_scale` not saved to `config.json`
2. Application not restarted after change
3. Hardcoded font sizes in custom stylesheets

**Solution**:
1. Verify `config.json` contains `"font_scale": 1.25`
2. Check if `apply_font_scale()` is called in settings save
3. Use `get_scaled_size()` for dynamic font sizing

---

### Dark Theme Too Bright

**Symptom**: Dark theme (#2D2D30) not dark enough.

**Solution**: Create custom theme with darker `Window` and `Base` colors:
```json
{
  "palette": {
    "Window": "#1A1A1A",   // Darker than #2D2D30
    "Base": "#0D0D0D"       // Almost black
  }
}
```

---

## Related Documentation

- **Settings Architecture**: `Documentations/Settings/SETTINGS_ARCHITECTURE_EN.md`
- **UI Component Template**: `Documentations/Settings/UI_COMPONENT_TEMPLATE.md`
- **Language System**: `Documentations/Lang/LANGUAGE_V2_TECHNICAL_DOC.md`
- **Configuration Schema**: `Functions/config_schema.py`

---

## Changelog (Theme System)

### v0.108 (November 17, 2025)

**Fixes**:
- ✅ Progress dialog status label: `background-color: transparent` (fixes white square in Purple theme)
- ✅ QLineEdit placeholder text: Added `color: #6272A4` to Purple theme stylesheet (fixes invisible placeholder)

**Branch**: `108_Fix_Purple_Theme`

**Files Modified**:
- `UI/progress_dialog_base.py` (lines 428, 610)
- `Themes/purple.json` (added QLineEdit rules)

---

**End of Documentation**
