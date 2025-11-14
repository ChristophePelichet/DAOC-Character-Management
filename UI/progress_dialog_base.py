"""
Progress Dialog Base Components - Composants de Base pour Dialogues de Progression

Ce module fournit les classes de base réutilisables pour créer des dialogues de progression
avec système d'étapes visuelles pour toutes les opérations longues de l'application.

Classes:
    - StepState: Énumération des états possibles d'une étape
    - ProgressStep: Modèle de données pour une étape individuelle
    - StepConfiguration: Configurations prédéfinies d'étapes réutilisables
    - ProgressStepsDialog: Dialogue de base avec système d'étapes configurables

Version: 0.110
Date: 14 novembre 2025
"""

from enum import Enum
from typing import List, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QPushButton, QScrollArea, QWidget, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer, QMetaObject, Slot
from PySide6.QtGui import QFont


# ============================================================================
# ÉNUMÉRATION DES ÉTATS
# ============================================================================

class StepState(str, Enum):
    """États possibles d'une étape de progression"""
    PENDING = "pending"      # ⏺️ En attente, pas encore démarré
    RUNNING = "running"      # ⏳ En cours d'exécution
    COMPLETED = "completed"  # ✅ Terminé avec succès
    SKIPPED = "skipped"      # ⏭️ Sauté (pour étapes conditionnelles)
    ERROR = "error"          # ❌ Échec


# ============================================================================
# CLASSE PROGRESSSTEP
# ============================================================================

class ProgressStep:
    """
    Représente une étape individuelle dans un processus de progression.
    
    Attributes:
        icon (str): Emoji représentant l'étape (ex: "🔐", "🌐")
        text (str): Description textuelle de l'étape
        conditional (bool): Si True, l'étape peut être sautée selon le contexte
        category (str): Catégorie de l'étape ("connection", "scraping", "processing", etc.)
        state (StepState): État actuel de l'étape
    
    Example:
        >>> step = ProgressStep("🔐", "Vérification des cookies", category="connection")
        >>> step.is_pending()
        True
        >>> step.state = StepState.RUNNING
        >>> step.get_display_icon()
        '⏳'
    """
    
    def __init__(
        self, 
        icon: str, 
        text: str, 
        conditional: bool = False, 
        category: str = "general"
    ):
        """
        Initialise une étape de progression.
        
        Args:
            icon: Emoji représentant l'étape
            text: Description de l'étape
            conditional: Si True, l'étape peut être sautée
            category: Catégorie de l'étape
            
        Raises:
            ValueError: Si icon ou text est vide
        """
        if not icon or not icon.strip():
            raise ValueError("L'icône ne peut pas être vide")
        if not text or not text.strip():
            raise ValueError("Le texte ne peut pas être vide")
        
        self.icon = icon.strip()
        self.text = text.strip()
        self.conditional = conditional
        self.category = category
        self.state = StepState.PENDING
    
    def is_pending(self) -> bool:
        """Retourne True si l'étape est en attente"""
        return self.state == StepState.PENDING
    
    def is_running(self) -> bool:
        """Retourne True si l'étape est en cours"""
        return self.state == StepState.RUNNING
    
    def is_completed(self) -> bool:
        """Retourne True si l'étape est terminée"""
        return self.state == StepState.COMPLETED
    
    def is_skipped(self) -> bool:
        """Retourne True si l'étape a été sautée"""
        return self.state == StepState.SKIPPED
    
    def is_error(self) -> bool:
        """Retourne True si l'étape est en erreur"""
        return self.state == StepState.ERROR
    
    def get_display_icon(self) -> str:
        """
        Retourne l'icône à afficher selon l'état actuel.
        
        Returns:
            Emoji correspondant à l'état actuel
        """
        icon_map = {
            StepState.PENDING: "⏺️",
            StepState.RUNNING: "⏳",
            StepState.COMPLETED: "✅",
            StepState.SKIPPED: "⏭️",
            StepState.ERROR: "❌"
        }
        return icon_map.get(self.state, "⏺️")
    
    def get_display_color(self) -> str:
        """
        Retourne la couleur à utiliser selon l'état actuel.
        
        Returns:
            Code couleur hexadécimal
        """
        color_map = {
            StepState.PENDING: "#888888",   # Gris
            StepState.RUNNING: "#2196F3",   # Bleu
            StepState.COMPLETED: "#4CAF50", # Vert
            StepState.SKIPPED: "#FF9800",   # Orange
            StepState.ERROR: "#F44336"      # Rouge
        }
        return color_map.get(self.state, "#888888")
    
    def __repr__(self) -> str:
        """Représentation pour debug"""
        return f"ProgressStep(icon='{self.icon}', text='{self.text}', state={self.state.value})"


