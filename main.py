import os
import sys
import traceback
import tkinter as tk
import logging
import time
import threading
from tkinter import ttk, simpledialog, messagebox, Menu, filedialog
from Functions.character_manager import create_character_data, save_character, get_all_characters, get_character_dir, REALM_ICONS
from Functions.language_manager import lang, get_available_languages
from Functions.config_manager import config, get_config_dir
from Functions.logging_manager import setup_logging, get_log_dir, get_img_dir
from Functions.path_manager import get_base_path
from PIL import Image, ImageTk # type: ignore

# Setup logging at the very beginning
setup_logging()
# --- Application Constants ---
APP_NAME = "Character Manager"
APP_VERSION = "0.1"

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Catches unhandled exceptions and logs them with full traceback."""
    # Format the traceback
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_string = "".join(tb_lines)
    logging.critical(f"Unhandled exception caught:\n{tb_string}")

class TextHandler(logging.Handler):
    """A custom logging handler that sends records to a Tkinter Text widget."""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        # Define colors for different log levels
        self.level_colors = {
            'DEBUG': 'grey',
            'INFO': 'black',
            'WARNING': 'orange',
            'ERROR': 'red',
            'CRITICAL': 'red'
        }

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n', record.levelname)
            self.text_widget.configure(state='disabled')
            self.text_widget.see(tk.END)
        # This is important to avoid threading issues with Tkinter
        self.text_widget.after(0, append)

class DebugWindow(tk.Toplevel):
    """A Toplevel window that displays log messages."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title(lang.get("debug_window_title"))
        self.geometry("1200x700")

        # --- Menu Bar ---
        self.menu_bar = Menu(self)
        self.config(menu=self.menu_bar)

        self.level_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=lang.get("debug_level_menu"), menu=self.level_menu, underline=0)
        self.level_cascade_index = self.menu_bar.index('end')

        # --- Font Size Menu ---
        self.font_size_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=lang.get("debug_font_size_menu"), menu=self.font_size_menu, underline=0)
        self.font_cascade_index = self.menu_bar.index('end')
        
        self.font_sizes = {
            "small": 8,
            "medium": 9,
            "large": 11
        }
        self.font_size_var = tk.StringVar(value="medium")

        self.log_level_var = tk.StringVar(value="DEBUG")
        self.log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }

        # Level Menu Items
        self.level_menu.add_radiobutton(
            label=lang.get("debug_level_all"),
            variable=self.log_level_var,
            value="DEBUG", # "All" is equivalent to the DEBUG level
            command=self.set_log_level
        )
        self.level_menu.add_separator()

        for level_name in self.log_levels.keys():
            self.level_menu.add_radiobutton(
                label=level_name,
                variable=self.log_level_var,
                value=level_name,
                command=self.set_log_level
            )

        # Font Size Menu Items
        self.font_size_menu.add_radiobutton(
            label=lang.get("font_size_small"), variable=self.font_size_var, value="small", command=self.set_font_size)
        self.font_size_menu.add_radiobutton(
            label=lang.get("font_size_medium"), variable=self.font_size_var, value="medium", command=self.set_font_size)
        self.font_size_menu.add_radiobutton(
            label=lang.get("font_size_large"), variable=self.font_size_var, value="large", command=self.set_font_size)

        # --- Button Bar ---
        button_bar_frame = ttk.Frame(self)
        button_bar_frame.pack(fill='x', padx=5, pady=2)
        self.test_debug_button = ttk.Button(button_bar_frame, text=lang.get("test_debug_button"), command=self.raise_test_exception)
        self.test_debug_button.pack(side='left')

        # --- Main horizontal Paned Window ---
        main_paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned_window.pack(expand=True, fill="both")

        # --- Left vertical Paned Window (for logs and errors) ---
        left_paned_window = ttk.PanedWindow(main_paned_window, orient=tk.VERTICAL)
        main_paned_window.add(left_paned_window, weight=2) # Give more space to the left side

        # --- Top-left pane for general logs ---
        log_frame = ttk.LabelFrame(left_paned_window, text=lang.get("debug_log_pane_title"), name="log_frame")
        self.log_widget = tk.Text(log_frame, wrap="word", state="disabled")
        self.log_widget.pack(expand=True, fill="both")
        left_paned_window.add(log_frame, weight=3) # Give more space to logs

        # --- Bottom-left pane for errors ---
        error_frame = ttk.LabelFrame(left_paned_window, text=lang.get("debug_errors_pane_title"), name="error_frame")
        self.error_widget = tk.Text(error_frame, wrap="word", state="disabled")
        self.error_widget.pack(expand=True, fill="both")
        left_paned_window.add(error_frame, weight=1)

        # --- Right pane for details ---
        self.log_reader_frame = ttk.LabelFrame(main_paned_window, text=lang.get("debug_log_reader_pane_title"), name="log_reader_frame")
        
        # --- File selection bar for log reader ---
        file_bar = ttk.Frame(self.log_reader_frame)
        file_bar.pack(fill='x', padx=5, pady=5)
        self.log_file_path_var = tk.StringVar()
        ttk.Entry(file_bar, textvariable=self.log_file_path_var, state="readonly").pack(side='left', fill='x', expand=True)
        self.browse_log_reader_button = ttk.Button(file_bar, text=lang.get("browse_button"), command=self.browse_log_file)
        self.browse_log_reader_button.pack(side='left', padx=(5, 0))
        self.clear_log_reader_button = ttk.Button(file_bar, text=lang.get("clear_button_text"), command=self.clear_log_reader)
        self.clear_log_reader_button.pack(side='left', padx=(5, 0))

        self.log_reader_widget = tk.Text(self.log_reader_frame, wrap="word", state="disabled")
        self.log_reader_widget.pack(expand=True, fill="both")
        main_paned_window.add(self.log_reader_frame, weight=1)

        # Configure color tags
        for widget in (self.log_widget, self.error_widget, self.log_reader_widget):
            widget.tag_config("DEBUG", foreground="grey")
            widget.tag_config("INFO", foreground="black")
            widget.tag_config("WARNING", foreground="orange")

        self.log_handler = None # For general logs
        self.error_handler = None # For errors and tracebacks

        self.monitoring_thread = None
        self.monitoring_active = False

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def set_log_level(self):
        """Sets the logging level for the text handler based on menu selection."""
        level_name = self.log_level_var.get()
        level = self.log_levels.get(level_name, logging.INFO)
        if self.log_handler:
            self.log_handler.setLevel(level)
            logging.info(f"Niveau de log de la console de débogage réglé sur {level_name}")

    def set_font_size(self):
        """Sets the font size for the text widget and its tags."""
        size_key = self.font_size_var.get()
        size_value = self.font_sizes.get(size_key, 9) # Default to 9 if not found
        
        for widget in (self.log_widget, self.error_widget, self.log_reader_widget):
            widget.config(font=("Courier New", size_value))
            # Re-apply tag fonts to update their size
            widget.tag_config("ERROR", foreground="red", font=("Courier New", size_value, "bold"))
            widget.tag_config("CRITICAL", foreground="red", font=("Courier New", size_value, "bold", "underline"))

    def retranslate(self):
        """Updates the text of the window and its menus."""
        self.title(lang.get("debug_window_title"))
        self.menu_bar.entryconfig(self.level_cascade_index, label=lang.get("debug_level_menu"))
        self.menu_bar.entryconfig(self.font_cascade_index, label=lang.get("debug_font_size_menu"))
        
        self.test_debug_button.config(text=lang.get("test_debug_button"))
        # Retranslate pane titles
        self.log_widget.master.config(text=lang.get("debug_log_pane_title")) # master is the LabelFrame
        self.error_widget.master.config(text=lang.get("debug_errors_pane_title"))
        self.log_reader_frame.config(text=lang.get("debug_log_reader_pane_title"))
        self.browse_log_reader_button.config(text=lang.get("browse_button"))
        self.clear_log_reader_button.config(text=lang.get("clear_button_text"))
        # Retranslate font size menu items
        self.level_menu.entryconfig(0, label=lang.get("debug_level_all"))
        self.font_size_menu.entryconfig(0, label=lang.get("font_size_small"))
        self.font_size_menu.entryconfig(1, label=lang.get("font_size_medium"))
        self.font_size_menu.entryconfig(2, label=lang.get("font_size_large"))

    def raise_test_exception(self):
        """Raises a test exception to verify the handler."""
        logging.info("Raising a test exception...")
        1 / 0

    def on_close(self):
        """Remove the handler and destroy the window."""
        self.stop_log_monitoring()
        if self.log_handler:
            logging.getLogger().removeHandler(self.log_handler)
        if self.error_handler:
            logging.getLogger().removeHandler(self.error_handler)
        self.destroy()

    def set_default_log_file(self, filepath):
        """Sets and tries to monitor the default log file."""
        if os.path.exists(filepath):
            self.log_file_path_var.set(filepath)
            self.start_log_monitoring(filepath)
        else:
            self._append_to_log_reader(lang.get("log_reader_file_not_found") + "\n")

    def browse_log_file(self):
        """Opens a file dialog to select a log file to monitor."""
        filepath = filedialog.askopenfilename(
            title="Select a log file to monitor",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            self.log_file_path_var.set(filepath)
            self.start_log_monitoring(filepath)

    def clear_log_reader(self):
        """Clears the content of the log reader widget."""
        self.log_reader_widget.config(state='normal')
        self.log_reader_widget.delete('1.0', tk.END)
        self.log_reader_widget.config(state='disabled')

    def start_log_monitoring(self, filepath):
        """Starts a thread to monitor the selected log file."""
        self.stop_log_monitoring() # Stop any previous monitoring
        self.clear_log_reader()

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_log_file, args=(filepath,), daemon=True)
        self.monitoring_thread.start()

    def stop_log_monitoring(self):
        """Stops the file monitoring thread."""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_active = False
            self.monitoring_thread.join(timeout=1) # Wait a bit for the thread to exit

    def _monitor_log_file(self, filepath):
        """The actual file monitoring logic that runs in a separate thread."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                # Go to the end of the file
                f.seek(0, 2)
                while self.monitoring_active:
                    line = f.readline()
                    if line:
                        self.log_reader_widget.after(0, self._append_to_log_reader, line)
                    else:
                        time.sleep(0.1) # Wait for new lines
        except Exception as e:
            error_message = f"Error monitoring file {filepath}: {e}\n"
            self.log_reader_widget.after(0, self._append_to_log_reader, error_message)

    def _append_to_log_reader(self, text):
        """Safely appends text to the log reader widget from the main thread."""
        self.log_reader_widget.config(state='normal')
        self.log_reader_widget.insert(tk.END, text)
        self.log_reader_widget.config(state='disabled')
        self.log_reader_widget.see(tk.END)
class NewCharacterDialog(tk.Toplevel):
    """Custom dialog to create a new character with a name and a realm."""
    def __init__(self, parent, title=None, icon_images=None):
        super().__init__(parent)
        self.transient(parent)
        if title:
            self.title(title)

        self.realms = REALM_ICONS
        self.result = None
        self.icon_images = icon_images or {} # Use pre-loaded icons

        self.body_frame = ttk.Frame(self, padding="10 10 10 10")
        self.body_frame.pack(fill="both", expand=True)

        self.body(self.body_frame)
        self.buttonbox()

        self.grab_set() # Modal behavior

    def body(self, master):
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

    def buttonbox(self):
        """Creates OK and Cancel buttons."""
        box = ttk.Frame(self)

        ok_button = ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        ok_button.pack(side=tk.LEFT, padx=5, pady=5)
        cancel_button = ttk.Button(box, text=lang.get("warning_title"), width=10, command=self.cancel)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def ok(self, event=None):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning(lang.get("error_title"), lang.get("char_name_empty_error"), parent=self)
            return

        self.result = (name, self.realm_var.get())
        self.destroy()

    def cancel(self, event=None):
        self.destroy()
    
    def update_realm_icon(self, event=None):
        """Updates the displayed icon based on the selected realm."""
        selected_realm = self.realm_var.get()
        self.realm_icon_label.config(image=self.icon_images.get(selected_realm))

def create_new_character_dialog(parent):
    """
    Wrapper function to launch the custom dialog and return the result.
    Returns a tuple (name, realm) or None if cancelled.
    """
    dialog = NewCharacterDialog(parent, title=lang.get("new_char_dialog_title"), icon_images=parent.app.realm_icons)
    parent.wait_window(dialog)
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
        master.app = self # Make app instance accessible

        # --- Pre-load resources for performance ---
        self.realm_icons = self._load_realm_icons()
        self.available_languages = get_available_languages()
        self.config_window = None

        # --- Debug Window ---
        self.debug_window = None
        self.debug_log_handler = None
        self.debug_error_handler = None
        # For development, we set the default to True
        if config.get("show_debug_window", True):
            self.show_debug_window()
        
        # --- Toolbar ---
        toolbar = ttk.Frame(master, padding=(2, 2))
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # --- Create "File" dropdown menu ---
        self.file_menu_button = ttk.Menubutton(toolbar, text=lang.get("file_menu_label"))
        self.file_menu = Menu(self.file_menu_button, tearoff=0)
        
        # Store references to menu items for easier re-translation
        self.menu_items = {}

        self.file_menu_button["menu"] = self.file_menu
        self.file_menu.add_command(label=lang.get("create_button_text"), command=self.create_new_character)
        self.menu_items['create_index'] = self.file_menu.index('end')
        self.file_menu.add_command(label=lang.get("configuration_menu_label"), command=self.open_configuration_window)
        self.menu_items['config_index'] = self.file_menu.index('end')
        self.file_menu.add_separator()
        self.file_menu.add_command(label=lang.get("exit_button_text"), command=master.quit)
        self.menu_items['exit_index'] = self.file_menu.index('end')
        self.file_menu_button.pack(side=tk.LEFT)

        # --- Create "Help" menu (?) ---
        self.help_menu_button = ttk.Menubutton(toolbar, text="?")
        self.help_menu = Menu(self.help_menu_button, tearoff=0)
        self.help_menu_button["menu"] = self.help_menu
        self.help_menu.add_command(label=lang.get("about_menu_label"), command=self.show_about_dialog)
        self.menu_items['about_index'] = self.help_menu.index('end')
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

        # --- Status Bar ---
        self.status_bar = ttk.Frame(master, relief=tk.SUNKEN, padding=(2, 2))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = ttk.Label(self.status_bar, text="Initialisation...")
        self.status_label.pack(side=tk.LEFT)

    def _load_realm_icons(self):
        """Loads and resizes realm icons once at startup."""
        logging.debug("Pre-loading realm icons.")
        icon_images = {}
        img_dir = get_img_dir() # Use the centralized function
        for realm, icon_path in REALM_ICONS.items():
            try:
                full_path = os.path.join(img_dir, icon_path)
                img = Image.open(full_path)
                img = img.resize((32, 32), Image.Resampling.LANCZOS)
                icon_images[realm] = ImageTk.PhotoImage(img)
            except FileNotFoundError:
                logging.warning(f"Icon not found for {realm} at {full_path}")
                icon_images[realm] = None
        return icon_images

    def create_new_character(self):
        """
        Handles the action of creating a new character manually.
        """
        result = create_new_character_dialog(self.master) # This now opens the clean dialog

        if result:
            character_name, realm = result
            character_data = create_character_data(character_name, realm)
            success, response = save_character(character_data)
            if success:
                self.refresh_character_list()
                logging.info(f"Successfully created character '{character_name}'.")
                messagebox.showinfo(lang.get("success_title"), lang.get("char_saved_success", name=character_name))
            else:
                # If the response is a known error key, translate it. Otherwise, display as is.
                if response == "char_exists_error":
                    error_message = lang.get(response, name=character_name)
                else:
                    error_message = response # For other potential errors
                logging.error(f"Failed to create character '{character_name}': {error_message}")
                messagebox.showerror(lang.get("error_title"), error_message)
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
        self.file_menu.entryconfig(self.menu_items['create_index'], label=lang.get("create_button_text"))
        self.file_menu.entryconfig(self.menu_items['config_index'], label=lang.get("configuration_menu_label"))
        self.file_menu.entryconfig(self.menu_items['exit_index'], label=lang.get("exit_button_text"))
        self.help_menu.entryconfig(self.menu_items['about_index'], label=lang.get("about_menu_label"))

        # Update the combobox if it's empty
        if not self.character_menu['values']:
            self.selected_character.set(lang.get("none_option"))
        
        # Update status bar if it exists
        self.update_status_bar(lang.get("status_bar_loaded", duration=self.master.load_time))
        
        # Retranslate the config window if it exists
        if self.config_window:
            self._retranslate_configuration_window()
        
        # Retranslate the debug window if it exists
        if self.debug_window:
            self.debug_window.retranslate()

    def show_debug_window(self):
        """Creates and shows the debug window."""
        if self.debug_window is None or not self.debug_window.winfo_exists():
            # Force the main window to update its geometry info
            self.master.update_idletasks()

            # Get main window position and size
            main_x = self.master.winfo_x()
            main_y = self.master.winfo_y()
            main_width = self.master.winfo_width()

            # Calculate position for the debug window (to the right of the main window)
            offset_x = main_x + main_width + 10
            offset_y = main_y

            self.debug_window = DebugWindow(self.master)
            self.debug_window.geometry(f"+{offset_x}+{offset_y}")

            # Create handler for general logs
            self.debug_log_handler = TextHandler(self.debug_window.log_widget)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            self.debug_log_handler.setFormatter(formatter)
            self.debug_window.log_handler = self.debug_log_handler # Give handler to window

            # Create handler for errors/tracebacks
            self.debug_error_handler = TextHandler(self.debug_window.error_widget)
            error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(pathname)s:%(lineno)d\n%(message)s')
            self.debug_error_handler.setFormatter(error_formatter)
            self.debug_error_handler.setLevel(logging.ERROR) # This handler only cares about errors
            self.debug_window.error_handler = self.debug_error_handler

            self.debug_window.set_log_level() # Set initial level
            self.debug_window.set_font_size() # Set initial font size

            # Re-run setup_logging to include the new handler
            setup_logging(extra_handlers=[self.debug_log_handler, self.debug_error_handler])
            logging.info("Fenêtre de débogage initialisée.")

            # Set default log file for the reader
            default_log_path = os.path.join(get_log_dir(), "debug.log")
            self.debug_window.set_default_log_file(default_log_path)

    def hide_debug_window(self):
        if self.debug_window and self.debug_window.winfo_exists():
            self.debug_window.on_close()

    def show_about_dialog(self):
        """Displays the 'About' dialog box."""
        title = lang.get("about_message_title", app_name=APP_NAME)
        message = lang.get(
            "about_message_content",
            version=APP_VERSION
        )
        messagebox.showinfo(title, message, parent=self.master)

    def update_status_bar(self, message):
        """Updates the text in the status bar."""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)

    def _create_configuration_window(self):
        """Creates the configuration window widgets. Called only once."""
        logging.debug("Creating configuration window for the first time.")
        self.config_window = tk.Toplevel(self.master)
        self.config_window.title(lang.get("configuration_window_title"))
        self.config_window.geometry("500x440")
        self.config_window.resizable(True, True)
        
        self.config_widgets = {} # To store widgets that need re-translation
        # Instead of destroying, hide the window
        self.config_window.protocol("WM_DELETE_WINDOW", self.hide_configuration_window)

        # --- Language Selection ---
        language_frame = ttk.Frame(self.config_window, padding=(10, 10, 10, 0))
        language_frame.pack(fill=tk.X)
        
        self.config_widgets['language_label'] = ttk.Label(language_frame, text=lang.get("config_language_label") + ":")
        self.config_widgets['language_label'].pack(side=tk.LEFT, padx=(0, 5))

        self.language_var = tk.StringVar()
        language_combo = ttk.Combobox(language_frame, textvariable=self.language_var, state="readonly")
        language_combo['values'] = list(self.available_languages.values())
        language_combo.pack(side=tk.LEFT)

        # --- Separator ---
        separator_conf = ttk.Separator(self.config_window, orient='horizontal')
        separator_conf.pack(fill='x', padx=10, pady=10)

        # --- Widgets for Config Folder Path ---
        self.config_widgets['config_path_frame'] = ttk.LabelFrame(self.config_window, text=lang.get("config_file_path_label"), padding=10)
        self.config_widgets['config_path_frame'].pack(fill=tk.X, padx=10, pady=5)
        self.config_path_var = tk.StringVar()
        config_path_entry = ttk.Entry(self.config_widgets['config_path_frame'], textvariable=self.config_path_var, width=50)
        config_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.config_widgets['config_browse_button'] = ttk.Button(self.config_widgets['config_path_frame'], text=lang.get("browse_button"), command=self.browse_config_folder)
        self.config_widgets['config_browse_button'].pack(side=tk.LEFT)

        # --- Separator for future options ---
        separator = ttk.Separator(self.config_window, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=10)

        # --- Widgets for Character Folder Path ---
        self.config_widgets['path_frame'] = ttk.LabelFrame(self.config_window, text=lang.get("config_path_label"), padding=10)
        self.config_widgets['path_frame'].pack(fill=tk.X, padx=10, pady=10)
        self.char_path_var = tk.StringVar()
        path_entry = ttk.Entry(self.config_widgets['path_frame'], textvariable=self.char_path_var, width=50)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.config_widgets['browse_button'] = ttk.Button(self.config_widgets['path_frame'], text=lang.get("browse_button"), command=self.browse_character_folder)
        self.config_widgets['browse_button'].pack(side=tk.LEFT)

        # --- Separator for directory sections ---
        dir_separator = ttk.Separator(self.config_window, orient='horizontal')
        dir_separator.pack(fill='x', padx=20, pady=5)

        # --- Debugging Mode Checkbox ---
        debug_frame = ttk.Frame(self.config_window, padding=(10, 0, 10, 5))
        debug_frame.pack(fill=tk.X)
        self.debug_mode_var = tk.BooleanVar()
        self.config_widgets['debug_check'] = ttk.Checkbutton(debug_frame, text=lang.get("config_debug_mode_label"), variable=self.debug_mode_var)
        self.config_widgets['debug_check'].pack(side=tk.LEFT, padx=10)

        # --- Show Debug Window Checkbox ---
        show_debug_win_frame = ttk.Frame(self.config_window, padding=(10, 0, 10, 5))
        show_debug_win_frame.pack(fill=tk.X)
        self.show_debug_window_var = tk.BooleanVar()
        self.config_widgets['show_debug_win_check'] = ttk.Checkbutton(show_debug_win_frame, text=lang.get("config_show_debug_window_label"), variable=self.show_debug_window_var)
        self.config_widgets['show_debug_win_check'].pack(side=tk.LEFT, padx=10)

        # --- Widgets for Log Folder Path ---
        self.config_widgets['log_path_frame'] = ttk.LabelFrame(self.config_window, text=lang.get("config_log_path_label"), padding=10)
        self.config_widgets['log_path_frame'].pack(fill=tk.X, padx=10, pady=10)
        self.log_path_var = tk.StringVar()
        log_path_entry = ttk.Entry(self.config_widgets['log_path_frame'], textvariable=self.log_path_var, width=50)
        log_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.config_widgets['log_browse_button'] = ttk.Button(self.config_widgets['log_path_frame'], text=lang.get("browse_button"), command=self.browse_log_folder)
        self.config_widgets['log_browse_button'].pack(side=tk.LEFT)

        # --- Save Button ---
        button_frame = ttk.Frame(self.config_window, padding=10)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.config_widgets['save_button'] = ttk.Button(button_frame, text=lang.get("save_button"), command=self.save_configuration)
        self.config_widgets['save_button'].pack(side=tk.RIGHT)

    def _update_configuration_fields(self):
        """Refreshes the values in the configuration window from the config."""
        current_lang_code = config.get("language")
        self.language_var.set(self.available_languages.get(current_lang_code))
        self.config_path_var.set(get_config_dir())
        self.char_path_var.set(get_character_dir())
        self.debug_mode_var.set(config.get("debug_mode", True))
        self.show_debug_window_var.set(config.get("show_debug_window", True))
        self.log_path_var.set(get_log_dir())

    def _retranslate_configuration_window(self):
        """Updates the text of all widgets in the configuration window."""
        if not self.config_window:
            return
        self.config_window.title(lang.get("configuration_window_title"))
        self.config_widgets['language_label'].config(text=lang.get("config_language_label") + ":")
        self.config_widgets['config_path_frame'].config(text=lang.get("config_file_path_label"))
        self.config_widgets['config_browse_button'].config(text=lang.get("browse_button"))
        self.config_widgets['path_frame'].config(text=lang.get("config_path_label"))
        self.config_widgets['browse_button'].config(text=lang.get("browse_button"))
        self.config_widgets['debug_check'].config(text=lang.get("config_debug_mode_label"))
        self.config_widgets['show_debug_win_check'].config(text=lang.get("config_show_debug_window_label"))
        self.config_widgets['log_path_frame'].config(text=lang.get("config_log_path_label"))
        self.config_widgets['log_browse_button'].config(text=lang.get("browse_button"))
        self.config_widgets['save_button'].config(text=lang.get("save_button"))

    def hide_configuration_window(self):
        """Hides the configuration window."""
        if self.config_window:
            self.config_window.grab_release()
            self.config_window.withdraw()

    def open_configuration_window(self):
        """Opens the configuration window."""
        logging.debug("Opening configuration window.")
        if self.config_window is None or not self.config_window.winfo_exists():
            self._create_configuration_window()
        
        # Refresh fields and show the window
        self._update_configuration_fields()
        self.config_window.deiconify()
        self.config_window.lift()
        self.config_window.grab_set()

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

    def save_configuration(self):
        """Saves the configuration and closes the window."""
        # Get old and new debug mode states for comparison
        old_debug_mode = config.get("debug_mode", True)
        new_debug_mode = self.debug_mode_var.get()

        # Log deactivation while logging is still active
        if not new_debug_mode and old_debug_mode:
            logging.info("Debug mode has been DEACTIVATED. This is the last log entry.")

        # Save all settings
        config.set("config_folder", self.config_path_var.get())
        config.set("character_folder", self.char_path_var.get())
        config.set("log_folder", self.log_path_var.get())
        config.set("debug_mode", new_debug_mode)
        
        show_debug = self.show_debug_window_var.get()
        config.set("show_debug_window", show_debug)

        # Determine if language needs to change, but don't apply it yet
        selected_lang_name = self.language_var.get()
        new_lang_code = None
        for code, name in self.available_languages.items():
            if name == selected_lang_name:
                new_lang_code = code
                break
        
        language_changed = new_lang_code and new_lang_code != config.get("language")
        if language_changed:
            config.set("language", new_lang_code)
        
        # Re-apply logging settings immediately after saving debug mode
        # Pass the debug handler if it exists
        setup_logging(extra_handlers=[self.debug_log_handler, self.debug_error_handler])
        
        # Show or hide the debug window based on the new setting
        if show_debug:
            self.show_debug_window()
        else:
            self.hide_debug_window()

        # Log activation now that logging is configured
        if new_debug_mode and not old_debug_mode:
            logging.info("Debug mode has been ACTIVATED.")

        self.refresh_character_list() # Refresh list in case path changed
        self.hide_configuration_window() # Hide window BEFORE showing messagebox
        messagebox.showinfo(lang.get("success_title"), lang.get("config_saved_success"), parent=self.master)

        # Apply language change AFTER all windows are closed/hidden
        if language_changed:
            self.change_language(new_lang_code)


def main():
    """Main function to launch the application."""
    start_time = time.perf_counter()
    root = tk.Tk()
    # Attach app instance to root to make it accessible from Toplevel windows

    # Set up global exception handling
    sys.excepthook = global_exception_handler
    root.report_callback_exception = global_exception_handler
    app = CharacterApp(root)

    # Calculate and store loading time
    end_time = time.perf_counter()
    load_duration = end_time - start_time
    logging.info(f"Application loaded in {load_duration:.4f} seconds.")
    root.load_time = load_duration # Store it on the root window
    app.update_status_bar(lang.get("status_bar_loaded", duration=load_duration))

    root.mainloop()

if __name__ == "__main__":
    main()