# ==========================================
# TRAIN DELAY DASHBOARD - DEPLOYMENT READY
# ==========================================
# This app works with ONLY pandas and streamlit
# No external files needed - data is inside the code!

import pandas as pd
import streamlit as st
from datetime import datetime
import io

# -------- PAGE SETUP --------
st.set_page_config(
    page_title="Train Delays Dashboard",
    page_icon="🚂",
    layout="wide"  # Makes the page use full width
)

st.title("🚂 Train Delay Analysis Dashboard")
st.markdown("**Exploratory Visualization of Train Delays Using Timeline Charts and Station Performance**")

# -------- DATA (BUILT-IN) --------
# We put the data directly in the code so we don't need a CSV file!
# This prevents "FileNotFoundError" when deploying to the internet

csv_data = """Date,Train_Number,Station,Scheduled_Time,Actual_Time
2024-01-01,101,New York,08:00,08:05
2024-01-01,101,Boston,10:00,10:15
2024-01-01,102,New York,09:00,09:02
2024-01-01,102,Washington,11:00,11:30
2024-01-02,101,New York,08:00,08:20
2024-01-02,101,Boston,10:00,10:05
2024-01-02,103,Washington,12:00,12:10
2024-01-03,102,New York,09:00,09:00
2024-01-03,102,Boston,11:00,11:45
2024-01-03,103,New York,14:00,14:05
2024-01-04,101,New York,08:00,08:35
2024-01-04,102,Washington,11:00,11:10
2024-01-04,103,Boston,15:00,15:05
2024-01-05,101,Boston,10:00,10:02
2024-01-05,102,New York,09:00,09:25
2024-01-05,103,Washington,12:00,12:40"""

# Read the data from the text above (like reading a CSV file from memory)
df = pd.read_csv(io.StringIO(csv_data))

# -------- DATA PROCESSING --------
# Calculate how many minutes late each train was

def calculate_delay_minutes(row):
    """Calculate difference between actual and scheduled time"""
    # Combine date and time into full datetime
    scheduled_str = f"{row['Date']} {row['Scheduled_Time']}"
    actual_str = f"{row['Date']} {row['Actual_Time']}"
    
    # Convert text to datetime objects
    scheduled = datetime.strptime(scheduled_str, "%Y-%m-%d %H:%M")
    actual = datetime.strptime(actual_str, "%Y-%m-%d %H:%M")
    
    # Calculate difference in minutes
    diff = (actual - scheduled).total_seconds() / 60
    return diff

# Apply the calculation to every row
df['Delay_Minutes'] = df.apply(calculate_delay_minutes, axis=1)

# Create a full timestamp for the timeline chart
df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Actual_Time'])

# -------- TOP METRICS (SUMMARY CARDS) --------
st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_delay = df['Delay_Minutes'].mean()
    st.metric("Average Delay", f"{avg_delay:.1f} min")

with col2:
    max_delay = df['Delay_Minutes'].max()
    st.metric("Maximum Delay", f"{max_delay:.0f} min")

with col3:
    late_trains = len(df[df['Delay_Minutes'] > 0])
    st.metric("Late Trains", f"{late_trains}")

with col4:
    on_time = len(df[df['Delay_Minutes'] == 0])
    st.metric("On Time", f"{on_time}")

st.divider()  # Adds a horizontal line

# -------- TIMELINE CHART --------
st.subheader("📈 Timeline: Delays Over Time")

# Prepare data for timeline (pivot for the chart)
timeline_data = df.pivot_table(
    index='DateTime', 
    columns='Station', 
    values='Delay_Minutes', 
    aggfunc='mean'
)

# Display the line chart (built-in Streamlit chart - no Plotly needed!)
st.line_chart(timeline_data)

st.caption("This timeline shows how delays changed across different dates and stations")

# -------- STATION PERFORMANCE DASHBOARD --------
st.subheader("🏫 Station-Wise Performance Analysis")

# Create two columns for layout
left_col, right_col = st.columns([2, 1])

with left_col:
    # Calculate average delay by station
    station_stats = df.groupby('Station').agg({
        'Delay_Minutes': ['mean', 'max', 'count']
    }).round(1)
    
    # Flatten column names (make them simple)
    station_stats.columns = ['Avg_Delay', 'Max_Delay', 'Total_Arrivals']
    station_stats = station_stats.sort_values('Avg_Delay', ascending=False)
    
    # Display bar chart (horizontal looks better for station names)
    st.bar_chart(station_stats['Avg_Delay'], color="#ff4b4b")
    
    st.caption("Average delay in minutes per station (sorted by worst performance)")

with right_col:
    st.markdown("**📋 Station Rankings**")
    st.dataframe(
        station_stats,
        column_config={
            "Avg_Delay": st.column_config.NumberColumn("Avg (min)", format="%.1f"),
            "Max_Delay": st.column_config.NumberColumn("Worst (min)", format="%.0f"),
            "Total_Arrivals": st.column_config.NumberColumn("Trains", format="%d")
        },
        use_container_width=True
    )

st.divider()

# -------- DETAILED DATA TABLE --------
st.subheader("📄 Detailed Train Records")

# Add a filter so users can search
station_filter = st.selectbox(
    "Filter by Station (or select 'All'):",
    options=['All'] + list(df['Station'].unique())
)

if station_filter == 'All':
    display_df = df
else:
    display_df = df[df['Station'] == station_filter]

# Show the data with some formatting
st.dataframe(
    display_df[['Date', 'Train_Number', 'Station', 'Scheduled_Time', 'Actual_Time', 'Delay_Minutes']].sort_values('Delay_Minutes', ascending=False),
    column_config={
        'Delay_Minutes': st.column_config.ProgressColumn(
            "Delay (minutes)",
            help="How late the train was",
            format="%d min",
            min_value=0,
            max_value=int(df['Delay_Minutes'].max()) + 5
        )
    },
    use_container_width=True
)

# -------- DOWNLOAD BUTTON --------
# Let users download the data as CSV
csv_for_download = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Data as CSV",
    data=csv_for_download,
    file_name='train_delay_data.csv',
    mime='text/csv'
)

# -------- FOOTER --------
st.divider()
st.markdown("*Built with ❤️ using Streamlit | First Project Deployment*")
st.success("✅ App deployed successfully! Share this link with others.")
