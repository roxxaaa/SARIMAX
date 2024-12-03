import pandas as pd
import streamlit as st
import os
from io import StringIO

from obj1 import objective1
from obj3Sarimax import objective3_sarimax
from obj4 import objective4

# Define the function to generate the report
def generate_report(df_cleaned, selected_municipalities, start_year, end_year):
    # Example of generating the report content
    report = f"Rice Production Report for {', '.join(selected_municipalities)}\n"
    report += f"Analysis Period: {start_year} to {end_year}\n\n"
    
    # Add a summary of the cleaned data
    report += f"Data Summary:\n"
    report += f"Number of rows in cleaned data: {df_cleaned.shape[0]}\n"
    report += f"Selected Municipalities: {', '.join(selected_municipalities)}\n"
    
    # Example of adding more detailed analysis
    report += "\nAnalysis Results:\n"
    # Here you can add any results from the analysis, like correlations, statistics, etc.
    
    return report

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
        
        # Generate the report after the analysis
        report = generate_report(df_cleaned, selected_municipalities, start_year, end_year)
        
        # Display the report on Streamlit
        st.write(report)
        
        # Button to download the report as text file
        if st.button("Download Full Report"):
            # Save the report to a StringIO buffer
            buffer = StringIO(report)
            st.download_button("Download Report", buffer.getvalue(), file_name="full_report.txt", mime="text/plain")
    else:
        st.warning("Please select at least one municipality to proceed with the analysis.")
