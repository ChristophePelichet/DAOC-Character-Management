#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de la fenêtre Debug Eden
Génère des logs de test pour vérifier la coloration et le fonctionnement
"""

import sys
import logging
from pathlib import Path

# Ajouter le dossier parent au path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from PySide6.QtWidgets import QApplication
from UI.debug_window import EdenDebugWindow

# Configurer le logger Eden
eden_logger = logging.getLogger('eden')
eden_logger.setLevel(logging.DEBUG)

def generate_test_logs():
    """Génère des logs de test pour vérifier la coloration"""
    
    print("\n🧪 Génération de logs de test pour la fenêtre Debug Eden...\n")
    
    # Logs de succès (vert)
    eden_logger.info("✅ Connexion Herald réussie")
    eden_logger.info("✅ Chrome (Selenium Manager)")
    eden_logger.info("✅ 4 cookies sauvegardés avec succès")
    
    # Logs d'erreur (rouge)
    eden_logger.error("❌ Échec de l'initialisation du driver")
    eden_logger.error("❌ Erreur de connexion au Herald")
    
    # Logs d'avertissement (orange)
    eden_logger.warning("⚠️ Attention : Cookies expirés")
    eden_logger.warning("⚠️ Le navigateur préféré n'est pas disponible")
    
    # Logs de recherche (jaune)
    eden_logger.info("🔍 Recherche de personnages : 'Ewoline'")
    eden_logger.info("🔍 Détection des navigateurs disponibles...")
    
    # Logs de navigateur (bleu)
    eden_logger.info("🌐 Ouverture du navigateur Chrome")
    eden_logger.info("🌐 Initialisation de Edge pour le scraping")
    eden_logger.info("🌐 Navigateur Firefox détecté")
    
    # Logs de cookies (violet)
    eden_logger.info("🍪 Chargement de 4 cookies : eden_daoc_sid, eden_daoc_u, eden_daoc_k, POWSESS")
    eden_logger.info("🍪 Sauvegarde des cookies dans eden_cookies.pkl")
    eden_logger.info("🍪 Authentification via cookies réussie")
    
    # Logs de configuration (cyan)
    eden_logger.info("📋 Configuration lue : preferred_browser='Edge', allow_download=False")
    eden_logger.info("📋 Ordre de priorité des navigateurs : Edge, Chrome, Firefox")
    eden_logger.info("📋 Paramètres de scraping chargés")
    
    # Logs mixtes (plusieurs couleurs)
    eden_logger.info("🔍 Détection des navigateurs... Chrome trouvé, Edge trouvé")
    eden_logger.info("🍪 Tentative de connexion avec les cookies existants...")
    eden_logger.error("❌ Échec de connexion - Erreur de navigateur")
    eden_logger.info("✅ Reconnexion réussie avec Edge")
    
    # Logs DEBUG (plus détaillés)
    eden_logger.debug("DEBUG: Vérification de l'existence de chromedriver.exe")
    eden_logger.debug("DEBUG: Path système : C:\\Users\\...\\selenium\\chromedriver")
    eden_logger.debug("DEBUG: Cookies trouvés : {'eden_daoc_sid': 'abc123', ...}")
    
    print("✅ Logs de test générés avec succès\n")

def main():
    """Fonction principale"""
    app = QApplication(sys.argv)
    
    # Créer la fenêtre Debug Eden
    window = EdenDebugWindow()
    window.show()
    
    # Générer les logs de test
    generate_test_logs()
    
    print("📝 Fenêtre Debug Eden ouverte")
    print("   - Vérifiez la coloration des logs")
    print("   - Testez le bouton 'Exporter'")
    print("   - Testez le bouton 'Effacer'")
    print("   - Vérifiez le compteur de logs\n")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
