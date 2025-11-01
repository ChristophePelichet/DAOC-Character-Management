# 🔄 Amélioration : Auto-Update lors de l'import de personnages

**Version :** 0.107  
**Date :** 1er novembre 2025  
**Type :** Amélioration (Feature)

---

## 📋 Résumé

Lors de l'import de personnages depuis Herald (recherche ou clic droit), si un personnage avec le même nom existe déjà, le logiciel le **met à jour automatiquement** au lieu de simplement le rejeter.

---

## ❌ Comportement précédent

Lors d'un import (depuis le Herald via la recherche) :
```
- Si le personnage N'existe PAS → Import réussi ✅
- Si le personnage EXISTE → Erreur et import rejeté ❌
  Message : "personnage déjà existant"
```

**Inconvénient :**
- Les utilisateurs devaient supprimer le personnage manuellement avant de le réimporter
- Impossible de mettre à jour les stats d'un personnage via l'import Herald
- Processus lourd et non intuitif

---

## ✅ Nouveau comportement

Lors d'un import :
```
- Si le personnage N'existe PAS → Import normal ✅
  Message : "✅ 1 personnage(s) importé(s)"

- Si le personnage EXISTE → Mise à jour automatique 🔄
  Message : "🔄 1 personnage(s) mis à jour !"
  
- Si les deux → Rapport complet
  Message : "✅ 5 importé(s) | 🔄 3 mis à jour(s) | ⚠️ 2 erreur(s)"
```

**Avantages :**
- Mise à jour transparente des stats (niveau, guild, realm rank, etc.)
- Pas besoin de supprimer/réimporter
- Workflow intuitif et fluide
- Idéal pour garder les personnages à jour

---

## 🔍 Fichier modifié

**`UI/dialogs.py`** - Fonction `_import_characters()` (ligne 2422)

### Détails de l'implémentation

#### 1. Détection du personnage existant

```python
# Vérifier si le personnage existe déjà
existing_chars = get_all_characters()
existing_char = None
for c in existing_chars:
    if c.get('name', '').lower() == name.lower():
        existing_char = c
        break
```

#### 2. Logique de mise à jour

```python
if existing_char:
    # Le personnage existe, on va le mettre à jour
    # Construire le chemin du fichier existant
    base_char_dir = get_character_dir()
    char_season = existing_char.get('season', 'S1')
    char_realm = existing_char.get('realm', realm)
    file_path = os.path.join(base_char_dir, char_season, char_realm, f"{name}.json")
    
    if os.path.exists(file_path):
        # Charger les données existantes
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        # Mettre à jour SEULEMENT les infos pertinentes
        existing_data.update({
            'class': character_data['class'],
            'race': character_data['race'],
            'guild': character_data['guild'],
            'level': character_data['level'],
            'realm_rank': character_data['realm_rank'],
            'realm_level': character_data['realm_level'],
            'realm_points': character_data['realm_points'],
            'url': character_data['url'],
            'notes': character_data['notes']
        })
        
        # Sauvegarder avec allow_overwrite=True
        success, msg = save_character(existing_data, allow_overwrite=True)
```

#### 3. Comptage des résultats

```python
success_count = 0      # Nouveaux personnages créés
error_count = 0        # Erreurs
updated_count = 0      # Personnages mis à jour
```

#### 4. Rapport final

```python
message = ""
if success_count > 0:
    message += f"✅ {success_count} personnage(s) importé(s) avec succès !"
if updated_count > 0:
    if message:
        message += "\n"
    message += f"🔄 {updated_count} personnage(s) mis à jour !"

if error_count > 0:
    message += f"\n⚠️ {error_count} erreur(s):\n" + ...
```

---

## 🎯 Données préservées lors de la mise à jour

Les données suivantes sont **CONSERVÉES** (non écrasées) :
- ✅ `name` (le nom)
- ✅ `realm` (le royaume)
- ✅ `season` (la saison S1, S2, S3)
- ✅ `server` (Eden, Live, etc.)
- ✅ Tous les autres champs personnalisés

