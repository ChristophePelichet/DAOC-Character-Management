"""
UI Manager - Gère la création et la configuration des éléments d'interface utilisateur
Extrait de main.py pour réduire la complexité
"""
import logging
from PySide6.QtWidgets import (
    QMenu, QMessageBox, QGroupBox, QHBoxLayout, QVBoxLayout, QComboBox, QPushButton, QStatusBar, QLabel
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QThread, Signal

from Functions.language_manager import lang


class EdenStatusThread(QThread):
    """Thread pour vérifier le statut de connexion Eden en arrière-plan"""
    status_updated = Signal(bool, str)  # (accessible, message)
    
    def __init__(self, cookie_manager):
        super().__init__()
        self.cookie_manager = cookie_manager
    
    def run(self):
        """Vérifie le statut de connexion"""
        if not self.cookie_manager.cookie_exists():
            self.status_updated.emit(False, "Aucun cookie")
            return
        
        info = self.cookie_manager.get_cookie_info()
        if not info or not info.get('is_valid'):
            self.status_updated.emit(False, "Cookies expirés")
            return
        
        # Test de connexion
        result = self.cookie_manager.test_eden_connection()
        self.status_updated.emit(result['accessible'], result['message'])


class UIManager:
    """Gestionnaire centralisé des éléments d'interface utilisateur"""
    
    def __init__(self, main_window):
        """
        Initialise le UIManager
        
        Args:
            main_window: Instance de la fenêtre principale CharacterApp
        """
        self.main_window = main_window
        self.context_menu = None
        self.eden_status_label = None
        self.eden_status_thread = None
        
    def create_menu_bar(self):
        """Crée la barre de menus avec Fichier, Actions, Affichage, Aide"""
        menubar = self.main_window.menuBar()
        menubar.clear()
        
        # Menu Fichier
        file_menu = menubar.addMenu(lang.get("menu_file"))
        
        new_char_action = QAction(lang.get("menu_file_new_character"), self.main_window)
        new_char_action.triggered.connect(self.main_window.create_new_character)
        file_menu.addAction(new_char_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction(lang.get("menu_file_settings"), self.main_window)
        settings_action.triggered.connect(self.main_window.open_configuration)
        file_menu.addAction(settings_action)
        
        # Menu Affichage
        view_menu = menubar.addMenu(lang.get("menu_view"))
        
        columns_action = QAction(lang.get("menu_view_columns"), self.main_window)
        columns_action.triggered.connect(self.main_window.open_columns_configuration)
        view_menu.addAction(columns_action)
        
        # Menu Outils
        tools_menu = menubar.addMenu(lang.get("tools_menu"))
        
        backup_action = QAction(lang.get("backup_menu_item"), self.main_window)
        backup_action.triggered.connect(self.main_window.open_backup_settings)
        tools_menu.addAction(backup_action)
        
        # Menu Aide
        help_menu = menubar.addMenu(lang.get("menu_help"))
        
        # Sous-menu Documentation
        doc_menu = QMenu(lang.get("menu_help_documentation"), self.main_window)
        help_menu.addMenu(doc_menu)
        
        help_create_char_action = QAction(lang.get("menu_help_create_character"), self.main_window)
        help_create_char_action.triggered.connect(self.main_window.show_help_create_character)
        doc_menu.addAction(help_create_char_action)
        
        help_edit_char_action = QAction(lang.get("menu_help_edit_character"), self.main_window)
        help_edit_char_action.triggered.connect(self.main_window.show_help_edit_character)
        doc_menu.addAction(help_edit_char_action)
        
        help_delete_char_action = QAction(lang.get("menu_help_delete_character"), self.main_window)
        help_delete_char_action.triggered.connect(self.main_window.show_help_delete_character)
        doc_menu.addAction(help_delete_char_action)
        
        help_menu.addSeparator()
        
        eden_debug_action = QAction(lang.get("menu_help_eden_debug"), self.main_window)
        eden_debug_action.triggered.connect(self.main_window.open_eden_debug)
        help_menu.addAction(eden_debug_action)
        
        # Vérifier la structure des fichiers JSON
        check_json_action = QAction("🔧 Vérifier la structure des fichiers", self.main_window)
        check_json_action.triggered.connect(self.main_window.check_json_structures)
        help_menu.addAction(check_json_action)
        
        help_menu.addSeparator()
        
        # Section À propos (en dernier)
        about_action = QAction(lang.get("menu_help_about"), self.main_window)
        about_action.triggered.connect(self.main_window.show_about_dialog)
        help_menu.addAction(about_action)
        
    def create_context_menu(self):
        """Crée le menu contextuel (clic droit) pour la liste des personnages"""
        self.context_menu = QMenu(self.main_window)

        # Renommer
        rename_action = self.context_menu.addAction(lang.get("context_menu_rename", default="Renommer"))
        rename_action.triggered.connect(self.main_window.rename_selected_character)

        # Dupliquer
        duplicate_action = self.context_menu.addAction(lang.get("context_menu_duplicate", default="Dupliquer"))
        duplicate_action.triggered.connect(self.main_window.duplicate_selected_character)

        self.context_menu.addSeparator()
        
        # Mettre à jour depuis Herald
        update_action = self.context_menu.addAction(lang.get("context_menu_update_from_herald", default="🔄 Mettre à jour depuis Herald"))
        update_action.triggered.connect(self.main_window.update_character_from_herald)

        self.context_menu.addSeparator()

        # Gestion des armures
        armor_action = self.context_menu.addAction(lang.get("context_menu_armor_management", default="Gestion des armures"))
        armor_action.triggered.connect(self.main_window.open_armor_management_global)

        self.context_menu.addSeparator()

        # Supprimer
        delete_action = self.context_menu.addAction(lang.get("context_menu_delete", default="Supprimer"))
        delete_action.triggered.connect(self.main_window.delete_selected_character)
        
        return self.context_menu
        
    def create_delete_button(self, parent_layout):
        """Crée le bouton de suppression de la sélection en bas de la liste"""
        delete_button_layout = QHBoxLayout()
        
        delete_button = QPushButton(lang.get("bulk_action_delete", default="Supprimer la sélection"))
        delete_button.clicked.connect(self.main_window.execute_bulk_action)
        delete_button_layout.addWidget(delete_button)
        
        delete_button_layout.addStretch()  # Aligné à gauche
        
        parent_layout.addLayout(delete_button_layout)
    
    def create_eden_status_bar(self, parent_layout):
        """Crée la barre de statut de connexion Eden et la section Monnaie"""
        # Conteneur horizontal pour deux colonnes
        container_layout = QHBoxLayout()
        
        # ===== SECTION GAUCHE : Status Herald Eden (réduite de moitié) =====
        status_group = QGroupBox("Statut Eden Herald")
        status_layout = QHBoxLayout()
        status_layout.setSpacing(5)
        status_layout.setContentsMargins(5, 5, 5, 5)
        
        # Label de statut
        self.eden_status_label = QLabel("⏳ Vérification en cours...")
        self.eden_status_label.setStyleSheet("padding: 3px; font-size: 12px;")
        self.eden_status_label.setMinimumHeight(35)
        status_layout.addWidget(self.eden_status_label, 1)
        
        # Boutons réduits alignés horizontalement - tous la même taille
        self.refresh_button = QPushButton("🔄 Actualiser")
        self.refresh_button.clicked.connect(self.check_eden_status)
        self.refresh_button.setEnabled(False)
        self.refresh_button.setMaximumWidth(750)
        self.refresh_button.setMinimumHeight(35)
        self.refresh_button.setStyleSheet("font-size: 12px; padding: 3px;")
        status_layout.addWidget(self.refresh_button)
        
        self.search_button = QPushButton("🔍 Recherche")
        self.search_button.clicked.connect(self.main_window.open_herald_search)
        self.search_button.setEnabled(False)
        self.search_button.setMaximumWidth(750)
        self.search_button.setMinimumHeight(35)
        self.search_button.setStyleSheet("font-size: 12px; padding: 3px;")
        status_layout.addWidget(self.search_button)
        
        manage_button = QPushButton("⚙️ Gérer")
        manage_button.clicked.connect(self.main_window.open_cookie_manager)
        manage_button.setMaximumWidth(750)
        manage_button.setMinimumHeight(35)
        manage_button.setStyleSheet("font-size: 12px; padding: 3px 15px;")
        status_layout.addWidget(manage_button)
        
        status_group.setLayout(status_layout)
        container_layout.addWidget(status_group, 1)  # Stretch = 1
        
        # ===== SECTION DROITE : Monnaie (feature à venir) =====
        currency_group = QGroupBox("Monnaie")
        currency_layout = QHBoxLayout()
        currency_layout.setContentsMargins(5, 5, 5, 5)
        
        currency_label = QLabel("🔜 Feature à venir")
        currency_label.setStyleSheet("padding: 3px; text-align: center; font-size: 12px;")
        currency_label.setAlignment(Qt.AlignCenter)
        currency_label.setMinimumHeight(35)
        currency_layout.addWidget(currency_label)
        
        currency_group.setLayout(currency_layout)
        container_layout.addWidget(currency_group, 1)  # Stretch = 1
        
        # Ajouter le conteneur à la layout principale
        parent_layout.addLayout(container_layout)
        
        # Lancer la vérification initiale
        self.check_eden_status()
    
    def check_eden_status(self):
        """Vérifie le statut de connexion Eden en arrière-plan"""
        # Arrêter un thread en cours si existant
        if self.eden_status_thread and self.eden_status_thread.isRunning():
            self.eden_status_thread.quit()
            self.eden_status_thread.wait()
        
        # Afficher le statut de chargement et désactiver les boutons
        self.eden_status_label.setText("⏳ Vérification en cours...")
        self.eden_status_label.setStyleSheet("padding: 5px; color: gray;")
        self.refresh_button.setEnabled(False)
        self.search_button.setEnabled(False)
        
        # Créer le gestionnaire de cookies
        from Functions.cookie_manager import CookieManager
        cookie_manager = CookieManager()
        
        # Lancer le thread de vérification
        self.eden_status_thread = EdenStatusThread(cookie_manager)
        self.eden_status_thread.status_updated.connect(self.update_eden_status)
        self.eden_status_thread.start()
    
    def update_eden_status(self, accessible, message):
        """Met à jour l'affichage du statut Eden"""
        if accessible:
            self.eden_status_label.setText(f"✅ Herald accessible")
            self.eden_status_label.setStyleSheet("padding: 5px; color: green; font-weight: bold;")
            # Réactiver les boutons - Herald est accessible
            self.refresh_button.setEnabled(True)
            self.search_button.setEnabled(True)
        else:
            self.eden_status_label.setText(f"❌ {message}")
            self.eden_status_label.setStyleSheet("padding: 5px; color: red;")
            
            # Griser les boutons si pas de cookies
            if "Aucun cookie" in message:
                self.refresh_button.setEnabled(False)
                self.search_button.setEnabled(False)
            else:
                # Si c'est juste une erreur de connexion, garder les boutons activés
                self.refresh_button.setEnabled(True)
                self.search_button.setEnabled(True)
        
        
    def create_status_bar(self):
        """Crée la barre de statut en bas de la fenêtre"""
        status_bar = QStatusBar()
        self.main_window.setStatusBar(status_bar)
        
        status_label = QLabel("Initialisation...")
        status_bar.addWidget(status_label)
        
        self.main_window.status_bar = status_bar
        self.main_window.status_label = status_label
        
        return status_bar, status_label
        
    def show_context_menu(self, position):
        """Affiche le menu contextuel à la position spécifiée"""
        index = self.main_window.character_tree.indexAt(position)
        if index.isValid():
            # Sélectionner la ligne cliquée avant d'afficher le menu
            self.main_window.character_tree.setCurrentIndex(index)
            self.context_menu.exec(self.main_window.character_tree.viewport().mapToGlobal(position))
            
    def update_status_bar(self, message):
        """Met à jour le texte de la barre de statut"""
        if hasattr(self.main_window, 'status_label'):
            self.main_window.status_label.setText(message)
            
    def show_about_dialog(self, app_name, app_version):
        """Affiche la boîte de dialogue 'À propos'"""
        title = lang.get("about_dialog_title", app_name=app_name)
        message = lang.get("about_dialog_content", app_name=app_name, version=app_version)
        QMessageBox.about(self.main_window, title, message)
        
    def retranslate_ui(self):
        """Met à jour toutes les traductions de l'interface"""
        self.main_window.setWindowTitle(lang.get("window_title"))
        self.create_menu_bar()
        self.create_context_menu()
