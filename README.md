
# YDD Downloader

Flask + yt-dlp pour tÃ©lÃ©charger des vidÃ©os (YouTube, Instagram, TikTok, Facebookâ€¦).

## DÃ©marrage local (Windows PowerShell)

```powershell
# 1) Entrer dans le dossier
cd "C:\chemin\vers\YDD-Downloader"

# 2) CrÃ©er/Activer venv
python -m venv .venv
.\.venv\Scripts\activate

# 3) Installer dÃ©pendances
pip install -r requirements.txt

# 4) Lancer l'app
python app.py
```

L'app tourne sur `http://127.0.0.1:5000`.

### Cookies (optionnel)
Certains sites nÃ©cessitent des cookies (connexion, anti-bot). Exportez vos cookies depuis votre navigateur vers un fichier `cookies.txt`
et placez-le **Ã  la racine du projet** (mÃªme niveau que `app.py`). Redeployez ensuite.

