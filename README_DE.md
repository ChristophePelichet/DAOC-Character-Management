# DAOC - Charakterverwaltung

Charakterverwaltungsanwendung für Dark Age of Camelot (DAOC), entwickelt in Python mit PySide6.

**🌍 Verfügbar in:** [Français](README.md) | [English](README_EN.md) | **Deutsch**

## 🎮 Funktionen

### Charakterverwaltung
- ✅ **Erstellen** von neuen Charakteren
- ✅ **Umbenennen** von vorhandenen Charakteren
- ✅ **Duplizieren** von Charakteren
- ✅ **Löschen** von Charakteren (einzeln oder in Masse)
- ✅ **Anzeigen** von vollständigen Details jedes Charakters

### Organisation
- 📁 Organisation nach **Reich** (Albion, Hibernia, Midgard)
- 🏷️ Filter nach **Saison** (S1, S2, S3, usw.)
- 🖥️ Multi-**Server** Verwaltung (Eden, Blackthorn, usw.)
- 📊 Tabelle mit sortierbaren Spalten

### Reichsränge
- 🏆 **Anzeige** von Reichsrang und Titel
- 📈 **Manuelle Anpassung** des Ranges (Rang 1-14, Level 1-9/10)
- 🎨 **Farbige Titel** nach Reich
- 📊 **Automatische Berechnung** basierend auf Reichspunkten

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
- **Seite**: Charakter-Seite (1-5)
- **Gilde**: Gildenname

Siehe [Documentation/COLUMN_CONFIGURATION_EN.md](Documentation/COLUMN_CONFIGURATION_EN.md) (EN) für weitere Details.

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

Siehe [Documentation/DATA_MANAGER_EN.md](Documentation/DATA_MANAGER_EN.md) (EN) für weitere Informationen zur Datenverwaltung.

## 📚 Dokumentation

Vollständige Dokumentation verfügbar im `Documentation/` Ordner:

### Français 🇫🇷
- [Configuration des Colonnes](Documentation/CONFIGURATION_COLONNES_FR.md)
- [Système Realm Ranks](Documentation/REALM_RANKS_FR.md)
- [Gestionnaire de Données](Documentation/DATA_MANAGER_FR.md)
- [Dossier Data](Documentation/DATA_FOLDER_FR.md)
- [Menu Interface](Documentation/INTERFACE_MENU_FR.md)

### English 🇬🇧
- [Column Configuration](Documentation/COLUMN_CONFIGURATION_EN.md)
- [Realm Ranks System](Documentation/REALM_RANKS_EN.md)
- [Data Manager](Documentation/DATA_MANAGER_EN.md)
- [Data Folder](Documentation/DATA_FOLDER_EN.md)
- [Menu Interface](Documentation/INTERFACE_MENU_EN.md)

## 🗂️ Projektstruktur

```
DAOC-Character-Management/
├── main.py                      # Hauptanwendung
├── requirements.txt             # Python-Abhängigkeiten
├── scrape_realm_ranks.py        # Rang-Extraktionsskript
├── Characters/                  # Charakterdaten
│   ├── Albion/
│   ├── Hibernia/
│   └── Midgard/
├── Configuration/               # Konfigurationsdateien
│   └── config.json
├── Data/                        # Spieldaten
│   └── realm_ranks.json
├── Documentation/               # Vollständige Dokumentation (FR/EN)
│   ├── INDEX.md
│   ├── CONFIGURATION_COLONNES_FR.md
│   ├── COLUMN_CONFIGURATION_EN.md
│   ├── REALM_RANKS_FR.md
│   ├── REALM_RANKS_EN.md
│   ├── DATA_MANAGER_FR.md
│   ├── DATA_MANAGER_EN.md
│   ├── DATA_FOLDER_FR.md
│   ├── DATA_FOLDER_EN.md
│   ├── INTERFACE_MENU_FR.md
│   └── INTERFACE_MENU_EN.md
├── Functions/                   # Python-Module
│   ├── character_manager.py
│   ├── config_manager.py
│   ├── data_manager.py
│   ├── language_manager.py
│   ├── logging_manager.py
│   └── path_manager.py
├── Img/                         # Bilder und Symbole
├── Language/                    # Übersetzungsdateien
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

Siehe das [Änderungsprotokoll](CHANGELOG_DE.md) für vollständige Historie.  
**🌍 Verfügbar in:** [Français](CHANGELOG_FR.md) | [English](CHANGELOG_EN.md) | [Deutsch](CHANGELOG_DE.md)

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
**Version:** 0.102  
**Letzte Aktualisierung:** 27. Oktober 2025
