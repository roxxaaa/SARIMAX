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
    show_corr_matrix = st.sidebar.checkbox("Show Correlation Matrix", value=True)
    show_heatmap = st.sidebar.checkbox("Show Correlation Heatmap", value=True)

    # Display correlation matrix if selected
    if show_corr_matrix:
        st.write(f"Correlation Matrix for {', '.join(selected_municipalities)}")
        st.write(correlation_matrix)

    # Display heatmap if selected
    if show_heatmap:
        st.subheader("Correlation Heatmap")
        # Adding tooltips for better understanding of the heatmap
        st.markdown("""
        **Tooltips for Heatmap**:
        - **Correlation Values**: A value above **0.7** or below **-0.7** indicates a strong positive or negative relationship, respectively, between variables.
        - **Color Scale**: The heatmap uses a **coolwarm** color scale to represent the correlation values, where darker blue indicates stronger negative correlations, and darker red indicates stronger positive correlations.
        - **Interpretation**: The heatmap provides a visual representation of how different variables are related to each other. High correlations (either positive or negative) should be investigated further for actionable insights.
        """)

        # Plot heatmap with no gaps
        fig, ax = plt.subplots(figsize=(12, 10))  # Increase figure size for better readability
        sns.heatmap(
            correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', 
            cbar=True, square=True, linewidths=0.5, ax=ax, 
            annot_kws={"size": 10},  # Adjust font size for readability
            linecolor='white',  # Set line color to white to make borders clean
            cbar_kws={'shrink': 0.75}  # Make the colorbar smaller for clarity
        )

        # Ensure the heatmap fits without gaps
        ax.set_title("Correlation Heatmap", fontsize=16)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

        # Adjust layout to remove unnecessary margins
        plt.tight_layout()

        # Show the heatmap
        st.pyplot(fig)

    # Extract strong correlations
    st.subheader("Strong Correlations Summary")
    high_corr = correlation_matrix.unstack().reset_index()
    high_corr.columns = ['Variable 1', 'Variable 2', 'Correlation']
    high_corr = high_corr[
        ((high_corr['Correlation'] > 0.7) | (high_corr['Correlation'] < -0.7)) &
        (high_corr['Variable 1'] != high_corr['Variable 2'])
    ].drop_duplicates()

    # Add an explanation about strong correlations summary
    st.markdown("""
    **Strong Correlations Summary**:
    - A strong correlation refers to a relationship between two variables where the correlation coefficient is either above **0.7** or below **-0.7**. 
    - Positive correlations (above 0.7) mean that as one variable increases, the other also increases. 
    - Negative correlations (below -0.7) mean that as one variable increases, the other decreases. 
    - These correlations are important because they help identify the factors that significantly influence rice production.

    **Moderate Strong Correlations**:
    - Moderate strong correlations fall between **0.5** and **0.7** or **-0.5** and **-0.7**. These correlations still suggest meaningful relationships, but they are not as pronounced as the strong ones.
    """)

    # Display the correlation summary
    if not high_corr.empty:
        st.write("Strong correlations found:")
        st.dataframe(high_corr)

        # **Summarize Key Takeaways**
        st.subheader("Key Takeaways for the Municipal Agricultural Office")
        key_takeaways = []

        # Group key variables and summarize
        strong_correlation_variables = high_corr['Variable 1'].tolist() + high_corr['Variable 2'].tolist()

        # Highlight the strongest correlations
        if any(var in strong_correlation_variables for var in ["Production(MT)", "Total_Production(MT)"]):
            key_takeaways.append(
                "The correlation between the area harvested, seed quality, and the timing of planting and harvesting shows a strong influence on total rice production. These factors are critical for improving yield."
            )
        
        if any(var in strong_correlation_variables for var in ["Area_Harvested(Ha)", "Total_Area_Harvested(Ha)"]):
            key_takeaways.append(
                "Expanding the harvested area is a significant driver of increased rice production. Policies that encourage efficient land use could have a major impact on overall yield."
            )
        
        if any(var in strong_correlation_variables for var in ["Planting_Date", "Harvesting_Date"]):
            key_takeaways.append(
                "The timing of planting and harvesting plays an essential role in maximizing rice yields. Ensuring optimal planting and harvesting dates could significantly improve production."
            )

        # Display summarized Key Takeaways
        st.write("Key Takeaways Summary:")
        st.write(" ".join(key_takeaways))

        # **Summarize Recommendations for Rice Production Growth**
        st.subheader("Recommendations for Rice Production Growth")
        recommendations = []

        # Group recommendations based on correlations
        if any(var in strong_correlation_variables for var in ["Production(MT)", "Total_Production(MT)"]):
            recommendations.append(
                "Focus on improving seed quality, optimizing the harvested area, and providing better guidance on planting and harvesting schedules to enhance rice production."
            )
        
        if any(var in strong_correlation_variables for var in ["Area_Harvested(Ha)", "Total_Area_Harvested(Ha)"]):
            recommendations.append(
                "Encourage farmers to maximize land use and expand the harvested area. Support programs that enable farmers to cultivate more hectares of land."
            )
        
        if any(var in strong_correlation_variables for var in ["Planting_Date", "Harvesting_Date"]):
            recommendations.append(
                "Provide region-specific guidance on the best planting and harvesting times to ensure maximum yields. This could be based on historical climate and yield data."
            )

        # Display summarized Recommendations
        st.write("Recommendations Summary:")
        st.write(" ".join(recommendations))

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
