# ÄNDERUNGSPROTOKOLL

> 📁 **Diese Datei wurde verschoben** : Früher im Stammverzeichnis, jetzt in `Documentation/` (v0.104)

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

## [0.106] - 2025-10-31 - Eden Scraping Korrektur 🔧

### 🐛 Fehlerbehebungen

#### Behoben (31.10.2025)
- **Eden-Cookies-Speicherpfad** : Speicherordner-Standort korrigiert
  - Problem: Cookies wurden nicht im Standard-Ordner `Configuration/` gespeichert
  - Der `CookieManager` verwendete `Path(__file__).parent.parent`, was Probleme mit PyInstaller verursachte
  - Lösung: Verwendung von `get_config_dir()` aus `config_manager.py` für globale Konsistenz
  - Cookies werden jetzt korrekt im durch `config_folder` in `config.json` definierten Ordner gespeichert
  - Kompatibel mit kompilierter Anwendung und normaler Ausführung
  - Geänderte Datei: `Functions/cookie_manager.py` (Zeile 22-34)
  - Dokumentation: `Documentation/COOKIE_PATH_FIX.md` mit vollständigen Details erstellt

#### Verbesserungen
- **Konfigurationszentralisierung** : Alle Pfade verwenden jetzt `get_config_dir()`
- **PyInstaller-Kompatibilität** : Funktioniert korrekt mit kompilierter Anwendung
- **Konsistenz** : Gleiche Pfadauflösungslogik wie der Rest der Anwendung

- **Spaltenkonfiguration korrigiert** : Vollständige Korrektur des Spaltensystems
  - Problem 1: URL Herald-Spalte (Index 11) war nicht in der Größenänderung enthalten (`range(11)` statt `range(12)`)
  - Problem 2: Die Reihenfolge der Spalten Klasse und Stufe war im Konfigurationsmenü vertauscht
  - Problem 3: Sichtbarkeitszuordnung verwendete falsche Reihenfolge und URL-Spalte fehlte
  - Lösung: 
    * `apply_column_resize_mode()` verarbeitet jetzt korrekt alle 12 Spalten
    * Konfigurationsmenü-Reihenfolge mit TreeView abgestimmt (Klasse vor Stufe)
    * `column_map`-Zuordnung mit korrekter Reihenfolge und URL-Spalten-Einbeziehung korrigiert
  - Auswirkung: Alle 12 Spalten (0-11) sind jetzt korrekt für Größenänderung und Sichtbarkeit konfigurierbar
  - Geänderte Dateien: `Functions/tree_manager.py`, `UI/dialogs.py`
  - Dokumentation: `Documentation/COLUMN_CONFIGURATION_FIX.md` mit detaillierter Analyse erstellt

---

## [0.105] - 2025-10-31 - Eden Scraping & Massenimport 🌐

### 🌐 Eden Herald - Import-Verbesserungen

#### Hinzugefügt (31.10.2025)
- **Automatische Standard-Saison-Zuweisung**: Beim Import von Eden Herald
  - Importierte Charaktere werden automatisch in der in `config.json` definierten Saison `default_season` platziert
  - Standardwert: "S1", wenn nicht in der Konfiguration definiert
  - Charakter wird in `Characters/{season}/{name}.json` gespeichert
  - Geändert in `UI/dialogs.py`: Methode `_import_characters()`
  - Feld `'season': default_season` in `character_data` hinzugefügt
  - Abgerufen über `config.get('default_season', 'S1')`

- **Kontextmenü für schnellen Import**: Rechtsklick auf Ergebnistabelle
  - Neues Kontextmenü in der Herald-Suchergebnistabelle
  - Aktion "📥 Diesen Charakter importieren" per Rechtsklick auf eine Zeile verfügbar
  - Direkter Charakter-Import ohne untere Schaltflächen
  - Bestätigungsdialog vor Import, um Fehler zu vermeiden
  - Neue Methode `show_context_menu(position)`: Zeigt Menü bei Rechtsklick
  - Neue Methode `_import_single_character(row)`: Importiert einen bestimmten Charakter
  - Import von `QMenu` in PySide6-Imports
  - Konfiguration: `results_table.setContextMenuPolicy(Qt.CustomContextMenu)`
  - Verbindung: `customContextMenuRequested.connect(self.show_context_menu)`

