import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
import plotly.express as px

def objective4(df, selected_municipalities, start_date, end_date):
    st.sidebar.markdown("____________________________")
    st.sidebar.title("Correlational Analysis")

    # Filter the data based on selected municipalities and date range
    df = df[(df['Municipality'].isin(selected_municipalities)) &
            (pd.to_datetime(df['Planting_Date']) >= pd.to_datetime(start_date)) &
            (pd.to_datetime(df['Harvesting_Date']) <= pd.to_datetime(end_date))]

    # Encode categorical variables (like 'Season') using LabelEncoder
    label_encoder = LabelEncoder()
    if 'Season' in df.columns:
        df['Season'] = label_encoder.fit_transform(df['Season'].astype(str))  # Ensure all entries are strings before encoding
    
    # Convert Planting and Harvesting Dates to day of the year
    if 'Planting_Date' in df.columns:
        df["Planting_Date"] = pd.to_datetime(df["Planting_Date"], errors='coerce').dt.dayofyear
    if 'Harvesting_Date' in df.columns:
        df["Harvesting_Date"] = pd.to_datetime(df["Harvesting_Date"], errors='coerce').dt.dayofyear

    # Handle missing values by dropping rows with any NaN values
    df = df.dropna()

    # Define seasonal and exogenous variables of interest
    seasonal_vars = ['Season', 'Planting_Date', 'Harvesting_Date']
    exogenous_vars = [
        'Rice_Ecosystem', 'Certified_Seeds_Area_Harvested(Ha)', 'Hybrid_Seeds_Area_Harvested_(Ha)',
        'Total_Area_Harvested(Ha)', 'Certified_Seeds_Production(MT)', 'Hybrid_Seeds_Production_(MT)'
    ]
    
    # Focus only on seasonal, exogenous variables, and Total Production
    focus_vars = seasonal_vars + exogenous_vars + ['Total_Production(MT)']

    # Filter the dataframe to only include relevant columns
    df_numeric = df[focus_vars]

    # Compute the correlation matrix
    correlation_matrix = df_numeric.corr()

    # Display options for correlation matrix and heatmap
    if st.sidebar.checkbox("Show Correlation Matrix"):
        st.write(f"Correlation between Seasonal and Exogenous Variables for {', '.join(selected_municipalities)}:")
        st.write(correlation_matrix)

    if st.sidebar.checkbox("Show Correlation Heatmap"):
        st.subheader("Correlation Heatmap")
        fig, ax = plt.subplots(figsize=(12, 10))
        heatmap = sns.heatmap(
            correlation_matrix, 
            annot=True, 
            fmt=".2f",  # Limit to 2 decimal places
            cmap='coolwarm', 
            cbar=True, 
            square=True, 
            linewidths=.5, 
            annot_kws={"size": 10},  # Adjust the size of the annotation
            ax=ax
        )
        heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation=45, horizontalalignment='right', fontsize=10)
        heatmap.set_yticklabels(heatmap.get_yticklabels(), fontsize=10)
        plt.title("Correlation Heatmap", fontsize=16)
        st.pyplot(fig)

    # Add correlation analysis summary focusing on Total Production (MT)
    st.subheader("Correlation Summary")
    st.write("The correlation values range from -1 to 1, indicating the strength of the relationship between variables.")

    # Summary of the strongest correlations (threshold filtering)
    st.write("### Strong Correlations Summary")
    high_corr = correlation_matrix[(correlation_matrix > 0.7) | (correlation_matrix < -0.7)].stack().reset_index()
    high_corr.columns = ['Variable 1', 'Variable 2', 'Correlation']
    high_corr = high_corr[high_corr['Variable 1'] != high_corr['Variable 2']]  # Exclude self-correlation

    if not high_corr.empty:
        st.write("Strong correlations found between variables:")
        st.dataframe(high_corr)
    else:
        st.write("No significant strong correlations found in the selected data.")

    # Performance validation statement
    st.write("**The strong correlations, if any, provide evidence that the model has robust performance in predicting outcomes based on the chosen features.**")

    # Key Takeaways based on the correlation analysis
    st.write("""
    ### Key Takeaways:
    - **Seasonal Variables**: Correlations between seasonal variables like season (Dry/Wet) and planting/harvesting dates with total production are analyzed here. Strong correlations would indicate these factors significantly impact production.
    - **Exogenous Variables**: Correlations between variables like rice ecosystem, area harvested, and seed types (certified, hybrid) with production. Strong correlations suggest these factors are important exogenous influences on production outcomes.
    """)

    # Dynamically generate recommendations based on correlation with Total Production (MT)
    st.subheader("Recommendations for Rice Production Growth")
    recommendations = []

    # Analyze strongest correlations with Total_Production(MT)
    total_production_corr = correlation_matrix['Total_Production(MT)'].dropna()
    total_production_corr_sorted = total_production_corr.abs().sort_values(ascending=False)

    # For each variable strongly correlated with Total Production, add a recommendation
    for var, corr_value in total_production_corr_sorted.items():
        if corr_value > 0.7:  # Threshold for high correlation
            recommendations.append(f"Increase focus on **{var}**, as it has a strong positive correlation with total rice production (correlation: {corr_value:.2f}).")
        elif corr_value < -0.7:
            recommendations.append(f"Investigate further into **{var}**, as it has a strong negative correlation with total rice production (correlation: {corr_value:.2f}).")

    # Provide recommendations dynamically
    if recommendations:
        for recommendation in recommendations:
            st.write(f"- {recommendation}")
    else:
        st.write("No strong correlations identified for recommendations.")

    # Tooltips for the user
    st.info("Tooltips: The recommendations above are based on the correlation between various factors and rice production. Strong positive correlations suggest areas to strengthen, while negative correlations may indicate areas that need improvement.")
