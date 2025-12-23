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
from UI.ui_armory_all_templates import UIArmoryAllTemplates


class EdenStatusThread(QThread):
    """Thread pour vérifier le statut de connexion Eden en arrière-plan"""
    status_updated = Signal(bool, str)  # (accessible, message)
    
    def __init__(self, cookie_manager):
        super().__init__()
        self.cookie_manager = cookie_manager
    
    def run(self):
        """Vérifie le statut de connexion"""
        try:
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
            
        except Exception as e:
            # Log and émettre un signal d'erreur au lieu of crasher
            import logging
            import traceback
            logging.error(f"EdenStatusThread crash: {e}\n{traceback.format_exc()}")
            self.status_updated.emit(False, f"Erreur: {str(e)[:50]}")


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
        """Crée la barre de menus avec Fichier, Outils, Aide"""
        menubar = self.main_window.menuBar()
        menubar.clear()
        
        # Menu Fichier
        file_menu = menubar.addMenu(lang.get("menu_file"))
        
        new_char_action = QAction(lang.get("menu_file_new_character"), self.main_window)
        new_char_action.setShortcut("Ctrl+N")
        new_char_action.triggered.connect(self.main_window.create_new_character)
        file_menu.addAction(new_char_action)
        
        file_menu.addSeparator()
        
        # Recherche Herald
        search_herald_action = QAction(lang.get("menu_file_search_herald", default="🔍 Rechercher sur Herald"), self.main_window)
        search_herald_action.setShortcut("Ctrl+F")
        search_herald_action.triggered.connect(self.main_window.open_herald_search_with_validation)
        file_menu.addAction(search_herald_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction(lang.get("menu_file_settings"), self.main_window)
        settings_action.setShortcut("Ctrl+S")
        settings_action.triggered.connect(self.main_window.open_configuration)
        file_menu.addAction(settings_action)
        
        # Note: Backup settings moved to Settings > Backup section
        
        # Menu Outils
        tools_menu = menubar.addMenu(lang.get("menu.tools.label", default="Outils"))
        
        # Armurerie - Browse all templates
        armory_action = QAction(lang.get("menu.tools.armory", default="Armurerie"), self.main_window)
        armory_action.triggered.connect(self._open_all_templates_window)
        tools_menu.addAction(armory_action)
        
        # Menu Aide
        help_menu = menubar.addMenu(lang.get("menu_help"))
        
        # Lien direct vers Wiki Documentation (F1)
        wiki_doc_action = QAction(lang.get("menu_help_documentation"), self.main_window)
        wiki_doc_action.setShortcut("F1")
        wiki_doc_action.triggered.connect(self._open_wiki_documentation)
        help_menu.addAction(wiki_doc_action)
        
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
        
        # Mettre à jour depuis Herald - stocker comme attribut pour pouvoir désactiver
        self.update_from_herald_action = self.context_menu.addAction(lang.get("context_menu_update_from_herald", default="🔄 Mettre à jour depuis Herald"))
        self.update_from_herald_action.triggered.connect(self.main_window.update_character_from_herald)
        # Store the original text for later restoration
        self.update_from_herald_action_text = lang.get("context_menu_update_from_herald", default="🔄 Mettre à jour depuis Herald")

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
        """Crée les boutons d'action groupée en bas de la liste"""
        action_button_layout = QHBoxLayout()
        
        # Bouton "Tout sélectionner"
        select_all_text = lang.get("menu.bulk_actions.select_all", default="✓ Select All")
        logging.debug(f"Creating select_all_button with text: {select_all_text}")
        self.select_all_button = QPushButton(select_all_text)
        self.select_all_button.clicked.connect(self.main_window.select_all_characters)
        action_button_layout.addWidget(self.select_all_button)
        
        # Bouton "Tout désélectionner"
        deselect_all_text = lang.get("menu.bulk_actions.deselect_all", default="✗ Deselect All")
        logging.debug(f"Creating deselect_all_button with text: {deselect_all_text}")
        self.deselect_all_button = QPushButton(deselect_all_text)
        self.deselect_all_button.clicked.connect(self.main_window.deselect_all_characters)
        action_button_layout.addWidget(self.deselect_all_button)
        
        # Bouton "Supprimer la sélection"
        delete_text = lang.get("menu.bulk_actions.delete", default="Delete Selection")
        logging.debug(f"Creating delete_button with text: {delete_text}")
        self.delete_button = QPushButton(delete_text)
        self.delete_button.clicked.connect(self.main_window.execute_bulk_action)
        action_button_layout.addWidget(self.delete_button)
        
        action_button_layout.addStretch()  # Aligné à gauche
        
        parent_layout.addLayout(action_button_layout)
    
    def create_eden_status_bar(self, parent_layout):
        """Crée la barre de statut de connexion Eden et la section Informations"""
        from Functions.language_manager import lang
        
        # Conteneur horizontal pour deux colonnes
        container_layout = QHBoxLayout()
        
        # ===== SECTION GAUCHE : Status Herald Eden (réduite of moitié) =====
        self.status_group = QGroupBox("Statut Eden Herald")
        status_layout = QHBoxLayout()
        status_layout.setSpacing(5)
        status_layout.setContentsMargins(5, 5, 5, 5)
        
        # Label de statut
        self.eden_status_label = QLabel("⏳ Vérification en cours...")
        self.eden_status_label.setStyleSheet("padding: 3px; font-size: 12px;")
        self.eden_status_label.setMinimumHeight(35)
        status_layout.addWidget(self.eden_status_label, 1)
        
        # Boutons réduits alignés horizontalement - all the même taille
        self.refresh_button = QPushButton(lang.get("buttons.eden_refresh"))
        self.refresh_button.clicked.connect(self.check_eden_status)
        self.refresh_button.setEnabled(False)
        self.refresh_button.setMaximumWidth(750)
        self.refresh_button.setMinimumHeight(35)
        self.refresh_button.setStyleSheet("font-size: 12px; padding: 3px;")
        status_layout.addWidget(self.refresh_button)
        
        self.search_button = QPushButton(lang.get("buttons.eden_search"))
        self.search_button.clicked.connect(self.main_window.open_herald_search)
        self.search_button.setEnabled(False)
        self.search_button.setMaximumWidth(750)
        self.search_button.setMinimumHeight(35)
        self.search_button.setStyleSheet("font-size: 12px; padding: 3px;")
        status_layout.addWidget(self.search_button)
        
        manage_button = QPushButton(lang.get("buttons.eden_manage"))
        manage_button.clicked.connect(self.main_window.open_cookie_manager)
        manage_button.setMaximumWidth(750)
        manage_button.setMinimumHeight(35)
        manage_button.setStyleSheet("font-size: 12px; padding: 3px 15px;")
        status_layout.addWidget(manage_button)
        
        self.status_group.setLayout(status_layout)
        container_layout.addWidget(self.status_group, 1)  # Stretch = 1
        
        # ===== SECTION DROITE : Informations (Version) =====
        self.info_group = QGroupBox(lang.get("info_section_title"))
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(10, 10, 10, 10)
        info_layout.setSpacing(5)
        
        # Version actuelle
        current_layout = QHBoxLayout()
        self.version_current_title_label = QLabel(lang.get("version_check_current"))
        self.version_current_title_label.setStyleSheet("font-size: 11px;")
        current_layout.addWidget(self.version_current_title_label)
        
        self.version_current_label = QLabel("—")
        self.version_current_label.setStyleSheet("font-size: 11px; font-weight: bold;")
        current_layout.addWidget(self.version_current_label)
        current_layout.addStretch()
        
        info_layout.addLayout(current_layout)
        
        # Dernière version
        latest_layout = QHBoxLayout()
        self.version_latest_title_label = QLabel(lang.get("version_check_latest"))
        self.version_latest_title_label.setStyleSheet("font-size: 11px;")
        latest_layout.addWidget(self.version_latest_title_label)
        
        self.version_latest_label = QLabel("—")
        self.version_latest_label.setStyleSheet("font-size: 11px; font-weight: bold;")
        latest_layout.addWidget(self.version_latest_label)
        latest_layout.addStretch()
        
        info_layout.addLayout(latest_layout)
        
        # Status et bouton de vérification (sur la même ligne)
        status_button_layout = QHBoxLayout()
        
        self.version_status_label = QLabel("⏳ Vérification...")
        self.version_status_label.setStyleSheet("font-size: 11px; font-style: italic; color: gray;")
        status_button_layout.addWidget(self.version_status_label)
        
        # Download link (hidden by default)
        self.version_download_link = QLabel()
        self.version_download_link.setStyleSheet("font-size: 11px;")
        self.version_download_link.setOpenExternalLinks(True)
        self.version_download_link.hide()
        status_button_layout.addWidget(self.version_download_link)
        
        self.version_check_button = QPushButton(lang.get("version_check_button"))
        self.version_check_button.setStyleSheet("""
            QPushButton {
                font-size: 10px;
                padding: 3px 8px;
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.version_check_button.clicked.connect(self._start_version_check)
        status_button_layout.addWidget(self.version_check_button)
        status_button_layout.addStretch()
        
        info_layout.addLayout(status_button_layout)
        
        self.info_group.setLayout(info_layout)
        container_layout.addWidget(self.info_group, 1)  # Stretch = 1
        
        # Ajouter the conteneur à the layout principale
        parent_layout.addLayout(container_layout)
        
        # Lancer the Checking initiale
        self.check_eden_status()
        
        # Lancer la vérification de version en arrière-plan
        self._start_version_check()
    
    def _start_version_check(self):
        """Démarre la vérification de version en arrière-plan"""
        from PySide6.QtCore import QThread, Signal
        from Functions.version_checker import check_for_updates
        from Functions.language_manager import lang
        import os
        
        # Désactiver le bouton pendant la vérification
        self.version_check_button.setEnabled(False)
        self.version_check_button.setText(lang.get("version_check_button_checking"))
        self.version_status_label.setText("⏳ Vérification...")
        self.version_status_label.setStyleSheet("font-size: 11px; font-style: italic; color: gray;")
        
        class VersionCheckThread(QThread):
            version_checked = Signal(dict)
            
            def run(self):
                try:
                    # Use version from code constant, not from file
                    from Functions.version import __version__
                    current_version = __version__
                    
                    result = check_for_updates(current_version)
                    self.version_checked.emit(result)
                except Exception as e:
                    self.version_checked.emit({
                        'update_available': False,
                        'current_version': '?',
                        'latest_version': None,
                        'error': str(e)
                    })
        
        self.version_thread = VersionCheckThread()
        self.version_thread.version_checked.connect(self._on_version_checked)
        self.version_thread.start()
    
    def _on_version_checked(self, result):
        """Gère le résultat de la vérification de version"""
        from Functions.language_manager import lang
        
        current_ver = result['current_version']
        latest_ver = result['latest_version']
        
        # Réactiver le bouton
        self.version_check_button.setEnabled(True)
        self.version_check_button.setText(lang.get("version_check_button"))
        
        if result['error']:
            # Erreur pendant la vérification
            self.version_current_label.setText(current_ver)
            self.version_current_label.setStyleSheet("font-size: 11px; font-weight: bold;")
            self.version_latest_label.setText("—")
            self.version_status_label.setText(lang.get("version_check_error"))
            self.version_status_label.setStyleSheet("font-size: 11px; font-style: italic; color: orange;")
            self.version_status_label.show()
            self.version_download_link.hide()
        elif result['update_available']:
            # Mise à jour disponible - croix rouge à côté de la version actuelle
            self.version_current_label.setText(f"✗ {current_ver}")
            self.version_current_label.setStyleSheet("font-size: 11px; font-weight: bold; color: red;")
            
            # Coche verte à côté de la dernière version
            self.version_latest_label.setText(f"✓ {latest_ver}")
            self.version_latest_label.setStyleSheet("font-size: 11px; font-weight: bold; color: green;")
            
            # Afficher le lien de téléchargement
            download_url = "https://github.com/ChristophePelichet/DAOC-Character-Management/releases/latest"
            download_text = lang.get("version_check_download")
            self.version_download_link.setText(f'<a href="{download_url}" style="color: #0078d4; text-decoration: none;">{download_text}</a>')
            self.version_download_link.show()
            
            self.version_status_label.setText(lang.get("version_check_update_available"))
            self.version_status_label.setStyleSheet("font-size: 11px; font-weight: bold; color: green;")
            self.version_status_label.show()
        else:
            # À jour - coche verte à côté de la version actuelle
            self.version_current_label.setText(f"✓ {current_ver}")
            self.version_current_label.setStyleSheet("font-size: 11px; font-weight: bold; color: green;")
            
            # Coche verte à côté de la dernière version
            self.version_latest_label.setText(f"✓ {latest_ver if latest_ver else current_ver}")
            self.version_latest_label.setStyleSheet("font-size: 11px; font-weight: bold; color: green;")
            
            self.version_status_label.setText(lang.get("version_check_up_to_date"))
            self.version_status_label.setStyleSheet("font-size: 11px; font-style: italic; color: green;")
            self.version_status_label.show()
            self.version_download_link.hide()
    
    def check_eden_status(self):
        """
        Verify Herald connection status by testing cookies and Eden accessibility.

        This function runs the Eden connection test independently of whether
        characters have Herald URLs configured. The test validates:
        1. Cookies are available and valid
        2. Connection to eden-daoc.net/herald is possible

        The button state (enabled/disabled) is managed separately by
        herald_url_validator.py based on whether a URL is configured
        in the selected character.
        """
        # Stop existing validation thread if running
        if self.eden_status_thread and self.eden_status_thread.isRunning():
            self.eden_status_thread.quit()
            self.eden_status_thread.wait()
        
        # Mark validation as in progress
        self.eden_validation_in_progress = True
        
        # Display loading status and disable buttons
        self.eden_status_label.setText("⏳ Vérification en cours...")
        self.eden_status_label.setStyleSheet("padding: 5px; color: gray;")
        self.refresh_button.setEnabled(False)
        self.search_button.setEnabled(False)
        
        # Create cookie manager
        from Functions.cookie_manager import CookieManager
        cookie_manager = CookieManager()
        
        # Launch validation thread (always, independent of character URLs)
        self.eden_status_thread = EdenStatusThread(cookie_manager)
        self.eden_status_thread.status_updated.connect(self.update_eden_status)
        self.eden_status_thread.finished.connect(self._on_validation_finished)
        self.eden_status_thread.start()
        
        # Update Herald button states immediately (thread-safe)
        self._update_herald_buttons_state()
    
    def update_eden_status(self, accessible, message):
        """Met à jour l'affichage du statut Eden"""
        # Marquer la validation comme terminée dès réception du résultat
        self.eden_validation_in_progress = False
        
        if accessible:
            self.eden_status_label.setText(f"✅ Herald accessible")
            self.eden_status_label.setStyleSheet("padding: 5px; color: green; font-weight: bold;")
            # Réactiver le bouton refresh
            self.refresh_button.setEnabled(True)
            # Le search_button sera réactivé par _update_herald_buttons_state() si validation terminée
        else:
            self.eden_status_label.setText(f"❌ {message}")
            self.eden_status_label.setStyleSheet("padding: 5px; color: red;")
            
            # Griser les boutons si pas de cookies
            if "Aucun cookie" in message:
                self.refresh_button.setEnabled(False)
                self.search_button.setEnabled(False)
            else:
                # if c'est juste une erreur of connexion, garder refresh activé
                self.refresh_button.setEnabled(True)
                # Le search_button sera géré par _update_herald_buttons_state()
        
        # Mettre à jour l'état des boutons/actions Herald IMMÉDIATEMENT (plus d'attente)
        self._update_herald_buttons_state()
    
    def _on_validation_finished(self):
        """Appelé quand le thread de validation se termine (sécurité)"""
        self.eden_validation_in_progress = False
        self._update_herald_buttons_state()
    
    def _update_herald_buttons_state(self):
        """Désactive/active les boutons et actions Herald selon l'état de validation Eden et la présence d'URL"""
        from Functions.language_manager import lang
        
        # Vérifier si validation en cours (basé sur le flag, pas sur isRunning())
        is_validation_running = getattr(self, 'eden_validation_in_progress', False)
        
        # Vérifier si le character sélectionné a une URL Herald
        selected_character_data = self._get_selected_character_data()
        has_herald_url = False
        if selected_character_data:
            has_herald_url = bool(selected_character_data.get('url', '').strip())
        
        # Action du menu contextuel
        if hasattr(self, 'update_from_herald_action'):
            # Désactiver si: validation en cours OU pas d'URL
            should_disable = is_validation_running or not has_herald_url
            self.update_from_herald_action.setEnabled(not should_disable)
            
            # Mettre à jour le texte et le style selon l'état
            if is_validation_running:
                text = lang.get("context_menu_update_from_herald", default="🔄 Mettre à jour depuis Herald")
                self.update_from_herald_action.setText(text)
                tooltip_text = lang.get("herald_buttons.validation_in_progress", default="⏳ Validation Eden en cours... Veuillez patienter")
                self.update_from_herald_action.setToolTip(tooltip_text)
                self.update_from_herald_action.setStatusTip(tooltip_text)
            elif not has_herald_url:
                # Afficher un texte et une icône ⚠️ quand pas d'URL
                # Récupérer le texte sans l'icône 🔄
                base_text = lang.get("context_menu_update_from_herald", default="Mettre à jour depuis Herald").replace("🔄 ", "")
                text = "⚠️ " + base_text
                self.update_from_herald_action.setText(text)
                tooltip_text = lang.get("herald_buttons.no_url", default="ℹ️ Aucune URL Herald configurée pour ce personnage")
                self.update_from_herald_action.setToolTip(tooltip_text)
                self.update_from_herald_action.setStatusTip(tooltip_text)
            else:
                text = lang.get("context_menu_update_from_herald", default="🔄 Mettre à jour depuis Herald")
                self.update_from_herald_action.setText(text)
                self.update_from_herald_action.setToolTip("")
                self.update_from_herald_action.setStatusTip("")
        
        # Bouton de recherche Herald (dans ui_manager)
        if hasattr(self, 'search_button'):
            if is_validation_running:
                self.search_button.setEnabled(False)
                self.search_button.setToolTip(lang.get("herald_buttons.validation_in_progress", default="⏳ Validation Eden en cours... Veuillez patienter"))
            else:
                # Réactiver le bouton si la validation est terminée
                self.search_button.setEnabled(True)
                self.search_button.setToolTip(lang.get("buttons.eden_search", default="Rechercher un personnage sur Herald"))
    
    def _get_selected_character_data(self):
        """Get the data of the currently selected character"""
        try:
            selected_indices = self.main_window.character_tree.selectedIndexes()
            if not selected_indices:
                return None
            
            # Map proxy index to source index
            proxy_index = selected_indices[0]
            source_index = self.main_window.tree_manager.proxy_model.mapToSource(proxy_index)
            row = source_index.row()
            
            # Get char_id from realm column (column 1) using Qt.UserRole
            realm_index = self.main_window.tree_manager.model.index(row, 1)
            char_id = realm_index.data(Qt.UserRole)
            
            if not char_id:
                return None
            
            # Get character data from tree_manager's internal dict
            return self.main_window.tree_manager.characters_by_id.get(char_id)
        except Exception:
            pass
        
        return None
        
        
        
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
            # Sélectionner la ligne cliquée AVANT de mettre à jour l'état du menu
            self.main_window.character_tree.setCurrentIndex(index)
            
            # Utiliser un délai très court pour laisser la sélection se finir
            # puis mettre à jour l'état du menu contextuel IMMÉDIATEMENT
            from PySide6.QtCore import QTimer
            QTimer.singleShot(50, self._update_herald_buttons_state)
            
            # Afficher le menu
            self.context_menu.exec(self.main_window.character_tree.viewport().mapToGlobal(position))
            
    def update_status_bar(self, message):
        """Met à jour le texte de la barre de statut"""
        if hasattr(self.main_window, 'status_label'):
            self.main_window.status_label.setText(message)
            
    def show_about_dialog(self, app_name, app_version):
        """Affiche la boîte de dialogue 'À propos' complète avec onglets"""
        from UI.about_dialog import AboutDialog
        
        dialog = AboutDialog(self.main_window, app_name, app_version)
        dialog.exec()
    
    def _open_all_templates_window(self):
        """Ouvre la fenêtre pour consulter tous les templates disponibles"""
        logging.info("Opening armory templates window")
        try:
            window = UIArmoryAllTemplates(self.main_window)
            window.show()
            logging.info("Armory templates window opened successfully")
        except Exception as e:
            import traceback
            logging.error(f"Erreur lors de l'ouverture de la fenêtre Armurerie: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(
                self.main_window,
                lang.get("error_title", default="Erreur"),
                lang.get("armory.window_error", default="Erreur lors de l'ouverture de la fenêtre Armurerie") + f"\n\n{str(e)}"
            )
    
    def _open_wiki_documentation(self):
        """Ouvre le Wiki GitHub dans le navigateur"""
        import webbrowser
        from Functions.config_manager import config
        
        # Déterminer la langue pour le lien Wiki
        current_lang = config.get("ui.language", "fr").upper()
        wiki_url = f"https://github.com/ChristophePelichet/DAOC-Character-Management/wiki/{current_lang}-Home"
        webbrowser.open(wiki_url)
        
    def retranslate_ui(self):
        """Met à jour toutes les traductions de l'interface"""
        self.main_window.setWindowTitle(lang.get("window_title"))
        self.create_menu_bar()
        self.create_context_menu()
        
        # Mettre à jour les boutons d'action groupée
        if hasattr(self, 'select_all_button'):
            new_text = lang.get("menu.bulk_actions.select_all", default="✓ Select All")
            logging.debug(f"Updating select_all_button text to: {new_text}")
            self.select_all_button.setText(new_text)
            self.select_all_button.update()
        else:
            logging.warning("select_all_button attribute not found")
            
        if hasattr(self, 'deselect_all_button'):
            new_text = lang.get("menu.bulk_actions.deselect_all", default="✗ Deselect All")
            logging.debug(f"Updating deselect_all_button text to: {new_text}")
            self.deselect_all_button.setText(new_text)
            self.deselect_all_button.update()
        else:
            logging.warning("deselect_all_button attribute not found")
            
        if hasattr(self, 'delete_button'):
            new_text = lang.get("menu.bulk_actions.delete", default="Delete Selection")
            logging.debug(f"Updating delete_button text to: {new_text}")
            self.delete_button.setText(new_text)
            self.delete_button.update()
        else:
            logging.warning("delete_button attribute not found")
        
        # Mettre à jour les titres des groupes de la barre de statut Eden
        if hasattr(self, 'status_group'):
            self.status_group.setTitle(lang.get("status_bar.status_group_title"))
        
        if hasattr(self, 'info_group'):
            self.info_group.setTitle(lang.get("info_section_title"))
        
        # Mettre à jour les labels de version
        if hasattr(self, 'version_current_title_label'):
            self.version_current_title_label.setText(lang.get("version_check_current"))
        
        if hasattr(self, 'version_latest_title_label'):
            self.version_latest_title_label.setText(lang.get("version_check_latest"))
        
        if hasattr(self, 'version_check_button'):
            self.version_check_button.setText(lang.get("version_check_button"))
        
        # Mettre à jour les boutons Eden
        if hasattr(self, 'refresh_button'):
            self.refresh_button.setText(lang.get("buttons.eden_refresh"))
        
        if hasattr(self, 'search_button'):
            self.search_button.setText(lang.get("buttons.eden_search"))