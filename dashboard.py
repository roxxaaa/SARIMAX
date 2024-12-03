import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import numpy as np

# Generate PDF report function
def generate_pdf_report(df_cleaned, selected_municipalities, start_year, end_year):
    # Create a buffer to hold the PDF data
    buffer = BytesIO()
    
    # Create PDF document
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Add Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, f"Rice Production Report for {', '.join(selected_municipalities)}")
    c.setFont("Helvetica", 12)
    c.drawString(100, 730, f"Analysis Period: {start_year} to {end_year}")
    
    # Add Data Summary
    c.drawString(100, 710, f"Data Summary:")
    c.drawString(100, 690, f"Number of rows in cleaned data: {df_cleaned.shape[0]}")
    c.drawString(100, 670, f"Selected Municipalities: {', '.join(selected_municipalities)}")

    # Filter only numeric columns to calculate correlation matrix
    df_numeric = df_cleaned.select_dtypes(include=[np.number])

    # Check if numeric data exists
    if not df_numeric.empty:
        # Generate the correlation matrix
        corr_matrix = df_numeric.corr()

        # Plotting the heatmap
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, square=True)
        plt.title("Correlation Matrix")
        
        # Save the heatmap as an image in the buffer
        heatmap_buffer = BytesIO()
        plt.savefig(heatmap_buffer, format="png")
        plt.close()

        # Rewind buffer and insert the image into the PDF
        heatmap_buffer.seek(0)
        c.drawImage(heatmap_buffer, 100, 400, width=400, height=300)
    else:
        c.drawString(100, 650, "No numeric data available for correlation.")

    # Add conclusion or additional results
    c.drawString(100, 350, "Conclusion: This is an example report summary.")
    
    # Finalize the PDF
    c.showPage()
    c.save()

    # Return the PDF buffer
    buffer.seek(0)
    return buffer

# Streamlit app setup
st.set_page_config(page_title="SARIMAX for Rice Production", page_icon=":ear_of_rice:", layout="wide")
st.title("Application of SARIMAX for Agricultural Rice Production")

# File uploader or dataset loading
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

df = None

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Dataset uploaded successfully!")
else:
    default_path = "data/San Mateo Dataset.csv"
    if os.path.exists(default_path):
        df = pd.read_csv(default_path)
        st.write("Using default dataset!")
    else:
        st.error("Please upload a dataset or make sure the default file exists.")
        st.stop()

# Check if dataframe is loaded
if df is not None:
    # Objective 1: Data Cleaning & Municipality Selection
    df_cleaned, selected_municipalities, start_year, end_year = objective1(df)

    if len(selected_municipalities) > 0:
        # Pass the cleaned data and municipalities to the SARIMAX model
        objective3_sarimax(df_cleaned, selected_municipalities, start_year, end_year)
        
        # Ensure dates for start and end year if objective4 needs date type
        start_date = pd.to_datetime(f"{start_year}-01-01")
        end_date = pd.to_datetime(f"{end_year}-12-31")
        
        # Pass cleaned data and selected municipalities to objective4
        objective4(df_cleaned, selected_municipalities, start_date, end_date)
        
        # Generate the PDF report after the analysis
        report_buffer = generate_pdf_report(df_cleaned, selected_municipalities, start_year, end_year)
        
        # Button to download the PDF report
        st.download_button(
            label="Download Full Report",
            data=report_buffer,
            file_name="full_report.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Please select at least one municipality to proceed with the analysis.")
