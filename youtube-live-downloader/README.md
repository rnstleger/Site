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

## Configuration (variables d'environnement)

Toutes optionnelles :

| Variable | Effet |
|----------|-------|
| `YTDL_DOWNLOAD_DIR` | Dossier de destination des fichiers |
| `YTDL_COOKIES_FILE` | Chemin d'un fichier cookies (format Netscape) pour l'authentification YouTube |
| `YTDL_COOKIES_FROM_BROWSER` | Importer les cookies depuis un navigateur : `chrome`, `firefox`, `edge`, `brave`, `safari`… |
| `YTDL_PLAYER_CLIENT` | Forcer le « player client » YouTube (`android`, `ios`, `tv`, `web`…) en cas d'erreur 403 |
| `YTDL_SYSTEM_CERTS` | Utiliser le magasin de certificats système plutôt que `certifi` (utile derrière un proxy d'entreprise) |

Exemple :

```bash
export YTDL_COOKIES_FROM_BROWSER=chrome
python app.py
```

## Résolution de problèmes

- **« Sign in to confirm you're not a bot » / HTTP 403** : YouTube bloque les
  requêtes provenant de certaines adresses IP (centres de données, VPN, réseaux
  très sollicités). Solution : fournir vos cookies via `YTDL_COOKIES_FROM_BROWSER`
  ou `YTDL_COOKIES_FILE`. Sur une connexion résidentielle classique, le
  téléchargement fonctionne généralement sans cookies.
- **« certificate verify failed: self-signed certificate »** : vous êtes derrière
  un proxy qui inspecte le trafic TLS. Définissez `YTDL_SYSTEM_CERTS=1` (ou
  `SSL_CERT_FILE` vers le bundle CA de votre organisation). C'est détecté
  automatiquement si `SSL_CERT_FILE`/`REQUESTS_CA_BUNDLE` est déjà défini.
- **Format indisponible** : essayez une autre qualité, ou « Meilleure
  disponible ».
- yt-dlp évolue vite ; en cas d'erreur d'extraction, mettez-le à jour :
  `pip install -U yt-dlp`.

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
