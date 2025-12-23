# 🔍 Debug Utilities - Technical Documentation

**Version**: 1.0  
**Date**: December 2025  
**Last Updated**: December 23, 2025 (Initial Documentation)  
**Components**: `Functions/debug_freeze_tracker.py`, and other debug utilities  
**Related**: `main.py`, `UI/dialogs.py`, `Functions/`

---

## Table of Contents

1. [Overview](#overview)
2. [Available Debug Utilities](#available-debug-utilities)
3. [Freeze Tracker - Purpose & Use Cases](#freeze-tracker---purpose--use-cases)
4. [Freeze Tracker - Architecture](#freeze-tracker---architecture)
5. [Freeze Tracker - Core Components](#freeze-tracker---core-components)
6. [Implementation](#implementation)
7. [Logging Configuration](#logging-configuration)
8. [Usage Examples](#usage-examples)
9. [Checkpoint Thresholds](#checkpoint-thresholds)
10. [Troubleshooting](#troubleshooting)
11. [Performance Considerations](#performance-considerations)
12. [FAQ](#faq)

---

## Overview

This documentation covers all debug utilities available in the DAOC Character Management application for diagnosing, profiling, and troubleshooting issues during development.

### Available Debug Utilities

**1. Freeze Tracker** (`Functions/debug_freeze_tracker.py`)
   - Millisecond-precision timing for operation sequences
   - Automatic visual warnings for slow operations
   - Ideal for UI freeze investigation and performance bottleneck identification

### Key Features

- ✅ **Millisecond-precision timing** using `time.perf_counter()`
- ✅ **Checkpoint-based profiling** for tracking operation sequences
- ✅ **Automatic visual warnings** (🔴 CRITICAL, 🟠 SLOW, 🟡 Normal)
- ✅ **Color-coded output** for quick identification of bottlenecks
- ✅ **Global singleton** pattern for easy access across codebase
- ✅ **Minimal overhead** - focuses only on timing, no full stack traces
- ✅ **Thread-safe logging** using Python's logging module
- ✅ **Standalone module** - no external dependencies beyond stdlib

### Ideal For

- UI freeze investigation (dialog closes, button clicks, etc.)
- Performance bottleneck identification
- Async operation timing
- Thread operation profiling
- Signal/slot timing verification

---

## Freeze Tracker - Purpose & Use Cases

### Primary Use Case: Herald Search Freeze Investigation

The Debug Freeze Tracker was created to investigate and resolve a critical 4+ second UI freeze that occurred when closing the Herald search dialog after performing a search operation.

**Investigation Flow:**
```
Dialog opens search
    ↓ [checkpoint: "Search started"]
User enters search terms
    ↓ [checkpoint: "Search query executed"]
Results displayed
    ↓ [checkpoint: "Results shown"]
User closes dialog
    ↓ [checkpoint: "Dialog.accept() called"]
    ↓ [checkpoint: "cleanup started"]
    ↓ [checkpoint: "thread cleanup"]
    ↓ ... [multiple sub-checkpoints]
    ↓ [checkpoint: "Dialog closed"]
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

---

## Freeze Tracker - Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                   DEBUG FREEZE TRACKER                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
        ┌───────▼────────┐        ┌────────▼──────┐
        │ FreezeTracker  │        │  freeze_logger│
        │    Class       │        │   (Singleton) │
        └───────┬────────┘        └───────────────┘
                │
        ┌───────▼────────────────┐
        │  checkpoint(name) call │
        └───────┬────────────────┘
                │
        ┌───────┴────────────────────────────┐
        │      Timing Calculation             │
        └────┬────────────────────────────────┘
             │
        ┌────▼──────────────────────────────┐
        │  Visual Warning Assessment         │
        │  • 🔴 > 3000ms (CRITICAL)         │
        │  • 🟠 > 1000ms (SLOW)              │
        │  • 🟡 > 500ms (WARNING)            │
        │  • (none) < 500ms (OK)             │
        └────┬──────────────────────────────┘
             │
        ┌────▼──────────────────────────────┐
        │  Log Message with Formatting       │
        │  [total_ms] name | Δ delta_ms⚠️  │
        └────────────────────────────────────┘
```

### Class Structure

```python
FreezeTracker
├── __init__()
│   ├── self.start_time (time.perf_counter)
│   └── self.last_checkpoint_time (time.perf_counter)
│
└── checkpoint(name: str) -> None
    ├── Measure time since last checkpoint
    ├── Calculate total elapsed
    ├── Assess warning level
    └── Log formatted message

freeze_tracker: FreezeTracker (Global singleton instance)
freeze_logger: Logger (Configured with StreamHandler)
```

---

## Freeze Tracker - Core Components

### FreezeTracker Class

**Purpose**: Main timing and tracking class

**Attributes:**
```python
start_time: float              # Absolute start time (perf_counter)
last_checkpoint_time: float    # Time of last checkpoint call
```

**Methods:**

#### `__init__()`

Initializes the freeze tracker with timing and logging setup.

```python
def __init__(self):
    self.start_time = time.perf_counter()
    self.last_checkpoint_time = self.start_time
```

**What it does:**
- Records absolute start time for total elapsed calculation
- Sets last checkpoint time to start (first checkpoint will measure initialization time)
- Logs header with timestamp and timestamp in ISO format
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
    
    self.last_checkpoint_time = current_time
    # ... warning assessment and logging
```

**Parameters:**
- `name` (str): Description of the checkpoint (max 55 chars recommended for formatting)

**Calculations:**
- **elapsed_since_last**: Time in milliseconds since previous checkpoint (Δ)
- **total_elapsed**: Total time in milliseconds since tracker initialization
- **warning level**: Visual indicator based on elapsed_since_last duration

**Output Format:**
```
[total_ms] name:55_chars_max | Δ delta_ms warning_emoji
```

**Example Output:**
```
[  145ms] Search dialog.exec() started                      | Δ   145ms
[  234ms] SearchThread.run() in background                 | Δ    89ms
[  567ms] Search results received                          | Δ   333ms
[ 4625ms] Dialog close initiated                           | Δ  4058ms 🔴 CRITICAL 4058ms
```

---

## Implementation

### Module Structure

**File Location**: `Functions/debug_freeze_tracker.py`

**Size**: Minimal (~70 lines)

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

### Logging Configuration

The module sets up its own logger to ensure visibility regardless of application debug mode.

**Logger Setup:**
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

**Features:**
- Logger name: `"freeze_tracker"` (appears in log messages)
- Level: `INFO` (shows even if application is not in debug mode)
- Handler: `StreamHandler` (prints to console/terminal)
- Format: `timestamp - FREEZE_TRACKER - LEVEL - message`

**Why This Approach:**
- ✅ Independent of application's main logger configuration
- ✅ Always visible in terminal output
- ✅ Doesn't require debug mode to be enabled
- ✅ Handler check prevents duplicate logging if imported multiple times

---

## Logging Configuration

### Logger Initialization

```python
freeze_logger = logging.getLogger("freeze_tracker")
freeze_logger.setLevel(logging.INFO)
```

**Logger Name**: `"freeze_tracker"` - Allows filtering in logging config if needed

**Log Level**: `INFO` - Intentionally set to INFO (not DEBUG) to ensure visibility even when application is running in production/non-debug mode

### StreamHandler Configuration

```python
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - FREEZE_TRACKER - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)
freeze_logger.addHandler(console_handler)
```

**Handler**: Streams to stdout (console/terminal)

**Formatter Pattern**:
- `%(asctime)s` - Timestamp with millisecond precision
- `FREEZE_TRACKER` - Module identifier (literal string)
- `%(levelname)s` - Log level (INFO, WARNING, etc.)
- `%(message)s` - The actual checkpoint/header message

**Example Output**:
```
2025-12-23 14:30:45,123 - FREEZE_TRACKER - INFO - [  145ms] Dialog opened | Δ   145ms
2025-12-23 14:30:45,234 - FREEZE_TRACKER - INFO - [ 4625ms] Dialog closed | Δ  4058ms 🔴 CRITICAL 4058ms
```

### Handler Deduplication

```python
if not freeze_logger.handlers:
    # ... add handler ...
```

**Purpose**: Prevents duplicate handlers if module is imported multiple times

**Scenario**: If `debug_freeze_tracker` is imported in multiple places or reloaded, this prevents multiple StreamHandlers from being added, which would cause duplicate log lines.

---

## Usage Examples

### Basic Setup - Single Sequence

**Scenario**: Track time for a dialog open → operation → close sequence

```python
from Functions.debug_freeze_tracker import freeze_tracker

# Tracker auto-initializes on import
freeze_tracker.checkpoint("Dialog.exec() starting")

# ... perform operation ...

freeze_tracker.checkpoint("Search query completed")

# ... more operations ...

freeze_tracker.checkpoint("Dialog accepted, cleanup starting")
freeze_tracker.checkpoint("Cleanup finished, returning to main")
```

**Output**:
```
================================================================================
FREEZE TRACKER START
Time: 2025-12-23T14:30:45.123456
================================================================================
2025-12-23 14:30:45,145 - FREEZE_TRACKER - INFO - [  145ms] Dialog.exec() starting                | Δ   145ms
2025-12-23 14:30:45,567 - FREEZE_TRACKER - INFO - [  422ms] Search query completed                | Δ   277ms
2025-12-23 14:30:45,890 - FREEZE_TRACKER - INFO - [  745ms] Dialog accepted, cleanup starting   | Δ   323ms
2025-12-23 14:30:49,948 - FREEZE_TRACKER - INFO - [ 4803ms] Cleanup finished, returning to main | Δ  4058ms 🔴 CRITICAL 4058ms
```

### Diagnosing Herald Freeze Issue

**Scenario**: Track the exact point where UI freezes during dialog close

```python
# In main.py open_herald_search() function
from Functions.debug_freeze_tracker import freeze_tracker

dialog = HeraldSearchDialog(self)
freeze_tracker.checkpoint("Herald dialog created")

dialog.exec()
freeze_tracker.checkpoint("dialog.exec() returned")

freeze_tracker.checkpoint("About to call cleanup")
# ... cleanup code ...
freeze_tracker.checkpoint("Cleanup finished")
```

**When Freeze Occurs**:
- If 4+ second gap appears between checkpoints, that segment is the bottleneck
- Example: Gap between "About to call cleanup" and "Cleanup finished" = problem is in cleanup code

### Multi-Phase Tracking

**Scenario**: Complex operation with multiple sub-phases

```python
freeze_tracker.checkpoint("Phase 1: Database query starting")
# ... database operation ...

freeze_tracker.checkpoint("Phase 2: Data processing")
# ... process results ...

freeze_tracker.checkpoint("Phase 3: UI update")
# ... update UI elements ...

freeze_tracker.checkpoint("Phase 4: Cleanup")
# ... cleanup resources ...

freeze_tracker.checkpoint("Phase 5: Complete")
```

**This Reveals**:
- Which phase is slow
- Whether total operation meets performance targets
- Non-obvious bottlenecks (e.g., Phase 2 takes 85% of total time)

### Integration with Dialog Operations

**In `UI/dialogs.py` HeraldSearchDialog:**

```python
class HeraldSearchDialog(QDialog):
    def accept(self):
        """Handle dialog close"""
        from Functions.debug_freeze_tracker import freeze_tracker
        freeze_tracker.checkpoint("HeraldSearchDialog.accept() called")
        super().accept()
        freeze_tracker.checkpoint("HeraldSearchDialog.accept() super() returned")
    
    def closeEvent(self, event):
        """Handle window close"""
        from Functions.debug_freeze_tracker import freeze_tracker
        freeze_tracker.checkpoint("HeraldSearchDialog.closeEvent() called")
        super().closeEvent(event)
        freeze_tracker.checkpoint("HeraldSearchDialog.closeEvent() super() returned")
```

---

## Checkpoint Thresholds

### Visual Warning System

The freeze tracker automatically assesses checkpoint duration and provides visual feedback:

| Duration | Visual Indicator | Interpretation | Action |
|----------|------------------|-----------------|--------|
| < 500ms  | (none) | Normal, acceptable | ✅ No action needed |
| 500-1000ms | 🟡 | Slightly slow, monitor | ⚠️ Note for regression testing |
| 1000-3000ms | 🟠 SLOW | Concerning, investigate | 🔍 May impact UX |
| > 3000ms | 🔴 CRITICAL | Blocking freeze | 🚨 Must fix |

### Threshold Rationale

**500ms threshold** (Yellow warning):
- Represents perceptible latency (human reaction time ~200-500ms)
- UI should feel responsive; > 500ms feels sluggish

**1000ms threshold** (Orange SLOW):
- One full second of unresponsiveness
- User experience noticeably affected
- Common threshold for "feels like a freeze"

**3000ms threshold** (Red CRITICAL):
- Three+ seconds is absolutely unacceptable
- Appears as application hang/crash to user
- Must be investigated and fixed

### Example Output with All Levels

```
[  145ms] Normal operation                          | Δ   145ms
[  234ms] Still normal                              | Δ    89ms
[  567ms] Getting slower                            | Δ   333ms 🟡 333ms
[  234ms] Back to normal                            | Δ  1267ms 🟠 SLOW 1267ms
[ 4625ms] Critical freeze detected                  | Δ  4391ms 🔴 CRITICAL 4391ms
```

---

## Troubleshooting

### Duplicate Log Messages

**Problem**: Checkpoint output appears twice in console

**Cause**: Logger imported and initialized multiple times

**Solution**: Module uses `if not freeze_logger.handlers:` check to prevent duplicates, but if duplicates still appear:
```python
# Reset handlers (if reimporting in same session)
freeze_logger.handlers = []
```

### No Output Appearing

**Problem**: Checkpoints are called but nothing prints

**Cause**: 
1. Logger level set to DEBUG but handlers level is INFO
2. No handlers configured (though code prevents this)
3. Output redirected elsewhere

**Solution**:
```python
# Verify logger is set up correctly
import logging
logger = logging.getLogger("freeze_tracker")
print(f"Logger level: {logger.level}")
print(f"Handlers: {logger.handlers}")
print(f"Handler levels: {[h.level for h in logger.handlers]}")
```

### Inaccurate Timing

**Problem**: Reported times don't match elapsed time in terminal output

**Cause**: `time.perf_counter()` uses system monotonic clock, which has different precision on different OS:
- Windows: ~0.1ms precision (depends on system timer)
- Linux: ~1ns precision
- macOS: ~1ns precision

**Note**: This is acceptable for our use case (identifying freezes > 500ms). Precision is sufficient.

### Timestamps Out of Sync

**Problem**: Log timestamps don't align with actual time between calls

**Cause**: `%(asctime)s` timestamp and `perf_counter()` measurements can drift because:
- `asctime` uses system clock
- `perf_counter()` uses monotonic clock
- They're independent measurements

**This is expected behavior** - `perf_counter()` is more reliable for timing, timestamps are for reference only.

---

## Performance Considerations

### Overhead

The Debug Freeze Tracker is designed to have minimal overhead:

**Per Checkpoint Call:**
- `time.perf_counter()` call: ~0.1 microseconds
- Arithmetic operations: ~0.05 microseconds
- Logger call: ~0.5-1 millisecond (I/O bound, depends on handler)
- **Total**: ~1-2 milliseconds per checkpoint (dominated by logging I/O)

**Overall**: Acceptable for profiling but would skew results if thousands of checkpoints are added

### Memory Footprint

- `FreezeTracker` instance: ~200 bytes
- Logger and handlers: ~500-1000 bytes
- **Total**: ~1-2 KB

**Note**: Negligible for application

### When to Disable

If freeze tracker adds measurable overhead to your investigation:

**Option 1: Comment out checkpoints** (simplest)
```python
# freeze_tracker.checkpoint("This operation")  # Disabled
```

**Option 2: Conditional checkpoints**
```python
DEBUG_FREEZE = os.getenv("DEBUG_FREEZE", "0") == "1"
if DEBUG_FREEZE:
    freeze_tracker.checkpoint("Operation name")
```

**Option 3: Disable logging temporarily**
```python
freeze_logger.setLevel(logging.CRITICAL)  # Only critical messages
freeze_logger.handlers[0].setLevel(logging.CRITICAL)
```

---

## FAQ

### Q: Can I use this for production code?

**A**: No. Debug Freeze Tracker is intended **exclusively for development/debugging**. 

- Remove all `freeze_tracker.checkpoint()` calls before production
- Logging overhead not acceptable for production
- Intended for problem diagnosis during development

### Q: Should I commit debug code to git?

**A**: Only the `debug_freeze_tracker.py` module itself, **NOT** the checkpoint calls scattered in code.

- Module: ✅ Commit to repository (utility for future debugging)
- Checkpoint calls: ❌ Remove before committing (use for investigation only)

See the v0.109 freeze issue investigation for reference - module is committed but checkpoint calls were removed.

### Q: Why not use Python's built-in `timeit` module?

**A**: Different purposes:

| Tool | Purpose | Best For |
|------|---------|----------|
| `timeit` | Measure function execution time (multiple runs, statistics) | Benchmarking function performance |
| Debug Freeze Tracker | Track timing of sequence of operations (single run) | Finding bottlenecks in complex sequences |

Use `timeit` for performance benchmarking, use Freeze Tracker for profiling event sequences.

### Q: Can I use this with multi-threaded code?

**A**: The freeze tracker itself is thread-safe (uses standard logging), but checkpoint times will include time from other threads.

**Better approach for multi-threaded code:**
- Create separate `FreezeTracker` instances per thread
- Each thread has its own start_time and checkpoint tracking
- No cross-thread interference

**Example:**
```python
# In worker thread
worker_tracker = FreezeTracker()  # New instance for this thread
worker_tracker.checkpoint("Worker phase 1")
# ... thread work ...
worker_tracker.checkpoint("Worker phase 2")
```

### Q: Why `perf_counter()` instead of `time.time()`?

**A**: `perf_counter()` is monotonically increasing and not affected by system clock adjustments:

| Clock | Affected By | Precision | Use Case |
|-------|------------|-----------|----------|
| `time.time()` | System clock adjustments, NTP | ~1ms | Wall-clock time |
| `time.perf_counter()` | None (monotonic) | ~0.1-1ns | Performance timing ✅ |

We use `perf_counter()` because we care about elapsed time, not absolute time.

### Q: How do I interpret the checkpoint name format?

**A**: Names are right-aligned in a 55-character field for readability:

```python
f"[{total_elapsed:7.0f}ms] {name:55s} | Δ {elapsed_since_last:7.0f}ms{warning}"
```

**Formatting:**
- `{:55s}` - Right-pad name to 55 chars with spaces
- `{:7.0f}ms` - Right-align milliseconds in 7-char field

**Benefit**: Columns line up for easy visual scanning

```
[  145ms] Dialog opened                                  | Δ   145ms
[  567ms] Search completed                              | Δ   422ms
[ 4625ms] Dialog cleanup (LONG)                         | Δ  4058ms 🔴 CRITICAL
```

---

## Version History

### v1.0 (December 2025)
- **Initial implementation** for Herald search dialog freeze investigation
- **Features**: Checkpoint-based timing with visual warnings
- **Use Case**: Identified that `_stop_search_thread_async()` was blocking in event loop (4058ms freeze)
- **Resolution**: Implemented async dialog destruction using `DialogDestructionWorker`
- **Impact**: Eliminated 4+ second UI freeze when closing Herald search dialog

### Deployment Notes

- Module: `Functions/debug_freeze_tracker.py`
- Usage: Preserved as utility for future debugging needs
- Status: Available for use but checkpoint calls removed from production code

---

## Related Documentation

- [ARMORY_TECHNICAL_DOCUMENTATION.md](../Armory/ARMORY_TECHNICAL_DOCUMENTATION.md) - Armory system architecture
- [DAOC-Character-Manager README](../../README.md) - Project overview
- Code Reference: [Functions/debug_freeze_tracker.py](../../Functions/debug_freeze_tracker.py)

---

## Future Debug Utilities

This documentation will be expanded to include additional debug utilities as they are created:

- Additional performance profiling tools
- Memory leak detectors
- Thread interaction tracers
- Signal/slot debugging utilities
- Database query profilers

When adding new debug utilities:
1. Add module reference to "Available Debug Utilities" section
2. Create detailed section documenting the new utility
3. Include practical usage examples
4. Document integration with other utilities
