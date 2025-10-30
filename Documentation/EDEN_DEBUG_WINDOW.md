# Fenêtre de Debug Eden

## Vue d'ensemble

La fenêtre de **Debug Eden** est un outil dédié pour surveiller et déboguer toutes les opérations liées à Eden Herald, y compris :

- 🍪 **Gestion des cookies** : Génération, importation, validation
- 🌐 **Connexion au navigateur** : Détection, initialisation, sélection
- 📡 **Connexion Herald** : Tests de connexion, scraping de données
- 🔍 **Recherche de personnages** : Requêtes et résultats

## Accès

Pour ouvrir la fenêtre de debug Eden :

1. Menu principal → **Debug** → **🌐 Debug Eden**
2. Ou utilisez le raccourci clavier (si configuré)

## Interface

### Apparence

La fenêtre utilise un **thème sombre** inspiré de VS Code :

- 🎨 **Arrière-plan** : #1e1e1e (gris foncé)
- 📝 **Texte** : #d4d4d4 (gris clair)
- 🔤 **Police** : Consolas (monospace)

### Composants

1. **Zone de logs** : Affiche les messages en temps réel avec coloration syntaxique
2. **Compteur de logs** : Nombre total de messages capturés
3. **Boutons d'action** :
   - **Exporter** : Sauvegarde les logs dans un fichier .txt horodaté
   - **Effacer** : Vide la zone de logs (ne supprime pas les logs déjà écrits)

## Coloration des Logs

Les messages sont automatiquement colorés selon leur contenu :

| Couleur | Mots-clés | Usage |
|---------|-----------|-------|
| 🟢 **Vert** (#4ec9b0) | succès, réussi, OK, valid | Opérations réussies |
| 🔴 **Rouge** (#f48771) | erreur, échec, failed, error | Erreurs et problèmes |
| 🟠 **Orange** (#ce9178) | attention, warning, alert | Avertissements |
| 🟡 **Jaune** (#dcdcaa) | recherche, détection, search | Opérations de recherche |
| 🔵 **Bleu** (#569cd6) | navigateur, browser, chrome, edge, firefox | Opérations de navigateur |
| 🟣 **Violet** (#c586c0) | cookie, cookies, authentification | Gestion des cookies |
| 🔷 **Cyan** (#9cdcfe) | configuration, config, paramètre | Configuration |

## Cas d'utilisation

### 1. Déboguer un problème de cookies

**Problème** : Les cookies ne se génèrent pas correctement.

**Solution** :
1. Ouvrir la fenêtre Debug Eden
2. Aller dans **Gestion des cookies** → **Générer**
3. Observer les logs en temps réel :
   - Vérifier la détection du navigateur (🔵 bleu)
   - Confirmer l'ouverture du navigateur (🟢 vert)
   - Vérifier la sauvegarde des cookies (🟣 violet)

### 2. Diagnostiquer un échec de connexion Herald

**Problème** : Le test de connexion échoue.

**Solution** :
1. Ouvrir Debug Eden
2. Effectuer un test de connexion
3. Analyser les logs :
   - URL testée
   - Cookies chargés
   - Résultat du test (🟢 succès ou 🔴 erreur)

### 3. Comprendre la sélection du navigateur

**Problème** : Le mauvais navigateur est utilisé.

**Solution** :
1. Ouvrir Debug Eden
2. Regarder les logs au démarrage ou lors d'une opération
3. Identifier l'ordre de priorité (📋 configuration)
4. Vérifier le navigateur utilisé (🔵 bleu)

### 4. Exporter les logs pour le support

Si vous devez partager vos logs pour obtenir de l'aide :

1. Reproduire le problème avec Debug Eden ouvert
2. Cliquer sur **Exporter**
3. Le fichier sera sauvegardé dans le dossier `Logs/` avec un nom du type :
   `eden_debug_2024-01-15_14-30-45.txt`
4. Partager ce fichier

## Différence avec la Console Debug Standard

| Fonctionnalité | Console Debug | Debug Eden |
|----------------|---------------|------------|
| **Logs affichés** | Tous les logs de l'application | Uniquement Eden/cookies/Herald |
| **Thème** | Clair ou système | Sombre (VS Code) |
| **Coloration** | Basique | Avancée (8 couleurs) |
| **Export** | Oui | Oui |
| **Usage** | Débogage général | Débogage Eden spécifique |

## Logs Capturés

Tous les logs provenant des modules suivants sont capturés :

- `Functions/cookie_manager.py` : Gestion des cookies Eden
- `Functions/eden_scraper.py` : Scraping du Herald
- `UI/dialogs.py` (CookieManagerDialog) : Interface de gestion des cookies

### Niveaux de logs

- **DEBUG** : Informations détaillées pour le débogage
- **INFO** : Messages informatifs généraux
- **WARNING** : Avertissements (opérations inhabituelles)
- **ERROR** : Erreurs (échecs d'opérations)

## Configuration

### Activer les logs de debug

Pour voir tous les logs de debug (niveau DEBUG) :

1. Aller dans **Paramètres** → **Debug**
2. Cocher **Activer le mode débogage**
3. Redémarrer l'application

### Changer le navigateur préféré

1. **Paramètres** → **Paramètres généraux**
2. Section **Navigateur**
3. Sélectionner votre navigateur préféré (Chrome, Edge, Firefox)

## Exemples de Messages

### Connexion réussie
```
✅ Chrome (Selenium Manager)
🍪 4 cookies sauvegardés dans eden_cookies.pkl
✅ Connexion Herald réussie
```

### Échec de connexion
```
❌ Chrome: Impossible d'initialiser le driver
⚠️ Tentative avec Edge...
✅ Edge (Selenium Manager)
```

### Génération de cookies
```
🔍 Détection des navigateurs disponibles...
📋 Navigateurs détectés: Chrome, Edge
🌐 Ouverture du navigateur pour authentification Eden
✅ Navigateur initialisé: Edge
En attente de l'authentification...
🍪 4 cookies extraits du navigateur
```

## Dépannage

### La fenêtre ne s'ouvre pas

**Cause possible** : Erreur d'importation.

**Solution** :
1. Vérifier les logs de la console principale
2. Vérifier que `UI/debug_window.py` existe
3. Redémarrer l'application

### Aucun log n'apparaît

**Cause possible** : Le logger 'eden' n'est pas correctement initialisé.

**Solution** :
1. Vérifier que `logging.getLogger('eden')` est utilisé dans les fichiers Eden
2. Redémarrer l'application
3. Vérifier le mode débogage activé dans les paramètres

### Les couleurs ne s'affichent pas

**Cause possible** : Problème d'encodage HTML.

**Solution** :
1. Fermer et rouvrir la fenêtre Debug Eden
2. Si le problème persiste, utiliser le bouton **Exporter** pour obtenir une version texte

## Notes Techniques

### Architecture

La fenêtre utilise :
- **QTextEdit** pour l'affichage avec support HTML
- **QTextEditHandler** pour capturer les logs du logger 'eden'
- **HTMLFormatter** pour formater les messages avec couleurs

### Performance

- Les logs sont affichés en temps réel
- Aucune limite de nombre de logs (jusqu'à saturation de la mémoire)
- L'export peut prendre quelques secondes pour de gros volumes

### Sécurité

- Les logs ne contiennent **jamais** de mots de passe
- Les cookies sont référencés par leur nom uniquement
- Les URLs complètes peuvent être affichées

## Mise à jour

Cette fonctionnalité a été ajoutée dans la **version 0.105** du gestionnaire de personnages.

Pour les versions futures, consultez le CHANGELOG pour les nouvelles fonctionnalités de debug.
