import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Function for the SARIMAX forecast
def objective3_sarimax(df, selected_municipalities, start_year, end_year):
    st.markdown("<h2 style='text-align: center; color: white;'>SARIMAX Forecast</h2>", unsafe_allow_html=True)
    st.write("Forecasting Production with Seasonal and Exogenous Variables")

    # Sidebar for user input
    st.sidebar.title("SARIMAX Forecast Settings")
    forecast_years_sarimax = st.sidebar.slider(
        "Forecast period (years):", min_value=1, max_value=5, value=3, step=1,
        help="Choose the forecast period for production."
    )

    # Filter data based on user-specified range
    df = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]

    # Specify exogenous variables
    exogenous_vars = [
        'Season', 'Rice_Ecosystem', 'Certified_Seeds_Area_Harvested(Ha)',
        'Hybrid_Seeds_Area_Harvested_(Ha)', 'Total_Area_Harvested(Ha)'
    ]
    exogenous_vars_present = [var for var in exogenous_vars if var in df.columns]

    if not exogenous_vars_present:
        st.error("No exogenous variables found in the dataset. Check your data.")
        return

    for municipality in selected_municipalities:
        muni_df = df[df['Municipality'] == municipality]

        if muni_df.empty:
            st.warning(f"No data available for {municipality} in the chosen date range.")
            continue

        # Extract production data and prepare exogenous variables
        years = muni_df['Year'].values
        production = muni_df['Total_Production(MT)'].values
        exog_data = muni_df[exogenous_vars_present].apply(pd.to_numeric, errors='coerce').fillna(0).values

        # Ensure no NaNs or infinite values in exogenous data
        if np.isnan(exog_data).any() or np.isinf(exog_data).any():
            st.warning(f"Non-numeric or infinite values in exogenous variables for {municipality} were replaced with zero.")
            exog_data = np.nan_to_num(exog_data, nan=0.0, posinf=0.0, neginf=0.0)

        # Fit SARIMAX model and handle potential fitting errors
        try:
            model = SARIMAX(production, exog=exog_data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
            fit_model = model.fit(disp=False)
        except ValueError as e:
            st.error(f"Error fitting SARIMAX model for {municipality}: {e}")
            continue

        # Generate future forecast
        future_exog = np.tile(exog_data[-1, :], (forecast_years_sarimax, 1))
        forecast_years = np.arange(years[-1] + 1, years[-1] + forecast_years_sarimax + 1)
        forecast_values = fit_model.forecast(steps=forecast_years_sarimax, exog=future_exog)

        # Create visualization
        fig = go.Figure()

        # Historical data plot
        fig.add_trace(go.Scatter(
            x=years, y=production,
            mode='lines', name='Historical Production',
            line=dict(color='blue'),
            hovertemplate='Year: %{x}<br>Historical Production: %{y:.2f} MT'
        ))

        # Forecasted data plot
        fig.add_trace(go.Scatter(
            x=forecast_years, y=forecast_values,
            mode='lines', name='Forecasted Production',
            line=dict(color='red'),
            hovertemplate='Year: %{x}<br>Forecasted Production: %{y:.2f} MT'
        ))

        # Layout customization
        fig.update_layout(
            title=f"SARIMAX Forecast for {municipality}",
            xaxis_title="Year",
            yaxis_title="Total Production (MT)",
            legend_title="Data",
            hovermode="x unified",
            template="plotly_dark"
        )

        st.plotly_chart(fig)

        # Display insights
        historical_trend = "increasing" if production[-1] > production[0] else "decreasing" if production[-1] < production[0] else "stable"
        forecast_trend = "increasing" if forecast_values[-1] > production[-1] else "decreasing" if forecast_values[-1] < production[-1] else "stable"
        avg_growth_rate = (forecast_values[-1] - production[-1]) / forecast_years_sarimax if forecast_years_sarimax > 0 else 0

        st.markdown(f"""
            **Dynamic Interpretation for {municipality}:**
            - **Historical Trend:** The historical production trend from {years[0]} to {years[-1]} has been **{historical_trend}**.
            - **Forecast Trend:** The forecasted production over the next {forecast_years_sarimax} year(s) is expected to be **{forecast_trend}**.
            - **Growth Rate:** The average annual change in production is approximately **{avg_growth_rate:.2f} MT/year**.
            - **Key Insight:** If the forecast trend continues, by {forecast_years[-1]}, production is projected to reach **{forecast_values[-1]:.2f} MT**, which could impact planning for resource allocation and agricultural strategies.
        """)

# Ensure your script has the correct entry point for Streamlit
if __name__ == "__main__":
    # Example placeholder for testing
    st.title("SARIMAX Forecast App")
    # Add a sample DataFrame for quick testing
    sample_df = pd.DataFrame({
        'Year': [2020, 2021, 2022, 2023],
        'Municipality': ['A', 'A', 'A', 'A'],
        'Total_Production(MT)': [100, 110, 120, 130],
        'Season': [1, 1, 2, 2],
        'Rice_Ecosystem': [1, 2, 1, 2],
        'Certified_Seeds_Area_Harvested(Ha)': [100, 110, 115, 120],
        'Hybrid_Seeds_Area_Harvested_(Ha)': [50, 55, 57, 60],
        'Total_Area_Harvested(Ha)': [150, 165, 172, 180]
    })

    objective3_sarimax(sample_df, ['A'], 2020, 2023)
