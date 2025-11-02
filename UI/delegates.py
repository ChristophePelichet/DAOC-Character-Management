"""
Custom QStyledItemDelegates for the character list view.
These delegates customize the rendering of specific columns.
"""

import logging
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle, QApplication, QStyleOptionButton
from PySide6.QtGui import QIcon, QPalette, QColor
from PySide6.QtCore import Qt, QRect, QSize, QEvent


class CenterIconDelegate(QStyledItemDelegate):
    """Custom delegate to center icons in TreeView cells with realm-colored background."""
    
    # Couleurs de fond par royaume (alpha 25 pour plus de subtilité)
    REALM_COLORS = {
        "Albion": QColor(204, 0, 0, 25),      # Rouge clair
        "Midgard": QColor(0, 102, 204, 25),   # Bleu clair
        "Hibernia": QColor(0, 170, 0, 25)     # Vert clair
    }
    
    def paint(self, painter, option, index):
        """Draws the icon centered in the cell with realm-colored background."""
        # Get realm from this cell (column 1 contains realm data)
        realm = index.data(Qt.UserRole + 1)  # Realm name stored in UserRole + 1
        
        # Draw background with realm color if not selected
        if not (option.state & QStyle.State_Selected):
            if realm and realm in self.REALM_COLORS:
                painter.save()
                painter.fillRect(option.rect, self.REALM_COLORS[realm])
                painter.restore()
        
        icon = index.data(Qt.DecorationRole)
        if icon and isinstance(icon, QIcon) and not icon.isNull():
            # Draw only the background, not the icon or text
            opt = QStyleOptionViewItem(option)
            self.initStyleOption(opt, index)
            
            # Remove decoration and text so super().paint() won't draw them
            opt.features &= ~QStyleOptionViewItem.HasDecoration
            opt.features &= ~QStyleOptionViewItem.HasDisplay
            opt.icon = QIcon()
            opt.text = ""
            opt.decorationSize = QSize(0, 0)
            
            # Draw background only (selection highlight, etc.)
            super().paint(painter, opt, index)
            
            # Draw the centered icon
            painter.save()
            
            icon_size = option.decorationSize
            if icon_size.width() == -1:
                icon_size = QSize(16, 16)
            
            # Center the icon in the cell
            x = option.rect.x() + (option.rect.width() - icon_size.width()) // 2
            y = option.rect.y() + (option.rect.height() - icon_size.height()) // 2
            
            icon.paint(painter, QRect(x, y, icon_size.width(), icon_size.height()))
            painter.restore()
        else:
            super().paint(painter, option, index)


class CenterCheckboxDelegate(QStyledItemDelegate):
    """Delegate to draw a checkbox in the center of a cell with realm-colored background."""
    
    # Couleurs de fond par royaume (alpha 25 pour plus de subtilité)
    REALM_COLORS = {
        "Albion": QColor(204, 0, 0, 25),      # Rouge clair
        "Midgard": QColor(0, 102, 204, 25),   # Bleu clair
        "Hibernia": QColor(0, 170, 0, 25)     # Vert clair
    }
    
    def paint(self, painter, option, index):
        """Draws a centered checkbox with realm-colored background."""
        # Get realm from row data (stored in column 1 - realm icon)
        realm_index = index.sibling(index.row(), 1)
        realm = realm_index.data(Qt.UserRole + 1)  # Realm name stored in UserRole + 1
        
        # Draw background with realm color if not selected
        if not (option.state & QStyle.State_Selected):
            if realm and realm in self.REALM_COLORS:
                painter.save()
                painter.fillRect(option.rect, self.REALM_COLORS[realm])
                painter.restore()
        
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        
        # Draw only the background (selection, hover, etc.) without the checkbox
        style = option.widget.style() if option.widget else QApplication.style()
        style.drawPrimitive(QStyle.PE_PanelItemViewItem, opt, painter, option.widget)
        
        # Draw custom centered checkbox
        painter.save()
        
        from PySide6.QtWidgets import QStyleOptionButton
        check_option = QStyleOptionButton()
        
        # Set check state from model data
        check_state = index.data(Qt.CheckStateRole)
        if check_state == Qt.Checked:
            check_option.state = QStyle.State_On | QStyle.State_Enabled
        else:
            check_option.state = QStyle.State_Off | QStyle.State_Enabled
        
        # Make checkbox 2x size for better visibility
        indicator_size = int(style.pixelMetric(QStyle.PM_IndicatorWidth) * 2)
        x = option.rect.center().x() - indicator_size // 2
        y = option.rect.center().y() - indicator_size // 2
        check_option.rect = QRect(x, y, indicator_size, indicator_size)

        style.drawControl(QStyle.CE_CheckBox, check_option, painter, option.widget)
        painter.restore()

    def editorEvent(self, event, model, option, index):
        """Handle user interaction to toggle the checkbox."""
        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            new_state = Qt.Unchecked if index.data(Qt.CheckStateRole) == Qt.Checked else Qt.Checked
            model.setData(index, new_state, Qt.CheckStateRole)
            return True
        return False


