# 🔍 Debug Utilities - Technical Documentation

**Version**: 2.0  
**Date**: December 2025  
**Last Updated**: December 24, 2025 (v0.109 Refactoring)  
**Components**: 
- `Functions/debug_freeze_tracker.py`
- `Functions/debug_logging_manager.py`
- `UI/ui_debug_window.py`
- `Tools/Debug-Log/tools_debug_log_editor.py`
- `Tools/Debug-Log/tools_debug_watch_logs.py`

**Related**: `main.py`, `UI/dialogs.py`, `Functions/`

---

## Table of Contents

1. [Overview](#overview)
2. [Debug Architecture](#debug-architecture)
3. [Freeze Tracker - Purpose & Implementation](#freeze-tracker---purpose--implementation)
4. [Logging Manager - Central Configuration](#logging-manager---central-configuration)
5. [Debug Window - Real-time Monitoring](#debug-window---real-time-monitoring)
6. [Log Source Editor - Code-level Log Management](#log-source-editor---code-level-log-management)
7. [Watch Logs Script - Tail Monitoring](#watch-logs-script---tail-monitoring)
8. [Logging Configuration](#logging-configuration)
9. [Usage Examples](#usage-examples)
10. [Troubleshooting](#troubleshooting)
11. [Performance Considerations](#performance-considerations)
12. [FAQ](#faq)

---

## Overview

This documentation covers all debug utilities available in the DAOC Character Management application for diagnosing, profiling, and troubleshooting issues during development.

### Available Debug Utilities

| Tool | Location | Purpose | Use Case |
|------|----------|---------|----------|
| **Freeze Tracker** | `Functions/debug_freeze_tracker.py` | Millisecond-precision timing for operation sequences | UI freeze investigation, performance bottleneck identification |
| **Logging Manager** | `Functions/debug_logging_manager.py` | Central logger configuration with contextual formatting | Unified logging across all modules |
| **Debug Window** | `UI/ui_debug_window.py` | Real-time log visualization with filtering and persistence | Live monitoring of application logs during development |
| **Log Source Editor** | `Tools/Debug-Log/tools_debug_log_editor.py` | Interactive editor for scanning and modifying logs in source code | Refactoring logs, changing loggers/levels, and managing actions |
| **Watch Logs** | `Tools/Debug-Log/tools_debug_watch_logs.py` | Real-time tail monitoring of log files | Quick log monitoring during development |

### Key Features

- ✅ **Millisecond-precision timing** using `time.perf_counter()`
- ✅ **Centralized logger configuration** with 5 main loggers (BACKUP, EDEN, UI, CHARACTER, ROOT)
- ✅ **Real-time log visualization** with filtering and sorting
- ✅ **Code-level log editor** for bulk log management
- ✅ **Contextual formatting** with logger names, levels, and custom actions
- ✅ **Color-coded output** for quick identification of issues
- ✅ **Global singleton pattern** for easy access across codebase
- ✅ **Minimal overhead** - focused tools for specific debugging tasks
- ✅ **Thread-safe logging** using Python's logging module
- ✅ **No external dependencies** beyond Python stdlib

---

## Debug Architecture

### System Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                    APPLICATION (main.py)                             │
└────────────────────────────────────────────────────────────────────┬─┘
                                                                      │
                ┌─────────────────────────────────────────────────────┘
                │
        ┌───────▼─────────────────────────────────────┐
        │  Logging Manager (debug_logging_manager.py) │
        │                                              │
        │  • setup_logging(extra_handlers)            │
        │  • get_logger(name)                         │
        │  • log_with_action(logger, level, msg)      │
        │  • ContextualFormatter                      │
        └────┬───────────────┬───────────────┬────────┘
             │               │               │
        ┌────▼─┐        ┌────▼─┐       ┌────▼──────┐
        │BACKUP│        │ EDEN │       │CHARACTER  │
        │Logger│        │Logger│       │Logger     │
        │      │        │      │       │           │
        └────┬─┘        └────┬─┘       └────┬──────┘
             │               │               │
             └───────────────┼───────────────┘
                             │
        ┌────────────────────┴────────────────────────┐
        │                                              │
    ┌───▼──────┐                                  ┌───▼──────┐
    │  UI       │                                  │  FILE    │
    │  WINDOW   │                                  │  HANDLER │
    │           │                                  │          │
    │ • Real-  │                                  │ • debug. │
    │   time   │                                  │   log    │
    │   filter │                                  │         │
    │ • Logger │                                  │ • Loggin │
    │   combo  │                                  │   Config │
    │ • Search │                                  │          │
    │           │                                  │          │
    └───────────┘                                  └──────────┘
        │                                              │
        │ (ui_debug_window.py)                        │ (Functions/)
        │                                              │
    ┌───▼────────────────────────────────────────────▼────────┐
    │                DEVELOPMENT PROCESS                       │
    │                                                          │
    │ 1. Run application with debug window open              │
    │ 2. Observe logs in real-time                           │
    │ 3. Use Log Source Editor to refactor logs             │
    │ 4. Use Watch Logs for file-based monitoring            │
    │ 5. Use Freeze Tracker for timing investigation         │
    └──────────────────────────────────────────────────────────┘
```

### Logger Hierarchy

```
ROOT Logger (logging.getLogger())
    │
    ├── BACKUP (get_logger(LOGGER_BACKUP))       → backup_manager.py, migration_manager.py
    ├── EDEN (get_logger(LOGGER_EDEN))           → eden_scraper.py, cookie_manager.py
    ├── EDEN_PERF (get_logger(LOGGER_EDEN_PERF)) → eden_scraper.py (performance metrics)
    ├── UI (get_logger(LOGGER_UI))               → item_model_viewer.py, UI modules
    └── CHARACTER (get_logger(LOGGER_CHARACTER)) → character_manager.py, character validators

All loggers use the ContextualFormatter which includes:
    Format: [timestamp] - LOGGER - LEVEL - ACTION - MESSAGE
```

---

## Freeze Tracker - Purpose & Implementation

### Primary Use Case: UI Freeze Investigation

The Debug Freeze Tracker was created to investigate and resolve a critical 4+ second UI freeze when closing the Herald search dialog after performing a search operation.

**Investigation Flow:**
```
Dialog opens
    ↓ [checkpoint: "Search dialog opened"]
User enters search terms
    ↓ [checkpoint: "Search query executed"]
Results displayed
    ↓ [checkpoint: "Results rendered"]
User closes dialog
    ↓ [checkpoint: "Dialog.accept() called"]
    ↓ [checkpoint: "Thread cleanup starting"]
    ↓ [checkpoint: "Thread cleanup finished"]
    ↓ [checkpoint: "Dialog destroyed"]
    → 🔴 CRITICAL 4058ms between checkpoints
```

### When to Use

**✅ Use Debug Freeze Tracker for:**
- Tracking sequence of operations (dialog open → search → close)
- Identifying which operation in a sequence is slow
- Measuring total elapsed time from start to end
- Finding performance regressions after code changes
- Profiling Qt signal/slot operations
- Diagnosing background thread operations

**❌ Don't Use For:**
- CPU profiling (use `cProfile` instead)
- Memory profiling (use `tracemalloc` instead)
- Line-by-line profiling (use `line_profiler` instead)
- Call graph analysis (use `graphviz` instead)

### Architecture

**File Location**: `Functions/debug_freeze_tracker.py`

**Size**: ~70 lines

**Dependencies**:
```python
import logging          # Standard library
import time            # Standard library
from datetime import datetime  # Standard library
```

**Exports**:
```python
freeze_tracker: FreezeTracker    # Global singleton instance
freeze_logger: Logger            # Configured logger instance
```

### FreezeTracker Class

#### `__init__()`

Initializes the freeze tracker with timing and logging setup.

```python
def __init__(self):
    self.start_time = time.perf_counter()
    self.last_checkpoint_time = self.start_time
```

**What it does:**
- Records absolute start time for total elapsed calculation
- Sets last checkpoint time to start (first checkpoint measures initialization time)
- Logs header with timestamp in ISO format
- Prints visual separator (80 equals signs)

**Output Example:**
```
================================================================================
FREEZE TRACKER START
Time: 2025-12-23T14:30:45.123456
================================================================================
```

#### `checkpoint(name: str) -> None`

Records a checkpoint with timing information relative to start and previous checkpoint.

```python
def checkpoint(self, name: str) -> None:
    current_time = time.perf_counter()
    elapsed_since_last = (current_time - self.last_checkpoint_time) * 1000
    total_elapsed = (current_time - self.start_time) * 1000
```

**Parameters:**
- `name` (str): Description of the checkpoint (max 55 chars recommended)

**Output Format:**
```
[total_ms] name:55_chars_max | Δ delta_ms warning_emoji
```

**Example Output:**
```
[  145ms] Dialog opened                                  | Δ   145ms
[  567ms] Search results received                      | Δ   422ms
[ 4625ms] Dialog close finished                        | Δ  4058ms 🔴 CRITICAL
```

### Checkpoint Thresholds

| Duration | Visual | Interpretation | Action |
|----------|--------|-----------------|--------|
| < 500ms | (none) | Normal, acceptable | ✅ No action |
| 500-1000ms | 🟡 | Slightly slow | ⚠️ Monitor |
| 1000-3000ms | 🟠 SLOW | Concerning | 🔍 Investigate |
| > 3000ms | 🔴 CRITICAL | Blocking freeze | 🚨 Must fix |

---

## Logging Manager - Central Configuration

### Module Structure

**File Location**: `Functions/debug_logging_manager.py`

**Purpose**: Centralized logger configuration and management

### Available Loggers

```python
LOGGER_ROOT = "ROOT"              # Default root logger
LOGGER_BACKUP = "BACKUP"          # Backup operations
LOGGER_EDEN = "EDEN"              # Eden scraper/API
LOGGER_EDEN_PERF = "EDEN_PERF"    # Eden performance logs
LOGGER_UI = "UI"                  # UI operations
LOGGER_CHARACTER = "CHARACTER"    # Character management

ALL_LOGGERS = [LOGGER_BACKUP, LOGGER_EDEN, LOGGER_EDEN_PERF, LOGGER_UI, LOGGER_CHARACTER]
```

### Key Functions

#### `setup_logging(extra_handlers=None)`

Configures the application's logger based on settings in config.json.

```python
def setup_logging(extra_handlers=None):
    """
    Configures the application's logger.
    Always logs CRITICAL and ERROR messages to file, even if debug mode is off.
    Optional extra_handlers (like for GUI window) can be provided.
    """
```

**Features:**
- Honors `system.debug_mode` setting in config.json
- Creates log directory if it doesn't exist
- Supports rotating file handlers (5MB max, 5 backups)
- Accepts extra handlers (e.g., for debug window)
- Uses ContextualFormatter for consistent formatting

#### `get_logger(name)`

Gets a logger with a specific name.

```python
logger = get_logger("backup")
logger.info("Backup started", extra={"action": "START"})
```

#### `log_with_action(logger, level, message, action="")`

Logs a message with an action field for better filtering.

```python
log_with_action(logger, "info", "Character updated", action="MODIFY")
```

#### `setup_eden_performance_logger()`

Configures a dedicated logger for Eden performance metrics.

```python
perf_logger = setup_eden_performance_logger()
# Creates Logs/eden_performance_YYYY-MM-DD.log
```

### ContextualFormatter

Provides enhanced formatting with:
- Timestamp (date and time)
- Logger name
- Level name
- Action (custom attribute)
- Message

**Format**: `[timestamp] - LOGGER - LEVEL - ACTION - MESSAGE`

**Example**:
```
2025-12-24 14:30:45,123 - EDEN - INFO - TEST - Connection to https://eden-daoc.net/herald?n=top_players&r=hib
```

---

## Debug Window - Real-time Monitoring

### Overview

The debug window provides real-time visualization of application logs with filtering and persistence capabilities.

**File Location**: `UI/ui_debug_window.py`

### Features

**Main Window**:
- Real-time log display with color-coded levels
- Split pane layout: Logs + Errors (left), Log File Reader (right)
- Logger filtering via dropdown menu
- Log level filtering (DEBUG, INFO, WARNING, ERROR, CRITICAL)

**Log File Reader**:
- Browse and select log files to monitor
- Real-time tail monitoring of selected file
- Clear display button

**Menu Bar**:
- Level menu: Set minimum log level for display
- Logger menu: Select which loggers to display

### Opening the Debug Window

**Method 1: Via Code**
```python
from UI.ui_debug_window import DebugWindow
debug_window = DebugWindow()
debug_window.show()
```

**Method 2: Via Settings**
- Enable `config.show_debug_window` in config.json
- Debug window opens automatically on application startup

### Logger Filtering

**Logger Dropdown** (Top Left):
```
🔍 Filter Logger: [All Loggers ▼]
                    • BACKUP
                    • CHARACTER
                    • EDEN
                    • UI
                    • ROOT
```

Select a logger to show only its messages.

### Log Level Filtering

**Menu → Level**:
- All (DEBUG and above)
- INFO and above
- WARNING and above
- ERROR and above
- CRITICAL only

### EdenDebugWindow

Specialized debug window for Eden-related operations:
- Syntax-highlighted log display
- Export logs to file
- Real-time monitoring of Eden scraper activity

---

## Log Source Editor - Code-level Log Management

### Purpose

Interactive tool for scanning, viewing, and modifying logs at the source code level.

**File Location**: `Tools/Debug-Log/tools_debug_log_editor.py`

### Key Features

- 🔍 Recursive scan of all Python files
- 📋 Interactive table with filtering (Logger, Level, Modified)
- ✏️ Editor with ComboBox for actions (history + auto-completion)
- ⌨️ Keyboard shortcuts (Enter, Ctrl+Enter)
- 💾 Direct save to source files
- 📂 Automatic loading of last project on startup

### Interface Layout

```
┌──────────────────────────────────────────────────────────┐
│  Toolbar: [🔍 Scan] [Logger: All▼] [Level: All▼]         │
│           [Display: All▼] [Search...] [📊 Stats]         │
│           [💾 Save Modifications]                         │
├────────────────────────┬─────────────────────────────────┤
│  Log Table (Left)      │  Editor (Right)                 │
│  • File, Line, Logger  │  • File Info                    │
│  • Level, Action       │  • Logger ComboBox              │
│  • Message, Modified   │  • Level Display                │
│                        │  • Action ComboBox              │
│                        │  • Message Editor               │
│                        │  • Original Code                │
│                        │  • Apply / Reset                │
└────────────────────────┴─────────────────────────────────┘
│ Status: Ready                                            │
└──────────────────────────────────────────────────────────┘
```

### Workflow

#### 1. Scan Project
```
Click [🔍 Scan Project] → Select folder → Scan starts
↓
Results displayed in table (File, Line, Logger, Level, Action, Message)
```

#### 2. Filter Results
```
Logger Filter: Select specific logger (BACKUP, EDEN, UI, CHARACTER, or All)
Level Filter: Select minimum log level
Display: Show all or modified-only logs
Search: Search in messages
```

#### 3. Edit Individual Log
```
Click a row in table → Editor populates with log details
↓
Change Logger, Action, or Message
↓
Click [✅ Apply] or press Enter
↓
Row highlights as "Modified" (column 7)
```

#### 4. Save Modifications
```
Review modified logs
↓
Click [💾 Save Modifications]
↓
Confirmation dialog shows preview
↓
Changes saved directly to source files
```

### Edit Features

**Change Logger**:
```python
# Before
logging.info("Character saved")

# Select logger: CHARACTER
# Result
log_with_action(CHARACTER, "info", "Character saved", action="")
```

**Add Action**:
```python
# Before
logger.info("Character saved")

# Enter Action: CREATE
# Select Logger: CHARACTER
# Result
log_with_action(CHARACTER, "info", "Character saved", action="CREATE")
```

**Change Message**:
```python
# Before
logger.info("Old message")

# New message: "Character created successfully"
# Result
logger.info("Character created successfully")
```

### Statistics

The editor automatically collects:
- Total logs found
- Logs by logger
- Logs by level
- Logs with/without actions
- Number of modified logs

---

## Watch Logs Script - Tail Monitoring

### Purpose

Real-time tail monitoring of log files for quick log inspection during development.

**File Location**: `Tools/Debug-Log/tools_debug_watch_logs.py`

### Features

- Real-time log file monitoring
- Keyword-based filtering
- Color-coded output
- Automatic file creation if missing

### Usage

```bash
python Tools/Debug-Log/tools_debug_watch_logs.py
```

**Output**:
```
======================================================================
REAL-TIME LOG FILE MONITORING
======================================================================

Monitored file: d:\...\Logs\debug.log

INSTRUCTIONS:
1. Leave this script running
2. Launch the application (F5 in VS Code)
3. Logs will appear here in real-time
4. Press Ctrl+C to stop monitoring

======================================================================
Waiting for logs...

>>> Application starting
>>> Populating tree [100%]
>>> Icon loading completed
... DEBUG: Processing item 1000 of 5000
!!! ERROR: Failed to load armory
>>> Pre-loading complete
```

### Keyword Filtering

The script filters logs by keywords:

```python
if any(keyword in line for keyword in [
    'REALM_ICONS', 'Verification', 'tree_realm_icons',
    'Populating tree', 'Icon loading', 'icon found', 
    'Pre-loading', 'Application starting'
]):
    print(f">>> {line}")  # Important
elif 'ERROR' in line or 'WARNING' in line:
    print(f"!!! {line}")  # Errors
elif 'DEBUG' in line:
    print(f"... {line}")  # Debug info
```

---

## Logging Configuration

### Logger Initialization

All loggers use a consistent setup:

```python
freeze_logger = logging.getLogger("freeze_tracker")
freeze_logger.setLevel(logging.INFO)

if not freeze_logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - FREEZE_TRACKER - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    freeze_logger.addHandler(console_handler)
```

### Log File Locations

**Debug Log**:
```
Logs/debug.log
- Configured in config.json: folders.logs
- Default: Logs/ directory next to executable
- Rotating file handler: 1MB per file, 5 backups
```

**Eden Performance Log**:
```
Logs/eden_performance_YYYY-MM-DD.log
- Created only if system.eden.enable_performance_logs = true
- Rotating file handler: 5MB per file, 10 backups
```

### Configuration Settings

**config.json**:
```json
{
  "system": {
    "debug_mode": true,
    "debug_window_visible": true,
    "eden": {
      "enable_performance_logs": false
    }
  },
  "folders": {
    "logs": "Logs"
  }
}
```

---

## Usage Examples

### Example 1: Debugging a Dialog Freeze

**Step 1**: Open Debug Window
```python
# Debug window auto-opens if enabled in config
# Or manually: UI → Debug Window menu
```

**Step 2**: Add Freeze Tracker Checkpoints
```python
from Functions.debug_freeze_tracker import freeze_tracker

dialog = HeraldSearchDialog(self)
freeze_tracker.checkpoint("Dialog created")

dialog.exec()
freeze_tracker.checkpoint("dialog.exec() returned")

# Cleanup operations
cleanup_threads()
freeze_tracker.checkpoint("Cleanup finished")
```

**Step 3**: Run Application and Observe
```
[  145ms] Dialog created                          | Δ   145ms
[  234ms] dialog.exec() returned                  | Δ    89ms
[ 4625ms] Cleanup finished                        | Δ  4391ms 🔴 CRITICAL
```

**Step 4**: Identify Bottleneck
```
The 4391ms gap is in cleanup_threads() - investigate that function
```

### Example 2: Refactoring Logs with Log Source Editor

**Step 1**: Run Log Source Editor
```bash
python Tools/Debug-Log/tools_debug_log_editor.py
```

**Step 2**: Scan Project
```
Click [🔍 Scan Project]
Select project root
Wait for scan to complete
```

**Step 3**: Filter Logs
```
Filter by Logger: EDEN
Show only logs with action: (empty)
```

**Step 4**: Add Actions
```
Select log: eden_scraper.py:125 - "Connection established"
Change Action to: "CONNECT"
Click [✅ Apply]
```

**Step 5**: Bulk Save
```
Click [💾 Save Modifications]
Review preview
Confirm
```

### Example 3: Real-time Log Monitoring

**Step 1**: Start Watch Script
```bash
python Tools/Debug-Log/tools_debug_watch_logs.py
```

**Step 2**: Launch Application
```bash
python main.py
```

**Step 3**: Observe Logs in Real-time
```
>>> Application starting
>>> Character loading started
>>> Pre-loading complete
>>> Populating tree [100%]
```

---

## Troubleshooting

### No Logs Appearing

**Cause**: `system.debug_mode` is false in config.json

**Solution**:
```json
{
  "system": {
    "debug_mode": true
  }
}
```

### Logs Not Reaching Debug Window

**Cause**: Extra handlers not passed to `setup_logging()`

**Solution**: Ensure debug window initializes handlers before setup_logging call:
```python
# In UI initialization
debug_window = DebugWindow(self)
handlers = [self.debug_window.log_handler]

# In main.py
setup_logging(extra_handlers=handlers)
```

### Log File Not Found

**Cause**: `folders.logs` path doesn't exist or is incorrect

**Solution**: Check config.json and ensure directory exists:
```bash
mkdir Logs
# Or configure in config.json:
# "folders.logs": "C:/path/to/logs"
```

### Freeze Tracker Output Not Showing

**Cause**: Logger level is too high

**Solution**: Freeze tracker uses INFO level, which should always display:
```python
freeze_logger.setLevel(logging.INFO)
freeze_logger.handlers[0].setLevel(logging.INFO)
```

---

## Performance Considerations

### Overhead per Checkpoint
- `time.perf_counter()` call: ~0.1 microseconds
- Arithmetic operations: ~0.05 microseconds
- Logger call (I/O): ~0.5-1 millisecond
- **Total**: ~1-2 milliseconds per checkpoint

### Memory Footprint
- `FreezeTracker` instance: ~200 bytes
- Logger and handlers: ~500-1000 bytes
- **Total**: ~1-2 KB (negligible)

### Best Practices

1. **Remove freeze tracker checkpoints** from production code
2. **Use conditional checkpoints** for optional profiling:
   ```python
   if os.getenv("DEBUG_FREEZE", "0") == "1":
       freeze_tracker.checkpoint("Operation name")
   ```
3. **Disable logging** if overhead is critical:
   ```python
   freeze_logger.setLevel(logging.CRITICAL)
   ```

---

## FAQ

### Q: Can I use these tools in production?

**A**: No. All debug tools are strictly for development/debugging.
- Remove `freeze_tracker.checkpoint()` calls before production
- Disable debug window before release
- Use standard Python logging only in production

### Q: Why use `perf_counter()` instead of `time.time()`?

**A**: `perf_counter()` is monotonic and unaffected by system clock adjustments:
- `time.time()`: Affected by NTP adjustments, ~1ms precision
- `time.perf_counter()`: Monotonic, ~0.1ns precision ✅

### Q: How do I export logs for analysis?

**A**: 
1. Logs are saved in `Logs/debug.log`
2. Use Log Source Editor to modify before saving
3. Use EdenDebugWindow Export feature
4. Manually copy logs from `Logs/` directory

### Q: Can I use multiple instances of FreezeTracker?

**A**: Yes! Create separate instances for different threads:
```python
worker_tracker = FreezeTracker()
worker_tracker.checkpoint("Worker phase 1")
```

### Q: How do I track performance regressions?

**A**: Compare freeze tracker output before/after code changes:
```bash
# Before change
[  567ms] Feature X completed | Δ   234ms

# After change
[  892ms] Feature X completed | Δ   325ms
# → 91ms regression detected
```

### Q: What's the difference between INFO and DEBUG levels?

**A**:
| Level | Shows | Use For |
|-------|-------|---------|
| DEBUG | All messages | Development, deep investigation |
| INFO | Messages + warnings | Normal operation, key events |
| WARNING | Warnings + errors | Production, important issues |
| ERROR | Errors + critical | Errors and critical problems |
| CRITICAL | Critical only | Emergency situations |

### Q: Can I filter logs by action?

**A**: Yes! Use Log Source Editor:
1. Scan project
2. Search box: Enter action keyword
3. Filter results by matching actions

---

## Version History

### v2.0 (December 24, 2025)
- **Refactored debug architecture** for better organization
- **Renamed tools** for consistent naming (tools_debug_* prefix)
- **Consolidated documentation** from 3 separate guides
- **Updated all docstrings** to English
- **Improved code quality** (100% Ruff compliance)
- **Enhanced tools**:
  - Debug window with Eden-specific capabilities
  - Improved log source editor with bulk operations
  - Real-time watch logs script

### v1.0 (December 2025)
- **Initial implementation** of freeze tracker for Herald search freeze investigation
- **Logging manager** with centralized configuration
- **Debug utilities** for profiling and troubleshooting

---

## Related Documentation

- [ARMORY_TECHNICAL_DOCUMENTATION.md](../Armory/ARMORY_TECHNICAL_DOCUMENTATION.md) - Armory system architecture
- [DAOC-Character-Manager README](../../README.md) - Project overview
- Code References:
  - [Functions/debug_freeze_tracker.py](../../Functions/debug_freeze_tracker.py)
  - [Functions/debug_logging_manager.py](../../Functions/debug_logging_manager.py)
  - [UI/ui_debug_window.py](../../UI/ui_debug_window.py)
  - [Tools/Debug-Log/tools_debug_log_editor.py](../../Tools/Debug-Log/tools_debug_log_editor.py)
  - [Tools/Debug-Log/tools_debug_watch_logs.py](../../Tools/Debug-Log/tools_debug_watch_logs.py)

---

## Future Enhancements

When adding new debug utilities:
1. Add module reference to "Available Debug Utilities" section
2. Create detailed section documenting the new utility
3. Include practical usage examples
4. Document integration with other utilities
5. Update this master documentation file
