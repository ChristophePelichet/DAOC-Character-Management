# Instructions Copilot - Workflow Complet de Fonctionnalité

Lorsque l'utilisateur demande de développer, modifier ou corriger une fonctionnalité, suivre **automatiquement** le workflow complet décrit dans `.prompts/feature_complete.prompt.md` :

## Workflow Automatique (7 étapes)

1. **Implémentation** : Coder la fonctionnalité demandée
2. **Traductions** : Ajouter/modifier automatiquement dans FR/EN/DE (Language/*.json)
3. **Changelog** : Mettre à jour les 4-5 fichiers changelog obligatoires
4. **Commit** : Message structuré en anglais (types conventionnels)
5. **Push** : Vers la branche actuelle
6. **Merge** : Sur main avec --no-ff (AUTOMATIQUE)
7. **Confirmation** : Statistiques complètes

## Règles Strictes

- ✅ **AUTOMATIQUE** : Aucune confirmation demandée
- ✅ **Traductions** : TOUJOURS FR/EN/DE pour textes UI
- ✅ **Changelog** : 4 fichiers minimum (Full FR/EN + Simple FR/EN)
- ✅ **Commit** : Anglais uniquement, 9 sections structurées
- ✅ **Merge** : Flag --no-ff OBLIGATOIRE
- ⚠️ **Exception** : Arrêt uniquement si conflits

## Référence Complète

Pour tous les détails, voir : `.prompts/feature_complete.prompt.md`
