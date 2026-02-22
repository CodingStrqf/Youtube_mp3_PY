import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import re
from utils import load_settings, save_settings, get_short_path
from downloader import download_media

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Downloader PRO")
        self.geometry("600x550") # Fenêtre un peu plus haute pour les nouvelles options
        self.resizable(False, False)

        self.download_folder = load_settings()
        self.status_message = "En attente d'un lien..."

        self.setup_ui()

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.label_title = ctk.CTkLabel(self.main_frame, text="Téléchargeur YouTube", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_title.pack(pady=(20, 10))

        # URL
        self.entry_url = ctk.CTkEntry(self.main_frame, placeholder_text="Collez le lien YouTube ici...", width=400, height=40)
        self.entry_url.pack(pady=10)

        # Choix MP3 / MP4
        self.format_var = ctk.StringVar(value="MP3")
        self.seg_button = ctk.CTkSegmentedButton(self.main_frame, values=["MP3", "MP4"], variable=self.format_var, width=200)
        self.seg_button.pack(pady=10)

        # Options de découpage (Temps)
        self.time_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.time_frame.pack(pady=5)
        
        self.entry_start = ctk.CTkEntry(self.time_frame, placeholder_text="Début (ex: 01:15)", width=120)
        self.entry_start.pack(side="left", padx=10)
        
        self.entry_end = ctk.CTkEntry(self.time_frame, placeholder_text="Fin (ex: 02:30)", width=120)
        self.entry_end.pack(side="left", padx=10)

        # Dossier
        self.folder_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.folder_frame.pack(pady=15)

        self.btn_folder = ctk.CTkButton(self.folder_frame, text="📂 Dossier", command=self.choose_directory, width=100, fg_color="#444")
        self.btn_folder.pack(side="left", padx=5)

        self.label_path = ctk.CTkLabel(self.folder_frame, text=get_short_path(self.download_folder), text_color="gray", font=("Arial", 12))
        self.label_path.pack(side="left", padx=5)

        # Bouton Télécharger
        self.btn_download = ctk.CTkButton(self.main_frame, text="DÉMARRER", command=self.start_download_thread, 
                                          width=300, height=50, font=ctk.CTkFont(size=15, weight="bold"),
                                          fg_color="#1f538d", hover_color="#163e6b")
        self.btn_download.pack(pady=(20, 10))

        # Statut & Progrès
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        self.label_status = ctk.CTkLabel(self.main_frame, text=self.status_message, text_color="#1f538d")
        self.label_status.pack(pady=5)

    def choose_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_folder = directory
            self.label_path.configure(text=get_short_path(self.download_folder))
            save_settings(self.download_folder)

    def start_download_thread(self):
        url = self.entry_url.get()
        if not url:
            self.label_status.configure(text="Erreur : Lien vide !", text_color="red")
            return

        self.btn_download.configure(state="disabled", text="Traitement en cours...")
        self.progress_bar.set(0)
        self.label_status.configure(text="Initialisation...", text_color="white")
        
        # Récupération des paramètres
        fmt = self.format_var.get()
        start = self.entry_start.get()
        end = self.entry_end.get()

        thread = threading.Thread(target=self.run_download, args=(url, fmt, start, end))
        thread.daemon = True
        thread.start()

    def run_download(self, url, fmt, start, end):
        try:
            download_media(url, self.download_folder, fmt, start, end, self.progress_hook)
            self.after(0, self.finish_download, "Succès", "Terminé avec succès !")
        except Exception as e:
            self.after(0, self.finish_download, "Erreur", str(e))

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%', '')
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                p = ansi_escape.sub('', p)
                progress_val = float(p) / 100
                self.after(0, lambda: self.update_progress(progress_val, f"Téléchargement : {p}%"))
            except:
                pass
        elif d['status'] == 'finished':
            self.after(0, lambda: self.update_progress(1.0, "Conversion/Finalisation..."))

    def update_progress(self, val, text):
        self.progress_bar.set(val)
        self.label_status.configure(text=text, text_color="white")

    def finish_download(self, state, message):
        self.btn_download.configure(state="normal", text="DÉMARRER")
        self.progress_bar.set(0 if state == "Erreur" else 1)
        color = "green" if state == "Succès" else "red"
        self.label_status.configure(text=message, text_color=color)
        
        if state == "Erreur":
            messagebox.showerror("Erreur", message)
        else:
            messagebox.showinfo("Terminé", "Tout est prêt dans votre dossier !")