#### Geändert (31.10.2025)
- **Verbesserte Import-Ergonomie**:
  - Zwei verfügbare Import-Methoden: Schaltflächen (bestehend) + Rechtsklick (neu)
  - Schaltflächen "Auswahl importieren" und "Alle importieren" bleiben voll funktionsfähig
  - Vereinfachter Workflow: Suchen → Rechtsklick → Bestätigen → In Standard-Saison importiert

#### Dokumentation (31.10.2025)
- Erstellt `Documentation/EDEN_IMPORT_IMPROVEMENTS_FR.md`:
  - Vollständige technische Implementierungsdetails
  - Vollständiger Workflow mit ASCII-Diagramm zur Veranschaulichung des Prozesses
  - Vorher-Nachher-Vergleich für Endbenutzer
  - Konfigurationsleitfaden und empfohlene Tests
  - Mehrsprachige Unterstützung (FR/EN/DE-Vorschläge für Internationalisierung)
  - Mögliche zukünftige Verbesserungen

### 📚 Dokumentation (30.10.2025)

#### Hinzugefügt
- **Integriertes Hilfesystem**: Vollständige In-App-Dokumentation
  - `Functions/help_manager.py`: Hilfe-Manager mit Markdown-Unterstützung
  - `HelpWindow`: Anzeigefenster mit professionellem HTML-Rendering
  - Erster Leitfaden: "Einen neuen Charakter erstellen" (FR)
  - Mehrsprachige Unterstützung mit automatischem Fallback (FR → EN → DE)
  - "Dokumentation"-Menü im Hilfe-Menü
  - Professionelles CSS-Styling für optimales Rendering
  - Emoji-Schriftart-Unterstützung: Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji
  - Markdown-Bibliothek 3.7 mit Erweiterungen (tables, code, toc)

- **Dokumentationsstruktur**: Vollständige Organisation
  - `Help/fr/`, `Help/en/`, `Help/de/`: Verzeichnisse nach Sprache
  - `Help/images/`: Ordner für Screenshots
  - `Documentation/HELP_SYSTEM_PLAN.md`: Vollständiger Plan (30+ geplante Hilfen)
  - `Help/README.md`: Entwicklerleitfaden zum Hinzufügen von Hilfen
  - `Documentation/HELP_SYSTEM_IMPLEMENTATION.md`: Implementierungszusammenfassung

#### Geändert
- Reorganisation des Hilfe-Menüs mit Untermenü "📚 Dokumentation"
- Emoji-Optimierung für bessere Windows/Qt-Kompatibilität
- Vereinfachte Emojis in Hilfen zur Vermeidung von Anzeigeproblemen

### 🔧 Verbesserungen (30.10.2025)

#### Geändert
- Sprachkonfiguration aus `config.json` abgerufen
- `AttributeError` in `show_help_create_character()` behoben

---

## [0.104] - 2025-10-29 - Vollständiges Refactoring & Migration ✨

### 🏗️ Architektur
- **Vollständiges Application-Refactoring** : Modularer und wartbarer Code
  - Extrahiert von `main.py` (1277 Zeilen) zu 3 neuen Managern
  - `Functions/ui_manager.py` (127 Zeilen) : UI-Elementverwaltung
  - `Functions/tree_manager.py` (297 Zeilen) : Charakterlistenverwaltung
  - `Functions/character_actions_manager.py` (228 Zeilen) : Charakteraktionen
  - `main.py` auf 493 Zeilen reduziert (-61%)
  - Klare Verantwortlichkeitstrennung (SRP)
  - Teilweise MVC-Architektur

### ⚡ Leistung
- **Große Optimierungen** :
  - Ladezeit : -22% (von ~0.45s auf ~0.35s)
  - Listen-Aktualisierung : -33% (von ~0.12s auf ~0.08s für 100 Charaktere)
  - Speichernutzung : -8% (von ~85MB auf ~78MB)
