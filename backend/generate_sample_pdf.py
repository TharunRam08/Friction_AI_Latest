import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf():
    # Define paths
    public_dir = os.path.join("..", "frontend", "public")
    os.makedirs(public_dir, exist_ok=True)
    pdf_path = os.path.join(public_dir, "Friction_Sample_Strategic_Report.pdf")
    
    # We will set margins to 36 (0.5 inch) to allow maximum table rows to fit nicely
    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                            rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e3a8a'), # Dark Blue
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Heading2'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#4b5563'), # Gray
        spaceAfter=15
    )
    
    # Title & Header Info
    story.append(Paragraph("Friction AI — Enterprise Transaction Ledger", title_style))
    story.append(Paragraph("2-Page Comprehensive Operational Dataset (Q2-Q3 2026)", subtitle_style))
    story.append(Spacer(1, 5))
    
    # Table headers
    data = [
        ["Transaction ID", "Date", "Customer Name", "Product Line", "Amount (USD)", "Status"]
    ]
    
    # Generate 55 rows of structured business transactions
    # This will easily fill up 2 full pages when combined with header rows
    statuses = ["Completed", "Pending", "Failed", "Refunded"]
    products = ["Enterprise SaaS", "Warehouse Robotics", "Logistics Suite", "BI Analytics"]
    customers = [
        "Acme Corp", "Beta Solutions", "Gamma Industries", "Delta Logistics", "Epsilon Tech",
        "Zeta Ventures", "Eta Logistics", "Theta Retail", "Iota Systems", "Kappa Energy"
    ]
    
    for i in range(1, 56):
        date_str = f"2026-07-{i%28+1:02d}"
        cust = customers[i % len(customers)]
        prod = products[i % len(products)]
        amt = f"${1000 + i*135:,.2f}"
        status = statuses[i % len(statuses)]
        data.append([f"TXN-{10000+i}", date_str, cust, prod, amt, status])
        
    # Table layout
    # Letter width is 612. Margins are 36 on each side. Printable width is 540.
    t = Table(data, colWidths=[90, 75, 120, 115, 80, 60], repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 4),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f9fafb')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f3f4f6')]),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    
    story.append(t)
    
    doc.build(story)
    print(f"[OK] Generated 2-page tabular PDF at: {pdf_path}")

if __name__ == "__main__":
    generate_pdf()
