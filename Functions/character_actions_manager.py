"""
Character Actions Manager - Gère toutes les actions sur les personnages
Regroupe: création, suppression, renommage, duplication, ouverture de fiche
"""
import logging
from PySide6.QtWidgets import QMessageBox, QInputDialog, QLineEdit, QDialog, QApplication
from PySide6.QtCore import Qt

from Functions.character_manager import (
    create_character_data, save_character, delete_character,
    rename_character, duplicate_character, REALMS
)
from Functions.language_manager import lang
from Functions.config_manager import config
from UI.dialogs import NewCharacterDialog, CharacterSheetWindow


class CharacterActionsManager:
    """Gestionnaire des actions sur les personnages"""
    
    def __init__(self, main_window, tree_manager):
        """
        Initialise le CharacterActionsManager
        
        Args:
            main_window: Instance de la fenêtre principale
            tree_manager: Instance du TreeManager pour accéder aux données
        """
        self.main_window = main_window
        self.tree_manager = tree_manager
        
    def create_new_character(self):
        """Ouvre le dialogue de création d'un nouveau personnage"""
        seasons = config.get("seasons", ["S1", "S2", "S3"])
        default_season = config.get("default_season", "S1")
        
        dialog = NewCharacterDialog(
            self.main_window, 
            realms=REALMS, 
            seasons=seasons, 
            default_season=default_season
        )
        
        result = dialog.get_data() if dialog.exec() == QDialog.Accepted else None
        
        if not result:
            logging.info("Character creation cancelled by user")
            return
            
        character_name, realm, season, level, page, guild, race, class_name = result
        
        character_data = create_character_data(
            character_name, realm, season, "Eden", 
            level, page, guild, race, class_name
        )
        
        success, response = save_character(character_data)
        
        if success:
            # Trigger automatic backup after character creation
            try:
                if hasattr(self.main_window, 'backup_manager'):
                    self.main_window.backup_manager.trigger_backup_if_needed()
            except Exception as e:
                logging.warning(f"Backup after character creation failed: {e}")
            self.tree_manager.refresh_character_list()
            logging.info(f"Character '{character_name}' ({race} {class_name}) created")
            QMessageBox.information(
                self.main_window,
                lang.get("success_title"),
                lang.get("char_saved_success", name=character_name)
            )
        else:
            error_message = (
                lang.get(response, name=character_name) 
                if response == "char_exists_error" 
                else response
            )
            logging.error(f"Failed to create character '{character_name}': {error_message}")
            QMessageBox.critical(
                self.main_window,
                lang.get("error_title"),
                error_message
            )
            
    def delete_selected_character(self):
        """Supprime le personnage sélectionné dans la liste"""
        char = self.tree_manager.get_selected_character()
        if not char:
            return
            
        char_name = char.get('name')
        if char_name:
            self._delete_character(char_name, confirm=True)
            
    def delete_checked_characters(self):
        """Supprime tous les personnages cochés (action groupée)"""
        checked_ids = self.tree_manager.get_checked_character_ids()
        
        if not checked_ids:
            QMessageBox.warning(
                self.main_window,
                lang.get("info_title"),
                lang.get("no_characters_selected_warning")
            )
            return
            
        reply = QMessageBox.question(
            self.main_window,
            lang.get("delete_char_confirm_title"),
            lang.get("bulk_delete_confirm_message", count=len(checked_ids)),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logging.info(f"Bulk deletion of {len(checked_ids)} characters initiated")
            for char_name in checked_ids:
                self._delete_character(char_name, confirm=False)
            self.tree_manager.refresh_character_list()
            
    def _delete_character(self, char_name, confirm=True):
        """
        Supprime un personnage
        
        Args:
            char_name: Nom du personnage à supprimer
            confirm: Si True, demande confirmation avant suppression
        """
        if not char_name:
            logging.warning("Attempted to delete character with empty name")
            return
            
        if confirm:
            reply = QMessageBox.question(
                self.main_window,
                lang.get("delete_char_confirm_title"),
                lang.get("delete_char_confirm_message", name=char_name),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
                
        success, msg = delete_character(char_name)
        
        if success:
            logging.info(f"Character '{char_name}' deleted")
            # Trigger automatic backup after deletion
            try:
                if hasattr(self.main_window, 'backup_manager'):
                    self.main_window.backup_manager.trigger_backup_if_needed()
            except Exception as e:
                logging.warning(f"Backup after deletion failed: {e}")
            if confirm:
                self.tree_manager.refresh_character_list()
        else:
            logging.error(f"Failed to delete character '{char_name}': {msg}")
            QMessageBox.critical(
                self.main_window,
                lang.get("error_title"),
                msg
            )
            
    def rename_selected_character(self):
        """Renomme le personnage sélectionné"""
        char = self.tree_manager.get_selected_character()
        if not char:
            return
            
        old_name = char.get('name')
        if not old_name:
            return
            
        new_name, ok = QInputDialog.getText(
            self.main_window,
            lang.get("rename_char_dialog_title", default="Renommer le personnage"),
            lang.get("rename_char_dialog_prompt", default="Nouveau nom :"),
            QLineEdit.Normal,
            old_name
        )
        
        if not ok or not new_name:
            return
            
        new_name = new_name.strip()
        if new_name == old_name:
            return
            
        if not new_name:
            QMessageBox.warning(
                self.main_window,
                lang.get("error_title"),
                lang.get("char_name_empty_error")
            )
            return
            
        success, msg = rename_character(old_name, new_name)
        
        if success:
            # Trigger automatic backup after renaming
            try:
                if hasattr(self.main_window, 'backup_manager'):
                    self.main_window.backup_manager.trigger_backup_if_needed()
            except Exception as e:
                logging.warning(f"Backup after character rename failed: {e}")
            self.tree_manager.refresh_character_list()
        else:
            error_msg = (
                lang.get(msg, name=new_name) 
                if msg == "char_exists_error" 
                else msg
            )
            QMessageBox.critical(
                self.main_window,
                lang.get("error_title"),
                error_msg
            )
            
    def duplicate_selected_character(self):
        """Duplique le personnage sélectionné"""
        char = self.tree_manager.get_selected_character()
        if not char:
            return
            
        original_name = char.get('name')
        if not original_name:
            return
            
        new_name, ok = QInputDialog.getText(
            self.main_window,
            lang.get("duplicate_char_dialog_title", default="Dupliquer le personnage"),
            lang.get("duplicate_char_dialog_prompt", default="Nom du nouveau personnage :"),
            QLineEdit.Normal,
            f"{original_name}_copy"
        )
        
        if not ok or not new_name:
            return
            
        new_name = new_name.strip()
        if not new_name:
            QMessageBox.warning(
                self.main_window,
                lang.get("error_title"),
                lang.get("char_name_empty_error")
            )
            return
            
        success, msg = duplicate_character(char, new_name)
        
        if success:
            # Trigger automatic backup after duplication
            try:
                if hasattr(self.main_window, 'backup_manager'):
                    self.main_window.backup_manager.trigger_backup_if_needed()
            except Exception as e:
                logging.warning(f"Backup after character duplication failed: {e}")
            self.tree_manager.refresh_character_list()
        else:
            error_msg = (
                lang.get(msg, name=new_name) 
                if msg == "char_exists_error" 
                else msg
            )
            QMessageBox.critical(
                self.main_window,
                lang.get("error_title"),
                error_msg
            )
            
    def open_character_sheet(self, index):
        """
        Ouvre la fiche détaillée d'un personnage
        
        Args:
            index: QModelIndex du personnage dans la vue
        """
        if not index.isValid():
            return
            
        # Ne pas ouvrir si on clique sur la case à cocher
        if index.column() == 0:
            return
            
        row = index.row()
        name_item = self.tree_manager.model.item(row, 2)
        char_name = name_item.text()
        
        character_data = self.tree_manager.characters_by_id.get(char_name)
        
        if character_data:
            logging.info(f"Opening character sheet for '{char_name}'")
            sheet = CharacterSheetWindow(self.main_window, character_data)
            sheet.exec()
        else:
            logging.warning(f"Could not find data for character '{char_name}'")
            
    def open_armor_management(self):
        """Ouvre la gestion des armures pour le personnage sélectionné"""
        char = self.tree_manager.get_selected_character()
        
        if not char:
            QMessageBox.information(
                self.main_window,
                lang.get("info_title", default="Information"),
                "Veuillez sélectionner un personnage dans la liste pour accéder à la gestion de ses armures.\n\n"
                "Vous pouvez aussi ouvrir la fiche du personnage et cliquer sur '📁 Gérer les armures'."
            )
            return
            
        character_id = char.get('id', '')
        if not character_id:
            QMessageBox.warning(
                self.main_window,
                "Erreur",
                "Impossible de déterminer l'ID du personnage."
            )
            return
            
        from UI.dialogs import ArmorManagementDialog
        dialog = ArmorManagementDialog(self.main_window, character_id)
        dialog.exec()
