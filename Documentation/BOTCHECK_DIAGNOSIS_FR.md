# Problème Bot Check Herald - Diagnostic et Solutions

## Date
29 octobre 2025

## Problème identifié

### Symptômes
- L'URL de recherche `https://eden-daoc.net/herald?n=search&s={character_name}` renvoie une page "Bot check"
- Aucun tableau HTML n'est trouvé dans la page
- Le fichier JSON sauvegardé contient 0 résultats
- Le timeout de 15 secondes ne suffit pas à résoudre le challenge

### Analyse technique
Le site Eden-DAOC utilise un **challenge anti-bot JavaScript** sur la page de recherche qui :
1. Détecte l'utilisation de Selenium/WebDriver
2. Empêche l'accès au contenu tant que le challenge n'est pas résolu
3. Est particulièrement efficace contre les navigateurs headless

### Preuve
```
📊 Nombre de tableaux trouvés: 0
🤖 Bot check: ✅ Détecté
💾 HTML sauvegardé: debug_search_page.html contient seulement:
<title>Bot check</title>
```

## Solutions potentielles

### Solution 1: Anti-détection avancée (✅ Implémentée)
Modifications apportées à `Functions/eden_scraper.py`:

```python
# Nouveau mode headless
chrome_options.add_argument('--headless=new')

# Anti-détection
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# User agent réaliste
chrome_options.add_argument('user-agent=Mozilla/5.0 ...')

# Masquer webdriver
self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    'source': '''
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    '''
})
```

**Résultat**: Toujours timeout - le bot check reste actif

### Solution 2: Temps d'attente prolongé (✅ Implémentée)
Augmentation du timeout de 3s à 15s avec détection active:

```python
max_wait = 15
for i in range(max_wait):
    time.sleep(1)
    if '<table' in page_source.lower():
        break
```

**Résultat**: Toujours timeout - le bot check ne se résout pas automatiquement

### Solution 3: Mode non-headless (🔄 En test)
Le bot check pourrait se résoudre plus facilement dans un navigateur visible.

**Scripts de test créés**:
- `Scripts/test_search_visible.py` - Test avec navigateur visible
- `Scripts/test_herald_pages.py` - Test de plusieurs pages Herald

**À tester**:
1. La page se charge-t-elle sans bot check en mode visible ?
2. Le challenge se résout-il automatiquement après quelques secondes ?
3. Y a-t-il un formulaire de recherche ailleurs dans le Herald ?

### Solution 4: Page alternative (🔍 À explorer)
Hypothèses:
- La page `n=search` pourrait être plus protégée que d'autres
- Il pourrait exister un formulaire de recherche sur la page principale
- Les URLs directes de personnages (`n=player&k={name}`) pourraient fonctionner

**Pages à tester**:
```
https://eden-daoc.net/herald              # Page principale
https://eden-daoc.net/herald?n=top_players # Top players (fonctionne ✅)
https://eden-daoc.net/herald?n=player&k={name}  # Direct player access
```

### Solution 5: Utiliser l'API ou un endpoint alternatif
Si le Herald expose une API ou un endpoint moins protégé.

**À investiguer**:
- Rechercher dans le code source JavaScript du Herald
- Analyser les requêtes réseau (DevTools)
- Chercher des APIs documentées

### Solution 6: Session persistante
Utiliser une session de navigateur authentifiée et la réutiliser.

**Concept**:
1. Ouvrir le Herald en mode manuel (avec authentification)
2. Sauvegarder le profile Chrome complet (pas juste les cookies)
3. Réutiliser ce profile pour les scraping automatiques

### Solution 7: Recherche par URL directe
Si on connaît le nom exact du personnage, construire l'URL directement:

```python
player_url = f"https://eden-daoc.net/herald?n=player&k={character_name}"
```

**Avantages**:
- Pas de page de recherche
- Accès direct au personnage
- Potentiellement moins de protection anti-bot

**Inconvénients**:
- Nécessite le nom exact
- Pas de suggestions si le nom est incorrect
- Pas de liste de résultats multiples

## Tests à effectuer

### Test 1: Pages Herald sans bot check
Script: `test_herald_pages.py`

**Objectif**: Identifier quelles pages fonctionnent sans bot check

**Résultat attendu**:
```
✅ Page principale: Pas de bot check
✅ Top players: Pas de bot check (déjà confirmé)
❌ Formulaire recherche: Bot check actif
```

### Test 2: Accès direct personnage
**URL à tester**: `https://eden-daoc.net/herald?n=player&k=Testchar`

**Questions**:
1. Le bot check est-il présent ?
2. La page affiche-t-elle "personnage non trouvé" ou un bot check ?
3. Les cookies sont-ils suffisants ?

### Test 3: Mode visible prolongé
Script: `test_search_visible.py`

**Procédure**:
1. Lancer en mode visible
2. Observer le navigateur
3. Noter après combien de temps le bot check se résout
4. Identifier si une action utilisateur est nécessaire

## Recommandations

### Court terme (immédiat)
1. ✅ Tester `test_herald_pages.py` pour identifier les pages accessibles
2. ✅ Tester l'accès direct aux personnages (`n=player&k={name}`)
3. Si l'accès direct fonctionne : modifier la recherche pour :
   - Essayer l'URL directe en premier
   - Afficher un message clair si le personnage n'existe pas
   - Sauvegarder le résultat même si c'est "non trouvé"

### Moyen terme (si nécessaire)
1. Implémenter une recherche via formulaire HTML si trouvé sur une autre page
2. Ajouter un mode "recherche manuelle" :
   - Ouvrir le navigateur en mode visible
   - Laisser l'utilisateur faire la recherche manuellement
   - Scraper le résultat une fois affiché

### Long terme
1. Chercher si Eden-DAOC propose une API officielle
2. Contacter les développeurs pour demander un accès API
3. Implémenter un système de résolution de CAPTCHA si nécessaire

## Code mis à jour

### Fichiers modifiés
1. `Functions/eden_scraper.py`
   - Ajout options anti-détection
   - Timeout prolongé à 15s
   - Détection active du bot check

2. `Scripts/test_herald_search.py`
   - Correction de l'affichage des infos cookies

### Fichiers créés
1. `Scripts/debug_herald_search.py` - Analyse détaillée de la page
2. `Scripts/test_search_visible.py` - Test en mode visible
3. `Scripts/test_herald_pages.py` - Test de plusieurs pages
4. `Documentation/BOTCHECK_DIAGNOSIS_FR.md` - Ce fichier

## Prochaines étapes

1. **Exécuter** `test_herald_pages.py` pour voir quelles pages sont accessibles
2. **Tester** l'accès direct aux personnages
3. **Décider** de la stratégie en fonction des résultats :
   - Si accès direct fonctionne → Modifier pour utiliser `n=player&k={name}`
   - Si formulaire trouvé → Utiliser soumission de formulaire
   - Si rien ne fonctionne → Mode manuel ou abandon de la recherche automatique

## Notes
- Les cookies sont valides (4 cookies, valide jusqu'en 2026)
- La page `top_players` fonctionne sans problème (utilisée pour le test de connexion)
- Le problème est spécifique à la page `n=search`
