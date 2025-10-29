# Eden Scraper - Documentation

## Vue d'ensemble

Le module Eden Scraper permet d'extraire des données depuis le Herald Eden-DAOC. Il utilise Selenium pour gérer les sessions authentifiées et BeautifulSoup pour parser le HTML.

## Fichier

- **Functions/eden_scraper.py** : Classe `EdenScraper` pour le scraping

## Fonctionnalités

### 1. Scraping de personnages individuels
Extrait toutes les données d'un personnage depuis sa page Herald :
- Statistiques de base
- Équipement
- Realm Ranks et Abilities
- Tableaux de données structurées

### 2. Recherche de personnages
Effectue des recherches sur le Herald :
- Par nom de joueur
- Par guilde
- Filtrage par realm (Albion, Midgard, Hibernia)

### 3. Gestion de session
- Utilise les cookies du CookieManager
- Maintient la session Selenium active
- Fermeture automatique via context manager

## Utilisation

### Scraper un personnage

```python
from Functions.cookie_manager import CookieManager
from Functions.eden_scraper import EdenScraper

# Initialiser le cookie manager
cookie_manager = CookieManager()

# Utiliser le context manager pour le scraper
with EdenScraper(cookie_manager) as scraper:
    data = scraper.scrape_character("Ewolinette")
    
    if data:
        print(f"Personnage: {data['character_name']}")
        print(f"Tables de données: {len(data['tables'])}")
```

### Rechercher des personnages

```python
from Functions.eden_scraper import EdenScraper

with EdenScraper(cookie_manager) as scraper:
    results = scraper.scrape_search_results("Ewoli", realm="hib")
    
    for char in results:
        print(f"- {char['name']}: {char['url']}")
```

### Fonctions utilitaires

```python
from Functions.eden_scraper import scrape_character_by_name, search_characters

# Scraper rapidement un personnage
data = scrape_character_by_name("Ewolinette", cookie_manager)

# Rechercher
characters = search_characters("Ewoli", realm="hib", cookie_manager=cookie_manager)
```

## API de la classe EdenScraper

### Constructeur
```python
scraper = EdenScraper(cookie_manager)
```
- **cookie_manager** : Instance de CookieManager pour l'authentification

### Méthodes principales

#### initialize_driver(headless=True)
Initialise le driver Selenium Chrome.
- **headless** : Si True, lance en mode sans interface
- **Returns** : bool - True si succès

#### load_cookies()
Charge les cookies d'authentification dans le driver.
- **Returns** : bool - True si les cookies ont été chargés

#### scrape_character(character_name)
Scrape les données d'un personnage.
- **character_name** : Nom du personnage
- **Returns** : dict - Données du personnage ou None

Structure des données retournées :
```python
{
    'character_name': 'Ewolinette',
    'scraped_at': '2025-10-29T18:30:00',
    'title': 'Eden Herald - Ewolinette',
    'h1': ['Titre niveau 1'],
    'h2': ['Titre niveau 2'],
    'h3': ['Titre niveau 3'],
    'tables': [
        [
            ['Header1', 'Header2'],
            ['Data1', 'Data2']
        ]
    ]
}
```

#### scrape_search_results(search_query, realm=None)
Recherche des personnages sur le Herald.
- **search_query** : Terme de recherche
- **realm** : Optionnel - 'alb', 'mid' ou 'hib'
- **Returns** : list - Liste des personnages trouvés

Structure des résultats :
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
Ferme le driver Selenium proprement.

### Context Manager
Le scraper supporte le context manager pour une gestion automatique des ressources :

```python
with EdenScraper(cookie_manager) as scraper:
    # Le driver est automatiquement fermé à la sortie
    data = scraper.scrape_character("Test")
```

## Extraction de données

### _extract_character_data(soup)
Méthode privée qui extrait les données structurées depuis BeautifulSoup :
- Titre de la page
- Tous les titres H1, H2, H3
- Tous les tableaux HTML convertis en listes

### _extract_search_results(soup)
Méthode privée qui extrait la liste des personnages depuis les résultats de recherche.

## Gestion des erreurs

### Driver non initialisé
- Tentative d'initialisation automatique lors du premier scrape
- Log d'erreur si l'initialisation échoue

### Cookies invalides
```python
if not scraper.load_cookies():
    logging.error("Impossible de charger les cookies")
    return None
```

### Erreur de scraping
- Exception capturée et loggée
- Retourne None au lieu de crasher

## Dépendances

- **selenium** : Automatisation du navigateur
- **webdriver-manager** : Gestion du ChromeDriver
- **beautifulsoup4** : Parsing HTML
- **lxml** : Parser HTML rapide (optionnel mais recommandé)

## Performance

### Mode headless
Le mode headless (sans interface) est activé par défaut pour :
- Réduire la consommation de ressources
- Accélérer le scraping
- Permettre l'exécution en arrière-plan

### Délais
Un délai de 2 secondes est appliqué après chaque chargement de page pour :
- Laisser le temps au JavaScript de s'exécuter
- Éviter de surcharger le serveur Eden
- Assurer le chargement complet du contenu

## Sécurité et bonnes pratiques

### Respect du serveur
- Délais entre requêtes
- Pas de requêtes parallèles abusives
- Fermeture propre des sessions

### Gestion des cookies
- Utilise toujours le CookieManager
- Ne stocke jamais les cookies en dur dans le code
- Vérifie la validité avant chaque session

### Logs
Tous les événements sont enregistrés :
```python
logging.info("Scraping du personnage: Ewolinette")
logging.error("Erreur lors du scraping: [détails]")
```

## Limitations

- **JavaScript** : Certains éléments dynamiques peuvent ne pas être capturés
- **Structure HTML** : Le scraper dépend de la structure actuelle du Herald
- **Rate limiting** : Pas de limitation implémentée côté client
- **Mise en cache** : Pas de cache des résultats (à implémenter en Phase 2)

## Évolutions futures

### Phase 2 - Intégration complète
- Import automatique de personnages dans l'application
- Synchronisation bidirectionnelle des données
- Cache des données scrapées
- Détection des changements (équipement, stats)
- Interface de recherche intégrée

### Optimisations
- Pool de drivers pour scraping parallèle
- Mise en cache intelligente
- Détection de changements HTML (alertes si structure change)
- Extraction plus précise des stats (parsing avancé)

## Exemples d'usage avancé

### Scraper tous les personnages d'une guilde

```python
with EdenScraper(cookie_manager) as scraper:
    # Rechercher la guilde
    members = scraper.scrape_search_results("NomGuild", realm="hib")
    
    # Scraper chaque membre
    all_data = []
    for member in members:
        char_name = member['name'].split()[0]
        data = scraper.scrape_character(char_name)
        if data:
            all_data.append(data)
    
    print(f"{len(all_data)} personnages scrapés")
```

### Exporter en JSON

```python
import json

data = scrape_character_by_name("Ewolinette", cookie_manager)
if data:
    with open('character_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```
