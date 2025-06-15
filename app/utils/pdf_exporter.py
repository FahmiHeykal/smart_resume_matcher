from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Job Match & Training Recommendation Report', ln=True, align='C')
        self.ln(10)

    def section_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, ln=True)
        self.ln(5)

    def section_body(self, text):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 8, text)
        self.ln()

def generate_match_report(job_title: str, match_score: float, skill_gap: list[str], trainings: list[str]) -> bytes:
    pdf = PDF()
    pdf.add_page()

    pdf.section_title("Job Title")
    pdf.section_body(job_title)

    pdf.section_title("Match Score")
    pdf.section_body(f"{match_score:.2f}/100")

    pdf.section_title("Skill Gaps")
    if skill_gap:
        pdf.section_body(", ".join(skill_gap))
    else:
        pdf.section_body("Tidak ada skill gap")

    pdf.section_title("Rekomendasi Pelatihan")
    if trainings:
        pdf.section_body("\n".join(trainings))
    else:
        pdf.section_body("Tidak ada pelatihan yang direkomendasikan.")

    return pdf.output(dest='S').encode('latin-1')
