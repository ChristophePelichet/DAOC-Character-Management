# ❌ Supprimer un Personnage

## ✏️ Résumé
Apprenez à supprimer un ou plusieurs personnages de manière sécurisée, avec confirmation et possibilité de suppression en masse.

## ✅ Objectif
À la fin de ce guide, vous saurez :
- Supprimer un personnage unique
- Supprimer plusieurs personnages en une fois (suppression en masse)
- Comprendre les confirmations de sécurité
- Récupérer un personnage supprimé (si possible)

---

## ✏️ Étapes Détaillées

### Étape 1 : Supprimer un Personnage Unique

Il existe **3 méthodes** pour supprimer un personnage :

#### Méthode 1 : Menu contextuel (Clic droit)
1. **Clic droit** sur le personnage dans la liste
2. Sélectionnez **Supprimer** dans le menu contextuel
3. Confirmez la suppression dans la boîte de dialogue

#### Méthode 2 : Touche Suppr
1. Cliquez une fois sur le personnage pour le sélectionner
2. Appuyez sur la touche **Suppr** (ou **Delete**)
3. Confirmez la suppression

#### Méthode 3 : Menu Fichier
1. Sélectionnez le personnage dans la liste
2. Menu **Fichier** → **Supprimer le personnage**
3. Confirmez la suppression

> ⚠️ **Attention** : La suppression est définitive ! Le fichier JSON sera supprimé du disque.

---

### Étape 2 : Confirmation de Suppression

Avant de supprimer, une fenêtre de confirmation s'affiche :

#### 2.1 Message de Confirmation
Le message affiche :
- Le **nom du personnage** à supprimer
- Le **royaume** du personnage
- La **classe** et la **race**
- Le **niveau** actuel
- L'**emplacement du fichier** sur le disque

#### 2.2 Choix Disponibles
Vous avez deux options :

**Oui / Confirmer**
- Le personnage sera supprimé définitivement
- Le fichier JSON sera supprimé du dossier `Characters/`
- Le personnage disparaîtra de la liste

**Non / Annuler**
- Aucune suppression ne sera effectuée
- Le personnage reste intact
- Vous revenez à la liste principale

> 💡 **Astuce** : Lisez bien le message de confirmation pour éviter de supprimer le mauvais personnage !

---

### Étape 3 : Suppression en Masse (Plusieurs Personnages)

Pour supprimer plusieurs personnages à la fois :

#### 3.1 Sélection Multiple
**Sélection continue** :
1. Cliquez sur le premier personnage
2. Maintenez **Shift** (Maj)
3. Cliquez sur le dernier personnage
4. Tous les personnages entre les deux sont sélectionnés

**Sélection discontinue** :
1. Cliquez sur le premier personnage
2. Maintenez **Ctrl**
3. Cliquez sur chaque personnage à supprimer
4. Seuls les personnages cliqués sont sélectionnés

#### 3.2 Lancer la Suppression en Masse
1. Une fois vos personnages sélectionnés
2. Appuyez sur **Suppr** ou **Clic droit** → **Supprimer**
3. Une confirmation globale s'affiche
4. Le message indique **le nombre de personnages** à supprimer

#### 3.3 Confirmation pour Suppression Multiple
Le message de confirmation affiche :
```
Êtes-vous sûr de vouloir supprimer 5 personnages ?

Cette action est irréversible.
```

- Cliquez sur **Oui** pour supprimer tous les personnages sélectionnés
- Cliquez sur **Non** pour annuler et ne rien supprimer

> ⚠️ **Attention** : Tous les personnages sélectionnés seront supprimés en une seule fois !

---

### Étape 4 : Après la Suppression

#### 4.1 Mise à Jour de la Liste
- Le ou les personnages disparaissent immédiatement de la liste
- Le compteur en bas de l'écran est mis à jour
- La sélection est effacée

#### 4.2 Fichiers Supprimés
Les fichiers suivants sont supprimés du disque :
- `Characters/[Saison]/[Royaume]/[NomPersonnage].json`
- Tous les fichiers associés (si présents)

