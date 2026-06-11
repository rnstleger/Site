"""Application web Flask pour télécharger des lives (et vidéos) YouTube.

Lancement :
    pip install -r requirements.txt
    python app.py
Puis ouvrir http://localhost:5000 dans un navigateur.
"""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request

import downloader

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/info")
def api_info():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not url:
        return jsonify({"error": "URL manquante"}), 400
    try:
        return jsonify(downloader.fetch_info(url))
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 400


@app.post("/api/download")
def api_download():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    quality = data.get("quality") or "best"
    live_from_start = bool(data.get("live_from_start", True))
    if not url:
        return jsonify({"error": "URL manquante"}), 400
    job_id = downloader.start_download(url, quality, live_from_start)
    return jsonify({"id": job_id})


@app.get("/api/jobs")
def api_jobs():
    return jsonify(downloader.list_jobs())


@app.get("/api/jobs/<job_id>")
def api_job(job_id: str):
    job = downloader.get_job(job_id)
    if job is None:
        return jsonify({"error": "Tâche introuvable"}), 404
    return jsonify(job)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
