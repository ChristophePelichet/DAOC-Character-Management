# CHANGELOG v0.106 - Logging-System & Entwicklerwerkzeuge# CHANGELOG v0.106 - Eden-Scraping & Auto-Update-Korrektionen



**Datum**: 2025-11-01  **Datum** : 2025-11-01  

**Version**: 0.106**Version** : 0.106



---## 🐛 Korrektionen



## 🔧 Neues Logging-System### Eden-Cookies-Speicherpfad (PyInstaller-Korrektur)

- **Problem** : Cookies wurden nicht standardmäßig im `Configuration/`-Ordner gespeichert

### Einheitliches Format mit ACTION- **Ursache** : `CookieManager` verwendete `Path(__file__).parent.parent`, was Probleme mit PyInstaller verursachte

- **Lösung** : Verwendung von `get_config_dir()` aus `config_manager.py` für globale Konsistenz

- **Vorher**: Inkonsistentes Format, schwierig zu filtern und zu analysieren- **Ergebnis** : Cookies werden jetzt korrekt im durch `config_folder` in `config.json` definierten Ordner gespeichert

- **Jetzt**: Standardisiertes Format `LOGGER - LEVEL - ACTION - MESSAGE`- **Kompatibilität** : Funktioniert korrekt mit kompilierter Anwendung und normaler Ausführung

- **Beispiel**: `2025-11-01 14:30:00 - BACKUP - INFO - INIT - BackupManager initialized`- **Geänderte Datei** : `Functions/cookie_manager.py` (Zeile 22-34)

- **Vorteile**:

  * Einfaches Filtern nach Logger (BACKUP, EDEN, UI, CHARACTER, ROOT)### Spaltenkonfiguration korrigiert

  * Klare Aktionen für jede Operation- **Problem 1** : Die Herald-URL-Spalte (Index 11) war nicht im Größenanpassungsmodus enthalten (`range(11)` statt `range(12)`)

  * Vollständige Rückverfolgbarkeit des Ausführungsablaufs- **Problem 2** : Die Reihenfolge der Class- und Level-Spalten war im Konfigurationsmenü umgekehrt

  * Kompatibel mit Log-Analyse-Tools- **Problem 3** : Sichtbarkeitszuordnung verwendete falsche Reihenfolge und URL-Spalte fehlte

- **Lösung** :

### BACKUP Logger - Backup-Modul  * `apply_column_resize_mode()` behandelt jetzt alle 12 Spalten korrekt

  * Konfigurationsmenü-Reihenfolge mit TreeView ausgerichtet (Class vor Level)

- **Geänderte Dateien**: `backup_manager.py`, `migration_manager.py`  * `column_map` mit korrekter Reihenfolge und URL-Spalten-Einbindung korrigiert

- **46+ Logs getaggt** mit klaren Aktionen- **Auswirkung** : Alle 12 Spalten (0-11) sind jetzt korrekt für Größenanpassungsmodus und Sichtbarkeit konfigurierbar

- **Standardisierte Aktionen**: INIT, DIRECTORY, CHECK, STARTUP, TRIGGER, AUTO_TRIGGER, AUTO_PROCEED, AUTO_BLOCKED, MANUAL_TRIGGER, ZIP, RETENTION, SCAN, DELETE, INFO, RESTORE, ERROR- **Geänderte Dateien** : `Functions/tree_manager.py`, `UI/dialogs.py`

- **Stufen**: DEBUG (Details), INFO (Fortschritt), WARNING (Warnungen), ERROR (Fehler)

## ✨ Verbesserungen

### EDEN Logger - Herald-Scraper

### Auto-Update bei Charakterimport

- **Datei**: `eden_scraper.py`- **Vorher** : Wenn Charakter existiert → Fehler "Charakter existiert bereits"

- **Aktionen**: INIT, COOKIES, SCRAPE, SEARCH, PARSE, TEST, CLOSE, CLEANUP, ERROR- **Jetzt** : Wenn Charakter existiert → Automatische Aktualisierung von Herald 🔄

- **Beibehaltene Daten** : name, realm, season, server, benutzerdefinierte Felder

### Verbessertes Debug-Fenster- **Aktualisierte Daten** : class, race, guild, level, realm_rank, realm_points, url, notes

- **Detaillierter Bericht** : Zeigt Anzahl von Erstellungen, Aktualisierungen und Fehlern

- **Neuer Filter**: Dropdown zum Filtern nach Logger- **Anwendungsfall** : Ideal, um Charaktere über Herald-Import aktuell zu halten

- **Optionen**: Alle, BACKUP, EDEN, UI, CHARACTER, ROOT- **Geänderte Datei** : `UI/dialogs.py` - Funktion `_import_characters()` (Zeile 2422)



