# ÄNDERUNGSPROTOKOLL

> 📁 **Diese Datei wurde verschoben**: Früher im Stammverzeichnis, jetzt in `Documentation/` (v0.104)

Alle bemerkenswerten Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt dem [Semantic Versioning](https://semver.org/lang/de/).

## [Unveröffentlicht]

### Hinzugefügt
- **Migrationsprüfung bei Pfadänderung**: Verbesserte Sicherheit
  - Automatische Erkennung, ob der neue Characters-Ordner eine Migration erfordert
  - Dreisprachiges Warnungs-Popup (FR/EN/DE), wenn alte Struktur erkannt wird
  - Nachricht, die darauf hinweist, die Anwendung neu zu starten, um die Migration durchzuführen
  - Test-Skript: `Scripts/test_migration_path_change.py`
  - Neue Übersetzungsschlüssel: `migration_path_change_title` und `migration_path_change_message`

## [0.104] - 2025-10-29

### Hinzugefügt
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
- **Neue Ordnerstruktur**: Migration zu hierarchischer Organisation nach Saison
  - Alte Struktur: `Characters/Realm/Character.json`
  - Neue Struktur: `Characters/Season/Realm/Character.json`
  - Bereitet auf zukünftige Saisons vor
  - Automatische Migration beim Start (mit Bestätigung)
  - Markierungsdatei `.migration_done` zur Vermeidung mehrfacher Migrationen
- **Hilfe-Menü > Ordnerstruktur migrieren**: Manuelle Migrationsoption
  - Ermöglicht manuelles Wiederholen der Migration bei Bedarf
  - Fragt vor dem Fortfahren nach Bestätigung
  - Erstellt automatisch ZIP-Sicherung
  - Zeigt detaillierten Migrationsbericht (Anzahl Charaktere, Verteilung nach Saison)
  - Aktualisiert Charakterliste automatisch nach Migration
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
- **Klassen- und Rassen-Spalten**: Neue Spalten in der Hauptansicht
  - "Klasse"-Spalte standardmäßig angezeigt
  - "Rasse"-Spalte standardmäßig ausgeblendet
  - Kontrollkästchen im Ansicht > Spalten-Menü zum Aktivieren/Deaktivieren von Spalten
  - Vollständige mehrsprachige Unterstützung (FR/EN/DE)
  - Daten werden automatisch aus den Charakter-JSON-Dateien extrahiert
- **Test-Skripte**: Tools zum Testen der Migration
  - `Scripts/simulate_old_structure.py`: Erstellt alte Struktur zum Testen
  - `Scripts/test_backup_structure.py`: Überprüft ZIP-Sicherungserstellung
- **Dokumentationsreorganisation**: Verbesserte Dateistruktur
  - CHANGELOGs nach `Documentation/` verschoben
  - Neues Haupt-`CHANGELOG.md` im Stammverzeichnis mit Verweis auf Sprachversionen
  - Sprach-READMEs (EN/DE) nach `Documentation/` verschoben
  - Haupt-README.md im Stammverzeichnis mit Links zu Sprachversionen
  - Bessere Organisation der Dokumentationsdateien
  - Alle internen Links aktualisiert

### Geändert
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
- **Reichsrang-Schnittstelle**: Schieberegler durch Dropdown-Menüs ersetzt
  - Dropdown-Menü für Rang (1-14)
  - Dropdown-Menü für Level (L0-L10 für Rang 1, L0-L9 für andere)
  - Rangtitel wird jetzt oben im Bereich in Reichsfarbe angezeigt
- **Auto-Speichern für Ränge**: "Diesen Rang anwenden"-Button entfernt
  - Rang/Level-Änderungen werden jetzt automatisch angewendet
  - Bestätigung von Änderungen nicht mehr erforderlich
- **.gitignore**: `Backup/`-Ordner zu Git-Ausschlüssen hinzugefügt

### Behoben
- **"Migration läuft"-Popup bleibt offen**: Kritischer Fehler behoben
  - `try/finally` hinzugefügt zur Garantie der Popup-Schließung
  - Expliziter Aufruf von `progress.close()` und `progress.deleteLater()`
  - Popup schließt jetzt korrekt nach Migration
- **LanguageManager-Fehler**: `lang.get()` Aufrufe mit falschen Standardwerten korrigiert
- **AttributeError**: Methodennamen für Rang/Level-Callbacks korrigiert

### Technisch
- **Verbesserte Architektur**: Saisontrennung auf Dateisystemebene
- **Rückwärtskompatibilität**: Automatische Migration bewahrt alle vorhandenen Charaktere
- **Detaillierte Protokollierung**: Alle Migrationsoperationen werden in Logs aufgezeichnet
- **Robuste Fehlerbehandlung**: Migration behandelt Fehlerfälle ohne Datenverlust
- **Optimierte Leistung**: Verwendet `zipfile` mit Kompression für Sicherungen
- **Qt-Speicherbereinigung**: Korrekte Verwendung von `deleteLater()` für temporäre Widgets
- 9 neue Übersetzungsschlüssel in FR/EN/DE für Migrationssystem hinzugefügt
- Vollständige Dokumentation erstellt: `BACKUP_ZIP_UPDATE.md`

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
- **Mauler-Entfernung**: Mauler-Klasse entfernt (nicht auf Eden-Server implementiert)
- **Eden-Unterstützung**: Daten angepasst, um verfügbare Klassen auf Eden zu entsprechen
- **Spezialisierungs-Struktur**: Mehrsprachiges Format `{"name": "EN", "name_fr": "FR", "name_de": "DE"}`
- **Erweiterter DataManager**: 11 neue Funktionen zur Verwaltung von Rassen/Klassen/Spezialisierungen hinzugefügt

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

- [0.101] - Aktuelle Version mit Windows-Menü-Oberfläche
- [0.1] - Ursprüngliche Version mit Toolbar

## Andere Sprachen

- 🇫🇷 [Français](CHANGELOG_FR.md)
- 🇬🇧 [English](CHANGELOG_EN.md)
- 🇩🇪 [Deutsch](CHANGELOG_DE.md) (diese Datei)