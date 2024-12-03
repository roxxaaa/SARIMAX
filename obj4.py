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

        # Add a title and adjust layout for the best fit
        plt.title("Correlation Heatmap", fontsize=18)
        plt.tight_layout()  # Adjust layout to prevent clipping

        # Display the heatmap
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
    - Strong correlations (above 0.7 or below -0.7) indicate significant relationships between factors influencing rice production.
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
    - **Harvesting_Date**: The date when rice was harvested.
    - **Correlation Values**: A value above 0.7 or below -0.7 indicates a strong positive or negative relationship, respectively, between variables.
    """)
