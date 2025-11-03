# CHANGELOG v0.106 - Logging-System, Cookie-Sicherung & Verbesserungen

**Datum**: 2025-11-01  
**Version**: 0.106

---

## 🔧 Neues Logging-System

### Einheitliches Format mit ACTION

- **Vorher**: Inkonsistentes Format, schwierig zu filtern und zu analysieren
- **Jetzt**: Standardisiertes Format `LOGGER - LEVEL - ACTION - MESSAGE`
- **Beispiel**: `2025-11-01 14:30:00 - BACKUP - INFO - INIT - BackupManager initialized`

**Vorteile**:
- Einfaches Filtern nach Logger (BACKUP, EDEN, UI, CHARACTER, ROOT)
- Klare Aktionen für jede Operation
- Vollständige Rückverfolgbarkeit des Ausführungsablaufs
- Kompatibel mit Log-Analyse-Tools

**Implementierung**:
- Neuer `ContextualFormatter` in `logging_manager.py`
- Aktionshandhabung: Verwendet `extra={"action": "VALUE"}` in Logs
- Fallback: Zeigt "-" an, wenn keine Aktion angegeben ist
- Hilfsfunktion: `log_with_action(logger, level, message, action="XXX")`

### BACKUP Logger - Backup-Modul

- **Geänderte Dateien**: `backup_manager.py`, `migration_manager.py`
- **46+ Logs getaggt** mit klaren Aktionen

**Standardisierte Aktionen**:
- `INIT` - BackupManager-Initialisierung
- `DIRECTORY` - Backup-Verzeichnis-Erstellung/Überprüfung
- `CHECK` - Überprüfung, ob Backup heute notwendig ist
- `STARTUP` - Automatisches Backup beim Start
- `TRIGGER` - Automatischer Backup-Trigger
- `AUTO_TRIGGER` - Auto-Backup-Start
- `AUTO_PROCEED` - Auto-Backup-Fortsetzung
- `AUTO_BLOCKED` - Auto-Backup blockiert (bereits durchgeführt)
- `MANUAL_TRIGGER` - Manuelles Backup ausgelöst
- `ZIP` - ZIP-Komprimierung im Gange
- `RETENTION` - Aufbewahrungsverwaltung (Löschen alter Backups)
- `SCAN` - Scan existierender Backups
- `DELETE` - Backup-Löschung
- `INFO` - Backup-Information
- `RESTORE` - Backup-Wiederherstellung
- `ERROR` - Allgemeine Fehler

**Ebenen**: DEBUG (Details), INFO (Fortschritt), WARNING (Warnungen), ERROR (Fehler)

**Rückverfolgbarkeit**: Detaillierte Logs für jeden Backup-Prozessschritt

### EDEN Logger - Herald-Scraper

- **Datei**: `eden_scraper.py`
- **Aktionen**: INIT, COOKIES, SCRAPE, SEARCH, PARSE, TEST, CLOSE, CLEANUP, ERROR
- **Alle Logs** verwenden jetzt `extra={"action": "XXX"}`

---

## 🛠️ Log Source Editor - Neues Entwicklerwerkzeug

### Überblick

- **Datei**: `Tools/log_source_editor.py` (975 Zeilen)
- **Zweck**: Logs direkt im Quellcode VOR Kompilierung bearbeiten
- **Framework**: PySide6 (Qt6) mit vollständiger GUI

### Quellcode-Scanner

- **Technologie**: Asynchroner QThread ohne UI-Blockierung
- **Muster 1**: Erkennt `logger.info()`, `self.logger.debug()`, `module_logger.warning()`
- **Muster 2**: Erkennt `log_with_action(logger, "info", "message", action="TEST")`

**Intelligente Erkennung**:
- Extrahiert Logger-Namen aus Dateinamen
- Parsing von `get_logger(LOGGER_XXX)`
- Parsing von `setup_logger("LOGGER_NAME")`

