# Copilot Instructions - Base Rules

## 🚫 NEVER DO AUTOMATICALLY

**ONLY on explicit user request:**
- ❌ Git commit
- ❌ Git push
- ❌ Git merge
- ❌ Documentation modifications (README, CHANGELOG, etc.)
- ❌ Translations (Language/*.json)
- ❌ Generate documentation, comments, JSDoc blocks, or README files
- ❌ Modify existing documentation, changelogs, or readme files
- ❌ Change version numbers in documentation

**UNIQUEMENT sur demande explicite de l'utilisateur :**
- ❌ Git commit
- ❌ Git push
- ❌ Git merge
- ❌ Modifications de documentation (README, CHANGELOG, etc.)
- ❌ Traductions (Language/*.json)
- ❌ Générer de la documentation, commentaires, blocs JSDoc, ou fichiers README
- ❌ Modifier la documentation existante, changelogs, ou fichiers readme
- ❌ Changer les numéros de version dans la documentation

## ✅ Standard Workflow

**When user requests a feature/fix:**

1. **Implementation ONLY**: Write the requested code
2. **STOP**: Wait for user instructions
3. **Ask user** if they want: commit, translations, documentation, etc.

**Lorsque l'utilisateur demande une fonctionnalité/correction :**

1. **Implémentation UNIQUEMENT** : Écrire le code demandé
2. **STOP** : Attendre les instructions de l'utilisateur
3. **Demander à l'utilisateur** s'il veut : commit, traductions, documentation, etc.

## 📝 Code Rules

**English:**
- **All code comments MUST be in English**
- **Variable names in English**
- **Function/class names in English**
- **Only UI strings use lang.get() for translations**
- **NEVER hardcode user-facing text in code** - Always use Language/*.json files with lang.get()
- **Always implement retranslate_ui() for dialogs/windows** - UI must refresh when language changes
- **Always think about refreshing UI items when language changes** - Update labels, buttons, menus, etc.

**Français:**
- **Tous les commentaires de code DOIVENT être en anglais**
- **Noms de variables en anglais**
- **Noms de fonctions/classes en anglais**
- **Seules les chaînes UI utilisent lang.get() pour les traductions**
- **JAMAIS de texte utilisateur hardcodé dans le code** - Toujours utiliser les fichiers Language/*.json avec lang.get()
- **Toujours implémenter retranslate_ui() pour les dialogues/fenêtres** - L'UI doit se rafraîchir au changement de langue
- **Toujours penser au refresh des items au changement de langue** - Mettre à jour labels, boutons, menus, etc.

## 📁 Folder Structure Rules

**English:**
- **Technical documentation**: Must be created in `Documentation/` folder (not "Documentation")
- **Changelogs**: Must be created in `Changelogs/` folder

**Français:**
- **Documentation technique** : Doit être créée dans le dossier `Documentation/` (pas "Documentation")
- **Changelogs** : Doivent être créés dans le dossier `Changelogs/`

## 🔗 Complete Workflow (only if explicitly requested)

If user says "use complete workflow" or "apply full process":
See `.prompts/feature_complete.prompt.md` for the 7-step automated process

Si l'utilisateur dit "utilise le workflow complet" ou "applique le processus complet" :
Voir `.prompts/feature_complete.prompt.md` pour le processus automatisé en 7 étapes

**Otherwise: Code only, then STOP and wait**
**Sinon : Code uniquement, puis STOP et attendre**
