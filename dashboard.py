import streamlit as st
import pandas as pd
import os
from io import StringIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import seaborn as sns
import matplotlib.pyplot as plt

# Your objective imports
from obj1 import objective1
from obj3Sarimax import objective3_sarimax
from obj4 import objective4

# Define the function to generate the text report
def generate_report(df_cleaned, selected_municipalities, start_year, end_year):
    report = f"Rice Production Report for {', '.join(selected_municipalities)}\n"
    report += f"Analysis Period: {start_year} to {end_year}\n\n"

    # Add a summary of the cleaned data
    report += f"Data Summary:\n"
    report += f"Number of rows in cleaned data: {df_cleaned.shape[0]}\n"
    report += f"Selected Municipalities: {', '.join(selected_municipalities)}\n"

    # Add analysis results
    report += "\nAnalysis Results:\n"
    # Example of adding correlation matrix (could add more detailed analysis)
    corr_matrix = df_cleaned.corr()
    report += f"\nCorrelation Matrix:\n{corr_matrix}\n"
    
    return report

# Define the function to generate the PDF report
def generate_pdf_report(df_cleaned, selected_municipalities, start_year, end_year):
    report_buffer = StringIO()

    # Create the PDF canvas
    c = canvas.Canvas(report_buffer, pagesize=letter)
    width, height = letter  # Define the page size

    # Add Title to PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, f"Rice Production Report for {', '.join(selected_municipalities)}")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 120, f"Analysis Period: {start_year} to {end_year}")

    # Data Summary Section
    c.drawString(100, height - 140, "Data Summary:")
    c.drawString(100, height - 160, f"Number of rows in cleaned data: {df_cleaned.shape[0]}")
    c.drawString(100, height - 180, f"Selected Municipalities: {', '.join(selected_municipalities)}")

    # Adding a plot to the PDF (correlation matrix as an example)
    plt.figure(figsize=(8, 6))
    sns.heatmap(df_cleaned.corr(), annot=True, cmap="coolwarm", fmt=".2f", cbar=True)
    plt.title("Correlation Matrix")
    plt.tight_layout()

    # Save the plot to a buffer and add it to the PDF
    img_path = "/tmp/correlation_matrix.png"
    plt.savefig(img_path)
    c.drawImage(img_path, 100, height - 500, width=500, height=300)

    # Finalize the PDF
    c.showPage()
    c.save()

    # Return the buffer with the PDF content
    report_buffer.seek(0)
    return report_buffer.getvalue()


# Streamlit app setup
st.set_page_config(page_title="SARIMAX for Rice Production", page_icon=":ear_of_rice:", layout="wide")
st.title("Application of SARIMAX for Agricultural Rice Production")
st.write("Seasonal Auto-Regressive Integrated Moving Average with Exogenous Regressor")

# Sidebar
st.sidebar.image("images/DALogo.jpg", use_column_width=True)

# File uploader or default dataset handling
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

# Initialize the 'df' variable
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

        # Generate the report after the analysis
        report = generate_report(df_cleaned, selected_municipalities, start_year, end_year)

        # Display the report on Streamlit
        st.write(report)

        # Button to download the report as a text file
        if st.button("Download Full Report as Text File"):
            # Save the report to a StringIO buffer
            buffer = StringIO(report)
            st.download_button("Download Report", buffer.getvalue(), file_name="full_report.txt", mime="text/plain")

        # Generate and download PDF report
        if st.button("Download Full Report as PDF"):
            report_buffer = generate_pdf_report(df_cleaned, selected_municipalities, start_year, end_year)
            st.download_button("Download PDF Report", report_buffer, file_name="full_report.pdf", mime="application/pdf")
    else:
        st.warning("Please select at least one municipality to proceed with the analysis.")
