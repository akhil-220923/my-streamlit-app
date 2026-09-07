import os
import re
import glob
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header
        self.drawString(54, 11 * 72 - 36, "IBVAP — Intelligent Border Video Analytics Platform (SIH 2026)")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)
        
        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 36, page_str)
        self.drawString(54, 36, "CONFIDENTIAL & PROPRIETARY — SIH PREPARATION PACKAGE")
        self.line(54, 48, 8.5 * 72 - 54, 48)
        self.restoreState()


def parse_inline_markdown(text):
    """Convert markdown inline formatting to HTML tags supported by ReportLab Paragraph."""
    # Escape XML/HTML special chars (except already formed tags)
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Re-enable specific tags
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Italic
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    # Inline Code
    text = re.sub(r'`(.*?)`', r'<font face="Courier" color="#0d9488" size="9"><b>\1</b></font>', text)
    
    return text


def md_to_flowables(md_content, styles):
    flowables = []
    lines = md_content.split('\n')
    
    in_code_block = False
    code_lines = []
    
    in_table = False
    table_rows = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Code blocks
        if stripped.startswith('```'):
            if in_code_block:
                # End code block
                code_text = '\n'.join(code_lines)
                code_text = code_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                formatted_code = code_text.replace(' ', '&nbsp;').replace('\n', '<br/>')
                p = Paragraph(f"<font face='Courier' size=8 color='#f8fafc'>{formatted_code}</font>", styles['CodeBlock'])
                t = Table([[p]], colWidths=[7.0 * inch])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#09101d")),
                    ('PADDING', (0,0), (-1,-1), 8),
                    ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#1e293b")),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ]))
                flowables.append(Spacer(1, 4))
                flowables.append(t)
                flowables.append(Spacer(1, 6))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
                code_lines = []
            i += 1
            continue
            
        if in_code_block:
            code_lines.append(line)
            i += 1
            continue
            
        # Tables
        if '|' in line and not stripped.startswith('>'):
            # Table row candidate
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if parts:
                # Check if divider line
                if all(re.match(r'^:?-+:?$', p) for p in parts if p):
                    i += 1
                    continue
                table_rows.append(parts)
                in_table = True
                i += 1
                continue
        elif in_table:
            # End of table
            if table_rows:
                # Render table
                formatted_table_data = []
                for r_idx, row in enumerate(table_rows):
                    formatted_row = []
                    for cell in row:
                        cell_html = parse_inline_markdown(cell)
                        style_to_use = styles['TableHeader'] if r_idx == 0 else styles['TableCell']
                        formatted_row.append(Paragraph(cell_html, style_to_use))
                    formatted_table_data.append(formatted_row)
                
                num_cols = max(len(r) for r in table_rows)
                col_width = (7.0 * inch) / num_cols
                
                t = Table(formatted_table_data, colWidths=[col_width] * num_cols)
                t_style = [
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0e1726")),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#00f5d4")),
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('LEFTPADDING', (0,0), (-1,-1), 6),
                    ('RIGHTPADDING', (0,0), (-1,-1), 6),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ]
                for r_idx in range(1, len(table_rows)):
                    if r_idx % 2 == 1:
                        t_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), colors.HexColor("#f8fafc")))
                t.setStyle(TableStyle(t_style))
                flowables.append(Spacer(1, 4))
                flowables.append(t)
                flowables.append(Spacer(1, 8))
            table_rows = []
            in_table = False

        if not stripped:
            flowables.append(Spacer(1, 4))
            i += 1
            continue

        # Horizontal Rule
        if stripped in ('---', '***', '___'):
            flowables.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=8, spaceAfter=8))
            i += 1
            continue

        # Headings
        if stripped.startswith('# '):
            text = parse_inline_markdown(stripped[2:])
            flowables.append(Paragraph(text, styles['Heading1_Custom']))
            flowables.append(Spacer(1, 4))
        elif stripped.startswith('## '):
            text = parse_inline_markdown(stripped[3:])
            flowables.append(Paragraph(text, styles['Heading2_Custom']))
            flowables.append(Spacer(1, 4))
        elif stripped.startswith('### '):
            text = parse_inline_markdown(stripped[4:])
            flowables.append(Paragraph(text, styles['Heading3_Custom']))
            flowables.append(Spacer(1, 4))
        elif stripped.startswith('#### '):
            text = parse_inline_markdown(stripped[5:])
            flowables.append(Paragraph(text, styles['Heading4_Custom']))
            flowables.append(Spacer(1, 3))
        # Blockquotes
        elif stripped.startswith('> '):
            text = parse_inline_markdown(stripped[2:])
            p = Paragraph(text, styles['BlockQuote'])
            t = Table([[p]], colWidths=[6.8 * inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0fdfa")),
                ('PADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#0d9488")),
            ]))
            flowables.append(Spacer(1, 4))
            flowables.append(t)
            flowables.append(Spacer(1, 4))
        # Bullet Lists
        elif re.match(r'^[\-\*\+]\s+', stripped) or re.match(r'^\d+\.\s+', stripped):
            text = re.sub(r'^([\-\*\+]|\d+\.)\s+', '', stripped)
            text_html = parse_inline_markdown(text)
            flowables.append(Paragraph(f"• {text_html}", styles['Bullet_Custom']))
        # Regular Body Paragraph
        else:
            text_html = parse_inline_markdown(stripped)
            flowables.append(Paragraph(text_html, styles['Body_Custom']))
            
        i += 1

    # Catch remaining table if at end of file
    if in_table and table_rows:
        formatted_table_data = []
        for r_idx, row in enumerate(table_rows):
            formatted_row = []
            for cell in row:
                cell_html = parse_inline_markdown(cell)
                style_to_use = styles['TableHeader'] if r_idx == 0 else styles['TableCell']
                formatted_row.append(Paragraph(cell_html, style_to_use))
            formatted_table_data.append(formatted_row)
        
        num_cols = max(len(r) for r in table_rows)
        col_width = (7.0 * inch) / num_cols
        
        t = Table(formatted_table_data, colWidths=[col_width] * num_cols)
        t_style = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0e1726")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#00f5d4")),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ]
        for r_idx in range(1, len(table_rows)):
            if r_idx % 2 == 1:
                t_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), colors.HexColor("#f8fafc")))
        t.setStyle(TableStyle(t_style))
        flowables.append(Spacer(1, 4))
        flowables.append(t)
        flowables.append(Spacer(1, 8))

    return flowables


