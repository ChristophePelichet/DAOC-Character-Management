# ÄNDERUNGSPROTOKOLL

Alle bemerkenswerten Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt dem [Semantic Versioning](https://semver.org/lang/de/).

## [Unveröffentlicht]

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