"""
Module de vérification de version pour DAOC Character Manager
Vérifie si une nouvelle version est disponible sur GitHub
"""

import requests
import logging
from packaging import version
import urllib3

# Désactiver les warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

module_logger = logging.getLogger(__name__)


def check_for_updates(current_version: str) -> dict:
    """
    Vérifie si une nouvelle version est disponible sur GitHub
    
    Args:
        current_version: Version actuelle du logiciel (ex: "0.107")
    
    Returns:
        dict: {
            'update_available': bool,
            'current_version': str,
            'latest_version': str,
            'error': str or None
        }
    """
    try:
        # URL du fichier version.txt sur GitHub (branche main)
        url = "https://raw.githubusercontent.com/ChristophePelichet/DAOC-Character-Management/main/version.txt"
        
        module_logger.info(f"Vérification de version : actuelle={current_version}")
        
        # Désactiver la vérification SSL pour éviter les problèmes de certificat
        response = requests.get(url, timeout=5, verify=False)
        response.raise_for_status()
        
        latest_version = response.text.strip()
        module_logger.info(f"Dernière version disponible : {latest_version}")
        
        # Comparaison de versions
        try:
            update_available = version.parse(latest_version) > version.parse(current_version)
        except Exception as e:
            module_logger.error(f"Erreur lors de la comparaison de versions: {e}")
            # Fallback: comparaison de chaînes simple
            update_available = latest_version != current_version
        
        return {
            'update_available': update_available,
            'current_version': current_version,
            'latest_version': latest_version,
            'error': None
        }
        
    except requests.Timeout:
        module_logger.warning("Timeout lors de la vérification de version")
        return {
            'update_available': False,
            'current_version': current_version,
            'latest_version': None,
            'error': 'timeout'
        }
    except requests.RequestException as e:
        module_logger.warning(f"Erreur réseau lors de la vérification de version: {e}")
        return {
            'update_available': False,
            'current_version': current_version,
            'latest_version': None,
            'error': 'network_error'
        }
    except Exception as e:
        module_logger.error(f"Erreur inattendue lors de la vérification de version: {e}")
        return {
            'update_available': False,
            'current_version': current_version,
            'latest_version': None,
            'error': str(e)
        }
