# Instructions pour la gestion des fichiers changelog simple et full

Création et ou update d'un fichier unique de changelog concis et simple. Avec ajout des versions futures.

**Contexte Général :**
* Les date devront être au format ISO : YYYY-MM-DD
* La version sera donné grace à la balise {version_cible}.
* Si aucune versionb n'est donnée pas la balise {version_cible}, utilise la version actuelle.
* Pour chaque ligne ajouté tenter de trouver un emoji adapté sauf pour celle des titres de section définies ci dessous.


**Context pour la version full :**
* Ajouté en fin de version les numéros de commit et les informations permettant de s'y retrouver facilement.

**Instructions :**
* Ajouté au fichier CHANGELOG_SIMPLE_FR.md le contenu de la nouvelle version selon les commits récents de cette branche. Les commit seront surement en anglais il faudra les traduire en français de façon concise.
* Ajouté au fichier CHANGELOG_FR.md le contenu de la nouvelle version selon les commits récents de cette branche. Les commit seront surement en anglais il faudra les traduire en français de façon complète.

**Structures :**
* Il faudra aussi les structurer par sujet puis appliquer la mise en forme suivante :

# ✨✨{version_cible} - Date au format ISO


### 🎉 Ajout 
Liste de toutes les fonctionnalités ajoutées dans cette version

### 🧰 Modification
Liste de toutes les modifications apportées dans cette version aux fonctionnalités existantes

### 🐛 Correction
Liste de tous les bugs ayant été corrigés dans cette version

### 🔚 Retrait
Liste de toutes les fonctionnalités retirées dans cette versio

**Tâches Post-Processing :**
* Une fois les fichier simple et full en _FR terminé , tu peux mettre à jour les fichiers _EN en traduisant le contenu français que tu viens de créer.

**Tâche de mise à jour du fichier principal CHANGELOG.md :**
* Cette tâche doit se passer en dernier , une fois que tous les fichiers simples et full dans les 2 langues sont terminées.
* Mettre à jour le fichier CHANGELOG.md en y ajoutant au début les liens sur la version simeple et full en français et en anglais de la verison en cours.
* Ne rien rajouter d'autre dans ce fichier.



