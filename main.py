"""
DAOC Character Manager - Main Application Entry Point (Refactored v0.104)
Application PySide6 de gestion de personnages pour Dark Age of Camelot

Refactoring complet:
- Code extrait vers des managers dédiés (UIManager, TreeManager, CharacterActionsManager)
- Optimisations des performances (cache, chargement lazy)
- Code nettoyé et documenté
- Architecture modulaire et maintenable
"""

import sys
import traceback
import logging
import time

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QMessageBox, QDialog, QStyleFactory, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtGui import QStandardItemModel
from PySide6.QtCore import Qt, Slot, QTimer

# Import des managers fonctionnels
from Functions.config_manager import config, get_config_dir
from Functions.language_manager import lang, get_available_languages
from Functions.logging_manager import setup_logging, get_log_dir
from Functions.path_manager import get_base_path
from Functions.data_manager import DataManager

# Import des managers UI
from Functions.ui_manager import UIManager
from Functions.tree_manager import TreeManager
from Functions.character_actions_manager import CharacterActionsManager

# Import des composants UI
from UI import DebugWindow, CenterIconDelegate, CenterCheckboxDelegate, RealmTitleDelegate, NormalTextDelegate, UrlButtonDelegate, CharacterUpdateDialog, HeraldScraperWorker
from UI.dialogs import ColumnsConfigDialog, ConfigurationDialog

# Configuration de l'application
setup_logging()

APP_NAME = "DAOC Character Manager"
APP_VERSION = "0.104"


