import yt_dlp
import os
import sys
import shutil
from .utils import time_to_seconds

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def download_media(url, folder, format_type, quality, start_time, end_time, progress_hook):
    # --- LOGIQUE DE DÉTECTION FFMPEG ---
    if hasattr(sys, '_MEIPASS'):
        # On est dans l'EXE compilé (Windows), on utilise le dossier interne
        ffmpeg_dir = resource_path(".")
    else:
        # On est en développement (Kali/Linux ou Windows)
        # shutil.which trouve automatiquement le chemin de ffmpeg installé sur le système
        ffmpeg_exe = shutil.which("ffmpeg")
        ffmpeg_dir = os.path.dirname(ffmpeg_exe) if ffmpeg_exe else None 

    ydl_opts = {
        'ffmpeg_location': ffmpeg_dir,
        'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'progress_hooks': [progress_hook],
    }

    if format_type == "MP3":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'writethumbnail': True,
            'postprocessors': [
                {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
                {'key': 'FFmpegMetadata', 'add_metadata': True},
                {'key': 'EmbedThumbnail'},
            ],
        })
    else: # MP4
        # On utilise la qualité choisie (ex: 1080) pour filtrer la hauteur
        quality_val = quality.replace("p", "")
        ydl_opts.update({
            'format': f'bestvideo[height<={quality_val}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality_val}][ext=mp4]/best',
            'merge_output_format': 'mp4',
        })

    # Gestion du découpage
    start_sec = time_to_seconds(start_time)
    end_sec = time_to_seconds(end_time)

    if start_sec is not None or end_sec is not None:
        from yt_dlp.utils import download_range_func
        s = start_sec if start_sec is not None else 0
        e = end_sec if end_sec is not None else 999999
        ydl_opts['download_ranges'] = download_range_func(None, [(s, e)])
        ydl_opts['force_keyframes_at_cuts'] = True

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])