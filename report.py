from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# The function to generate the report
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

    # Draw Correlation Matrix Table (optional, you can enhance this part)
    c.drawString(100, 640, "Correlation Matrix:")
    y_position = 620
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
