# StudyMate AI — Full Stack Setup Guide
### PDF-to-Quiz Platform | Flask + Supabase + Google Gemini

---

## Project Structure

```
studymate/
├── backend/
│   ├── app.py                  ← Flask entry point
│   ├── database.py             ← Supabase client
│   ├── requirements.txt        ← Python dependencies
│   ├── schema.sql              ← Run this in Supabase SQL Editor
│   ├── .env                    ← Your secret keys (edit this)
│   ├── routes/
│   │   ├── auth.py             ← Register, login, JWT auth
│   │   ├── upload.py           ← PDF upload + text extraction
│   │   ├── quiz.py             ← Generate + retrieve quizzes
│   │   └── results.py          ← Submit + retrieve results
│   └── services/
│       ├── pdf_parser.py       ← PyMuPDF text extraction
│       └── ai_service.py       ← Gemini API + demo mode
└── frontend/
    ├── index.html              ← Complete single-file frontend
    └── api.js                  ← API helper functions (reference)
```

---

## Step 1 — Set Up Supabase (Free)

1. Go to https://supabase.com and create a free account
2. Click **New Project** → give it a name → set a database password → click Create
3. Wait for the project to be ready (~1 minute)
4. Go to **Settings → API** and copy:
   - **Project URL** (looks like: `https://abcdef.supabase.co`)
   - **anon public key** (long string starting with `eyJ...`)
5. Go to **SQL Editor → New Query**
6. Copy the entire contents of `backend/schema.sql` and paste it → click **Run**
7. Go to **Storage → Create bucket** → name it `studymate-pdfs` → set to Public → Save

---

## Step 2 — Configure Your .env File

Open `backend/.env` and fill in your values:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SECRET_KEY=any-random-string-here-like-studymate2025
GEMINI_API_KEY=DEMO
SUPABASE_BUCKET=studymate-pdfs
```

> Leave GEMINI_API_KEY=DEMO for now. The app will work with demo questions.
> When ready for real questions: get a FREE key at https://aistudio.google.com

---

## Step 3 — Install Python & Run the Backend

Make sure Python 3.10+ is installed. Then:

```bash
# Navigate to backend folder
cd studymate/backend

# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Run the Flask server
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

Test it by opening: http://localhost:5000/api/health
You should see: `{"status": "ok", "message": "StudyMate AI backend is running"}`

---

## Step 4 — Open the Frontend

Simply open `frontend/index.html` in your browser.
No server needed for the frontend — it's a plain HTML file.

> On Windows: double-click `index.html`
> Or drag it into Chrome/Firefox

---

## Step 5 — Test the Full App

1. Open `frontend/index.html` in your browser
2. Click **Create one** to register a new account
3. You will be logged in automatically
4. Upload any PDF lecture note
5. Select your settings (difficulty, number of questions)
6. Click **Generate Questions from PDF**
7. You will be taken to CBT mode automatically
8. Answer questions and click Submit Quiz
9. View your results and feedback

---

## Getting a Real Gemini API Key (Free)

When you are ready to generate questions from YOUR actual PDF content:

1. Go to https://aistudio.google.com
2. Sign in with your Google account
3. Click **Get API Key → Create API Key**
4. Copy the key
5. Open `backend/.env`
6. Replace `GEMINI_API_KEY=DEMO` with `GEMINI_API_KEY=your-key-here`
7. Restart the Flask server

That's it — no payment, no credit card needed.

---

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Create new account |
| POST | /api/auth/login | Login and get token |
| GET | /api/auth/me | Get current user |
| POST | /api/upload/pdf | Upload PDF file |
| POST | /api/quiz/generate | Generate quiz from document |
| GET | /api/quiz/ | Get all my quizzes |
| GET | /api/quiz/:id | Get single quiz |
| POST | /api/quiz/:id/share | Make quiz shareable |
| GET | /api/quiz/shared/:id | Get shared quiz (no auth) |
| POST | /api/results/submit | Submit quiz answers |
| GET | /api/results/quiz/:id | Get results for a quiz |
| GET | /api/results/stats | Get overall stats |

---

## Tech Stack Summary

| Layer | Technology | Cost |
|-------|-----------|------|
| Frontend | HTML + CSS + Vanilla JavaScript | Free |
| Backend | Python 3 + Flask | Free |
| Database | PostgreSQL on Supabase | Free |
| File Storage | Supabase Storage | Free (1GB) |
| PDF Extraction | PyMuPDF | Free |
| AI Questions | Google Gemini 1.5 Flash API | Free |
| Auth | JWT (PyJWT + bcrypt) | Free |
| Frontend Hosting | Open index.html directly OR Vercel | Free |
| Backend Hosting | Render.com (deploy app.py) | Free |

**Total cost = ₦0**

---

## Deploying to Render (Optional — to host online)

1. Push your backend folder to GitHub
2. Go to https://render.com → New → Web Service
3. Connect your GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python app.py`
6. Add all your .env variables in the Environment section
7. Click Deploy
8. Update `BASE` in `frontend/index.html` from `http://localhost:5000/api` to your Render URL

---

## Troubleshooting

**"CORS error" in browser console**
→ Make sure Flask is running on port 5000
→ Check that CORS is enabled in app.py (it is by default)

**"Connection refused" error**
→ Flask server is not running. Run `python app.py` in the backend folder

**"Could not extract text from PDF"**
→ The PDF might be a scanned image (not text-based)
→ Try a different PDF — lecture notes downloaded as PDF work best

**Supabase connection error**
→ Double-check your SUPABASE_URL and SUPABASE_ANON_KEY in .env
→ Make sure you ran the schema.sql in Supabase SQL Editor

---

Built for CMP 431 — Net-Centric Computing | Benue State University
