"""
About Dialog - Complete application information dialog with tabs
Displays application info, credits, and license information
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
    QTextBrowser, QPushButton, QLabel, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
import markdown
import logging

from Functions.language_manager import lang

logger = logging.getLogger(__name__)


class AboutDialog(QDialog):
    """Complete About dialog with tabs for Info, Credits, and License"""
    
    def __init__(self, parent=None, app_name="DAOC Character Manager", app_version="0.108"):
        super().__init__(parent)
        self.app_name = app_name
        self.app_version = app_version
        
        self.setWindowTitle(lang.get("app.about_title", app_name=self.app_name))
        self.resize(800, 600)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Add tabs
        self.tabs.addTab(self._create_about_tab(), lang.get("dialogs.about_dialog.tab_about", default="About"))
        self.tabs.addTab(self._create_credits_tab(), lang.get("dialogs.about_dialog.tab_credits", default="Credits"))
        self.tabs.addTab(self._create_license_tab(), lang.get("dialogs.about_dialog.tab_license", default="License"))
        
        main_layout.addWidget(self.tabs)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton(lang.get("button_close", default="Close"))
        close_button.clicked.connect(self.accept)
        close_button.setDefault(True)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def _create_about_tab(self):
        """Create the About tab with basic app information"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Application name and version
        title_label = QLabel(f"<h1>{self.app_name}</h1>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        version_label = QLabel(f"<h3>{lang.get('app.version_info', version=self.app_version)}</h3>")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        layout.addSpacing(20)
        
        # Description - with theme-aware HTML
        description = QTextBrowser()
        description.setOpenExternalLinks(True)
        
        # Remove default background to use theme colors
        description.setStyleSheet("QTextBrowser { background-color: transparent; border: none; }")
        
        # Set font with emoji support
        font = QFont()
        font.setFamilies(["Segoe UI Emoji", "Segoe UI Symbol", "Apple Color Emoji", "Noto Color Emoji", "Segoe UI", "Arial"])
        font.setPointSize(11)
        description.setFont(font)
        
        # Get theme-aware colors
        about_html = self._get_themed_about_html()
        description.setHtml(about_html)
        
        layout.addWidget(description, 1)  # stretch factor = 1 to fill remaining space
        
        widget.setLayout(layout)
        return widget
    
    def _get_themed_about_html(self):
        """Generate theme-aware HTML for About tab"""
        try:
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            palette = app.palette()
            
            link_color = palette.color(palette.Link).name()
            
        except:
            link_color = "#3498db"
        
        return f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; padding: 20px;">
            <h2>{lang.get("dialogs.about_dialog.description_title", default="Description")}</h2>
            <p>{lang.get("dialogs.about_dialog.description_text", default="Character management application for Dark Age of Camelot (DAOC), developed in Python with PySide6.")}</p>
            
            <h2>{lang.get("dialogs.about_dialog.creator_title", default="Creator")}</h2>
            <p><strong>{lang.get("dialogs.about_dialog.creator_name", default="Ewoline")}</strong></p>
            
            <h2>{lang.get("dialogs.about_dialog.repository_title", default="Repository")}</h2>
            <p><a href="https://github.com/ChristophePelichet/DAOC-Character-Management" style="color: {link_color};">{lang.get("dialogs.about_dialog.repository_label", default="GitHub - DAOC Character Management")}</a></p>
        </div>
        """
    
    def _create_credits_tab(self):
        """Create the Credits tab with hardcoded HTML content"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Text browser for credits
        credits_browser = QTextBrowser()
        credits_browser.setOpenExternalLinks(True)
        
        # Remove default background to use theme colors
        credits_browser.setStyleSheet("QTextBrowser { background-color: transparent; border: none; }")
        
        # Set font with emoji support
        font = QFont()
        font.setFamilies(["Segoe UI Emoji", "Segoe UI Symbol", "Apple Color Emoji", "Noto Color Emoji", "Segoe UI", "Arial"])
        font.setPointSize(11)
        credits_browser.setFont(font)
        
        # Generate theme-aware credits HTML
        credits_html = self._get_themed_credits_html()
        credits_browser.setHtml(credits_html)
        
        layout.addWidget(credits_browser)
        
        widget.setLayout(layout)
        return widget
    
    def _get_themed_credits_html(self):
        """Generate theme-aware HTML for Credits tab"""
        try:
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            palette = app.palette()
            
            link_color = palette.color(palette.Link).name()
            highlight_color = palette.color(palette.Highlight).name()
            
            # Determine if dark theme
            is_dark = palette.color(palette.Text).lightness() > palette.color(palette.Base).lightness()
            
            if is_dark:
                h1_color = "#FFFFFF"
                h2_color = "#E0E0E0"
                h3_color = "#C0C0C0"
                hr_color = "#666666"
            else:
                h1_color = "#2c3e50"
                h2_color = "#34495e"
                h3_color = "#7f8c8d"
                hr_color = "#e0e0e0"
                
        except:
            link_color = "#3498db"
            highlight_color = "#3498db"
            h1_color = "#2c3e50"
            h2_color = "#34495e"
            h3_color = "#7f8c8d"
            hr_color = "#e0e0e0"
        
        return f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; padding: 20px;">
            <h1 style="color: {h1_color}; border-bottom: 3px solid {highlight_color}; padding-bottom: 10px; font-size: 28px;">{lang.get("dialogs.about_dialog.credits_title", default="Credits & Acknowledgments")}</h1>
            
            <p>{lang.get("dialogs.about_dialog.credits_intro", default="This project would not be possible without the contributions of various open-source projects, data sources, and the DAOC community.")}</p>
            
            <hr style="border: none; border-top: 2px solid {hr_color}; margin: 30px 0;">
            
            <h2 style="color: {h2_color}; border-bottom: 2px solid {highlight_color}; padding-bottom: 8px; font-size: 22px;">{lang.get("dialogs.about_dialog.daoc_community_title", default="DAOC Community")}</h2>
            
            <h3 style="color: {h3_color}; font-size: 18px; margin-top: 20px;">{lang.get("dialogs.about_dialog.dol_project_title", default="Dawn of Light (DOL)")}</h3>
            <ul>
                <li><strong>{lang.get("dialogs.about_dialog.dol_project_label", default="Project:")}  </strong> <a href="https://github.com/Dawn-of-Light" style="color: {link_color};">Dawn of Light</a></li>
                <li><strong>{lang.get("dialogs.about_dialog.dol_description_label", default="Description:")}  </strong> {lang.get("dialogs.about_dialog.dol_description", default="Open-source DAOC server emulator")}</li>
            </ul>
            
            <h3 style="color: {h3_color}; font-size: 18px; margin-top: 20px;">{lang.get("dialogs.about_dialog.eden_server_title", default="Eden DAOC")}</h3>
            <ul>
                <li><strong>{lang.get("dialogs.about_dialog.eden_server_label", default="Server:")}  </strong> <a href="https://www.eden-daoc.net/" style="color: {link_color};">Eden DAOC</a></li>
                <li><strong>{lang.get("dialogs.about_dialog.eden_description_label", default="Description:")}  </strong> {lang.get("dialogs.about_dialog.eden_description", default="DAOC private server")}</li>
            </ul>
            
            <h3 style="color: {h3_color}; font-size: 18px; margin-top: 20px;">{lang.get("dialogs.about_dialog.dolmodels_source_title", default="Eve-of-Darkness DolModels")}</h3>
            <ul>
                <li><strong>{lang.get("dialogs.about_dialog.dolmodels_source_label", default="Source:")}  </strong> <a href="https://github.com/Eve-of-Darkness/DolModels" style="color: {link_color};">Eve-of-Darkness/DolModels</a></li>
                <li><strong>{lang.get("dialogs.about_dialog.dolmodels_description_label", default="Description:")}  </strong> {lang.get("dialogs.about_dialog.dolmodels_description", default="1000+ DAOC item model images")}</li>
            </ul>
            
            <hr style="border: none; border-top: 2px solid {hr_color}; margin: 30px 0;">
            
            <h2 style="color: {h2_color}; border-bottom: 2px solid {highlight_color}; padding-bottom: 8px; font-size: 22px;">{lang.get("dialogs.about_dialog.special_thanks_title", default="Special Thanks")}</h2>
            
            <p><strong>{lang.get("dialogs.about_dialog.special_thanks_text", default="Testers and friends who made this project possible:")}:</strong></p>
            <ul>
                <li><strong>Morfuin / Leifur</strong></li>
                <li><strong>Laelly</strong></li>
            </ul>
            
            <hr style="border: none; border-top: 2px solid {hr_color}; margin: 30px 0;">
            
            <h2 style="color: {h2_color}; border-bottom: 2px solid {highlight_color}; padding-bottom: 8px; font-size: 22px;">{lang.get("dialogs.about_dialog.translations_title", default="🌍 Translations")}</h2>
            
            <p><strong>{lang.get("dialogs.about_dialog.translations_label", default="Language Contributors:")}:</strong></p>
            <ul>
                <li><strong>{lang.get("dialogs.about_dialog.translation_french", default="French")}</strong> - {lang.get("dialogs.about_dialog.translation_credits", default="Ewoline / IA")}</li>
                <li><strong>{lang.get("dialogs.about_dialog.translation_english", default="English")}</strong> - {lang.get("dialogs.about_dialog.translation_credits", default="Ewoline / IA")}</li>
                <li><strong>{lang.get("dialogs.about_dialog.translation_german", default="German")}</strong> - {lang.get("dialogs.about_dialog.translation_credits", default="Ewoline / IA")}</li>
                <li><strong>{lang.get("dialogs.about_dialog.translation_spanish", default="Spanish")}</strong> - <em>{lang.get("dialogs.about_dialog.translation_spanish_coming", default="Coming soon")}</em></li>
            </ul>
        </div>
        """
    
    def _create_license_tab(self):
        """Create the License tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Text browser for license
        license_browser = QTextBrowser()
        license_browser.setOpenExternalLinks(True)
        
        # Remove default background to use theme colors
        license_browser.setStyleSheet("QTextBrowser { background-color: transparent; border: none; }")
        
        # Set font
        font = QFont()
        font.setFamilies(["Segoe UI Emoji", "Segoe UI Symbol", "Segoe UI", "Arial"])
        font.setPointSize(11)
        license_browser.setFont(font)
        
        # Check for LICENSE file
        license_file = Path(__file__).parent.parent / "LICENSE"
        
        if license_file.exists():
            try:
                with open(license_file, 'r', encoding='utf-8') as f:
                    license_content = f.read()
                
                license_browser.setPlainText(license_content)
                logger.info("LICENSE file loaded successfully")
                
            except Exception as e:
                logger.error(f"Error loading LICENSE: {e}")
                license_browser.setHtml(f"<h1>❌ Error</h1><p>Could not load license file: {e}</p>")
        else:
            # Default license message - theme-aware
            license_html = """
            <div style="font-family: 'Segoe UI', Arial, sans-serif; padding: 20px;">
                <h1>MIT License</h1>
                <p><strong>Copyright &copy; 2025 Christophe Pelichet (Ewoline)</strong></p>
                
                <p>Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:</p>
                
                <p>The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.</p>
                
                <p>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ccc;">
                
                <h2>Third-Party Licenses</h2>
                <p>This application uses various open-source components with different licenses:</p>
                <ul>
                    <li><strong>Eve-of-Darkness/DolModels</strong> - GNU GPL v3.0</li>
                    <li><strong>PySide6</strong> - LGPL v3</li>
                    <li><strong>Other dependencies</strong> - See CREDITS tab for details</li>
                </ul>
            </div>
            """
            license_browser.setHtml(license_html)
            logger.info("Using default license text (LICENSE file not found)")
        
        layout.addWidget(license_browser)
        
        widget.setLayout(layout)
        return widget
    
    def _add_css_styling(self, html_content):
        """Add CSS styling to HTML content - theme-aware"""
        # Get theme colors from palette
        try:
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            palette = app.palette()
            
            # Extract colors from current theme
            bg_color = palette.color(palette.Base).name()
            text_color = palette.color(palette.Text).name()
            window_color = palette.color(palette.Window).name()
            link_color = palette.color(palette.Link).name()
            highlight_color = palette.color(palette.Highlight).name()
            
            # Determine if dark theme (text is brighter than background)
            is_dark = palette.color(palette.Text).lightness() > palette.color(palette.Base).lightness()
            
            # Adjust colors for headers and code blocks
            if is_dark:
                h1_color = "#FFFFFF"  # Blanc pur pour dark theme
                h2_color = "#E0E0E0"  # Gris très clair
                h3_color = "#C0C0C0"  # Gris clair
                code_bg = "#2D2D30"
                code_color = "#E96666"
                blockquote_bg = "#1E3A5F"
                blockquote_border = "#3498DB"
                table_header_bg = "#0078D7"
                table_row_alt_bg = "#2A2A2A"
                hr_color = "#666666"
            else:
                h1_color = "#2c3e50"  # Dark blue for light theme
                h2_color = "#34495e"  # Dark gray
                h3_color = "#7f8c8d"  # Medium gray
                code_bg = "#f4f4f4"
                code_color = "#e74c3c"
                blockquote_bg = "#ecf7fd"
                blockquote_border = "#3498db"
                table_header_bg = "#3498db"
                table_row_alt_bg = "#f9f9f9"
                hr_color = "#e0e0e0"
            
        except Exception as e:
            # Fallback to light theme colors
            bg_color = "#ffffff"
            text_color = "#333333"
            link_color = "#3498db"
            highlight_color = "#3498db"
            h1_color = "#2c3e50"
            h2_color = "#34495e"
            h3_color = "#7f8c8d"
            code_bg = "#f4f4f4"
            code_color = "#e74c3c"
            blockquote_bg = "#ecf7fd"
            blockquote_border = "#3498db"
            table_header_bg = "#3498db"
            table_row_alt_bg = "#f9f9f9"
            hr_color = "#e0e0e0"
        
        css = f"""
        <style>
            body {{
                font-family: 'Segoe UI Emoji', 'Segoe UI', 'Apple Color Emoji', 'Noto Color Emoji', Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
                max-width: 750px;
                margin: 0 auto;
            }}
            h1 {{
                color: {h1_color};
                border-bottom: 3px solid {highlight_color};
                padding-bottom: 10px;
                margin-top: 30px;
            }}
            h2 {{
                color: {h2_color};
                border-bottom: 2px solid {h2_color};
                padding-bottom: 8px;
                margin-top: 25px;
            }}
            h3 {{
                color: {h2_color};
                margin-top: 20px;
            }}
            code {{
                background-color: {code_bg};
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Consolas', 'Courier New', monospace;
                color: {code_color};
            }}
            ul, ol {{
                margin-left: 20px;
            }}
            li {{
                margin: 8px 0;
            }}
            a {{
                color: {link_color};
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            hr {{
                border: none;
                border-top: 2px solid {h2_color};
                margin: 30px 0;
                opacity: 0.3;
            }}
            strong {{
                color: {text_color};
                font-weight: 600;
            }}
            blockquote {{
                border-left: 4px solid {blockquote_border};
                padding-left: 15px;
                margin-left: 0;
                background-color: {blockquote_bg};
                padding: 10px 15px;
                border-radius: 3px;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            table th {{
                background-color: {table_header_bg};
                color: white;
                padding: 12px;
                text-align: left;
            }}
            table td {{
                border: 1px solid {h2_color};
                padding: 10px;
            }}
            table tr:nth-child(even) {{
                background-color: {table_row_alt_bg};
            }}
        </style>
        """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            {css}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
    
    def retranslate_ui(self):
        """Update translations when language changes"""
        self.setWindowTitle(lang.get("app.about_title", app_name=self.app_name))
        
        # Update tab titles
        self.tabs.setTabText(0, lang.get("dialogs.about_dialog.tab_about", default="About"))
        self.tabs.setTabText(1, lang.get("dialogs.about_dialog.tab_credits", default="Credits"))
        self.tabs.setTabText(2, lang.get("dialogs.about_dialog.tab_license", default="License"))
        
        # Reload about tab content with new language
        about_widget = self.tabs.widget(0)
        if about_widget and about_widget.layout().count() > 0:
            # Find the text browser in the layout (skip labels and spacing)
            for i in range(about_widget.layout().count()):
                item = about_widget.layout().itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if widget.__class__.__name__ == 'QTextBrowser':
                        about_html = self._get_themed_about_html()
                        widget.setHtml(about_html)
                        break
        
        # Reload credits tab content with new language
        credits_widget = self.tabs.widget(1)
        if credits_widget and credits_widget.layout().count() > 0:
            credits_browser = credits_widget.layout().itemAt(0).widget()
            if credits_browser:
                credits_html = self._get_themed_credits_html()
                credits_browser.setHtml(credits_html)
