# v0.106 - Logging-System, Cookie-Sicherung & Verbesserungen

## 🍪 Eden-Cookies-Sicherung (NEU)
✅ Automatische tägliche Cookie-Sicherung beim Start  
✅ Dedizierter "Cookies Eden" Abschnitt im Sicherungsfenster  
✅ Gleiche Optionen wie Characters: Komprimierung, Speicherlimit  
✅ Schaltfläche "Jetzt sichern" für sofortige erzwungene Sicherung  
✅ Schaltfläche "Ordner öffnen" für direkten Ordnerzugriff  
✅ Automatische Aktualisierung nach Sicherung  
✅ Anzeige der Sicherungsanzahl und des letzten Sicherungsdatums  

## 🔧 Neues Logging-System
✅ Einheitliches Format: `LOGGER - LEVEL - ACTION - MESSAGE`  
✅ BACKUP-Logger: alle Backup-Modul-Logs getaggt  
✅ EDEN-Logger: alle Eden-Scraper-Logs getaggt  
✅ Standardisierte Aktionen für jedes Modul  
✅ Verbessertes Debug-Fenster mit Logger-Filter  

## 🛠️ Log Source Editor (Neues Tool)
✅ Quellcode-Scanner zum Finden aller Logs  
✅ Interaktiver Editor (Tabelle + Bearbeitungspanel)  
✅ Erkennt `logger.xxx()` und `log_with_action()`  
✅ Action-ComboBox mit Verlauf und Auto-Vervollständigung  
✅ Tastaturkürzel (Enter, Strg+Enter)  
✅ Filter nach Logger, Level, geänderte Logs  
✅ Direktes Speichern in Quelldateien  
✅ Merkt sich das zuletzt bearbeitete Projekt  
✅ Echtzeit-Statistiken  

## 🔍 Eden-Scraping-Korrektionen
✅ Korrektur des Eden-Cookies-Speicherpfads (PyInstaller-Korrektur)  
✅ Auto-Update beim Charakterimport  
✅ Konfigurierbarer Herald-Cookies-Ordner  

## 🧬 Herald-Authentifizierung - Vereinfachte & Zuverlässige Erkennung
✅ Authentifizierungserkennung basierend auf einzelnem definitivem Kriterium  
✅ Fehlermeldung 'The requested page "herald" is not available.' = NICHT VERBUNDEN  
✅ Abwesenheit der Fehlermeldung = VERBUNDEN (kann Daten scrapen)  
✅ Kohärente Logik zwischen `test_eden_connection()` und `load_cookies()`  
✅ Ungültige Cookies korrekt erkannt und gemeldet  
✅ Tests mit etwa 58 Herald-Suchergebnissen validiert  

## 🎛️ Herald-Schaltflächen-Steuerung
✅ "Aktualisieren" und "Herald-Suche" Schaltflächen automatisch deaktiviert  
✅ Deaktiviert, wenn kein Cookie erkannt wird  
✅ Deaktiviert, wenn Cookies abgelaufen sind  
✅ Schaltflächenzustand mit Verbindungsstatus synchronisiert  
✅ Klare Benutzer-Nachricht: "Kein Cookie erkannt"  

## 📝 Backup-Modul
✅ 46+ Logs mit klaren Aktionen getaggt  
✅ Aktionen: INIT, CHECK, TRIGGER, RETENTION, ZIP, RESTORE, etc.  
✅ Debug-Logs für vollständige Rückverfolgbarkeit  
✅ Vollständige Unterstützung für Cookie-Sicherung mit Aufbewahrungsrichtlinien  

## 🎨 Benutzeroberfläche - Sicherungsfenster
✅ Nebeneinander-Layout: Characters und Cookies Eden  
✅ Vergrößertes Fenster für beide Abschnitte (1400x800)  
✅ Intelligente Aktualisierung der Info nach Sicherung  
✅ "Ordner öffnen" Schaltflächen für direkten Zugriff (Windows/Mac/Linux)  

## 🎨 Benutzeroberfläche - Allgemein
✅ Korrektur der Spaltenkonfiguration (12 Spalten)  
✅ Einheitliche Verzeichnis-Labels ("Verzeichnis")  
✅ Verbesserte Pfadanzeige  
✅ Robustes Diagnosesystem für unerwartete Abstürze  
✅ **Funktionale Reich-Sortierung** (RealmSortProxyModel hinzugefügt)  
✅ **Optimierte Herald-URL-Spaltenbreite** (120px Minimum)  
✅ **Proxy-Modell-Index-Zuordnung** für sortierte Operationen  
✅ **Speichern-Schaltfläche Charakterblatt** schließt nicht mehr  
✅ **Herald-Schaltflächen einheitliche Größe** im Charakterblatt  
✅ **Hauptfenster-Layout Redesign** mit Währungssektion  
✅ **Herald-Statusleisten-Optimierungen** (750px Schaltflächen × 35px)  
✅ **Charakterblatt-Redesign** (Statistiken-Umbennung, Widerstands-Taste entfernt, Rüstung-Manager verlegt)  

## 🐛 Fehlerbehebungen - PyInstaller .exe Stabilität
✅ **sys.stderr/stdout None Behandlung** - Noconsole-Crash behoben (AttributeError bei flush)  
✅ **Herald-Verbindungstest-Schutz** - Stumme Abstürze mit vollständigem Fehler-Logging verhindert  
✅ **Selenium-Import-Fehlerbehandlung** - Explizite Fehlermeldungen für fehlende Module  
✅ **Driver-Bereinigungsschutz** - Sicheres driver.quit() mit None-Prüfungen  
✅ **Thread-Exception-Abfangen** - EdenStatusThread-Fehler stürzen Anwendung nicht mehr ab  
✅ **Vollständiges Traceback-Logging** - Alle Fehler in debug.log protokolliert für Fehlerbehebung  

## 🧹 Repository-Bereinigung
✅ Löschung von 13 temporären Debug-Skripten  
✅ Löschung von 3 Debug-HTML-Dateien  
✅ Sauberes und wartbares Repository  
✅ Leistungsoptimierung  

## 📚 Dokumentation
✅ Bereinigung und Umstrukturierung des CHANGELOGs-Systems
