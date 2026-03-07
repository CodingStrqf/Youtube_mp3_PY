python -m venv venv

source venv/bin/activate

pip install customtkinter yt_dlp ffmpeg pyinstaller

.exe windows :
pyinstaller --noconsole --onefile --collect-all customtkinter youtube_mp3_v2.py

# Windows compile
C'est une erreur classique sous Linux/Kali. PyInstaller a besoin de la librairie partagée de Python pour "emballer" l'interpréteur, et elle n'est pas installée par défaut avec la version standard de Python.

Voici comment régler le problème et une **mise en garde très importante** concernant le fichier que vous allez générer.

### 1. La solution immédiate

Vous devez installer le paquet de développement pour Python 3.13. Ouvrez votre terminal et lancez :

```bash
sudo apt update
sudo apt install libpython3.13-dev

```

*Si cette commande ne trouve pas le paquet, essayez celle-ci (plus générique) :*

```bash
sudo apt install python3-dev

```

Une fois installé, relancez votre commande PyInstaller :

```bash
pyinstaller --noconsole --onefile youtube_mp3.py

pyinstaller --noconsole --onefile --icon="icone.ico" --name="YT_Downloader" main.py

```

---

### 2. ATTENTION : Problème de compatibilité (Windows vs Linux)

Je vois dans vos logs que vous êtes sous **WSL2 (Linux)** :
`Platform: Linux-6.6.87.2-microsoft-standard-WSL2`

Il y a un piège important : **PyInstaller n'est pas un compilateur croisé.**

* Si vous créez l'exécutable sous **Linux (Kali/WSL)**, le fichier résultant (dans le dossier `dist`) sera un exécutable **Linux**.
* Ce fichier **ne fonctionnera pas** sur un PC Windows classique (il ne sera pas un `.exe`).

**Si votre objectif est de donner cette application à des amis qui ont Windows :**
Vous ne pouvez pas utiliser Kali/WSL pour générer le `.exe`. Vous devez :

1. Installer Python **sur Windows directement** (pas dans WSL).
2. Installer les librairies (`pip install yt-dlp pyinstaller`) dans l'invite de commande Windows (PowerShell ou CMD).
3. Lancer la commande `pyinstaller` depuis Windows.

Voulez-vous que je vous explique comment faire cette manipulation côté Windows pour avoir un vrai `.exe` ?








===============
https://www.youtube.com/watch?v=4lRWIQzuge8

Nouvelles features : 
- Liste d'attente
- Selection de vidéo dans la playlist 
- Previsualisation de la vidéo pour savoir comment la couper 
- Normalisation Audio : Utiliser FFmpeg pour que tous les MP3 téléchargés aient le même niveau sonore

- Upscaler de vidéo 
    - https://cel.hal.science/cel-00125868v2/file/Coursimage08.pdf
    - https://perso.univ-rennes1.fr/pierre.maurel/IMA/CM/ima03_restauration_presentation.pdf


480p    720x480 pixels
720p	1280x720 pixels	
1080p	1920x1080 pixels
2160p	3840x2160 pixels
4320p	7680x4320 pixels