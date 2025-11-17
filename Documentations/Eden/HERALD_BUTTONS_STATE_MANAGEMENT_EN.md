# Herald Buttons State Management - Technical Documentation

## Overview

**Version**: 0.108+  
**Purpose**: Prevent Chrome profile conflicts during Eden Herald validation  
**Impact**: Selenium stability, user experience, Chrome profile integrity  
**Implementation**: Button state management + validation thread lifecycle tracking  

---

## Problem Statement

### Chrome Profile Conflict Issue

**Scenario**: Two Selenium instances trying to access the same Chrome profile simultaneously:
1. **Startup validation thread** (`EdenStatusThread`) - Checks Herald connection automatically at app launch
2. **User-triggered operation** - Manual character update, Herald search, or stats update

**Error Symptom**:
```
Selenium Error: Chrome profile cannot be opened by multiple processes
Browser freezes on first load
Cookies fail to load
```

**Root Cause**: Chrome locks the profile directory when opened by Selenium. A second Selenium instance cannot access the same profile until the first one releases it.

### Previous Solution (Removed)

**Approach**: Show `QMessageBox.warning()` popup when user clicks during validation

**Problems**:
- ❌ Poor user experience (unexpected error dialogs)
- ❌ Reactive instead of proactive (user already clicked)
- ❌ No visual feedback that operation is unavailable
- ❌ User doesn't know when they can retry

---

## Solution Architecture

### Design Principles

1. **Proactive UI State Management** - Disable buttons BEFORE user can click
2. **Visual Feedback** - Tooltips explain why buttons are disabled
3. **Instant Reactivity** - State updates immediately when validation completes
4. **Thread-Safe** - No race conditions between validation thread and UI updates

### State Management Flow

```
App Startup
    ↓
create_context_menu() → Menu action created
    ↓
check_eden_status() → Validation thread started
    ↓                  eden_validation_in_progress = True
    ↓
_update_herald_buttons_state() → Disable all Herald buttons/actions
    ↓                              Set tooltips "⏳ Validation en cours..."
    ↓
[Validation Running - Buttons DISABLED]
    ↓
update_eden_status(result) ← Thread sends result signal
    ↓                         eden_validation_in_progress = False
    ↓
_update_herald_buttons_state() → Enable all Herald buttons/actions
    ↓                              Restore normal tooltips
    ↓
[Validation Complete - Buttons ENABLED]
```

---

## Implementation Details

### Flag-Based Validation Tracking

**Why Not `thread.isRunning()`?**

**Problem**: Thread's `finished` signal is emitted **after** `status_updated` signal, causing 2-3 second delay:

```python
# OLD APPROACH (Slow)
is_validation_running = (
    hasattr(self, 'eden_status_thread') and 
    self.eden_status_thread and 
    self.eden_status_thread.isRunning()  # ← Still True for 2-3s after result
)
```

**Solution**: Use internal flag set immediately when result arrives:

```python
# NEW APPROACH (Instant)
is_validation_running = getattr(self, 'eden_validation_in_progress', False)
```

**Timeline Comparison**:

| Event | Old `isRunning()` | New Flag |
|-------|------------------|----------|
| Validation starts | `True` | `True` |
| Result received | `True` ⚠️ | `False` ✅ |
| Thread cleanup | `True` ⚠️ | `False` ✅ |
| Thread finished | `False` | `False` |
| **UI Update Delay** | **2-3 seconds** | **Instant** |

### Code Implementation

**File**: `Functions/ui_manager.py`

#### 1. Start Validation

```python
def check_eden_status(self):
    """Vérifie le statut de connexion Eden en arrière-plan"""
    # Mark validation as in progress
    self.eden_validation_in_progress = True
    
    # Disable buttons immediately
    self.refresh_button.setEnabled(False)
    self.search_button.setEnabled(False)
    
    # Start validation thread
    self.eden_status_thread = EdenStatusThread(cookie_manager)
    self.eden_status_thread.status_updated.connect(self.update_eden_status)
    self.eden_status_thread.finished.connect(self._on_validation_finished)
    self.eden_status_thread.start()
    
    # Update Herald buttons state (will disable them)
    self._update_herald_buttons_state()
```

#### 2. Receive Validation Result

```python
def update_eden_status(self, accessible, message):
    """Met à jour l'affichage du statut Eden"""
    # Mark validation as FINISHED immediately when result arrives
    self.eden_validation_in_progress = False
    
    if accessible:
        self.eden_status_label.setText(f"✅ Herald accessible")
        self.refresh_button.setEnabled(True)
    else:
        self.eden_status_label.setText(f"❌ {message}")
        if "Aucun cookie" in message:
            self.refresh_button.setEnabled(False)
            self.search_button.setEnabled(False)
    
    # Update Herald buttons IMMEDIATELY (no delay)
    self._update_herald_buttons_state()
```