# ============================================================================
# CLASSE STEPCONFIGURATION
# ============================================================================

class StepConfiguration:
    """
    Configurations prédéfinies d'étapes réutilisables.
    
    Cette classe fournit des ensembles d'étapes standards pour les opérations
    courantes (connexion Herald, recherche, scraping stats, etc.).
    
    Example:
        >>> steps = StepConfiguration.build_steps(
        ...     StepConfiguration.HERALD_CONNECTION,
        ...     StepConfiguration.HERALD_SEARCH,
        ...     StepConfiguration.CLEANUP
        ... )
        >>> len(steps)
        9
    """
    
    # Étapes de connexion Herald (communes à beaucoup d'opérations)
    HERALD_CONNECTION = [
        ProgressStep("🔐", "step_herald_connection_cookies", category="connection"),
        ProgressStep("🌐", "step_herald_connection_init", category="connection"),
        ProgressStep("🍪", "step_herald_connection_load", category="connection"),
    ]
    
    # Initialisation simple du scraper (sans cookies/browser complet)
    SCRAPER_INIT = [
        ProgressStep("🔌", "step_scraper_init", category="connection"),
    ]
    
    # Étapes de recherche Herald
    HERALD_SEARCH = [
        ProgressStep("🔍", "step_herald_search_search", category="scraping"),
        ProgressStep("⏳", "step_herald_search_load", category="scraping"),
        ProgressStep("📊", "step_herald_search_extract", category="scraping"),
        ProgressStep("💾", "step_herald_search_save", category="processing"),
        ProgressStep("🎯", "step_herald_search_format", category="processing"),
    ]
    
    # Étapes de mise à jour stats
    STATS_SCRAPING = [
        ProgressStep("🏰", "step_stats_scraping_rvr", category="scraping"),
        ProgressStep("⚔️", "step_stats_scraping_pvp", category="scraping"),
        ProgressStep("🐉", "step_stats_scraping_pve", category="scraping"),
        ProgressStep("💰", "step_stats_scraping_wealth", category="scraping"),
        ProgressStep("🏆", "step_stats_scraping_achievements", conditional=True, category="scraping"),
    ]
    
    # Étapes de mise à jour personnage (ANCIENNE VERSION - 3 étapes)
    # Cette config est pour un workflow différent
    CHARACTER_UPDATE_SIMPLE = [
        ProgressStep("🔍", "Scraping de la page personnage", category="scraping"),
        ProgressStep("📊", "Comparaison des données", category="processing"),
        ProgressStep("💾", "Application des modifications", category="processing"),
    ]
    
    # Étapes de mise à jour personnage depuis Herald (NOUVELLE VERSION - 8 étapes complètes)
    CHARACTER_UPDATE = [
        ProgressStep("📝", "step_character_update_extract_name", category="connection"),
        ProgressStep("🌐", "step_character_update_init", category="connection"),
        ProgressStep("🍪", "step_character_update_load_cookies", category="connection"),
        ProgressStep("🔍", "step_character_update_navigate", category="scraping"),
        ProgressStep("⏳", "step_character_update_wait", category="scraping"),
        ProgressStep("📊", "step_character_update_extract_data", category="scraping"),
        ProgressStep("🎯", "step_character_update_format", category="processing"),
        ProgressStep("🔄", "step_character_update_close", category="cleanup"),
    ]
    
    # Étapes de génération de cookies (PAS de connexion Herald)
    COOKIE_GENERATION = [
        ProgressStep("⚙️", "step_cookie_gen_config", category="setup"),
        ProgressStep("🌐", "step_cookie_gen_open", category="setup"),
        ProgressStep("👤", "step_cookie_gen_wait_user", category="interactive"),
        ProgressStep("🍪", "step_cookie_gen_extract", category="processing"),
        ProgressStep("💾", "step_cookie_gen_save", category="processing"),
        ProgressStep("✅", "step_cookie_gen_validate", category="processing"),
    ]
    
    # Étapes de richesse multi-royaumes
    WEALTH_MULTI_REALM = [
        ProgressStep("🔍", "Recherche des personnages par royaume", category="scraping"),
        ProgressStep("🔴", "Scraping Albion", conditional=True, category="scraping"),
        ProgressStep("🔵", "Scraping Midgard", conditional=True, category="scraping"),
        ProgressStep("🟢", "Scraping Hibernia", conditional=True, category="scraping"),
        ProgressStep("💰", "Calcul du total", category="processing"),
    ]
    
    # Étape de fermeture (commune)
    CLEANUP = [
        ProgressStep("🔄", "step_cleanup", category="cleanup"),
    ]
    
    @classmethod
    def build_steps(cls, *step_groups: List[ProgressStep]) -> List[ProgressStep]:
        """
        Construit une liste d'étapes en combinant plusieurs groupes.
        
        Args:
            *step_groups: Groupes d'étapes à combiner
            
        Returns:
            Liste unifiée d'étapes
            
        Example:
            >>> steps = StepConfiguration.build_steps(
            ...     StepConfiguration.HERALD_CONNECTION,
            ...     StepConfiguration.HERALD_SEARCH,
            ...     StepConfiguration.CLEANUP
            ... )
        """
        combined = []
        for group in step_groups:
            # Créer des copies pour éviter de partager les instances
            combined.extend([
                ProgressStep(
                    step.icon, 
                    step.text, 
                    step.conditional, 
                    step.category
                ) for step in group
            ])
        return combined


