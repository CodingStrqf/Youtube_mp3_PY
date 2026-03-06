import os
import json

CONFIG_FILE = "settings.json"

def load_settings():
    """Charge le dossier depuis le fichier JSON s'il existe."""
    default_path = os.path.join(os.path.expanduser("~"), "Music")
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                saved_path = data.get("download_folder", default_path)
                if os.path.exists(saved_path):
                    return saved_path
        except Exception:
            pass
    return default_path

def save_settings(folder_path):
    """Sauvegarde le dossier actuel dans le fichier JSON."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"download_folder": folder_path}, f)
    except Exception as e:
        print(f"Erreur sauvegarde settings: {e}")

def get_short_path(path):
    """Raccourcit le chemin pour l'affichage."""
    return "..." + path[-25:] if len(path) > 25 else path

def time_to_seconds(time_str):
    """Convertit un string 'MM:SS' ou 'HH:MM:SS' en secondes."""
    if not time_str or not time_str.strip():
        return None
    try:
        parts = list(map(int, time_str.strip().split(':')))
        if len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
        elif len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
    except ValueError:
        return None
    return None