class RealmTitleDelegate(QStyledItemDelegate):
    """Delegate to display realm titles in color and bold."""
    
    # Realm colors
    REALM_COLORS = {
        "Albion": "#CC0000",      # Red
        "Hibernia": "#00AA00",    # Green
        "Midgard": "#0066CC"      # Blue
    }
    
    def paint(self, painter, option, index):
        """Draws the title in color and bold."""
        text = index.data(Qt.DisplayRole)
        realm = index.data(Qt.UserRole)
        
        if not text:
            super().paint(painter, option, index)
            return
        
        # Draw only the background (without text)
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.text = ""
        
        # Draw background only
        style = opt.widget.style() if opt.widget else QApplication.style()
        style.drawControl(QStyle.CE_ItemViewItem, opt, painter, opt.widget)
        
        # Draw custom text
        painter.save()
        
        # Set bold font
        font = option.font
        font.setBold(True)
        painter.setFont(font)
        
        # Set color based on realm
        if realm in self.REALM_COLORS:
            if option.state & QStyle.State_Selected:
                painter.setPen(option.palette.color(QPalette.HighlightedText))
            else:
                painter.setPen(QColor(self.REALM_COLORS[realm]))
        else:
            painter.setPen(option.palette.color(QPalette.Text))
        
        # Draw centered text
        painter.drawText(option.rect, Qt.AlignCenter, text)
        painter.restore()


class NormalTextDelegate(QStyledItemDelegate):
    """Delegate to force normal (non-bold) text in cells with realm-based row coloring."""
    
    # Couleurs de fond par royaume (alpha 25 pour plus de subtilité)
    REALM_COLORS = {
        "Albion": QColor(204, 0, 0, 25),      # Rouge clair
        "Midgard": QColor(0, 102, 204, 25),   # Bleu clair
        "Hibernia": QColor(0, 170, 0, 25)     # Vert clair
    }
    
    def paint(self, painter, option, index):
        """Draws text with explicitly non-bold font and realm-colored background."""
        # Get the text
        text = index.data(Qt.DisplayRole)
        
        # Get realm from row data (stored in column 1 - realm icon)
        realm_index = index.sibling(index.row(), 1)
        realm = realm_index.data(Qt.UserRole + 1)  # Realm name stored in UserRole + 1
        
        # Draw background with realm color (même si pas de texte)
        painter.save()
        
        # Fill background with realm color if not selected
        if not (option.state & QStyle.State_Selected):
            if realm and realm in self.REALM_COLORS:
                painter.fillRect(option.rect, self.REALM_COLORS[realm])
        
        painter.restore()
        
        # Draw standard background (selection, hover, etc.)
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        
        style = option.widget.style() if option.widget else QApplication.style()
        style.drawPrimitive(QStyle.PE_PanelItemViewItem, opt, painter, option.widget)
        
        # Si pas de texte, on s'arrête ici (mais le fond est déjà dessiné)
        if not text:
            return
        
        # Draw custom text with non-bold font
        painter.save()
        
        # Force non-bold font
        font = option.font
        font.setBold(False)
        painter.setFont(font)
        
        # Use default text color
        if option.state & QStyle.State_Selected:
            painter.setPen(option.palette.color(QPalette.HighlightedText))
        else:
            painter.setPen(option.palette.color(QPalette.Text))
        
        # Draw text with proper alignment
        alignment = index.data(Qt.TextAlignmentRole)
        if alignment is None:
            alignment = Qt.AlignLeft | Qt.AlignVCenter
        
        painter.drawText(option.rect, alignment, str(text))
        painter.restore()


