import pandas as pd
import streamlit as st
import os
from io import StringIO
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import seaborn as sns

from obj1 import objective1
from obj3Sarimax import objective3_sarimax
from obj4 import objective4

# Define the function to generate the report in PDF
def generate_pdf_report(df_cleaned, selected_municipalities, start_year, end_year):
    # Create a buffer to hold the PDF data
    buffer = BytesIO()
    
    # Create a canvas object to start writing the PDF
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, height - 72, f"Rice Production Report for {', '.join(selected_municipalities)}")
    c.setFont("Helvetica", 12)
    c.drawString(72, height - 100, f"Analysis Period: {start_year} to {end_year}")
    
    # Add data summary
    c.drawString(72, height - 130, "Data Summary:")
    c.drawString(72, height - 150, f"Number of rows in cleaned data: {df_cleaned.shape[0]}")
    c.drawString(72, height - 170, f"Selected Municipalities: {', '.join(selected_municipalities)}")
    
    # Add a section for the analysis results
    c.drawString(72, height - 200, "Analysis Results:")
    
    # Here you can include any textual or visual results from the analysis
    c.drawString(72, height - 220, "Correlation Analysis:")
    
    # Generating correlation plot
    corr_matrix = df_cleaned.corr()
    plt.figure(figsize=(6, 5))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", cbar=True)
    plt.tight_layout()

    # Save the plot to the buffer
    plot_buffer = BytesIO()
    plt.savefig(plot_buffer, format='png')
    plt.close()
    
    # Add the plot to the PDF
    plot_buffer.seek(0)
    c.drawImage(plot_buffer, 72, height - 500, width=500, height=300)
    
    # Add interpretation and summary text
    c.setFont("Helvetica", 10)
    text = """
    The correlation heatmap shows the relationships between various agricultural factors.
    Positive correlations suggest that as one factor increases, the other also increases, while negative correlations suggest the opposite.

    Based on the data analysis, it is evident that certain factors like area harvested, seed quality, and planting timing
    strongly influence rice production outcomes. These insights will help guide the agricultural policies for the municipalities.
    """
    
    c.drawString(72, height - 520, text)
    
    # Finalize the PDF
    c.showPage()
    c.save()
    
    # Get the PDF data from the buffer
    buffer.seek(0)
    return buffer

# Streamlit app setup
st.set_page_config(page_title="SARIMAX for Rice Production", page_icon=":ear_of_rice:", layout="wide")
st.title("Application of SARIMAX for Agricultural Rice Production")

# Check if dataframe is loaded
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

df = None

# Check if an uploaded file exists or use the default dataset
if uploaded_file:
    df = pd.read_csv(uploaded_file)  # Read the uploaded file into a dataframe
    st.write("Dataset uploaded successfully!")
else:
    default_path = "data/San Mateo Dataset.csv"
    if os.path.exists(default_path):
        df = pd.read_csv(default_path)  # Load from the default path if the file exists or dataset
        st.write("Using default dataset!")
    else:
        st.error("Please upload a dataset or make sure the default file exists.")
        st.stop()  # Stop execution if no dataset

# Check if dataframe is loaded
if df is not None:
    # Objective 1: Data Cleaning & Municipality Selection
    df_cleaned, selected_municipalities, start_year, end_year = objective1(df)

    # Only proceed if municipalities are selected
    if len(selected_municipalities) > 0:
        # Pass the cleaned data and municipalities to the SARIMAX model
        objective3_sarimax(df_cleaned, selected_municipalities, start_year, end_year)
        
        # Ensure dates for start and end year if objective4 needs date type
        start_date = pd.to_datetime(f"{start_year}-01-01")
        end_date = pd.to_datetime(f"{end_year}-12-31")
        
        # Pass cleaned data and selected municipalities to objective4
        objective4(df_cleaned, selected_municipalities, start_date, end_date)
        
        # Generate the PDF report
        report_buffer = generate_pdf_report(df_cleaned, selected_municipalities, start_year, end_year)
        
        # Display the report text (optional)
        st.write("Report generated successfully!")
        
        # Button to download the report as a PDF
        st.download_button(
            label="Download Full Report",
            data=report_buffer,
            file_name="full_report.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Please select at least one municipality to proceed with the analysis.")
