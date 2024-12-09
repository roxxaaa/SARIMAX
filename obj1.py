import pandas as pd
import streamlit as st

def objective1(df):
    # Data Cleaning & Variable Identification
    
    st.sidebar.markdown("### Data Cleaning and Variable Identification")
    st.sidebar.markdown("##### Add Columns, Filter, and Clean the Dataset")
    
    if st.sidebar.checkbox("Show Dataset"):
        st.write(df)

    # Convert 'Planting_Date' and 'Harvesting_Date' to datetime format
    if 'Planting_Date' in df.columns:
        df["Planting_Date"] = pd.to_datetime(df["Planting_Date"], errors='coerce')
    if 'Harvesting_Date' in df.columns:
        df["Harvesting_Date"] = pd.to_datetime(df["Harvesting_Date"], errors='coerce')

    # Create 'Year' column from 'Planting_Date' or 'Harvesting_Date' if possible
    if 'Planting_Date' in df.columns:
        df['Year'] = df['Planting_Date'].dt.year
    elif 'Harvesting_Date' in df.columns:
        df['Year'] = df['Harvesting_Date'].dt.year
    else:
        st.error("No valid date columns found in the dataset. Please check your data.")
        return None, [], None, None

    # Determine the year range from the dataset
    min_year = int(df['Year'].min())
    max_year = int(df['Year'].max())

    # Sidebar year selection constrained to the dataset's year range
    st.sidebar.markdown("##### Select Year Range for Forecasting")
    start_year = st.sidebar.selectbox("Start Year", options=range(min_year, max_year + 1), index=0)
    end_year = st.sidebar.selectbox("End Year", options=range(min_year, max_year + 1), index=(max_year - min_year))

    # Filter the dataset based on selected year range
    date_filtered_df = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]

    # Automatically check the box if columns exist
    auto_check_categorical = 'Season' in date_filtered_df.columns or 'Rice_Ecosystem' in date_filtered_df.columns

    # Checkbox to convert categorical values
    if st.sidebar.checkbox("Convert 'Season' and 'Rice Ecosystem' to numeric", value=auto_check_categorical):
        if 'Season' in date_filtered_df.columns:
            date_filtered_df['Season'] = date_filtered_df['Season'].replace({'Dry': 1, 'Wet': 2}).astype(float)
        
        if 'Rice_Ecosystem' in date_filtered_df.columns:
            date_filtered_df['Rice_Ecosystem'] = date_filtered_df['Rice_Ecosystem'].replace({'Rainfed': 1, 'Irrigated': 2}).astype(float)

    # Multi-select for filtering by 'Municipality' with a tooltip
    if 'Municipality' in date_filtered_df.columns:
        municipalities = date_filtered_df['Municipality'].unique().tolist()
        st.sidebar.markdown("Choose one or more municipalities to analyze.")
        selected_municipalities = st.sidebar.multiselect(
            "Select Municipalities to Filter", municipalities, default=municipalities[:2], 
            help="Filter data by specific municipalities."
        )

        if len(selected_municipalities) == 0:
            st.warning("Please select at least one municipality.")
        else:
            # Filter the dataframe based on selected municipalities
            filtered_df = date_filtered_df[date_filtered_df['Municipality'].isin(selected_municipalities)]
            
            # Drop rows with missing or infinite values
            filtered_df = filtered_df.replace([float('inf'), -float('inf')], float('nan')).dropna()

            # Show filtered data if selected
            st.sidebar.markdown("Show a preview of the filtered data below.")
            if st.sidebar.checkbox("Show Filtered Data"):
                display_text = f"Filtered Data for {', '.join(selected_municipalities)}"
                st.markdown(f"<h3 style='text-align: center;'>{display_text}</h3>", unsafe_allow_html=True)
                st.dataframe(filtered_df.head(100))

            # Display seasonal and exogenous variables
            st.subheader(f"Seasonal Variables and Exogenous Regressors for {', '.join(selected_municipalities)}")
            st.markdown("The following data provides seasonal and exogenous variable insights.")
            st.dataframe(filtered_df[['Year', 'Municipality', 'Season', 'Rice_Ecosystem', 'Planting_Date', 'Harvesting_Date']].head(100))
    else:
        st.warning("Municipality column is not found in the dataset!")
    
    return filtered_df, selected_municipalities, start_year, end_year
