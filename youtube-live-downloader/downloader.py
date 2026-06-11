"""Gestion des téléchargements YouTube (lives et vidéos) via yt-dlp.

Chaque téléchargement est exécuté dans un thread séparé. L'état de chaque
tâche (job) est conservé en mémoire et exposé à l'interface web pour le suivi
de progression.
"""

from __future__ import annotations

import os
import threading
import uuid
from datetime import datetime
from typing import Any

import yt_dlp


# Dossier de destination des fichiers téléchargés.
DOWNLOAD_DIR = os.environ.get(
    "YTDL_DOWNLOAD_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads"),
)

# Registre en mémoire des tâches de téléchargement, protégé par un verrou.
_jobs: dict[str, dict[str, Any]] = {}
_jobs_lock = threading.Lock()


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _update_job(job_id: str, **fields: Any) -> None:
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job is not None:
            job.update(fields)


def get_job(job_id: str) -> dict[str, Any] | None:
    with _jobs_lock:
        job = _jobs.get(job_id)
        return dict(job) if job is not None else None


def list_jobs() -> list[dict[str, Any]]:
    with _jobs_lock:
        jobs = [dict(j) for j in _jobs.values()]
    jobs.sort(key=lambda j: j["created_at"], reverse=True)
    return jobs


# Correspondance entre le choix de qualité de l'interface et le sélecteur de
# format yt-dlp. Pour les lives, yt-dlp choisit automatiquement le meilleur
# flux disponible selon ces contraintes.
QUALITY_FORMATS = {
    "best": "bestvideo+bestaudio/best",
    "1080": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "720": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "480": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "audio": "bestaudio/best",
}


def fetch_info(url: str) -> dict[str, Any]:
    """Récupère les métadonnées d'une URL sans la télécharger."""
    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {
        "title": info.get("title"),
        "uploader": info.get("uploader"),
        "is_live": bool(info.get("is_live")),
        "was_live": bool(info.get("was_live")),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
    }


def _make_progress_hook(job_id: str):
    def hook(d: dict[str, Any]) -> None:
        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes") or 0
            percent = (downloaded / total * 100) if total else None
            _update_job(
                job_id,
                status="downloading",
                downloaded_bytes=downloaded,
                total_bytes=total or None,
                percent=round(percent, 1) if percent is not None else None,
                speed=d.get("speed"),
                eta=d.get("eta"),
                filename=os.path.basename(d.get("filename") or ""),
            )
        elif status == "finished":
            # Fin du téléchargement d'un flux ; le post-traitement (fusion
            # audio/vidéo) peut encore suivre.
            _update_job(job_id, status="processing", percent=100.0)

    return hook


def _run_download(job_id: str, url: str, quality: str, live_from_start: bool) -> None:
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    outtmpl = os.path.join(DOWNLOAD_DIR, "%(title)s [%(id)s].%(ext)s")

    opts: dict[str, Any] = {
        "format": QUALITY_FORMATS.get(quality, QUALITY_FORMATS["best"]),
        "outtmpl": outtmpl,
        "progress_hooks": [_make_progress_hook(job_id)],
        "noprogress": True,
        "quiet": True,
        "no_warnings": True,
        # Permet de reprendre un live depuis le début plutôt qu'au point
        # courant de diffusion.
        "live_from_start": live_from_start,
        # Continue en cas de fragment manquant (utile pour les lives).
        "ignoreerrors": False,
    }
    if quality == "audio":
        opts["postprocessors"] = [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}
        ]

    _update_job(job_id, status="downloading", started_at=_now())
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title") if isinstance(info, dict) else None
        _update_job(
            job_id,
            status="done",
            percent=100.0,
            title=title,
            finished_at=_now(),
        )
    except Exception as exc:  # noqa: BLE001 - on remonte l'erreur à l'UI
        _update_job(job_id, status="error", error=str(exc), finished_at=_now())


def start_download(url: str, quality: str = "best", live_from_start: bool = True) -> str:
    """Lance un téléchargement en arrière-plan et renvoie l'identifiant du job."""
    job_id = uuid.uuid4().hex[:12]
    with _jobs_lock:
        _jobs[job_id] = {
            "id": job_id,
            "url": url,
            "quality": quality,
            "status": "queued",
            "percent": None,
            "created_at": _now(),
            "title": None,
            "filename": None,
            "error": None,
        }
    thread = threading.Thread(
        target=_run_download,
        args=(job_id, url, quality, live_from_start),
        daemon=True,
    )
    thread.start()
    return job_id