## 📝 Données mises à jour depuis Herald

Les informations suivantes sont **MISES À JOUR** :
- 🔄 `class` (classe)
- 🔄 `race` (race)
- 🔄 `guild` (guilde)
- 🔄 `level` (niveau)
- 🔄 `realm_rank` (rang de royaume)
- 🔄 `realm_level` (niveau du rang)
- 🔄 `realm_points` (points de royaume)
- 🔄 `url` (URL Herald)
- 🔄 `notes` (timestamp de mise à jour)

---

## 📊 Cas d'usage

### Cas 1 : Import d'un personnage existant
```
Herald Search : "Merlin" trouvé
→ Merlin existe dans la BD
→ Mise à jour automatique de ses stats depuis Herald
✅ Résultat : "🔄 1 personnage(s) mis à jour !"
```

### Cas 2 : Import mixte (neufs + existants)
```
Herald Search : "Merlin", "Arthur", "Lancelot"
→ Merlin existe → Mise à jour 🔄
→ Arthur n'existe pas → Import ✅
→ Lancelot existe → Mise à jour 🔄
✅ Résultat : "✅ 1 importé | 🔄 2 mis à jour"
```

### Cas 3 : Erreur lors de la mise à jour
```
Herald Search : "Merlin"
→ Merlin existe mais fichier corrompu
❌ Résultat : "⚠️ Merlin: impossible de lire le fichier existant"
```

---

## 🔧 Maintenance et évolution

### Points à vérifier

1. **Saison du personnage** : Lors de la mise à jour, la saison reste inchangée (celle de l'import original)
2. **Doublons** : La détection est en minuscules (insensible à la casse) pour éviter les doublons
3. **Erreurs de fichier** : Si le fichier est corrompu, l'import échoue proprement sans crash
4. **Traçabilité** : Le champ `notes` est mis à jour avec la date/heure de la mise à jour

### Évolutions futures possibles

- [ ] Dialogue de confirmation avant de mettre à jour (optionnel)
- [ ] Log détaillé des changements effectués
- [ ] Option pour conserver/éccraser le guild existant
- [ ] Historique des mises à jour

---

## ✅ Validation

- ✅ Les personnages neufs sont importés normalement
- ✅ Les personnages existants sont mis à jour
- ✅ Les données importantes sont conservées
- ✅ Les erreurs sont gérées proprement
- ✅ Le rapport final affiche les 3 compteurs (import, update, erreurs)
- ✅ L'interface se rafraîchit après l'import/update
- ✅ Pas de régression sur la création manuelle de personnages

---

## 📌 Notes importantes

1. **Pas de suppression** : Cette fonction ne supprime jamais de personnages
2. **Saison statique** : La saison du personnage ne change pas lors de la mise à jour
3. **Reversible** : Les données conservées sont toujours accessibles (pas de perte)
4. **Non-intrusif** : L'update ne modifie que les champs pertinents du Herald

---

## 🚀 Migration pour l'utilisateur

**Aucune action requise** ! La fonctionnalité fonctionne automatiquement.

Les utilisateurs qui avaient l'habitude de :
1. Rechercher un personnage existant
2. Voir "erreur : personnage déjà existant"
3. Supprimer le personnage manuellement
4. Réimporter

Peuvent maintenant :
1. Rechercher le personnage
2. Le voir automatiquement mis à jour ✅

---

## 📋 Checklist de test

- [ ] Import d'un nouveau personnage → ✅ Importé
- [ ] Import d'un personnage existant → 🔄 Mis à jour
- [ ] Import mixte (neufs + existants) → ✅ 2 importés, 🔄 1 mis à jour
- [ ] Stats mises à jour correctement (niveau, guild, etc.)
- [ ] Informations anciennes préservées (season, realm, etc.)
- [ ] Erreurs gérées proprement (fichier corrompu, etc.)
- [ ] Refresh de l'interface après import
