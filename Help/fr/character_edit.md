# ✏️ Modifier un Personnage

## ✏️ Résumé
Apprenez à modifier les informations d'un personnage existant : niveau, guilde, rangs de royaume, armures et toutes les autres données.

## ✅ Objectif
À la fin de ce guide, vous saurez :
- Ouvrir la fiche d'un personnage pour modification
- Modifier les informations de base (niveau, guilde, serveur)
- Gérer les rangs de royaume
- Configurer les sets d'armures
- Sauvegarder les modifications

---

## ✏️ Étapes Détaillées

### Étape 1 : Ouvrir la Fiche du Personnage

Il existe **3 méthodes** pour ouvrir un personnage en modification :

#### Méthode 1 : Double-clic
1. Trouvez le personnage dans la liste principale
2. **Double-cliquez** sur le personnage

#### Méthode 2 : Menu contextuel (Clic droit)
1. **Clic droit** sur le personnage dans la liste
2. Sélectionnez **Modifier** dans le menu contextuel

#### Méthode 3 : Sélection + Menu Fichier
1. Cliquez une fois sur le personnage pour le sélectionner
2. Menu **Fichier** → **Modifier le personnage**

> ℹ️ **Note** : Le double-clic est la méthode la plus rapide !

---

### Étape 2 : Modifier les Informations de Base

La fenêtre de modification s'ouvre avec plusieurs onglets :

#### 2.1 Informations Générales

**Nom** 🔒
- Le nom du personnage **ne peut pas être modifié directement**
- Pour renommer : Clic droit → **Renommer** (ou F2)
- ⚠️ Le renommage déplace aussi le fichier JSON

**Niveau** (1-50)
- Mettez à jour le niveau actuel de votre personnage
- Exemple : Passez de 20 à 35 après une session de jeu

**Guilde**
- Nom de la guilde actuelle
- Laissez vide si le personnage n'a pas de guilde
- Exemple : `Les Gardiens`, `The Brotherhood`

**Serveur**
- Serveur de jeu : Eden, Blackthorn, etc.
- Utile si vous jouez sur plusieurs serveurs

**Saison**
- Saison actuelle : S1, S2, S3...
- Pour organiser vos personnages par période

**Page** (1-5)
- Numéro de page dans le jeu DAOC
- Utile pour retrouver vos personnages en jeu

---

### Étape 3 : Gérer les Rangs de Royaume

Les rangs de royaume (Realm Ranks) sont un système de progression PvP.

#### 3.1 Sélectionner le Rang
1. Trouvez la section **Rangs de Royaume**
2. Sélectionnez le rang actuel dans la liste déroulante
3. Exemples de rangs :
   - **Albion** : Guardian, Crusader, Hero, Legend...
   - **Hibernia** : Savant, Warden, Defender, Champion...
   - **Midgard** : Thunderer, Stormcaller, Battlemaster...

#### 3.2 Rang Personnalisé
Si votre rang n'est pas dans la liste :
1. Cochez **Titre personnalisé**
2. Entrez votre titre dans le champ texte
3. Utile pour les rangs très élevés ou spéciaux

> ℹ️ **Note** : Les rangs de royaume dépendent du royaume du personnage (Albion, Hibernia, Midgard).

---

### Étape 4 : Configurer les Sets d'Armures (Optionnel)

Vous pouvez créer plusieurs sets d'armures avec leurs résistances.

#### 4.1 Créer un Set d'Armure
1. Cliquez sur le bouton **Ajouter un Set**
2. Donnez un nom au set : `PvP`, `PvE`, `Farming`, etc.
3. Le set apparaît dans la liste

#### 4.2 Configurer les Résistances
Pour chaque set d'armure, configurez les résistances :

**Résistances Élémentaires**
- ❄️ **Froid** (Crush) : 0-26%
- 🔥 **Chaleur** (Heat) : 0-26%
- ⚡ **Énergie** (Energy) : 0-26%
- 🌿 **Matière** (Matter) : 0-26%
- 🌙 **Esprit** (Spirit) : 0-26%
- 💀 **Corps** (Body) : 0-26%

**Résistances Physiques**
- 🗡️ **Tranchant** (Slash) : 0-26%
- 🔨 **Contondant** (Crush) : 0-26%
- 🗡️ **Perforant** (Thrust) : 0-26%

