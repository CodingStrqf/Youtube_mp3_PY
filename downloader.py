import yt_dlp
import os
from utils import time_to_seconds

def download_media(url, folder, format_type, start_time, end_time, progress_hook):
    """Gère le téléchargement via yt_dlp."""
    
    ydl_opts = {
        'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'progress_hooks': [progress_hook],
    }

    # -- Configuration MP3 vs MP4 --
    if format_type == "MP3":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['writethumbnail'] = True
        ydl_opts['postprocessors'] = [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
            {'key': 'FFmpegMetadata', 'add_metadata': True},
            {'key': 'EmbedThumbnail'},
        ]
    else: # MP4
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        ydl_opts['merge_output_format'] = 'mp4'

    # -- Configuration du découpage (Time range) --
    start_sec = time_to_seconds(start_time)
    end_sec = time_to_seconds(end_time)

    if start_sec is not None or end_sec is not None:
        from yt_dlp.utils import download_range_func
        # Si la fin n'est pas spécifiée, on met une valeur très grande
        start = start_sec if start_sec is not None else 0
        end = end_sec if end_sec is not None else 999999
        ydl_opts['download_ranges'] = download_range_func(None, [(start, end)])
        ydl_opts['force_keyframes_at_cuts'] = True # Nécessaire pour des coupes précises via FFmpeg

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])