#### 4.3 Message de Confirmation
Un message peut s'afficher pour confirmer :
```
✅ Personnage "NomDuPersonnage" supprimé avec succès
```
ou
```
✅ 5 personnages supprimés avec succès
```

---

## ⚡ Raccourcis Clavier

| Raccourci | Action |
|-----------|--------|
| **Suppr** | Supprimer le(s) personnage(s) sélectionné(s) |
| **Shift + Clic** | Sélection continue (plage) |
| **Ctrl + Clic** | Sélection discontinue (individuelle) |
| **Ctrl + A** | Tout sélectionner |
| **Échap** | Annuler la confirmation |

---

## ❌ Erreurs Courantes

### Erreur 1 : "Impossible de supprimer le personnage"
**Cause** : Le fichier JSON est en lecture seule ou verrouillé.

**Solution** :
1. Vérifiez que le fichier n'est pas ouvert dans un autre programme
2. Vérifiez les permissions du dossier `Characters/`
3. Fermez tous les éditeurs de texte ou explorateurs de fichiers
4. Redémarrez l'application

### Erreur 2 : "Le fichier n'existe plus"
**Cause** : Le fichier a été supprimé manuellement en dehors de l'application.

**Solution** :
1. Actualisez la liste (F5 ou redémarrage)
2. Le personnage disparaîtra de la liste automatiquement

### Erreur 3 : "Accès refusé"
**Cause** : Vous n'avez pas les permissions pour supprimer le fichier.

**Solution** :
1. Exécutez l'application en tant qu'administrateur
2. Vérifiez les permissions du dossier `Characters/`
3. Vérifiez que le fichier n'est pas protégé en écriture

---

## ℹ️ Astuces et Conseils

### 📋 Sauvegarde Avant Suppression
Avant de supprimer des personnages importants :
1. Faites une **sauvegarde** du dossier `Characters/`
2. Ou exportez les personnages (Menu **Fichier** → **Exporter**)
3. Vous pourrez les restaurer en cas d'erreur

### ✏️ Nettoyage de Personnages Obsolètes
Pour nettoyer les anciens personnages :
1. Triez par **Saison** pour voir les anciens personnages
2. Triez par **Niveau** pour supprimer les personnages bas niveau
3. Utilisez la **sélection multiple** pour supprimer en masse

### ⬇️ Alternative à la Suppression
Si vous n'êtes pas sûr de vouloir supprimer :
- **Exportez** le personnage avant de supprimer
- Changez la **Saison** pour archiver (S1 → Archive)
- Gardez une copie du fichier JSON dans un autre dossier

### ➕ Récupération Accidentelle
Si vous supprimez un personnage par erreur :
1. Vérifiez la **Corbeille Windows** immédiatement
2. Le fichier JSON peut être restauré depuis la corbeille
3. Remettez-le dans `Characters/[Saison]/[Royaume]/`
4. Redémarrez l'application pour le voir réapparaître

> ⚠️ **Important** : Une fois la corbeille vidée, le personnage est perdu définitivement !

---

## ➡️ Voir Aussi

- ✏️ [Créer un personnage manuellement](character_create.md)
- ✏️ [Modifier un personnage](character_edit.md)
- 📥 [Importer depuis Eden Herald](character_import.md)
- 📤 [Exporter des personnages](character_export.md)
- 🔄 [Dupliquer un personnage](character_duplicate.md)

---

## ❓ Besoin d'Aide ?

Si vous rencontrez un problème non couvert par ce guide :
1. Consultez la section [Dépannage](troubleshooting.md)
2. Vérifiez les logs de debug (Menu **Aide** → **Debug Eden**)
3. Vérifiez que vous avez les permissions nécessaires sur le dossier
4. Contactez le support avec vos logs

---

**Dernière mise à jour** : 30 octobre 2025  
**Version de la documentation** : 1.0
