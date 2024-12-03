from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import seaborn as sns
import matplotlib.pyplot as plt

def generate_report(df_cleaned, selected_municipalities, start_year, end_year, corr_matrix):
    # PDF File Path
    report_filename = "/tmp/production_report.pdf"
    
    # Create the PDF
    c = canvas.Canvas(report_filename, pagesize=letter)
    c.setFont("Helvetica", 12)
    
    # Title of the report
    c.drawString(100, 750, "Rice Production Report")
    c.drawString(100, 735, f"Selected Municipalities: {', '.join(selected_municipalities)}")
    c.drawString(100, 720, f"Period: {start_year} - {end_year}")
    
    # Add some text-based information (analysis, etc.)
    c.drawString(100, 700, "System Analysis Results:")
    y_position = 680
    c.drawString(100, y_position, "This section contains the summary of the analysis performed.")
    y_position -= 15

    # Insert the correlation matrix as text
    c.drawString(100, y_position, "Correlation Matrix:")
    y_position -= 15
    for row in corr_matrix.iterrows():
        row_values = row[1].values
        row_text = ', '.join([f"{val:.2f}" for val in row_values])
        c.drawString(100, y_position, row_text)
        y_position -= 15
    
    # Plot and save the correlation heatmap as an image
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    plt.title("Correlation Matrix")
    plt.tight_layout()
    plot_filename = "/tmp/correlation_matrix.png"
    plt.savefig(plot_filename)

    # Insert the plot image into the PDF
    c.drawImage(plot_filename, 100, y_position - 100, width=400, height=300)
    
    # Finalize PDF
    c.save()
    
    # Return the file path for download
    return report_filename
