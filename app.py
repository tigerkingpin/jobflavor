"""
Jobflavor — Flask backend
Holds the Anthropic API key server-side, exposes a /decode endpoint.
Users call /decode from the browser — no API key needed client-side.
"""

import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__,
            static_folder='.',
            static_url_path='')

# Load from environment variable
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
MODEL = 'claude-sonnet-4-20250514'

SYSTEM_PROMPT = """You are a job description decoder. Analyze the provided job description and return a structured JSON response with exactly these fields:

{
  "summary": "A 1-2 sentence plain-English summary of what this role actually does and what the company culture is like",
  "verdict": "apply" | "maybe" | "skip",
  "verdict_reason": "1 sentence explaining why you gave this verdict",
  "real_role_meaning": "What this role REALLY means in plain English. 3-5 sentences. Decode buzzwords, clarify vague phrases, explain what they'll actually do day-to-day.",
  "red_flags": [
    {
      "flag": "The specific red flag (short phrase)",
      "explain": "Why it's a red flag in 1 sentence"
    }
  ],
  "must_have_skills": ["list of non-negotiable skills"],
  "nice_to_have_skills": ["list of bonus skills"],
  "salary_estimate": {
    "low": number (annual USD, no commas),
    "high": number (annual USD, no commas),
    "currency": "USD",
    "basis": "1-2 sentence explanation of how you estimated this"
  }
}

Be honest and direct. If a job asks for too much at low pay, say so. If the wording is deceptive, point it out."""


@app.route('/health')
def health():
    if ANTHROPIC_KEY:
        return jsonify({'status': 'ok', 'api_key_configured': True})
    return jsonify({'status': 'ok', 'api_key_configured': False})


@app.route('/decode', methods=['POST'])
def decode():
    if not ANTHROPIC_KEY:
        return jsonify({'error': 'API key not configured on server'}), 500

    body = request.get_json()
    job_text = (body or {}).get('job_text', '').strip()

    if not job_text or len(job_text) < 50:
        return jsonify({'error': 'Job description too short (min 50 characters)'}), 400

    try:
        resp = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': ANTHROPIC_KEY,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json',
            },
            json={
                'model': MODEL,
                'max_tokens': 1024,
                'system': SYSTEM_PROMPT,
                'messages': [{
                    'role': 'user',
                    'content': f"Decode this job description:\n\n{job_text}"
                }]
            },
            timeout=30,
        )

        if not resp.ok:
            err = resp.json()
            return jsonify({'error': err.get('error', {}).get('message', 'API error')}), 502

        data = resp.json()
        text = data.get('content', [{}])[0].get('text', '')

        import json
        # Try to extract JSON block
        import re
        match = re.search(r'\{[\s\S]*\}', text)
        if not match:
            return jsonify({'error': 'Could not parse model response'}), 502

        return jsonify(json.loads(match.group()))

    except requests.Timeout:
        return jsonify({'error': 'Request timed out — try a shorter description'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)