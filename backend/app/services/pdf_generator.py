"""
TrustLens AI - PDF Model Card Generator
"""
import os
import uuid
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

def generate_model_card_pdf(model_card_data: dict, output_dir: str = "reports") -> str:
    """
    Generates a PDF Model Card from the provided dictionary data.
    Returns the absolute path to the generated PDF.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = f"Model_Card_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.pdf"
    file_path = os.path.abspath(os.path.join(output_dir, filename))

    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontSize=20,
        spaceAfter=20
    )
    heading_style = styles['Heading2']
    body_style = styles['Normal']

    story = []

    # Title
    model_name = model_card_data.get("model_name", "Unknown Model")
    story.append(Paragraph(f"TrustLens AI Model Card: {model_name}", title_style))
    story.append(Spacer(1, 12))

    # Sections to render
    sections = [
        ("Intended Use", "intended_use"),
        ("Out of Scope Use", "out_of_scope_use"),
        ("Training Data", "training_data_desc"),
        ("Evaluation Data", "evaluation_data"),
        ("Limitations", "limitations"),
        ("Recommendations", "recommendations"),
    ]

    for title, key in sections:
        val = model_card_data.get(key)
        if val:
            story.append(Paragraph(title, heading_style))
            story.append(Paragraph(str(val), body_style))
            story.append(Spacer(1, 12))

    # JSON Summaries
    json_sections = [
        ("Performance Summary", "performance_summary"),
        ("Fairness Metrics", "fairness_summary"),
    ]

    for title, key in json_sections:
        val = model_card_data.get(key)
        if val:
            story.append(Paragraph(title, heading_style))
            formatted_json = json.dumps(val, indent=2).replace('\\n', '<br/>').replace(' ', '&nbsp;')
            story.append(Paragraph(f"<pre>{formatted_json}</pre>", body_style))
            story.append(Spacer(1, 12))

    doc.build(story)
    return file_path
