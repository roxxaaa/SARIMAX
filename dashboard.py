import pandas as pd
import streamlit as st
import os
from io import StringIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import seaborn as sns
import matplotlib.pyplot as plt

from obj1 import objective1
from obj3Sarimax import objective3_sarimax
from obj4 import objective4

# Assuming objective1, objective3_sarimax, and objective4 are correctly imported
# If they are in different files, make sure to import them like this:
# from obj1 import objective1
# from obj3Sarimax import objective3_sarimax
# from obj4 import objective4

# Define the function to generate the PDF report
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

# Ensure the dataframe is loaded
if df is not None:
    # Objective 1: Data Cleaning & Municipality Selection
    # Assuming objective1 is a function that cleans the data and selects municipalities
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
        report_file = generate_report(df_cleaned, selected_municipalities, start_year, end_year)
        
        # Display a message that the report is ready
        st.write("The report has been generated. You can download it below:")
        
        # Button to download the PDF report
        with open(report_file, "rb") as f:
            st.download_button(
                label="Download Full Report",
                data=f,
                file_name="production_report.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("Please select at least one municipality to proceed with the analysis.")
