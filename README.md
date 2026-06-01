# Jobflavor

**Decode any job posting in seconds.**

Paste a job description → get a plain-English translation, red flags, must-have vs nice-to-have skills, and a salary estimate. AI-powered, zero config, works right in your browser.

## Features

- 📋 **Plain-English role summary** — no more deciphering corporate buzzwords
- 🚩 **Red flags detected** — underpaid, overqualified, toxic culture signals
- 🎯 **Skills split** — must-have vs nice-to-have, clearly separated
- 💰 **Salary estimate** — low-high range with reasoning
- 🛡️ **Red flag detection** — "fast-paced startup", "wear many hats", "competitive compensation"
- ⚡ **One-click example** — try it before deploying
- 📱 **Fully responsive** — works on mobile and desktop

## How It Works

1. Deploy the Flask backend (free on Render, Railway, or any Python host)
2. Set your `ANTHROPIC_API_KEY` environment variable
3. Open `index.html` in a browser (or serve it from the same host)
4. Paste any job description and hit **Decode**

The API key lives server-side — users never need to provide one.

## Quick Start (Local Development)

```bash
# Backend
pip install flask requests
export ANTHROPIC_API_KEY=your_key_here
python app.py

# Open http://localhost:5000 in your browser
```

Or serve the static files with any web server:

```bash
# Serve index.html only (backend must run separately)
python -m http.server 8080
```

## Deployment

### Render (Free Tier)

1. Create a new **Web Service**
2. Set root directory to `jobflavor`
3. **Build command:** `pip install -r requirements.txt`
4. **Start command:** `python app.py`
5. Add environment variable: `ANTHROPIC_API_KEY` = your key
6. Deploy

The `index.html` is served automatically from the same Flask app (`app.static_folder = '.'`).

### Railway

Same steps — Railway's free tier supports Python Web Services out of the box.

## Tech Stack

- **Frontend:** Vanilla HTML/CSS/JS (no build step, no framework)
- **Backend:** Python Flask
- **AI:** Anthropic Claude API (server-side)

## API

### `POST /decode`

```json
// Request
{ "job_text": "Senior Full-Stack Engineer..." }

// Response
{
  "summary": "Full-stack role at a startup...",
  "verdict": "maybe",
  "verdict_reason": "Reasonable expectations but salary below market",
  "real_role_meaning": "You'll be building and maintaining...",
  "red_flags": [
    { "flag": "Unlimited PTO", "explain": "Often means no actual PTO policy" }
  ],
  "must_have_skills": ["React", "Node.js", "PostgreSQL"],
  "nice_to_have_skills": ["AWS", "Docker"],
  "salary_estimate": {
    "low": 120000,
    "high": 160000,
    "currency": "USD",
    "basis": "Based on market rates for similar roles in 2025"
  }
}
```

### `GET /health`

Returns server status and whether the API key is configured.

## License

MIT