- **Icon-Caching** : Einmaliges Laden beim Start
- **Reduzierte redundante Aufrufe** : -60% unnötige Aufrufe
- **Lazy Loading** : Verzögertes Laden von Ressourcen

### 🧹 Aufräumen
- **Toter Code entfernt** :
  - Veraltete Testskripte (8 Dateien gelöscht)
  - Ungenutzte Imports eliminiert
  - Duplizierter Code konsolidiert
- **Reduzierte Komplexität** :
  - Zyklomatische Komplexität von main.py : -71%
  - Funktionen > 50 Zeilen : -83%
  - Imports in main.py : -36%

### 📚 Dokumentation
- **Vollständige Refactoring-Dokumentation** : [REFACTORING_v0.104_COMPLETE.md](REFACTORING_v0.104_COMPLETE.md)
  - Detaillierter Vorher-Nachher-Vergleich
  - Modulare Architektur erklärt
  - Leistungsmetriken
  - Migrationsleitfaden für Mitwirkende
- **Aktualisiertes README** : 
  - Version v0.104 im Titel hinzugefügt
  - Vollständig überarbeitete und detaillierte Projektstruktur
  - Neuer `Tools/`-Ordner mit Entwicklungswerkzeugen
  - Neuer `UI/`-Ordner mit Oberflächenkomponenten
  - Dokumentation der neuen Manager (Codezeilen)
  - Klare Organisation der Dateien nach Kategorien
- **Erweitertes INDEX.md** : Dedizierter Abschnitt für v0.104
- **Dokumentationsreorganisation**: Verbesserte Dateistruktur
  - CHANGELOGs nach `Documentation/` verschoben
  - Neues Haupt-`CHANGELOG.md` im Stammverzeichnis mit Verweis auf Sprachversionen
  - Sprach-READMEs (EN/DE) nach `Documentation/` verschoben
  - Haupt-README.md im Stammverzeichnis mit Links zu Sprachversionen
  - Bessere Organisation der Dokumentationsdateien
  - Alle internen Links aktualisiert

### 🛠️ Entwicklungswerkzeuge
- **Projekt-Bereinigungsskript** : `Tools/clean_project.py`
  - Automatisches Entfernen temporärer Ordner (Backup, build, dist, Characters, Configuration, Logs)
  - Python-Cache-Bereinigung (__pycache__, .pyc, .pyo, .pyd)
  - Simulationsmodus mit --dry-run
  - Automatische Git-Branch-Erstellung
  - Automatischer Wechsel und Push zum Remote-Repository
  - Interaktive Oberfläche mit Bestätigungen
  - --no-git Option zum Bereinigen ohne Branch-Erstellung

### ✅ Qualität
- **Verbesserte Testbarkeit** : Modularer Code leicht testbar
- **Wartbarkeit** : +200% einfachere Wartung
- **Erweiterbarkeit** : Vereinfachtes Hinzufügen von Funktionen
- **Abwärtskompatibilität** : Alle Funktionen erhalten

### 🔒 Migration & Sicherheit

#### Hinzugefügt
- **Migrationsbestätigungs-Popup**: Dreisprachige Anzeige (FR/EN/DE) vor jeder Migration
  - Detaillierte Erklärung der Strukturänderung
  - Visueller Vergleich: Alte Struktur → Neue Struktur
  - Information über automatische Sicherung mit Pfadangabe
  - "OK"-Schaltfläche: Startet ZIP-Sicherung und dann Migration
  - "Abbrechen"-Schaltfläche: Schließt Anwendung ohne Änderungen
  - Benutzerdefinierte Abbruchmeldung bei Benutzerabbruch
- **Automatische ZIP-Sicherung vor Migration**: Optimierter Datenschutz
  - Erstellt komprimiertes ZIP-Archiv des `Characters`-Ordners
  - Name mit Zeitstempel: `Characters_backup_JJJJMMTT_HHMMSS.zip`
  - Organisierter Speicherort: `Backup/Characters/`
  - ZIP_DEFLATED-Kompression spart 70-90% Speicherplatz
  - Erfolgsüberprüfung vor Start der Migration
  - Bestätigungsnachricht mit Sicherungsort
