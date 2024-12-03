# report.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

def clean_data(df, selected_municipalities, start_date, end_date):
    # Filter data based on selected municipalities and date range
    df_cleaned = df[
        (df['Municipality'].isin(selected_municipalities)) & 
        (pd.to_datetime(df['Planting_Date']) >= pd.to_datetime(start_date)) & 
        (pd.to_datetime(df['Harvesting_Date']) <= pd.to_datetime(end_date))
    ]
    
    # Ensure 'SanMateo' is valid and set to 1 if present in the selected municipalities
    if 'San Mateo' in selected_municipalities:
        # If 'San Mateo' is selected, make sure it is valid by setting SanMateo = 1
        df_cleaned.loc[df_cleaned['Municipality'] == 'San Mateo', 'SanMateo'] = 1

    # Encode categorical variables (e.g., 'Season') as numbers
    if 'Season' in df_cleaned.columns:
        label_encoder = LabelEncoder()
        df_cleaned['Season'] = label_encoder.fit_transform(df_cleaned['Season'].astype(str))

    # Convert Planting and Harvesting Dates to day-of-year
    if 'Planting_Date' in df_cleaned.columns:
        df_cleaned['Planting_Date'] = pd.to_datetime(df_cleaned['Planting_Date'], errors='coerce').dt.dayofyear
    if 'Harvesting_Date' in df_cleaned.columns:
        df_cleaned['Harvesting_Date'] = pd.to_datetime(df_cleaned['Harvesting_Date'], errors='coerce').dt.dayofyear

    # Drop rows with missing values
    df_cleaned = df_cleaned.dropna()

    return df_cleaned


def generate_report(df, selected_municipalities, start_year, end_year):
    # Automatically clean the data before generating the report
    start_date = pd.to_datetime(f"{start_year}-01-01")
    end_date = pd.to_datetime(f"{end_year}-12-31")
    
    df_cleaned = clean_data(df, selected_municipalities, start_date, end_date)

    # Check if cleaned data is valid
    if df_cleaned.empty:
        raise ValueError("Cleaned data is empty after processing. Cannot generate the report.")
    
    # Compute correlation matrix (this is the key change)
    correlation_matrix = df_cleaned.corr()

    # Create the PDF report
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Rice Production Report", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Report for: {', '.join(selected_municipalities)}", ln=True, align="C")
    pdf.cell(200, 10, txt=f"From: {start_year} To: {end_year}", ln=True, align="C")
    
    # Add some space
    pdf.ln(10)
    
    # Add the cleaned data into the PDF
    pdf.cell(200, 10, txt="Cleaned Data:", ln=True)
    pdf.ln(5)

    # Write the cleaned dataframe as a table (as an example, you can improve this with more complex table formatting)
    for i, column in enumerate(df_cleaned.columns):
        pdf.cell(40, 10, txt=column, border=1)
    pdf.ln()

    for i, row in df_cleaned.iterrows():
        for col in df_cleaned.columns:
            pdf.cell(40, 10, txt=str(row[col]), border=1)
        pdf.ln()
    
    # Add a placeholder for the correlation matrix (as an example of how to generate a figure)
    # Plot the heatmap of the correlation matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', cbar=True)
    plt.title("Correlation Heatmap")

    # Save the plot to a temporary file and add it to the PDF
    plot_file = "heatmap.png"
    plt.savefig(plot_file)
    plt.close()
    
    # Add the heatmap image to the PDF
    pdf.ln(10)
    pdf.image(plot_file, x=10, w=180)
    
    # Save the PDF to a file
    report_file = "rice_production_report.pdf"
    pdf.output(report_file)
    
    # Clean up the temporary plot file
    if os.path.exists(plot_file):
        os.remove(plot_file)
    
    return report_file
