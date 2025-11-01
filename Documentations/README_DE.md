# DAOC - Charakterverwaltung v0.104

> 📁 **Diese Datei wurde verschoben**: Früher im Stammverzeichnis, jetzt in `Documentation/` (v0.104)

Charakterverwaltungsanwendung für Dark Age of Camelot (DAOC), entwickelt in Python mit PySide6.

**🌍 Verfügbar in:** [Français](../README.md) | [English](README_EN.md) | **Deutsch**

## 📦 Download

**Aktuelle Version: v0.104**

[![Download Ausführbare Datei](https://img.shields.io/badge/Download-EXE-blue?style=for-the-badge&logo=windows)](https://github.com/ChristophePelichet/DAOC-Character-Management/releases/latest)

➡️ [Download DAOC-Character-Manager.exe](https://github.com/ChristophePelichet/DAOC-Character-Management/releases/latest)

*Keine Installation erforderlich - portable ausführbare Windows-Datei*

## 🎮 Funktionen

### Charakterverwaltung
- ✅ **Erstellen** von neuen Charakteren mit Rasse und Klasse
- ✅ **Dynamische Auswahl** von Klassen basierend auf der Rasse
- ✅ **Automatische Validierung** von Rassen-/Klassen-Kombinationen
- ✅ **Bearbeiten** von Rasse und Klasse im Charakterbogen
- ✅ **Umbenennen** von vorhandenen Charakteren
- ✅ **Duplizieren** von Charakteren
- ✅ **Löschen** von Charakteren (einzeln oder in Masse)
- ✅ **Anzeigen** von vollständigen Details jedes Charakters

### Rassen & Klassen
- 🎭 **44 Klassen** verfügbar über 3 Reiche
- 👤 **18 spielbare Rassen** (6 pro Reich)
- 📚 **188 Spezialisierungen** übersetzt in DE/EN/FR
- ✅ **Intelligente Filterung**: nur Klassen, die mit der gewählten Rasse kompatibel sind, werden angezeigt
- 🌍 **Vollständige Übersetzungen**: Rassen, Klassen und Spezialisierungen in 3 Sprachen

### Organisation
- 📁 Organisation nach **Reich** (Albion, Hibernia, Midgard)
- 🏷️ Filter nach **Saison** (S1, S2, S3, usw.)
- 🖥️ Multi-**Server** Verwaltung (Eden, Blackthorn, usw.)
- 📊 Tabelle mit sortierbaren Spalten

### Reichsränge
- 🏆 **Anzeige** von Reichsrang und Titel
- 📈 **Dropdown-Anpassung** des Ranges (Rang 1-14, Level 0-9/10)
- 💾 **Auto-Speichern** von Rang/Level-Änderungen
- 🎨 **Farbige Titel** nach Reich (rot für Albion, grün für Hibernia, blau für Midgard)
- 📊 **Automatische Berechnung** basierend auf Reichspunkten

### Rüstung & Widerstände *(Demnächst)*
- 🛡️ **Rüstungsbereich** für Ausrüstungsverwaltung
- ⚔️ **Widerstände**: Funktion in Vorbereitung

### Erweiterte Konfiguration
- 🌍 **Mehrsprachig**: Français, English, Deutsch
- 🔧 **Anpassung** der Pfade (Charaktere, Logs, Konfiguration)
- 📋 **Konfigurierbare Spalten**: Gewünschte Spalten ein-/ausblenden
- 🐛 **Debug-Modus** mit integrierter Konsole

## 📋 Konfigurierbare Spalten

Sie können die Spaltenanzeige über das Menü **Ansicht > Spalten** anpassen.

Verfügbare Spalten:
- **Auswahl**: Kontrollkästchen für Massenaktionen
- **Reich**: Reich-Symbol
- **Saison**: Charakter-Saison
- **Server**: Charakter-Server (standardmäßig ausgeblendet)
- **Name**: Charaktername
- **Level**: Charakter-Level
- **Rang**: Reichsrang (z.B.: 5L7)
- **Titel**: Rang-Titel (z.B.: Challenger)
- **Gilde**: Gildenname
- **Seite**: Charakter-Seite (1-5)
- **Klasse**: Charakter-Klasse (standardmäßig angezeigt)
- **Rasse**: Charakter-Rasse (standardmäßig ausgeblendet)

Siehe [COLUMN_CONFIGURATION_EN.md](COLUMN_CONFIGURATION_EN.md) (EN) für weitere Details.

## 🚀 Installation

### Voraussetzungen
- Python 3.13 oder höher (⚠️ PySide6 ist nicht mit Python 3.14+ kompatibel)
- Windows, macOS oder Linux

### Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### Anwendung starten

```bash
python main.py
```

## 📦 Abhängigkeiten

- **PySide6**: Qt6 grafische Oberfläche
- **requests**: HTTP-Anfragen für Web-Scraping
- **beautifulsoup4**: HTML-Parsing
- **lxml**: XML/HTML-Parser
- **urllib3**: HTTP-Anfragenverwaltung

## 📊 Reichsrang-Daten

Um Reichsrang-Daten von der offiziellen DAOC-Website zu aktualisieren:

```bash
python scrape_realm_ranks.py
```

Siehe [DATA_MANAGER_EN.md](DATA_MANAGER_EN.md) (EN) für weitere Informationen zur Datenverwaltung.

## 📚 Dokumentation

Vollständige Dokumentation verfügbar im `Documentation/` Ordner:

### Français 🇫🇷
- [Configuration des Colonnes](CONFIGURATION_COLONNES_FR.md)
- [Système Realm Ranks](REALM_RANKS_FR.md)
- [Gestionnaire de Données](DATA_MANAGER_FR.md)
- [Dossier Data](DATA_FOLDER_FR.md)
- [Menu Interface](INTERFACE_MENU_FR.md)

### English 🇬🇧
- [Column Configuration](COLUMN_CONFIGURATION_EN.md)
- [Realm Ranks System](REALM_RANKS_EN.md)
- [Data Manager](DATA_MANAGER_EN.md)
- [Data Folder](DATA_FOLDER_EN.md)
- [Menu Interface](INTERFACE_MENU_EN.md)

## 🗂️ Projektstruktur

```
DAOC---Gestion-des-personnages/
├── 📄 Root-Dateien
│   ├── main.py                          # Hauptanwendung (493 Zeilen - v0.104)
│   ├── requirements.txt                 # Python-Projektabhängigkeiten
│   ├── CHANGELOG.md                     # Änderungsprotokoll
│   ├── README.md                        # Haupt-README (Französisch)
│   ├── .gitignore                       # Von Git ausgeschlossene Dateien
│   └── .gitattributes                   # Git-Konfiguration
│
├── 📁 Characters/                       # ⭐ Charakterdaten (Season/Realm-Struktur v0.104)
│   ├── S1/                              # Saison 1
│   │   ├── Albion/                      # Albion S1-Charaktere
│   │   │   └── *.json                   # Charakterdateien
│   │   ├── Hibernia/                    # Hibernia S1-Charaktere
│   │   └── Midgard/                     # Midgard S1-Charaktere
│   ├── S2/                              # Saison 2
│   │   ├── Albion/
│   │   ├── Hibernia/
│   │   └── Midgard/
│   ├── S3/                              # Saison 3
│   │   ├── Albion/
│   │   ├── Hibernia/
│   │   └── Midgard/
│   └── .migration_done                  # Migrations-Markierung
│
├── 📁 Backup/                           # Automatische Sicherungen
│   └── Characters/                      # ZIP-Sicherungen vor Migration
│       └── Characters_backup_*.zip      # Format: JJJJMMTT_HHMMSS.zip
│
├── 📁 Configuration/                    # Anwendungseinstellungen
│   └── config.json                      # Benutzerkonfiguration
│
├── 📁 Data/                             # Spieldaten (Referenz)
│   ├── realm_ranks.json                 # Konsolidierte Ränge (3 Reiche)
│   ├── realm_ranks_albion.json          # Albion-spezifische Ränge
│   ├── realm_ranks_hibernia.json        # Hibernia-spezifische Ränge
│   ├── realm_ranks_midgard.json         # Midgard-spezifische Ränge
│   ├── classes_races.json               # 44 Klassen, 18 Rassen, 188 Spezialisierungen
│   ├── classes_races_stats.json         # Klassen-/Rassen-Statistiken
│   ├── armor_resists.json               # Widerstände nach Rüstungstyp
│   └── README.md                        # Data-Ordner-Dokumentation
│
├── 📁 Documentation/                    # Vollständige Dokumentation (FR/EN/DE)
│   ├── 📋 Hauptdateien
│   │   ├── INDEX.md                     # Dokumentationsindex
│   │   ├── README_EN.md                 # Englisches README
│   │   └── README_DE.md                 # Deutsches README
│   ├── 📝 Änderungsprotokolle
│   │   ├── CHANGELOG_FR.md              # Französisches Änderungsprotokoll
│   │   ├── CHANGELOG_EN.md              # Englisches Änderungsprotokoll
│   │   └── CHANGELOG_DE.md              # Deutsches Änderungsprotokoll
│   ├── 🎮 Benutzerhandbücher
│   │   ├── CONFIGURATION_COLONNES_FR.md # Spaltenkonfiguration (FR)
│   │   ├── COLUMN_CONFIGURATION_EN.md   # Spaltenkonfiguration (EN)
│   │   ├── REALM_RANKS_FR.md            # Realm Ranks-System (FR)
│   │   ├── REALM_RANKS_EN.md            # Realm Ranks-System (EN)
│   │   ├── INTERFACE_MENU_FR.md         # Oberflächen-Menü (FR)
│   │   ├── INTERFACE_MENU_EN.md         # Oberflächen-Menü (EN)
│   │   ├── ACTION_MENU_FR.md            # Aktionsmenü (FR)
│   │   ├── ARMOR_MANAGEMENT_FR.md       # Rüstungsverwaltung (FR)
│   │   └── ARMOR_MANAGEMENT_USER_GUIDE_FR.md  # Rüstungs-Benutzerhandbuch (FR)
│   ├── 🔧 Technische Handbücher
│   │   ├── DATA_MANAGER_FR.md           # Datenmanager (FR)
│   │   ├── DATA_MANAGER_EN.md           # Datenmanager (EN)
│   │   ├── DATA_FOLDER_FR.md            # Data-Ordner (FR)
│   │   ├── DATA_FOLDER_EN.md            # Data-Ordner (EN)
│   │   ├── CLASSES_RACES_IMPLEMENTATION.md    # Klassen-/Rassen-Implementierung
│   │   ├── CLASSES_RACES_USAGE.md       # Klassen-/Rassen-Verwendung
│   │   └── DATA_EDITOR_README.md        # Data Editor-Handbuch
│   └── 📊 v0.104 Dokumentation
│       ├── REFACTORING_v0.104_COMPLETE.md     # Vollständiger Refactoring-Leitfaden
│       ├── REFACTORING_SUMMARY_v0.104.md      # Refactoring-Zusammenfassung
│       ├── REFACTORING_FINAL_REPORT_v0.104.md # Abschlussbericht mit Metriken
│       ├── REFACTORING_SUMMARY.md       # Allgemeine Zusammenfassung
│       ├── IMPLEMENTATION_COMPLETE.md   # Vollständige Implementierung
│       ├── IMPLEMENTATION_SUMMARY_ARMOR_v0.105.md  # Rüstungs-Zusammenfassung v0.105
│       ├── ACTION_MENU_IMPLEMENTATION_SUMMARY.md   # Aktionsmenü-Zusammenfassung
│       ├── BACKUP_ZIP_UPDATE.md         # ZIP-Backup-Update
│       ├── MIGRATION_CONFIRMATION_UPDATE.md    # Migrationsbestätigungs-Update
│       ├── MIGRATION_MULTILANG_UPDATE.md       # Mehrsprachiges Migrations-Update
│       ├── MIGRATION_SECURITY.md        # Migrationssicherheit
│       ├── UPDATE_SUMMARY_29OCT2025.md  # Update-Zusammenfassung 29. Okt. 2025
│       └── VERIFICATION_RAPPORT.md      # Verifizierungsbericht
│
├── 📁 Functions/                        # ⭐ Python-Module (Modulare Architektur v0.104)
│   ├── __init__.py                      # Python-Paket-Markierung
│   ├── 🎨 Oberflächen-Manager (v0.104)
│   │   ├── ui_manager.py                # Menüs, Dialoge, Statusleiste (127 Zeilen)
│   │   ├── tree_manager.py              # Charakterliste, QTreeView (297 Zeilen)
│   │   └── character_actions_manager.py # Charakter-CRUD-Aktionen (228 Zeilen)
│   └── 🔧 Funktionale Manager
│       ├── character_manager.py         # Charakterdateiverwaltung
│       ├── config_manager.py            # JSON-Konfigurationsverwaltung
│       ├── data_manager.py              # Spieldaten-Laden
│       ├── language_manager.py          # Mehrsprachige Übersetzungen
│       ├── logging_manager.py           # Logging-System
│       ├── migration_manager.py         # Season/Realm-Migration mit Backup
│       ├── path_manager.py              # Pfadverwaltung
│       └── armor_manager.py             # Rüstungsverwaltung
│
├── 📁 UI/                               # Benutzeroberflächenkomponenten
│   ├── __init__.py                      # Python-Paket-Markierung
│   ├── dialogs.py                       # Benutzerdefinierte Dialoge (Erstellung, Bearbeitung)
│   ├── delegates.py                     # QTreeView-Delegaten (Spalten-Rendering)
│   └── debug_window.py                  # Integrierte Debug-Konsole
│
├── 📁 Img/                              # Grafikressourcen
│   ├── albion.png                       # Albion-Reich-Symbol
│   ├── hibernia.png                     # Hibernia-Reich-Symbol
│   └── midgard.png                      # Midgard-Reich-Symbol
│
├── 📁 Language/                         # Mehrsprachige Übersetzungen
│   ├── fr.json                          # Französische Übersetzungen (Standardsprache)
│   ├── en.json                          # Englische Übersetzungen
│   └── de.json                          # Deutsche Übersetzungen
│
├── 📁 Logs/                             # Anwendungsprotokollierung
│   └── debug.log                        # Debug-Protokolle (automatisch erstellt)
│
├── 📁 Scripts/                          # Hilfs- und Wartungsskripte
│   ├── 🌐 Web Scraping
│   │   ├── scrape_realm_ranks.py        # Ränge von DAOC-Site extrahieren
│   │   ├── scrape_armor_resists.py      # Rüstungswiderstände extrahieren
│   │   └── add_armor_translations.py    # FR/DE-Übersetzungen hinzufügen
│   ├── 📊 Datenverwaltung
│   │   ├── update_classes_races.py      # Klassen/Rassen aktualisieren
│   │   └── validate_classes_races.py    # Klassen-/Rassen-Daten validieren
│   ├── 🎨 Grafik
│   │   ├── create_icons.py              # Symbol-Erstellung
│   │   ├── create_simple_icons.py       # Vereinfachte Symbole
│   │   └── check_png.py                 # PNG-Integritätsprüfung
│   ├── 🧪 Tests
│   │   ├── test_armor_manager.py        # Rüstungsverwaltungs-Tests
│   │   ├── test_column_configuration.py # Spaltenkonfigurations-Tests
│   │   ├── test_dynamic_data.py         # Dynamische Daten-Tests
│   │   ├── test_realm_ranks_ui.py       # Realm Ranks UI-Tests
│   │   └── test_run.py                  # Allgemeine Test-Suite
│   ├── 📝 Beispiele
│   │   ├── example_classes_usage.py     # Klassen-Verwendungsbeispiele
│   │   └── example_integration.py       # Integrationsbeispiele
│   └── 🔧 Dienstprogramme
│       ├── watch_logs.py                # Echtzeit-Protokollüberwachung
│       ├── analyse_gestion_erreurs.md   # Fehleranalyse
│       └── CORRECTIONS_ICONES.md        # Symbol-Korrekturen-Dokumentation
│
└── 📁 Tools/                            # ⭐ Entwicklungswerkzeuge (v0.104)
    ├── clean_project.py                 # Projekt-Bereinigung + Git-Branch-Erstellung
    ├── generate_test_characters.py      # 20 Testcharaktere generieren (Season/Realm)
    ├── generate_test_characters_old.py  # Legacy-Version (nur Realm)
    ├── data_editor.py                   # Visueller JSON-Dateneditor
    ├── DAOC-Character-Manager.spec      # PyInstaller-Konfiguration für EXE-Erstellung
    └── requirements.txt                 # Abhängigkeiten für EXE-Kompilierung
```

**Legende:**
- ⭐ = Neue Funktionen oder größere Änderungen v0.104
- 📁 = Ordner
- 📄 = Wichtige Datei
- 🎨/🔧/🌐/📊/🧪/📝 = Funktionskategorien
│   ├── fr.json
│   ├── en.json
│   └── de.json
└── Logs/                        # Log-Dateien
```

## ⚙️ Konfiguration

Die Konfiguration ist über das Menü **Datei > Einstellungen** zugänglich.

### Verfügbare Optionen:
- 📁 **Verzeichnisse**: Charaktere, Konfiguration, Logs
- 🌍 **Sprache**: Français, English, Deutsch
- 🎨 **Thema**: Hell / Dunkel
- 🖥️ **Standard-Server**: Eden, Blackthorn, usw.
- 📅 **Standard-Saison**: S1, S2, S3, usw.
- 🐛 **Debug-Modus**: Detaillierte Logs aktivieren/deaktivieren

## 🔄 Strukturmigration

**Wichtig**: Ab Version 0.104 hat sich die Ordnerstruktur geändert, um Charaktere besser nach Saison zu organisieren.

### Aktuelle Struktur (v0.104+)
```
Characters/
└── Season/              # S1, S2, S3, usw.
    └── Realm/           # Albion, Hibernia, Midgard
        └── Character.json
```

### Automatische Migration mit Sicherung
- **Bestätigungs-Popup**: Beim ersten Start erklärt ein Dialog die Migration
  - Visueller Vergleich: Alte Struktur → Neue Struktur
  - Information über automatische Sicherung
  - "OK"-Button: Startet Sicherung und dann Migration
  - "Abbrechen"-Button: Schließt Anwendung ohne Änderungen
- **Automatische Sicherung**: Vor jeder Migration wird eine vollständige Sicherung erstellt
  - Format: Komprimiertes ZIP-Archiv (`Characters_backup_JJJJMMTT_HHMMSS.zip`)
  - Speicherort: `Backup/Characters/`
  - Schützt Ihre Daten im Falle von Problemen
- **Sichere Migration**: Ihre vorhandenen Charaktere bleiben erhalten und werden in die neue Struktur verschoben
- Eine `.migration_done` Markierungsdatei wird erstellt, um mehrfache Migrationen zu vermeiden

## 🎯 Verwendung

### Charakter erstellen
1. Gehen Sie zum Menü **Datei > Neuer Charakter**
2. Geben Sie Namen ein, wählen Sie Reich, Saison und Server
3. Klicken Sie auf "OK"

### Charakter umbenennen
1. Doppelklicken Sie auf einen Charakter, um seinen Bogen zu öffnen
2. Ändern Sie den Namen im "Name"-Feld
3. Drücken Sie **Enter** zum Umbenennen
4. Bestätigen Sie die Umbenennung im Dialog

### Reichsrang anpassen
1. Doppelklicken Sie auf einen Charakter, um seinen Bogen zu öffnen
2. Verwenden Sie Schieberegler, um Rang (1-14) und Level (1-9/10) anzupassen
3. Klicken Sie auf "Diesen Rang anwenden" zum Speichern

### Sichtbare Spalten konfigurieren
1. Gehen Sie zum Menü **Ansicht > Spalten**
2. Aktivieren/deaktivieren Sie Spalten zur Anzeige (einschließlich Server-Spalte)
3. Klicken Sie auf "OK" zum Speichern

### Spaltenbreite verwalten
Um zwischen automatischem und manuellem Modus zu wählen:
1. Öffnen Sie die Konfiguration über **Datei > Einstellungen**
2. Aktivieren/deaktivieren Sie unter "Allgemeine Einstellungen" die Option "Manuelle Spaltengrößenanpassung"
3. Automatischer Modus (Standard): Spalten passen sich automatisch dem Inhalt an
4. Manueller Modus: Sie können jede Spalte frei durch Ziehen der Trennlinien anpassen
5. Klicken Sie auf "Speichern" und starten Sie die Anwendung neu

### Massenaktionen
1. Markieren Sie Charaktere in der "Auswahl"-Spalte
2. Verwenden Sie das Dropdown-Menü "Massenaktionen"
3. Wählen Sie "Auswahl löschen" und klicken Sie auf "Ausführen"

## 🐛 Debugging

Um den Debug-Modus zu aktivieren:
1. Öffnen Sie die Konfiguration über **Datei > Einstellungen**
2. Aktivieren Sie "Debug-Modus aktivieren"
3. Starten Sie die Anwendung neu
4. Überprüfen Sie Logs in `Logs/debug.log`

## 📝 Versionshinweise

Siehe das [Änderungsprotokoll](../CHANGELOG.md) für vollständige Historie.  
**🌍 Verfügbar in:** [Français](CHANGELOG_FR.md) | [English](CHANGELOG_EN.md) | [Deutsch](CHANGELOG_DE.md)

### Version 0.104 (29. Oktober 2025) - Vollständiges Refactoring & Migration ✨
- ⚡ **Leistung**: -22% Ladezeit, -33% Aktualisierungszeit
- 🏗️ **Modulare Architektur**: Code in dedizierte Manager extrahiert
  - `Functions/ui_manager.py`: UI-Elementverwaltung (Menüs, Statusleiste)
  - `Functions/tree_manager.py`: Charakterlistenverwaltung
  - `Functions/character_actions_manager.py`: Charakteraktionen
- 🧹 **Code-Bereinigung**: main.py von 1277 auf 493 Zeilen reduziert (-61%)
- 📦 **Optimierungen**: Icon-Caching, reduzierte redundante Aufrufe
- 🗑️ **Aufräumen**: Veraltete Testskripte entfernt
- 📚 **Dokumentation**: Neue vollständige Refactoring-Anleitung
- ✅ **Kompatibilität**: Alle Funktionen erhalten
- 🎯 **Testbarkeit**: Modularer Code leichter zu testen
- 🔄 **Sichere Migration mit automatischer Sicherung**
  - Dreisprachiges Bestätigungs-Popup (FR/EN/DE) vor Migration
  - Automatische ZIP-Sicherung in `Backup/Characters/`
  - Format: `Characters_backup_JJJJMMTT_HHMMSS.zip`
  - Optimale Komprimierung zur Speicherplatzeinsparung
  - Vollständiger Datenschutz vor jeder Änderung
- 📁 **Neue Ordnerstruktur**: Organisation nach Saison
  - Alt: `Characters/Realm/` → Neu: `Characters/Season/Realm/`
  - Automatische Migration beim ersten Start
  - Markierungsdatei `.migration_done` zur Vermeidung mehrfacher Migrationen
- 📋 **Klassen- und Rassen-Spalten**: Neue Spalten in der Hauptansicht
  - "Klasse"-Spalte standardmäßig angezeigt
  - "Rasse"-Spalte standardmäßig ausgeblendet
  - Konfiguration über Ansicht > Spalten-Menü
- 🏆 **Verbesserte Reichsrang-Schnittstelle**: Schieberegler durch Dropdown-Menüs ersetzt
- 💾 **Auto-Speichern für Ränge**: Kein Klick auf "Diesen Rang anwenden" mehr erforderlich
- 🎨 **Visuelle Organisation**: Rangtitel oben in Reichsfarbe angezeigt
- 🐛 **Korrekturen**: "Migration läuft"-Popup, das offen blieb, behoben

Siehe [REFACTORING_v0.104_COMPLETE.md](REFACTORING_v0.104_COMPLETE.md) für alle Refactoring-Details.

### Version 0.103 (28. Oktober 2025)
- ✅ **Rassen-Auswahl**: Rassen-Feld in der Charaktererstellung hinzugefügt
- ✅ **Klassen-Auswahl**: Klassen-Feld in der Charaktererstellung hinzugefügt
- ✅ **Dynamische Filterung**: Verfügbare Klassen nach ausgewählter Rasse gefiltert (und umgekehrt)
- ✅ **Rassen/Klassen-Validierung**: Automatische Überprüfung der Rassen/Klassen-Kompatibilität
- ✅ **Spezialisierungs-Übersetzungen**: Alle Spezialisierungen in FR/EN/DE übersetzt
- ✅ **Vollständiges Datensystem**: 44 Klassen, 18 Rassen und 188 Spezialisierungen
- ✅ **Optimierte Reihenfolge**: Klasse VOR Rasse ausgewählt für logischeren Workflow
- ✅ **Eden-Unterstützung**: Daten für Eden-Server angepasst (ohne Mauler)
- ✅ **Spaltenbreiten-Verwaltung**: Automatischer oder manueller Modus für Spaltengrößenanpassung

### Version 0.102 (27. Oktober 2025)
- ✅ **Server-Spalte**: Server-Spalte wiederhergestellt (Eden/Blackthorn)
- ✅ **Server-Konfiguration**: Standard-Server auf "Eden" gesetzt
- ✅ **Charakterbogen**: Dropdown zum Auswählen des Servers hinzugefügt
- ✅ **Sichtbarkeit**: Server-Spalte standardmäßig ausgeblendet (anzeigbar über Ansicht > Spalten)
- ✅ **Spalten-Reorganisation**: Neue Reihenfolge: Auswahl, Reich, Name, Level, Rang, Titel, Gilde, Seite, Server
- ✅ **Multi-Server-Unterstützung**: Möglichkeit, Charaktere auf Eden und Blackthorn zu verwalten
- ✅ **Spalten-Menü**: Spaltenliste im Menü korrigiert (Server hinzugefügt, Season entfernt)
- ✅ **Schnelle Umbenennung**: Enter-Taste im "Name"-Feld drücken, um direkt umzubenennen
- ✅ **Aufgeräumtere Oberfläche**: "Umbenennen"-Button und unnötige Popups entfernt
- ✅ **Fehlerbehebung**: Kritischer Fehler bei farbigen Titeln behoben

### Version 0.101 (27. Oktober 2025)
- ✅ **Windows-Oberfläche**: Toolbar durch traditionelle Menüleiste ersetzt
- ✅ **Datei-Menü**: Neuer Charakter, Einstellungen
- ✅ **Ansicht-Menü**: Spaltenkonfiguration
- ✅ **Hilfe-Menü**: Über mit vollständigen Informationen
- ✅ **Übersetzungen**: Vollständige Menü-Unterstützung in 3 Sprachen
- ✅ **Dokumentation**: Vollständige Aktualisierung mit Menü-Oberflächen-Anleitungen
- ✅ **Ersteller**: Auf "Ewoline" aktualisiert

### Version 0.1 (Oktober 2025)
- ✅ Vollständige Charakterverwaltung (CRUD)
- ✅ Reichsrang-System mit Web-Scraping
- ✅ Mehrsprachige Oberfläche (FR/EN/DE)
- ✅ Konfigurierbare sichtbare Spalten
- ✅ Debug-Modus mit integrierter Konsole
- ✅ Massenaktionen

## 🤝 Beitrag

Beiträge sind willkommen! Fühlen Sie sich frei:
- Fehler zu melden
- Neue Funktionen vorzuschlagen
- Dokumentation zu verbessern
- Übersetzungen hinzuzufügen

## 📄 Lizenz

Dieses Projekt ist ein persönliches DAOC-Charakterverwaltungstool.

---

**Erstellt von:** Ewoline  
**Version:** 0.104  
**Letzte Aktualisierung:** 29. Oktober 2025