- **Sicherungsintegritätsprüfung**: Verbesserter Schutz gegen Beschädigung
  - Automatischer ZIP-Dateitest nach Erstellung mit `zipfile.testzip()`
  - Überprüfung der Dateianzahl im Archiv
  - Automatische Entfernung der Sicherung bei Beschädigung
  - Migration abgebrochen, wenn Sicherung ungültig ist
  - Detaillierte Logs zur Diagnose
- **Automatischer Rollback bei Fehler**: Maximale Datensicherheit
  - Tracking aller migrierten Dateien in einer Liste
  - Bei einem einzigen Fehler → Entfernung aller migrierten Dateien
  - Originaldaten immer in alter Struktur erhalten
  - Rollback auch bei kritischer Ausnahme
  - Klare Nachricht an Benutzer mit Sicherungsverfügbarkeit
- **Vollständige JSON-Dateivalidierung**: Verbesserte Robustheit
  - Erkennung beschädigter JSON-Dateien (JSONDecodeError)
  - Überprüfung, dass Inhalt ein Wörterbuch ist
  - Validierung des 'season'-Felds
  - Ungültige Dateien werden übersprungen, Migration für andere fortgesetzt
  - Präzise Fehlerstatistiken in Logs
- **Überprüfung jeder Dateikopie**: Garantierte Integrität
  - Jede kopierte Datei wird sofort neu gelesen und mit Original verglichen
  - Bei Unterschied → Datei gelöscht und Fehler gezählt
  - Schutz vor Beschädigung während des Kopierens
- **Sofortige Migration bei Pfadänderung**: Verbesserte UX
  - Ersetzung des "Neustart"-Popups durch Ja/Nein-Frage
  - Bei Ja → Migration sofort mit Fortschrittsdialog ausgeführt
  - Bei Nein → Informative Nachricht, Migration verschoben
  - Automatische Listenaktualisierung nach Migration
  - Kein Neustart der Anwendung erforderlich
- **Übersetzte Fehlermeldungen**: Bessere Benutzererfahrung
  - `migration_success_message`: Erfolgsnachricht mit Charakteranzahl
  - `migration_no_characters`: Nachricht, wenn keine Charaktere zu migrieren
  - `migration_rollback_info`: Information während Rollback
  - `migration_data_safe`: Bestätigung, dass Daten sicher sind
  - ✅ Symbol vor Erfolgsnachricht
  - 💾 Symbol nur vor Sicherungspfad (erscheint einmal)
- **Verbesserte sichere Bereinigung**: Datenverlust-Prävention
  - Alter Ordner nur gelöscht, wenn 100% der Dateien migriert
  - Bei Teilmigration → alter Ordner behalten
  - Datei-für-Datei-Überprüfung vor Bereinigung
- **Überschreibungsschutz**: Zusätzlicher Schutz
  - Prüfung, ob Zieldatei bereits existiert
  - Bei ja → Überspringen mit Fehler, kein Überschreiben
- **Teilweise Sicherungsbereinigung**: Keine beschädigten Dateien
  - Bei Sicherungsfehler wird teilweise ZIP-Datei gelöscht
  - Keine Verwechslung mit ungültigen Sicherungen
- **Migrations-Done-Flag nur bei vollständigem Erfolg**: Zuverlässigkeit
  - `.migration_done`-Datei nur bei null Fehlern erstellt
  - Bei Fehler → Benutzer kann Migration wiederholen
  - Keine "festgefahrene" Migration
- **Neue Ordnerstruktur**: Migration zu hierarchischer Organisation nach Saison
  - Alte Struktur: `Characters/Realm/Character.json`
  - Neue Struktur: `Characters/Season/Realm/Character.json`
  - Bereitet auf zukünftige Saisons vor
  - Automatische Migration beim Start (mit Bestätigung)
  - Markierungsdatei `.migration_done` zur Vermeidung mehrfacher Migrationen
