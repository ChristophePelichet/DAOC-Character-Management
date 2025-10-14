import json
import os


class LanguageManager:
    """
    Gère le chargement et l'accès aux chaînes de texte pour l'internationalisation.
    """
    def __init__(self, lang_code='fr'):
        self.strings = {}
        self.load_language(lang_code)
    
    def set_language(self, lang_code):
        """Change la langue active et recharge les chaînes de texte."""
        self.load_language(lang_code)

    def load_language(self, lang_code):
        """Charge un fichier de langue JSON."""
        # Construit le chemin vers le dossier 'Language' à la racine du projet
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # This is d:/Projets/1
        lang_file = os.path.join(project_root, 'Language', f'{lang_code}.json')

        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.strings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erreur: Impossible de charger le fichier de langue '{lang_file}'. {e}")
            # En cas d'erreur, on utilise un dictionnaire vide pour éviter de planter
            self.strings = {}

    def get(self, key, **kwargs):
        """Récupère une chaîne de texte par sa clé et la formate si nécessaire."""
        return self.strings.get(key, key).format(**kwargs)

def get_available_languages():
    """Scanne le dossier 'Language' et retourne une liste des codes de langue disponibles."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    lang_dir = os.path.join(project_root, 'Language')
    if not os.path.exists(lang_dir):
        return []
    
    languages = []
    for filename in os.listdir(lang_dir):
        if filename.endswith('.json'):
            languages.append(os.path.splitext(filename)[0])
    return sorted(languages)

# Instance globale pour être facilement accessible dans toute l'application
lang = LanguageManager()