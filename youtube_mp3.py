import customtkinter as ctk
from tkinter import filedialog, messagebox
import yt_dlp
import threading
import os
import json

# Configuration du thème
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PersistantConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre
        self.title("YouTube Audio Downloader")
        self.geometry("600x400")
        self.resizable(False, False)

        # --- GESTION DE LA PERSISTANCE ---
        self.config_file = "settings.json"
        # On charge le dossier sauvegardé, sinon on prend "Music" par défaut
        self.download_folder = self.load_settings()
        
        self.status_message = "En attente d'un lien..."

        # --- LAYOUT ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Cadre Principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Titre
        self.label_title = ctk.CTkLabel(self.main_frame, text="Convertisseur YouTube MP3", 
                                      font=ctk.CTkFont(size=20, weight="bold"))
        self.label_title.pack(pady=(20, 10))

        # Champ URL
        self.entry_url = ctk.CTkEntry(self.main_frame, placeholder_text="Collez le lien YouTube ici...", 
                                    width=400, height=40)
        self.entry_url.pack(pady=10)

        # Sélection Dossier
        self.folder_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.folder_frame.pack(pady=5)

        self.btn_folder = ctk.CTkButton(self.folder_frame, text="📂 Choisir Dossier", 
                                      command=self.choose_directory, width=120, fg_color="#444")
        self.btn_folder.pack(side="left", padx=5)

        # On affiche le dossier chargé
        self.label_path = ctk.CTkLabel(self.folder_frame, text=self.get_short_path(self.download_folder), 
                                     text_color="gray", font=("Arial", 12))
        self.label_path.pack(side="left", padx=5)

        # Bouton Télécharger
        self.btn_download = ctk.CTkButton(self.main_frame, text="DÉMARRER LA CONVERSION", 
                                        command=self.start_download_thread, 
                                        width=300, height=50, 
                                        font=ctk.CTkFont(size=15, weight="bold"),
                                        fg_color="#1f538d", hover_color="#163e6b")
        self.btn_download.pack(pady=(20, 10))

        # Barre de progression
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        # Label Statut
        self.label_status = ctk.CTkLabel(self.main_frame, text=self.status_message, text_color="#1f538d")
        self.label_status.pack(pady=5)

    # --- NOUVELLES FONCTIONS DE SAUVEGARDE ---

    def load_settings(self):
        """Charge le dossier depuis le fichier JSON s'il existe"""
        default_path = os.path.join(os.path.expanduser("~"), "Music")
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    saved_path = data.get("download_folder", default_path)
                    # Vérifie si le dossier sauvegardé existe toujours
                    if os.path.exists(saved_path):
                        return saved_path
            except:
                pass # Si erreur lecture, on ignore
        
        return default_path

    def save_settings(self):
        """Sauvegarde le dossier actuel dans le fichier JSON"""
        data = {"download_folder": self.download_folder}
        try:
            with open(self.config_file, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Erreur sauvegarde settings: {e}")

    def get_short_path(self, path):
        """Raccourcit le chemin pour l'affichage"""
        return "..." + path[-25:] if len(path) > 25 else path

    # -----------------------------------------

    def choose_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_folder = directory
            self.label_path.configure(text=self.get_short_path(self.download_folder))
            self.save_settings() # <--- On sauvegarde dès qu'on change !

    def start_download_thread(self):
        url = self.entry_url.get()
        if not url:
            self.label_status.configure(text="Erreur : Lien vide !", text_color="red")
            return

        self.btn_download.configure(state="disabled", text="Téléchargement...")
        self.progress_bar.set(0)
        self.label_status.configure(text="Initialisation...", text_color="white")
        
        thread = threading.Thread(target=self.download_logic, args=(url,))
        thread.daemon = True
        thread.start()

    def download_logic(self, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'writethumbnail': True,
            'postprocessors': [
                {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
                {'key': 'FFmpegMetadata', 'add_metadata': True},
                {'key': 'EmbedThumbnail'},
            ],
            'noplaylist': False,
            'quiet': True,
            'progress_hooks': [self.progress_hook],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.after(0, self.finish_download, "Succès", "Conversion terminée !")
        except Exception as e:
            self.after(0, self.finish_download, "Erreur", str(e))

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%', '')
                # Nettoyage des codes couleurs ANSI qui peuvent trainer sous Linux
                import re
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                p = ansi_escape.sub('', p)
                
                progress_val = float(p) / 100
                self.after(0, lambda: self.update_progress(progress_val, f"Téléchargement : {p}%"))
            except:
                pass
        elif d['status'] == 'finished':
            self.after(0, lambda: self.update_progress(1.0, "Conversion MP3..."))

    def update_progress(self, val, text):
        self.progress_bar.set(val)
        self.label_status.configure(text=text, text_color="white")

    def finish_download(self, state, message):
        self.btn_download.configure(state="normal", text="DÉMARRER LA CONVERSION")
        self.progress_bar.set(0 if state == "Erreur" else 1)
        color = "green" if state == "Succès" else "red"
        self.label_status.configure(text=message, text_color=color)
        if state == "Erreur":
            messagebox.showerror("Erreur", message)
        else:
            messagebox.showinfo("Terminé", "Tout est prêt dans votre dossier !")

if __name__ == "__main__":
    app = PersistantConverterApp()
    app.mainloop()