#### 3. Update Button States

```python
def _update_herald_buttons_state(self):
    """Désactive/active les boutons et actions Herald selon l'état de validation Eden"""
    from Functions.language_manager import lang
    
    # Check validation status (based on flag, NOT isRunning())
    is_validation_running = getattr(self, 'eden_validation_in_progress', False)
    
    # Context menu action
    if hasattr(self, 'update_from_herald_action'):
        self.update_from_herald_action.setEnabled(not is_validation_running)
        if is_validation_running:
            tooltip = lang.get("herald_buttons.validation_in_progress")
            self.update_from_herald_action.setToolTip(tooltip)
            self.update_from_herald_action.setStatusTip(tooltip)
        else:
            self.update_from_herald_action.setToolTip("")
            self.update_from_herald_action.setStatusTip("")
    
    # Search button
    if hasattr(self, 'search_button'):
        if is_validation_running:
            self.search_button.setEnabled(False)
            self.search_button.setToolTip(lang.get("herald_buttons.validation_in_progress"))
        else:
            self.search_button.setEnabled(True)
            self.search_button.setToolTip(lang.get("buttons.eden_search"))
```

#### 4. Context Menu Display Hook

```python
def show_context_menu(self, position):
    """Affiche le menu contextuel à la position spécifiée"""
    index = self.main_window.character_tree.indexAt(position)
    if index.isValid():
        # Update button states RIGHT BEFORE showing menu
        # This ensures visual state matches actual state
        self._update_herald_buttons_state()
        
        self.main_window.character_tree.setCurrentIndex(index)
        self.context_menu.exec(...)
```

**Why Update on Display?**: Qt doesn't automatically refresh QAction visual state. We must update it just before showing the menu to ensure disabled actions appear grayed out.

#### 5. Safety Callback

```python
def _on_validation_finished(self):
    """Appelé quand le thread de validation se termine (sécurité)"""
    # Final safety check when thread actually finishes
    self.eden_validation_in_progress = False
    self._update_herald_buttons_state()
```

**Purpose**: Ensure flag is reset even if `update_eden_status()` is never called (error handling).

---

## Protected Operations

### Four Entry Points

All operations that use Chrome profile are protected:

| Entry Point | File | Method | UI Element |
|-------------|------|--------|------------|
| **Character Update (Context)** | `main.py` | `update_character_from_herald()` | Right-click menu → "Update from Herald" |
| **Character Update (Sheet)** | `UI/dialogs.py` | `update_from_herald()` | Character Sheet → "Update from Herald" button |
| **Herald Search** | `main.py` | `open_herald_search()` | Main window → "Search" button |
| **Stats Update** | `UI/dialogs.py` | `update_rvr_stats()` | Character Sheet → "Update RvR Stats" button |

### Protection Pattern

**In main.py**:
```python
def update_character_from_herald(self):
    """Update character from Herald (context menu)"""
    # Silent return if validation running (action already disabled)
    if hasattr(self.ui_manager, 'eden_validation_in_progress'):
        if self.ui_manager.eden_validation_in_progress:
            return  # No popup, button is disabled with tooltip
    
    # Proceed with update...
```

**In UI/dialogs.py**:
```python
def update_from_herald(self):
    """Update character from Herald (sheet button)"""
    main_window = self.parent()
    if main_window and hasattr(main_window, 'ui_manager'):
        if getattr(main_window.ui_manager, 'eden_validation_in_progress', False):
            return  # Button is disabled, should not reach here
    
    # Proceed with update...
```

**Why Check?**: Defense in depth - even if button state fails to update, operation is blocked.

---

## Character Sheet Integration

### Button State Management

**File**: `UI/dialogs.py` - `CharacterSheetWindow` class

#### Initialization

```python
def __init__(self, parent, character_data):
    super().__init__(parent)
    
    # Connect to Eden validation lifecycle
    if hasattr(parent, 'ui_manager'):
        ui_manager = parent.ui_manager
        # Update buttons when validation finishes
        if hasattr(ui_manager, 'eden_status_thread'):
            ui_manager.eden_status_thread.finished.connect(
                self._update_herald_buttons_state
            )
        
        # Initial state check (after buttons created)
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self._update_herald_buttons_state)
```

#### Button State Update