**Parsing**:
- Aktionsextraktion aus `action="XXX"` oder `extra={"action": "XXX"}`
- Nachrichtextraktion (unterstützt f-Strings, normale Strings, Konkatenationen)
- Ebenenabfrage (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Benutzeroberfläche

**Hauptlayout**:
- **Links**: Tabelle gefundener Logs (schreibgeschützt)
  - Spalten: Datei, Zeile, Logger, Ebene, Aktion, Nachricht, Geändert
  - Schutz: `setEditTriggers(QTableWidget.NoEditTriggers)`
- **Rechts**: Bearbeitungsfeld
  - Datei/Zeile/Logger/Ebene (Anzeige)
  - Aktion: Bearbeitbares ComboBox mit Verlauf
  - Nachricht: Multi-Zeilen-QTextEdit
  - Originalcode: Schreibgeschütztes QTextEdit
  - Schaltflächen: Anwenden, Zurücksetzen

**Symbolleiste**:
- 🔍 Projekt scannen
- Filter: Logger (Dropdown), Ebene (Dropdown), Nur geändert, Textsuche
- Statistiken: `📊 X/Y Logs | ✏️ Z geändert`

### Schlüsselfunktionen

**1. Aktions-ComboBox mit Verlauf**
- Vorausgefüllt mit allen im Scan gefundenen Aktionen
- Bearbeitbar: ermöglicht Eingabe neuer Aktionen
- Auto-Vervollständigung: Vorschläge basierend auf Verlauf
- Dynamisches Hinzufügen: neue Aktionen automatisch zur Liste hinzugefügt
- Richtlinie: `NoInsert` zum manuellen Steuern des Hinzufügens

**2. Tastaturkürzel**
- `Enter` im Aktionsfeld → Wendet Änderungen an
- `Ctrl+Enter` im Nachrichtenfeld → Wendet Änderungen an
- Pfeiltasten-Navigation in der Tabelle

**3. Filteriersystem**
- **Nach Logger**: BACKUP, EDEN, UI, CHARACTER, ROOT, Alle
- **Nach Ebene**: DEBUG, INFO, WARNING, ERROR, CRITICAL, Alle
- **Nach Status**: Alle, Nur geändert
- **Nach Text**: Suche in Nachrichten
- Echtzeit-Statistik-Aktualisierung

**4. Datei-Speicherung**
- Direkte Python-Quellcode-Datei-Änderung
- Originaleinrückung beibehalten
- Unterstützung für f-Strings und komplexe Formate
- `self.logger` und `module_logger` Handhabung
- Sichere Zeile-für-Zeile-Ersetzung

**5. Speicherung des letzten Projekts**
- JSON-Konfiguration: `Tools/log_editor_config.json`
- Automatisches Laden beim Start (100ms Verzögerung)
- Standardauswahl im Dialog
- Fenstertitel: `🔧 Log Source Editor - ProjektName (X Logs)`

**6. Schutzmechanismen und Validierungen**
- `_updating` Flag: Verhindert rekursive Update-Schleifen
- `blockSignals(True)`: während Tabellenaktualisierungen
- `__eq__` und `__hash__` Vergleich: Vermeidet Neuladen desselben Logs
- Vorspeicher-Überprüfung: Erkennt ungeänderte Dateien

### Benutzer-Workflow

1. **Start**: `.venv\Scripts\python.exe Tools\log_source_editor.py`
2. **Auto-Scan**: Letztes Projekt wird automatisch geladen
3. **Filterung**: Wähle "Logger: BACKUP" um Backup-Modul-Logs zu sehen
4. **Auswahl**: Klick auf ein Log in der Tabelle
5. **Bearbeitung**:
   - Wähle Aktion aus Dropdown oder gebe eine neue ein
   - Ändere Nachricht falls nötig
6. **Anwendung**: Drücke Enter oder klick "Anwenden"
7. **Wiederholung**: Navigiere mit ↓ zum nächsten Log
8. **Speicherung**: Klick "💾 Speichern" um in Dateien zu schreiben

### Angezeigte Statistiken (Nach Scan)

```
✅ Scan abgeschlossen: 144 Logs gefunden

📊 Nach Logger:
   BACKUP: 46
   EDEN: 52
   ROOT: 30
   UI: 16

📊 Nach Ebene:
   INFO: 80
   DEBUG: 40
   WARNING: 15
   ERROR: 9

📊 Aktionen:
   • Gefundene Aktionen: CHECK, DELETE, DIRECTORY, ERROR, INIT, PARSE, RETENTION, RESTORE, SCAN, SCRAPE, TRIGGER, ZIP
   • Mit Aktion: 120
   • Ohne Aktion: 24
```

---

## 🐛 Korrektionen

### Eden-Cookies-Speicherpfad (PyInstaller-Korrektur)

- **Problem**: Cookies wurden nicht standardmäßig im `Configuration/`-Ordner gespeichert
- **Ursache**: `CookieManager` verwendete `Path(__file__).parent.parent`, was PyInstaller-Probleme verursachte
- **Lösung**: Verwendung von `get_config_dir()` aus `config_manager.py` für globale Konsistenz
- **Ergebnis**: Cookies werden jetzt korrekt im durch `config_folder` in `config.json` definierten Ordner gespeichert
- **Kompatibilität**: Funktioniert korrekt mit kompilierter Anwendung und normaler Ausführung
- **Geänderte Datei**: `Functions/cookie_manager.py`

### Spaltenkonfiguration korrigiert

- **Problem 1**: Herald-URL-Spalte (Index 11) war nicht im Größenanpassungsmodus enthalten (`range(11)` statt `range(12)`)
- **Problem 2**: Reihenfolge der Class- und Level-Spalten war im Konfigurationsmenü umgekehrt
- **Problem 3**: Sichtbarkeitszuordnung verwendete falsche Reihenfolge und URL-Spalte fehlte

**Lösung**:
- `apply_column_resize_mode()` behandelt jetzt alle 12 Spalten korrekt
- Konfigurationsmenü-Reihenfolge mit TreeView ausgerichtet (Class vor Level)
- `column_map` mit korrekter Reihenfolge und URL-Spalten-Einbindung korrigiert

**Auswirkung**: Alle 12 Spalten (0-11) sind jetzt korrekt für Größenanpassungsmodus und Sichtbarkeit konfigurierbar

**Geänderte Dateien**: `Functions/tree_manager.py`, `UI/dialogs.py`

### 🧬 Herald-Authentifizierung - Vereinfachte & Zuverlässige Erkennung

- **Problem**: Authentifizierungserkennung mit mehreren unzuverlässigen Kriterien
- **Ursache**: Ungültige Cookies oder inkonsistente Erkennungstechnik
- **Lösung**: Erkennung basierend auf einzelnem definitivem Kriterium

**Erkennungslogik**:
- Fehlermeldung `'The requested page "herald" is not available.'` = NICHT VERBUNDEN
- Abwesenheit der Fehlermeldung = VERBUNDEN (kann Daten scrapen)

**Konsistenz**:
- Identische Logik zwischen `test_eden_connection()` (cookie_manager.py) und `load_cookies()` (eden_scraper.py)
- Ungültige Cookies korrekt erkannt und gemeldet
- Tests mit etwa 58 Herald-Suchergebnissen validiert

**Geänderte Dateien**: `Functions/cookie_manager.py`, `Functions/eden_scraper.py`

---

## ✨ Verbesserungen

### Auto-Update bei Charakterimport

- **Vorher**: Wenn Charakter existiert → Fehler "Charakter existiert bereits"
- **Jetzt**: Wenn Charakter existiert → Automatische Aktualisierung von Herald 🔄

**Beibehaltene Daten**: name, realm, season, server, benutzerdefinierte Felder

**Aktualisierte Daten**: class, race, guild, level, realm_rank, realm_points, url, notes

**Detaillierter Bericht**: Zeigt Anzahl der Erstellungen, Aktualisierungen und Fehler

**Anwendungsfall**: Ideal, um Charaktere über Herald-Import aktuell zu halten

**Geänderte Datei**: `UI/dialogs.py` - Funktion `_import_characters()` (Zeile 2422)

### Konfigurierbarer Herald-Cookies-Ordner

- **Neue Option**: Einstellungsfenster → "Herald-Cookies-Ordner"
- **Funktion**: Benutzerdefinierten Ordner zur Speicherung von Eden-Scraping-Cookies angeben
- **Schnittstelle**: "Durchsuchen..."-Schaltfläche zur erleichterten Ordnerauswahl
- **Standardwert**: `Configuration/`-Ordner (Verhalten bleibt erhalten, wenn nicht konfiguriert)
- **Portable Anwendung**: Pfade sind absolut, keine Abhängigkeit von `__file__`
- **Persistenz**: Die Konfiguration wird in `config.json` unter dem Schlüssel `"cookies_folder"` gespeichert
- **Fallback-Logik**: Wenn `cookies_folder` nicht gesetzt ist, wird `config_folder` verwendet (gewährleistet Abwärtskompatibilität)

**Geänderte Dateien**: `UI/dialogs.py`, `main.py`, `Functions/cookie_manager.py`

### Verbessertes Debug-Fenster

- **Neuer Filter**: Dropdown zum Filtern nach Logger
- **Optionen**: Alle, BACKUP, EDEN, UI, CHARACTER, ROOT

**Geänderte Datei**: `UI/debug_window.py`

### Einheitliche Verzeichnis-Labels

- **Vorher**: Gemischte Labels ("Ordner von...", "Verzeichnis von...")
- **Jetzt**: Alle Ordner-Pfade beginnen mit "Verzeichnis"

**Labels**:
- Verzeichnis der Charaktere
- Verzeichnis der Konfiguration
- Verzeichnis der Logs
- Verzeichnis der Rüstungen
- Verzeichnis der Herald-Cookies

**Doppelpunkt-Entfernung**: Keine Doppelpunkte mehr am Ende von Labels (werden automatisch von QFormLayout hinzugefügt)

**Lokalisierung**: Vollständige Übersetzungen in EN, FR, DE

**Geänderte Dateien**: `UI/dialogs.py`, `Language/fr.json`, `Language/en.json`, `Language/de.json`

### Pfadanfang-Anzeige

- **Vorher**: Cursor am Anfang, aber Text am Ende ausgerichtet (zeigte "...Configuration/" in QLineEdit)
- **Jetzt**: `setCursorPosition(0)` auf alle Pfadfelder angewendet
- **Ergebnis**: Anfang des Pfads angezeigt (z.B.: "d:\Projekte\Python\..." statt "...Configuration/")

**Geänderte Datei**: `UI/dialogs.py` - Methode `update_fields()`

### Robustes Diagnosesystem für unerwartete Stopps

- **Globaler Exception-Handler**: Erfasst und protokolliert alle nicht behandelten Ausnahmen
- **System-Signal-Handler**: Erkennt SIGTERM, SIGINT und andere OS-Unterbrechungen
- **Immer aktives CRITICAL/ERROR-Logging**: Auch mit debug_mode = OFF werden Fehler aufgezeichnet
- **Startup-Verfolgung**: Zeichnet Zeit (ISO 8601), Python-Version, aktive Threads auf
- **Shutdown-Verfolgung**: Zeichnet genau auf, wann und wie App stoppt
- **Exit-Code**: Zeigt von Qt-Event-Loop zurückgegebenen Code an

**Geänderte Dateien**: `main.py`, `Functions/logging_manager.py`

### 🎛️ Herald-Schaltflächen-Steuerung

- **Schaltflächen**: "Aktualisieren" und "Herald-Suche" automatisch deaktiviert
- **Deaktivierungsbedingungen**:
  - Wenn kein Cookie erkannt wird
  - Wenn Cookies abgelaufen sind
- **Synchronisierung**: Schaltflächenzustand mit Verbindungsstatus synchronisiert
- **Benutzer-Nachricht**: Klar - "Kein Cookie erkannt"

**Logik**: Wenn `cookie_exists()` False zurückgibt oder Cookies ungültig → Schaltflächen deaktiviert

**Geänderte Datei**: `UI/ui_manager.py` - Funktion `update_eden_status()`

### Automatisches Speichersystem bei Charakteraktualisierungen

- **Problem**: Bei Änderung eines existierenden Charakters (Rang, Info, Rüstung, Fähigkeiten) oder Herald-Update wurde keine Speicherung ausgelöst
- **Lösung**: Integration automatischer Backups mit beschreibendem Grund an allen Änderungspunkten

**Abgedeckte Punkte**:
- Herald-Update nach Bestätigung (main.py)
- Automatische Rang-Änderung (auto_apply_rank)
- Manuelle Rang-Änderung (apply_rank_manual)
- Basis-Info-Änderung (save_basic_info)
- Rüstungs-/Fähigkeits-Änderung (CharacterSheetWindow)
- Massiver Import/Update (Import-Dialog)

**Backup-Typ**: `backup_characters_force(reason="Update")` → MANUELL (umgeht tägliches Limit)

**Dateiname**: `backup_characters_YYYYMMDD_HHMMSS_Update.zip`

**Generierte Logs**: Jede Änderung generiert sichtbare Logs mit `[BACKUP_TRIGGER]` Tag:

```
[BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) - Backup with reason=Update
[BACKUP] MANUAL-BACKUP - Creating compressed backup: backup_characters_20251101_143045_Update.zip
```

**Ergebnis**: Jede Charakteränderung erstellt automatisch Backup mit beschreibendem Grund und sichtbaren Logs

**Geänderte Dateien**: `main.py`, `UI/dialogs.py`

**Dokumentation**: `Documentations/BACKUP_DEBUG_GUIDE.md` mit neuen Szenarien aktualisiert

---

## 🎨 Schnittstellen-Verbesserungen

### Spaltenkonfiguration

- Alle 12 Spalten (0-11) korrekt konfigurierbar
- Größenanpassungsmodus und Sichtbarkeit funktional
- Konfigurationsmenü mit TreeView ausgerichtet

### Einheitliche Labels

- Alle Ordner-Pfade beginnen mit "Verzeichnis"
- Entfernung unnötiger Doppelpunkte
- Konsistente und professionelle Schnittstelle

### Optimierte Pfad-Anzeige

- Anfang der Pfade sichtbar (kein "...")
- Cursor am Anfang der Felder
- Bessere Lesbarkeit für Benutzer

### Reich-Sortierung

**Problem**: Die Reich-Spalte erlaubte keine Sortierung durch Klicken auf die Kopfzeile

**Lösung**:
- Benutzerdefiniertes `RealmSortProxyModel` hinzugefügt
- Implementierung von `lessThan()` für Spalte 1 (Reich)
- Verwendung von `Qt.UserRole + 2` zum Speichern von Sortierdaten
- Proxy fängt Sortierung ab und verwendet Reich-Namen

**Geänderte Dateien**:
- `Functions/tree_manager.py`: `RealmSortProxyModel`-Klasse hinzugefügt
- Import von `QSortFilterProxyModel` aus `PySide6.QtCore`
- Proxy-Konfiguration in `__init__()`: `self.proxy_model.setSourceModel(self.model)`

**Ergebnis**:
- ✅ Funktionale alphabetische Sortierung (Albion → Hibernia → Midgard)
- ✅ Reich-Icons immer angezeigt (ohne Text)
- ✅ Vorhandener Delegate beibehalten (`CenterIconDelegate`)

### Herald-URL-Spaltenbreite

**Problem**: Herald-Schaltfläche war in zu schmaler URL-Spalte zerquetscht

**Lösung**:
- Mindestbreite von 120px für Spalte 11 (URL) festgelegt
- Angewendet in `apply_column_resize_mode()` nach `ResizeToContents`

**Code**:
```python
# Mindestbreite für URL-Spalte (11) festlegen
self.tree_view.setColumnWidth(11, 120)
```

**Ergebnis**:
- ✅ Herald-Schaltfläche perfekt sichtbar
- ✅ Komfortabler Platz für Interaktion
- ✅ Keine Auswirkungen auf andere Spalten

---

## 🧹 Repository-Bereinigung

- **Löschung von 13 temporären Debug-Skripten**
- **Löschung von 3 Debug-HTML-Dateien**
- **Sauberes und wartbares Repository**
- **Leistungsoptimierung**

**Gelöschte Dateien**:
- analyze_search_structure.py
- debug_comparison.py
- debug_herald_content.py
- debug_search_html.py
- debug_test_connection.py
- save_search_html.py
- show_cookies.py
- test_direct_search.py
- test_full_flow.py
- test_herald_detection.py
- test_identical_flow.py
- test_load_cookies_msg.py
- test_simple.py
- debug_herald_page.html
- debug_test_connection.html
- search_result.html

---

## 📚 Dokumentation

### Bereinigung und Neuorganisation des CHANGELOG-Systems

- **Altes System**: Monolithische CHANGELOGs in `Documentation/` mit gemischten Versionen (schwierig zu navigieren)
- **Neues System**: Hierarchische Struktur in `Changelogs/` mit klarer Versions- und Sprachtrennung

**Erstellte Struktur**:
- `Changelogs/Full/`: Detaillierte CHANGELOGs (~200+ Zeilen) für v0.106, v0.104 und frühere Versionen
- `Changelogs/Simple/`: Prägnante Listen zur schnellen Navigation aller Versionen (v0.1 bis v0.106)
- Mehrsprachige Unterstützung: EN, FR, DE für jede Datei

**Zentralisierter Zugriff**: Neues `CHANGELOG.md` im Root mit Index und Navigation zu allen Versionen

**Alter Inhalt**: Monolithische CHANGELOGs aus `Documentation/` entfernt

**Erstellte Dateien**: 27+ Dateien insgesamt (6 Full + 21 Simple)

**Ergebnis**: Viel klareres und wartbareres System zum Auffinden von Änderungen nach Version und Sprache

---

## 📊 Statistiken

- **Hinzugefügte Code-Zeilen**: ~1000+ (log_source_editor.py: 975 Zeilen)
- **Geänderte Dateien**: 12 Dateien
- **Erstellte Dateien**: 2 Dateien (log_source_editor.py, log_editor_config.json)
- **Getaggte Logs**: 46+ in backup_manager.py, 52+ in eden_scraper.py
- **Standardisierte Aktionen**: 20+ verschiedene Aktionen
- **Durchgeführte Tests**: Scannen, Filtern, Bearbeitung, Speicherung validiert

---

## 🔗 Geänderte Dateien

- `main.py`
- `UI/dialogs.py`
- `UI/ui_manager.py`
- `UI/debug_window.py`
- `Functions/cookie_manager.py`
- `Functions/eden_scraper.py`
- `Functions/tree_manager.py`
- `Functions/logging_manager.py`
- `Language/fr.json`
- `Language/en.json`
- `Language/de.json`
- `Documentations/BACKUP_DEBUG_GUIDE.md`

---

## 📊 Gesamtauswirkung

✅ **Intuitiverer und flüssigerer Import-Workflow** - Kein Löschen/Neuimport bestehender Charaktere erforderlich

✅ **Transparente Stats-Aktualisierung von Herald** - Charaktere aktualisieren sich automatisch

✅ **Saubere Fehlerbehandlung mit detailliertem Bericht** - Anzahl der Erstellungen, Aktualisierungen und Fehler

✅ **Erhöhte Cookie-Verwaltungsflexibilität** - Anpassbare Pfade für Scraping

✅ **Vollständige Anwendungsportabilität** - Zentralisierte Konfiguration ohne __file__ Abhängigkeiten

✅ **Fähigkeit zur Diagnose unerwarteter Stopps** - Detaillierte Logs aller kritischen Ereignisse

✅ **Konsistente und kohärente Schnittstelle** - Einheitliche Labels und optimale Pfad-Anzeige

✅ **Automatisches Speichern bei Änderungen** - Jede Charakteränderung erstellt Backup mit sichtbaren Logs

---

## 🔄 Migration

**Keine Migration erforderlich** - Diese Version ist 100% abwärtskompatibel mit v0.105

---

## 🐛 Bekannte Fehler

Keine bekannten Fehler zum aktuellen Zeitpunkt.

---

## 📝 Entwicklungsnotizen

- Der Log Source Editor ist ein Entwicklungswerkzeug, nicht in der Hauptanwendung enthalten
- Das Werkzeug erleichtert die Wartung und Verbesserung des Logging-Systems erheblich
- Das einheitliche Logging-Format ermöglicht bessere Analyse und Debugging
- Standardisierte Aktionen erleichtern Filterung und Log-Suche