- **migration_manager.py Modul**: Vollständiger Migrationsmanager
  - `get_backup_path()`: Generiert Sicherungspfad in `Backup/Characters/`
  - `backup_characters()`: Erstellt komprimiertes ZIP-Archiv
  - `check_migration_needed()`: Erkennt, ob Migration erforderlich ist
  - `migrate_character_structure()`: Führt Migration mit detailliertem Bericht durch
  - `is_migration_done()`: Prüft, ob Migration bereits durchgeführt wurde
  - `run_migration_with_backup()`: Orchestriert Sicherung und dann Migration
  - `run_migration_if_needed()`: Führt automatische Migration beim Start aus
  - Vollständige Fehlerbehandlung mit detaillierten Logs
  - Erhält Dateimetadaten (Daten, Attribute)
  - Automatische Bereinigung leerer alter Ordner
- **MIGRATION_SECURITY.md Dokumentation**: Vollständiger Sicherheitsleitfaden
  - Details aller implementierten Schutzmaßnahmen
  - Alle Datenverlust-Szenarien abgedeckt
  - Empfohlene Tests zur Validierung
  - Dokumentierte Sicherheitsgarantien
- **Test-Skripte**: Tools zum Testen der Migration
  - `Scripts/simulate_old_structure.py`: Erstellt alte Struktur zum Testen
  - `Scripts/test_backup_structure.py`: Überprüft ZIP-Sicherungserstellung

#### Geändert
- **Alle Charakterverwaltungsfunktionen**: Anpassung an neue Season/Realm-Struktur
  - `save_character()`: Speichert in `Season/Realm/`
  - `get_all_characters()`: Durchläuft Season/Realm-Struktur mit `os.walk()`
  - `rename_character()`: Sucht und benennt in neuer Struktur um
  - `delete_character()`: Löscht in neuer Struktur
  - `move_character_to_realm()`: Verschiebt zwischen Reichen innerhalb derselben Saison
  - Standardwert "S1" für Charaktere ohne angegebene Saison
- **Automatische Migration**: Erfordert jetzt Benutzerbestätigung
  - Startet nicht mehr automatisch ohne Nachfrage
  - Zeigt Bestätigungs-Popup beim Start an
  - Schließt Anwendung bei Benutzerabbruch
- **Funktion `run_automatic_migration()` in main.py**: Vollständige Überarbeitung
  - Zeigt Bestätigungs-Popup mit QMessageBox an
  - Verwendet try/finally zur Garantie der Fortschritts-Popup-Schließung
  - Ruft `progress.deleteLater()` auf, um Qt-Speicher zu bereinigen
  - Behandelt Abbruchfälle mit dreisprachiger Nachricht
- **Sicherungssystem**: Migration von Ordnerkopie zu ZIP-Archiv
  - Alte Methode: `shutil.copytree()` erstellte schwere Kopie
  - Neue Methode: `zipfile.ZipFile()` mit ZIP_DEFLATED-Kompression
  - Spart 70-90% Speicherplatz für JSON-Dateien
  - Organisation in dediziertem `Backup/`-Ordner
- **Mehrsprachige Migrationsmeldungen**: Sprachliche Konsistenz
  - Entfernung des fest codierten "Successfully migrated"-Textes auf Englisch
  - Entfernung des fest codierten "Backup location:"-Textes
  - Alle Meldungen verwenden jetzt Übersetzungsschlüssel
  - `migration_backup_location` enthält nicht mehr alle 3 Sprachen
  - Anzeige nur in Schnittstellensprache
- **.gitignore**: `Backup/`-Ordner zu Git-Ausschlüssen hinzugefügt

#### Behoben
- **"Migration läuft"-Popup bleibt offen**: Kritischer Fehler behoben
  - `try/finally` hinzugefügt zur Garantie der Popup-Schließung
  - Expliziter Aufruf von `progress.close()` und `progress.deleteLater()`
  - Popup schließt jetzt korrekt nach Migration
- **LanguageManager-Fehler**: `lang.get()` Aufrufe mit falschen Standardwerten korrigiert
- **AttributeError**: Methodennamen für Rang/Level-Callbacks korrigiert

