import os
import openai


openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_cv_text(cv_text: str) -> tuple[str, str]:
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY is not set in environment variables.")
    
    prompt = (
        f"Buatkan ringkasan singkat dari CV berikut dan daftar skill pentingnya dalam format comma separated.\n\n"
        f"{cv_text}\n\n"
        f"Format output:\nSummary:\n[ringkasan]\nSkills:\n[skill1, skill2, ...]"
    )
    
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=300,
            temperature=0.3,
        )
        text = response.choices[0].text.strip()
    except Exception as e:
        raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    summary = ""
    skills = ""
    if "Summary:" in text and "Skills:" in text:
        summary = text.split("Summary:")[1].split("Skills:")[0].strip()
        skills = text.split("Skills:")[1].strip()
    else:
        summary = text
        skills = ""

    return summary, skills
