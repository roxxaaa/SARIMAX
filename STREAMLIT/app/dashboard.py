import streamlit as st
import pandas as pd
import os

from obj1 import objective1
from obj3Sarimax import objective3_sarimax
from obj4 import objective4

# Streamlit app configuration
st.set_page_config(page_title="SARIMAX for Rice Production", page_icon="🌾", layout="wide")
st.title("Application of SARIMAX for Agricultural Rice Production")
st.write("Seasonal Auto-Regressive Integrated Moving Average with Exogenous Regressor")

# CSS for styling
try:
    css_path = "app.css"
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("CSS file not found.")
except Exception as e:
    st.error(f"Error loading CSS: {e}")

# Sidebar for file uploader or default dataset
try:
    st.sidebar.image("images/DALogo.jpg", use_column_width=True)
except Exception as e:
    st.sidebar.warning(f"Logo not found: {e}")

# File uploader or default dataset handling
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])
default_path = "data/aliciasanmateodatasets.csv"

# Initialize the 'df' variable
df = None

# Check if an uploaded file exists or use the default path
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)  # Read the uploaded file into a dataframe
        st.write("Dataset uploaded successfully!")
    except Exception as e:
        st.error(f"Error reading uploaded file: {e}")
else:
    if os.path.exists(default_path):
        try:
            df = pd.read_csv(default_path)  # Load from the default path if the file exists or dataset
            st.write("Using default dataset!")
        except Exception as e:
            st.error(f"Error reading default dataset: {e}")
    else:
        st.error("Default dataset not found. Please upload a dataset.")
        st.stop()  # Stop execution if no dataset

# Check if dataframe is loaded
if df is not None:
    # Objective 1: Data Cleaning & Municipality Selection
    df_cleaned, selected_municipalities, start_year, end_year = objective1(df)

    # Only proceed if municipalities are selected
    if len(selected_municipalities) > 0:
        # Pass the required parameters to objective3_sarimax
        objective3_sarimax(df_cleaned, selected_municipalities, start_year, end_year)
        
        # Ensure dates for start and end year if objective4 needs date type
        start_date = pd.to_datetime(f"{start_year}-01-01")
        end_date = pd.to_datetime(f"{end_year}-12-31")
        
        # Pass cleaned data and selected municipalities to objective4
        objective4(df_cleaned, selected_municipalities, start_date, end_date)
    else:
        st.warning("Please select at least one municipality to proceed with the analysis.")
