from flask import Blueprint, request
from app_utils import *
import logging
from services.authentication import authenticate
from services.gcp_toolkit import upload_to_gcs
import os
import requests
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch

doc_to_pdf_bp = Blueprint('doc_to_pdf', __name__)
logger = logging.getLogger(__name__)

def convert_docx_to_pdf(input_path, output_path):
    doc = Document(input_path)
    pdf = SimpleDocTemplate(output_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    
    # Modify existing styles instead of adding new ones
    styles['Title'].fontSize = 18
    styles['Title'].alignment = TA_CENTER
    styles['Heading1'].fontSize = 16
    styles['Heading2'].fontSize = 14

    flowables = []

    for para in doc.paragraphs:
        if para.style.name == 'Title':
            p = Paragraph(para.text, style=styles['Title'])
        elif para.style.name == 'Heading 1':
            p = Paragraph(para.text, style=styles['Heading1'])
        elif para.style.name == 'Heading 2':
            p = Paragraph(para.text, style=styles['Heading2'])
        elif para.style.name.startswith('Heading'):
            p = Paragraph(para.text, style=styles['Heading3'])
        else:
            p = Paragraph(para.text, style=styles['Normal'])
        
        flowables.append(p)
        flowables.append(Spacer(1, 0.2*inch))  # Add some space between paragraphs

    pdf.build(flowables)

@doc_to_pdf_bp.route('/doc-to-pdf', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "document_url": {"type": "string", "format": "uri"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["document_url"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def doc_to_pdf(job_id, data):
    document_url = data.get('document_url')
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    logger.info(f"Job {job_id}: Received doc-to-pdf request for {document_url}")

    try:
        # Download the document
        response = requests.get(document_url)
        if response.status_code != 200:
            raise Exception(f"Failed to download document: HTTP {response.status_code}")

        # Save the document temporarily
        input_filename = f"/tmp/{job_id}_input.docx"
        with open(input_filename, 'wb') as f:
            f.write(response.content)

        # Convert to PDF
        output_filename = f"/tmp/{job_id}_output.pdf"
        convert_docx_to_pdf(input_filename, output_filename)

        # Upload to GCS
        gcs_url = upload_to_gcs(output_filename)

        # Clean up temporary files
        os.remove(input_filename)
        os.remove(output_filename)

        return gcs_url, "/doc-to-pdf", 200
        
    except Exception as e:
        logger.error(f"Job {job_id}: Error in doc-to-pdf conversion: {str(e)}")
        return str(e), "/doc-to-pdf", 500