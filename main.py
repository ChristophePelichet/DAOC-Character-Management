import os
import tkinter as tk
import logging
from tkinter import ttk, simpledialog, messagebox, Menu, filedialog
from Functions.character_manager import create_character_data, save_character, get_all_characters, get_character_dir
from Functions.language_manager import lang, get_available_languages
from Functions.config_manager import config
from Functions.logging_manager import setup_logging, get_log_dir

# Setup logging at the very beginning
setup_logging()
# --- Application Constants ---
APP_NAME = "Character Manager"
APP_VERSION = "0.1"


class CharacterApp:
    """
    Main class for the character management application.
    Manages the user interface and interactions.
    """
    def __init__(self, master):
        logging.info("Application starting...")
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
        self.file_menu.add_command(label=lang.get("configuration_menu_label"), command=self.open_configuration_window)
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
                logging.info(f"Successfully created character '{character_name}'.")
                messagebox.showinfo(lang.get("success_title"), lang.get("char_saved_success", name=character_name))
            else:
                messagebox.showerror(lang.get("error_title"), lang.get("char_exists_error", name=character_name))
        else:
            messagebox.showwarning(lang.get("warning_title"), lang.get("creation_cancelled_message"))

    def refresh_character_list(self):
        """Updates the character list in the dropdown menu."""
        logging.debug("Refreshing character list.")
        characters = get_all_characters()

        if characters:
            self.character_menu['values'] = characters
            self.selected_character.set(characters[0]) # Select the first one by default
        else:
            self.character_menu['values'] = []
            self.selected_character.set(lang.get("none_option"))
    
    def change_language(self, lang_code):
        """Changes the application language and updates the UI."""
        logging.info(f"Changing language to {lang_code}.")
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
        self.file_menu.entryconfig(1, label=lang.get("configuration_menu_label"))
        self.file_menu.entryconfig(3, label=lang.get("exit_button_text")) # Index 3 because there is a separator

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

    def open_configuration_window(self):
        """Opens the configuration window."""
        logging.debug("Opening configuration window.")
        config_window = tk.Toplevel(self.master)
        config_window.title(lang.get("configuration_window_title"))
        config_window.geometry("500x280")
        config_window.resizable(True, True)
        config_window.grab_set()  # Modal behavior

        # --- Widgets for Character Folder Path ---
        path_frame = ttk.LabelFrame(config_window, text=lang.get("config_path_label"), padding=10)
        path_frame.pack(fill=tk.X, padx=10, pady=10)

        self.char_path_var = tk.StringVar(value=get_character_dir())
        
        path_entry = ttk.Entry(path_frame, textvariable=self.char_path_var, width=50)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        browse_button = ttk.Button(path_frame, text=lang.get("browse_button"), command=self.browse_character_folder)
        browse_button.pack(side=tk.LEFT)

        # --- Separator for future options ---
        separator = ttk.Separator(config_window, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=10)

        # --- Debugging Mode Checkbox ---
        debug_frame = ttk.Frame(config_window, padding=(10, 0))
        debug_frame.pack(fill=tk.X, padx=10)

        self.debug_mode_var = tk.BooleanVar(value=config.get("debug_mode", False))
        debug_check = ttk.Checkbutton(debug_frame, text=lang.get("config_debug_mode_label"), variable=self.debug_mode_var)
        debug_check.pack(side=tk.LEFT)

        # --- Widgets for Log Folder Path ---
        log_path_frame = ttk.LabelFrame(config_window, text=lang.get("config_log_path_label"), padding=10)
        log_path_frame.pack(fill=tk.X, padx=10, pady=10)

        self.log_path_var = tk.StringVar(value=get_log_dir())
        
        log_path_entry = ttk.Entry(log_path_frame, textvariable=self.log_path_var, width=50)
        log_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        log_browse_button = ttk.Button(log_path_frame, text=lang.get("browse_button"), command=self.browse_log_folder)
        log_browse_button.pack(side=tk.LEFT)

        # --- Save Button ---
        button_frame = ttk.Frame(config_window, padding=10)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        save_button = ttk.Button(button_frame, text=lang.get("save_button"), command=lambda: self.save_configuration(config_window))
        save_button.pack(side=tk.RIGHT)

    def browse_character_folder(self):
        """Opens a dialog to select a directory."""
        directory = filedialog.askdirectory(
            title=lang.get("select_folder_dialog_title"),
            initialdir=self.char_path_var.get() or os.path.expanduser("~")
        )
        if directory:
            self.char_path_var.set(directory)

    def browse_log_folder(self):
        """Opens a dialog to select a directory for logs."""
        directory = filedialog.askdirectory(
            title=lang.get("select_log_folder_dialog_title"),
            initialdir=self.log_path_var.get() or os.path.expanduser("~")
        )
        if directory:
            self.log_path_var.set(directory)

    def save_configuration(self, window):
        """Saves the configuration and closes the window."""
        # Get old and new debug mode states for comparison
        old_debug_mode = config.get("debug_mode", False)
        new_debug_mode = self.debug_mode_var.get()

        # Log deactivation while logging is still active
        if not new_debug_mode and old_debug_mode:
            logging.info("Debug mode has been DEACTIVATED. This is the last log entry.")

        # Save all settings
        config.set("character_folder", self.char_path_var.get())
        config.set("log_folder", self.log_path_var.get())
        config.set("debug_mode", new_debug_mode)
        
        # Re-apply logging settings immediately
        setup_logging()
        
        # Log activation now that logging is configured
        if new_debug_mode and not old_debug_mode:
            logging.info("Debug mode has been ACTIVATED.")

        self.refresh_character_list() # Refresh list in case path changed
        messagebox.showinfo(lang.get("success_title"), lang.get("config_saved_success"), parent=window)
        window.destroy()


def main():
    """Main function to launch the application."""
    root = tk.Tk()
    app = CharacterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()