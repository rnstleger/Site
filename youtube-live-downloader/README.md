# Téléchargeur de lives YouTube

Petite application web pour télécharger des **lives YouTube** (en cours ou
terminés) ainsi que des vidéos classiques, à partir d'un simple lien. Construite
avec **Flask** et **yt-dlp**.

![interface](https://img.shields.io/badge/Flask-yt--dlp-e23b3b)

## Fonctionnalités

- 🔗 Téléchargement à partir d'un lien YouTube
- 🔴 Prise en charge des **lives** en cours, avec option « reprendre depuis le début »
- 🎚️ Choix de la qualité (meilleure, 1080p, 720p, 480p, ou **audio MP3** seulement)
- 📊 Suivi de progression en temps réel (vitesse, ETA, pourcentage)
- 🗂️ File de plusieurs téléchargements en parallèle

## Prérequis

- **Python 3.10+**
- **ffmpeg** installé et accessible dans le `PATH` (nécessaire pour fusionner
  l'audio/vidéo et convertir en MP3).
  - macOS : `brew install ffmpeg`
  - Debian/Ubuntu : `sudo apt install ffmpeg`
  - Windows : [télécharger ffmpeg](https://ffmpeg.org/download.html)

## Installation

```bash
cd youtube-live-downloader
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

## Lancement

```bash
python app.py
```

Puis ouvrir **http://localhost:5000** dans un navigateur.

1. Collez le lien YouTube.
2. (Optionnel) Cliquez sur **Vérifier** pour voir le titre et savoir s'il s'agit
   d'un live.
3. Choisissez la qualité, puis cliquez sur **Télécharger**.

Les fichiers sont enregistrés dans le dossier `downloads/`. On peut changer cet
emplacement via la variable d'environnement `YTDL_DOWNLOAD_DIR`.

## Notes sur les lives

- Pour un live **en cours**, l'option « reprendre depuis le début »
  (`--live-from-start`) télécharge depuis le tout début de la diffusion. Sans
  cette option, le téléchargement commence au point courant et se poursuit
  jusqu'à la fin du live.
- Un live très long peut prendre un temps important et générer un fichier
  volumineux.

## Architecture

| Fichier | Rôle |
|---------|------|
| `app.py` | Serveur Flask et points d'API (`/api/info`, `/api/download`, `/api/jobs`) |
| `downloader.py` | Encapsulation de yt-dlp, gestion des tâches en arrière-plan et suivi de progression |
| `templates/index.html` | Interface web |
| `static/app.js` | Logique côté client (appels API, rafraîchissement) |
| `static/style.css` | Styles |

## Avertissement

Cet outil est destiné à un usage personnel et au téléchargement de contenus dont
vous détenez les droits ou pour lesquels vous y êtes autorisé. Respectez les
[conditions d'utilisation de YouTube](https://www.youtube.com/t/terms) et le
droit d'auteur applicable.
