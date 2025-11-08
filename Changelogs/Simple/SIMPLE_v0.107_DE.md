# v0.107 - Herald-Verbindungstest-Absturz-Fix

## 🔧 Kritischer Fix (8. Nov. 2025)
✅ **KRITISCHER FIX**: Herald-Verbindungstest-Absturz behoben  
✅ Sauberes WebDriver-Herunterfahren in allen Fehlerpfaden  
✅ `finally`-Block hinzugefügt zur Garantie des Cleanups  
✅ Gleiches Fix-Muster wie Herald-Such-Korrektur  
✅ `scraper`-Variable auf `None` initialisiert zur Fehlervermeidung  
✅ Keine Anwendungsabstürze mehr bei Verbindungsfehlern  

## 🧪 Test-Skript Hinzugefügt
✅ **Neues Skript**: `test_herald_connection_stability.py`  
✅ Testet Herald-Verbindungsstabilität (25 Tests standardmäßig)  
✅ Detaillierte Statistiken: Durchschnitt/Min/Max Zeit, Erfolgsquote  
✅ Absturz- und Fehlererkennung  
✅ Anpassbare Testanzahl  

## Technische Details
- **Problem**: Herald-Verbindungstest konnte Anwendung zum Absturz bringen wie die Suche
- **Ursache**: Kein `finally`-Block zum Schließen des Drivers, fehlende `close()`-Aufrufe in einigen Fehlerpfaden
- **Lösung**: Identisches Muster zum `search_herald_character()`-Fix
- **Auswirkung**: Stabile Anwendung, keine Abstürze während Verbindungstests