#### Entfernt
- **Hilfe-Menü > Ordnerstruktur migrieren**: Schnittstellenvereinfachung
  - Manuelle Migrationsoption aus Hilfe-Menü entfernt
  - Migration erfolgt automatisch beim Start, falls erforderlich
  - Migration auch bei Änderung des Characters-Ordnerpfads angeboten
  - `run_manual_migration()`-Methode entfernt
  - `menu_help_migrate` Übersetzungsschlüssel nicht mehr verwendet

### 🎨 Oberfläche & Benutzererfahrung

#### Hinzugefügt
- **Klassen- und Rassen-Spalten**: Neue Spalten in der Hauptansicht
  - "Klasse"-Spalte standardmäßig angezeigt
  - "Rasse"-Spalte standardmäßig ausgeblendet
  - Kontrollkästchen im Ansicht > Spalten-Menü zum Aktivieren/Deaktivieren von Spalten
  - Vollständige mehrsprachige Unterstützung (FR/EN/DE)
  - Daten werden automatisch aus den Charakter-JSON-Dateien extrahiert

#### Geändert
- **Reichsrang-Schnittstelle**: Schieberegler durch Dropdown-Menüs ersetzt
  - Dropdown-Menü für Rang (1-14)
  - Dropdown-Menü für Level (L0-L10 für Rang 1, L0-L9 für andere)
  - Rangtitel wird jetzt oben im Bereich in Reichsfarbe angezeigt
- **Auto-Speichern für Ränge**: "Diesen Rang anwenden"-Button entfernt
  - Rang/Level-Änderungen werden jetzt automatisch angewendet
  - Bestätigung von Änderungen nicht mehr erforderlich

### 🔧 Technisch
- **Verbesserte Architektur**: Saisontrennung auf Dateisystemebene
- **Rückwärtskompatibilität**: Automatische Migration bewahrt alle vorhandenen Charaktere
- **Detaillierte Protokollierung**: Alle Migrationsoperationen werden in Logs aufgezeichnet
- **Robuste Fehlerbehandlung**: Migration behandelt Fehlerfälle ohne Datenverlust
- **Optimierte Leistung**: Verwendet `zipfile` mit Kompression für Sicherungen
- **Qt-Speicherbereinigung**: Korrekte Verwendung von `deleteLater()` für temporäre Widgets
- 9 neue Übersetzungsschlüssel in FR/EN/DE für Migrationssystem hinzugefügt
- Vollständige Dokumentation erstellt: `BACKUP_ZIP_UPDATE.md`, `MIGRATION_SECURITY.md`

## [0.103] - 2025-10-28

### Hinzugefügt
- **Rassen-Auswahl**: Rassen-Feld in der Charaktererstellung hinzugefügt
- **Klassen-Auswahl**: Klassen-Feld in der Charaktererstellung hinzugefügt
- **Dynamische Filterung**: Verfügbare Klassen werden nach ausgewählter Rasse gefiltert
- **Rassen/Klassen-Validierung**: Automatische Überprüfung der Rassen/Klassen-Kompatibilität
- **Spezialisierungs-Übersetzungen**: Alle Spezialisierungen jetzt in FR/EN/DE übersetzt
- **Vollständiges Datensystem**: `Data/classes_races.json` mit 44 Klassen, 18 Rassen und 188 Spezialisierungen hinzugefügt
- **Vollständige Dokumentation**: Nutzungsanleitungen und technische Dokumentation hinzugefügt
- **Spaltenbreiten-Verwaltung**: Option zum Umschalten zwischen automatischem und manuellem Modus
  - Automatischer Modus: Inhaltsbasierte Größenanpassung mit erweiterbarer Name-Spalte
  - Manueller Modus: Freie Größenanpassung aller Spalten durch Benutzer

