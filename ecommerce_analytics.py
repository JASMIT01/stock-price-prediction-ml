"""
E-Commerce Sales Analytics & Prediction Dashboard
Author: Jasmit Singh Dhall
Description: Comprehensive sales analysis with ML-based forecasting and customer segmentation
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(page_title="E-Commerce Analytics", layout="wide", page_icon="🛒")

# Custom styling
st.markdown("""
    <style>
    .main {background-color: #f5f7fa;}
    .stMetric {background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}
    h1 {color: #2c3e50;}
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🛒 E-Commerce Sales Analytics & Prediction")
st.markdown("**AI-Powered Sales Analysis with Forecasting & Customer Segmentation**")
st.markdown("---")

@st.cache_data
def generate_sample_data():
    """Generate realistic e-commerce sample data"""
    np.random.seed(42)
    
    # Date range
    dates = pd.date_range(start='2022-01-01', end='2024-12-31', freq='D')
    
    # Categories and products
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books']
    products = {
        'Electronics': ['Laptop', 'Smartphone', 'Headphones', 'Tablet'],
        'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Shoes'],
        'Home & Garden': ['Furniture', 'Kitchenware', 'Decor', 'Tools'],
        'Sports': ['Fitness Equipment', 'Sports Wear', 'Accessories', 'Outdoor Gear'],
        'Books': ['Fiction', 'Non-Fiction', 'Comics', 'Educational']
    }
    
    data = []
    customer_id = 1000
    
    for date in dates:
        # Seasonal trend
        month = date.month
        seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * month / 12)
        
        # Weekend boost
        weekend_factor = 1.2 if date.weekday() >= 5 else 1.0
        
        # Number of transactions per day
        num_transactions = np.random.poisson(20 * seasonal_factor * weekend_factor)
        
        for _ in range(num_transactions):
            category = np.random.choice(categories, p=[0.3, 0.25, 0.2, 0.15, 0.1])
            product = np.random.choice(products[category])
            
            # Price based on category
            base_prices = {
                'Electronics': 500,
                'Clothing': 50,
                'Home & Garden': 100,
                'Sports': 80,
                'Books': 20
            }
            
            price = base_prices[category] * np.random.uniform(0.5, 2.0)
            quantity = np.random.choice([1, 2, 3], p=[0.7, 0.2, 0.1])
            revenue = price * quantity
            
            # Customer attributes
            customer_age = np.random.randint(18, 70)
            region = np.random.choice(['North', 'South', 'East', 'West'])
            
            data.append({
                'Date': date,
                'OrderID': f'ORD{len(data):06d}',
                'CustomerID': f'CUST{customer_id}',
                'Category': category,
                'Product': product,
                'Quantity': quantity,
                'Price': round(price, 2),
                'Revenue': round(revenue, 2),
                'CustomerAge': customer_age,
                'Region': region
            })
            
            if np.random.random() < 0.1:  # 10% chance of new customer
                customer_id += 1
    
    return pd.DataFrame(data)

# Load data
with st.spinner("Loading sales data..."):
    df = generate_sample_data()
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    df['Year'] = df['Date'].dt.year
    df['DayOfWeek'] = df['Date'].dt.day_name()

# Sidebar
st.sidebar.header("📊 Analytics Filters")

# Date range
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df['Date'].min().date(), df['Date'].max().date()),
    min_value=df['Date'].min().date(),
    max_value=df['Date'].max().date()
)

# Category filter
categories = st.sidebar.multiselect(
    "Select Categories",
    options=df['Category'].unique().tolist(),
    default=df['Category'].unique().tolist()
)

# Region filter
regions = st.sidebar.multiselect(
    "Select Regions",
    options=df['Region'].unique().tolist(),
    default=df['Region'].unique().tolist()
)

# Filter data
if len(date_range) == 2:
    mask = (
        (df['Date'].dt.date >= date_range[0]) &
        (df['Date'].dt.date <= date_range[1]) &
        (df['Category'].isin(categories)) &
        (df['Region'].isin(regions))
    )
    filtered_df = df[mask].copy()
else:
    filtered_df = df[(df['Category'].isin(categories)) & (df['Region'].isin(regions))].copy()

