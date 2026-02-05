"""
COVID-19 Global Data Analysis Dashboard
Author: Jasmit Singh Dhall
Description: Interactive dashboard for analyzing global COVID-19 trends with visualizations
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime
import requests
from io import StringIO

# Page configuration
st.set_page_config(page_title="COVID-19 Global Dashboard", layout="wide", page_icon="🦠")

# Custom CSS
st.markdown("""
    <style>
    .main {background-color: #f0f2f6;}
    .stAlert {background-color: #e1f5ff;}
    h1 {color: #1f77b4;}
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🦠 COVID-19 Global Data Analysis Dashboard")
st.markdown("**Real-time analysis of global pandemic trends with interactive visualizations**")
st.markdown("---")

@st.cache_data(ttl=3600)
def load_data():
    """Load COVID-19 data from Our World in Data"""
    try:
        url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
        df = pd.read_csv(url)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Load data with progress indicator
with st.spinner("Loading latest COVID-19 data..."):
    df = load_data()

if df is not None:
    # Sidebar filters
    st.sidebar.header("📊 Dashboard Filters")
    
    # Get unique continents and countries
    continents = ['All'] + sorted(df['continent'].dropna().unique().tolist())
    selected_continent = st.sidebar.selectbox("Select Continent", continents)
    
    # Filter countries based on continent
    if selected_continent == 'All':
        countries = sorted(df['location'].unique().tolist())
    else:
        countries = sorted(df[df['continent'] == selected_continent]['location'].unique().tolist())
    
    selected_countries = st.sidebar.multiselect(
        "Select Countries (max 10)",
        countries,
        default=countries[:5] if len(countries) >= 5 else countries
    )[:10]
    
    # Date range filter
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(max_date - pd.Timedelta(days=180), max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Metric selection
    metric = st.sidebar.selectbox(
        "Select Metric",
        ["total_cases", "new_cases", "total_deaths", "new_deaths", 
         "total_vaccinations", "people_fully_vaccinated"]
    )
    
    # Filter data
    if len(date_range) == 2:
        mask = (
            (df['location'].isin(selected_countries)) &
            (df['date'].dt.date >= date_range[0]) &
            (df['date'].dt.date <= date_range[1])
        )
        filtered_df = df[mask].copy()
    else:
        filtered_df = df[df['location'].isin(selected_countries)].copy()
    
    # Key Metrics Row
    st.header("📈 Key Global Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    latest_data = df[df['date'] == df['date'].max()]
    
    with col1:
        total_cases = latest_data['total_cases'].sum()
        st.metric("Total Cases", f"{total_cases:,.0f}")
    
    with col2:
        total_deaths = latest_data['total_deaths'].sum()
        st.metric("Total Deaths", f"{total_deaths:,.0f}")
    
    with col3:
        total_vaccinations = latest_data['total_vaccinations'].sum()
        st.metric("Total Vaccinations", f"{total_vaccinations:,.0f}")
    
    with col4:
        countries_affected = df['location'].nunique()
        st.metric("Countries Affected", f"{countries_affected}")
    
    st.markdown("---")
    
    # Main visualizations
    if not filtered_df.empty:
        # Time series plot
        st.header(f"📊 {metric.replace('_', ' ').title()} Over Time")
        
        fig_line = px.line(
            filtered_df,
            x='date',
            y=metric,
            color='location',
            title=f"{metric.replace('_', ' ').title()} Trend",
            labels={'date': 'Date', metric: metric.replace('_', ' ').title()},
            template='plotly_white'
        )
        fig_line.update_layout(height=500, hovermode='x unified')
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Two column layout for additional charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart - Latest values
            st.subheader("📊 Latest Values Comparison")
            latest_filtered = filtered_df[filtered_df['date'] == filtered_df['date'].max()]
            
            fig_bar = px.bar(
                latest_filtered.sort_values(metric, ascending=False),
                x='location',
                y=metric,
                title=f"Current {metric.replace('_', ' ').title()} by Country",
                labels={'location': 'Country', metric: metric.replace('_', ' ').title()},
                template='plotly_white'
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Pie chart - Distribution
            st.subheader("🥧 Distribution")
            
            fig_pie = px.pie(
                latest_filtered,
                values=metric,
                names='location',
                title=f"{metric.replace('_', ' ').title()} Distribution",
                template='plotly_white'
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Geographical visualization
        st.header("🗺️ Global Heatmap")
        
        world_data = df[df['date'] == df['date'].max()].copy()
        
        fig_map = px.choropleth(
            world_data,
            locations='iso_code',
            color=metric,
            hover_name='location',
            title=f"Global {metric.replace('_', ' ').title()} Distribution",
            color_continuous_scale='Reds',
            template='plotly_white'
        )
        fig_map.update_layout(height=500)
        st.plotly_chart(fig_map, use_container_width=True)
        
        # Statistical Summary
        st.header("📋 Statistical Summary")
        
        summary_cols = ['total_cases', 'total_deaths', 'new_cases', 'new_deaths']
        available_cols = [col for col in summary_cols if col in filtered_df.columns]
        
        if available_cols:
            summary_stats = filtered_df.groupby('location')[available_cols].agg(['mean', 'max', 'min', 'std']).round(2)
            st.dataframe(summary_stats, use_container_width=True)
        
        # Download section
        st.header("💾 Download Data")
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f"covid_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
    else:
        st.warning("⚠️ No data available for selected filters. Please adjust your selection.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Data Source:** [Our World in Data](https://ourworldindata.org/coronavirus)  
    **Developed by:** Jasmit Singh Dhall | [LinkedIn](https://www.linkedin.com/in/jasmit-singhdhall-a8b739279)  
    **Last Updated:** {}
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

else:
    st.error("❌ Unable to load data. Please check your internet connection and try again.")
