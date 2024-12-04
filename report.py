from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import pandas as pd
from fpdf import FPDF

# The function to generate the report using reportlab (for a more customizable layout)
def generate_report(df, selected_municipalities, start_year, end_year, corr_matrix):
    # Create a PDF in memory
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Add the title to the PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Rice Production Report")
    c.setFont("Helvetica", 12)
    
    # Adding system info
    c.drawString(100, 730, f"Date Range: {start_year} - {end_year}")
    c.drawString(100, 710, f"Municipalities: {', '.join(selected_municipalities)}")

    # Add some more detailed content
    c.drawString(100, 680, "Summary of Data Cleaning and Selection Process:")
    c.drawString(100, 660, f"Number of records selected: {len(df)}")
    
    # Add summary statistics for the data
    c.drawString(100, 640, "Summary of Data:")
    c.drawString(100, 620, str(df.describe()))
    
    # Draw the Correlation Matrix Table
    c.drawString(100, 580, "Correlation Matrix:")

    # Set initial Y position for the table
    y_position = 560
    for col in corr_matrix.columns:
        c.drawString(100, y_position, f"{col}:")
        y_position -= 15
        for value in corr_matrix[col]:
            c.drawString(130, y_position, f"{value:.2f}")
            y_position -= 15

    # Save the PDF
    c.showPage()
    c.save()

    # Return the path of the saved file
    buffer.seek(0)
    return buffer


# The function to generate the report using fpdf (for simpler layout)
def generate_report_fpdf(filtered_df, selected_municipalities, corr_matrix):
    # Create a PDF document (using FPDF as an example)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add title to the report
    pdf.cell(200, 10, txt="Report on Agricultural Data Analysis", ln=True, align='C')
    pdf.ln(10)

    # Add a section for selected municipalities
    pdf.cell(200, 10, txt=f"Selected Municipalities: {', '.join(selected_municipalities)}", ln=True)
    pdf.ln(10)

    # Add summary of the dataset
    pdf.cell(200, 10, txt="Summary of the Data", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt=str(filtered_df.describe()))
    
    # Add a section for the correlation matrix
    pdf.cell(200, 10, txt="Correlation Matrix", ln=True)
    pdf.ln(5)

    # Add the correlation matrix to the report
    for i, col in enumerate(corr_matrix.columns):
        pdf.cell(200, 10, txt=f"{col}: {', '.join([f'{value:.2f}' for value in corr_matrix[col]])}", ln=True)
        pdf.ln(5)

    # Save the PDF file
    report_file = "generated_report.pdf"
    pdf.output(report_file)

    return report_file