---### Konfigurierbarer Herald-Cookies-Ordner

- **Neue Option** : Einstellungsfenster → "Herald-Cookies-Ordner"

## 🛠️ Log Source Editor - Neues Entwicklerwerkzeug- **Funktion** : Benutzerdefinierten Ordner zur Speicherung von Eden-Scraping-Cookies angeben

- **Interface** : "Durchsuchen..."-Schaltfläche zur erleichterten Ordnerauswahl

### Überblick- **Standardwert** : `Configuration/`-Ordner (Verhalten bleibt erhalten, wenn nicht konfiguriert)

- **Portable Anwendung** : Pfade sind absolut, keine Abhängigkeit von `__file__`

- **Datei**: `Tools/log_source_editor.py` (975 Zeilen)- **Persistenz** : Die Konfiguration wird in `config.json` unter dem Schlüssel `"cookies_folder"` gespeichert

- **Zweck**: Logs direkt im Quellcode VOR Kompilierung bearbeiten- **Fallback-Logik** : Wenn `cookies_folder` nicht gesetzt ist, wird `config_folder` verwendet (gewährleistet Abwärtskompatibilität)

- **Framework**: PySide6 (Qt6) mit vollständiger GUI- **Geänderte Dateien** : `UI/dialogs.py`, `main.py`, `Functions/cookie_manager.py`



### Quellcode-Scanner### Einheitliche Verzeichnis-Labels

- **Vorher** : Gemischte Labels ("Ordner von...", "Verzeichnis von...")

- **Technologie**: Asynchroner QThread ohne UI-Blockierung- **Jetzt** : Alle Ordner-Pfade beginnen mit "Verzeichnis"

- **Pattern 1**: Erkennt `logger.info()`, `self.logger.debug()`, `module_logger.warning()`- **Labels** :

- **Pattern 2**: Erkennt `log_with_action(logger, "info", "message", action="TEST")`  * Charakterverzeichnis

- **Intelligente Erkennung**:  * Konfigurationsverzeichnis

  * Logger-Name aus Dateinamen extrahieren  * Log-Verzeichnis

  * Parse `get_logger(LOGGER_XXX)`  * Rüstungsverzeichnis

  * Parse `setup_logger("LOGGER_NAME")`  * Herald-Cookie-Verzeichnis

- **Doppelpunkte entfernt** : Keine Doppelpunkte mehr am Ende von Labels (werden von QFormLayout automatisch hinzugefügt)

### Benutzeroberfläche- **Lokalisierung** : Vollständige Übersetzungen in DE, FR, EN

- **Geänderte Dateien** : `UI/dialogs.py`, `Language/fr.json`, `Language/en.json`, `Language/de.json`

**Hauptlayout**:

- **Links**: Tabelle der gefundenen Logs (schreibgeschützt)### Verbesserte Pfadanzeige

  * Spalten: File, Line, Logger, Level, Action, Message, Modified- **Vorher** : Cursor war am Anfang, aber Text war am Ende ausgerichtet (zeigt "...Configuration/" in QLineEdit)

- **Rechts**: Bearbeitungspanel- **Jetzt** : `setCursorPosition(0)` auf alle Pfadfelder angewendet

  * Action: Bearbeitbare ComboBox mit Verlauf- **Ergebnis** : Anfang des Pfads ist sichtbar (z. B. "d:\Projekte\Python\..." statt "...Configuration/")

  * Message: Mehrzeilige QTextEdit- **Geänderte Datei** : `UI/dialogs.py` - Methode `update_fields()` (Zeile 1260+)

  * Originalcode: Schreibgeschützte QTextEdit

### Robustes Diagnosesystem für unerwartete Abstürze

**Symbolleiste**:- **Global Exception Handler** : Erfasst und protokolliert alle unbehandelten Ausnahmen

- 🔍 Projekt scannen- **System-Signal-Handler** : Erkennt SIGTERM, SIGINT und andere Betriebssystem-Unterbrechungen

- Filter: Logger, Level, Nur geändert, Textsuche- **CRITICAL/ERROR-Logging immer aktiv** : Auch bei debug_mode = OFF werden Fehler aufgezeichnet

- Statistiken: `📊 X/Y Logs | ✏️ Z geändert`- **Startup-Verfolgung** : Zeichnet Zeit (ISO 8601), Python-Version, aktive Threads auf

- **Shutdown-Verfolgung** : Zeichnet genau auf, wann und wie die App beendet wird

### Hauptfunktionen- **Exit-Code** : Zeigt den von der Qt-Ereignisschleife zurückgegebenen Code

- **Geänderte Dateien** : `main.py`, `Functions/logging_manager.py`

**1. Action-ComboBox mit Verlauf**

- Vorgefüllt mit allen beim Scan gefundenen Aktionen### Bereinigung und Umstrukturierung des CHANGELOGs-Systems