def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Gestionnaire global des exceptions non gérées"""
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_string = "".join(tb_lines)
    logging.critical(f"Unhandled exception:\n{tb_string}")


class CharacterApp(QMainWindow):
    """
    Application principale de gestion de personnages DAOC
    Architecture refactorisée avec managers dédiés
    """
    
    def __init__(self):
        logging.info(f"Starting {APP_NAME} v{APP_VERSION}")
        super().__init__()
        
        self.setWindowTitle(lang.get("window_title"))
        self.resize(550, 400)
        
        # Initialisation des managers de données
        self.data_manager = DataManager()
        self.available_languages = get_available_languages()
        
        # Fenêtres auxiliaires
        self.config_window = None
        self.debug_window = None
        self.eden_debug_window = None
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Initialisation de l'UIManager
        self.ui_manager = UIManager(self)
        self.ui_manager.create_menu_bar()
        self.ui_manager.create_eden_status_bar(main_layout)
        self.ui_manager.create_bulk_actions_bar(main_layout)
        
        # Création du TreeView
        from PySide6.QtWidgets import QTreeView
        self.character_tree = QTreeView()
        main_layout.addWidget(self.character_tree)
        
        # Initialisation du TreeManager
        self.tree_manager = TreeManager(self, self.character_tree, self.data_manager)
        
        # Application des delegates personnalisés
        self.center_icon_delegate = CenterIconDelegate(self)
        self.character_tree.setItemDelegateForColumn(1, self.center_icon_delegate)
        
        self.center_checkbox_delegate = CenterCheckboxDelegate(self)
        self.character_tree.setItemDelegateForColumn(0, self.center_checkbox_delegate)
        
        # Appliquer le delegate texte normal pour toutes les colonnes de texte (y compris le titre)
        # Ordre: Selection(0), Realm(1), Name(2), Class(3), Level(4), Rank(5), Title(6), Guild(7), Page(8), Server(9), Race(10), URL(11)
        self.normal_text_delegate = NormalTextDelegate(self)
        for col in [2, 3, 4, 5, 6, 7, 8, 9, 10]:  # Name, Class, Level, Rank, Title, Guild, Page, Server, Race
            self.character_tree.setItemDelegateForColumn(col, self.normal_text_delegate)
        
        # Appliquer le delegate URL pour la colonne URL (11)
        self.url_button_delegate = UrlButtonDelegate(self)
        self.character_tree.setItemDelegateForColumn(11, self.url_button_delegate)
        
        # Initialisation du CharacterActionsManager
        self.actions_manager = CharacterActionsManager(self, self.tree_manager)
        
        # Connexion des signaux
        self.character_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.character_tree.customContextMenuRequested.connect(self._on_tree_right_click)
        self.character_tree.doubleClicked.connect(self.actions_manager.open_character_sheet)
        self.character_tree.header().sectionMoved.connect(self._on_section_moved)
        
        # Création du menu contextuel
        self.ui_manager.create_context_menu()
        
        # Barre de statut
        self.ui_manager.create_status_bar()
        
        # Chargement des personnages
        self.tree_manager.refresh_character_list()
        
        # Migration automatique si nécessaire
        self._run_automatic_migration()
        
        # Disclaimer au démarrage
        self._show_startup_disclaimer()
        
    def _run_automatic_migration(self):
        """Exécute la migration automatique au démarrage si nécessaire"""
        try:
            from Functions.migration_manager import (
                run_migration_if_needed, run_migration_with_backup, get_backup_path
            )
            
            was_needed, success, message = run_migration_if_needed()
            
            if was_needed and not success:
                backup_path = get_backup_path()
                
                # Message multilingue avec chemin de sauvegarde
                message_parts = [
                    lang.get("migration_startup_message_fr", default=""),
                    "",
                    lang.get("migration_startup_message_en", default=""),
                    "",
                    lang.get("migration_startup_message_de", default=""),
                    "",
                    "─" * 60,
                    "",
                    lang.get("migration_backup_location", default="💾 Backup location:"),
                    backup_path,
                    "",
                    "─" * 60,
                    "",
                    lang.get("migration_warning", default=""),
                    "",
                    lang.get("migration_question", default="")
                ]
                
                complete_message = "\n".join(message_parts)
                
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle(lang.get("migration_startup_title", default="Migration Required"))
                msg_box.setIcon(QMessageBox.Question)
                msg_box.setText(complete_message)
                
                ok_button = msg_box.addButton(QMessageBox.Ok)
                cancel_button = msg_box.addButton(QMessageBox.Cancel)
                msg_box.setDefaultButton(ok_button)
                
                result = msg_box.exec()
                
                if result == QMessageBox.Cancel:
                    logging.info("User cancelled migration. Closing application.")
                    QMessageBox.information(
                        self,
                        lang.get("migration_cancelled_title", default="Migration Cancelled"),
                        lang.get("migration_cancelled_message", default="Migration cancelled.")
                    )
                    sys.exit(0)
                else:
                    logging.info("User confirmed migration. Starting backup and migration...")
                    
                    progress = QMessageBox(self)
                    progress.setWindowTitle(lang.get("migration_in_progress", default="Migration in progress..."))
                    progress.setText(lang.get("migration_backup_info", default="Creating backup..."))
                    progress.setStandardButtons(QMessageBox.NoButton)
                    progress.setModal(True)
                    progress.show()
                    QApplication.processEvents()
                    
                    try:
                        success, migration_message, backup_path = run_migration_with_backup()
                    finally:
                        progress.close()
                        progress.deleteLater()
                    
                    if success:
                        logging.info(f"Migration successful: {migration_message}")
                        
                        # Vérifier et mettre à jour la structure des fichiers JSON
                        logging.info("Checking JSON structure...")
                        from Functions.migration_manager import check_and_upgrade_json_structures_if_needed
                        
                        json_success, json_message, json_stats = check_and_upgrade_json_structures_if_needed()
                        
                        if json_success and json_stats.get('upgraded', 0) > 0:
                            migration_message += f"\n\n📄 {json_message}"
                            logging.info(f"JSON structure upgrade: {json_message}")
                        
                        QMessageBox.information(
                            self,
                            lang.get("migration_success", default="Migration successful!"),
                            f"✅ {migration_message}\n\n💾 {lang.get('migration_backup_location')}\n{backup_path}"
                        )
                        self.tree_manager.refresh_character_list()
                    else:
                        logging.error(f"Migration failed: {migration_message}")
                        QMessageBox.critical(
                            self,
                            lang.get("migration_error", default="Migration error"),
                            migration_message
                        )
                        sys.exit(1)
                        
        except Exception as e:
            logging.error(f"Error during automatic migration: {e}")
            QMessageBox.critical(
                self,
                lang.get("migration_error", default="Migration error"),
                f"An error occurred during migration: {str(e)}"
            )
            sys.exit(1)
            
    def _show_startup_disclaimer(self):
        """Affiche le disclaimer au démarrage si non désactivé"""
        if not config.get("disable_disclaimer", False):
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(lang.get("disclaimer_title", default="Alpha Version"))
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText(lang.get("disclaimer_message", default="Version Alpha"))
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            
    # ========================================================================
    # MÉTHODES PUBLIQUES - Actions principales
    # ========================================================================
    
    def create_new_character(self):
        """Crée un nouveau personnage (appelé depuis le menu)"""
        self.actions_manager.create_new_character()
        
    def delete_selected_character(self):
        """Supprime le personnage sélectionné (appelé depuis menu contextuel)"""
        self.actions_manager.delete_selected_character()
        
    def rename_selected_character(self):
        """Renomme le personnage sélectionné (appelé depuis menu contextuel)"""
        self.actions_manager.rename_selected_character()
        
    def duplicate_selected_character(self):
        """Duplique le personnage sélectionné (appelé depuis menu contextuel)"""
        self.actions_manager.duplicate_selected_character()
    
    def update_character_from_herald(self):
        """Met à jour le personnage sélectionné depuis Herald"""
        # Récupérer le personnage sélectionné
        selected_indices = self.character_tree.selectedIndexes()
        if not selected_indices:
            return
        
        # Récupérer l'ID du personnage
        row = selected_indices[0].row()
        realm_index = self.tree_manager.model.index(row, 1)
        char_id = realm_index.data(Qt.UserRole)
        
        if not char_id:
            return
        
        # Récupérer les données du personnage
        character_data = self.tree_manager.characters_by_id.get(char_id)
        if not character_data:
            return
        
        # Vérifier si le personnage a une URL Herald
        herald_url = character_data.get('url', '').strip()
        if not herald_url:
            QMessageBox.warning(
                self,
                lang.get("update_char_error"),
                lang.get("update_char_no_url")
            )
            return
        
        # Stocker les données du personnage pour le callback
        self._current_character_data = character_data
        
        # Créer une fenêtre de progression personnalisée avec animation
        self.progress_dialog = QDialog(self)
        self.progress_dialog.setWindowTitle("⏳ Mise à jour en cours...")
        self.progress_dialog.setModal(True)
        self.progress_dialog.setFixedSize(450, 150)
        
        progress_layout = QVBoxLayout(self.progress_dialog)
        progress_layout.setSpacing(15)
        
        # Icône et titre
        title_layout = QHBoxLayout()
        title_label = QLabel("🌐 Récupération des données depuis Eden Herald...")
        title_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        title_layout.addWidget(title_label)
        progress_layout.addLayout(title_layout)
        
        # Message de détail
        detail_label = QLabel("Connexion au serveur et extraction des informations du personnage.")
        detail_label.setWordWrap(True)
        detail_label.setStyleSheet("color: #666; font-size: 10pt;")
        progress_layout.addWidget(detail_label)
        
        # Barre de progression indéterminée (animation)
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 0)  # Mode indéterminé = animation
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(25)
        progress_layout.addWidget(progress_bar)
        
        # Message d'attente
        wait_label = QLabel("⏱️ Veuillez patienter, cette opération peut prendre quelques secondes...")
        wait_label.setStyleSheet("color: #888; font-size: 9pt; font-style: italic;")
        wait_label.setWordWrap(True)
        progress_layout.addWidget(wait_label)
        
        progress_layout.addStretch()
        
        # Créer et démarrer le worker thread
        self.herald_worker = HeraldScraperWorker(herald_url)
        self.herald_worker.finished.connect(self._on_herald_scraping_finished_main)
        
        # Afficher le dialogue et démarrer le worker
        self.progress_dialog.show()
        self.herald_worker.start()
    
    def _on_herald_scraping_finished_main(self, success, new_data, error_msg):
        """Callback appelé quand le scraping est terminé (depuis main)"""
        # Fermer et supprimer la fenêtre de progression
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
            self.progress_dialog.deleteLater()
            delattr(self, 'progress_dialog')
        
        if not success:
            QMessageBox.critical(
                self,
                lang.get("update_char_error"),
                f"{lang.get('update_char_error')}: {error_msg}"
            )
            return
        
        # Récupérer les données du personnage depuis la variable stockée
        character_data = self._current_character_data
        
        # Afficher le dialogue de validation des changements
        dialog = CharacterUpdateDialog(self, character_data, new_data, character_data['name'])
        
        if dialog.exec() == QDialog.Accepted:
            selected_changes = dialog.get_selected_changes()
            
            if not selected_changes:
                QMessageBox.information(
                    self,
                    lang.get("update_char_cancelled"),
                    lang.get("update_char_no_changes")
                )
                return
            
            # Appliquer les changements sélectionnés
            for field, value in selected_changes.items():
                character_data[field] = value
            
            # Sauvegarder le personnage (allow_overwrite=True pour écraser le fichier existant)
            from Functions.character_manager import save_character
            success, msg = save_character(character_data, allow_overwrite=True)
            
            if not success:
                QMessageBox.critical(
                    self,
                    lang.get("error_title", default="Erreur"),
                    f"Échec de la sauvegarde : {msg}"
                )
                return
            
            # Rafraîchir l'affichage
            self.tree_manager.refresh_character_list()
            
            QMessageBox.information(
                self,
                lang.get("success_title", default="Succès"),
                lang.get("update_char_success")
            )
        else:
            QMessageBox.information(
                self,
                lang.get("update_char_cancelled"),
                lang.get("update_char_cancelled")
            )
        
    def execute_bulk_action(self):
        """Exécute l'action groupée sélectionnée"""
        selected_action = self.bulk_action_combo.currentText()
        if selected_action == lang.get("bulk_action_delete"):
            self.actions_manager.delete_checked_characters()
            
    def open_armor_management_global(self):
        """Ouvre la gestion des armures (appelé depuis menu contextuel)"""
        self.actions_manager.open_armor_management()
        
    def update_selection_count(self):
        """Met à jour le compteur de sélection dans la barre de statut"""
        checked_ids = self.tree_manager.get_checked_character_ids()
        total = self.tree_manager.model.rowCount()
        
        if len(checked_ids) > 0:
            self.ui_manager.update_status_bar(
                lang.get("status_bar_selection_count", count=len(checked_ids), total=total)
            )
        else:
            if hasattr(self, 'load_time'):
                self.ui_manager.update_status_bar(
                    lang.get("status_bar_loaded", duration=self.load_time)
                )
            else:
                self.ui_manager.update_status_bar("")
                
    def refresh_character_list(self):
        """Rafraîchit la liste des personnages (compatibilité ascendante)"""
        self.tree_manager.refresh_character_list()
        
    # ========================================================================
    # CONFIGURATION
    # ========================================================================
    
    def open_columns_configuration(self):
        """Ouvre la configuration des colonnes"""
        logging.debug("Opening columns configuration dialog")
        dialog = ColumnsConfigDialog(self)
        if dialog.exec() == QDialog.Accepted:
            visibility_config = dialog.get_visibility_config()
            config.set("column_visibility", visibility_config)
            self.tree_manager.apply_column_visibility()
            QMessageBox.information(
                self,
                lang.get("success_title", default="Succès"),
                lang.get("columns_config_saved", default="Configuration sauvegardée.")
            )
    
    def open_cookie_manager(self):
        """Ouvre le gestionnaire de cookies Eden"""
        logging.debug("Opening cookie manager dialog")
        from UI.dialogs import CookieManagerDialog
        
        dialog = CookieManagerDialog(self)
        dialog.exec()
    
    def open_eden_debug(self):
        """Ouvre la fenêtre de debug Eden"""
        if self.eden_debug_window is None:
            from UI.debug_window import EdenDebugWindow
            self.eden_debug_window = EdenDebugWindow(self)
        
        self.eden_debug_window.show()
        self.eden_debug_window.raise_()
        self.eden_debug_window.activateWindow()
    
    def check_json_structures(self):
        """Vérifie et met à jour la structure des fichiers JSON"""
        from Functions.migration_manager import check_and_upgrade_json_structures_if_needed
        
        # Confirmation
        reply = QMessageBox.question(
            self,
            "Vérification de structure",
            "Cette opération va vérifier tous les fichiers de personnages et ajouter les champs manquants si nécessaire.\n\n"
            "Un backup de chaque fichier sera créé avant modification.\n\n"
            "Voulez-vous continuer ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Afficher une fenêtre de progression
        progress = QMessageBox(self)
        progress.setWindowTitle("Vérification en cours...")
        progress.setText("🔍 Analyse des fichiers JSON en cours...\n\nVeuillez patienter...")
        progress.setStandardButtons(QMessageBox.NoButton)
        progress.setModal(True)
        progress.show()
        QApplication.processEvents()
        
        try:
            success, message, stats = check_and_upgrade_json_structures_if_needed()
        finally:
            progress.close()
            progress.deleteLater()
        
        # Afficher le résultat
        if success:
            details = f"\n\n📊 Statistiques :\n"
            details += f"  • Fichiers vérifiés : {stats.get('checked', 0)}\n"
            details += f"  • Fichiers mis à jour : {stats.get('upgraded', 0)}\n"
            details += f"  • Erreurs : {stats.get('errors', 0)}"
            
            QMessageBox.information(
                self,
                "✅ Vérification terminée",
                f"{message}{details}"
            )
            
            # Rafraîchir la liste si des fichiers ont été modifiés
            if stats.get('upgraded', 0) > 0:
                self.tree_manager.refresh_character_list()
        else:
            QMessageBox.critical(
                self,
                "❌ Erreur",
                f"Une erreur est survenue :\n\n{message}"
            )
    
    def show_help_create_character(self):
        """Affiche l'aide pour créer un nouveau personnage"""
        from Functions.help_manager import HelpManager
        from Functions.config_manager import config
        
        # Créer le gestionnaire d'aide avec la langue actuelle
        current_lang = config.get("language", "fr")
        help_manager = HelpManager(language=current_lang)
        
        # Afficher l'aide
        help_manager.show_help('character_create', parent=self)
    
    def show_help_edit_character(self):
        """Affiche l'aide pour modifier un personnage"""
        from Functions.help_manager import HelpManager
        from Functions.config_manager import config
        
        current_lang = config.get("language", "fr")
        help_manager = HelpManager(language=current_lang)
        help_manager.show_help('character_edit', parent=self)
    
    def show_help_delete_character(self):
        """Affiche l'aide pour supprimer un personnage"""
        from Functions.help_manager import HelpManager
        from Functions.config_manager import config
        
        current_lang = config.get("language", "fr")
        help_manager = HelpManager(language=current_lang)
        help_manager.show_help('character_delete', parent=self)
            
    def open_configuration(self):
        """Ouvre la fenêtre de configuration"""
        logging.debug("Opening configuration window")
        seasons = config.get("seasons", ["S1", "S2", "S3"])
        servers = config.get("servers", ["Eden", "Blackthorn"])
        realms = self.data_manager.get_realms()
        
        dialog = ConfigurationDialog(
            self, self.available_languages,
            available_seasons=seasons,
            available_servers=servers,
            available_realms=realms
        )
        
        if dialog.exec() == QDialog.Accepted:
            self.save_configuration(dialog)
            
    def save_configuration(self, dialog):
        """Sauvegarde la configuration"""
        old_debug_mode = config.get("debug_mode", False)
        new_debug_mode = dialog.debug_mode_check.isChecked()
        
        if not new_debug_mode and old_debug_mode:
            logging.info("Debug mode DEACTIVATED")
            
        # Vérifier si le dossier des personnages a changé
        old_char_folder = config.get("character_folder", "")
        new_char_folder = dialog.char_path_edit.text()
        char_folder_changed = (old_char_folder != new_char_folder)
        
        # Sauvegarder tous les paramètres
        config.set("character_folder", new_char_folder)
        config.set("config_folder", dialog.config_path_edit.text())
        config.set("log_folder", dialog.log_path_edit.text())
        config.set("armor_folder", dialog.armor_path_edit.text())
        config.set("debug_mode", new_debug_mode)
        config.set("show_debug_window", dialog.show_debug_window_check.isChecked())
        config.set("disable_disclaimer", dialog.disable_disclaimer_check.isChecked())
        config.set("seasons", dialog.available_seasons)
        config.set("servers", dialog.available_servers)
        config.set("default_season", dialog.default_season_combo.currentText())
        config.set("default_server", dialog.default_server_combo.currentText())
        config.set("default_realm", dialog.default_realm_combo.currentText())
        
        # Mode de redimensionnement des colonnes
        new_manual_resize = dialog.manual_column_resize_check.isChecked()
        old_manual_resize = config.get("manual_column_resize", False)
        config.set("manual_column_resize", new_manual_resize)
        if new_manual_resize != old_manual_resize:
            self.tree_manager.apply_column_resize_mode(new_manual_resize)
        
        # Navigateur et téléchargement
        config.set("preferred_browser", dialog.browser_combo.currentText())
        config.set("allow_browser_download", dialog.allow_browser_download_check.isChecked())
            
        # Langue
        selected_lang_name = dialog.language_combo.currentText()
        new_lang_code = None
        for code, name in self.available_languages.items():
            if name == selected_lang_name:
                new_lang_code = code
                break
                
        language_changed = new_lang_code and new_lang_code != config.get("language")
        if language_changed:
            config.set("language", new_lang_code)
            
        setup_logging()
        
        if new_debug_mode and not old_debug_mode:
            logging.info("Debug mode ACTIVATED")
            
        QMessageBox.information(
            self,
            lang.get("success_title"),
            lang.get("config_saved_success")
        )
        
        # Vérifier la migration si le dossier des personnages a changé
        if char_folder_changed:
            self._check_migration_on_path_change()
            
        if language_changed:
            self.change_language(new_lang_code)
            
    def _check_migration_on_path_change(self):
        """Vérifie si une migration est nécessaire après changement de chemin"""
        from Functions.migration_manager import (
            check_migration_needed, is_migration_done, run_migration_with_backup
        )
        
        if check_migration_needed() and not is_migration_done():
            new_char_folder = config.get("character_folder", "")
            logging.warning(f"Path changed to location requiring migration: {new_char_folder}")
            
            reply = QMessageBox.question(
                self,
                lang.get("migration_path_change_title"),
                lang.get("migration_path_change_question"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                logging.info("User chose immediate migration after path change")
                
                progress = QMessageBox(self)
                progress.setWindowTitle(lang.get("migration_backup_info"))
                progress.setText(lang.get("migration_backup_info"))
                progress.setStandardButtons(QMessageBox.NoButton)
                progress.show()
                QApplication.processEvents()
                
                try:
                    success, migration_message, backup_path = run_migration_with_backup()
                    
                    if success:
                        logging.info(f"Migration successful. Backup: {backup_path}")
                        QMessageBox.information(
                            self,
                            lang.get("success_title"),
                            f"✅ {migration_message}\n\n💾 {lang.get('migration_backup_location')}\n{backup_path}"
                        )
                        self.tree_manager.refresh_character_list()
                    else:
                        logging.error(f"Migration failed: {migration_message}")
                        QMessageBox.critical(
                            self,
                            lang.get("error_title"),
                            f"{lang.get('migration_error')}\n\n{migration_message}"
                        )
                finally:
                    progress.close()
                    progress.deleteLater()
            else:
                logging.info("User declined immediate migration")
                QMessageBox.information(
                    self,
                    lang.get("info_title"),
                    lang.get("migration_path_change_later")
                )
                
    # ========================================================================
    # LANGUE ET INTERFACE
    # ========================================================================
    
    def change_language(self, lang_code):
        """Change la langue de l'application"""
        logging.info(f"Changing language to {lang_code}")
        config.set("language", lang_code)
        lang.set_language(lang_code)
        self.retranslate_ui()
        
    def retranslate_ui(self):
        """Met à jour toutes les traductions de l'interface"""
        self.setWindowTitle(lang.get("window_title"))
        self.ui_manager.retranslate_ui()
        self.tree_manager.refresh_character_list()
        
        if hasattr(self, 'load_time'):
            self.ui_manager.update_status_bar(
                lang.get("status_bar_loaded", duration=self.load_time)
            )
            
    # ========================================================================
    # FENÊTRES AUXILIAIRES
    # ========================================================================
    
    def show_debug_window(self):
        """Affiche la fenêtre de debug"""
        if not self.debug_window:
            self.debug_window = DebugWindow()
        
        main_window_geom = self.geometry()
        self.debug_window.move(main_window_geom.right() + 10, main_window_geom.top())
        self.debug_window.show()
        
    def hide_debug_window(self):
        """Cache la fenêtre de debug"""
        if self.debug_window:
            self.debug_window.close()
            self.debug_window = None
            
    def show_about_dialog(self):
        """Affiche la boîte de dialogue 'À propos'"""
        self.ui_manager.show_about_dialog(APP_NAME, APP_VERSION)
        
    def open_herald_search(self):
        """Ouvre la fenêtre de recherche Herald"""
        from UI.dialogs import HeraldSearchDialog
        dialog = HeraldSearchDialog(self)
        dialog.exec()
        
    # ========================================================================
    # ÉVÉNEMENTS
    # ========================================================================
    
    def _on_tree_right_click(self, position):
        """Gère le clic droit sur la liste"""
        self.ui_manager.show_context_menu(position)
        
    @Slot(int, int, int)
    def _on_section_moved(self, logical_index, old_visual_index, new_visual_index):
        """Log le déplacement d'une colonne"""
        header_item = self.tree_manager.model.horizontalHeaderItem(logical_index)
        column_name = header_item.text() if header_item else f"Column {logical_index}"
        logging.debug(f"Column '{column_name}' moved from {old_visual_index} to {new_visual_index}")
        
    def closeEvent(self, event):
        """Sauvegarde l'état de l'application à la fermeture"""
        logging.info("Main window closing")
        
        # Sauvegarder l'état de l'en-tête
        self.tree_manager.save_header_state()
        
        if self.debug_window:
            self.debug_window.close()
            
        super().closeEvent(event)


def apply_theme(app):
    """Applique le thème configuré"""
    app.setStyleSheet("")
    if "windowsvista" in QStyleFactory.keys():
        logging.info("Applying 'windowsvista' style")
        app.setStyle("windowsvista")
    else:
        logging.info("Applying default system style")


def main():
    """Point d'entrée principal de l'application"""
    start_time = time.perf_counter()
    
    app = QApplication(sys.argv)
    apply_theme(app)
    
    # Configuration du gestionnaire d'exceptions global
    sys.excepthook = global_exception_handler
    
    main_window = CharacterApp()
    
    # Calcul et affichage du temps de chargement
    end_time = time.perf_counter()
    load_duration = end_time - start_time
    logging.info(f"Application loaded in {load_duration:.4f} seconds")
    main_window.load_time = load_duration
    main_window.ui_manager.update_status_bar(
        lang.get("status_bar_loaded", duration=load_duration)
    )
    
    main_window.show()
    
    # Afficher la fenêtre de debug si configuré
    if config.get("show_debug_window", False):
        main_window.show_debug_window()
        
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
