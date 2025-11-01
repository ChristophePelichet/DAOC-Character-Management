# Vollständige Dokumentation des Eden Herald Scrapers

## 📋 Inhaltsverzeichnis

1. [Überblick](#überblick)
2. [Systemarchitektur](#systemarchitektur)
3. [Detaillierter Ablauf](#detaillierter-ablauf)
4. [Hauptkomponenten](#hauptkomponenten)
5. [Cookie-Verwaltung](#cookie-verwaltung)
6. [Benutzeroberfläche](#benutzeroberfläche)
7. [Datenverarbeitung](#datenverarbeitung)
8. [Fehlerbehandlung](#fehlerbehandlung)

---

## 🎯 Überblick

Der Eden Herald Scraper ermöglicht die automatische Suche und den Import von Charakteren von der Eden DAOC Herald-Website. Er verwendet Selenium zur Navigation auf der Website und BeautifulSoup zur Analyse der HTML-Ergebnisse.

### Hauptfunktionen

- ✅ **Charaktersuche** nach Name mit optionalem Reichsfilter
- ✅ **Automatische Überprüfung** der Herald-Erreichbarkeit
- ✅ **Cookie-Verwaltung** zur Umgehung der Bot-Prüfung
- ✅ **Einfacher oder Massenimport** gefundener Charaktere
- ✅ **Automatische Erkennung** des Reichs basierend auf der Klasse
- ✅ **Automatische Berechnung** des Reichsrangs
- ✅ **Intelligente Filterung** der Suchergebnisse
- ✅ **Mehrsprachige Oberfläche** (FR, EN, DE)

---

## 🏗️ Systemarchitektur

```
┌─────────────────────────────────────────────────────────────────┐
│                    HAUPTANWENDUNG                                │
│                         (main.py)                                │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ├─── UI Manager (Functions/ui_manager.py)
                 │    └─── Eden Herald Statusleiste
                 │         ├─── Status-Label
                 │         ├─── Aktualisieren-Button
                 │         ├─── Herald-Suche-Button
                 │         └─── Verwalten-Button (Cookies)
                 │
                 ├─── Cookie Manager (Functions/cookie_manager.py)
                 │    ├─── Sichere Cookie-Speicherung
                 │    ├─── Datenverschlüsselung
                 │    ├─── Import/Export
                 │    └─── Validierung
                 │
                 ├─── Eden Scraper (Functions/eden_scraper.py)
                 │    ├─── Selenium-Konfiguration
                 │    ├─── Herald-Navigation
                 │    ├─── Datenextraktion
                 │    └─── Bot-Check-Behandlung
                 │
                 └─── Herald Search Dialog (UI/dialogs.py)
                      ├─── Such-Oberfläche
                      ├─── Ergebnisanzeige
                      ├─── Charakterauswahl
                      └─── Import in Datenbank
```

---

## 🔄 Detaillierter Ablauf

### 1. Erste Herald-Überprüfung

```
┌──────────────┐
│  Anwendungs- │
│    start     │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────┐
│ UIManager.create_eden_status_bar()      │
│ - Erstellt Status-Oberfläche            │
│ - Deaktiviert Aktualisieren/Suche-Knöpfe│
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│ UIManager.check_eden_status()           │
│ - Erstellt EdenStatusThread             │
│ - Startet Hintergrundüberprüfung        │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│ EdenStatusThread.run()                  │
│ - Lädt Cookies von CookieManager        │
│ - Versucht Zugriff auf eden-daoc.net    │
│ - Überprüft Herald-Präsenz              │
└──────┬──────────────────────────────────┘
       │
       ├─── ✅ Erfolg
       │    └──▶ Signal: status_updated(True, "")
       │
       └─── ❌ Fehler
            └──▶ Signal: status_updated(False, "Nachricht")
       │
       ▼
┌─────────────────────────────────────────┐
│ UIManager.update_eden_status()          │
│ - Aktualisiert Label (✅/❌)            │
│ - Aktiviert Aktualisieren/Suche-Knöpfe  │
└─────────────────────────────────────────┘
```

### 2. Charaktersuche

```
┌──────────────────┐
│ Benutzer klickt  │
│ "🔍 Herald       │
│    Suche"        │
└────────┬─────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ CharacterApp.open_herald_search()          │
│ - Öffnet HeraldSearchDialog                │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ HeraldSearchDialog.__init__()              │
│ - Erstellt Such-Oberfläche                 │
│ - Charaktername-Textfeld                   │
│ - Reichsfilter-Dropdown (mit Logos)        │
│ - Ergebnistabelle mit Checkboxen           │
│ - Import ausgewählt/alle Buttons           │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ Benutzer gibt Name ein (min 3 Zeichen)     │
│ + wählt optionales Reich                   │
│ + klickt "Suchen"                          │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ HeraldSearchDialog.start_search()          │
│ - Validiert Länge >= 3 Zeichen             │
│ - Holt realm_filter vom Dropdown           │
│ - Deaktiviert Oberfläche während Suche     │
│ - Erstellt SearchThread                    │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ SearchThread.run()                         │
│ - Ruft eden_scraper.search_herald_...()    │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ eden_scraper.search_herald_character()     │
│ 1. Konfiguriert Chrome (off-screen)       │
│ 2. Lädt Cookies                            │
│ 3. Baut URL mit Parametern                 │
│    - name={character_name}                 │
│    - &r={realm} (wenn Filter aktiv)        │
│ 4. Navigiert zum Herald                    │
│ 5. Extrahiert Daten aus 28 HTML-Tabellen   │
│ 6. Bereinigt temporären Ordner             │
│ 7. Speichert JSON in temp-Ordner           │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ Signal: search_finished(success, message,  │
│                         json_path)         │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ HeraldSearchDialog.on_search_finished()    │
│ - Lädt JSON aus temporärer Datei           │
│ - Filtert: behält nur Namen, die mit       │
│   Abfrage beginnen (startswith)            │
│ - Füllt Tabelle mit Ergebnissen            │
│ - Färbt Zeilen nach Reich                  │
│ - Aktiviert Oberfläche wieder              │
└────────────────────────────────────────────┘
```

### 3. Charakterimport

```
┌──────────────────┐
│ Benutzer markiert│
│ Charaktere und   │
│ klickt "Import"  │
└────────┬─────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ HeraldSearchDialog.import_selected_...()   │
│ - Holt markierte Zeilen                    │
│ - Fragt nach Bestätigung                   │
│ - Ruft _import_characters()                │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ HeraldSearchDialog._import_characters()    │
│ Für jeden Charakter:                       │
│   1. Holt Daten (Name, Klasse, usw.)       │
│   2. Erkennt Reich über CLASS_TO_REALM     │
│   3. Prüft ob bereits vorhanden (Duplikat) │
│   4. Erstellt character_data dict          │
│   5. Ruft save_character()                 │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ character_manager.save_character()         │
│ - Speichert in JSON-Datei                  │
│   Characters/{realm}/{name}.json           │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ Automatische Aktualisierung                │
│ - parent().tree_manager.refresh_...()      │
│ - Zeigt neue Charaktere in Liste an        │
└────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ Zeigt Ergebnis an                          │
│ - ✅ X Charakter(e) importiert            │
│ - ⚠️ Y Fehler (Duplikate, usw.)           │
└────────────────────────────────────────────┘
```

---

## 🧩 Hauptkomponenten

### 1. UIManager (`Functions/ui_manager.py`)

**Rolle**: Verwaltet Eden-Status-Oberfläche im Hauptfenster

#### Hauptmethoden

```python
create_eden_status_bar(parent_layout)
```
- Erstellt Gruppe "Eden Herald Status"
- Initialisiert Buttons und Status-Label
- Startet erste Überprüfung

```python
check_eden_status()
```
- Deaktiviert Buttons während Überprüfung
- Erstellt Überprüfungs-Thread (EdenStatusThread)
- Startet Hintergrundüberprüfung

```python
update_eden_status(accessible, message)
```
- Aktualisiert Status-Anzeige
- Aktiviert Buttons nach Überprüfung wieder
- Zeigt ✅ oder ❌ je nach Ergebnis

#### EdenStatusThread-Klasse

Thread, der Herald-Erreichbarkeit überprüft ohne die Oberfläche zu blockieren.

**Signal**: `status_updated(bool accessible, str message)`

---

### 2. CookieManager (`Functions/cookie_manager.py`)

**Rolle**: Verwaltet sichere Speicherung von Eden-Cookies

#### Speicherstruktur

```json
{
  "cookies": [
    {
      "name": "cookie_name",
      "value": "verschlüsselter_wert",
      "domain": ".eden-daoc.net",
      "path": "/",
      "secure": true,
      "httpOnly": false,
      "sameSite": "Lax"
    }
  ],
  "created_at": "2025-01-29T10:30:00",
  "last_used": "2025-01-29T14:45:00"
}
```

#### Hauptmethoden

```python
load_cookies_for_selenium(driver)
```
- Lädt Cookies aus verschlüsselter Datei
- Injiziert sie in Selenium-Browser
- Gibt True zurück bei Erfolg, False sonst

```python
import_cookies_from_file(file_path)
```
- Importiert Cookies aus externer JSON-Datei
- Validiert Format
- Verschlüsselt und speichert

```python
export_cookies_to_file(file_path)
```
- Exportiert aktuelle Cookies in Datei
- Entschlüsselt Werte für Export

---

### 3. Eden Scraper (`Functions/eden_scraper.py`)

**Rolle**: Haupt-Scraper, der Herald-Daten extrahiert

#### Selenium-Konfiguration

```python
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--window-position=-2400,-2400")  # Off-screen
```

**Wichtig**: Browser wird außerhalb des Bildschirms positioniert (`-2400,-2400`), um unsichtbar zu bleiben, während er technisch "sichtbar" ist (umgeht Bot-Check).

#### Hauptfunktion

```python
search_herald_character(character_name, realm_filter="")
```

**Parameter**:
- `character_name`: Zu suchender Charaktername
- `realm_filter`: "albion", "midgard", "hibernia" oder "" (alle)

**Rückgabe**: `(success: bool, message: str, json_path: str)`

**Prozess**:

1. **Bereinigung**: Löscht alte temporäre Dateien
2. **Konfiguration**: Konfiguriert Chrome mit spezifischen Optionen
3. **Cookies**: Lädt Cookies über CookieManager
4. **Navigation**: Greift auf `https://eden-daoc.net/herald/character/search` zu
5. **Anfrage**: Sendet Suchparameter
6. **Extraktion**: Parst 28 HTML-Tabellen mit BeautifulSoup
7. **Speicherung**: Erstellt JSON in `tempfile.gettempdir()/EdenSearchResult/`
8. **Bereinigung**: Schließt Browser

#### Extrahierte HTML-Tabellenstruktur

Der Herald gibt Daten in 28 verschiedenen HTML-Tabellen zurück:
- Tabellen 0-27 enthalten jeweils Charakterinformationen

**Tabellenformat**:
```html
<table>
  <tr><td>Rang</td><td>Name</td><td>Klasse</td><td>Rasse</td>...</tr>
  <tr><td>1</td><td>Ewoline</td><td>Cleric</td><td>Briton</td>...</tr>
</table>
```

#### Extrahierte Spalten

1. **rank**: Position im Ranking
2. **name**: Vollständiger Charaktername
3. **clean_name**: Bereinigter Name (ohne HTML-Tags)
4. **class**: Charakterklasse
5. **race**: Charakterrasse
6. **guild**: Gilde (oder "Unguilded")
7. **level**: Level (1-50)
8. **realm_points**: Reichspunkte (Format "331 862")
9. **realm_rank**: Reichsrang (z.B. "12L3")
10. **realm_level**: Rangstufe (z.B. "12")
11. **url**: Link zur Charakterseite

#### Generierte temporäre Dateien

```
%TEMP%/EdenSearchResult/
├── search_20250129_143045.json      # Rohdaten
└── characters_20250129_143045.json  # Formatierte Daten
```

**Bereinigung**: Dateien werden beim Schließen des Such-Dialogs gelöscht.

---

### 4. Herald Search Dialog (`UI/dialogs.py`)

**Rolle**: Such- und Import-Oberfläche

#### HeraldSearchDialog-Klasse

##### Oberfläche

```
┌────────────────────────────────────────────────────┐
│  Charaktersuche - Eden Herald                      │
├────────────────────────────────────────────────────┤
│  Charaktername: [___________]                      │
│  Reich: [Alle Reiche ▼]                           │
│  [Suchen]                                          │
├────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────┐ │
│  │ ☑ │ 🏰 │ Name   │ Klasse │ Rasse │ Gilde  │ │ │
│  ├───┼────┼────────┼────────┼───────┼────────┤ │ │
│  │ ☑ │ 🔴 │ Ewoline│ Cleric │Briton │MyGuild │ │ │
│  │ ☐ │ 🔵 │ Olaf   │Warrior │Norseman│      │ │ │
│  │ ☑ │ 🟢 │ Fionn  │ Druid  │ Celt  │OtherG  │ │ │
│  └──────────────────────────────────────────────┘ │
│                                                    │
│  [⬇️ Auswahl importieren] [⬇️⬇️ Alle importieren] │
└────────────────────────────────────────────────────┘
```

##### Hauptmethoden

```python
_load_realm_icons_for_combo()
```
- Lädt Reichslogos (Img/)
- Erstellt QComboBox mit 20x20 Icons
- Optionen: Alle, Albion, Midgard, Hibernia

```python
start_search()
```
- Validiert Mindestlänge (3 Zeichen)
- Holt Reichsfilter
- Startet SearchThread

```python
on_search_finished(success, message, json_path)
```
- Lädt Ergebnis-JSON
- **Wichtiger Filter**: `name.lower().startswith(query.lower())`
  - Vermeidet Teilergebnisse ("oli" findet nicht "Ewoline")
- Füllt Tabelle mit farbigen Spalten
- Wendet Hintergrundfarbe nach Reich an (Alpha 50)

```python
import_selected_characters()
```
- Holt markierte Zeilen
- Fragt nach Bestätigung
- Ruft `_import_characters()`

```python
import_all_characters()
```
- Importiert alle Ergebnisse ohne Auswahlbestätigung
- Fragt nach globaler Bestätigung
- Ruft `_import_characters()`

```python
_import_characters(characters)
```
Für jeden Charakter:
1. Extrahiert `clean_name` oder `name`
2. Bestimmt Reich über `CLASS_TO_REALM[class]`
3. **Prüft Duplikate**:
   ```python
   existing_chars = get_all_characters()
   if any(c.get('name', '').lower() == name.lower() for c in existing_chars):
       # Fehler: Charakter existiert bereits
   ```
4. Erstellt vollständiges `character_data` dict
5. Ruft `save_character(character_data)`
6. Zählt Erfolge/Fehler
7. Aktualisiert Hauptoberfläche
8. Zeigt Ergebnis in QMessageBox

##### Klasse → Reich-Zuordnung

```python
CLASS_TO_REALM = {
    # Albion
    "Armsman": "Albion", "Cabalist": "Albion", "Cleric": "Albion",
    "Friar": "Albion", "Heretic": "Albion", "Infiltrator": "Albion",
    "Mauler": "Albion", "Mercenary": "Albion", "Minstrel": "Albion",
    "Necromancer": "Albion", "Paladin": "Albion", "Reaver": "Albion",
    "Scout": "Albion", "Sorcerer": "Albion", "Theurgist": "Albion",
    "Wizard": "Albion",
    
    # Midgard
    "Berserker": "Midgard", "Bonedancer": "Midgard", "Healer": "Midgard",
    "Hunter": "Midgard", "Runemaster": "Midgard", "Savage": "Midgard",
    "Shadowblade": "Midgard", "Shaman": "Midgard", "Skald": "Midgard",
    "Spiritmaster": "Midgard", "Thane": "Midgard", "Valkyrie": "Midgard",
    "Warlock": "Midgard", "Warrior": "Midgard",
    
    # Hibernia
    "Animist": "Hibernia", "Bainshee": "Hibernia", "Bard": "Hibernia",
    "Blademaster": "Hibernia", "Champion": "Hibernia", "Druid": "Hibernia",
    "Eldritch": "Hibernia", "Enchanter": "Hibernia", "Hero": "Hibernia",
    "Mentalist": "Hibernia", "Nightshade": "Hibernia", "Ranger": "Hibernia",
    "Valewalker": "Hibernia", "Vampiir": "Hibernia", "Warden": "Hibernia"
}
```

##### Reichsfarben (Tabelle)

```python
REALM_COLORS = {
    "Albion": QColor(204, 0, 0, 50),      # Rot Alpha 50
    "Midgard": QColor(0, 102, 204, 50),   # Blau Alpha 50
    "Hibernia": QColor(0, 170, 0, 50)     # Grün Alpha 50
}
```

---

## 🍪 Cookie-Verwaltung

### Warum Cookies?

Die Eden Herald-Website verwendet ein Anti-Bot-System, das eine erste Validierung erfordert. Cookies ermöglichen die Umgehung dieser Überprüfung durch Wiederverwendung einer authentifizierten Sitzung.

### Cookie-Beschaffungsprozess

#### Methode 1: Import aus Browser

1. Firefox/Chrome öffnen
2. Bei https://eden-daoc.net anmelden
3. DevTools öffnen (F12)
4. Zum Tab "Speicher" / "Application" gehen
5. Cookies von Domain `.eden-daoc.net` kopieren
6. JSON-Datei erstellen:

```json
[
  {
    "name": "__cf_bm",
    "value": "ihr_wert_hier",
    "domain": ".eden-daoc.net",
    "path": "/",
    "secure": true,
    "httpOnly": true,
    "sameSite": "Lax"
  }
]
```

7. In Anwendung: **Aktionen-Menü → Eden-Cookies verwalten → Importieren**

#### Methode 2: Automatische Generierung (TODO)

Geplante Funktion zur Automatisierung der Beschaffung.

### Cookie-Dateistruktur

**Ort**: `%APPDATA%/DAOCCharacterManager/eden_cookies.json`

**Format**:
```json
{
  "cookies": [
    {
      "name": "__cf_bm",
      "value": "BASE64_VERSCHLÜSSELTER_WERT",
      "domain": ".eden-daoc.net",
      "path": "/",
      "secure": true,
      "httpOnly": true,
      "sameSite": "Lax"
    }
  ],
  "created_at": "2025-01-29T10:00:00",
  "last_used": "2025-01-29T14:30:00"
}
```

### Sicherheit

- ✅ Werte mit cryptography verschlüsselt (Fernet)
- ✅ Eindeutiger Verschlüsselungsschlüssel pro Installation
- ✅ Restriktive Dateiberechtigungen
- ✅ Format-Validierung vor Verwendung

---

## 🎨 Benutzeroberfläche

### Hauptfenster

#### Eden Herald Statusleiste

```
┌──────────────────────────────────────────────────────┐
│ Eden Herald Status                                   │
├──────────────────────────────────────────────────────┤
│ ⏳ Überprüfung läuft...                              │
│ [🔄 Aktualisieren] [🔍 Herald Suche] [⚙️ Verwalten] │
└──────────────────────────────────────────────────────┘
```

**Mögliche Zustände**:
- `⏳ Überprüfung läuft...` (grau) → Buttons deaktiviert
- `✅ Herald erreichbar` (grün fett) → Buttons aktiviert
- `❌ Herald nicht erreichbar: <Grund>` (rot) → Buttons aktiviert

#### Charakterliste (Färbung)

Zeilen sind nach Reich mit subtilem Hintergrund gefärbt (Alpha 25):
- 🔴 **Albion**: Hellroter Hintergrund
- 🔵 **Midgard**: Hellblauer Hintergrund
- 🟢 **Hibernia**: Hellgrüner Hintergrund

**Implementierung**: Benutzerdefinierte Delegates in `UI/delegates.py`
- `NormalTextDelegate`: Normaler Text + farbiger Hintergrund
- `CenterIconDelegate`: Zentriertes Icon + farbiger Hintergrund
- `CenterCheckboxDelegate`: Zentrierte Checkbox + farbiger Hintergrund

### Herald-Such-Dialog

#### Komponenten

1. **Suchfeld**: QLineEdit mit 3+ Zeichen Validierung
2. **Reichsfilter**: QComboBox mit Logos (20x20px)
3. **Such-Button**: Startet Suche
4. **Ergebnistabelle**: QTableWidget mit 9 Spalten
5. **Import-Buttons**: Import Auswahl / Import alle

#### Tabellenspalten

| Spalte | Typ | Beschreibung |
|---------|------|-------------|
| ☑ | Checkbox | Auswahl für Import |
| Reich | Icon | Reichslogo |
| Name | Text | Charaktername |
| Klasse | Text | Klasse |
| Rasse | Text | Rasse |
| Gilde | Text | Gildenname |
| Level | Zahl | Level (1-50) |
| RP | Zahl | Formatierte Reichspunkte |
| Realm Rank | Text | Rang (z.B. 12L3) |

#### Such-Validierung

```python
def start_search(self):
    query = self.search_input.text().strip()
    
    # Mindestlängen-Validierung
    if len(query) < 3:
        QMessageBox.warning(
            self,
            "Ungültige Suche",
            "Bitte geben Sie mindestens 3 Zeichen ein."
        )
        return
    
    # Reichsfilter holen
    realm_filter = ""
    realm_index = self.realm_combo.currentIndex()
    if realm_index > 0:  # 0 = "Alle"
        realm_filter = ["albion", "midgard", "hibernia"][realm_index - 1]
    
    # Suche starten
    self.search_thread = SearchThread(query, realm_filter)
    # ...
```

#### Ergebnisfilterung

Nach Abruf vom Herald, lokale Filterung für Präzision:

```python
def on_search_finished(self, success, message, json_path):
    # ...
    search_query = self.search_input.text().strip().lower()
    
    # Filter: nur Namen, die mit Abfrage beginnen
    filtered_characters = [
        char for char in all_characters
        if char.get('clean_name', '').lower().startswith(search_query)
        or char.get('name', '').lower().startswith(search_query)
    ]
    
    # In Tabelle anzeigen
    self._populate_results_table(filtered_characters)
```

**Beispiel**:
- Suche: `"Ewo"`
- Herald gibt zurück: `["Ewoline", "Ewolinette", "NewoB", "Aewo"]`
- Lokaler Filter behält: `["Ewoline", "Ewolinette"]`
- Eliminiert: `["NewoB", "Aewo"]` (beginnen nicht mit "Ewo")

---

## 📊 Datenverarbeitung

### Charakterdatenstruktur

#### Rohdaten vom Herald

```json
{
  "rank": "1",
  "name": "Ewoline",
  "clean_name": "Ewoline",
  "class": "Cleric",
  "race": "Briton",
  "guild": "Phoenix Rising",
  "level": "50",
  "realm_points": "331 862",
  "realm_rank": "12L3",
  "realm_level": "12",
  "url": "/herald/character/view/Ewoline"
}
```

#### Daten nach Import (character_data)

```json
{
  "name": "Ewoline",
  "class": "Cleric",
  "race": "Briton",
  "realm": "Albion",
  "guild": "Phoenix Rising",
  "level": "50",
  "realm_rank": "12L3",
  "realm_points": 331862,
  "realm_level": "12",
  "server": "Eden",
  "mlevel": "0",
  "clevel": "0",
  "notes": "Vom Herald importiert am 2025-01-29 14:30"
}
```

#### Angewandte Transformationen

1. **Reichserkennung**:
   ```python
   realm = CLASS_TO_REALM.get(class_name, "Unknown")
   ```

2. **realm_points Konvertierung**:
   ```python
   # Herald-Format: "331 862" (String mit Leerzeichen)
   # Endformat: 331862 (Integer)
   if isinstance(realm_points, str):
       realm_points = int(realm_points.replace(' ', '').replace('\xa0', ''))
   ```

3. **Automatische Reichsrang-Berechnung**:
   ```python
   rank_info = data_manager.get_realm_rank_info(realm, realm_points)
   # Gibt zurück: {rank, title, level, realm_points}
   ```

### Reichsrang-Berechnung

Das System verwendet `Data/realm_ranks_*.json` Dateien zur Rangbestimmung.

**Albion-Beispiel** (`Data/realm_ranks_albion.json`):
```json
{
  "1": {
    "1": {"title": "Guardian", "rp": 0},
    "2": {"title": "Guardian", "rp": 125},
    ...
  },
  "12": {
    "1": {"title": "General", "rp": 309000},
    "2": {"title": "General", "rp": 318000},
    "3": {"title": "General", "rp": 327000}
  }
}
```

**Algorithmus** (`data_manager.py::get_realm_rank_info()`):
```python
def get_realm_rank_info(realm, realm_points):
    # Konvertierung falls String
    if isinstance(realm_points, str):
        realm_points = int(realm_points.replace(' ', '').replace('\xa0', ''))
    
    # Durchlaufe Ränge von hoch nach niedrig
    for rank in range(max_rank, 0, -1):
        for level in range(max_level, 0, -1):
            required_rp = rank_data[rank][level]['rp']
            if realm_points >= required_rp:
                return {
                    'rank': rank,
                    'level': f"{rank}L{level}",
                    'title': rank_data[rank][level]['title'],
                    'realm_points': required_rp
                }
    
    # Standard: 1L1
    return {'rank': 1, 'level': '1L1', 'title': 'Guardian', 'realm_points': 0}
```

### Charakterspeicherung

**Dateistruktur**:
```
Characters/
├── Albion/
│   ├── Ewoline.json
│   └── Paladin42.json
├── Midgard/
│   ├── Olaf.json
│   └── Berserker99.json
└── Hibernia/
    ├── Fionn.json
    └── Druidess.json
```

**Dateiformat** (`Ewoline.json`):
```json
{
  "id": "eindeutige-uuid",
  "name": "Ewoline",
  "class": "Cleric",
  "race": "Briton",
  "realm": "Albion",
  "guild": "Phoenix Rising",
  "level": "50",
  "realm_rank": "12L3",
  "realm_points": 331862,
  "realm_level": "12",
  "server": "Eden",
  "mlevel": "0",
  "clevel": "0",
  "notes": "Vom Herald importiert am 2025-01-29 14:30",
  "page": "1",
  "armor": {
    "head": {"name": "", "type": "", "af": 0, "abs": 0, ...},
    "hands": {...},
    "arms": {...},
    "torso": {...},
    "legs": {...},
    "feet": {...}
  },
  "resists": {
    "crush": 0, "slash": 0, "thrust": 0, "heat": 0, "cold": 0, "matter": 0,
    "body": 0, "spirit": 0, "energy": 0
  }
}
```

---

## ⚠️ Fehlerbehandlung

### Häufige Fehler und Lösungen

#### 1. "❌ Herald nicht erreichbar: Fehlende oder ungültige Cookies"

**Ursache**: Keine konfigurierten Cookies oder abgelaufene Cookies

**Lösung**:
1. Auf "⚙️ Verwalten" klicken
2. Gültige Cookies aus Browser importieren
3. Auf "🔄 Aktualisieren" klicken zur erneuten Prüfung

---

#### 2. "Keine Ergebnisse für 'xxx' gefunden"

**Mögliche Ursachen**:
- Charakter existiert nicht auf Eden-Server
- Falscher Reichsfilter
- Name falsch geschrieben

**Lösung**:
- Rechtschreibung prüfen
- Ohne Reichsfilter versuchen
- Prüfen, ob Charakter auf Eden existiert

---

#### 3. "Bitte mindestens 3 Zeichen eingeben"

**Ursache**: Mindestlängen-Validierung

**Lösung**: Mindestens 3 Zeichen im Suchfeld eingeben

---

#### 4. "X: Charakter existiert bereits"

**Ursache**: Versuch, Duplikat zu importieren

**Verhalten**:
- Bestehender Charakter wird nicht überschrieben
- Als Fehler im Import-Bericht gezählt
- Andere Charaktere werden weiter importiert

**Lösung**: Wenn Aktualisierung gewünscht, zuerst alten Charakter löschen

---

#### 5. "Scraping-Fehler"

**Mögliche Ursachen**:
- Geänderte Herald-Seite (HTML-Struktur geändert)
- Netzwerk-Timeout
- Bot-Check aktiviert trotz Cookies

**Lösung**:
1. Internetverbindung prüfen
2. Aktuelle Cookies neu generieren/importieren
3. Einige Minuten warten vor erneutem Versuch
4. Logs prüfen: `Logs/app.log`

---

### Logs und Debugging

#### Log-Ort

```
%APPDATA%/DAOCCharacterManager/Logs/
└── app.log
```

#### Log-Stufen

```python
logging.DEBUG    # Technische Details (Scraping, Parsing)
logging.INFO     # Allgemeine Informationen (Import erfolgreich)
logging.WARNING  # Warnungen (Duplikat erkannt)
logging.ERROR    # Fehler (Scraping fehlgeschlagen)
logging.CRITICAL # Kritische Fehler (Anwendungsabsturz)
```

#### Beispiel-Logs bei Suche

```
2025-01-29 14:30:15 [INFO] Herald-Suche: name='Ewoline', realm='albion'
2025-01-29 14:30:16 [DEBUG] Chrome-Konfiguration mit Off-Screen-Optionen
2025-01-29 14:30:17 [DEBUG] Lade 3 Cookies von CookieManager
2025-01-29 14:30:18 [INFO] Navigiere zum Herald: https://eden-daoc.net/herald/character/search?name=Ewoline&r=albion
2025-01-29 14:30:20 [DEBUG] Extrahiere 28 HTML-Tabellen
2025-01-29 14:30:21 [INFO] 2 Charaktere gefunden: ['Ewoline', 'Ewolinette']
2025-01-29 14:30:21 [DEBUG] Filterung: behalte nur Namen, die mit 'ewoline' beginnen
2025-01-29 14:30:21 [INFO] Gefilterte Ergebnisse: 2 Charaktere
2025-01-29 14:30:22 [INFO] Temporäre Speicherung: C:\Users\...\Temp\EdenSearchResult\characters_20250129_143022.json
2025-01-29 14:30:22 [INFO] Suche erfolgreich abgeschlossen
```

#### Beispiel-Logs bei Import

```
2025-01-29 14:32:10 [INFO] Importiere 2 ausgewählte Charaktere
2025-01-29 14:32:10 [DEBUG] Import 'Ewoline': Klasse=Cleric, Reich=Albion
2025-01-29 14:32:10 [DEBUG] Prüfe Duplikate: 45 bestehende Charaktere
2025-01-29 14:32:10 [WARNING] Duplikat erkannt: 'Ewoline' existiert bereits
2025-01-29 14:32:10 [DEBUG] Import 'Ewolinette': Klasse=Cleric, Reich=Albion
2025-01-29 14:32:10 [INFO] Speichern: Characters/Albion/Ewolinette.json
2025-01-29 14:32:10 [INFO] Import abgeschlossen: 1 Erfolg, 1 Fehler
2025-01-29 14:32:10 [INFO] Hauptoberfläche aktualisieren
```

---

## 🔧 Technische Konfiguration

### Systemanforderungen

- **Python**: 3.9+
- **Selenium**: 4.15.2+
- **BeautifulSoup4**: 4.12.2+
- **Chrome/Chromium**: Aktuelle Version
- **ChromeDriver**: Kompatibel mit Chrome-Version

### Python-Abhängigkeiten

```
selenium>=4.15.2
beautifulsoup4>=4.12.2
PySide6>=6.6.0
cryptography>=41.0.0
requests>=2.31.0
```

### Umgebungsvariablen (optional)

```bash
# Spezifischen ChromeDriver erzwingen
CHROMEDRIVER_PATH=/pfad/zu/chromedriver

# Benutzerdefiniertes Timeout (Sekunden)
HERALD_TIMEOUT=30

# Log-Stufe
LOG_LEVEL=DEBUG
```

---

## 📈 Leistung und Einschränkungen

### Durchschnittliche Antwortzeiten

| Vorgang | Durchschnittliche Dauer | Hinweise |
|---------|-------------------------|----------|
| Status-Prüfung | 2-4 Sekunden | Abhängig von Netzwerklatenz |
| Suche 1 Charakter | 5-8 Sekunden | Lädt 28 HTML-Tabellen |
| Import 1 Charakter | < 1 Sekunde | Lokaler Vorgang |
| Import 10 Charaktere | < 2 Sekunden | Duplikatsprüfung enthalten |

### Bekannte Einschränkungen

1. **Teilsuche**: Herald unterstützt keine Wildcards
   - `"Ewo*"` funktioniert nicht
   - Lösung: Exakten Namensanfang eingeben

2. **Ergebnisanzahl**: Maximum ~100 Charaktere pro Suche
   - Herald begrenzt angezeigte Ergebnisse
   - Lösung: Spezifischere Namen verwenden

3. **Abgelaufene Cookies**: Begrenzte Lebensdauer (Stunden/Tage)
   - Lösung: Regelmäßig neu importieren

4. **Bot-Check**: Kann sich zufällig reaktivieren
   - Lösung: 5-10 Minuten warten, Cookies neu importieren

---

## 🔐 Sicherheit und Datenschutz

### Sensible Daten

- ✅ **Verschlüsselte Cookies**: Verwendung von Fernet (AES-128)
- ✅ **Eindeutiger Schlüssel**: Bei Installation generiert
- ✅ **Lokale Speicherung**: Keine Daten an Dritte gesendet
- ✅ **Temporäre Dateien**: Automatisch gelöscht

### Best Practices

1. **Nicht teilen**: Datei `eden_cookies.json` nicht weitergeben
2. **Nicht committen**: Cookies nicht in Git (`.gitignore` konfiguriert)
3. **Regelmäßig exportieren**: Ihre Charaktere (Backup)
4. **Aktualisieren**: Cookies bei Zugriffsproblemen

---

## 🆘 Support und Fehlerbehebung

### Diagnose-Checkliste

Wenn Suche nicht funktioniert:

- [ ] Internetverbindung prüfen
- [ ] Manuellen Zugriff auf https://eden-daoc.net testen
- [ ] Prüfen ob Chrome/Chromium installiert ist
- [ ] Aktuelle Cookies neu importieren
- [ ] Auf "🔄 Aktualisieren" klicken zur erneuten Prüfung
- [ ] `Logs/app.log` auf Fehler prüfen
- [ ] Mit bekanntem Charakternamen versuchen

### Vollständiger Reset

Wenn nichts funktioniert:

1. Anwendung schließen
2. `%APPDATA%/DAOCCharacterManager/eden_cookies.json` löschen
3. Anwendung neu starten
4. Frische Cookies neu importieren
5. Suche testen

---

## 📝 Versionshistorie

### Aktuelle Version: 0.105

**Funktionen**:
- ✅ Herald-Suche mit Reichsfilter
- ✅ Einfacher und Massenimport
- ✅ Automatische Reichserkennung
- ✅ Automatische Reichsrang-Berechnung
- ✅ Nach Reich gefärbte Oberfläche
- ✅ Duplikatsvalidierung
- ✅ Automatische Aktualisierung
- ✅ Sichere Cookie-Verwaltung
- ✅ Präzise Ergebnisfilterung (startswith)
- ✅ Gegraute Buttons während Überprüfung

**Aktuelle Korrekturen**:
- 🐛 Fix realm_points String/Int-Konvertierung
- 🐛 Fix fetter Text in Hauptansicht
- 🐛 Fix farbige Titel-Spalte (jetzt normal)
- 🐛 Fix Färbung leerer Zellen
- 🐛 Fix Zentrierung Name- und Gilden-Spalten

---

## 🎓 Glossar

**Bot-Check**: Anti-Automatisierungssystem auf Eden-Site

**Cookie**: Kleine Sitzungsdatei zur Browser-Identifikation

**Delegate**: Qt-Komponente zur Anpassung der Zellendarstellung

**Herald**: Offizielle Website mit DAOC-Statistiken

**Reich**: Königreich (Albion, Midgard, Hibernia)

**Realm Points (RP)**: In RvR akkumulierte Punkte (Reich gegen Reich Kampf)

**Realm Rank (RR)**: Reichsrang (z.B. 12L3 = Rang 12, Stufe 3)

**Scraper**: Programm zur Datenextraktion von Website

**Selenium**: Webbrowser-Automatisierungstool

**Thread**: Parallelprozess um Oberfläche nicht zu blockieren

---

## 📚 Ressourcen

### Technische Dokumentation

- [Selenium Python Docs](https://selenium-python.readthedocs.io/)
- [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [PySide6 Docs](https://doc.qt.io/qtforpython/)

### Eden DAOC Links

- [Hauptseite](https://eden-daoc.net)
- [Herald](https://eden-daoc.net/herald)
- [Discord](https://discord.gg/eden-daoc)

---

## 👥 Credits

**Entwicklung**: ChristophePelichet  
**Version**: 0.105  
**Datum**: Januar 2025  
**Lizenz**: MIT

---

*Diese Dokumentation wird mit jeder Anwendungsversion aktuell gehalten.*
