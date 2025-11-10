# Class Banners / Bannières de Classe

## 📁 Structure des Dossiers / Folder Structure

Les bannières de classe doivent être organisées par royaume :

```
Img/Banner/
├── Alb/          # Albion banners
├── Hib/          # Hibernia banners
└── Mid/          # Midgard banners
```

## 🖼️ Format des Fichiers / File Format

- **Nom du fichier** : `{class_name}.jpg` ou `{class_name}.png`
- **Format d'image** : JPG ou PNG
- **Dimensions recommandées** : Largeur 150px (la hauteur s'adapte automatiquement)
- **Ratio recommandé** : Portrait (par exemple 150x400, 150x500, etc.)

## 📝 Noms de Classes / Class Names

Les noms de fichiers doivent correspondre aux noms de classes anglais en **minuscules** :

### Albion (Alb/)
- `armsman.jpg`
- `cabalist.jpg`
- `cleric.jpg`
- `friar.jpg`
- `heretic.jpg`
- `infiltrator.jpg`
- `mercenary.jpg`
- `minstrel.jpg`
- `necromancer.jpg`
- `paladin.jpg`
- `reaver.jpg`
- `scout.jpg`
- `sorcerer.jpg`
- `theurgist.jpg`
- `wizard.jpg`

### Hibernia (Hib/)
- `animist.jpg` ✅
- `bainshee.jpg`
- `bard.jpg`
- `blademaster.jpg`
- `champion.jpg`
- `druid.jpg` ✅
- `eldritch.jpg`
- `enchanter.jpg`
- `hero.jpg`
- `mentalist.jpg`
- `nightshade.jpg`
- `ranger.jpg`
- `valewalker.jpg`
- `vampiir.jpg`
- `warden.jpg` ✅

### Midgard (Mid/)
- `berserker.jpg`
- `bonedancer.jpg`
- `healer.jpg`
- `hunter.jpg`
- `runemaster.jpg`
- `savage.jpg`
- `shadowblade.jpg`
- `shaman.jpg`
- `skald.jpg`
- `spiritmaster.jpg`
- `thane.jpg`
- `valkyrie.jpg`
- `warlock.jpg`
- `warrior.jpg`

## 🔧 Comportement / Behavior

1. **Affichage automatique** : La bannière s'affiche automatiquement quand un personnage a une classe assignée
2. **Mise à jour dynamique** : La bannière change automatiquement quand vous changez de classe ou de royaume
3. **Placeholder** : Si aucune bannière n'est trouvée, un message "Banner not found" s'affiche
4. **Position** : La bannière apparaît sur le côté gauche de la fiche personnage (largeur fixe 150px)

## ✨ Exemples / Examples

### Fichier valide :
- ✅ `Img/Banner/Hib/druid.jpg`
- ✅ `Img/Banner/Alb/paladin.png`
- ✅ `Img/Banner/Mid/berserker.jpg`

### Fichier invalide :
- ❌ `Img/Banner/druid.jpg` (pas dans un dossier de royaume)
- ❌ `Img/Banner/Hib/Druid.jpg` (majuscule incorrecte)
- ❌ `Img/Banner/Hib/druid_class.jpg` (nom incorrect)

## 📥 Sources Recommandées / Recommended Sources

1. Sites officiels DAoC
2. Wikis DAoC communautaires
3. Fan art (avec permission)
4. Créations personnelles

**Note** : Assurez-vous d'avoir les droits d'utilisation des images que vous ajoutez.

---

**Astuce** : Pour créer rapidement toutes les bannières manquantes avec un placeholder, vous pouvez utiliser un outil graphique pour générer des images 150x400px avec le nom de la classe écrit dessus.
