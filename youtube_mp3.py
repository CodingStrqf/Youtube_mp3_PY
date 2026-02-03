import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp
import threading
import os

class YoutubeConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Convertisseur YouTube vers MP3")
        self.root.geometry("500x250")
        self.root.resizable(False, False)

        # Variables
        self.download_folder = os.path.join(os.path.expanduser("~"), "Music")
        self.url_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Prêt")

        # --- UI ELEMENTS ---
        
        # Label URL
        tk.Label(root, text="Lien YouTube (Vidéo ou Playlist):", font=("Arial", 10, "bold")).pack(pady=(15, 5))
        
        # Entry URL
        self.url_entry = tk.Entry(root, textvariable=self.url_var, width=50)
        self.url_entry.pack(pady=5)

        # Frame pour le dossier
        folder_frame = tk.Frame(root)
        folder_frame.pack(pady=10)
        
        self.path_label = tk.Label(folder_frame, text=f"Dossier: {self.download_folder}", fg="gray", wraplength=350)
        self.path_label.pack(side=tk.LEFT, padx=5)
        
        tk.Button(folder_frame, text="Choisir...", command=self.choose_directory).pack(side=tk.LEFT)

        # Bouton Télécharger
        self.download_btn = tk.Button(root, text="Convertir en MP3", command=self.start_download_thread, bg="#cc0000", fg="white", font=("Arial", 11, "bold"))
        self.download_btn.pack(pady=15)

        # Status Label
        tk.Label(root, textvariable=self.status_var, fg="blue").pack(pady=5)

    def choose_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_folder = directory
            self.path_label.config(text=f"Dossier: {self.download_folder}")

    def start_download_thread(self):
        url = self.url_var.get()
        if not url:
            messagebox.showerror("Erreur", "Veuillez entrer une URL valide.")
            return

        self.download_btn.config(state=tk.DISABLED, text="Téléchargement en cours...")
        self.status_var.set("Préparation...")
        
        thread = threading.Thread(target=self.download_logic, args=(url,))
        thread.daemon = True
        thread.start()

    def download_logic(self, url):
        # Configuration de yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': False,
            'quiet': True,
            'progress_hooks': [self.progress_hook],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Succès
            self.root.after(0, self.finish_download, "Succès", "Conversion terminée !")
            
        except Exception as e:
            # CORRECTION ICI : On convertit l'erreur en texte immédiatement
            error_message = str(e)
            self.root.after(0, self.finish_download, "Erreur", error_message)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            # On retire les couleurs ANSI qui peuvent polluer l'affichage
            percent = d.get('_percent_str', '0%').strip()
            # Mise à jour thread-safe de l'interface
            self.root.after(0, lambda: self.status_var.set(f"Téléchargement : {percent}"))
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.status_var.set("Conversion en MP3..."))

    def finish_download(self, title, message):
        self.download_btn.config(state=tk.NORMAL, text="Convertir en MP3")
        self.status_var.set(message)
        if title == "Succès":
            messagebox.showinfo(title, message)
        else:
            messagebox.showerror(title, f"Une erreur est survenue :\n{message}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = YoutubeConverterApp(root)
        root.mainloop()
    except Exception as main_e:
        print(f"Erreur critique au lancement : {main_e}")