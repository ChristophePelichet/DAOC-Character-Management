# v0.107 - RvR/PvP Herald Statistics

## 📊 New Herald Statistics (Nov 8, 2025)

### ⚔️ RvR Section
✅ 🗼 Tower Captures: Number of captured towers  
✅ 🏰 Keep Captures: Number of captured keeps  
✅ 💎 Relic Captures: Number of captured relics  

### 🗡️ PvP Section with Realm Breakdown
✅ ⚔️ Solo Kills: Total + Alb/Hib/Mid breakdown  
✅ 💀 Deathblows: Total + Alb/Hib/Mid breakdown  
✅ 🎯 Kills: Total + Alb/Hib/Mid breakdown  
✅ Realm colors (Red/Green/Blue)  
✅ Display: `Kills: 4,715 → Alb: 1,811 | Hib: 34 | Mid: 2,870`  

### 🔄 "Update Stats" Button
✅ Fetches RvR and PvP from Herald  
✅ Partial update handling  
✅ Explanatory error messages  
✅ Multilingual support (FR/EN/DE)  

## 🔧 Technical Improvements

### 📥 Herald Scraper
✅ New module `character_profile_scraper.py`  
✅ Scrapes Characters and PvP tabs from Herald  
✅ Handles thousand separators (spaces, commas)  
✅ Extraction by realm (Albion/Hibernia/Midgard)  

### 🐛 Fixes
✅ **Fix number parsing**: `"1 811"` → `clean_number()` removes spaces/commas  
✅ **Fix missing stats**: Precise messages, partial save, debug HTML  
✅ **Characters without stats**: Informative messages instead of errors  

### 🎨 Interface
✅ Resizable character sheet  
✅ Organized Statistics section: RvR / PvP / PvE  
✅ Bold total values  
✅ Indented realm details with colors  
✅ 50/50 layout (Information/Statistics)  
✅ Complete translations (FR/EN/DE)  

## 📦 Test Scripts
✅ `Scripts/test_pvp_stats.py`: Isolated PvP scraping test  
✅ `Scripts/test_rvr_captures.py`: Isolated RvR scraping test  

## ⚠️ Notes
- Requires valid Herald cookies  
- Character level 11+ recommended  
- Visible browser minimized (headless=False)
