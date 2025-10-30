# ✅ Créer un Nouveau Personnage Manuellement

## ✏️ Résumé
Apprenez à créer manuellement un nouveau personnage dans le gestionnaire avec toutes ses informations de base.

## ✅ Objectif
À la fin de ce guide, vous saurez :
- Ouvrir le dialogue de création
- Remplir tous les champs obligatoires
- Choisir le royaume, la classe et la race
- Sauvegarder le personnage

---

## ✏️ Étapes Détaillées

### Étape 1 : Ouvrir le Dialogue de Création

Il existe **3 méthodes** pour créer un nouveau personnage :

#### Méthode 1 : Menu Fichier
1. Cliquez sur le menu **Fichier** en haut de la fenêtre
2. Sélectionnez **Nouveau Personnage**

#### Méthode 2 : Raccourci Clavier
- Appuyez sur **Ctrl+N** (maintenir Ctrl et appuyer sur N)

#### Méthode 3 : Bouton dans l'interface (si disponible)
- Cliquez sur le bouton **+** ou **Nouveau** dans la barre d'outils

> 💡 **Astuce** : Le raccourci **Ctrl+N** est le plus rapide !

---

### Étape 2 : Remplir les Informations Obligatoires

Une fenêtre s'ouvre avec plusieurs champs à remplir :

#### 2.1 Nom du Personnage ⭐ (Obligatoire)
- **Description** : Le nom unique de votre personnage
- **Format** : Lettres uniquement, pas d'espaces ni de caractères spéciaux
- **Longueur** : Maximum 12 caractères
- **Exemple** : `Ewoline`, `Thorgnir`, `Meridiana`

> ⚠️ **Attention** : Le nom doit être unique dans votre liste. Si un personnage avec ce nom existe déjà, vous devrez en choisir un autre.

#### 2.2 Royaume ⭐ (Obligatoire)
- **Albion** 🛡️ : Royaume britannique avec classes basées sur la Table Ronde
- **Hibernia** 🍀 : Royaume celtique avec classes basées sur la mythologie irlandaise
- **Midgard** ⚔️ : Royaume nordique avec classes basées sur la mythologie viking

> 💡 **Astuce** : Vous pourrez changer le royaume plus tard, mais cela déplacera le fichier du personnage.

#### 2.3 Classe ⭐ (Obligatoire)
1. **Sélectionnez d'abord le royaume** (la liste des classes dépend du royaume)
2. Choisissez une classe dans la liste déroulante
3. Exemples par royaume :
   - **Albion** : Paladin, Armsman, Wizard, Cleric, Scout...
   - **Hibernia** : Hero, Champion, Druid, Warden, Ranger...
   - **Midgard** : Warrior, Thane, Runemaster, Healer, Hunter...

> ℹ️ **Note** : La liste des classes est automatiquement filtrée selon le royaume sélectionné.

#### 2.4 Race ⭐ (Obligatoire)
1. **La liste des races dépend de la classe choisie**
2. Exemples :
   - **Albion** : Briton, Avalonian, Highlander, Saracen, etc.
   - **Hibernia** : Celt, Firbolg, Lurikeen, Elf, etc.
   - **Midgard** : Norseman, Troll, Dwarf, Kobold, etc.

> ⚠️ **Important** : Toutes les races ne peuvent pas jouer toutes les classes. La liste est automatiquement filtrée.

---

### Étape 3 : Remplir les Informations Optionnelles

Ces champs peuvent être laissés vides et remplis plus tard :

#### 3.1 Niveau (Optionnel)
- **Valeur par défaut** : 1
- **Plage** : 1 à 50
- **Description** : Le niveau actuel de votre personnage

#### 3.2 Saison (Optionnel)
- **Valeur par défaut** : S1 (Saison 1)
- **Format** : S1, S2, S3, etc.
- **Description** : Pour organiser vos personnages par saison de jeu
- **Utilité** : Permet de séparer les personnages de différentes périodes

#### 3.3 Serveur (Optionnel)
- **Valeur par défaut** : Eden
- **Options** : Eden, Blackthorn, ou autre
- **Description** : Le serveur sur lequel joue le personnage

#### 3.4 Guilde (Optionnel)
- **Description** : Le nom de la guilde du personnage
- **Format** : Texte libre
- **Exemple** : `Les Gardiens`, `The Brotherhood`, `Die Krieger`

