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

    # Sidebar checkbox to display the heatmap
    show_heatmap = st.sidebar.checkbox("Show Correlation Heatmap", value=True)

    if show_heatmap:
        st.subheader("Correlation Heatmap")
        
        # Create the heatmap with continuous gradient and no gaps
        fig, ax = plt.subplots(figsize=(12, 10))  # Adjust figure size
        heatmap = sns.heatmap(
            correlation_matrix, 
            annot=True, 
            fmt=".2f",  # Limit to 2 decimal places
            cmap='coolwarm',  # Continuous color scale from blue (low) to red (high)
            cbar=True, 
            square=True,  # Force the plot to be square for consistent cell sizes
            linewidths=0,  # Remove the cell borders (no gaps)
            annot_kws={"size": 10},  # Adjust the size of the annotation
            ax=ax
        )

        # Rotate x and y axis labels for better readability
        heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation=45, horizontalalignment='right', fontsize=10)
        heatmap.set_yticklabels(heatmap.get_yticklabels(), fontsize=10)

        # Set title and adjust layout
        plt.title("Correlation Heatmap", fontsize=16)
        plt.tight_layout()  # Adjust the layout to avoid any clipping

        # Display heatmap
        st.pyplot(fig)

    # Extract strong correlations
    st.subheader("Strong Correlations")
    high_corr = correlation_matrix.unstack().reset_index()
    high_corr.columns = ['Variable 1', 'Variable 2', 'Correlation']
    high_corr = high_corr[
        ((high_corr['Correlation'] > 0.7) | (high_corr['Correlation'] < -0.7)) & 
        (high_corr['Variable 1'] != high_corr['Variable 2'])
    ].drop_duplicates()

    # Display short summary
    if not high_corr.empty:
        st.write("Strong correlations (above 0.7 or below -0.7) indicate significant relationships between factors influencing rice production.")
        st.dataframe(high_corr)
    else:
        st.write("No strong correlations detected. Explore other factors affecting rice production.")
        
    # Tooltips for better user understanding
    st.markdown("""
    **Tooltips for Key Variables**:
    - **Production(MT)**: Total rice production in metric tons.
    - **Area_Harvested(Ha)**: Area of land harvested in hectares.
    - **Planting_Date**: The date when rice was planted.
    - **Harvesting_Date**: The date when rice was harvested.
    - **Correlation Values**: Strong positive correlations (> 0.7) mean both variables increase together, while negative correlations (< -0.7) mean one increases as the other decreases.
    """)
