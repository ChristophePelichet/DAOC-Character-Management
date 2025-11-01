# Guide d'utilisation - Système de Gestion des Armures

## Introduction

Le système de gestion des armures vous permet de conserver et d'organiser tous vos fichiers relatifs aux armures de vos personnages. Que vous utilisiez des logiciels externes pour créer des configurations d'armure, des captures d'écran, ou des documents, tout peut être centralisé ici.

## 📁 Accéder à la gestion des armures

1. **Ouvrir la fiche d'un personnage**
   - Dans la liste principale, double-cliquez sur un personnage
   - Ou sélectionnez un personnage et cliquez sur "Ouvrir la fiche"

2. **Localiser la section Armure**
   - Dans la fiche du personnage, cherchez la section "Armure" (à droite de "Informations générales")
   - Cliquez sur le bouton **"📁 Gérer les armures"**

3. **La fenêtre de gestion s'ouvre**
   - Vous voyez maintenant tous les fichiers d'armure pour ce personnage
   - Un tableau affiche : nom du fichier, taille, date de modification, et actions

## 📤 Uploader un fichier d'armure

### Étape par étape

1. **Cliquer sur "📤 Uploader un fichier"**
   - Un explorateur de fichiers s'ouvre

2. **Sélectionner votre fichier**
   - Tous les formats sont acceptés : PNG, JPG, PDF, TXT, XLSX, etc.
   - Vous pouvez uploader des captures d'écran, des configurations, des notes...

3. **Validation**
   - Le fichier est automatiquement copié dans le dossier du personnage
   - Un message de succès confirme l'upload
   - Le fichier apparaît dans la liste

### Gestion automatique des doublons

Si vous uploadez un fichier avec le même nom :
- Le système ajoute automatiquement un suffixe : `_1`, `_2`, etc.
- Exemple : `armor_setup.png` devient `armor_setup_1.png`
- Vos fichiers originaux ne sont jamais écrasés

## 🔍 Visualiser une armure

1. **Dans la liste des armures**
   - Trouvez le fichier que vous souhaitez ouvrir

2. **Cliquer sur "🔍 Ouvrir"**
   - Le fichier s'ouvre automatiquement avec l'application par défaut
   - Images : visionneuse d'images
   - PDF : lecteur PDF
   - Texte : éditeur de texte

## 🗑️ Supprimer une armure

1. **Sélectionner le fichier à supprimer**
   - Cliquer sur "🗑️ Supprimer" pour le fichier souhaité

2. **Confirmer la suppression**
   - Une boîte de dialogue demande confirmation
   - Cliquez sur "Oui" pour confirmer

3. **Fichier supprimé**
   - Le fichier est définitivement supprimé
   - La liste se rafraîchit automatiquement

⚠️ **Attention** : La suppression est définitive et ne peut pas être annulée.

## 🔄 Actualiser la liste

- Cliquez sur "🔄 Actualiser" pour recharger la liste
- Utile si vous avez ajouté des fichiers manuellement dans le dossier

## ⚙️ Configuration du dossier d'armures

### Changer l'emplacement du dossier

1. **Ouvrir la configuration**
   - Menu "Paramètres" > "Configuration"

2. **Section "Chemins des dossiers"**
   - Cherchez le champ "Dossier des armures"

3. **Modifier le chemin**
   - Tapez directement le chemin
   - Ou cliquez sur "Parcourir" pour sélectionner un dossier

4. **Sauvegarder**
   - Cliquez sur "Enregistrer"
   - Le nouveau chemin est immédiatement appliqué

### Chemin par défaut

Si vous ne spécifiez pas de chemin, le système utilise :
```
<répertoire_de_l'application>/Armures/
```

### Organisation automatique

Le système crée automatiquement :
```
Armures/
  ├── character_id_1/
  │   └── vos_fichiers_ici
  ├── character_id_2/
  │   └── vos_fichiers_ici
  └── ...
```

Chaque personnage a son propre sous-dossier identifié par son ID unique.

## 💡 Cas d'usage recommandés

### 1. Captures d'écran d'armure
- Faites une capture d'écran de votre personnage équipé
- Uploadez l'image (PNG, JPG)
- Accès rapide pour comparer différentes configurations

### 2. Configurations de template
- Créez des configurations d'armure avec des logiciels externes
- Uploadez les fichiers (PDF, XLSX, TXT)
- Gardez une trace de vos meilleures configurations

