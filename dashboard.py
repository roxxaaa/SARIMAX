import streamlit as st
import pandas as pd
import os
from obj1 import objective1  # Assuming you have this function for data cleaning
from obj3Sarimax import objective3_sarimax  # Assuming SARIMAX logic is here
from report import generate_report  # Import the updated generate_report

# Streamlit app configuration
st.set_page_config(page_title="SARIMAX for Rice Production", page_icon=":ear_of_rice:", layout="wide")
st.title("Application of SARIMAX for Agricultural Rice Production")
st.write("Seasonal Auto-Regressive Integrated Moving Average with Exogenous Regressor")

# CSS for styling
with open("app.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Sidebar for file uploader or default dataset
st.sidebar.image("images/DALogo.jpg", use_container_width=True)

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
        df = pd.read_csv(default_path)  # Load from the default path if the file exists
        st.write("Using default dataset!")
    else:
        st.error("Please upload a dataset or make sure the default file exists.")
        st.stop()  # Stop execution if no dataset

# Ensure the dataframe is loaded
if df is not None:
    # Step 1: Clean the data and get necessary parameters
    df_cleaned, selected_municipalities, start_year, end_year = objective1(df)

    # Check if cleaning was successful (e.g., non-empty data, valid year selection)
    if df_cleaned is not None and len(selected_municipalities) > 0 and isinstance(start_year, int) and isinstance(end_year, int):
        # Step 2: Apply SARIMAX model (you can call this after the cleaning and before generating the report)
        objective3_sarimax(df_cleaned, selected_municipalities, start_year, end_year)

        # Step 3: Generate the PDF report after all outputs
        try:
            report_file = generate_report(df_cleaned, selected_municipalities, start_year, end_year)

            # Button to download the PDF report
            with open(report_file, "rb") as f:
                st.download_button(
                    label="Download Full Report",
                    data=f,
                    file_name="production_report.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Error generating report: {e}")
    else:
        st.error("Error: Invalid data received. Please check the cleaning and selection steps.")
        st.stop()  # Stop execution if the data is invalid