> ℹ️ **Note** : La limite maximale est 26% par résistance (sans buffs).

#### 4.3 Dupliquer un Set
Pour créer un set similaire :
1. Sélectionnez le set à copier
2. Cliquez sur **Dupliquer le Set**
3. Modifiez les valeurs selon vos besoins

#### 4.4 Supprimer un Set
1. Sélectionnez le set à supprimer
2. Cliquez sur **Supprimer le Set**
3. Confirmez la suppression

---

### Étape 5 : Sauvegarder les Modifications

#### 5.1 Valider les Changements
- Cliquez sur le bouton **OK** ou **Enregistrer**
- Ou appuyez sur **Entrée**

#### 5.2 Annuler les Modifications
Si vous ne voulez pas sauvegarder :
- Cliquez sur **Annuler**
- Ou appuyez sur **Échap**
- Toutes les modifications seront perdues

#### 5.3 Confirmation
- Les modifications sont enregistrées dans le fichier JSON
- La liste principale se met à jour automatiquement
- Un message de confirmation peut s'afficher

---

## ⚡ Raccourcis Clavier

| Raccourci | Action |
|-----------|--------|
| **Double-clic** | Ouvrir en modification |
| **F2** | Renommer le personnage |
| **Tab** | Passer au champ suivant |
| **Shift+Tab** | Revenir au champ précédent |
| **Entrée** | Valider les modifications |
| **Échap** | Annuler |

---

## ❌ Erreurs Courantes

### Erreur 1 : "Impossible de sauvegarder les modifications"
**Cause** : Le fichier JSON est en lecture seule ou verrouillé.

**Solution** :
1. Vérifiez que le fichier n'est pas ouvert dans un autre programme
2. Vérifiez les permissions du dossier `Characters/`
3. Redémarrez l'application

### Erreur 2 : "Résistance invalide"
**Cause** : Vous avez entré une valeur hors limites (< 0 ou > 26).

**Solution** :
1. Les résistances doivent être entre 0 et 26%
2. Utilisez les flèches ou tapez une valeur valide

### Erreur 3 : "Le personnage n'a pas pu être rechargé"
**Cause** : Le fichier JSON a été modifié manuellement et est corrompu.

**Solution** :
1. Consultez les logs : Menu **Aide** → **Debug Eden**
2. Vérifiez le fichier JSON dans `Characters/[Saison]/[Royaume]/`
3. Restaurez depuis une sauvegarde si nécessaire

---

## ℹ️ Astuces et Conseils

### ✏️ Mises à Jour Régulières
- Mettez à jour le niveau après chaque session de jeu
- Gardez les rangs de royaume à jour pour suivre votre progression PvP
- Mettez à jour la guilde si vous changez

### 📋 Organisation des Sets d'Armures
Créez des sets pour différentes situations :
- **PvP** : Résistances optimisées pour le RvR
- **PvE** : Résistances pour le farming et les donjons
- **Solo** : Set équilibré pour jouer seul
- **Groupe** : Set spécialisé pour le groupe

### ⬇️ Modification Rapide
Pour modifier plusieurs personnages rapidement :
1. Triez la liste par royaume ou niveau
2. Modifiez les personnages un par un
3. Utilisez **Entrée** pour valider rapidement

### ➕ Compléter Progressivement
Pas besoin de tout remplir immédiatement :
- Commencez par les infos de base (niveau, guilde)
- Ajoutez les rangs de royaume quand vous progressez
- Configurez les armures quand vous avez le temps

---

## ➡️ Voir Aussi

- ✏️ [Créer un personnage manuellement](character_create.md)
- ❌ [Supprimer un personnage](character_delete.md)
- 🏰 [Comprendre les rangs de royaume](realm_ranks.md)
- 🛡️ [Gérer les armures et résistances](armor_management.md)
- 📥 [Importer depuis Eden Herald](character_import.md)

---

## ❓ Besoin d'Aide ?

Si vous rencontrez un problème non couvert par ce guide :
1. Consultez la section [Dépannage](troubleshooting.md)
2. Vérifiez les logs de debug (Menu **Aide** → **Debug Eden**)
3. Contactez le support avec vos logs

---

**Dernière mise à jour** : 30 octobre 2025  
**Version de la documentation** : 1.0
