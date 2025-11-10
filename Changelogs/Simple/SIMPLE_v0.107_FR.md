# v0.107 - Statistiques RvR/PvP/PvE Herald & Améliorations UI

## 🎯 Résumé (10 novembre 2025)

✅ Statistiques complètes RvR/PvP/PvE/Wealth depuis Herald  
✅ **Nouveau : Layout 50/50 pour sections RvR/PvP et PvE/Monnaies**  
✅ **Nouveau : Section Réalisations (Achievements) fonctionnelle**  
✅ **Amélioration : Alignement PvP avec QGridLayout**  
✅ **Amélioration : Détails royaume sur la même ligne**  
✅ **Amélioration : Section PvE avec séparateur vertical**  
✅ **Amélioration : Réalisations en 2 colonnes de 8 avec QGridLayout**  
✅ Bouton "Actualiser Stats" désactivé pendant validation Herald  
✅ Bouton "Informations" sur les statistiques  
✅ Affichage amélioré de la monnaie (taille réduite, gras conservé)  
✅ Messages d'erreur détaillés (RvR/PvP/PvE/Wealth)  
✅ Fix crash test connexion Herald  
✅ **Fix : Suppression fichiers debug HTML automatiques**  

---

## 📊 Nouvelles Statistiques Herald

### ⚔️ Section RvR
- 🗼 **Tower Captures** : Nombre de tours capturées  
- 🏰 **Keep Captures** : Nombre de forteresses capturées  
- 💎 **Relic Captures** : Nombre de reliques capturées  

### 🗡️ Section PvP avec Répartition par Royaume
- ⚔️ **Solo Kills** : Total + détail Alb/Hib/Mid  
- 💀 **Deathblows** : Total + détail Alb/Hib/Mid  
- 🎯 **Kills** : Total + détail Alb/Hib/Mid  
- Couleurs par royaume : Rouge (Alb) / Vert (Hib) / Bleu (Mid)  
- Affichage : `Kills: 4,715 → Alb: 1,811 | Hib: 34 | Mid: 2,870`

### � Section PvE
- 🐉 **Dragons** : Kills de dragons majeurs  
- 👹 **Légions** : Kills de légionnaires  
- 🐲 **Mini Dragons** : Kills de jeunes dragons  
- ⚔️ **Epic Encounters** : Rencontres épiques  
- 🏛️ **Epic Dungeons** : Donjons épiques complétés  
- 🐊 **Sobekite** : Boss Sobekite

### 💰 Section Wealth
- **Monnaie** : Affichage au format "18p 128g 45s 12c"  
- Style : Taille 9pt en gras

---

## ℹ️ Nouveau : Bouton "Informations"

### Fonctionnalité
- **Bouton ℹ️** : Placé à côté du bouton "Actualiser Stats"  
- **Message explicatif** : Informe que les statistiques sont cumulatives depuis la création du personnage  
- **Clarification importante** : Le Herald d'Eden ne fournit pas de stats par saison, uniquement le total global  
- **Multilingue** : Disponible en FR/EN/DE

### Contenu du message
- 📊 Données globales depuis la création du personnage  
- 🚫 Pas de réinitialisation par saison  
- 📖 Historique complet de toutes les actions  
- 🌐 Explication de la source des données (Herald Eden)

---

## 🔄 Bouton "Actualiser les stats"

### Fonctionnalités
- Récupère RvR, PvP, PvE et Wealth depuis Herald  
- Gestion des mises à jour partielles  
- Messages d'erreur détaillés par catégorie  
- Désactivé automatiquement pendant :
  - Validation Herald au démarrage  
  - Scraping Herald en cours  
  - Récupération des statistiques  

### État du Bouton
- ⏳ **Grisé au démarrage** : Validation Herald en cours  
- ✅ **Activé** : Herald accessible et URL configurée  
- 🔄 **"⏳ Récupération..."** : Pendant le scraping  
- ✅ **Réactivé** : Après succès ou erreur  

---

## 🎨 Améliorations Interface

### Disposition 50/50

**Layout Principal** :
- ⚔️ **RvR (50%)** et 🗡️ **PvP (50%)** côte à côte  
- 🐉 **PvE (50%)** et 💰 **Monnaies (50%)** côte à côte  
- 🏆 **Réalisations** : Pleine largeur, 2 colonnes de 8
- Largeur minimale : 250px par section  
- Répartition équitable de l'espace

**Résultat Visuel** :
```
┌─────────────────────────────────────┐
│     RvR (50%)    │    PvP (50%)     │
├─────────────────────────────────────┤
│     PvE (50%)    │  Monnaies (50%)  │
├─────────────────────────────────────┤
│    Réalisations (100% - 2 colonnes) │
└─────────────────────────────────────┘
```

### Alignement PvP avec QGridLayout

**Avant** : Labels et valeurs mal alignés  

**Maintenant** : QGridLayout pour alignement parfait
```
⚔️ Solo Kills:     1,234    → Alb: 456 | Hib: 123 | Mid: 655
💀 Deathblows:     5,678    → Alb: 2,100 | Hib: 890 | Mid: 2,688
🎯 Kills:          9,999    → Alb: 3,500 | Hib: 1,200 | Mid: 5,299
```

### Détails Royaume sur la Même Ligne

**Avant** : Détails en dessous (2 lignes par stat)
```
Solo Kills: 1,234
  → Alb: 456 | Hib: 123 | Mid: 655
```

**Maintenant** : Tout sur 1 ligne (plus compact)
```
Solo Kills: 1,234    → Alb: 456 | Hib: 123 | Mid: 655
```

### Section PvE Améliorée