class UrlButtonDelegate(QStyledItemDelegate):
    """Delegate pour afficher un bouton 'Ouvrir' dans la colonne URL si une URL existe."""
    
    # Couleurs de fond par royaume (alpha 25 pour plus de subtilité)
    REALM_COLORS = {
        "Albion": QColor(204, 0, 0, 25),      # Rouge clair
        "Midgard": QColor(0, 102, 204, 25),   # Bleu clair
        "Hibernia": QColor(0, 170, 0, 25)     # Vert clair
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.button_padding = 2
        self.parent_app = parent  # Store reference to main app
        
    def paint(self, painter, option, index):
        """Dessine un bouton 'Ouvrir' si l'URL existe."""
        url = index.data(Qt.DisplayRole)
        
        # Get realm from row data
        realm_index = index.sibling(index.row(), 1)
        realm = realm_index.data(Qt.UserRole + 1)
        
        # Draw background with realm color
        painter.save()
        
        if not (option.state & QStyle.State_Selected):
            if realm and realm in self.REALM_COLORS:
                painter.fillRect(option.rect, self.REALM_COLORS[realm])
        
        painter.restore()
        
        # Draw standard background (selection, hover, etc.)
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        
        style = option.widget.style() if option.widget else QApplication.style()
        style.drawPrimitive(QStyle.PE_PanelItemViewItem, opt, painter, option.widget)
        
        # Si pas d'URL, on s'arrête ici
        if not url or not url.strip():
            return
        
        # Dessiner le bouton "Ouvrir"
        button_rect = self._get_button_rect(option.rect)
        
        # Style du bouton
        button_opt = QStyleOptionButton()
        button_opt.rect = button_rect
        button_opt.text = "🌐 Ouvrir"
        button_opt.state = QStyle.State_Enabled
        
        # Effet de survol
        if option.state & QStyle.State_MouseOver:
            button_opt.state |= QStyle.State_MouseOver
        
        # Dessiner le bouton
        style.drawControl(QStyle.CE_PushButton, button_opt, painter, option.widget)
    
    def _get_button_rect(self, rect):
        """Calcule le rectangle pour le bouton (aligné à gauche)."""
        button_width = 100  # Réduit de 120 à 100
        button_height = rect.height() - 2 * self.button_padding
        x = rect.x() + self.button_padding  # Aligné à gauche avec padding
        y = rect.y() + self.button_padding
        return QRect(x, y, button_width, button_height)
    
    def editorEvent(self, event, model, option, index):
        """Gère les clics sur le bouton avec vérification de la connexion Herald."""
        if event.type() == QEvent.MouseButtonRelease:
            url = index.data(Qt.DisplayRole)
            if url and url.strip():
                button_rect = self._get_button_rect(option.rect)
                if button_rect.contains(event.pos()):
                    # Vérifier la connexion Herald
                    if not self._check_herald_connection():
                        return True
                    
                    # Ouvrir l'URL dans le navigateur
                    import webbrowser
                    try:
                        if not url.startswith(('http://', 'https://')):
                            url = 'https://' + url
                        webbrowser.open(url)
                    except Exception as e:
                        logging.error(f"Erreur lors de l'ouverture de l'URL: {e}")
                    return True
        
        return super().editorEvent(event, model, option, index)
    
    def _check_herald_connection(self):
        """Vérifie si la connexion Herald est OK, sinon affiche un message."""
        if not self.parent_app:
            return True
        
        try:
            # Vérifier si les cookies existent
            from Functions.cookie_manager import CookieManager
            cookie_manager = CookieManager()
            
            if not cookie_manager.cookie_exists():
                self._show_connection_error("Aucun cookie détecté", 
                    "Vous devez d'abord générer des cookies Herald.\n\nAllez dans Paramètres pour configurer vos cookies.")
                return False
            
            # Tester la connexion Herald
            is_connected = cookie_manager.test_eden_connection()
            if not is_connected:
                self._show_connection_error("Connexion Herald impossible",
                    "Les cookies ont expiré ou la connexion a échoué.\n\nAllez dans Paramètres pour mettre à jour vos cookies.")
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Erreur lors de la vérification Herald: {e}")
            return False
    
    def _show_connection_error(self, title, message):
        """Affiche un message d'erreur avec suggestion de configuration."""
        from PySide6.QtWidgets import QMessageBox
        
        msg = QMessageBox(self.parent_app if self.parent_app else None)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Open)
        
        # Modifier les labels des boutons
        msg.button(QMessageBox.Ok).setText("Fermer")
        msg.button(QMessageBox.Open).setText("Ouvrir Paramètres")
        
        result = msg.exec()
        
        # Si l'utilisateur clique sur "Ouvrir Paramètres"
        if result == QMessageBox.Open and self.parent_app:
            if hasattr(self.parent_app, 'open_configuration'):
                self.parent_app.open_configuration()
    
    def sizeHint(self, option, index):
        """Retourne la taille recommandée pour la cellule."""
        return QSize(110, 32)  # Réduit de (130, 40) à (110, 32)
