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

    # Encode categorical variables (like 'Season') as numbers
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

    # Sidebar options to display the correlation matrix and heatmap
    if st.sidebar.checkbox("Show Correlation Matrix"):
        st.write(f"Correlation Matrix for {', '.join(selected_municipalities)}")
        st.write(correlation_matrix)

    if st.sidebar.checkbox("Show Correlation Heatmap"):
        st.subheader("Correlation Heatmap")
        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(
            correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', 
            cbar=True, square=True, linewidths=0.5, ax=ax
        )
        ax.set_title("Correlation Heatmap", fontsize=16)
        st.pyplot(fig)

    # Extract strong correlations
    st.subheader("Strong Correlations Summary")
    high_corr = correlation_matrix.unstack().reset_index()
    high_corr.columns = ['Variable 1', 'Variable 2', 'Correlation']
    high_corr = high_corr[
        ((high_corr['Correlation'] > 0.7) | (high_corr['Correlation'] < -0.7)) &
        (high_corr['Variable 1'] != high_corr['Variable 2'])
    ].drop_duplicates()

    if not high_corr.empty:
        st.write("Strong correlations found:")
        st.dataframe(high_corr)

        # **Dynamic Key Takeaways**
        st.subheader("Key Takeaways for the Municipal Agricultural Office")
        recommendations = []
        for _, row in high_corr.iterrows():
            variable_1 = row['Variable 1']
            variable_2 = row['Variable 2']
            corr_value = row['Correlation']

            # Generate natural language interpretations
            if "Production(MT)" in variable_2 or "Production(MT)" in variable_1:
                st.write(f"- The relationship between **{variable_1}** and **{variable_2}** (correlation: {corr_value:.2f}) shows these factors are critical for total rice production.")
                recommendations.append(f"Focus on improving practices related to **{variable_1}** and **{variable_2}** to increase rice yields.")
            elif "Area_Harvested(Ha)" in variable_1 or "Area_Harvested(Ha)" in variable_2:
                st.write(f"- A strong correlation between **{variable_1}** and **{variable_2}** (correlation: {corr_value:.2f}) suggests that expanding harvested areas can significantly improve production.")
                recommendations.append(f"Encourage farmers to maximize the harvested area for better yields.")
            elif "Planting_Date" in variable_1 or "Harvesting_Date" in variable_2:
                st.write(f"- The correlation between **{variable_1}** and **{variable_2}** (correlation: {corr_value:.2f}) highlights the importance of proper timing for planting and harvesting.")
                recommendations.append(f"Provide better guidance on planting and harvesting schedules to optimize production.")

    else:
        st.write("No strong correlations detected in the selected data.")
        recommendations = ["Ensure data completeness and explore additional factors affecting rice production."]

    # **Dynamic Recommendations Based on Correlations**
    st.subheader("Recommendations for Rice Production Growth")
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            st.write(f"{i}. {rec}")
    else:
        st.write("No actionable insights found. Collect more data or refine analysis criteria.")

