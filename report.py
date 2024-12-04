from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# The function to generate the report
def generate_report(df, selected_municipalities, start_year, end_year, corr_matrix):
    # Create a PDF in memory
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter  # get the dimensions of the page

    # Add the title to the PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, "Rice Production Report")  # Adjusted title position
    c.setFont("Helvetica", 12)

    # Adding system info
    c.drawString(100, height - 70, f"Date Range: {start_year} - {end_year}")
    c.drawString(100, height - 90, f"Municipalities: {', '.join(selected_municipalities)}")

    # Add summary of data cleaning
    c.drawString(100, height - 120, "Summary of Data Cleaning and Selection Process:")
    c.drawString(100, height - 140, f"Number of records selected: {len(df)}")

    # Start printing correlation matrix
    c.drawString(100, height - 160, "Correlation Matrix:")

    # Adjust Y position for the matrix
    y_position = height - 180

    # Add headers for the correlation matrix
    c.setFont("Helvetica-Bold", 10)
    for col in corr_matrix.columns:
        c.drawString(100, y_position, col)
        y_position -= 12  # Reduce Y after header
        if y_position < 100:  # If the content exceeds page height, add a new page
            c.showPage()
            c.setFont("Helvetica", 10)
            y_position = height - 50  # Reset Y position for new page
            c.drawString(100, y_position, "Correlation Matrix (Continued):")
            y_position -= 20

    # Add matrix values to the report
    c.setFont("Helvetica", 10)
    for i, col in enumerate(corr_matrix.columns):
        y_position -= 15
        c.drawString(100, y_position, f"{col}:")
        for j, value in enumerate(corr_matrix[col]):
            c.drawString(130, y_position, f"{value:.2f}")
            y_position -= 15
            if y_position < 100:  # Page overflow check
                c.showPage()
                c.setFont("Helvetica", 10)
                y_position = height - 50  # Reset Y position for new page
                c.drawString(100, y_position, f"Correlation Matrix (Continued from {col}):")
                y_position -= 20

    # Save the PDF
    c.showPage()
    c.save()

    # Return the buffer containing the PDF
    buffer.seek(0)
    return buffer
