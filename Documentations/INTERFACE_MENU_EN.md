# Windows Menu Interface

## 📋 Overview

The DAOC Character Manager application uses a traditional Windows interface with a menu bar instead of a toolbar. This approach provides a more familiar and professional user experience.

## 🎯 Menu Structure

### File Menu

The **File** menu contains the main application actions:

- **New Character**: Creates a new character with name, realm, season and server
- **Settings**: Opens the application configuration window

### View Menu

The **View** menu allows interface customization:

- **Columns**: Configure visible columns in the character list

### Help Menu

The **Help** menu provides application information:

- **About**: Displays application information, version and creator

## 🚀 Usage

### Creating a New Character

1. Click **File > New Character**
2. Fill out the form:
   - **Name**: Character name
   - **Realm**: Albion, Hibernia or Midgard
   - **Season**: S1, S2, S3, etc.
   - **Server**: Eden, Blackthorn, etc.
3. Click "OK" to create the character

### Configuring the Application

1. Click **File > Settings**
2. Adjust settings according to your preferences:
   - Storage directories
   - Interface language
   - Theme (light/dark)
   - Default server and season
   - Debug mode
3. Click "Save" to save changes

### Customizing the Display

1. Click **View > Columns**
2. Check/uncheck columns to display:
   - Selection (for bulk actions)
   - Realm (icon)
   - Season, Server, Name, Level
   - Realm Rank and Title
3. Click "OK" to apply changes

## 🌍 Multilingual Support

The menu interface is fully translated into:
- 🇫🇷 **Français**: Fichier, Affichage, Aide
- 🇬🇧 **English**: File, View, Help  
- 🇩🇪 **Deutsch**: Datei, Ansicht, Hilfe

Language change is done via **File > Settings > Language**.

## ✨ Menu Interface Advantages

### Compared to a toolbar:

- ✅ **More professional**: Standard Windows interface
- ✅ **Space saving**: More room for data
- ✅ **Logical organization**: Actions grouped by category
- ✅ **Accessibility**: Keyboard navigation with Alt+key
- ✅ **Scalability**: Easier to add new features

### Keyboard shortcuts (future):
- `Ctrl+N`: New character
- `Ctrl+,`: Settings
- `F1`: About

## 🔧 Technical Configuration

The menu interface uses the following PySide6 components:
- `QMenuBar`: Main menu bar
- `QMenu`: Individual menus (File, View, Help)
- `QAction`: Menu actions
- Translation system via `language_manager.py`

Menu recreation during language changes ensures instant interface translation.

---

**Version**: 0.101  
**Date**: October 27, 2025  
**Author**: DAOC Character Manager Team