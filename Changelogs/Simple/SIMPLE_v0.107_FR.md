# v0.107 - Statistiques RvR/PvP Herald# v0.107 - Statistiques RvR/PvP Herald# v0.107 - Correction Crash Test Connexion Herald



## 📊 Nouvelles Statistiques Herald (8 nov 2025)



### ⚔️ Section RvR## 🎯 Résumé (8 nov 2025)##
✅ 🗼 Tower Captures : Nombre de tours capturées  
✅ 🏰 Keep Captures : Nombre de forteresses capturées 
✅ 💎 Relic Captures : Nombre de reliques capturées  



### 🗡️ Section PvP avec Répartition par Royaume
✅ ⚔️ Solo Kills : Total + détail Alb/Hib/Mid
✅ 💀 Deathblows : Total + détail Alb/Hib/Mid  
✅ 🎯 Kills : Total + détail Alb/Hib/Mid  
✅ Couleurs par royaume (Rouge/Vert/Bleu)  
✅ Affichage : `Kills: 4,715 → Alb: 1,811 | Hib: 34 | Mid: 2,870`


### 🔄 Bouton "Actualiser les stats"## ✨ Nouvelles Fonctionnalités✅ Plus de crash de l'application lors d'erreurs de connexion  

✅ Récupère RvR et PvP depuis le Herald  

✅ Gestion des mises à jour partielles  

✅ Messages explicatifs en cas d'erreur  

✅ Support multilingue (FR/EN/DE)  ### 📊 Section Statistiques Réorganisée## 🧪 Script de Test Ajouté



## 🔧 Améliorations Techniques✅ **Nouveau script** : `test_herald_connection_stability.py`  



### 📥 Scraper Herald**3 sous-sections** :✅ Teste la stabilité de la connexion Herald (25 tests par défaut)  

✅ Nouveau module `character_profile_scraper.py`  

✅ Scraping onglets Characters et PvP du Herald  - ⚔️ **RvR** : Tower Captures, Keep Captures, Relic Captures✅ Statistiques détaillées : temps moyen/min/max, taux de succès  

✅ Gestion séparateurs de milliers (espaces, virgules)  

✅ Extraction par royaume (Albion/Hibernia/Midgard)  - 🗡️ **PvP** : Solo Kills, Deathblows, Kills (avec détails par royaume)✅ Détection de crashs et erreurs  



### 🐛 Corrections- 🐉 **PvE** : Section préparée (à venir)✅ Nombre de tests personnalisable  

✅ **Fix parsing nombres** : `"1 811"` → fonction `clean_number()` supprime espaces/virgules  

✅ **Fix stats manquantes** : Messages précis, sauvegarde partielle, HTML debug  

✅ **Personnages sans stats** : Messages informatifs au lieu d'erreurs  

### 🔍 Statistiques RvR## Détails Techniques

### 🎨 Interface

✅ Fiche personnage redimensionnable  - 🗼 Tower Captures- **Problème** : Le test de connexion Herald pouvait crasher l'application comme la recherche

✅ Section Statistiques organisée : RvR / PvP / PvE  

✅ Valeurs totales en gras  - 🏰 Keep Captures  - **Cause** : Pas de bloc `finally` pour fermer le driver, appels `close()` manquants dans certains chemins d'erreur

✅ Détails royaume indentés avec couleurs  

✅ Layout 50/50 (Informations/Statistiques)  - 💎 Relic Captures- **Solution** : Pattern identique au fix de `search_herald_character()`

✅ Traductions complètes (FR/EN/DE)  

- **Impact** : Application stable, pas de crash lors des tests de connexion

## 📦 Scripts de Test

✅ `Scripts/test_pvp_stats.py` : Test scraping PvP isolé  ### ⚔️ Statistiques PvP avec Répartition par Royaume

✅ `Scripts/test_rvr_captures.py` : Test scraping RvR isolé  - **Solo Kills** : Kills en 1v1

- **Deathblows** : Coups de grâce

## ⚠️ Notes- **Kills** : Total

- Nécessite cookies Herald valides  

- Personnage niveau 11+ recommandé  **Affichage détaillé** :

- Navigateur visible minimisé (headless=False)```

🎯 Kills: 4,715
   → Alb: 1,811  |  Hib: 34  |  Mid: 2,870
```

**Couleurs par royaume** :
- Alb (Rouge #C41E3A)
- Hib (Vert #228B22)
- Mid (Bleu #4169E1)

### 🔄 Bouton "Actualiser les stats"
- Récupère RvR et PvP depuis le Herald
- Gestion des mises à jour partielles
- Messages explicatifs en cas d'erreur

### 🌐 Support Multilingue
- 🇫🇷 Français
- 🇬🇧 Anglais  
- 🇩🇪 Allemand

---

## 🔧 Améliorations

### Scraping Herald
- Nouveau module `character_profile_scraper.py`
- Gestion des séparateurs de milliers (espaces, virgules)
- Extraction par royaume (Alb/Hib/Mid)
- Gestion d'erreurs robuste

### Interface
- Fiche personnage redimensionnable
- Sections organisées avec icônes
- Valeurs totales en gras
- Layout 50/50 (Informations/Statistiques)

---

## 🐛 Corrections

### Fix Parsing des Nombres
**Problème** : Erreur sur "1 811" (espaces dans les nombres)  
**Solution** : Fonction `clean_number()` supprimant espaces, virgules et `\xa0`

### Fix Stats Manquantes
**Avant** : Erreur générique  
**Maintenant** : Message précis + sauvegarde des stats disponibles + HTML debug

---

## 📦 Scripts de Test

```bash
python Scripts/test_pvp_stats.py
```

---

## ⚠️ Prérequis

- Cookies Herald valides
- Personnage niveau 11+
- Stats PvP disponibles sur Herald

---

## 🔜 Prochaines Étapes

- Section PvE (Quêtes, Donjons, Crafting)
- Graphiques d'évolution
- Comparaison entre personnages
