# Configuration des Colonnes Visibles

## 📋 Vue d'ensemble

Cette fonctionnalité vous permet de personnaliser quelles colonnes sont affichées dans la liste principale des personnages. Vous pouvez masquer les colonnes dont vous n'avez pas besoin pour obtenir une vue plus épurée.

## 🎯 Accès à la Configuration

### Via la Barre d'Outils

1. Cliquez sur le bouton **Colonnes** (icône `colonnes.png`) dans la barre d'outils
2. Le bouton se trouve entre le bouton **+** (Nouveau personnage) et l'icône de configuration (roue dentée)

### Interface de Configuration

La fenêtre de configuration affiche :
- ✅ Liste de toutes les colonnes disponibles avec des cases à cocher
- 🔘 Bouton "Tout sélectionner" pour afficher toutes les colonnes
- 🔘 Bouton "Tout désélectionner" pour masquer toutes les colonnes
- ✔️ Bouton "OK" pour sauvegarder les changements
- ✖️ Bouton "Annuler" pour fermer sans sauvegarder

## 📊 Colonnes Disponibles

| Colonne | Clé | Description | Défaut |
|---------|-----|-------------|--------|
| **Sélection** | `selection` | Case à cocher pour les actions en masse | ✅ Visible |
| **Royaume** | `realm` | Icône du royaume (Albion/Hibernia/Midgard) | ✅ Visible |
| **Saison** | `season` | Saison du personnage (S1, S2, S3, etc.) | ✅ Visible |
| **Serveur** | `server` | Serveur du personnage (Eden, Blackthorn, etc.) | ✅ Visible |
| **Nom** | `name` | Nom du personnage | ✅ Visible |
| **Niveau** | `level` | Niveau du personnage | ✅ Visible |
| **Rang** | `realm_rank` | Rang de royaume (ex: 5L7) | ✅ Visible |
| **Titre** | `realm_title` | Titre du rang (ex: Challenger) | ✅ Visible |

## 💾 Sauvegarde et Persistance

- La configuration est **automatiquement sauvegardée** dans `Configuration/config.json`
- Les paramètres sont **conservés entre les sessions**
- La visibilité est appliquée au démarrage de l'application
- Un message de confirmation apparaît après la sauvegarde

## 🔧 Configuration Technique

### Fichier de Configuration

```json
{
  "column_visibility": {
    "selection": true,
    "realm": true,
    "season": false,
    "server": false,
    "name": true,
    "level": true,
    "realm_rank": true,
    "realm_title": true
  }
}
```

### Traductions

La fonctionnalité est disponible dans toutes les langues :
- 🇫🇷 **Français** : "Colonnes" / "Configuration des colonnes"
- 🇬🇧 **English** : "Columns" / "Column Configuration"
- 🇩🇪 **Deutsch** : "Spalten" / "Spaltenkonfiguration"

## 🎨 Icône

L'icône utilisée est `Img/colonnes.png`.

## 📝 Utilisation Recommandée

### Exemples de Cas d'Usage

1. **Vue Simplifiée** : Masquer "Saison" et "Serveur" si vous jouez sur un seul serveur
2. **Focus sur le Rang** : Afficher uniquement Nom, Niveau, Rang et Titre
3. **Vue Complète** : Tout afficher pour une vision globale

### Conseils

- ✅ Gardez toujours la colonne "Nom" visible
- ✅ La colonne "Sélection" est utile pour les suppressions en masse
- ⚠️ Si vous masquez toutes les colonnes, rien ne s'affichera !

## 🐛 Dépannage

### Les colonnes ne se masquent pas

1. Vérifiez que vous avez cliqué sur "OK" (pas "Annuler")
2. Redémarrez l'application si nécessaire
3. Vérifiez le fichier `Configuration/config.json`

### Configuration perdue

Si la configuration ne persiste pas :
- Vérifiez les permissions d'écriture sur le dossier `Configuration/`
- Consultez les logs dans `Logs/debug.log` (si le mode debug est activé)

## 🔄 Mise à Jour Future

Cette fonctionnalité pourra être étendue pour :
- Réorganiser l'ordre des colonnes par glisser-déposer
- Sauvegarder plusieurs "profils" de vues
- Ajuster la largeur des colonnes
- Ajouter de nouvelles colonnes (classe, race, guilde, etc.)

---

**Version** : 0.1  
**Date** : Octobre 2025  
**Auteur** : DAOC Character Manager Team
