import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from datetime import timedelta

st.set_page_config(page_title="Rainfall Data Dashboard", layout="wide")

st.title("☔ Rainfall Data Dashboard (Tamil Nadu)")

# Load the dataset
df = pd.read_csv("tnRainfallData.csv",index_col=0)
df['date'] = pd.to_datetime(df['date'])

def sidebar():
    # Sidebar Filters
    st.sidebar.header("Filter Options")

    selected_dist = st.sidebar.multiselect("Select District(s)", options=df['dist'].unique(), default=df['dist'].unique())

    # Date filter
    min_date = df['date'].min()
    max_date = df['date'].max()
    date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])
    return selected_dist, date_range

selected_dist, date_range = sidebar()


# Apply filters
filtered_df = df[
    (df['dist'].isin(selected_dist)) &
    (df['date'] >= pd.to_datetime(date_range[0])) &
    (df['date'] <= pd.to_datetime(date_range[1]))
]

st.subheader("Key Performance Indicators (for selected range)")
if not filtered_df.empty:
    total_rainfall = filtered_df['value'].sum()
    rainy_days = filtered_df['date'].nunique()
    avg_daily_rain = total_rainfall / rainy_days if rainy_days > 0 else 0
    top_district = filtered_df.groupby('dist')['value'].sum().idxmax()

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(label="Total Rainfall", value=f"{total_rainfall:.1f} mm")
    kpi2.metric(label="Avg. Daily Rain", value=f"{avg_daily_rain:.1f} mm")
    kpi3.metric(label="Rainy Days", value=f"{rainy_days}")
    kpi4.metric(label="Top District", value=top_district)
else:
    st.warning("No data available for the selected filters. Please adjust your filters.")


# Show filtered table
st.subheader("Filtered Rainfall Data")
st.dataframe(filtered_df, use_container_width=True)


# Visualizations
st.subheader("📊 Rainfall Visualizations Over all by year")
chart1, chart2 = st.columns(2)

with(chart1):
    # Optional: Total Rainfall by District
    st.markdown("### Total Rainfall by District")
    total_by_dist = filtered_df.groupby("dist")["value"].sum().sort_values(ascending=False)
    st.bar_chart(total_by_dist)

with(chart2):
    # Line chart: Overall Rainfall Over Year
    st.markdown("### 🌧️ Rainfall Trend year")

    # Group by year (sum rainfall per year)
    daily_rainfall = filtered_df.groupby('date')['value'].sum().reset_index()
    daily_rainfall['year'] = daily_rainfall['date'].dt.year
    daily_rainfall = daily_rainfall.groupby('year')['value'].sum().reset_index()

    # Optional: rolling average for smoothing
    daily_rainfall['rolling_avg'] = daily_rainfall['value'].rolling(window=3, min_periods=1).mean()

    # Plot
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    fig1.patch.set_alpha(1)
    ax1.patch.set_alpha(1)
    sns.lineplot(data=daily_rainfall, x='year', y='rolling_avg', marker='o', color='blue', ax=ax1)

    ax1.set_title("Overall Rainfall Over Time", fontsize=16, weight='bold')
    ax1.set_xlabel("Year",color='white')
    ax1.set_ylabel("Rainfall (mm)")
    plt.xticks(rotation=45)
    st.pyplot(fig1)

# Function to show time-based visualizations

def show_time_based_visualizations(df):
    """
    Creates a section with visualizations for current year, month, and week rainfall.
    """
    st.header("Rainfall Snapshots")
    
    # Use a fixed date for "today" to work with the sample data
    today = datetime.datetime.now()
    
    # Get start dates for the periods
    start_of_year = today.replace(month=1, day=1)
    start_of_month = today.replace(day=1)
    start_of_week = today - timedelta(days=today.weekday()) # Monday

    # Create columns for the three charts
    col1, col2, col3 = st.columns(3)

    # --- Current Year Visualization ---
    with col1:
        st.subheader(f"This Year ({today.year})")
        year_df = df[df['date'] >= pd.to_datetime(start_of_year)]
        if not year_df.empty:
            year_total = year_df.groupby('dist')['value'].sum().sort_values()
            st.bar_chart(year_total)
            st.metric(label="Total This Year", value=f"{year_total.sum():.1f} mm")
        else:
            st.info("No data for the current year.")

    # --- Current Month Visualization ---
    with col2:
        st.subheader(f"This Month ({today.strftime('%B')})")
        month_df = df[df['date'] >= pd.to_datetime(start_of_month)]
        if not month_df.empty:
            month_total = month_df.groupby('dist')['value'].sum().sort_values()
            st.bar_chart(month_total)
            st.metric(label="Total This Month", value=f"{month_total.sum():.1f} mm")
        else:
            st.info("No data for the current month.")

    # --- Current Week Visualization ---
    with col3:
        st.subheader("This Week")
        week_df = df[df['date'] >= pd.to_datetime(start_of_week)]
        if not week_df.empty:
            week_total = week_df.groupby('dist')['value'].sum().sort_values()
            st.bar_chart(week_total)
            st.metric(label="Total This Week", value=f"{week_total.sum():.1f} mm")
        else:
            st.info("No data for the current week.")

show_time_based_visualizations(filtered_df)


# Line chart: Rainfall over time
st.markdown("### Rainfall Over Time")
fig1, ax1 = plt.subplots(figsize=(10, 4))
fig1.patch.set_alpha(1)
ax1.patch.set_alpha(1)
sns.lineplot(data=filtered_df, x='date', y='value', ax=ax1)
plt.xticks(rotation=45,)
st.pyplot(fig1)

df1 = pd.read_csv("raingauge_stations.csv")

def show_station_map(df):
    st.subheader("🌧️ Rain Gauge Station Locations")

    map_data = df.copy()
    map_data.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'}, inplace=True)
    
    st.map(map_data)

show_station_map(df1)