```python
def _update_herald_buttons_state(self):
    """Met à jour l'état des boutons Herald selon l'état de validation Eden"""
    from Functions.language_manager import lang
    
    main_window = self.parent()
    is_validation_running = False
    
    if main_window and hasattr(main_window, 'ui_manager'):
        is_validation_running = getattr(
            main_window.ui_manager, 
            'eden_validation_in_progress', 
            False
        )
    
    # Update "Update from Herald" button
    if hasattr(self, 'update_herald_button'):
        if is_validation_running:
            self.update_herald_button.setEnabled(False)
            self.update_herald_button.setToolTip(
                lang.get("herald_buttons.validation_in_progress")
            )
        else:
            self.update_herald_button.setEnabled(True)
            self.update_herald_button.setToolTip(
                lang.get("character_sheet.labels.update_from_herald_tooltip")
            )
    
    # Update "Update RvR Stats" button
    if hasattr(self, 'update_rvr_button'):
        herald_url = self.herald_url_edit.text().strip()
        
        if is_validation_running:
            self.update_rvr_button.setEnabled(False)
            self.update_rvr_button.setToolTip(
                lang.get("herald_buttons.validation_in_progress")
            )
        elif not herald_url or self.herald_scraping_in_progress:
            pass  # Keep disabled (no URL or already scraping)
        else:
            self.update_rvr_button.setEnabled(True)
            self.update_rvr_button.setToolTip(
                lang.get("update_rvr_pvp_tooltip")
            )
```

---

## Internationalization

### Translation Keys

**File**: `Language/{fr,en,de}.json`

```json
{
  "herald_buttons": {
    "validation_in_progress": "⏳ Validation Eden en cours... Veuillez patienter"
  }
}
```

**Translations**:

| Language | Text |
|----------|------|
| 🇫🇷 French | "⏳ Validation Eden en cours... Veuillez patienter" |
| 🇬🇧 English | "⏳ Eden validation in progress... Please wait" |
| 🇩🇪 German | "⏳ Eden-Validierung läuft... Bitte warten" |

### Usage in Code

```python
from Functions.language_manager import lang

tooltip_text = lang.get(
    "herald_buttons.validation_in_progress",
    default="⏳ Validation Eden en cours... Veuillez patienter"
)
```

**Fallback**: If translation missing, default French text is used.

---

## User Experience

### Before (v0.107 and earlier)

**Scenario**: User clicks "Update from Herald" during startup validation

```
User Action: Click "Update from Herald"
    ↓
Application: Process click
    ↓
Check: Is validation running?
    ↓
Result: YES → Show error popup
    ↓
User sees: ⚠️ "Mise à jour bloquée - La validation Eden est en cours"
    ↓
User must: Click OK, wait unknown time, retry
```

**Problems**:
- ❌ Unexpected error dialog
- ❌ No indication of when to retry
- ❌ User doesn't know validation is happening

### After (v0.108+)

**Scenario**: User sees disabled button during startup validation

```
App Startup
    ↓
Validation starts (2-4 seconds)
    ↓
Button state: DISABLED + tooltip "⏳ Validation Eden en cours..."
    ↓
User hovers: Sees tooltip explaining why disabled
    ↓
Validation completes
    ↓
Button state: ENABLED (instant, < 100ms)
    ↓
User can click immediately
```

**Benefits**:
- ✅ Clear visual feedback (grayed out button)
- ✅ Explanatory tooltip on hover
- ✅ Instant re-enable when ready
- ✅ No unexpected popups

### Visual States

#### Context Menu (Right-Click)

**During Validation**:
```
┌─────────────────────────────────┐
│ Renommer                        │
│ Dupliquer                       │
├─────────────────────────────────┤
│ 🔄 Mettre à jour depuis Herald  │  ← GRAYED OUT
│   (disabled)                    │
├─────────────────────────────────┤
│ Gestion des armures             │
├─────────────────────────────────┤
│ Supprimer                       │
└─────────────────────────────────┘
```

**After Validation**:
```
┌─────────────────────────────────┐
│ Renommer                        │
│ Dupliquer                       │
├─────────────────────────────────┤
│ 🔄 Mettre à jour depuis Herald  │  ← CLICKABLE
└─────────────────────────────────┘
```

#### Main Window Buttons

**During Validation**:
```
[⏳ Vérification en cours...]  ← Status label
[🔄 Actualiser] ← Disabled     [🔍 Recherche] ← Disabled + Tooltip
```

**After Validation (Success)**:
```
[✅ Herald accessible]  ← Status label
[🔄 Actualiser] ← Enabled     [🔍 Recherche] ← Enabled
```