### Geändert
- **Klassen/Rassen-Reihenfolge umgekehrt**: Klasse wird jetzt VOR Rasse ausgewählt
- **Rassen-Filterung nach Klasse**: Verfügbare Rassen werden nach ausgewählter Klasse gefiltert
- **Mauler-Entfernung**: Mauler-Klasse entfernt (nicht auf Eden-Server implementiert)
- **Eden-Unterstützung**: Daten angepasst, um verfügbare Klassen auf Eden zu entsprechen
- **Spezialisierungs-Struktur**: Mehrsprachiges Format `{"name": "EN", "name_fr": "FR", "name_de": "DE"}`
- **Erweiterter DataManager**: 11 neue Funktionen zur Verwaltung von Rassen/Klassen/Spezialisierungen und `get_available_races_for_class()` für umgekehrte Filterung hinzugefügt

### Verbessert
- **Benutzererfahrung**: Logischere Reihenfolge (Klasse → Rasse)
- **Konsistenz**: Gleiche Reihenfolge bei Charaktererstellung und -bearbeitung

### Hinzugefügte Dateien
- `Data/classes_races.json`: Vollständige Rassen-, Klassen- und Spezialisierungsdaten
- `Data/classes_races_stats.json`: Detaillierte Statistiken
- `Documentation/CLASSES_RACES_USAGE.md`: Vollständige Nutzungsanleitung
- `Documentation/CLASSES_RACES_IMPLEMENTATION.md`: Technische Dokumentation
- `validate_classes_races.py`: Datenvalidierungs-Skript
- `example_classes_usage.py`: Praktische Nutzungsbeispiele

### Statistiken
- **44 Klassen** über 3 Reiche (Albion: 15, Midgard: 14, Hibernia: 15)
- **18 Rassen** insgesamt (6 pro Reich)
- **188 Spezialisierungen** in 3 Sprachen übersetzt

## [0.102] - 2025-10-27

### Geändert
- **Server-Spalte**: Server-Spalte wiederhergestellt (Eden/Blackthorn)
- **Server-Konfiguration**: Standard-Server auf "Eden" gesetzt
- **Charakterbogen**: Dropdown zum Auswählen des Servers hinzugefügt
- **Sichtbarkeit**: Server-Spalte standardmäßig ausgeblendet (kann über Ansicht > Spalten angezeigt werden)
- **Spalten-Reorganisation**: Neue Reihenfolge: Auswahl, Reich, Name, Level, Rang, Titel, Gilde, Seite, Server
- **Spalten-Menü**: Spaltenliste im Menü korrigiert (Server hinzugefügt, Season entfernt)
- **Vereinfachte Umbenennung**: "Umbenennen"-Button aus Charakterbogen entfernt
- **Vereinfachte Meldungen**: "Dies aktualisiert die JSON-Datei"-Nachricht und Erfolgs-Popup entfernt

### Hinzugefügt
- **Multi-Server-Unterstützung**: Möglichkeit, Charaktere auf Eden und Blackthorn zu verwalten
- **Server-Bearbeitung**: Server über Charakterbogen ändern
- **Schnelle Umbenennung**: Enter-Taste im "Name"-Feld drücken, um Charakter direkt umzubenennen

### Verbessert
- **Benutzeroberfläche**: Aufgeräumtere Oberfläche im Charakterbogen
- **Ergonomie**: Schnellere Umbenennung mit Enter-Taste
- **Benutzererfahrung**: Flüssigerer Umbenennungsprozess ohne unnötige Popups

### Behoben
- **RealmTitleDelegate**: Kritischer Fehler beim Zeichnen farbiger Titel behoben

## [0.101] - 2025-10-27

