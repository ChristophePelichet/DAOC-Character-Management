# v0.107 - Herald Connection Test Crash Fix

## 🔧 Critical Fix (Nov 8, 2025)
✅ **CRITICAL FIX**: Herald connection test crash resolved  
✅ Clean WebDriver shutdown in all error paths  
✅ `finally` block added to guarantee cleanup  
✅ Same fix pattern as Herald search correction  
✅ `scraper` variable initialized to `None` to prevent errors  
✅ No more application crashes during connection errors  

## 🧪 Test Script Added
✅ **New script**: `test_herald_connection_stability.py`  
✅ Tests Herald connection stability (25 tests by default)  
✅ Detailed statistics: average/min/max time, success rate  
✅ Crash and error detection  
✅ Customizable number of tests  

## Technical Details
- **Problem**: Herald connection test could crash application like search did
- **Cause**: No `finally` block to close driver, missing `close()` calls in some error paths
- **Solution**: Identical pattern to `search_herald_character()` fix
- **Impact**: Stable application, no crashes during connection tests
