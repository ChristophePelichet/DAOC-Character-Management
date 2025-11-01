# Gestionnaire de Cookies Eden - Documentation

## Vue d'ensemble

Le gestionnaire de cookies Eden permet de gérer l'authentification pour accéder au Herald Eden-DAOC. Il stocke les cookies d'authentification OAuth Discord et vérifie leur validité.

## Fichiers concernés

- **Functions/cookie_manager.py** : Classe `CookieManager` pour la gestion des cookies
- **UI/dialogs.py** : `CookieManagerDialog` - Interface graphique de gestion
- **Functions/ui_manager.py** : Barre de statut Eden dans l'interface principale

## Fonctionnalités

### 1. Génération de cookies
- Ouvre un navigateur Chrome pour l'authentification Discord OAuth
- Récupère automatiquement les cookies après connexion
- Sauvegarde dans `Configuration/eden_cookies.pkl`

### 2. Validation des cookies
- Vérifie la date d'expiration (364 jours)
- Teste l'accès réel au Herald Eden (`https://eden-daoc.net/herald?n=top_players&r=hib`)
- Détecte les cookies invalides ou expirés

### 3. Import/Export
- Import de fichiers .pkl de cookies existants
- Sauvegarde automatique de backup avant suppression
- Validation du format lors de l'import

### 4. Interface utilisateur

#### Barre de statut principale
Affichée dans la fenêtre principale entre le menu et les actions :
- **Statut** : ✅ Herald accessible / ❌ Message d'erreur / ⏳ Vérification en cours
- **Bouton Actualiser** : Re-teste la connexion
- **Bouton Gérer** : Ouvre le gestionnaire détaillé

#### Fenêtre de gestion
Accessible via le bouton "⚙️ Gérer" :
- **Statut des cookies** : Valides / Expirés / Absents
- **Date d'expiration** : Affichage avec compte à rebours
- **Test de connexion** : Vérification en temps réel (thread en arrière-plan)
- **Actions** :
  - 🔐 Générer des Cookies : Lance le processus OAuth
  - 🔄 Actualiser : Rafraîchit l'affichage
  - 🗑️ Supprimer : Supprime les cookies (avec backup)
- **Import** : Zone de texte + bouton Parcourir pour importer un fichier

## Utilisation

### Générer des cookies pour la première fois
1. Cliquer sur "⚙️ Gérer" dans la barre de statut Eden
2. Cliquer sur "🔐 Générer des Cookies"
3. Se connecter avec Discord dans le navigateur qui s'ouvre
4. Cliquer sur "Entrée" après connexion
5. Les cookies sont automatiquement sauvegardés

### Vérifier le statut
La barre de statut principale affiche en temps réel l'état de connexion au Herald. Le test se fait automatiquement au démarrage en arrière-plan.

### Importer des cookies existants
1. Ouvrir le gestionnaire ("⚙️ Gérer")
2. Saisir le chemin du fichier .pkl OU cliquer sur "📁 Parcourir"
3. Appuyer sur Entrée ou cliquer sur Importer
4. Le statut se met à jour automatiquement

## Architecture technique

### Classes principales

#### CookieManager (Functions/cookie_manager.py)
- `cookie_exists()` : Vérifie la présence du fichier de cookies
- `get_cookie_info()` : Retourne les informations détaillées (validité, expiration, compteurs)
- `generate_cookies_with_browser()` : Lance le processus d'authentification
- `save_cookies_from_driver()` : Récupère les cookies depuis Selenium
- `import_cookie_file()` : Importe un fichier de cookies externe
- `delete_cookies()` : Supprime avec backup automatique
- `test_eden_connection()` : Teste l'accès au Herald avec Selenium

#### ConnectionTestThread (UI/dialogs.py)
Thread QThread pour exécuter le test de connexion en arrière-plan sans bloquer l'interface.

#### EdenStatusThread (Functions/ui_manager.py)
Thread QThread pour la barre de statut principale, met à jour l'indicateur de connexion.

### Format des cookies
Fichier pickle contenant une liste de dictionnaires avec :
```python
{
    'name': 'eden_daoc_sid',
    'value': '...',
    'domain': '.eden-daoc.net',
    'path': '/',
    'expiry': 1761753600  # Timestamp Unix
}
```

### Test de connexion
1. Initialise un driver Chrome headless
2. Charge la page d'accueil Eden
3. Injecte les cookies
4. Navigue vers `https://eden-daoc.net/herald?n=top_players&r=hib`
5. Analyse le contenu pour détecter :
   - Redirection vers login → cookies invalides
   - Formulaire de connexion → non authentifié
   - Contenu Herald présent → connexion OK

## Dépendances

- **selenium** : Automatisation du navigateur
- **webdriver-manager** : Gestion automatique du ChromeDriver
- **PySide6** : Interface graphique (QThread, QDialog)

## Gestion des erreurs

### Cookies non trouvés
- Affichage : "❌ Aucun cookie trouvé"
- Action : Générer de nouveaux cookies

### Cookies expirés
- Affichage : "⚠️ Cookies expirés"
- Action : Régénérer les cookies

### Erreur de connexion
- Affichage : "❌ [Message d'erreur]"
- Causes possibles :
  - Pas de connexion Internet
  - Serveur Eden inaccessible
  - ChromeDriver non installé
  - Module manquant (selenium, requests)

### Import échoué
- Validation du chemin de fichier
- Vérification du format pickle
- Messages d'erreur détaillés avec logging

## Sécurité

- **Stockage local** : Les cookies sont stockés en local dans `Configuration/`
- **Backup automatique** : Sauvegarde avant suppression
- **Pas de transmission** : Les cookies ne sont jamais envoyés ailleurs que vers Eden-DAOC
- **Durée de vie** : 364 jours, puis renouvellement nécessaire

## Logs

Tous les événements sont enregistrés via le module `logging` :
- INFO : Opérations réussies (génération, import, test)
- WARNING : Problèmes non bloquants (cookie spécifique non ajouté)
- ERROR : Erreurs bloquantes (import échoué, driver non initialisé)
- CRITICAL : Erreurs graves (exception non gérée)

## Évolutions futures (Phase 2)

- Intégration complète du scraper pour importer des personnages depuis le Herald
- Synchronisation automatique des données de personnages
- Gestion de plusieurs comptes Discord
- Cache des données scrapées
- Interface de recherche de personnages/guildes
