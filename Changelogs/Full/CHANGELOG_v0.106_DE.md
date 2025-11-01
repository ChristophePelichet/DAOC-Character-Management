# CHANGELOG v0.106 - Eden-Scraping & Auto-Update-Korrektionen

**Datum** : 2025-11-01  
**Version** : 0.106

## 🐛 Korrektionen

### Eden-Cookies-Speicherpfad (PyInstaller-Korrektur)
- **Problem** : Cookies wurden nicht standardmäßig im `Configuration/`-Ordner gespeichert
- **Ursache** : `CookieManager` verwendete `Path(__file__).parent.parent`, was Probleme mit PyInstaller verursachte
- **Lösung** : Verwendung von `get_config_dir()` aus `config_manager.py` für globale Konsistenz
- **Ergebnis** : Cookies werden jetzt korrekt im durch `config_folder` in `config.json` definierten Ordner gespeichert
- **Kompatibilität** : Funktioniert korrekt mit kompilierter Anwendung und normaler Ausführung
- **Geänderte Datei** : `Functions/cookie_manager.py` (Zeile 22-34)

### Spaltenkonfiguration korrigiert
- **Problem 1** : Die Herald-URL-Spalte (Index 11) war nicht im Größenanpassungsmodus enthalten (`range(11)` statt `range(12)`)
- **Problem 2** : Die Reihenfolge der Class- und Level-Spalten war im Konfigurationsmenü umgekehrt
- **Problem 3** : Sichtbarkeitszuordnung verwendete falsche Reihenfolge und URL-Spalte fehlte
- **Lösung** :
  * `apply_column_resize_mode()` behandelt jetzt alle 12 Spalten korrekt
  * Konfigurationsmenü-Reihenfolge mit TreeView ausgerichtet (Class vor Level)
  * `column_map` mit korrekter Reihenfolge und URL-Spalten-Einbindung korrigiert
- **Auswirkung** : Alle 12 Spalten (0-11) sind jetzt korrekt für Größenanpassungsmodus und Sichtbarkeit konfigurierbar
- **Geänderte Dateien** : `Functions/tree_manager.py`, `UI/dialogs.py`

## ✨ Verbesserungen

### Auto-Update bei Charakterimport
- **Vorher** : Wenn Charakter existiert → Fehler "Charakter existiert bereits"
- **Jetzt** : Wenn Charakter existiert → Automatische Aktualisierung von Herald 🔄
- **Beibehaltene Daten** : name, realm, season, server, benutzerdefinierte Felder
- **Aktualisierte Daten** : class, race, guild, level, realm_rank, realm_points, url, notes
- **Detaillierter Bericht** : Zeigt Anzahl von Erstellungen, Aktualisierungen und Fehlern
- **Anwendungsfall** : Ideal, um Charaktere über Herald-Import aktuell zu halten
- **Geänderte Datei** : `UI/dialogs.py` - Funktion `_import_characters()` (Zeile 2422)

### Konfigurierbarer Herald-Cookies-Ordner
- **Neue Option** : Einstellungsfenster → "Herald-Cookies-Ordner"
- **Funktion** : Benutzerdefinierten Ordner zur Speicherung von Eden-Scraping-Cookies angeben
- **Interface** : "Durchsuchen..."-Schaltfläche zur erleichterten Ordnerauswahl
- **Standardwert** : `Configuration/`-Ordner (Verhalten bleibt erhalten, wenn nicht konfiguriert)
- **Portable Anwendung** : Pfade sind absolut, keine Abhängigkeit von `__file__`
- **Persistenz** : Die Konfiguration wird in `config.json` unter dem Schlüssel `"cookies_folder"` gespeichert
- **Fallback-Logik** : Wenn `cookies_folder` nicht gesetzt ist, wird `config_folder` verwendet (gewährleistet Abwärtskompatibilität)
- **Geänderte Dateien** : `UI/dialogs.py`, `main.py`, `Functions/cookie_manager.py`

### Einheitliche Verzeichnis-Labels
- **Vorher** : Gemischte Labels ("Ordner von...", "Verzeichnis von...")
- **Jetzt** : Alle Ordner-Pfade beginnen mit "Verzeichnis"
- **Labels** :
  * Charakterverzeichnis
  * Konfigurationsverzeichnis
  * Log-Verzeichnis
  * Rüstungsverzeichnis
  * Herald-Cookie-Verzeichnis
