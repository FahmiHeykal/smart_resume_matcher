# Smart Resume Matcher API

Smart Resume Matcher adalah API backend untuk mencocokkan resume (CV) dengan lowongan kerja (job) secara otomatis berdasarkan analisis teks. Dibangun dengan FastAPI dan PostgreSQL, API ini dapat menyimpan data, menghitung skor kecocokan, memberikan rekomendasi, serta menyajikan riwayat dan detail pencocokan.

## Fitur
- Simpan resume dan lowongan kerja
- Hitung skor kecocokan resume dan job
- Rekomendasi job terbaik untuk setiap resume
- Riwayat pencocokan dan detail skor
- Pencarian dan pagination job berdasarkan kata kunci
- API berbasis REST

## Teknologi
- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Uvicorn

## Instalasi
1. Clone repo: `git clone https://github.com/username/smart_resume_matcher.git && cd smart_resume_matcher`
2. Buat virtual env: `python -m venv venv && source venv/bin/activate` (Linux/macOS) atau `.\venv\Scripts\activate` (Windows)
3. Install dependensi : `pip install -r requirements.txt`
4. Siapkan database PostgreSQL dan buat database baru
5. Update koneksi database di `.env` atau `app/core/config.py`
6. Jalankan: `uvicorn app.main:app --reload`

## Contoh Endpoint
- Hitung skor teks:
  - `POST /match/text`
  - Body: `{ "resume_text": "...", "job_text": "..." }`
- Simpan hasil pencocokan:
  - `POST /match/resume`
  - Body: `{ "resume_id": 1, "job_id": 2 }`
- Rekomendasi job terbaik:
  - `GET /match/ranked/{resume_id}?page=1&limit=10&search=kata`
- Riwayat pencocokan:
  - `GET /match/history/{resume_id}`
- Detail pencocokan:
  - `GET /match/history/detail/{match_result_id}`

## Struktur Database
- Resume : ID, nama, isi teks, skill, dan ringkasan
- Job : ID, judul, deskripsi, skill dibutuhkan, lokasi, kategori
- MatchResult : ID, resume_id, job_id, skor, waktu pencocokan

## Catatan
- File `.env` harus disiapkan secara manual jika belum ada
- Semua endpoint dapat diuji melalui Postman
- Tidak menggunakan Alembic; migrasi tabel dilakukan manual di PostgreSQL
