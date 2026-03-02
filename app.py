# Import the tools we downloaded earlier
import pandas as pd  # Pandas helps us work with tables
import plotly.express as px  # Plotly makes charts
import streamlit as st  # Streamlit makes the dashboard
from datetime import datetime  # This helps with time math

# Set up the web page title
st.set_page_config(page_title="Train Delay Dashboard", page_icon="🚂")
st.title("🚂 Train Delay Analysis")
st.write("This shows how late trains are at different stations")

# Step 1: Load the data (read the CSV file)
# 'df' is short for 'dataframe' - it means 'our table'
df = pd.read_csv(r'C:\Users\saite\OneDrive\Documents\Desktop\TrainProject\train_data.csv')

# Step 2: Clean and prepare the data
# We need to calculate "How many minutes late?"
# First, combine Date and Time columns to make proper timestamps

def calculate_delay(row):
    # Combine date and scheduled time
    scheduled = datetime.strptime(f"{row['Date']} {row['Scheduled_Time']}", "%Y-%m-%d %H:%M")
    # Combine date and actual time
    actual = datetime.strptime(f"{row['Date']} {row['Actual_Time']}", "%Y-%m-%d %H:%M")
    # Calculate difference in minutes
    delay = (actual - scheduled).total_seconds() / 60
    return delay

# Apply the calculation to every row
df['Delay_Minutes'] = df.apply(calculate_delay, axis=1)

# Create a full timestamp for the timeline chart
df['Full_Timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Actual_Time'])

# Step 3: Show basic statistics (numbers at the top)
st.header("📊 Quick Summary")
col1, col2, col3 = st.columns(3)

with col1:
    avg_delay = df['Delay_Minutes'].mean()
    st.metric("Average Delay", f"{avg_delay:.1f} minutes")

with col2:
    max_delay = df['Delay_Minutes'].max()
    st.metric("Worst Delay", f"{max_delay:.0f} minutes")

with col3:
    total_trains = df['Train_Number'].nunique()
    st.metric("Total Trains", total_trains)

# Step 4: TIMELINE CHART (Delays over time)
st.header("📈 Timeline: Delays Over Time")

# Create the line chart
fig_timeline = px.line(
    df, 
    x='Full_Timestamp', 
    y='Delay_Minutes',
    color='Station',  # Different color for each station
    markers=True,  # Show dots on the line
    title='How Late Were Trains? (Timeline View)',
    labels={'Delay_Minutes': 'Minutes Late', 'Full_Timestamp': 'Date and Time'}
)

# Make the chart look better
fig_timeline.update_layout(
    xaxis_title="Date",
    yaxis_title="Minutes Late",
    hovermode='x unified'  # When you hover, show all stations
)

st.plotly_chart(fig_timeline, use_container_width=True)

# Step 5: STATION-WISE DASHBOARD (Compare stations)
st.header("🏫 Station Performance Dashboard")

# Calculate average delay per station
station_stats = df.groupby('Station').agg({
    'Delay_Minutes': ['mean', 'max', 'count']
}).reset_index()

# Clean up the column names (make them simple)
station_stats.columns = ['Station', 'Average_Delay', 'Worst_Delay', 'Total_Arrivals']

# Sort by worst average delay
station_stats = station_stats.sort_values('Average_Delay', ascending=False)

# Show as a bar chart
fig_stations = px.bar(
    station_stats,
    x='Station',
    y='Average_Delay',
    color='Average_Delay',
    title='Which Stations Have the Most Delays?',
    labels={'Average_Delay': 'Average Minutes Late', 'Station': 'Train Station'},
    color_continuous_scale='Reds'  # Red color for delays (bad = red)
)

st.plotly_chart(fig_stations, use_container_width=True)

# Step 6: Show the detailed table
st.header("📋 Detailed Data Table")
st.dataframe(df[['Date', 'Train_Number', 'Station', 'Delay_Minutes']].sort_values('Delay_Minutes', ascending=False))

# Step 7: Add filters (make it interactive)
st.header("🔍 Filter the Data")
selected_station = st.selectbox("Choose a Station to See Only Its Trains:", 
                                options=['All'] + list(df['Station'].unique()))

if selected_station != 'All':
    filtered_data = df[df['Station'] == selected_station]
    st.write(f"Showing data for {selected_station}:")
    st.dataframe(filtered_data)
    
    # Show average for just this station
    avg_for_station = filtered_data['Delay_Minutes'].mean()
    st.info(f"Average delay at {selected_station}: {avg_for_station:.1f} minutes")