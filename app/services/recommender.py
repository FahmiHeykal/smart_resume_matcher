def get_skill_gap(user_skills: str, required_skills: str) -> list[str]:
    """
    Hitung skill gap dari dua string skill (comma-separated)
    """
    user_set = set(map(str.strip, user_skills.lower().split(',')))
    required_set = set(map(str.strip, required_skills.lower().split(',')))

    gap = required_set - user_set
    return list(gap)

def recommend_trainings_for_skills(skills: list[str]) -> list[str]:
    """
    Rekomendasi pelatihan berdasarkan skill yang belum dimiliki.
    Untuk saat ini hardcoded mapping skill → saran pelatihan.
    """
    sample_training_db = {
        "python": "Belajar Python Dasar di Dicoding",
        "sql": "Kursus SQL Interaktif di Mode Analytics",
        "react": "Frontend Web dengan React - Udemy",
        "docker": "Belajar Docker dari 0 - YouTube Kelas Terbuka",
        "machine learning": "Machine Learning Stanford - Coursera",
    }

    recommendations = []
    for skill in skills:
        training = sample_training_db.get(skill.lower(), f"Pelatihan untuk {skill.title()} belum tersedia.")
        recommendations.append(f"{skill.title()}: {training}")
    return recommendations
