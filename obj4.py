import pandas as pd 
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder

def objective4(df, selected_municipalities, start_date, end_date):
    st.sidebar.title("Correlational Analysis")

    # Filter data based on user inputs
    df = df[
        (df['Municipality'].isin(selected_municipalities)) & 
        (pd.to_datetime(df['Planting_Date']) >= pd.to_datetime(start_date)) & 
        (pd.to_datetime(df['Harvesting_Date']) <= pd.to_datetime(end_date))
    ]

    # Encode categorical variables (e.g., 'Season') as numbers
    if 'Season' in df.columns:
        label_encoder = LabelEncoder()
        df['Season'] = label_encoder.fit_transform(df['Season'].astype(str))

    # Convert Planting and Harvesting Dates to day-of-year
    if 'Planting_Date' in df.columns:
        df['Planting_Date'] = pd.to_datetime(df['Planting_Date'], errors='coerce').dt.dayofyear
    if 'Harvesting_Date' in df.columns:
        df['Harvesting_Date'] = pd.to_datetime(df['Harvesting_Date'], errors='coerce').dt.dayofyear

    # Drop rows with missing values
    df = df.dropna()

    # Define key variables
    seasonal_vars = ['Season', 'Planting_Date', 'Harvesting_Date']
    exogenous_vars = [
        'Rice_Ecosystem', 'Certified_Seeds_Area_Harvested(Ha)', 
        'Hybrid_Seeds_Area_Harvested_(Ha)', 'Total_Area_Harvested(Ha)', 
        'Certified_Seeds_Production(MT)', 'Hybrid_Seeds_Production_(MT)'
    ]
    focus_vars = seasonal_vars + exogenous_vars + ['Total_Production(MT)']

    # Filter data to relevant columns
    df_numeric = df[focus_vars]

    # Compute correlation matrix
    correlation_matrix = df_numeric.corr()

    # Sidebar checkbox to display the Correlation Matrix for San Mateo
    show_sanmateo_corr = st.sidebar.checkbox("Show Correlation Matrix for San Mateo", value=False)
    
    if show_sanmateo_corr and 'SanMateo' in selected_municipalities:
        st.subheader("Correlation Matrix for San Mateo")
        st.write(correlation_matrix)  # Display the correlation matrix for San Mateo

    # Sidebar checkbox to display the heatmap
    show_heatmap = st.sidebar.checkbox("Show Correlation Heatmap", value=True)

    if show_heatmap:
        st.subheader("Correlation Heatmap")
        
        # Add tooltips for better user understanding
        st.markdown("""  
        **Heatmap Explanation:**
        - The color scale indicates the strength and direction of the correlation.
        - A correlation value of **1** means perfect positive correlation, and **-1** means perfect negative correlation.
        - A value around **0** indicates no correlation.
        - Values **above 0.7** or **below -0.7** are considered strong correlations.
        - Positive correlations (above 0.7) mean that as one variable increases, the other also increases. 
        - Negative correlations (below -0.7) mean that as one variable increases, the other decreases.
        """)

        # Create the heatmap with no gaps between cells
        fig, ax = plt.subplots(figsize=(14, 12))  # Adjust figure size for clarity
        heatmap = sns.heatmap(
            correlation_matrix, 
            annot=True,  # Display correlation values
            fmt=".2f",  # Limit to 2 decimal places
            cmap='coolwarm',  # Subtle smooth color map
            cbar=True,  # Display color bar
            square=True,  # Keep the plot square
            linewidths=0,  # No gaps between cells
            linecolor='black',  # Ensure no visible grid lines
            annot_kws={"size": 12, "weight": 'bold', "color": 'black'},  # Clear and bold annotations
            cbar_kws={'shrink': 0.8, 'label': 'Correlation Value'},  # Colorbar adjustments
            ax=ax,
            xticklabels=True,
            yticklabels=True
        )

        # Remove gridlines and adjust the layout to make the cells look filled
        heatmap.grid(False)

        # Rotate x and y axis labels for better readability
        heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation=45, horizontalalignment='right', fontsize=12)
        heatmap.set_yticklabels(heatmap.get_yticklabels(), fontsize=12)

        # Set background color and adjust layout for full-fill
        ax.set_facecolor('white')  # Ensure background color is white or any color you prefer

        # Add a title and adjust layout for the best fit
        plt.title("Correlation Heatmap", fontsize=18)
        plt.tight_layout()  # Adjust layout to prevent clipping

        # Display the heatmap
        st.pyplot(fig)

    # Extract strong correlations
