import pandas as pd
import streamlit as st
import os
from io import StringIO

from obj1 import objective1
from obj3Sarimax import objective3_sarimax
from obj4 import objective4

# Streamlit app configuration
st.set_page_config(page_title="SARIMAX for Rice Production", page_icon=":ear_of_rice:", layout="wide")
st.title("Application of SARIMAX for Agricultural Rice Production")
st.write("Seasonal Auto-Regressive Integrated Moving Average with Exogenous Regressor")

# CSS for styling
with open("app.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Sidebar for file uploader or default dataset
st.sidebar.image("images/DALogo.jpg", use_column_width=True)

# File uploader or default dataset handling
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

# Initialize the 'df' variable
df = None

# Check if an uploaded file exists or use the default path
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

    # Check if required variables are defined
    if df_cleaned is not None and len(selected_municipalities) > 0 and start_year and end_year:
        # Pass the required parameters to objective3_sarimax
        objective3_sarimax(df_cleaned, selected_municipalities, start_year, end_year)
        
        # Ensure dates for start and end year if objective4 needs date type
        start_date = pd.to_datetime(f"{start_year}-01-01")
        end_date = pd.to_datetime(f"{end_year}-12-31")
        
        # Pass cleaned data and selected municipalities to objective4
        objective4(df_cleaned, selected_municipalities, start_date, end_date)

        # Add a button to download the full report
        st.subheader("Download Full Report")
        
        # Generate the report as a string or CSV
        try:
            report = generate_report(df_cleaned, selected_municipalities, start_year, end_year)
            # Create a download button
            st.download_button(
                label="Download Report",
                data=report,
                file_name="SARIMAX_Report.txt",  # Change to .csv or other formats if preferred
                mime="text/plain"  # Change mime type for CSV, JSON, etc.
            )
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")
    else:
        st.warning("Please select at least one municipality to proceed with the analysis.")

# Function to generate the report content
def generate_report(df_cleaned, selected_municipalities, start_year, end_year):
    if not df_cleaned or not selected_municipalities:
        raise ValueError("Missing necessary data to generate the report")
    
    report = StringIO()  # Using StringIO to generate text-based content

    # Write the general info
    report.write(f"Report: SARIMAX for Rice Production Analysis\n")
    report.write(f"Selected Municipalities: {', '.join(selected_municipalities)}\n")
    report.write(f"Start Year: {start_year}, End Year: {end_year}\n\n")
    
    # Add a summary of the cleaned dataset
    report.write("Cleaned Dataset Summary:\n")
    report.write(f"Rows: {df_cleaned.shape[0]}, Columns: {df_cleaned.shape[1]}\n\n")
    
    # Add data description (e.g., statistical summary of the cleaned data)
    report.write("Data Description (Statistical Summary):\n")
    report.write(df_cleaned.describe().to_string())
    report.write("\n\n")
    
    # Include the results from objective3 (SARIMAX model output)
    report.write("SARIMAX Model Output:\n")
    # Add your SARIMAX model results here (can be output from objective3)
    # report.write(str(sarimax_results))  # Example (add actual results)
    
    # Include results from objective4 (Correlation analysis, heatmaps)
    report.write("Correlation Analysis:\n")
    # Add correlation results here (can be output from objective4)
    # report.write(str(correlation_matrix))  # Example (add actual results)
    
    # Add any additional information or summaries here
    
    # Finalize the report
    report.seek(0)  # Rewind the StringIO buffer
    return report.getvalue()  # Return the content of the report as a string