### 3. Notes et stratégies
- Écrivez des notes sur les résistances optimales
- Uploadez des documents texte ou Word
- Consultez-les directement depuis l'application

### 4. Builds théoriques
- Planifiez des builds d'armure
- Uploadez des feuilles de calcul
- Comparez facilement plusieurs options

## 📊 Informations affichées

Pour chaque fichier, vous voyez :

| Colonne | Description | Exemple |
|---------|-------------|---------|
| **Nom du fichier** | Nom complet avec extension | `armor_setup_pvp.png` |
| **Taille** | Taille du fichier | `1.25 MB` ou `456.78 KB` |
| **Date de modification** | Dernière modification | `15/12/2024 14:30` |
| **Actions** | Boutons Ouvrir/Supprimer | 🔍 🗑️ |

## ❓ Questions fréquentes

### Q1 : Quels formats de fichiers sont supportés ?
**R :** Tous les formats ! PNG, JPG, PDF, TXT, DOCX, XLSX, et tout autre format.

### Q2 : Puis-je ajouter des fichiers manuellement dans le dossier ?
**R :** Oui ! Vous pouvez copier des fichiers directement dans `Armures/character_id/`. Cliquez sur "🔄 Actualiser" pour les voir dans l'application.

### Q3 : Que se passe-t-il si je change le chemin du dossier ?
**R :** L'application utilisera le nouveau chemin. Les anciens fichiers restent à leur emplacement original. Vous pouvez les déplacer manuellement si nécessaire.

### Q4 : Les fichiers sont-ils copiés ou déplacés ?
**R :** **Copiés**. Vos fichiers originaux ne sont jamais déplacés ou modifiés.

### Q5 : Puis-je partager mes armures avec d'autres personnages ?
**R :** Actuellement, chaque personnage a son propre dossier. Vous pouvez copier manuellement des fichiers entre les dossiers de personnages.

### Q6 : Y a-t-il une limite de taille pour les fichiers ?
**R :** Non, aucune limite technique. Cependant, les très gros fichiers peuvent ralentir l'affichage.

### Q7 : Puis-je renommer un fichier ?
**R :** Actuellement, le renommage n'est pas supporté dans l'interface. Vous pouvez renommer manuellement dans le dossier, puis actualiser la liste.

## 🚀 Astuces et bonnes pratiques

### Nommage des fichiers
- Utilisez des noms descriptifs : `pve_armor_heal.png`, `pvp_setup_mage.pdf`
- Incluez la date si pertinent : `armor_2024-12-15.png`
- Évitez les caractères spéciaux (é, à, ç) pour une meilleure compatibilité

### Organisation
- Créez plusieurs fichiers pour différentes configurations (PvE, PvP, RvR)
- Gardez un fichier "notes.txt" avec vos réflexions
- Supprimez les anciennes configurations obsolètes

### Sauvegarde
- Le dossier d'armures peut être sauvegardé comme n'importe quel dossier
- Copiez-le régulièrement sur un disque externe ou cloud
- En cas de réinstallation, restaurez simplement le dossier

### Performance
- Si vous avez beaucoup de fichiers lourds, envisagez de les compresser
- Les images peuvent être réduites en résolution sans perte de lisibilité
- Supprimez les fichiers que vous n'utilisez plus

## 🛠️ Dépannage

### Problème : "Impossible d'ouvrir le fichier"
- **Solution** : Vérifiez qu'une application par défaut est configurée pour ce type de fichier dans Windows.

### Problème : "Impossible d'uploader le fichier"
- **Solution** : Vérifiez que vous avez les permissions d'écriture dans le dossier d'armures.

### Problème : "La liste est vide mais j'ai des fichiers"
- **Solution** : Cliquez sur "🔄 Actualiser". Vérifiez que les fichiers sont bien dans le bon sous-dossier (character_id).

### Problème : "Le dossier n'existe pas"
- **Solution** : L'application crée automatiquement le dossier. Si le problème persiste, vérifiez les permissions et le chemin dans la configuration.

## 📞 Support

Pour toute question ou problème :
1. Consultez la documentation complète : `Documentation/ARMOR_MANAGEMENT_FR.md`
2. Vérifiez les logs : Menu "Aide" > "Logs"
3. Créez une issue sur le dépôt GitHub du projet

---

**Version du guide** : 0.105  
**Dernière mise à jour** : Décembre 2024