- Bearbeitbar: Eingabe neuer Aktionen möglich- **Altes System** : Monolithische CHANGELOGs in `Documentation/` vermischten alle Versionen (schwer zu navigieren)

- Auto-Vervollständigung basierend auf Verlauf- **Neues System** : Hierarchische Struktur in `Changelogs/` mit klarer Trennung nach Version und Sprache

- Dynamisches Hinzufügen neuer Aktionen- **Erstellte Struktur** :

  - `Changelogs/Full/` : Detaillierte CHANGELOGs (~150 Zeilen) für v0.106, v0.104 und frühere Versionen

**2. Tastaturkürzel**  - `Changelogs/Simple/` : Prägnante Listen für schnelle Navigation aller 7 Versionen (v0.1 bis v0.106)

- `Enter` im Action-Feld → Änderungen übernehmen  - Mehrsprachige Unterstützung : FR, EN, DE für jede Datei

- `Strg+Enter` im Message-Feld → Änderungen übernehmen- **Zentrale Zugriff** : Neues `CHANGELOG.md` im Root mit Index und Navigation zu allen Versionen

- **Alte Inhalte** : Monolithische CHANGELOGs aus `Documentation/` entfernt (CHANGELOG_FR.md, CHANGELOG_EN.md, CHANGELOG_DE.md)

**3. Filtersystem**- **Erstellte Dateien** : 27 Dateien insgesamt (6 Full + 21 Simple)

- **Nach Logger**: BACKUP, EDEN, UI, CHARACTER, ROOT, Alle- **Ergebnis** : Viel klareres und wartbareres System zum Auffinden von Änderungen nach Version und Sprache

- **Nach Level**: DEBUG, INFO, WARNING, ERROR, CRITICAL, Alle

- **Nach Status**: Alle, Nur geändert## 📊 Allgemeine Auswirkungen

- **Nach Text**: Suche in Nachrichten

✅ **Intuitiverer und flüssigerer Import-Workflow** - Kein Löschen/Neuimportieren erforderlich  

**4. In Dateien speichern**✅ **Transparente Stats-Aktualisierung von Herald** - Charaktere werden automatisch aktualisiert  

- Direkte Änderung von Python-Quelldateien✅ **Ordnungsgemäße Fehlerbehandlung mit detailliertem Bericht** - Anzahl von Erstellungen, Aktualisierungen und Fehlern  

- Bewahrt ursprüngliche Einrückung✅ **Erhöhte Flexibilität für Cookie-Verwaltung** - Anpassbare Pfade für Scraping  

- Unterstützt f-Strings und komplexe Formate✅ **Vollständige Anwendungsportabilität** - Zentralisierte Konfiguration ohne __file__-Abhängigkeiten  

✅ **Möglichkeit, unerwartete Abstürze zu diagnostizieren** - Detaillierte Protokolle aller kritischen Ereignisse  

**5. Letztes Projekt merken**✅ **Konsistente und kohärente Benutzeroberfläche** - Einheitliche Labels und optimale Pfadanzeige  

- JSON-Konfiguration: `Tools/log_editor_config.json`✅ **Automatische Sicherung bei Änderungen** - Jede Charaktermodifikation erstellt eine Sicherung mit sichtbaren Logs  

- Automatisches Laden beim Start

- Fenstertitel: `🔧 Log Source Editor - ProjektName (X Logs)`### Automatisches Sicherungssystem bei Charakteraktualisierungen

- **Problem** : Bei der Änderung eines vorhandenen Charakters (Rang, Info, Rüstung, Fähigkeiten) oder bei der Aktualisierung von Herald wurde keine Sicherung ausgelöst

---- **Lösung** : Integration automatischer Sicherungen mit aussagekräftigen Gründen an allen Änderungspunkten

- **Abgedeckte Punkte** :

## 🔍 Eden-Scraping-Korrekturen  * Herald-Aktualisierung nach Bestätigung (main.py)

  * Automatische Rangänderung (auto_apply_rank)

### Eden-Cookies-Speicherpfad (PyInstaller-Korrektur)  * Manuelle Rangänderung (apply_rank_manual)

  * Änderung von Basis-Infos (save_basic_info)

- **Problem**: Cookies wurden nicht standardmäßig im Ordner `Configuration/` gespeichert  * Rüstungs-/Fähigkeitsänderung (CharacterSheetWindow)

- **Lösung**: Verwendung von `get_config_dir()` aus `config_manager.py` für globale Konsistenz  * Massen-Import/Aktualisierung (Import-Dialog)

- **Ergebnis**: Cookies werden jetzt korrekt im durch `config_folder` in `config.json` definierten Ordner gespeichert- **Sicherungstyp** : `backup_characters_force(reason="Update")` → MANUELL (umgeht tägliches Limit)

