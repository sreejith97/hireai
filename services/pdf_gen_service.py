from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from io import BytesIO

def generate_contract_pdf(contract_text: str, filename: str = "contract.pdf") -> BytesIO:
    """
    Generates a PDF file from the contract text.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    Story = []
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, leading=14, spaceAfter=10))
    styles.add(ParagraphStyle(name='SectionHeader', parent=styles['Heading2'], spaceBefore=15, spaceAfter=8))
    
    # Title
    Story.append(Paragraph("Employment Contract", styles["Title"]))
    Story.append(Spacer(1, 20))
    
    # Content - splitting by newlines for paragraphs
    lines = contract_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('# '):
            # Header 1 (Title - already handled really, but just in case)
            Story.append(Paragraph(line[2:], styles["Heading1"]))
        elif line.startswith('## '):
            # Header 2
            Story.append(Paragraph(line[3:], styles["SectionHeader"]))
        elif line.startswith('### '):
             # Header 3
            Story.append(Paragraph(line[4:], styles["Heading3"]))
        elif line.startswith('- '):
            # Bullet point
            Story.append(Paragraph(f"• {line[2:]}", styles["Justify"]))
        else:
            # Normal paragraph
            # Bold support: **text** -> <b>text</b>
            import re
            formatted_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            p = Paragraph(formatted_line, styles["Justify"])
            Story.append(p)
            
    doc.build(Story)
    buffer.seek(0)
    return buffer