- **Doppelpunkte entfernt** : Keine Doppelpunkte mehr am Ende von Labels (werden von QFormLayout automatisch hinzugefügt)
- **Lokalisierung** : Vollständige Übersetzungen in DE, FR, EN
- **Geänderte Dateien** : `UI/dialogs.py`, `Language/fr.json`, `Language/en.json`, `Language/de.json`

### Verbesserte Pfadanzeige
- **Vorher** : Cursor war am Anfang, aber Text war am Ende ausgerichtet (zeigt "...Configuration/" in QLineEdit)
- **Jetzt** : `setCursorPosition(0)` auf alle Pfadfelder angewendet
- **Ergebnis** : Anfang des Pfads ist sichtbar (z. B. "d:\Projekte\Python\..." statt "...Configuration/")
- **Geänderte Datei** : `UI/dialogs.py` - Methode `update_fields()` (Zeile 1260+)

### Robustes Diagnosesystem für unerwartete Abstürze
- **Global Exception Handler** : Erfasst und protokolliert alle unbehandelten Ausnahmen
- **System-Signal-Handler** : Erkennt SIGTERM, SIGINT und andere Betriebssystem-Unterbrechungen
- **CRITICAL/ERROR-Logging immer aktiv** : Auch bei debug_mode = OFF werden Fehler aufgezeichnet
- **Startup-Verfolgung** : Zeichnet Zeit (ISO 8601), Python-Version, aktive Threads auf
- **Shutdown-Verfolgung** : Zeichnet genau auf, wann und wie die App beendet wird
- **Exit-Code** : Zeigt den von der Qt-Ereignisschleife zurückgegebenen Code
- **Geänderte Dateien** : `main.py`, `Functions/logging_manager.py`

### Bereinigung und Umstrukturierung des CHANGELOGs-Systems
- **Altes System** : Monolithische CHANGELOGs in `Documentation/` vermischten alle Versionen (schwer zu navigieren)
- **Neues System** : Hierarchische Struktur in `Changelogs/` mit klarer Trennung nach Version und Sprache
- **Erstellte Struktur** :
  - `Changelogs/Full/` : Detaillierte CHANGELOGs (~150 Zeilen) für v0.106, v0.104 und frühere Versionen
  - `Changelogs/Simple/` : Prägnante Listen für schnelle Navigation aller 7 Versionen (v0.1 bis v0.106)
  - Mehrsprachige Unterstützung : FR, EN, DE für jede Datei
- **Zentrale Zugriff** : Neues `CHANGELOG.md` im Root mit Index und Navigation zu allen Versionen
- **Alte Inhalte** : Monolithische CHANGELOGs aus `Documentation/` entfernt (CHANGELOG_FR.md, CHANGELOG_EN.md, CHANGELOG_DE.md)
- **Erstellte Dateien** : 27 Dateien insgesamt (6 Full + 21 Simple)
- **Ergebnis** : Viel klareres und wartbareres System zum Auffinden von Änderungen nach Version und Sprache

## 📊 Allgemeine Auswirkungen

✅ **Intuitiverer und flüssigerer Import-Workflow** - Kein Löschen/Neuimportieren erforderlich  
✅ **Transparente Stats-Aktualisierung von Herald** - Charaktere werden automatisch aktualisiert  
✅ **Ordnungsgemäße Fehlerbehandlung mit detailliertem Bericht** - Anzahl von Erstellungen, Aktualisierungen und Fehlern  
✅ **Erhöhte Flexibilität für Cookie-Verwaltung** - Anpassbare Pfade für Scraping  
✅ **Vollständige Anwendungsportabilität** - Zentralisierte Konfiguration ohne __file__-Abhängigkeiten  
✅ **Möglichkeit, unerwartete Abstürze zu diagnostizieren** - Detaillierte Protokolle aller kritischen Ereignisse  
✅ **Konsistente und kohärente Benutzeroberfläche** - Einheitliche Labels und optimale Pfadanzeige  

## 🔗 Geänderte Dateien

- `main.py`
- `UI/dialogs.py`
- `Functions/cookie_manager.py`
- `Functions/tree_manager.py`
- `Functions/logging_manager.py`
- `Language/fr.json`
- `Language/en.json`
- `Language/de.json`
