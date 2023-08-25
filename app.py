import pandas as pd
import plotly.express as px
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="AFL Dashboard", layout="wide")

df = pd.read_excel(
    io='player_stats.xlsx',
    engine='openpyxl',
    sheet_name='player_data',
    skiprows=2,
    usecols='A:N',
    nrows=9200,
)

# Convert Round column to strings without trailing .0 and handling non-finite values
df["Round"] = df["Round"].apply(lambda x: str(int(x)) if pd.notna(x) and not np.isinf(x) else str(x))

player = st.multiselect(
    "Player Name",
    options=df["Player"].unique(),
)

df_selection = df.query(
    "Player == @player"
)


# Create a two-column layout
col1, col2 = st.columns(2)

# Column 1: Stats Breakdown
col1.title(":bar_chart: Breakdown")

# Calculate average values
average_disposals = round(df_selection["disposals"].mean(), 1)
average_AF = round(df_selection["fantasy"].mean(), 1)
average_goals = round(df_selection["goals"].mean(), 1)

# Calculate rolling averages for the last 3, 5, and 10 rows of each statistic
last_3_disposals_avg = df_selection["disposals"].tail(3).mean()
last_5_disposals_avg = df_selection["disposals"].tail(5).mean()
last_10_disposals_avg = df_selection["disposals"].tail(10).mean()

last_3_fantasy_avg = df_selection["fantasy"].tail(3).mean()
last_5_fantasy_avg = df_selection["fantasy"].tail(5).mean()
last_10_fantasy_avg = df_selection["fantasy"].tail(10).mean()

last_3_goals_avg = df_selection["goals"].tail(3).mean()
last_5_goals_avg = df_selection["goals"].tail(5).mean()
last_10_goals_avg = df_selection["goals"].tail(10).mean()

# Display the calculated values in a single table without index column
stats_table = pd.DataFrame({
    "Stat": ["Disposals", "Fantasy", "Goals"],
    "Average": [f"{average_disposals:.1f}", f"{average_AF:.1f}", f"{average_goals:.1f}"],
    "Last 3 Avg": [f"{last_3_disposals_avg:.1f}", f"{last_3_fantasy_avg:.1f}", f"{last_3_goals_avg:.1f}"],
    "Last 5 Avg": [f"{last_5_disposals_avg:.1f}", f"{last_5_fantasy_avg:.1f}", f"{last_5_goals_avg:.1f}"],
    "Last 10 Avg": [f"{last_10_disposals_avg:.1f}", f"{last_10_fantasy_avg:.1f}", f"{last_10_goals_avg:.1f}"]
})

# Calculate splits
disposals_home_away = df_selection.groupby("home_away")["disposals"].mean()
goals_home_away = df_selection.groupby("home_away")["goals"].mean()
fantasy_home_away = df_selection.groupby("home_away")["fantasy"].mean()

disposals_venue = df_selection.groupby("Venue")["disposals"].mean()
goals_venue = df_selection.groupby("Venue")["goals"].mean()
fantasy_venue = df_selection.groupby("Venue")["fantasy"].mean()

disposals_win_loss = df_selection.groupby("win_lose_draw")["disposals"].mean()
goals_win_loss = df_selection.groupby("win_lose_draw")["goals"].mean()
fantasy_win_loss = df_selection.groupby("win_lose_draw")["fantasy"].mean()

# Create tables for splits
combined_table = pd.DataFrame({
    "Category": ["Home", "Away", "Win", "Loss"],
    "Avg Disposals": [
        round(disposals_home_away.get("Home", 0), 1),
        round(disposals_home_away.get("Away", 0), 1),
        round(disposals_win_loss.get("Win", 0), 1),
        round(disposals_win_loss.get("Lose", 0), 1),
        
    ],
    "Avg Goals": [
        round(goals_home_away.get("Home", 0), 1),
        round(goals_home_away.get("Away", 0), 1),
        round(goals_win_loss.get("Win", 0), 1),
        round(goals_win_loss.get("Lose", 0), 1),
        
    ],
    "Avg Fantasy": [
        round(fantasy_home_away.get("Home", 0), 1),
        round(fantasy_home_away.get("Away", 0), 1),
        round(fantasy_win_loss.get("Win", 0), 1),
        round(fantasy_win_loss.get("Lose", 0), 1),

    ]
})

venue_table = pd.DataFrame({
    "Venue": df_selection["Venue"].unique(),
    "Avg Disposals": [round(disposals_venue.get(venue, 0), 1) for venue in df_selection["Venue"].unique()],
    "Avg Goals": [round(goals_venue.get(venue, 0), 1) for venue in df_selection["Venue"].unique()],
    "Avg Fantasy": [round(fantasy_venue.get(venue, 0), 1) for venue in df_selection["Venue"].unique()]
})

