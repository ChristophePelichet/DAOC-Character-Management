# 🚀 Future Improvements - DAOC Character Management

List of improvement ideas and features to develop later.

---

## 📋 Overview

### Theme System
- [ ] [Integrated Theme Editor](#1-integrated-theme-editor)
- [ ] [Automatic Variant Generation](#2-automatic-variant-generation)
- [ ] [Theme Import/Export](#3-theme-importexport)

### Ignored Items Management System
- [ ] [Ignored Items Management Interface](#4-ignored-items-management-interface)
- [ ] [Unignore Button to Reactivate an Item](#5-unignore-button-to-reactivate-an-item)
- [ ] [Export/Import Ignored Items List](#6-exportimport-ignored-items-list)

---

## 🎨 Theme System

### 1. Integrated Theme Editor
- Graphical interface to create/modify themes directly in the application
- Color pickers for each element (window, text, buttons, etc.)
- Real-time preview of modifications
- Automatic save to a new JSON file

### 2. Automatic Variant Generation
- From a base color, automatically generate:
  - Complementary colors (text, background, highlight)
  - Disabled variations (grayed out)
  - Complete harmonious palette
- Contrast algorithms to ensure readability
- Generation of light/dark variants of the same theme

### 3. Theme Import/Export
- Theme sharing between users
- Standardized export format (JSON with metadata)
- Community theme library
- Automatic validation of imported themes

---

## 📋 Features to Add

### Ignored Items Management System

#### 4. Ignored Items Management Interface
**Objective**: Allow visualization and complete management of items marked as ignored

**Features**:
- Dedicated window listing all items with `ignore_item: true`
- Table with columns: Name, Realm, Initial Reason, Ignore Date
- Sorting and filtering by realm/name
- Quick search in the list
- Total counter of ignored items
- Access via "Tools" menu or button in Mass Import

**Benefits**:
- Transparency on ignored items
- Avoids oversights (items ignored by mistake)
- Facilitates database auditing

#### 5. Unignore Button to Reactivate an Item
**Objective**: Allow removing the `ignore_item` flag from one or more items

**Features**:
- "Unignore" button in the management interface (point 4)
- Multiple selection of items to reactivate
- Confirmation before flag removal
- Action logging in debug logs
- Automatic DB update

**Workflow**:
1. User opens the ignored items management interface
2. Selects one or more items (e.g., quest item that became useful)
3. Clicks "Unignore" → Confirmation
4. `ignore_item` flag removed from DB
5. Item will reappear in future imports

**Benefits**:
- Flexibility to correct errors
- Adaptation to game content changes
- No need to manually edit JSON

#### 6. Export/Import Ignored Items List
**Objective**: Share or save the ignored items list

**Export Features**:
- "Export Ignored List" button in the management interface
- Readable JSON format with metadata:
  ```json
  {
    "version": "1.0",
    "exported_date": "2025-11-19",
    "total_items": 25,
    "items": [
      {
        "name": "Quest Item X",
        "realm": "Albion",
        "id": "12345",
        "reason": "Quest item - not importable"
      }
    ]
  }
  ```
- Export to `.ignore-list.json` file
- Option to filter by realm before export

**Import Features**:
- "Import Ignored List" button
- Selection of a `.ignore-list.json` file
- Item preview before import
- Options:
  - Merge (add to existing ignored items)
  - Replace (replace current list)
- Format validation before import
- Import report: X items added, Y already present

**Use Cases**:
- **Player sharing**: "Here's my quest items to ignore list"
- **Backup**: Save before reinstallation
- **Template**: Create a common list for a guild
- **Migration**: Transfer between servers/seasons

**Benefits**:
- Time saving for new users
- Configuration standardization
- Security (backup before modifications)

---

## 💡 Additional Ideas

### Ignored Items - Advanced Features
- [ ] **Custom ignore reason**: Free text field to document why an item is ignored
- [ ] **Ignore categories**: Tags (Quest, Duplicate, Obsolete, Low Priority)
- [ ] **Temporary ignore**: Flag expiration date (useful for limited events)
- [ ] **Statistics**: Graph of ignore reasons, top ignored items by category
- [ ] **Automatic suggestions**: AI detecting patterns (recurring quest items)
- [ ] **Ignore history**: Log with date/time/user of each modification

---

*(This section will be completed as development progresses)*



---
## 💡 Miscellaneous Ideas

*(Brainstorming ideas to refine later)*

### 7. Dropdown Menus in Database Editor
**Objective**: Add dropdown menus in editable columns to limit input errors and standardize values

**Features**:
- **Realm column**: Dropdown with predefined values (Albion, Hibernia, Midgard, All)
- **Slot column**: Dropdown with valid slots (Helmet, Hands, Torso, Arms, Feet, Legs, Right Hand, Left Hand, Two Handed, Ranged, Neck, Cloak, Jewelry, Waist, L Ring, R Ring, L Wrist, R Wrist, Mythical)
- **Type column**: Dropdown with item types (Armor, Weapon, Jewelry, Mythical, etc.)
- **Damage Type column**: Dropdown with damage types (Crush, Slash, Thrust, Body, Cold, Energy, Heat, Matter, Spirit)
- **Source column**: Dropdown with sources (internal, user, scraped)
- **Item Category column**: Dropdown with categories (quest_reward, event_reward, unknown)
- Auto-completion for frequently used values

**Benefits**:
- Prevents typos and inconsistent data
- Faster data entry
- Improved database data quality
- Better validation before saving

**Current Status**: 
- ❌ **To be implemented later** - Current free text input in all fields

---

### 8. Owned Items Tracking System (Armory)
**Objective**: Allow checking items from a template that the player already owns to automatically calculate missing currencies

**Features**:
- Interactive table with checkboxes for each template item
- Columns: ✓ Owned | Item | Price | Currency | Zone
- Real-time dynamic calculation:
  ```
  Scales        12 / 50   (38 missing)
  Souls          0 / 25   (25 missing)
  ```
- Checkbox state saving per template/character
- Quick reset for new template

**Benefits**:
- Precise planning of necessary farming
- Visualization of progress towards complete template
- Avoids buying already owned items
- Farm run optimization by zone

**Current Status**: 
- ✅ Display of total currency summary by type (in text preview with frame)
- ❌ Checkbox system and owned/missing calculation **to be implemented later**

---

**Note**: This file serves as an informal backlog. Priority items will be turned into issues/development branches at the appropriate time.
