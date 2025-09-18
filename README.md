
# YDD Downloader

Flask + yt-dlp pour télécharger des vidéos (YouTube, Instagram, TikTok, Facebook…).

## Démarrage local (Windows PowerShell)

```powershell
# 1) Entrer dans le dossier
cd "C:\chemin\vers\YDD-Downloader"

# 2) Créer/Activer venv
python -m venv .venv
.\.venv\Scripts\activate

# 3) Installer dépendances
pip install -r requirements.txt

# 4) Lancer l'app
python app.py
```

L'app tourne sur `http://127.0.0.1:5000`.

### Cookies (optionnel)
Certains sites nécessitent des cookies (connexion, anti-bot). Exportez vos cookies depuis votre navigateur vers un fichier `cookies.json`
et placez-le **à la racine du projet** (même niveau que `app.py`). Redeployez ensuite.
