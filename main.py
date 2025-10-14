import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, Menu
from Functions.character_manager import create_character_data, save_character, get_all_characters
from Functions.language_manager import lang, get_available_languages

# --- Constantes de l'application ---
APP_NAME = "Character Manager"
APP_VERSION = "0.1"


class CharacterApp:
    """
    Classe principale de l'application de gestion de personnages.
    Gère l'interface utilisateur et les interactions.
    """
    def __init__(self, master):
        self.master = master
        master.title(lang.get("window_title"))
        master.geometry("450x300")
        
        # --- Barre d'outils ---
        toolbar = ttk.Frame(master, padding=(2, 2))
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # --- Création du menu déroulant "Fichier" ---
        self.file_menu_button = ttk.Menubutton(toolbar, text=lang.get("file_menu_label"))
        self.file_menu = Menu(self.file_menu_button, tearoff=0)
        self.file_menu_button["menu"] = self.file_menu
        self.file_menu.add_command(label=lang.get("create_button_text"), command=self.create_new_character)
        self.file_menu.add_separator()
        self.file_menu.add_command(label=lang.get("exit_button_text"), command=master.quit)
        self.file_menu_button.pack(side=tk.LEFT)

        # --- Création du menu "Affichage" ---
        self.view_menu_button = ttk.Menubutton(toolbar, text=lang.get("view_menu_label"))
        self.view_menu = Menu(self.view_menu_button, tearoff=0)
        self.view_menu_button["menu"] = self.view_menu
        self.view_menu_button.pack(side=tk.LEFT)

        # --- Sous-menu pour la langue ---
        self.language_submenu = Menu(self.view_menu, tearoff=0)
        self.view_menu.add_cascade(label=lang.get("language_menu_label"), menu=self.language_submenu)
        self.populate_language_menu()

        # --- Création du menu "Aide" (?) ---
        self.help_menu_button = ttk.Menubutton(toolbar, text="?")
        self.help_menu = Menu(self.help_menu_button, tearoff=0)
        self.help_menu_button["menu"] = self.help_menu
        self.help_menu.add_command(label=lang.get("about_menu_label"), command=self.show_about_dialog)
        # Placer le bouton d'aide à droite de la barre d'outils
        self.help_menu_button.pack(side=tk.RIGHT)

        # --- Contenu principal ---
        main_frame = ttk.Frame(master)
        main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.label = ttk.Label(main_frame, text=lang.get("welcome_message"), font=("Segoe UI", 12))
        self.label.pack(pady=10)

        # --- Cadre pour la sélection de personnage ---
        selection_frame = ttk.Frame(main_frame)
        selection_frame.pack(pady=5)

        self.char_label = ttk.Label(selection_frame, text=lang.get("existing_character_label"))
        self.char_label.pack(side=tk.LEFT, padx=5)

        self.selected_character = tk.StringVar(master)
        self.character_menu = ttk.Combobox(selection_frame, textvariable=self.selected_character, state="readonly")
        self.character_menu.pack(side=tk.LEFT, padx=5)

        # Charger la liste des personnages au démarrage de l'application
        self.refresh_character_list()

    def populate_language_menu(self):
        """Remplit le sous-menu des langues avec les fichiers .json trouvés."""
        self.language_submenu.delete(0, "end")
        available_langs = get_available_languages()
        for lang_code in available_langs:
            # La lambda capture la valeur de lang_code au moment de la création
            self.language_submenu.add_command(
                label=lang_code.upper(), 
                command=lambda lc=lang_code: self.change_language(lc)
            )

    def create_new_character(self):
        """
        Gère l'action de création d'un nouveau personnage :
        demande le nom à l'utilisateur et sauvegarde le personnage.
        """
        character_name = simpledialog.askstring(
            lang.get("new_char_dialog_title"),
            lang.get("new_char_dialog_prompt"),
            parent=self.master
        )

        if character_name:
            character_data = create_character_data(character_name)
            success, response = save_character(character_data)            

            key, params = response 
            message = lang.get(key, **params) # On utilise les paramètres pour formater le message
            
            if success:
                self.refresh_character_list() # Mettre à jour la liste après création
                messagebox.showinfo(lang.get("success_title"), message)
            else:
                messagebox.showerror(lang.get("error_title"), message)
        else:
            messagebox.showwarning(lang.get("warning_title"), lang.get("creation_cancelled_message"))

    def refresh_character_list(self):
        """Met à jour la liste des personnages dans le menu déroulant."""
        characters = get_all_characters()

        if characters:
            self.character_menu['values'] = characters
            self.selected_character.set(characters[0]) # Sélectionner le premier par défaut
        else:
            self.character_menu['values'] = []
            self.selected_character.set(lang.get("none_option"))
    
    def change_language(self, lang_code):
        """Change la langue de l'application et met à jour l'interface."""
        lang.set_language(lang_code)
        self.retranslate_ui()

    def retranslate_ui(self):
        """Met à jour le texte de tous les widgets de l'interface."""
        self.master.title(lang.get("window_title"))
        self.label.config(text=lang.get("welcome_message"))
        self.char_label.config(text=lang.get("existing_character_label"))
        
        # Menu Fichier
        self.file_menu_button.config(text=lang.get("file_menu_label"))
        self.file_menu.entryconfig(0, label=lang.get("create_button_text"))
        self.file_menu.entryconfig(2, label=lang.get("exit_button_text")) # L'index 2 car il y a un séparateur

        # Menu Affichage
        self.view_menu_button.config(text=lang.get("view_menu_label"))
        self.view_menu.entryconfig(0, label=lang.get("language_menu_label"))

        # Mettre à jour la combobox si elle est vide
        if not self.character_menu['values']:
            self.selected_character.set(lang.get("none_option"))

    def show_about_dialog(self):
        """Affiche la boîte de dialogue 'À propos'."""
        title = lang.get("about_message_title", app_name=APP_NAME)
        message = lang.get(
            "about_message_content",
            version=APP_VERSION
        )
        messagebox.showinfo(title, message, parent=self.master)


def main():
    """Fonction principale pour lancer l'application."""
    root = tk.Tk()
    app = CharacterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()