def build_styles():
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0a1929"),
        spaceBefore=14,
        spaceAfter=6
    ))
    
    styles.add(ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=12,
        spaceAfter=4
    ))
    
    styles.add(ParagraphStyle(
        'Heading3_Custom',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0d9488"),
        spaceBefore=10,
        spaceAfter=3
    ))
    
    styles.add(ParagraphStyle(
        'Heading4_Custom',
        parent=styles['Heading4'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceBefore=8,
        spaceAfter=2
    ))
    
    styles.add(ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=2,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1e293b"),
        leftIndent=12,
        spaceBefore=2,
        spaceAfter=2
    ))
    
    styles.add(ParagraphStyle(
        'BlockQuote',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#0f766e"),
        spaceBefore=2,
        spaceAfter=2
    ))
    
    styles.add(ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#f8fafc")
    ))

    styles.add(ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#ffffff")
    ))

    styles.add(ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0f172a")
    ))

    return styles


def main():
    base_dir = r"c:\Users\Akhil\Downloads\IBVAP_1-20260906T165416Z-1-001\IBVAP_1\SIH_PREPARATION"
    output_pdf_dir = os.path.join(base_dir, "PDFs")
    os.makedirs(output_pdf_dir, exist_ok=True)

    styles = build_styles()
    md_files = sorted(glob.glob(os.path.join(base_dir, "*.md")))

    print(f"Found {len(md_files)} markdown files to convert to PDF.")

    for md_path in md_files:
        filename = os.path.basename(md_path)
        pdf_name = filename.replace('.md', '.pdf')
        pdf_path = os.path.join(output_pdf_dir, pdf_name)

        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        flowables = md_to_flowables(content, styles)

        # Build Individual PDF
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            leftMargin=54, rightMargin=54,
            topMargin=54, bottomMargin=54
        )
        doc.build(flowables, canvasmaker=NumberedCanvas)
        print(f"[OK] Generated: {pdf_name}")

    # Title Page for Master PDF
    title_style = ParagraphStyle(
        'MasterTitle', parent=styles['Heading1_Custom'],
        fontName='Helvetica-Bold', fontSize=26, leading=30,
        textColor=colors.HexColor("#0a1929"), alignment=1, spaceAfter=15
    )
    subtitle_style = ParagraphStyle(
        'MasterSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=13, leading=17,
        textColor=colors.HexColor("#0d9488"), alignment=1, spaceAfter=30
    )
    meta_style = ParagraphStyle(
        'MasterMeta', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=14,
        textColor=colors.HexColor("#475569"), alignment=1, spaceAfter=5
    )

    all_master_flowables = []
    all_master_flowables.append(Spacer(1, 1.5 * inch))
    all_master_flowables.append(Paragraph("IBVAP", title_style))
    all_master_flowables.append(Paragraph("Intelligent Border Video Analytics Platform", title_style))
    all_master_flowables.append(Spacer(1, 10))
    all_master_flowables.append(Paragraph("SIH 2026 — Comprehensive Project Audit & Technical Presentation Package", subtitle_style))
    all_master_flowables.append(HRFlowable(width="80%", thickness=2, color=colors.HexColor("#0d9488"), spaceBefore=20, spaceAfter=30))
    all_master_flowables.append(Paragraph("<b>Category:</b> Blockchain & Cybersecurity / AI Video Surveillance", meta_style))
    all_master_flowables.append(Paragraph("<b>Project Status:</b> 100% Deployed & Operational Prototype", meta_style))
    all_master_flowables.append(Paragraph("<b>Security Certification:</b> SHA-256 Cryptographic Audit Chain Verified", meta_style))
    all_master_flowables.append(Paragraph("<b>Database Architecture:</b> Multi-Tier Fallback (MongoDB Atlas / Local CSV / Seed)", meta_style))
    all_master_flowables.append(Spacer(1, 2 * inch))
    all_master_flowables.append(Paragraph("CONFIDENTIAL DOCUMENT PREPARED FOR SIH HACKATHON EVALUATION", meta_style))
    all_master_flowables.append(PageBreak())

    for md_path in md_files:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        flowables = md_to_flowables(content, styles)
        all_master_flowables.extend(flowables)
        all_master_flowables.append(PageBreak())

    # Build Complete Master Package PDF
    master_pdf_path = os.path.join(base_dir, "IBVAP_SIH_COMPLETE_MASTER_PACKAGE.pdf")
    master_doc = SimpleDocTemplate(
        master_pdf_path,
        pagesize=letter,
        leftMargin=54, rightMargin=54,
        topMargin=54, bottomMargin=54
    )
    master_doc.build(all_master_flowables, canvasmaker=NumberedCanvas)
    print(f"\n[OK] MASTER PDF PACKAGE GENERATED AT: {master_pdf_path}")

if __name__ == "__main__":
    main()