**After Validation (No Cookies)**:
```
[❌ Aucun cookie configuré]  ← Status label
[🔄 Actualiser] ← Disabled     [🔍 Recherche] ← Disabled
```

---

## Performance Considerations

### State Update Timing

**Measurements** (Windows 11, Intel i7):

| Event | Time from Validation Start |
|-------|----------------------------|
| Thread started | 0 ms |
| Buttons disabled | 5 ms |
| Validation result received | 2000-4000 ms |
| `update_eden_status()` called | 2000-4000 ms |
| Flag set to `False` | 2000-4000 ms |
| `_update_herald_buttons_state()` called | 2000-4000 ms |
| Buttons re-enabled | **2000-4000 ms** ✅ |
| Thread `finished` signal | 2500-5000 ms |

**Old Approach** (waiting for `isRunning() == False`):
- Buttons re-enabled: **4500-7000 ms** ❌ (2-3 seconds AFTER result)

**New Approach** (flag-based):
- Buttons re-enabled: **2000-4000 ms** ✅ (IMMEDIATELY with result)

### Memory Impact

**Overhead**: Negligible
- Flag: 1 boolean (1 byte)
- No additional threads or timers
- No performance degradation

---

## Debugging

### Log Messages

**Enable Debug Logs**: Settings → System → Debug Mode → ON

**Log Output** (`Logs/ui.log`):

```
2025-11-17 13:54:27 - UI - DEBUG - UI_STATE - _update_herald_buttons_state: validation_running=True
2025-11-17 13:54:27 - UI - DEBUG - UI_STATE - Menu contextuel action enabled=False
2025-11-17 13:54:27 - UI - DEBUG - UI_STATE - search_button désactivé
... [2-4 seconds] ...
2025-11-17 13:54:31 - UI - DEBUG - UI_STATE - _update_herald_buttons_state: validation_running=False
2025-11-17 13:54:31 - UI - DEBUG - UI_STATE - Menu contextuel action enabled=True
2025-11-17 13:54:31 - UI - DEBUG - UI_STATE - search_button réactivé
```

**What to Check**:
1. ✅ `validation_running=True` at startup
2. ✅ Action/button disabled messages
3. ✅ `validation_running=False` when result arrives
4. ✅ Action/button enabled messages
5. ⚠️ Time gap between validation result and button enable < 100ms

### Common Issues

#### Issue: "Buttons stay disabled forever"

**Symptom**: After validation completes, buttons never re-enable

**Possible Causes**:
1. `eden_validation_in_progress` never set to `False`
2. `_update_herald_buttons_state()` not called after validation
3. Signal connection missing (`status_updated` → `update_eden_status`)

**Debug Steps**:
```python
# Add breakpoint in update_eden_status()
def update_eden_status(self, accessible, message):
    print(f"DEBUG: Setting flag to False")  # Should print
    self.eden_validation_in_progress = False
    print(f"DEBUG: Calling _update_herald_buttons_state")  # Should print
    self._update_herald_buttons_state()
```

#### Issue: "Context menu action not grayed out"

**Symptom**: Right-click menu shows enabled action during validation

**Possible Causes**:
1. `update_from_herald_action` doesn't exist yet when first called
2. `show_context_menu()` not calling `_update_herald_buttons_state()`
3. QAction doesn't refresh visually

**Debug Steps**:
```python
# Check action exists
def show_context_menu(self, position):
    print(f"DEBUG: Action exists = {hasattr(self, 'update_from_herald_action')}")
    print(f"DEBUG: Action enabled = {self.update_from_herald_action.isEnabled()}")
    self._update_herald_buttons_state()
    self.context_menu.exec(...)
```

**Solution**: Ensure `show_context_menu()` calls `_update_herald_buttons_state()` before `exec()`.

#### Issue: "Delay between status and button enable"

**Symptom**: Status shows "✅ Herald accessible" but buttons stay disabled for 2-3 seconds

**Cause**: Using `thread.isRunning()` instead of flag

**Fix**: Verify `_update_herald_buttons_state()` checks `eden_validation_in_progress` flag:
```python
# CORRECT
is_validation_running = getattr(self, 'eden_validation_in_progress', False)

# WRONG
is_validation_running = self.eden_status_thread.isRunning()
```

---

## Testing Checklist

### Unit Tests

- [ ] `eden_validation_in_progress` flag set to `True` on `check_eden_status()`
- [ ] `eden_validation_in_progress` flag set to `False` in `update_eden_status()`
- [ ] `eden_validation_in_progress` flag set to `False` in `_on_validation_finished()`
- [ ] `_update_herald_buttons_state()` disables buttons when flag is `True`
- [ ] `_update_herald_buttons_state()` enables buttons when flag is `False`

