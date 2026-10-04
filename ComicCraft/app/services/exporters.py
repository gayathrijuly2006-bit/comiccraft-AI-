from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from app.config import BASE_DIR, EXPORTS_DIR


def _local_image_path(url_path: str) -> Path:
    relative = url_path.replace("/static/", "", 1).lstrip("/")
    return BASE_DIR / "static" / relative


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def save_pdf(layout: list[dict]) -> str:
    """Compile all comic panels into a multi-page PDF and return a static URL."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"comic_{timestamp}.pdf"
    output = EXPORTS_DIR / filename

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.multi_cell(0, 10, f"Panel {panel['panel']}: {panel['title']}", align="C")
        pdf.ln(4)

        image_file = _local_image_path(panel.get("image_path", ""))
        if image_file.exists():
            x, y, w = 20, pdf.get_y(), 170
            pdf.image(str(image_file), x=x, y=y, w=w)
            pdf.set_y(y + 100)
        else:
            pdf.set_font("Helvetica", "I", 11)
            pdf.multi_cell(0, 7, "Illustration unavailable.", align="C")
            pdf.ln(5)

        pdf.set_font("Helvetica", "I", 11)
        pdf.multi_cell(0, 7, _clean_text(panel.get("scene_description", "")))
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, "Caption")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, _clean_text(panel.get("caption", "")))
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, "Narration")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, _clean_text(panel.get("narration", "")))
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, "Dialogue")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, _clean_text(panel.get("dialogue", "")))

    pdf.output(str(output))
    return f"/static/exports/{filename}"