- **Dateiname** : `backup_characters_YYYYMMDD_HHMMSS_Update.zip`

### Auto-Update beim Charakterimport- **Generierte Logs** : Jede Änderung generiert sichtbare Logs mit Tag `[BACKUP_TRIGGER]` :

  ```

- **Vorher**: Wenn Charakter existiert → Fehler "Charakter existiert bereits"  [BACKUP_TRIGGER] Action: CHARACTER MODIFICATION (Rank) - Backup with reason=Update

- **Jetzt**: Wenn Charakter existiert → Automatisches Update von Herald 🔄  [BACKUP] MANUAL-BACKUP - Creating compressed backup: backup_characters_20251101_143045_Update.zip

- **Daten beibehalten**: name, realm, season, server, benutzerdefinierte Daten  ```

- **Daten aktualisiert**: class, race, guild, level, realm_rank, realm_points, url, notes- **Ergebnis** : Jede Charakteränderung erstellt automatisch eine Sicherung mit aussagekräftigem Grund und sichtbaren Logs

- **Geänderte Dateien** : `main.py`, `UI/dialogs.py`

### Konfigurierbarer Herald-Cookies-Ordner- **Dokumentation** : `Documentations/BACKUP_DEBUG_GUIDE.md` mit neuen Szenarien aktualisiert



- **Neue Option**: Einstellungsfenster → "Herald-Cookies-Verzeichnis"## 🔗 Geänderte Dateien

- **Funktionalität**: Benutzerdefinierten Ordner für Eden-Scraping-Cookies angeben

- **Standard**: Ordner `Configuration/` (beibehalten, wenn nicht konfiguriert)- `main.py`

- `UI/dialogs.py`

---- `Functions/cookie_manager.py`

- `Functions/tree_manager.py`

## 🎨 Schnittstellenverbesserungen- `Functions/logging_manager.py`

- `Language/fr.json`

### Spaltenkonfiguration korrigiert- `Language/en.json`

- `Language/de.json`

- **Problem 1**: Herald-URL-Spalte (Index 11) nicht in Größenänderung enthalten- `Documentations/BACKUP_DEBUG_GUIDE.md`

- **Problem 2**: Class- und Level-Spaltenreihenfolge im Konfigurationsmenü vertauscht
- **Problem 3**: Sichtbarkeitszuordnung verwendete falsche Reihenfolge und URL-Spalte fehlte
- **Lösung**: Alle 12 Spalten (0-11) jetzt korrekt konfigurierbar

### Einheitliche Verzeichnislabels

- **Vorher**: Gemischte Labels ("Ordner der...", "Verzeichnis der...")
- **Jetzt**: Alle Ordnerpfade beginnen mit "Verzeichnis"
- **Labels**: Charakterverzeichnis, Konfigurationsverzeichnis, Protokollverzeichnis, Rüstungsverzeichnis, Herald-Cookies-Verzeichnis

### Pfadanfang anzeigen

- **Vorher**: Cursor am Anfang, aber Text am Ende ausgerichtet
- **Jetzt**: `setCursorPosition(0)` auf alle Pfadfelder angewendet
- **Ergebnis**: Pfadanfang anzeigen (z.B. "d:\Projekte\Python\..." statt "...Configuration/")

---

## 📚 Dokumentation

### CHANGELOG-System-Bereinigung und Umstrukturierung

- **Altes System**: Monolithische CHANGELOGs in `Documentation/` mit gemischten Versionen
- **Neues System**: Hierarchische Struktur in `Changelogs/` mit klarer Trennung nach Version und Sprache
- **Struktur**:
  - `Changelogs/Full/`: Detaillierte CHANGELOGs (~200+ Zeilen)
  - `Changelogs/Simple/`: Prägnante Listen zur schnellen Navigation
  - Dreisprachige Unterstützung: FR, EN, DE

---

## 📊 Statistiken

- **Hinzugefügte Codezeilen**: ~1000+ (log_source_editor.py: 975 Zeilen)
- **Geänderte Dateien**: 12 Dateien
- **Erstellte Dateien**: 2 Dateien
- **Getaggte Logs**: 46+ in backup_manager.py, 52+ in eden_scraper.py
- **Standardisierte Aktionen**: 20+ verschiedene Aktionen

---

## 🔄 Migration

**Keine Migration erforderlich** - Diese Version ist 100% abwärtskompatibel mit v0.105

---

## 📝 Entwicklungshinweise

- Log Source Editor ist ein Entwicklungswerkzeug, nicht in der Hauptanwendung enthalten
- Einheitliches Logging-Format ermöglicht bessere Analyse und Fehlersuche
- Standardisierte Aktionen erleichtern Filterung und Suche in Logs
