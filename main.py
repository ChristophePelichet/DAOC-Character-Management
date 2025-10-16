import os
import sys
import tkinter as tk
import logging
from tkinter import ttk, simpledialog, messagebox, Menu, filedialog
from PIL import Image, ImageTk # type: ignore
from Functions.character_manager import create_character_data, save_character, get_all_characters, get_character_dir, REALM_ICONS
from Functions.language_manager import lang, get_available_languages
from Functions.config_manager import config, get_config_dir
from Functions.logging_manager import setup_logging, get_log_dir, get_img_dir
from Functions.path_manager import get_base_path

# Setup logging at the very beginning
setup_logging()
# --- Application Constants ---
APP_NAME = "Character Manager"
APP_VERSION = "0.1"

class NewCharacterDialog(simpledialog.Dialog):
    """Custom dialog to create a new character with a name and a realm."""
    def __init__(self, parent, title=None):
        self.realms = REALM_ICONS
        self.result = None
        self.icon_images = {} # To hold PhotoImage objects
        super().__init__(parent, title)

    def _load_icons(self):
        """Load realm icons and store them as PhotoImage objects."""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = get_base_path()
        img_dir = os.path.join(base_path, "Img")
        for realm, icon_path in self.realms.items():
            try:
                full_path = os.path.join(img_dir, icon_path)
                img = Image.open(full_path)
                img = img.resize((32, 32), Image.Resampling.LANCZOS) # Resize for display
                self.icon_images[realm] = ImageTk.PhotoImage(img)
            except FileNotFoundError:
                logging.warning(f"Icon not found for {realm} at {full_path}")
                self.icon_images[realm] = None # Handle missing icon gracefully    

    def body(self, master):
        self._load_icons()

        # --- Realm Icon Display ---
        self.realm_icon_label = ttk.Label(master)
        self.realm_icon_label.grid(row=0, columnspan=2, padx=5, pady=(5, 10)) # Centered at the top

        # --- Name entry ---
        ttk.Label(master, text=lang.get("new_char_dialog_prompt")).grid(row=1, columnspan=2, sticky=tk.W, padx=5, pady=2)
        self.name_entry = ttk.Entry(master, width=30)
        self.name_entry.grid(row=2, columnspan=2, padx=5, pady=2)
        self.name_entry.focus_set()

        # --- Realm selection ---
        ttk.Label(master, text=lang.get("new_char_realm_prompt")).grid(row=3, columnspan=2, sticky=tk.W, padx=5, pady=2)

        self.realm_var = tk.StringVar(value=list(self.realms.keys())[0])
        self.realm_combo = ttk.Combobox(master, textvariable=self.realm_var, values=list(self.realms.keys()), state="readonly")
        self.realm_combo.grid(row=4, columnspan=2, padx=5, pady=2)
        self.realm_combo.bind("<<ComboboxSelected>>", self.update_realm_icon)

        self.update_realm_icon() # Set initial icon

        return self.name_entry # initial focus

    def validate(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning(lang.get("error_title"), lang.get("char_name_empty_error"), parent=self)
            return 0
        return 1

    def apply(self):
        name = self.name_entry.get().strip()
        realm = self.realm_var.get()
        self.result = (name, realm)
    
    def update_realm_icon(self, event=None):
        """Updates the displayed icon based on the selected realm."""
        selected_realm = self.realm_var.get()
        self.realm_icon_label.config(image=self.icon_images.get(selected_realm))

def create_new_character_dialog(parent):
    """
    Wrapper function to launch the custom dialog and return the result.
    Returns a tuple (name, realm) or None if cancelled.
    """
    dialog = NewCharacterDialog(parent, title=lang.get("new_char_dialog_title"))
    return dialog.result







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

    def create_new_character(self):
        """
        Handles the action of creating a new character:
        asks the user for a name and saves the character.
        """
        result = create_new_character_dialog(self.master)

        if result:
            character_name, realm = result
            character_data = create_character_data(character_name, realm)
            success, response = save_character(character_data)            
            
            if success:
                self.refresh_character_list() # Update the list after creation
                logging.info(f"Successfully created character '{character_name}'.")
                messagebox.showinfo(lang.get("success_title"), lang.get("char_saved_success", name=character_name))
            else:
                # The error message from save_character is already translated
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
        config.set("language", lang_code)
        lang.set_language(lang_code)
        self.retranslate_ui()

    def retranslate_ui(self):
        """Updates the text of all UI widgets."""
        self.master.title(lang.get("window_title"))
        self.label.config(text=lang.get("welcome_message"))
        self.char_label.config(text=lang.get("existing_character_label"))
        
        # Rebuild File Menu
        self.file_menu_button.config(text=lang.get("file_menu_label"))
        self.file_menu.delete(0, "end")
        self.file_menu.add_command(label=lang.get("create_button_text"), command=self.create_new_character)
        self.file_menu.add_command(label=lang.get("configuration_menu_label"), command=self.open_configuration_window)
        self.file_menu.add_separator()
        self.file_menu.add_command(label=lang.get("exit_button_text"), command=self.master.quit)

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
        config_window.geometry("500x440")
        config_window.resizable(True, True)
        config_window.grab_set()  # Modal behavior

        # --- Language Selection ---
        self.available_languages = get_available_languages() # e.g., {'fr': 'Français', 'en': 'English'}
        
        language_frame = ttk.Frame(config_window, padding=(10, 10, 10, 0))
        language_frame.pack(fill=tk.X)
        
        language_label = ttk.Label(language_frame, text=lang.get("config_language_label") + ":")
        language_label.pack(side=tk.LEFT, padx=(0, 5))

        # The variable will store the full name for display
        current_lang_code = config.get("language")
        self.language_var = tk.StringVar(value=self.available_languages.get(current_lang_code))

        language_combo = ttk.Combobox(language_frame, textvariable=self.language_var, state="readonly")
        language_combo['values'] = list(self.available_languages.values())
        language_combo.pack(side=tk.LEFT)

        # --- Separator ---
        separator_conf = ttk.Separator(config_window, orient='horizontal')
        separator_conf.pack(fill='x', padx=10, pady=10)

        # --- Widgets for Config Folder Path ---
        config_path_frame = ttk.LabelFrame(config_window, text=lang.get("config_file_path_label"), padding=10)
        config_path_frame.pack(fill=tk.X, padx=10, pady=5)

        self.config_path_var = tk.StringVar(value=get_config_dir())
        
        config_path_entry = ttk.Entry(config_path_frame, textvariable=self.config_path_var, width=50)
        config_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        config_browse_button = ttk.Button(config_path_frame, text=lang.get("browse_button"), command=self.browse_config_folder)
        config_browse_button.pack(side=tk.LEFT)



        # --- Separator for future options ---
        separator = ttk.Separator(config_window, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=10)

        # --- Widgets for Character Folder Path ---
        path_frame = ttk.LabelFrame(config_window, text=lang.get("config_path_label"), padding=10)
        path_frame.pack(fill=tk.X, padx=10, pady=10)

        self.char_path_var = tk.StringVar(value=get_character_dir())
        
        path_entry = ttk.Entry(path_frame, textvariable=self.char_path_var, width=50)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        browse_button = ttk.Button(path_frame, text=lang.get("browse_button"), command=self.browse_character_folder)
        browse_button.pack(side=tk.LEFT)

        # --- Separator for directory sections ---
        dir_separator = ttk.Separator(config_window, orient='horizontal')
        dir_separator.pack(fill='x', padx=20, pady=5)

        # --- Debugging Mode Checkbox ---
        debug_frame = ttk.Frame(config_window, padding=(10, 0, 10, 5))
        debug_frame.pack(fill=tk.X)

        self.debug_mode_var = tk.BooleanVar(value=config.get("debug_mode", False))
        debug_check = ttk.Checkbutton(debug_frame, text=lang.get("config_debug_mode_label"), variable=self.debug_mode_var)
        debug_check.pack(side=tk.LEFT, padx=10)

        # --- Widgets for Log Folder Path ---
        log_path_frame = ttk.LabelFrame(config_window, text=lang.get("config_log_path_label"), padding=10)
        log_path_frame.pack(fill=tk.X, padx=10, pady=10)

        self.log_path_var = tk.StringVar(value=get_log_dir())
        
        log_path_entry = ttk.Entry(log_path_frame, textvariable=self.log_path_var, width=50)
        log_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        log_browse_button = ttk.Button(log_path_frame, text=lang.get("browse_button"), command=self.browse_log_folder)
        log_browse_button.pack(side=tk.LEFT)

        # --- Widgets for Img Folder Path ---
        img_path_frame = ttk.LabelFrame(config_window, text=lang.get("config_img_path_label"), padding=10)
        img_path_frame.pack(fill=tk.X, padx=10, pady=10)

        self.img_path_var = tk.StringVar(value=get_img_dir())
        
        img_path_entry = ttk.Entry(img_path_frame, textvariable=self.img_path_var, width=50)
        img_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        img_browse_button = ttk.Button(img_path_frame, text=lang.get("browse_button"), command=self.browse_img_folder)
        img_browse_button.pack(side=tk.LEFT)


        # --- Save Button ---
        button_frame = ttk.Frame(config_window, padding=10)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        save_button = ttk.Button(button_frame, text=lang.get("save_button"), command=lambda: self.save_configuration(config_window))
        save_button.pack(side=tk.RIGHT)

    def browse_config_folder(self):
        """Opens a dialog to select a directory for the configuration file."""
        directory = filedialog.askdirectory(
            title=lang.get("select_config_folder_dialog_title"),
            initialdir=self.config_path_var.get() or os.path.expanduser("~")
        )
        if directory:
            self.config_path_var.set(directory)

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

    def browse_img_folder(self):
        """Opens a dialog to select a directory for images."""
        directory = filedialog.askdirectory(
            title=lang.get("select_img_folder_dialog_title"),
            initialdir=self.img_path_var.get() or os.path.expanduser("~")
        )
        if directory:
            self.img_path_var.set(directory)

    def save_configuration(self, window):
        """Saves the configuration and closes the window."""
        # Get old and new debug mode states for comparison
        old_debug_mode = config.get("debug_mode", False)
        new_debug_mode = self.debug_mode_var.get()

        # Log deactivation while logging is still active
        if not new_debug_mode and old_debug_mode:
            logging.info("Debug mode has been DEACTIVATED. This is the last log entry.")

        # Check if language has changed
        selected_lang_name = self.language_var.get()
        # Find the code corresponding to the selected name
        new_lang_code = None
        for code, name in self.available_languages.items():
            if name == selected_lang_name:
                new_lang_code = code
                break
        if new_lang_code and new_lang_code != config.get("language"):
            self.change_language(new_lang_code)

        # Save all settings
        config.set("config_folder", self.config_path_var.get())
        config.set("character_folder", self.char_path_var.get())
        config.set("log_folder", self.log_path_var.get())
        config.set("img_folder", self.img_path_var.get())
        config.set("debug_mode", new_debug_mode)
        
        # Re-apply logging settings immediately after saving debug mode
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