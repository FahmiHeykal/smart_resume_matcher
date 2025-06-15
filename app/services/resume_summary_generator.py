import os
from typing import Tuple
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def summarize_cv_text(cv_text: str) -> Tuple[str, str]:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY tidak ditemukan di environment variables.")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {"role": "system", "content": "You are an assistant that summarizes resumes."},
        {"role": "user", "content": (
            "Buatkan ringkasan singkat dari CV berikut dan daftar skill pentingnya "
            "dalam format comma separated.\n\n"
            f"{cv_text}\n\n"
            "Format output:\nSummary:\n[ringkasan]\nSkills:\n[skill1, skill2, ...]"
        )}
    ]

    payload = {
        "model": "llama3-8b-8192",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 500
    }

    try:
        response = httpx.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"Groq API error: {str(e)}")

    # Parsing hasil respon
    summary, skills = "", ""
    if "Summary:" in content and "Skills:" in content:
        try:
            summary = content.split("Summary:")[1].split("Skills:")[0].strip()
            skills = content.split("Skills:")[1].strip()
        except Exception:
            summary = content
            skills = ""
    else:
        summary = content
        skills = ""

    return summary, skills
