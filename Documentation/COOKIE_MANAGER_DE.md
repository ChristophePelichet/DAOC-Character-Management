# Eden Cookie-Manager - Dokumentation

## Übersicht

Der Eden Cookie-Manager verwaltet die Authentifizierung für den Zugriff auf den Eden-DAOC Herald. Er speichert Discord OAuth-Authentifizierungs-Cookies und überprüft deren Gültigkeit.

## Zugehörige Dateien

- **Functions/cookie_manager.py**: `CookieManager`-Klasse für Cookie-Verwaltung
- **UI/dialogs.py**: `CookieManagerDialog` - Grafische Verwaltungsoberfläche
- **Functions/ui_manager.py**: Eden-Statusleiste in der Hauptoberfläche

## Funktionen

### 1. Cookie-Generierung
- Öffnet Chrome-Browser für Discord OAuth-Authentifizierung
- Ruft Cookies automatisch nach Anmeldung ab
- Speichert in `Configuration/eden_cookies.pkl`

### 2. Cookie-Validierung
- Prüft Ablaufdatum (364 Tage)
- Testet tatsächlichen Herald-Zugriff (`https://eden-daoc.net/herald?n=top_players&r=hib`)
- Erkennt ungültige oder abgelaufene Cookies

### 3. Import/Export
- Import vorhandener .pkl Cookie-Dateien
- Automatische Sicherung vor Löschung
- Formatvalidierung beim Import

### 4. Benutzeroberfläche

#### Haupt-Statusleiste
Angezeigt im Hauptfenster zwischen Menü und Aktionen:
- **Status**: ✅ Herald erreichbar / ❌ Fehlermeldung / ⏳ Überprüfung läuft
- **Aktualisieren-Schaltfläche**: Testet Verbindung erneut
- **Verwalten-Schaltfläche**: Öffnet detaillierten Manager

#### Verwaltungsfenster
Erreichbar über "⚙️ Verwalten"-Schaltfläche:
- **Cookie-Status**: Gültig / Abgelaufen / Keine
- **Ablaufdatum**: Anzeige mit Countdown
- **Verbindungstest**: Echtzeit-Überprüfung (Hintergrund-Thread)
- **Aktionen**:
  - 🔐 Cookies generieren: Startet OAuth-Prozess
  - 🔄 Aktualisieren: Aktualisiert Anzeige
  - 🗑️ Löschen: Entfernt Cookies (mit Sicherung)
- **Import**: Textfeld + Durchsuchen-Schaltfläche zum Importieren

## Verwendung

### Cookies zum ersten Mal generieren
1. "⚙️ Verwalten" in Eden-Statusleiste klicken
2. "🔐 Cookies generieren" klicken
3. Mit Discord im sich öffnenden Browser anmelden
4. Nach Anmeldung Enter drücken
5. Cookies werden automatisch gespeichert

### Status überprüfen
Die Haupt-Statusleiste zeigt den Herald-Verbindungsstatus in Echtzeit an. Der Test läuft automatisch beim Start im Hintergrund.

### Vorhandene Cookies importieren
1. Manager öffnen ("⚙️ Verwalten")
2. .pkl-Dateipfad eingeben ODER "📁 Durchsuchen" klicken
3. Enter drücken oder Importieren klicken
4. Status wird automatisch aktualisiert

## Technische Architektur

### Hauptklassen

#### CookieManager (Functions/cookie_manager.py)
- `cookie_exists()`: Prüft Vorhandensein der Cookie-Datei
- `get_cookie_info()`: Gibt detaillierte Informationen zurück (Gültigkeit, Ablauf, Zähler)
- `generate_cookies_with_browser()`: Startet Authentifizierungsprozess
- `save_cookies_from_driver()`: Ruft Cookies von Selenium ab
- `import_cookie_file()`: Importiert externe Cookie-Datei
- `delete_cookies()`: Löscht mit automatischer Sicherung
- `test_eden_connection()`: Testet Herald-Zugriff mit Selenium

#### ConnectionTestThread (UI/dialogs.py)
QThread-Thread zum Ausführen des Verbindungstests im Hintergrund ohne Blockierung der Oberfläche.

#### EdenStatusThread (Functions/ui_manager.py)
QThread-Thread für Haupt-Statusleiste, aktualisiert Verbindungsanzeige.

### Cookie-Format
Pickle-Datei mit Liste von Wörterbüchern:
```python
{
    'name': 'eden_daoc_sid',
    'value': '...',
    'domain': '.eden-daoc.net',
    'path': '/',
    'expiry': 1761753600  # Unix-Zeitstempel
}
```

### Verbindungstest
1. Initialisiert Headless Chrome-Treiber
2. Lädt Eden-Startseite
3. Injiziert Cookies
4. Navigiert zu `https://eden-daoc.net/herald?n=top_players&r=hib`
5. Analysiert Inhalt zum Erkennen:
   - Umleitung zu Login → ungültige Cookies
   - Anmeldeformular → nicht authentifiziert
   - Herald-Inhalt vorhanden → Verbindung OK

## Abhängigkeiten

- **selenium**: Browser-Automatisierung
- **webdriver-manager**: Automatische ChromeDriver-Verwaltung
- **PySide6**: Grafische Oberfläche (QThread, QDialog)

## Fehlerbehandlung

### Cookies nicht gefunden
- Anzeige: "❌ Keine Cookies gefunden"
- Aktion: Neue Cookies generieren

### Abgelaufene Cookies
- Anzeige: "⚠️ Abgelaufene Cookies"
- Aktion: Cookies neu generieren

### Verbindungsfehler
- Anzeige: "❌ [Fehlermeldung]"
- Mögliche Ursachen:
  - Keine Internetverbindung
  - Eden-Server nicht erreichbar
  - ChromeDriver nicht installiert
  - Fehlendes Modul (selenium, requests)

### Import fehlgeschlagen
- Dateipfad-Validierung
- Pickle-Format-Überprüfung
- Detaillierte Fehlermeldungen mit Logging

## Sicherheit

- **Lokale Speicherung**: Cookies lokal in `Configuration/` gespeichert
- **Automatische Sicherung**: Sicherung vor Löschung
- **Keine Übertragung**: Cookies werden nirgendwo außer Eden-DAOC gesendet
- **Lebensdauer**: 364 Tage, dann Erneuerung erforderlich

## Protokolle

Alle Ereignisse werden über `logging`-Modul protokolliert:
- INFO: Erfolgreiche Operationen (Generierung, Import, Test)
- WARNING: Nicht blockierende Probleme (bestimmtes Cookie nicht hinzugefügt)
- ERROR: Blockierende Fehler (Import fehlgeschlagen, Treiber nicht initialisiert)
- CRITICAL: Schwerwiegende Fehler (unbehandelte Ausnahme)

## Zukünftige Verbesserungen (Phase 2)

- Vollständige Scraper-Integration zum Importieren von Charakteren aus Herald
- Automatische Charakterdaten-Synchronisierung
- Verwaltung mehrerer Discord-Konten
- Caching gescrapeter Daten
- Charakter-/Gilden-Suchoberfläche
