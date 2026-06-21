# InsureWise AI

AI-powered health insurance navigator — USAII Global AI Hackathon 2026.

## Setup

1. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

2. **Add your Gemini API key**
   - Open the `.env` file
   - Replace `PASTE_YOUR_GEMINI_API_KEY_HERE` with your key from https://aistudio.google.com

3. **Run locally**
   ```
   python app.py
   ```
   Then open http://localhost:5000 in your browser.

## Deploying to Render (free)

1. Push this repo to GitHub (the `.env` file is in `.gitignore` — it will NOT be uploaded)
2. Go to https://render.com and create a free account
3. New → Web Service → connect your GitHub repo
4. Set:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python app.py`
5. Under **Environment Variables**, add:
   - Key: `GEMINI_API_KEY`
   - Value: your actual Gemini key
6. Deploy — Render gives you a live public URL

## Note
The API key is stored only in `.env` locally and in Render's environment variables when deployed. It is never in the code or on GitHub.
