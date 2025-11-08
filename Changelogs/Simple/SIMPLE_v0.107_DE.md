# v0.107 - RvR/PvP Herald-Statistiken

## 📊 Neue Herald-Statistiken (8. Nov 2025)

### ⚔️ RvR-Bereich
✅ 🗼 Turmeroberungen: Anzahl eroberter Türme  
✅ 🏰 Festungseroberungen: Anzahl eroberter Festungen  
✅ 💎 Relikteroberungen: Anzahl eroberter Relikte  

### 🗡️ PvP-Bereich mit Reichsaufschlüsselung
✅ ⚔️ Solokills: Gesamt + Alb/Hib/Mid Aufschlüsselung  
✅ 💀 Todesstöße: Gesamt + Alb/Hib/Mid Aufschlüsselung  
✅ 🎯 Kills: Gesamt + Alb/Hib/Mid Aufschlüsselung  
✅ Reichsfarben (Rot/Grün/Blau)  
✅ Anzeige: `Kills: 4.715 → Alb: 1.811 | Hib: 34 | Mid: 2.870`  

### 🔄 Schaltfläche "Stats aktualisieren"
✅ Lädt RvR und PvP vom Herald  
✅ Verarbeitung teilweiser Updates  
✅ Erklärende Fehlermeldungen  
✅ Mehrsprachige Unterstützung (FR/EN/DE)  

## 🔧 Technische Verbesserungen

### 📥 Herald-Scraper
✅ Neues Modul `character_profile_scraper.py`  
✅ Scraping der Tabs Characters und PvP vom Herald  
✅ Verarbeitung von Tausendertrennzeichen (Leerzeichen, Kommas)  
✅ Extraktion nach Reich (Albion/Hibernia/Midgard)  

### 🐛 Korrekturen
✅ **Fix Zahlen-Parsing**: `"1 811"` → `clean_number()` entfernt Leerzeichen/Kommas  
✅ **Fix fehlende Stats**: Präzise Meldungen, teilweise Speicherung, Debug-HTML  
✅ **Charaktere ohne Stats**: Informative Meldungen statt Fehler  

### 🎨 Benutzeroberfläche
✅ Größenverstellbarer Charakterbogen  
✅ Organisierter Statistikbereich: RvR / PvP / PvE  
✅ Fett gedruckte Gesamtwerte  
✅ Eingerückte Reichsdetails mit Farben  
✅ 50/50 Layout (Informationen/Statistiken)  
✅ Vollständige Übersetzungen (FR/EN/DE)  

## 📦 Testskripte
✅ `Scripts/test_pvp_stats.py`: Isolierter PvP-Scraping-Test  
✅ `Scripts/test_rvr_captures.py`: Isolierter RvR-Scraping-Test  

## ⚠️ Hinweise
- Gültige Herald-Cookies erforderlich  
- Charakter Level 11+ empfohlen  
- Sichtbarer Browser minimiert (headless=False)