# Key Metrics
st.header("📈 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_revenue = filtered_df['Revenue'].sum()
    st.metric("Total Revenue", f"${total_revenue:,.2f}")

with col2:
    total_orders = filtered_df['OrderID'].nunique()
    st.metric("Total Orders", f"{total_orders:,}")

with col3:
    avg_order_value = filtered_df['Revenue'].mean()
    st.metric("Avg Order Value", f"${avg_order_value:.2f}")

with col4:
    unique_customers = filtered_df['CustomerID'].nunique()
    st.metric("Unique Customers", f"{unique_customers:,}")

st.markdown("---")

# Tabs for different analyses
tab1, tab2, tab3, tab4 = st.tabs(["📊 Sales Analysis", "🤖 ML Forecasting", "👥 Customer Segmentation", "📋 Detailed Reports"])

with tab1:
    st.header("Sales Trends & Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue over time
        st.subheader("Revenue Trend")
        daily_revenue = filtered_df.groupby('Date')['Revenue'].sum().reset_index()
        
        fig_revenue = px.line(
            daily_revenue,
            x='Date',
            y='Revenue',
            title="Daily Revenue Trend",
            template='plotly_white'
        )
        fig_revenue.update_traces(line_color='#3498db', line_width=2)
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        # Category performance
        st.subheader("Revenue by Category")
        category_revenue = filtered_df.groupby('Category')['Revenue'].sum().reset_index()
        
        fig_category = px.pie(
            category_revenue,
            values='Revenue',
            names='Category',
            title="Revenue Distribution",
            template='plotly_white'
        )
        st.plotly_chart(fig_category, use_container_width=True)
    
    # Regional analysis
    st.subheader("Regional Performance")
    region_stats = filtered_df.groupby('Region').agg({
        'Revenue': 'sum',
        'OrderID': 'count',
        'CustomerID': 'nunique'
    }).reset_index()
    region_stats.columns = ['Region', 'Total Revenue', 'Total Orders', 'Unique Customers']
    
    fig_region = px.bar(
        region_stats,
        x='Region',
        y='Total Revenue',
        title="Revenue by Region",
        template='plotly_white',
        color='Total Revenue',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_region, use_container_width=True)
    
    # Day of week analysis
    st.subheader("Sales by Day of Week")
    dow_revenue = filtered_df.groupby('DayOfWeek')['Revenue'].sum().reset_index()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_revenue['DayOfWeek'] = pd.Categorical(dow_revenue['DayOfWeek'], categories=day_order, ordered=True)
    dow_revenue = dow_revenue.sort_values('DayOfWeek')
    
    fig_dow = px.bar(
        dow_revenue,
        x='DayOfWeek',
        y='Revenue',
        title="Revenue by Day of Week",
        template='plotly_white',
        color='Revenue',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig_dow, use_container_width=True)

with tab2:
    st.header("🤖 ML-Based Sales Forecasting")
    
    # Prepare data for ML
    st.subheader("Revenue Prediction Model")
    
    # Aggregate by date
    ml_data = filtered_df.groupby('Date').agg({
        'Revenue': 'sum',
        'OrderID': 'count',
        'Quantity': 'sum'
    }).reset_index()
    
    # Feature engineering
    ml_data['DayOfYear'] = ml_data['Date'].dt.dayofyear
    ml_data['Month'] = ml_data['Date'].dt.month
    ml_data['DayOfWeek'] = ml_data['Date'].dt.dayofweek
    ml_data['Quarter'] = ml_data['Date'].dt.quarter
    ml_data['WeekOfYear'] = ml_data['Date'].dt.isocalendar().week
    
    # Rolling features
    ml_data['Revenue_MA7'] = ml_data['Revenue'].rolling(window=7, min_periods=1).mean()
    ml_data['Revenue_MA30'] = ml_data['Revenue'].rolling(window=30, min_periods=1).mean()
    
    ml_data = ml_data.fillna(0)
    
    # Train-test split
    features = ['DayOfYear', 'Month', 'DayOfWeek', 'Quarter', 'WeekOfYear', 
                'OrderID', 'Quantity', 'Revenue_MA7', 'Revenue_MA30']
    
    X = ml_data[features]
    y = ml_data['Revenue']
    
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Train model
    with st.spinner("Training Random Forest model..."):
        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred = model.predict(X_test)
        
        # Metrics
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Mean Absolute Error", f"${mae:,.2f}")
    with col2:
        st.metric("R² Score", f"{r2:.4f}")
    
    # Visualization
    test_dates = ml_data['Date'].iloc[split_idx:].reset_index(drop=True)
    results_df = pd.DataFrame({
        'Date': test_dates,
        'Actual': y_test.values,
        'Predicted': y_pred
    })
    
    fig_pred = go.Figure()
    fig_pred.add_trace(go.Scatter(x=results_df['Date'], y=results_df['Actual'], 
                                   name='Actual', line=dict(color='#3498db')))
    fig_pred.add_trace(go.Scatter(x=results_df['Date'], y=results_df['Predicted'], 
                                   name='Predicted', line=dict(color='#e74c3c', dash='dash')))
    fig_pred.update_layout(title="Actual vs Predicted Revenue", template='plotly_white')
    st.plotly_chart(fig_pred, use_container_width=True)
    
    # Feature importance
    st.subheader("Feature Importance")
    importance_df = pd.DataFrame({
        'Feature': features,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    fig_importance = px.bar(
        importance_df,
        x='Importance',
        y='Feature',
        orientation='h',
        title="Feature Importance in Revenue Prediction",
        template='plotly_white'
    )
    st.plotly_chart(fig_importance, use_container_width=True)

with tab3:
    st.header("👥 Customer Segmentation (K-Means Clustering)")
    
    # Prepare customer data
    customer_features = filtered_df.groupby('CustomerID').agg({
        'Revenue': 'sum',
        'OrderID': 'count',
        'CustomerAge': 'first'
    }).reset_index()
    customer_features.columns = ['CustomerID', 'TotalSpent', 'OrderCount', 'Age']
    customer_features['AvgOrderValue'] = customer_features['TotalSpent'] / customer_features['OrderCount']
    
    # Standardize features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(customer_features[['TotalSpent', 'OrderCount', 'AvgOrderValue', 'Age']])
    
    # K-Means clustering
    n_clusters = st.slider("Select Number of Customer Segments", 2, 6, 3)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    customer_features['Segment'] = kmeans.fit_predict(features_scaled)
    customer_features['Segment'] = 'Segment ' + (customer_features['Segment'] + 1).astype(str)
    
    # Visualize segments
    col1, col2 = st.columns(2)
    
    with col1:
        fig_seg1 = px.scatter(
            customer_features,
            x='TotalSpent',
            y='OrderCount',
            color='Segment',
            size='AvgOrderValue',
            title="Customer Segments: Spending vs Order Frequency",
            template='plotly_white'
        )
        st.plotly_chart(fig_seg1, use_container_width=True)
    
    with col2:
        segment_stats = customer_features.groupby('Segment').agg({
            'CustomerID': 'count',
            'TotalSpent': 'mean',
            'OrderCount': 'mean',
            'AvgOrderValue': 'mean'
        }).reset_index()
        
        fig_seg2 = px.bar(
            segment_stats,
            x='Segment',
            y='TotalSpent',
            title="Average Total Spent by Segment",
            template='plotly_white',
            color='TotalSpent',
            color_continuous_scale='Teal'
        )
        st.plotly_chart(fig_seg2, use_container_width=True)
    
    # Segment summary table
    st.subheader("Segment Summary")
    segment_stats.columns = ['Segment', 'Customer Count', 'Avg Total Spent', 'Avg Orders', 'Avg Order Value']
    st.dataframe(segment_stats.round(2), use_container_width=True)

with tab4:
    st.header("📋 Detailed Analytics Reports")
    
    # Top products
    st.subheader("Top 10 Products by Revenue")
    top_products = filtered_df.groupby('Product')['Revenue'].sum().sort_values(ascending=False).head(10).reset_index()
    st.dataframe(top_products, use_container_width=True)
    
    # Monthly summary
    st.subheader("Monthly Performance Summary")
    monthly_summary = filtered_df.groupby('Month').agg({
        'Revenue': 'sum',
        'OrderID': 'count',
        'CustomerID': 'nunique',
        'Quantity': 'sum'
    }).reset_index()
    monthly_summary.columns = ['Month', 'Total Revenue', 'Total Orders', 'Unique Customers', 'Items Sold']
    st.dataframe(monthly_summary.round(2), use_container_width=True)
    
    # Download option
    st.subheader("💾 Export Data")
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data",
        data=csv,
        file_name=f"ecommerce_data_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown("""
**Developed by:** Jasmit Singh Dhall | [LinkedIn](https://www.linkedin.com/in/jasmit-singhdhall-a8b739279)  
**Technologies:** Python, Pandas, Scikit-learn, Plotly, Streamlit  
**Project Type:** Data Analysis & Machine Learning
""")
