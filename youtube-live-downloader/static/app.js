const $ = (id) => document.getElementById(id);

const urlInput = $("url");
const checkBtn = $("check-btn");
const downloadBtn = $("download-btn");
const infoBox = $("info");
const errorBox = $("error");
const jobsList = $("jobs-list");

function showError(msg) {
  errorBox.textContent = msg;
  errorBox.classList.remove("hidden");
}
function clearError() {
  errorBox.textContent = "";
  errorBox.classList.add("hidden");
}

function fmtBytes(n) {
  if (!n) return "";
  const units = ["o", "Ko", "Mo", "Go"];
  let i = 0;
  while (n >= 1024 && i < units.length - 1) { n /= 1024; i++; }
  return `${n.toFixed(1)} ${units[i]}`;
}

function fmtSpeed(n) {
  return n ? `${fmtBytes(n)}/s` : "";
}

async function checkUrl() {
  const url = urlInput.value.trim();
  if (!url) return;
  clearError();
  infoBox.classList.add("hidden");
  checkBtn.disabled = true;
  checkBtn.textContent = "…";
  try {
    const res = await fetch("/api/info", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Erreur");
    const badge = data.is_live
      ? '<span class="badge live">● EN DIRECT</span>'
      : data.was_live
      ? '<span class="badge vod">Live terminé</span>'
      : '<span class="badge vod">Vidéo</span>';
    infoBox.innerHTML = `<strong>${data.title || "Sans titre"}</strong>${badge}<br>` +
      `<span class="job-meta">${data.uploader || ""}</span>`;
    infoBox.classList.remove("hidden");
  } catch (e) {
    showError(e.message);
  } finally {
    checkBtn.disabled = false;
    checkBtn.textContent = "Vérifier";
  }
}

async function startDownload() {
  const url = urlInput.value.trim();
  if (!url) { showError("Veuillez saisir un lien."); return; }
  clearError();
  downloadBtn.disabled = true;
  try {
    const res = await fetch("/api/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url,
        quality: $("quality").value,
        live_from_start: $("live-from-start").checked,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Erreur");
    refreshJobs();
  } catch (e) {
    showError(e.message);
  } finally {
    downloadBtn.disabled = false;
  }
}

function renderJob(job) {
  const statusLabels = {
    queued: "En attente…",
    downloading: "Téléchargement",
    processing: "Traitement…",
    done: "Terminé ✓",
    error: "Erreur",
  };
  let detail = "";
  if (job.status === "downloading") {
    const parts = [];
    if (job.percent != null) parts.push(`${job.percent}%`);
    if (job.speed) parts.push(fmtSpeed(job.speed));
    if (job.eta) parts.push(`ETA ${job.eta}s`);
    if (job.total_bytes) parts.push(fmtBytes(job.total_bytes));
    detail = parts.join(" · ");
  } else if (job.status === "error") {
    detail = job.error || "";
  }
  const pct = job.percent != null ? job.percent : (job.status === "done" ? 100 : 0);
  const showBar = ["downloading", "processing", "done"].includes(job.status);
  return `
    <li class="job">
      <div class="job-title">${job.title || job.filename || job.url}</div>
      <div class="job-meta">${job.quality} · ${job.created_at}</div>
      <div class="job-status status-${job.status}">${statusLabels[job.status] || job.status} ${detail ? "— " + detail : ""}</div>
      ${showBar ? `<div class="progress"><div class="progress-bar" style="width:${pct}%"></div></div>` : ""}
    </li>`;
}

async function refreshJobs() {
  try {
    const res = await fetch("/api/jobs");
    const jobs = await res.json();
    if (!jobs.length) {
      jobsList.innerHTML = '<li class="empty">Aucun téléchargement pour le moment.</li>';
      return;
    }
    jobsList.innerHTML = jobs.map(renderJob).join("");
  } catch (e) {
    /* silencieux : on réessaiera au prochain cycle */
  }
}

checkBtn.addEventListener("click", checkUrl);
downloadBtn.addEventListener("click", startDownload);
urlInput.addEventListener("keydown", (e) => { if (e.key === "Enter") checkUrl(); });

refreshJobs();
setInterval(refreshJobs, 1500);