### Integration Tests

- [ ] **Startup Test**: Launch app, verify buttons disabled during validation
- [ ] **Validation Success**: Verify buttons enabled when "✅ Herald accessible" appears
- [ ] **Validation Failure**: Verify search button stays disabled when "❌ No cookies"
- [ ] **Context Menu**: Right-click during validation, verify action grayed out
- [ ] **Character Sheet**: Open sheet during validation, verify buttons disabled
- [ ] **Timing Test**: Measure delay between status update and button enable (< 100ms)

### Manual Testing

```
Test 1: Startup Validation
1. Close application completely
2. Launch application
3. IMMEDIATELY hover over "🔍 Recherche" button
   ✅ Verify tooltip: "⏳ Validation Eden en cours..."
   ✅ Verify button grayed out
4. Wait for validation complete (2-4 seconds)
   ✅ Verify "✅ Herald accessible" appears
   ✅ Verify button becomes clickable IMMEDIATELY (< 1 second)

Test 2: Context Menu During Validation
1. Close application
2. Launch application
3. IMMEDIATELY right-click on a character
   ✅ Verify "🔄 Mettre à jour depuis Herald" is grayed out
4. Try clicking the disabled action
   ✅ Verify nothing happens (no popup)
5. Wait for validation complete
6. Right-click again
   ✅ Verify action is now enabled

Test 3: Character Sheet During Validation
1. Close application
2. Launch application
3. IMMEDIATELY double-click a character (open sheet)
   ✅ Verify "Update from Herald" button disabled
   ✅ Verify "Update RvR Stats" button disabled (if URL exists)
4. Hover over buttons
   ✅ Verify tooltips show "⏳ Validation Eden en cours..."
5. Wait for validation complete
   ✅ Verify buttons enable automatically

Test 4: No Cookies Scenario
1. Settings → Herald Eden → Clean Eden
2. Restart application
3. Wait for validation
   ✅ Verify "❌ Aucun cookie configuré" appears
   ✅ Verify search button STAYS disabled
   ✅ Verify refresh button enabled (can generate cookies)
```

---

## Migration Guide

### From v0.107 to v0.108

**Removed Code**:
```python
# DELETE THIS (main.py, dialogs.py)
if hasattr(self.ui_manager, 'eden_status_thread'):
    if self.ui_manager.eden_status_thread.isRunning():
        QMessageBox.warning(
            self,
            lang.get("update_blocked_title"),
            lang.get("update_blocked_validation")
        )
        return
```

**New Code**:
```python
# REPLACE WITH THIS
if hasattr(self.ui_manager, 'eden_validation_in_progress'):
    if self.ui_manager.eden_validation_in_progress:
        return  # Silent return, button is disabled
```

**Translation Keys to Remove**:
```json
{
  "update_blocked_title": "Mise à jour bloquée",  // DELETE
  "update_blocked_validation": "La validation...",  // DELETE
  "search_blocked_title": "Recherche bloquée",  // DELETE
  "search_blocked_validation": "La validation..."  // DELETE
}
```

**Translation Keys to Add**:
```json
{
  "herald_buttons": {
    "validation_in_progress": "⏳ Validation Eden en cours... Veuillez patienter"
  }
}
```

---

## Related Documentation

- [Chrome Profile Management](CHROME_PROFILE_TECHNICAL_EN.md) - Chrome profile conflict issue
- [Connect to Eden Herald](CONNECT_TO_EDEN_HERALD_EN.md) - Cookie generation workflow
- [Selenium Integration](CHARACTER_PROFILE_SCRAPER_EN.md) - Browser automation details

---

## Summary

**Key Improvements**:
1. ✅ **Proactive UI** - Buttons disabled BEFORE user can click
2. ✅ **Visual Feedback** - Tooltips explain disabled state
3. ✅ **Instant Response** - Flag-based tracking (not `isRunning()`)
4. ✅ **No Popups** - Silent protection with clear visual state
5. ✅ **Multi-Language** - Fully translated (FR/EN/DE)
6. ✅ **Thread-Safe** - No race conditions

**User Impact**:
- 🎯 Better UX - No more unexpected error dialogs
- ⚡ Faster Response - Buttons enable instantly (< 100ms instead of 2-3s)
- 📖 Clear Status - Always know why buttons are disabled

**Technical Benefits**:
- 🔒 Chrome profile protection maintained
- 🐛 Easier debugging (clear log messages)
- 🧪 Testable (flag-based state)
- 🌐 Internationalized (all tooltips translated)
