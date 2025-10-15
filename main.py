import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, Menu
from Functions.character_manager import create_character_data, save_character, get_all_characters
from Functions.language_manager import lang, get_available_languages

# --- Application Constants ---
APP_NAME = "Character Manager"
APP_VERSION = "0.1"


class CharacterApp:
    """
    Main class for the character management application.
    Manages the user interface and interactions.
    """
    def __init__(self, master):
        self.master = master
        master.title(lang.get("window_title"))
        master.geometry("450x300")
        
        # --- Toolbar ---
        toolbar = ttk.Frame(master, padding=(2, 2))
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # --- Create "File" dropdown menu ---
        self.file_menu_button = ttk.Menubutton(toolbar, text=lang.get("file_menu_label"))
        self.file_menu = Menu(self.file_menu_button, tearoff=0)
        self.file_menu_button["menu"] = self.file_menu
        self.file_menu.add_command(label=lang.get("create_button_text"), command=self.create_new_character)
        self.file_menu.add_separator()
        self.file_menu.add_command(label=lang.get("exit_button_text"), command=master.quit)
        self.file_menu_button.pack(side=tk.LEFT)

        # --- Create "View" menu ---
        self.view_menu_button = ttk.Menubutton(toolbar, text=lang.get("view_menu_label"))
        self.view_menu = Menu(self.view_menu_button, tearoff=0)
        self.view_menu_button["menu"] = self.view_menu
        self.view_menu_button.pack(side=tk.LEFT)

        # --- Submenu for language ---
        self.language_submenu = Menu(self.view_menu, tearoff=0)
        self.view_menu.add_cascade(label=lang.get("language_menu_label"), menu=self.language_submenu)
        self.populate_language_menu()

        # --- Create "Help" menu (?) ---
        self.help_menu_button = ttk.Menubutton(toolbar, text="?")
        self.help_menu = Menu(self.help_menu_button, tearoff=0)
        self.help_menu_button["menu"] = self.help_menu
        self.help_menu.add_command(label=lang.get("about_menu_label"), command=self.show_about_dialog)
        # Place the help button on the right side of the toolbar
        self.help_menu_button.pack(side=tk.RIGHT)

        # --- Main content ---
        main_frame = ttk.Frame(master)
        main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.label = ttk.Label(main_frame, text=lang.get("welcome_message"), font=("Segoe UI", 12))
        self.label.pack(pady=10)

        # --- Frame for character selection ---
        selection_frame = ttk.Frame(main_frame)
        selection_frame.pack(pady=5)

        self.char_label = ttk.Label(selection_frame, text=lang.get("existing_character_label"))
        self.char_label.pack(side=tk.LEFT, padx=5)

        self.selected_character = tk.StringVar(master)
        self.character_menu = ttk.Combobox(selection_frame, textvariable=self.selected_character, state="readonly")
        self.character_menu.pack(side=tk.LEFT, padx=5)

        # Load the character list on application startup
        self.refresh_character_list()

    def populate_language_menu(self):
        """Populates the language submenu with the found .json files."""
        self.language_submenu.delete(0, "end")
        available_langs = get_available_languages()
        for lang_code in available_langs:
            # The lambda captures the value of lang_code at creation time
            self.language_submenu.add_command(
                label=lang_code.upper(), 
                command=lambda lc=lang_code: self.change_language(lc)
            )

    def create_new_character(self):
        """
        Handles the action of creating a new character:
        asks the user for a name and saves the character.
        """
        character_name = simpledialog.askstring(
            lang.get("new_char_dialog_title"),
            lang.get("new_char_dialog_prompt"),
            parent=self.master
        )

        if character_name:
            character_data = create_character_data(character_name)
            success, response = save_character(character_data)            

            # The response from save_character is now expected to be a simple string
            message = response
            
            if success:
                self.refresh_character_list() # Update the list after creation
                messagebox.showinfo(lang.get("success_title"), lang.get("char_saved_success", name=character_name))
            else:
                messagebox.showerror(lang.get("error_title"), lang.get("char_exists_error", name=character_name))
        else:
            messagebox.showwarning(lang.get("warning_title"), lang.get("creation_cancelled_message"))

    def refresh_character_list(self):
        """Updates the character list in the dropdown menu."""
        characters = get_all_characters()

        if characters:
            self.character_menu['values'] = characters
            self.selected_character.set(characters[0]) # Select the first one by default
        else:
            self.character_menu['values'] = []
            self.selected_character.set(lang.get("none_option"))
    
    def change_language(self, lang_code):
        """Changes the application language and updates the UI."""
        lang.set_language(lang_code)
        self.retranslate_ui()

    def retranslate_ui(self):
        """Updates the text of all UI widgets."""
        self.master.title(lang.get("window_title"))
        self.label.config(text=lang.get("welcome_message"))
        self.char_label.config(text=lang.get("existing_character_label"))
        
        # File Menu
        self.file_menu_button.config(text=lang.get("file_menu_label"))
        self.file_menu.entryconfig(0, label=lang.get("create_button_text"))
        self.file_menu.entryconfig(2, label=lang.get("exit_button_text")) # Index 2 because there is a separator

        # View Menu
        self.view_menu_button.config(text=lang.get("view_menu_label"))
        self.view_menu.entryconfig(0, label=lang.get("language_menu_label"))

        # Update the combobox if it's empty
        if not self.character_menu['values']:
            self.selected_character.set(lang.get("none_option"))

    def show_about_dialog(self):
        """Displays the 'About' dialog box."""
        title = lang.get("about_message_title", app_name=APP_NAME)
        message = lang.get(
            "about_message_content",
            version=APP_VERSION
        )
        messagebox.showinfo(title, message, parent=self.master)


def main():
    """Main function to launch the application."""
    root = tk.Tk()
    app = CharacterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()