#### 3.5 Page (Optionnel)
- **Valeur par défaut** : 1
- **Plage** : 1 à 5
- **Description** : Numéro de page pour organiser vos personnages dans le jeu
- **Utilité** : Si vous organisez vos personnages par "pages" dans DAOC

---

### Étape 4 : Valider et Sauvegarder

#### 4.1 Vérifier les Informations
Avant de valider, assurez-vous que :
- ✅ Le **nom** est correct (impossible de le changer facilement après)
- ✅ Le **royaume** est correct
- ✅ La **classe** est correcte
- ✅ La **race** est correcte

#### 4.2 Cliquer sur "OK" ou "Créer"
- Le bouton est actif uniquement si tous les champs obligatoires sont remplis
- Si le bouton est grisé, vérifiez que vous avez rempli : Nom, Royaume, Classe, Race

#### 4.3 Confirmation
- Un message de succès s'affiche
- Le personnage apparaît dans la liste principale
- Le fichier JSON est créé automatiquement dans : `Characters/[Saison]/[Royaume]/[Nom].json`

---

## ⚡ Raccourcis Clavier

| Raccourci | Action |
|-----------|--------|
| **Ctrl+N** | Ouvrir le dialogue de création |
| **Tab** | Passer au champ suivant |
| **Shift+Tab** | Revenir au champ précédent |
| **Entrée** | Valider (si tous les champs sont remplis) |
| **Échap** | Annuler |

---

## ❌ Erreurs Courantes

### Erreur 1 : "Un personnage nommé 'XXX' existe déjà"
**Cause** : Un personnage avec ce nom existe déjà dans le même royaume et la même saison.

**Solution** :
1. Choisissez un nom différent
2. OU supprimez l'ancien personnage
3. OU changez de saison

### Erreur 2 : "Le nom ne peut pas être vide"
**Cause** : Vous n'avez pas rempli le champ "Nom".

**Solution** : Entrez un nom pour votre personnage.

### Erreur 3 : "Combinaison race/classe invalide"
**Cause** : Vous avez changé le royaume après avoir sélectionné la classe et la race.

**Solution** :
1. Sélectionnez d'abord le **royaume**
2. Puis la **classe**
3. Enfin la **race**

---

## ℹ️ Astuces et Conseils

### ✏️ Convention de Nommage
Pour une meilleure organisation, utilisez une convention cohérente :
- **Par type** : `EwoTank`, `EwoHeal`, `EwoDD` (Tank, Healer, Damage Dealer)
- **Par royaume** : `AlbEwo`, `HibEwo`, `MidEwo`
- **Par niveau** : `Ewo50`, `Ewo20` (selon le niveau)

### 📋 Organisation par Saison
Si vous jouez sur plusieurs saisons :
1. Créez vos personnages de la saison en cours en **S1**
2. Lors d'une nouvelle saison, créez-les en **S2**
3. Cela vous permet de garder l'historique

### ⬇️ Import Automatique
Vous avez beaucoup de personnages à créer ?
- Utilisez **l'import depuis Eden Herald** au lieu de créer manuellement
- Menu : **Fichier** → **Import Herald**
- Voir l'aide : [Importer depuis Eden Herald](character_import.md)

### ➕ Compléter Plus Tard
Pas besoin de tout remplir maintenant :
- Créez le personnage avec les infos minimales (Nom, Royaume, Classe, Race)
- Double-cliquez dessus plus tard pour compléter les détails
- Ajoutez le niveau, la guilde, les rangs de royaume au fur et à mesure

---

## ➡️ Voir Aussi

- ✏️ [Éditer un personnage](character_edit.md)
- 📥 [Importer depuis Eden Herald](character_import.md)
- 🏰 [Comprendre les rangs de royaume](realm_ranks.md)
- 🛡️ [Gérer les armures](armor_management.md)
- ⚙️ [Configurer l'application](settings.md)

---

## ❓ Besoin d'Aide ?

Si vous rencontrez un problème non couvert par ce guide :
1. Consultez la section [Dépannage](troubleshooting.md)
2. Vérifiez les logs de debug (Menu **Aide** → **Debug**)
3. Contactez le support avec vos logs

---

**Dernière mise à jour** : 30 octobre 2025  
**Version de la documentation** : 1.0