# Convert the DataFrames to HTML tables
stats_table_html = stats_table.to_html(index=False, escape=False)
combined_table_html = combined_table.to_html(index=False, escape=False)
venue_table_html = venue_table.to_html(index=False, escape=False)


# Display the tables
col1.write(stats_table_html, unsafe_allow_html=True)
col1.write(combined_table_html, unsafe_allow_html=True)
col1.write(venue_table_html, unsafe_allow_html=True)

# Column 2: Chart
col2.title(":bar_chart: Stats vs Player Line")

# Define allowed_columns before using it in the selectbox
allowed_columns = ['disposals', 'marks', 'fantasy', 'goals', 'tackles']

# Display the "Select a stat" dropdown and "Player Line" input below the chart heading
selected_column = col2.selectbox("Select a stat", allowed_columns, key="select_stat")
line_value = col2.number_input("Player Line", step=0.5, key="player_line")

# Reverse the DataFrame to plot the most recent game on the left
df_reversed = df_selection.iloc[::-1]

# Calculate for different game spans using the specified "Player Line"
def calculate_percentage_and_count(data, selected_column, line_value, game_span):
    df_selected = data.head(game_span)  # Get the data for the specified game span
    values_above_line = df_selected[df_selected[selected_column] > line_value][selected_column].count()
    values_below_line = df_selected[df_selected[selected_column] < line_value][selected_column].count()
    total_values = df_selected[selected_column].count()
    percentage_above = (values_above_line / total_values) * 100
    percentage_below = (values_below_line / total_values) * 100
    return values_above_line, values_below_line, percentage_above, percentage_below

# Calculate for different game spans using the specified "Player Line"
last_3_above, last_3_below, last_3_above_percentage, last_3_below_percentage = calculate_percentage_and_count(df_reversed, selected_column, line_value, 3)
last_5_above, last_5_below, last_5_above_percentage, last_5_below_percentage = calculate_percentage_and_count(df_reversed, selected_column, line_value, 5)
last_10_above, last_10_below, last_10_above_percentage, last_10_below_percentage = calculate_percentage_and_count(df_reversed, selected_column, line_value, 10)
overall_above, overall_below, overall_above_percentage, overall_below_percentage = calculate_percentage_and_count(df_reversed, selected_column, line_value, df_reversed.shape[0])

# Display the percentages and counts above and below the line for different game spans
table_html = (
    f"<table>"
    f"<tr><th>Game Span</th><th>Over</th><th>Over %</th><th>Under</th><th>Under %</th></tr>"
     f"<tr><td>Overall</td><td>{overall_above}</td><td>{overall_above_percentage:.1f}%</td><td>{overall_below}</td><td>{overall_below_percentage:.1f}%</td></tr>"
    f"<tr><td>Last 3 Games</td><td>{last_3_above}</td><td>{last_3_above_percentage:.1f}%</td><td>{last_3_below}</td><td>{last_3_below_percentage:.1f}%</td></tr>"
    f"<tr><td>Last 5 Games</td><td>{last_5_above}</td><td>{last_5_above_percentage:.1f}%</td><td>{last_5_below}</td><td>{last_5_below_percentage:.1f}%</td></tr>"
    f"<tr><td>Last 10 Games</td><td>{last_10_above}</td><td>{last_10_above_percentage:.1f}%</td><td>{last_10_below}</td><td>{last_10_below_percentage:.1f}%</td></tr>"
    f"</table>"
)

# Display the HTML table using st.write()
col2.write(table_html, unsafe_allow_html=True)

# Display the chart
plt.figure(figsize=(8, 5))
plt.bar(df_reversed["Round"], df_reversed[selected_column])
plt.ylabel(selected_column)
plt.title(f"{selected_column.capitalize()} by Round")
plt.xticks(rotation=45, ha="right", fontsize=8)  # Rotate x-axis labels
plt.tight_layout()

# Add a horizontal line at the specified value
plt.axhline(y=line_value, color="red", linestyle="--", label=f"Line at {line_value}")
plt.legend()

# Display the chart at the bottom of column 2
col2.pyplot(plt)

# Filter the data based on player selection
df_filtered = df.query("Player == @player")

# Convert the filtered DataFrame to an HTML table
filtered_table_html = df_filtered.to_html(index=False, escape=False)

# Display the filtered data table at the bottom of the page
st.write("### Season Game Log")
st.write(filtered_table_html, unsafe_allow_html=True)
