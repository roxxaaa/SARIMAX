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

    # Summarize Key Takeaways and Recommendations based on correlations
    if not high_corr.empty:
        st.write("Strong correlations found:")
        st.dataframe(high_corr)

        # **Summarize Key Takeaways**
        st.subheader("Key Takeaways for the Municipal Agricultural Office")
        key_takeaways = []

        # Group key variables and summarize
        if any(high_corr['Variable 1'].str.contains("Production(MT)")) or any(high_corr['Variable 2'].str.contains("Production(MT)")):
            key_takeaways.append(
                "The production of rice (Total_Production(MT)) is strongly influenced by various factors like the area harvested, seeds used, and timing of planting and harvesting."
            )
        
        if any(high_corr['Variable 1'].str.contains("Area_Harvested(Ha)")) or any(high_corr['Variable 2'].str.contains("Area_Harvested(Ha)")):
            key_takeaways.append(
                "Expanding the harvested area is a key factor in boosting overall rice production. This is supported by strong correlations with total production."
            )
        
        if any(high_corr['Variable 1'].str.contains("Planting_Date")) or any(high_corr['Variable 2'].str.contains("Harvesting_Date")):
            key_takeaways.append(
                "Proper timing of planting and harvesting is essential for maximizing yield. Timeliness shows a significant correlation with production."
            )

        # Display summarized Key Takeaways
        for takeaway in key_takeaways:
            st.write(f"- {takeaway}")

        # **Summarize Recommendations for Rice Production Growth**
        st.subheader("Recommendations for Rice Production Growth")
        recommendations = []

        # Group recommendations based on correlations
        if any(high_corr['Variable 1'].str.contains("Production(MT)")) or any(high_corr['Variable 2'].str.contains("Production(MT)")):
            recommendations.append(
                "Focus on improving the factors that directly impact total production, such as the area harvested, seed quality, and efficient timing of planting and harvesting."
            )
        
        if any(high_corr['Variable 1'].str.contains("Area_Harvested(Ha)")) or any(high_corr['Variable 2'].str.contains("Area_Harvested(Ha)")):
            recommendations.append(
                "Encourage farmers to increase the harvested area by optimizing land use and enhancing their capacity to cultivate more hectares."
            )
        
        if any(high_corr['Variable 1'].str.contains("Planting_Date")) or any(high_corr['Variable 2'].str.contains("Harvesting_Date")):
            recommendations.append(
                "Provide guidance on the best planting and harvesting times to optimize rice yield, ensuring that these activities align with the ideal environmental conditions."
            )

        # Display summarized Recommendations
        for rec in recommendations:
            st.write(f"- {rec}")

    else:
        st.write("No strong correlations detected in the selected data.")
        st.subheader("Key Takeaways for the Municipal Agricultural Office")
        st.write("Ensure data completeness and explore additional factors affecting rice production.")

        st.subheader("Recommendations for Rice Production Growth")
        st.write("No actionable insights found. Collect more data or refine analysis criteria.")

    # Tooltips for better user understanding
    st.markdown("""
    **Tooltips for Key Variables**:
    - **Production(MT)**: Total rice production in metric tons.
    - **Area_Harvested(Ha)**: Area of land harvested in hectares.
    - **Planting_Date**: The date when rice was planted.
    - **Harvesting_Date**: The date when rice was harvested.
    - **Correlation Values**: A value above 0.7 or below -0.7 indicates a strong positive or negative relationship, respectively, between variables.
    """)
