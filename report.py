from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def generate_report(df_cleaned, selected_municipalities, start_year, end_year, corr_matrix):
    report_filename = "/tmp/production_report.pdf"
    
    # Create the PDF
    c = canvas.Canvas(report_filename, pagesize=letter)
    c.setFont("Helvetica", 12)
    
    # Title
    c.drawString(100, 750, "Rice Production Report")
    c.drawString(100, 735, f"Selected Municipalities: {', '.join(selected_municipalities)}")
    c.drawString(100, 720, f"Period: {start_year} - {end_year}")
    
    # Add correlation matrix table
    c.drawString(100, 700, "Correlation Matrix:")
    y_position = 680
    for row in corr_matrix.iterrows():
        row_values = row[1].values
        row_text = ', '.join([f"{val:.2f}" for val in row_values])
        c.drawString(100, y_position, row_text)
        y_position -= 15
    
    # Finalize PDF
    c.save()
    
    return report_filename
