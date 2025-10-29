"""
Tree Manager - Gère l'affichage et les interactions avec la liste des personnages
Extrait de main.py pour améliorer la maintenabilité
"""
import logging
from PySide6.QtWidgets import QHeaderView, QMessageBox, QInputDialog, QLineEdit, QTreeView
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PySide6.QtCore import Qt, QByteArray

from Functions.character_manager import (
    get_all_characters, REALM_ICONS, delete_character, 
    rename_character, duplicate_character
)
from Functions.language_manager import lang
from Functions.config_manager import config
from Functions.logging_manager import get_img_dir


class TreeManager:
    """Gestionnaire de la vue arborescente des personnages"""
    
    def __init__(self, main_window, tree_view, data_manager):
        """
        Initialise le TreeManager
        
        Args:
            main_window: Instance de la fenêtre principale
            tree_view: Widget QTreeView à gérer
            data_manager: Instance de DataManager pour les données de jeu
        """
        self.main_window = main_window
        self.tree_view = tree_view
        self.data_manager = data_manager
        self.model = QStandardItemModel()
        self.tree_view.setModel(self.model)
        self.characters_by_id = {}
        self.realm_icons = {}
        
        # Configuration initiale du tree view
        self._configure_tree_view()
        self._load_realm_icons()
        
    def _configure_tree_view(self):
        """Configure l'apparence et le comportement du tree view"""
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setRootIsDecorated(False)
        self.tree_view.setSortingEnabled(True)
        
        # Style pour les lignes de grille
        grid_color = "#d6d6d6"
        text_color = "#000000"
        selected_text_color = "#ffffff"
        selected_bg_color = "#0078d4"
        
        self.tree_view.setStyleSheet(f"""
            QTreeView::item {{
                border-right: 1px solid {grid_color};
                color: {text_color};
            }}
            QTreeView::item:selected {{
                color: {selected_text_color};
                background-color: {selected_bg_color};
            }}
            QTreeView {{
                border-bottom: 1px solid {grid_color};
            }}
        """)
        
    def _load_realm_icons(self):
        """Charge les icônes des royaumes"""
        img_dir = get_img_dir()
        
        if not REALM_ICONS:
            logging.warning("REALM_ICONS dictionary is empty")
            return
            
        for realm, icon_filename in REALM_ICONS.items():
            try:
                icon_path = f"{img_dir}/{icon_filename}"
                icon = QIcon(icon_path)
                self.realm_icons[realm] = icon
                logging.debug(f"Icon loaded for {realm}: {icon_path}")
            except Exception as e:
                logging.warning(f"Error loading icon for {realm}: {e}")
                self.realm_icons[realm] = None
                
    def refresh_character_list(self):
        """Rafraîchit la liste complète des personnages"""
        logging.debug("Refreshing character list")
        
        self.model.clear()
        self.characters_by_id.clear()
        
        # Définir les en-têtes
        headers = [
            lang.get("column_selection"),
            lang.get("column_realm"),
            lang.get("column_name"),
            lang.get("column_level"),
            lang.get("column_realm_rank", default="Rang"),
            lang.get("column_realm_title", default="Titre"),
            lang.get("column_guild", default="Guilde"),
            lang.get("column_page", default="Page"),
            lang.get("column_server", default="Serveur"),
            lang.get("column_class", default="Classe"),
            lang.get("column_race", default="Race")
        ]
        self.model.setHorizontalHeaderLabels(headers)
        
        # Centrer les en-têtes de certaines colonnes
        for col_index in [1, 2, 5, 6, 8, 9]:  # Realm, Season, Level, Page, RR, Title
            header_item = self.model.horizontalHeaderItem(col_index)
            if header_item:
                header_item.setTextAlignment(Qt.AlignCenter)
        
        # Charger les personnages
        characters = get_all_characters()
        logging.debug(f"Loading {len(characters)} character(s)")
        
        for char in characters:
            self._add_character_row(char)
        
        # Restaurer l'état de l'en-tête
        self._restore_header_state()
        
        # Appliquer la visibilité des colonnes
        self.apply_column_visibility()
        
        # Appliquer le mode de redimensionnement
        manual_resize = config.get("manual_column_resize", False)
        self.apply_column_resize_mode(manual_resize)
        
        # Connecter le signal de changement pour le compteur de sélection
        self.model.dataChanged.connect(self.main_window.update_selection_count)
        
    def _add_character_row(self, char):
        """Ajoute une ligne de personnage au modèle"""
        realm_name = char.get('realm', 'N/A')
        char_id = char.get('id')
        self.characters_by_id[char_id] = char
        
        # Icône de royaume
        item_realm = QStandardItem()
        realm_icon = self.realm_icons.get(realm_name)
        if realm_icon:
            item_realm.setData(realm_name, Qt.UserRole + 1)  # Pour le tri
            item_realm.setIcon(realm_icon)
        item_realm.setData(char_id, Qt.UserRole)
        item_realm.setTextAlignment(Qt.AlignCenter)
        item_realm.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        
        # Autres colonnes
        item_name = QStandardItem(char.get('name', 'N/A'))
        item_name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        
        item_level = QStandardItem(str(char.get('level', 1)))
        item_level.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_level.setTextAlignment(Qt.AlignCenter)
        
        # Calcul du rang et titre de royaume
        realm_points = char.get('realm_points', 0)
        realm_rank_level = '1L1'
        realm_title = ''
        
        rank_info = self.data_manager.get_realm_rank_info(realm_name, realm_points)
        if rank_info:
            realm_rank_level = rank_info['level']
            realm_title = rank_info['title']
        
        item_realm_rank = QStandardItem(str(realm_rank_level))
        item_realm_rank.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_realm_rank.setTextAlignment(Qt.AlignCenter)
        
        item_realm_title = QStandardItem(realm_title)
        item_realm_title.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_realm_title.setTextAlignment(Qt.AlignCenter)
        item_realm_title.setData(realm_name, Qt.UserRole)
        
        item_guild = QStandardItem(char.get('guild', ''))
        item_guild.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        
        item_page = QStandardItem(str(char.get('page', 1)))
        item_page.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_page.setTextAlignment(Qt.AlignCenter)
        
        item_server = QStandardItem(char.get('server', 'Eden'))
        item_server.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_server.setTextAlignment(Qt.AlignCenter)
        
        item_class = QStandardItem(char.get('class', ''))
        item_class.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_class.setTextAlignment(Qt.AlignCenter)
        font = item_class.font()
        font.setBold(False)
        item_class.setFont(font)
        
        item_race = QStandardItem(char.get('race', ''))
        item_race.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_race.setTextAlignment(Qt.AlignCenter)
        
        # Case à cocher pour la sélection
        item_selection = QStandardItem()
        item_selection.setCheckable(True)
        item_selection.setCheckState(Qt.Unchecked)
        item_selection.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        
        # Ordre: Selection, Realm, Name, Level, Rank, Title, Guild, Page, Server, Class, Race
        row_items = [
            item_selection, item_realm, item_name, item_level,
            item_realm_rank, item_realm_title, item_guild, item_page,
            item_server, item_class, item_race
        ]
        self.model.appendRow(row_items)
        
    def _restore_header_state(self):
        """Restaure l'état sauvegardé de l'en-tête (ordre et taille des colonnes)"""
        header_state_b64 = config.get("tree_view_header_state")
        if header_state_b64:
            try:
                header_state = QByteArray.fromBase64(header_state_b64.encode('ascii'))
                if self.tree_view.header().restoreState(header_state):
                    logging.info("QTreeView header state restored")
                else:
                    logging.warning("Could not restore QTreeView header state")
            except Exception as e:
                logging.error(f"Error restoring header state: {e}")
                
    def apply_column_visibility(self):
        """Applique les paramètres de visibilité des colonnes"""
        visibility_config = config.get("column_visibility", {})
        
        # Visibilité par défaut
        default_visibility = {
            "selection": True, "realm": True, "name": True, "level": True,
            "page": True, "guild": True, "realm_rank": True, "realm_title": True,
            "server": False, "class": True, "race": False
        }
        
        # Mapping colonnes -> indices
        column_map = {
            "selection": 0, "realm": 1, "name": 2, "level": 3,
            "realm_rank": 4, "realm_title": 5, "guild": 6, "page": 7,
            "server": 8, "class": 9, "race": 10
        }
        
        # Appliquer la visibilité
        for key, index in column_map.items():
            is_visible = visibility_config.get(key, default_visibility.get(key, True))
            self.tree_view.setColumnHidden(index, not is_visible)
            
            # Redimensionner les colonnes visibles (sauf Name)
            if is_visible and index != 2:
                self.tree_view.resizeColumnToContents(index)
        
        # Réappliquer Stretch sur la colonne Name si visible
        if visibility_config.get("name", True):
            self.tree_view.header().setSectionResizeMode(2, QHeaderView.Stretch)
            
    def apply_column_resize_mode(self, manual_mode=False):
        """Applique le mode de redimensionnement des colonnes"""
        header = self.tree_view.header()
        
        if manual_mode:
            header.setSectionResizeMode(QHeaderView.Interactive)
            logging.debug("Column resize mode: Manual")
        else:
            for i in range(11):
                if i == 2:  # Colonne Name
                    header.setSectionResizeMode(i, QHeaderView.Stretch)
                else:
                    header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            logging.debug("Column resize mode: Automatic")
            
    def save_header_state(self):
        """Sauvegarde l'état actuel de l'en-tête"""
        header_state = self.tree_view.header().saveState()
        header_state_b64 = header_state.toBase64().data().decode('ascii')
        config.set("tree_view_header_state", header_state_b64)
        logging.debug("Header state saved")
        
    def get_checked_character_ids(self):
        """Retourne la liste des IDs des personnages cochés"""
        checked_ids = []
        for row in range(self.model.rowCount()):
            selection_item = self.model.item(row, 0)
            if selection_item and selection_item.checkState() == Qt.Checked:
                name_item = self.model.item(row, 2)
                char_name = name_item.text()
                if char_name:
                    checked_ids.append(char_name)
        return checked_ids
        
    def select_all_characters(self):
        """Coche tous les personnages"""
        for row in range(self.model.rowCount()):
            selection_item = self.model.item(row, 0)
            if selection_item:
                selection_item.setCheckState(Qt.Checked)
        logging.debug(f"All {self.model.rowCount()} characters selected")
        
    def deselect_all_characters(self):
        """Décoche tous les personnages"""
        for row in range(self.model.rowCount()):
            selection_item = self.model.item(row, 0)
            if selection_item:
                selection_item.setCheckState(Qt.Unchecked)
        logging.debug("All characters deselected")
        
    def get_selected_character(self):
        """Retourne les données du personnage sélectionné"""
        indexes = self.tree_view.selectedIndexes()
        if not indexes:
            return None
            
        row = indexes[0].row()
        name_item = self.model.item(row, 2)
        char_name = name_item.text()
        
        return self.characters_by_id.get(char_name)
