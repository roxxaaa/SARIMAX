import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_report(df_cleaned, selected_municipalities, start_year, end_year):
    # Create a PDF report
    pdf_filename = "/tmp/production_report.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    c.setFont("Helvetica", 12)

    # Add header to the report
    c.drawString(100, 750, f"Rice Production Report")
    c.drawString(100, 735, f"Selected Municipalities: {', '.join(selected_municipalities)}")
    c.drawString(100, 720, f"Analysis Period: {start_year} to {end_year}")
    
    # Add summary of the cleaned data
    c.drawString(100, 700, f"Data Summary:")
    c.drawString(100, 685, f"Number of rows in cleaned data: {df_cleaned.shape[0]}")
    c.drawString(100, 670, f"Selected Municipalities: {', '.join(selected_municipalities)}")
    
    # Generate and add correlation matrix plot to the report
    corr_matrix = df_cleaned.corr()  # Assuming df_cleaned has numerical data
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Matrix")
    plt.tight_layout()

    # Save the correlation matrix plot to a file and add it to the PDF
    plot_filename = "/tmp/corr_matrix.png"
    plt.savefig(plot_filename)
    plt.close()

    # Add the plot image to the PDF
    c.drawImage(plot_filename, 100, 350, width=400, height=300)

    # Finalize the PDF
    c.save()

    # Return the PDF filename for downloading
    return pdf_filename