**Améliorations** :
- Espacement réduit (5px au lieu de 8px)
- Séparateur vertical entre les 2 colonnes
- Suppression des ":" doublés dans les labels
- Nombres plus proches des titres

**Résultat** :
```
🐉 Dragon Kills: 9       | 👹 Legion Kills: 5
🐲 Mini Dragon: 38       | ⚔️ Epic Encounters: 3
🏛️ Epic Dungeons: 2      | 🐊 Sobekite: 1
```

### Nouvelle Section Réalisations (Achievements)

**Emplacement** : Pleine largeur sous PvE/Monnaies

**Traductions** :
- FR : 🏆 Réalisations
- EN : 🏆 Achievements
- DE : 🏆 Errungenschaften

**Fonctionnalités** :
- ✅ Scraping automatique depuis Herald (`&t=achievements`)
- ✅ Affichage en 2 colonnes de 8 achievements
- ✅ Séparateur vertical entre les colonnes
- ✅ QGridLayout pour alignement parfait (3 colonnes)
- ✅ QScrollArea avec hauteur max 200px
- ✅ Scrollbar verticale seulement si nécessaire

**Format d'Affichage** :
```
Titre Achievement    Progression    (Tier actuel)
Dragon Kills         19 / 50        (Dragon Foe)
Legion Kills         5 / 10         (Demon Killer)
Total Kills          4.71 / 5 K     (Master Soldier)
```

**Disposition** :
```
┌─────────────────────────────┬─│─┬─────────────────────────────┐
│ Colonne 1 (8 achievements)  │ │ │ Colonne 2 (8 suivants)      │
│ Dragon Kills   19/50  (...)  │ │ │ Loyalty        36/50  (...)  │
│ Legion Kills   5/10   (...)  │ │ │ Relics         32/50  (...)  │
│ ...                         │ │ │ ...                         │
└─────────────────────────────┴─│─┴─────────────────────────────┘
```

**Optimisations** :
- Espacement vertical réduit (2px) pour compacité
- Tier actuel en gris italique entre parenthèses
- Scrollbar horizontale désactivée
- Récupération automatique lors de "Actualiser Stats"

---

## 🐛 Corrections

### Fix Fichiers Debug HTML

**Problème** : Deux fichiers HTML créés automatiquement à la racine :
- `debug_herald_after_cookies.html`
- `debug_wealth_page.html`

**Cause** : Code de débogage actif en production

**Solution** :
- ✅ Suppression des 3 sections de création de fichiers
- ✅ Ajout au .gitignore
- ✅ Nettoyage des fichiers existants
- ✅ Logs conservés pour le débogage

### Organisation Statistiques
**3 sous-sections claires** :
- ⚔️ **RvR** : Tower/Keep/Relic Captures  
- 🗡️ **PvP** : Solo Kills, Deathblows, Kills (avec détails royaume)  
- 🐉 **PvE** : Dragons, Légions, Epic content  

### Affichage
- Fiche personnage redimensionnable  
- Layout 50/50 (Informations / Statistiques)  
- Valeurs totales en gras  
- Détails royaume indentés avec couleurs  
- Monnaie en 9pt gras  

---

## � Corrections

### Fix Bouton "Actualiser Stats" Toujours Actif
**Problème** : Bouton restait actif pendant :
- Validation Herald au démarrage  
- Scraping Herald (dialogue de validation)  
- Multiples points de sortie réactivaient le bouton  

**Solution** :
- Flag `herald_scraping_in_progress` pour suivre l'état  
- Vérification validation Herald terminée avant activation  
- Bloc `try/finally` garantissant réactivation en toutes circonstances  
- Signal de fin de validation pour réactivation automatique  

### Fix Messages d'Erreur Incomplets
**Avant** : Seuls RvR et PvP affichés en cas d'erreur  
**Maintenant** : Affichage de TOUTES les erreurs (RvR/PvP/PvE/Wealth)

### Fix Affichage Monnaie
**Avant** : Taille 11pt  
**Maintenant** : Taille 9pt (gras conservé)

### Fix Formatage Monnaie
**Problème** : TypeError avec `f"{money:,}"` sur string "18p 128g"  
**Solution** : Affichage direct `str(money)` sans formatage numérique

### Fix Crash Test Connexion Herald
**Problème** : Application crashait lors d'erreurs de connexion  
**Cause** : Pas de bloc `finally` pour fermer le driver  
**Solution** : Pattern identique au fix de `search_herald_character()`

---

## 🔧 Améliorations Techniques

### Scraping Herald
- Nouveau module `character_profile_scraper.py`  
- 4 fonctions de scraping : RvR, PvP, PvE, Wealth  
- Gestion des séparateurs de milliers  
- Extraction par royaume (Alb/Hib/Mid)  
- Gestion d'erreurs robuste avec messages détaillés  

### Gestion État Boutons
- Flag `herald_scraping_in_progress`  
- Connexion aux signaux de validation  
- `processEvents()` pour mise à jour visuelle immédiate  
- Protection contre réactivation prématurée  

---

## 📦 Scripts de Test

```bash
python Scripts/test_pvp_stats.py      # Test PvP isolé
python Scripts/test_rvr_captures.py   # Test RvR isolé
python Scripts/test_herald_connection_stability.py  # Test stabilité (25 tests)
```

---

## ⚠️ Prérequis

- Cookies Herald valides  
- Personnage niveau 11+ (pour stats PvP)  
- URL Herald configurée dans la fiche personnage  

---

## 🌐 Support Multilingue

- 🇫🇷 Français  
- 🇬🇧 Anglais  
- 🇩🇪 Allemand
