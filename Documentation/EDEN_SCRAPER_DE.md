# Eden Scraper - Dokumentation

## Übersicht

Das Eden Scraper-Modul extrahiert Daten aus dem Eden-DAOC Herald. Es verwendet Selenium zur Verwaltung authentifizierter Sitzungen und BeautifulSoup zum Parsen von HTML.

## Datei

- **Functions/eden_scraper.py**: `EdenScraper`-Klasse für Scraping

## Funktionen

### 1. Individuelles Charakter-Scraping
Extrahiert alle Daten von einer Charakter-Herald-Seite:
- Grundstatistiken
- Ausrüstung
- Realm Ranks und Fähigkeiten
- Strukturierte Datentabellen

### 2. Charaktersuche
Führt Herald-Suchen durch:
- Nach Spielername
- Nach Gilde
- Filterung nach Realm (Albion, Midgard, Hibernia)

### 3. Sitzungsverwaltung
- Verwendet CookieManager-Cookies
- Hält aktive Selenium-Sitzung aufrecht
- Automatisches Schließen via Context Manager

## Verwendung

### Einen Charakter scrapen

```python
from Functions.cookie_manager import CookieManager
from Functions.eden_scraper import EdenScraper

# Cookie-Manager initialisieren
cookie_manager = CookieManager()

# Context Manager für Scraper verwenden
with EdenScraper(cookie_manager) as scraper:
    data = scraper.scrape_character("Ewolinette")
    
    if data:
        print(f"Charakter: {data['character_name']}")
        print(f"Datentabellen: {len(data['tables'])}")
```

### Charaktere suchen

```python
from Functions.eden_scraper import EdenScraper

with EdenScraper(cookie_manager) as scraper:
    results = scraper.scrape_search_results("Ewoli", realm="hib")
    
    for char in results:
        print(f"- {char['name']}: {char['url']}")
```

### Hilfsfunktionen

```python
from Functions.eden_scraper import scrape_character_by_name, search_characters

# Schnell einen Charakter scrapen
data = scrape_character_by_name("Ewolinette", cookie_manager)

# Suchen
characters = search_characters("Ewoli", realm="hib", cookie_manager=cookie_manager)
```

## EdenScraper-Klassen-API

### Konstruktor
```python
scraper = EdenScraper(cookie_manager)
```
- **cookie_manager**: CookieManager-Instanz für Authentifizierung

### Hauptmethoden

#### initialize_driver(headless=True)
Initialisiert Selenium Chrome-Treiber.
- **headless**: Wenn True, startet im Headless-Modus
- **Returns**: bool - True bei Erfolg

#### load_cookies()
Lädt Authentifizierungs-Cookies in Treiber.
- **Returns**: bool - True wenn Cookies geladen wurden

#### scrape_character(character_name)
Scrapt Charakterdaten.
- **character_name**: Charaktername
- **Returns**: dict - Charakterdaten oder None

Zurückgegebene Datenstruktur:
```python
{
    'character_name': 'Ewolinette',
    'scraped_at': '2025-10-29T18:30:00',
    'title': 'Eden Herald - Ewolinette',
    'h1': ['Überschrift Ebene 1'],
    'h2': ['Überschrift Ebene 2'],
    'h3': ['Überschrift Ebene 3'],
    'tables': [
        [
            ['Header1', 'Header2'],
            ['Data1', 'Data2']
        ]
    ]
}
```

#### scrape_search_results(search_query, realm=None)
Sucht Charaktere im Herald.
- **search_query**: Suchbegriff
- **realm**: Optional - 'alb', 'mid' oder 'hib'
- **Returns**: list - Liste gefundener Charaktere

Ergebnisstruktur:
```python
[
    {
        'name': 'Ewolinette',
        'url': 'https://eden-daoc.net/herald?n=player&k=Ewolinette',
        'raw_data': ['Ewolinette', 'Mentalist', 'Lurikeen', ...]
    }
]
```

#### close()
Schließt Selenium-Treiber sauber.