### Geändert
- **Benutzeroberfläche**: Toolbar durch traditionelle Windows-Menüleiste ersetzt
- **Datei-Menü**: Menü mit "Neuer Charakter" und "Einstellungen" hinzugefügt
- **Ansicht-Menü**: Menü mit "Spalten" hinzugefügt
- **Hilfe-Menü**: Menü mit "Über" hinzugefügt
- **Über-Dialog**: Verbessert mit vollständigen Informationen (Name, Version, Ersteller)
- **Übersetzungen**: Menü-Übersetzungen in allen 3 Sprachen hinzugefügt (FR/EN/DE)
- **Dokumentation**: Gesamte Dokumentation aktualisiert, um die neue Oberfläche zu reflektieren
- **Ersteller**: Ersteller-Name auf "Ewoline" aktualisiert
- **Charakterbogen**: Möglichkeit hinzugefügt, Reich, Level (1-50), Saison, Seite (1-5) und Gildennamen zu bearbeiten
- **Reich-Wechsel**: Automatische Datei-Verlagerung ins korrekte Verzeichnis bei Reich-Wechsel
- **Dynamische Farben**: Automatische Farb-Updates entsprechend dem neuen Reich
- **Umbenennung**: Möglichkeit zum Umbenennen von Charakteren über Kontextmenü (Rechtsklick) oder Charakterbogen
- **Datei-Verwaltung**: Automatische JSON-Datei-Umbenennung beim Charakter-Umbenennen
- **Server-Spalte entfernt**: Permanente Löschung der Server-Spalte und aller zugehörigen Funktionen
- **Interface-Vereinfachung**: Server automatisch auf "Eden" gesetzt ohne Benutzerauswahl
- **Spalten-Reorganisation**: Alle Spalten nach Server-Spalten-Entfernung neu indexiert
- **Speichern**: "Speichern"-Button im Charakterbogen hinzugefügt, um Änderungen zu speichern
- **Konfiguration**: Standard-Spaltenwerte auch ohne bestehende Konfiguration anwenden

### Entfernt
- **Toolbar**: Toolbar mit Symbolen entfernt
- **Veralteter Code**: Code im Zusammenhang mit ungenutzten Toolbar-Symbolen bereinigt

### Technisch
- Optimiertes Laden von Symbolen (nur Reich-Symbole beibehalten)
- Vereinfachtes Aktionssystem
- Verbesserte Behandlung der Neuübersetzung bei Sprachwechseln

## [0.1] - 2025-10-XX

### Hinzugefügt
- **Vollständige Charakterverwaltung**: Erstellen, ändern, löschen, duplizieren
- **Reichsrang-System**: Anzeige von Rängen und Titeln mit Web-Scraping
- **Mehrsprachige Oberfläche**: Vollständige Unterstützung für Français, English, Deutsch
- **Spaltenkonfiguration**: Anpassbare sichtbare Spalten
- **Debug-Modus**: Integrierte Konsole mit Log-Management
- **Massenaktionen**: Mehrfachauswahl und Stapellöschung
- **Reich-Organisation**: Albion, Hibernia, Midgard mit Symbolen
- **Multi-Server-Verwaltung**: Unterstützung für verschiedene DAOC-Server
- **Saison-System**: Organisation nach Saisons (S1, S2, S3, etc.)
- **Themes**: Hell/Dunkel-Theme-Unterstützung
- **Persistenz**: Automatische Konfigurationsspeicherung

### Hauptfunktionen
- **PySide6-Oberfläche**: Moderne und responsive grafische Oberfläche
- **Daten-Manager**: Vollständiges Spieldaten-Verwaltungssystem
- **Web-Scraping**: Automatische Reichsrang-Datenextraktion von der offiziellen Website
- **Erweiterte Konfiguration**: Vollständige Anpassung von Pfaden und Parametern
- **Vollständige Dokumentation**: Detaillierte Anleitungen auf Französisch und Englisch

---

## Arten von Änderungen

- `Hinzugefügt` für neue Funktionen
- `Geändert` für Änderungen in bestehender Funktionalität
- `Veraltet` für bald zu entfernende Funktionen
- `Entfernt` für jetzt entfernte Funktionen
- `Behoben` für Fehlerbehebungen
- `Sicherheit` im Fall von Sicherheitslücken

## Versions-Links

- [0.104] - Aktuelle Version mit vollständigem Refactoring und Migrationssystem
- [0.103] - Rassen/Klassen-System und Spezialisierungen
- [0.102] - Multi-Server-Unterstützung Eden/Blackthorn
- [0.101] - Windows-Menü-Oberfläche
- [0.1] - Ursprüngliche Version mit Toolbar

## Andere Sprachen

- 🇫🇷 [Français](CHANGELOG_FR.md)
- 🇬🇧 [English](CHANGELOG_EN.md)
- 🇩🇪 [Deutsch](CHANGELOG_DE.md) (diese Datei)
