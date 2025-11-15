"""
Character Actions Manager - Gère toutes les actions sur les personnages
Regroupe: création, suppression, renommage, duplication, ouverture de fiche
"""
import logging
from PySide6.QtWidgets import QMessageBox, QInputDialog, QDialog, QLineEdit
from PySide6.QtCore import Qt

from Functions.character_manager import (
    create_character_data, save_character, delete_character,
    rename_character, duplicate_character, REALMS
)
from Functions.logging_manager import get_logger, log_with_action, LOGGER_CHARACTER
from Functions.language_manager import lang
from Functions.config_manager import config
from UI.dialogs import NewCharacterDialog, CharacterSheetWindow

# Get CHARACTER logger
logger = get_logger(LOGGER_CHARACTER)


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
        seasons = config.get("seasons", ["S3"])
        default_season = config.get("default_season", "S3")
        
        dialog = NewCharacterDialog(
            self.main_window, 
            realms=REALMS, 
            seasons=seasons, 
            default_season=default_season
        )
        
        result = dialog.get_data() if dialog.exec() == QDialog.Accepted else None
        
        if not result:
            log_with_action(logger, "info", "Character creation cancelled by user", action="CREATE")
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
                    print("[BACKUP_TRIGGER] Action: CREATE character - Attempting backup...")
                    self.main_window.backup_manager.trigger_backup_if_needed()
            except Exception as e:
                logging.warning(f"Backup after character creation failed: {e}")
            self.tree_manager.refresh_character_list()
            log_with_action(logger, "info", f"Character '{character_name}' ({race} {class_name}) created successfully", action="CREATE")
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
            log_with_action(logger, "error", f"Failed to create character '{character_name}': {error_message}", action="ERROR")
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
            log_with_action(logger, "info", f"Bulk deletion of {len(checked_ids)} characters initiated", action="DELETE")
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
            log_with_action(logger, "warning", "Attempted to delete character with empty name", action="ERROR")
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
                log_with_action(logger, "info", f"Character deletion cancelled by user for '{char_name}'", action="DELETE")
                return
        
        # Backup BEFORE deletion
        try:
            if hasattr(self.main_window, 'backup_manager'):
                print(f"[BACKUP_TRIGGER] Action: DELETE character '{char_name}' (BEFORE) - Creating backup...")
                self.main_window.backup_manager.backup_characters_force(reason="Delete", character_name=char_name)
        except Exception as e:
            logging.warning(f"Backup before deletion failed: {e}")
                
        success, msg = delete_character(char_name)
        
        if success:
            log_with_action(logger, "info", f"Character '{char_name}' deleted successfully", action="DELETE")
            if confirm:
                self.tree_manager.refresh_character_list()
        else:
            logger.error("f\"Failed to delete character '{char_name}': {msg}\"", extra={"action": "FILE"})
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
            log_with_action(logger, "info", f"Character rename cancelled by user for '{old_name}'", action="RENAME")
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
        
        # Backup BEFORE renaming
        try:
            if hasattr(self.main_window, 'backup_manager'):
                print(f"[BACKUP_TRIGGER] Action: RENAME character '{old_name}' -> '{new_name}' (BEFORE) - Creating backup...")
                self.main_window.backup_manager.backup_characters_force(reason="Rename", character_name=old_name)
        except Exception as e:
            logging.warning(f"Backup before rename failed: {e}")
            
        success, msg = rename_character(old_name, new_name)
        
        if success:
            log_with_action(logger, "info", f"Character renamed from '{old_name}' to '{new_name}'", action="RENAME")
            self.tree_manager.refresh_character_list()
        else:
            error_msg = (
                lang.get(msg, name=new_name) 
                if msg == "char_exists_error" 
                else msg
            )
            logger.error("f\"Failed to rename character from '{old_name}' to '{new_name}': {error_msg}\"", extra={"action": "RENAME"})
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
            log_with_action(logger, "info", f"Character duplication cancelled by user for '{original_name}'", action="DUPLICATE")
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
                    print("[BACKUP_TRIGGER] Action: DUPLICATE character - Attempting backup...")
                    self.main_window.backup_manager.trigger_backup_if_needed()
            except Exception as e:
                logging.warning(f"Backup after character duplication failed: {e}")
            log_with_action(logger, "info", f"Character '{original_name}' duplicated to '{new_name}'", action="DUPLICATE")
            self.tree_manager.refresh_character_list()
        else:
            error_msg = (
                lang.get(msg, name=new_name) 
                if msg == "char_exists_error" 
                else msg
            )
            logger.error("f\"Failed to duplicate character from '{original_name}' to '{new_name}': {error_m...", extra={"action": "DUPLICATE"})
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
            
        # Ne not ouvrir if on clique on the case à cocher
        if index.column() == 0:
            return
        
        # Mapper l'index of the proxy vers the modèle source
        source_index = self.tree_manager.proxy_model.mapToSource(index)
        row = source_index.row()
        name_item = self.tree_manager.model.item(row, 2)
        char_name = name_item.text()
        
        character_data = self.tree_manager.characters_by_id.get(char_name)
        
        if character_data:
            log_with_action(logger, "info", f"Opening character sheet for '{char_name}'", action="UPDATE")
            sheet = CharacterSheetWindow(self.main_window, character_data)
            sheet.exec()
        else:
            log_with_action(logger, "warning", f"Could not find data for character '{char_name}'", action="ERROR")

            
    def open_armor_management(self):
        """Ouvre la gestion des armures pour le personnage sélectionné"""
        try:
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
        except Exception as e:
            import traceback
            error_msg = f"Erreur lors de l'ouverture de la gestion des armures:\n{str(e)}\n\n{traceback.format_exc()}"
            logging.error(error_msg)
            QMessageBox.critical(self.main_window, "Erreur", error_msg)