### Context Manager
Der Scraper unterstützt Context Manager für automatische Ressourcenverwaltung:

```python
with EdenScraper(cookie_manager) as scraper:
    # Treiber wird automatisch beim Verlassen geschlossen
    data = scraper.scrape_character("Test")
```

## Datenextraktion

### _extract_character_data(soup)
Private Methode, die strukturierte Daten aus BeautifulSoup extrahiert:
- Seitentitel
- Alle H1-, H2-, H3-Überschriften
- Alle HTML-Tabellen in Listen konvertiert

### _extract_search_results(soup)
Private Methode, die Charakterliste aus Suchergebnissen extrahiert.

## Fehlerbehandlung

### Treiber nicht initialisiert
- Automatischer Initialisierungsversuch beim ersten Scrape
- Fehlerprotokoll wenn Initialisierung fehlschlägt

### Ungültige Cookies
```python
if not scraper.load_cookies():
    logging.error("Cookies können nicht geladen werden")
    return None
```

### Scraping-Fehler
- Ausnahme abgefangen und protokolliert
- Gibt None zurück statt abzustürzen

## Abhängigkeiten

- **selenium**: Browser-Automatisierung
- **webdriver-manager**: ChromeDriver-Verwaltung
- **beautifulsoup4**: HTML-Parsing
- **lxml**: Schneller HTML-Parser (optional aber empfohlen)

## Leistung

### Headless-Modus
Headless-Modus (keine Oberfläche) ist standardmäßig aktiviert für:
- Reduzierter Ressourcenverbrauch
- Schnelleres Scraping
- Hintergrundausführung ermöglichen

### Verzögerungen
Eine 2-Sekunden-Verzögerung wird nach jedem Seitenladen angewendet für:
- JavaScript-Ausführungszeit
- Vermeidung von Eden-Server-Überlastung
- Sicherstellung vollständigen Inhaltsladens

## Sicherheit und Best Practices

### Server-Respekt
- Verzögerungen zwischen Anfragen
- Keine missbräuchlichen parallelen Anfragen
- Sauberes Sitzungsschließen

### Cookie-Verwaltung
- Verwendet immer CookieManager
- Speichert nie Cookies fest im Code
- Prüft Gültigkeit vor jeder Sitzung

### Protokolle
Alle Ereignisse werden protokolliert:
```python
logging.info("Scraping Charakter: Ewolinette")
logging.error("Scraping-Fehler: [Details]")
```

## Einschränkungen

- **JavaScript**: Einige dynamische Elemente werden möglicherweise nicht erfasst
- **HTML-Struktur**: Scraper hängt von aktueller Herald-Struktur ab
- **Rate Limiting**: Keine clientseitige Begrenzung implementiert
- **Caching**: Kein Ergebnis-Caching (in Phase 2 zu implementieren)

## Zukünftige Verbesserungen

### Phase 2 - Vollständige Integration
- Automatischer Charakter-Import in Anwendung
- Bidirektionale Datensynchronisierung
- Gescrapte Daten-Caching
- Änderungserkennung (Ausrüstung, Stats)
- Integrierte Suchoberfläche

### Optimierungen
- Treiber-Pool für paralleles Scraping
- Intelligentes Caching
- HTML-Änderungserkennung (Warnungen bei Strukturänderungen)
- Genauere Stat-Extraktion (erweitertes Parsing)

## Erweiterte Verwendungsbeispiele

### Alle Gildenmitglieder scrapen

```python
with EdenScraper(cookie_manager) as scraper:
    # Gilde suchen
    members = scraper.scrape_search_results("GildenName", realm="hib")
    
    # Jedes Mitglied scrapen
    all_data = []
    for member in members:
        char_name = member['name'].split()[0]
        data = scraper.scrape_character(char_name)
        if data:
            all_data.append(data)
    
    print(f"{len(all_data)} Charaktere gescrapt")
```

### Export nach JSON

```python
import json

data = scrape_character_by_name("Ewolinette", cookie_manager)
if data:
    with open('character_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```
