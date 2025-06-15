import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def calculate_match_score(cv_text: str, job_skills: str) -> float:
    """
    Kirim prompt ke OpenAI untuk dapatkan skor kecocokan
    cv_text: isi CV sebagai teks
    job_skills: skill yang dibutuhkan lowongan, comma separated
    Return skor 0-100 (float)
    """
    prompt = (
        f"Berikan skor dari 0 sampai 100 seberapa cocok kandidat dengan skill berikut:\n"
        f"Skills yang dibutuhkan: {job_skills}\n"
        f"Deskripsi kandidat: {cv_text}\n"
        f"Jawab hanya dengan angka tanpa penjelasan."
    )
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=5,
            temperature=0
        )
        score_text = response.choices[0].text.strip()
        score = float(score_text)
        if score < 0 or score > 100:
            score = 0.0
        return score
    except Exception:
        return 0.0
