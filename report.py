import streamlit as st
import pandas as pd
import os
from obj1 import objective1
from obj3Sarimax import objective3_sarimax
from report import generate_report  # Import the generate_report function from report.py

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
        df = pd.read_csv(default_path)  # Load from the default path if the file exists or dataset
        st.write("Using default dataset!")
    else:
        st.error("Please upload a dataset or make sure the default file exists.")
        st.stop()  # Stop execution if no dataset

# Ensure the dataframe is loaded
if df is not None:
    # Objective 1: Data Cleaning & Municipality Selection
    df_cleaned, selected_municipalities, start_year, end_year = objective1(df)

    # Debugging output: Check the values returned by objective1
    st.write("Checking variables:")
    st.write("df_cleaned:", df_cleaned)
    st.write("selected_municipalities:", selected_municipalities)
    st.write("start_year:", start_year)
    st.write("end_year:", end_year)

    # Ensure that the data is valid before proceeding
    if df_cleaned is not None and len(selected_municipalities) > 0 and isinstance(start_year, int) and isinstance(end_year, int):
        # Objective 3: Apply SARIMAX model
        objective3_sarimax(df_cleaned, selected_municipalities, start_year, end_year)
        
        # Calculate correlation matrix (corr_matrix) for report
        corr_matrix = df_cleaned.corr()  # Assuming corr_matrix is derived from df_cleaned
        st.write("Correlation Matrix:")
        st.write(corr_matrix)

        # Generate the report and pass the required arguments to generate_report()
        report_file = generate_report(df_cleaned, selected_municipalities, corr_matrix)

        # Provide the option to download the generated report
        with open(report_file, "rb") as f:
            st.download_button(
                label="Download Report",
                data=f,
                file_name="report.pdf",
                mime="application/pdf"
            )
    else:
        st.error("Data is invalid. Please check the dataset and selections.")
