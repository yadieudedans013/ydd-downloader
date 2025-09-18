
import os
import json
from flask import Flask, request, jsonify, render_template, send_file, abort
import subprocess
import tempfile
import shutil
from pathlib import Path

app = Flask(__name__)

# --- Config ---
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Helper to build yt-dlp command
def build_ytdlp_cmd(url, fmt="best", audio_only=False, cookies_path=None, out_tmpl=None):
    cmd = ["yt-dlp", "-N", "8", "--no-warnings", "--no-call-home"]
    # format
    if audio_only:
        # m4a preferred
        cmd += ["-f", "bestaudio[ext=m4a]/bestaudio"]
        cmd += ["--extract-audio", "--audio-format", "m4a"]
    else:
        # mp4  prefer h264+aac if available, else best
        cmd += ["-f", "bv*[ext=mp4][vcodec~='^(avc1|h264)']+ba[ext=m4a]/b[ext=mp4]/bv+ba/b"]
        cmd += ["--merge-output-format", "mp4"]
    # out template
    if out_tmpl:
        cmd += ["-o", out_tmpl]
    # cookies
    if cookies_path and Path(cookies_path).exists():
        cmd += ["--cookies", cookies_path]
    # no playlist by default
    cmd += ["--no-playlist", url]
    return cmd

def run_cmd(cmd, cwd=None, timeout=180):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        ok = p.returncode == 0
        return ok, p.stdout.strip(), p.stderr.strip()
    except subprocess.TimeoutExpired as e:
        return False, "", f"Timeout: {e}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/preview", methods=["POST"])
def preview():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    audio_only = bool(data.get("audio", False))

    if not url:
        return jsonify({"error": "Aucun lien fourni"}), 400

    # Try to fetch basic metadata
    cmd = ["yt-dlp", "--dump-json", "--no-playlist", url]
    # cookies support (optional)
    cookies_path = Path("cookies.json")
    if cookies_path.exists():
        cmd = ["yt-dlp", "--cookies", str(cookies_path), "--dump-json", "--no-playlist", url]

    ok, out, err = run_cmd(cmd, timeout=60)
    if not ok:
        return jsonify({"error": err or out or "Impossible d'obtenir l'aperçu"}), 400
    try:
        info = json.loads(out.splitlines()[-1])
    except Exception:
        return jsonify({"error": "Impossible de lire les métadonnées"}), 400

    thumb = info.get("thumbnail")
    title = info.get("title")
    duration = info.get("duration")
    uploader = info.get("uploader") or info.get("channel")

    return jsonify({
        "title": title,
        "thumbnail": thumb,
        "duration": duration,
        "uploader": uploader,
        "audio": audio_only
    })

@app.route("/api/download", methods=["POST"])
def download():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    quality = data.get("quality", "best")
    audio_only = bool(data.get("audio", False))

    if not url:
        return jsonify({"error": "Aucun lien fourni"}), 400

    # Output temp dir per request
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        out_tmpl = str(tmpdir / ("%(title).80s.%(ext)s"))

        cookies_path = Path("cookies.json") if Path("cookies.json").exists() else None

        cmd = build_ytdlp_cmd(url, fmt=quality, audio_only=audio_only, cookies_path=str(cookies_path) if cookies_path else None, out_tmpl=out_tmpl)
        ok, out, err = run_cmd(cmd, timeout=180)
        if not ok:
            # Common hint for sites needing cookies
            hint = ""
            if "Sign in to confirm" in (out+err) or "login required" in (out+err).lower():
                hint = " Astuce : ajoute un cookies.json exporté depuis ton navigateur."
            return jsonify({"error": (err or out or "Téléchargement échoué") + hint}), 400

        # Find produced file
        files = list(tmpdir.glob("*"))
        if not files:
            return jsonify({"error": "Aucun fichier téléchargé"}), 400

        # Move to persistent dir
        DOWNLOAD_DIR.mkdir(exist_ok=True, parents=True)
        dst = DOWNLOAD_DIR / files[0].name
        shutil.move(str(files[0]), dst)

        return jsonify({
            "ok": True,
            "filename": dst.name,
            "url": f"/download/file/{dst.name}"
        })

@app.route("/download/file/<path:fname>")
def serve_file(fname):
    f = DOWNLOAD_DIR / fname
    if not f.exists():
        abort(404)
    return send_file(f, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