# ============================================================================
# CLASSE PROGRESSSTEPSDIALOG
# ============================================================================

class ProgressStepsDialog(QDialog):
    """
    Dialogue de progression avec système d'étapes visuelles configurables.
    
    Ce dialogue affiche une liste d'étapes avec leur statut en temps réel,
    une barre de progression optionnelle, et gère les mises à jour thread-safe.
    
    Signals:
        step_updated: Émis quand une étape change d'état (step_index: int, new_state: str)
        all_completed: Émis quand toutes les étapes sont terminées
        canceled: Émis si l'utilisateur annule l'opération
    
    Example:
        >>> steps = StepConfiguration.build_steps(
        ...     StepConfiguration.HERALD_CONNECTION,
        ...     StepConfiguration.CLEANUP
        ... )
        >>> dialog = ProgressStepsDialog(
        ...     parent=self,
        ...     title="🔍 Opération en cours...",
        ...     steps=steps
        ... )
        >>> dialog.show()
        >>> dialog.start_step(0)
        >>> dialog.complete_step(0)
    """
    
    # Signaux
    step_updated = Signal(int, str)  # (step_index, new_state)
    all_completed = Signal()
    canceled = Signal()
    
    def __init__(
        self,
        parent: Optional[QWidget],
        title: str,
        steps: List[ProgressStep],
        description: Optional[str] = None,
        show_progress_bar: bool = True,
        determinate_progress: bool = False,
        allow_cancel: bool = False
    ):
        """
        Initialise le dialogue de progression.
        
        Args:
            parent: Widget parent
            title: Titre de la fenêtre (ex: "🔍 Recherche en cours...")
            steps: Liste des étapes à afficher
            description: Description supplémentaire (optionnel)
            show_progress_bar: Afficher la barre de progression
            determinate_progress: Mode déterminé (avec %) ou indéterminé (animation)
            allow_cancel: Permettre l'annulation
        """
        super().__init__(parent)
        
        self.steps = steps
        self.show_progress_bar = show_progress_bar
        self.determinate_progress = determinate_progress
        self.allow_cancel = allow_cancel
        
        # Configuration de la fenêtre
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Stockage des labels d'étapes pour mise à jour
        self.step_labels: List[QLabel] = []
        
        # Initialiser l'interface
        self._init_ui(title, description)
    
    def _init_ui(self, title: str, description: Optional[str]):
        """Initialise l'interface utilisateur"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre
        title_label = QLabel(f"<h2>{title}</h2>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Description (optionnelle)
        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setStyleSheet("color: gray; padding: 5px;")
            layout.addWidget(desc_label)
        
        # Zone d'étapes avec scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        steps_widget = QWidget()
        steps_layout = QVBoxLayout(steps_widget)
        steps_layout.setSpacing(8)
        steps_layout.setContentsMargins(10, 10, 10, 10)
        
        # Créer un label pour chaque étape
        from Functions.language_manager import lang
        for step in self.steps:
            # Traduire le texte de l'étape si c'est une clé de traduction
            translated_text = lang.get(step.text, default=step.text)
            step_label = QLabel(f"{step.get_display_icon()} {translated_text}")
            step_label.setStyleSheet(f"color: {step.get_display_color()}; padding: 5px;")
            
            font = step_label.font()
            font.setPointSize(10)
            step_label.setFont(font)
            
            steps_layout.addWidget(step_label)
            self.step_labels.append(step_label)
        
        steps_layout.addStretch()
        scroll_area.setWidget(steps_widget)
        layout.addWidget(scroll_area, 1)  # Stretch factor = 1
        
        # Barre de progression (optionnelle)
        if self.show_progress_bar:
            self.progress_bar = QProgressBar()
            self.progress_bar.setTextVisible(self.determinate_progress)
            
            if self.determinate_progress:
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(0)
            else:
                # Mode indéterminé (animation continue)
                self.progress_bar.setRange(0, 0)
            
            layout.addWidget(self.progress_bar)
        else:
            self.progress_bar = None
        
        # Message de statut
        self.status_label = QLabel("⏳ Opération en cours...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            "padding: 10px; "
            "border: 1px solid #ccc; "
            "border-radius: 5px; "
            "background-color: #f5f5f5;"
        )
        layout.addWidget(self.status_label)
        
        # Bouton Annuler (optionnel)
        if self.allow_cancel:
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            self.cancel_button = QPushButton("Annuler")
            self.cancel_button.clicked.connect(self._on_cancel_clicked)
            button_layout.addWidget(self.cancel_button)
            button_layout.addStretch()
            
            layout.addLayout(button_layout)
        else:
            self.cancel_button = None
    
    def _on_cancel_clicked(self):
        """Gestion du clic sur le bouton Annuler"""
        if self.cancel_button:
            self.cancel_button.setEnabled(False)
            self.cancel_button.setText("Annulation...")
        
        self.set_status_message("⚠️ Annulation en cours...", "#FF9800")
        self.canceled.emit()
    
    def update_step(
        self, 
        step_index: int, 
        state: StepState, 
        custom_message: Optional[str] = None
    ):
        """
        Met à jour l'état d'une étape (thread-safe).
        
        Args:
            step_index: Index de l'étape (0-based)
            state: Nouvel état
            custom_message: Message personnalisé pour le status_label (optionnel)
        """
        # Vérifier l'index
        if step_index < 0 or step_index >= len(self.steps):
            return
        
        # Mettre à jour l'état de l'étape
        self.steps[step_index].state = state
        
        # Mettre à jour l'UI (thread-safe via invokeMethod)
        self._update_step_ui(step_index, custom_message if custom_message else "")
        
        # Émettre le signal
        self.step_updated.emit(step_index, state.value)
    
    def _update_step_ui(self, step_index: int, custom_message: str):
        """Mise à jour UI (appelé dans le thread principal)"""
        from Functions.language_manager import lang
        step = self.steps[step_index]
        label = self.step_labels[step_index]
        
        # Mettre à jour le texte et la couleur
        icon = step.get_display_icon()
        color = step.get_display_color()
        
        # Traduire le texte de l'étape
        translated_text = lang.get(step.text, default=step.text)
        label.setText(f"{icon} {translated_text}")
        
        # Appliquer le style selon l'état
        font_weight = "bold" if step.is_running() else "normal"
        font_style = "italic" if step.is_skipped() else "normal"
        
        label.setStyleSheet(
            f"color: {color}; "
            f"padding: 5px; "
            f"font-weight: {font_weight}; "
            f"font-style: {font_style};"
        )
        
        # Mettre à jour le message de statut si fourni
        if custom_message:
            self.set_status_message(custom_message, color)
        
        # Mettre à jour la barre de progression (mode déterminé)
        if self.progress_bar and self.determinate_progress:
            completed_count = sum(1 for s in self.steps if s.is_completed() or s.is_skipped())
            total_count = len(self.steps)
            percentage = int((completed_count / total_count) * 100)
            self.progress_bar.setValue(percentage)
    
    def start_step(self, step_index: int):
        """Démarre une étape (marque comme "running")"""
        self.update_step(step_index, StepState.RUNNING)
    
    def complete_step(self, step_index: int):
        """Termine une étape avec succès"""
        self.update_step(step_index, StepState.COMPLETED)
    
    def skip_step(self, step_index: int, reason: Optional[str] = None):
        """
        Saute une étape conditionnelle.
        
        Args:
            step_index: Index de l'étape
            reason: Raison du saut (ajouté au tooltip)
        """
        self.update_step(step_index, StepState.SKIPPED)
        
        if reason:
            # Ajouter la raison au tooltip
            self.step_labels[step_index].setToolTip(f"Sauté: {reason}")
    
    def error_step(self, step_index: int, error_message: Optional[str] = None):
        """
        Marque une étape comme échouée.
        
        Args:
            step_index: Index de l'étape
            error_message: Message d'erreur (ajouté au tooltip)
        """
        self.update_step(step_index, StepState.ERROR)
        
        if error_message:
            # Ajouter le message d'erreur au tooltip
            self.step_labels[step_index].setToolTip(f"Erreur: {error_message}")
        
        # Mettre à jour le message de statut
        self.set_status_message(
            f"❌ Erreur: {error_message if error_message else 'Opération échouée'}", 
            "#F44336"
        )
    
    def complete_all(self, success_message: str = "✅ Opération terminée avec succès !"):
        """
        Marque toutes les étapes comme terminées.
        
        Args:
            success_message: Message de succès à afficher
        """
        # Marquer toutes les étapes non-terminées comme completed
        for i, step in enumerate(self.steps):
            if step.is_pending() or step.is_running():
                self.complete_step(i)
        
        # Mettre à jour le message de statut
        self.set_status_message(success_message, "#4CAF50")
        
        # Émettre le signal
        self.all_completed.emit()
        
        # Fermer automatiquement après 1.5 secondes
        QTimer.singleShot(1500, self.accept)
    
    def set_status_message(self, message: str, color: Optional[str] = None):
        """
        Change le message de statut.
        
        Args:
            message: Message à afficher
            color: Couleur du texte (optionnel)
        """
        self._set_status_message_ui(message, color if color else "#000000")
    
    def _set_status_message_ui(self, message: str, color: str):
        """Mise à jour du message de statut (thread principal)"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(
            f"padding: 10px; "
            f"border: 1px solid #ccc; "
            f"border-radius: 5px; "
            f"background-color: #f5f5f5; "
            f"color: {color};"
        )
    
    def set_indeterminate(self):
        """Active le mode indéterminé pour la barre de progression"""
        if self.progress_bar:
            self.progress_bar.setRange(0, 0)
    
    def update_progress(self, percentage: int):
        """
        Met à jour la barre de progression (mode déterminé uniquement).
        
        Args:
            percentage: Pourcentage (0-100)
        """
        if self.progress_bar and self.determinate_progress:
            self.progress_bar.setValue(max(0, min(100, percentage)))
