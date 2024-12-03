import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile

def generate_report(df_cleaned, selected_municipalities, start_year, end_year, corr_matrix):
    # Create a temporary file for the PDF
    pdf_filename = tempfile.mktemp(suffix=".pdf")
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    c.setFont("Helvetica", 12)

    # Add header to the report
    c.drawString(100, 750, "Rice Production Report")
    c.drawString(100, 735, f"Selected Municipalities: {', '.join(selected_municipalities)}")
    c.drawString(100, 720, f"Analysis Period: {start_year} to {end_year}")

    # Add summary of the cleaned data
    c.drawString(100, 700, f"Data Summary:")
    c.drawString(100, 685, f"Number of rows in cleaned data: {df_cleaned.shape[0]}")
    c.drawString(100, 670, f"Selected Municipalities: {', '.join(selected_municipalities)}")

    # Save the correlation matrix plot to a file
    plot_filename = tempfile.mktemp(suffix=".png")
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Matrix")
    plt.tight_layout()
    plt.savefig(plot_filename)
    plt.close()

    # Add the correlation matrix plot to the PDF
    c.drawImage(plot_filename, 100, 350, width=400, height=300)

    # Finalize the PDF
    c.save()

    # Return the PDF filename for downloading
    return pdf_filename
