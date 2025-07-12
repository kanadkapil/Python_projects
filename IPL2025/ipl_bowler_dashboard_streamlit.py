import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from math import pi
import plotly.express as px
import plotly.graph_objects as go

@st.cache_data
def load_and_clean_data(min_overs=10):
    url = "https://raw.githubusercontent.com/kanadkapil/Data/main/IPL2025_BowlerData.csv"
    df = pd.read_csv(url, on_bad_lines='skip')

    numeric_cols = [
        'Overs', 'Pace (km/h)', 'Runs Conceded', 'Boundary % (4s & 6s)', 'Dot Ball %',
        'Average Runs per Over (PP)', 'Average Runs per Over (MO)', 'Average Runs per Over (DO)'
    ]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    df.dropna(subset=numeric_cols, inplace=True)
    df = df[df['Overs'] >= min_overs].copy()
    df['Economy_calc'] = df['Runs Conceded'] / df['Overs']
    return df

def add_filters(df):
    st.sidebar.header("Filter Options")
    overs = st.sidebar.slider("Min Overs", 0, int(df['Overs'].max()), 10)
    wickets = st.sidebar.slider("Min Wickets", 0, int(df['Wickets'].max()), 0)
    pace = st.sidebar.slider("Pace Range (km/h)", int(df['Pace (km/h)'].min()), int(df['Pace (km/h)'].max()), (120, 150))
    economy = st.sidebar.slider("Max Economy", 0.0, float(df['Economy_calc'].max()), float(df['Economy_calc'].max()))

    df = df[(df['Overs'] >= overs) &
            (df['Wickets'] >= wickets) &
            (df['Pace (km/h)'].between(*pace)) &
            (df['Economy_calc'] <= economy)]
    return df

def show_interactive_table(df):
    st.subheader("📋 Full Bowler Data Table")
    st.dataframe(df, use_container_width=True)

def dot_vs_boundary_ratio(df):
    df['Dot/Boundary Ratio'] = df['Dot Ball %'] / df['Boundary % (4s & 6s)']
    top5 = df.sort_values(by='Dot/Boundary Ratio', ascending=False).head(5)
    st.subheader("🏆 Top 5 Most Disciplined Bowlers")
    st.dataframe(top5[['Bowler Name', 'Dot Ball %', 'Boundary % (4s & 6s)', 'Dot/Boundary Ratio']])

def compare_bowlers(df):
    st.subheader("🆚 Compare Two Bowlers")
    bowler_list = df['Bowler Name'].unique()
    b1 = st.selectbox("Select Bowler 1", bowler_list, index=0)
    b2 = st.selectbox("Select Bowler 2", bowler_list, index=1)

    bowler_df = df[df['Bowler Name'].isin([b1, b2])]
    if len(bowler_df) < 2:
        st.warning("Select two different bowlers.")
        return

    # Radar Plot
    st.markdown("### 📊 Radar Chart Comparison")
    scaler = MinMaxScaler()
    stats = ['Dot Ball %', 'Wickets', 'Economy_calc']
    norm_data = scaler.fit_transform(bowler_df[stats])
    radar_df = pd.DataFrame(norm_data, columns=stats)
    radar_df['Bowler Name'] = bowler_df['Bowler Name'].values

    fig = go.Figure()
    for _, row in radar_df.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=list(row[stats]) + [row[stats[0]]],
            theta=stats + [stats[0]],
            fill='toself',
            name=row['Bowler Name']
        ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)
    st.plotly_chart(fig)

    # Bar Chart
    st.markdown("### 📊 Wickets & Economy")
    bar_data = bowler_df[['Bowler Name', 'Wickets', 'Economy_calc']]
    st.bar_chart(bar_data.set_index('Bowler Name'))

    # Pie Chart
    st.markdown("### 🥧 Overs Distribution")
    fig = px.pie(bowler_df, names='Bowler Name', values='Overs', title='Overs Bowled')
    st.plotly_chart(fig)

    # Line Chart
    st.markdown("### 📈 Phase-wise Economy Comparison")
    phases = ['Average Runs per Over (PP)', 'Average Runs per Over (MO)', 'Average Runs per Over (DO)']
    long_df = bowler_df.melt(id_vars='Bowler Name', value_vars=phases, var_name='Phase', value_name='Economy')
    fig = px.line(long_df, x='Phase', y='Economy', color='Bowler Name', markers=True)
    st.plotly_chart(fig)

def main():
    st.set_page_config("IPL 2025 Bowler Dashboard", layout="wide")
    st.title("🏏 IPL 2025 Bowler Dashboard")
    st.markdown("Analyze, compare, and explore detailed stats of IPL 2025 bowlers.")

    min_overs = st.sidebar.number_input("Minimum Overs to Consider", value=10, min_value=0)
    df = load_and_clean_data(min_overs)
    df = add_filters(df)

    show_interactive_table(df)

    st.header("📈 Visual Analytics")
    dot_vs_boundary_ratio(df)

    st.subheader("📊 Economy Rate Across Match Phases")
    melt_df = df.melt(id_vars='Bowler Name',
                      value_vars=['Average Runs per Over (PP)', 'Average Runs per Over (MO)', 'Average Runs per Over (DO)'],
                      var_name='Phase', value_name='Economy')
    fig = px.bar(melt_df, x='Economy', y='Bowler Name', color='Phase', orientation='h')
    st.plotly_chart(fig)

    st.subheader("🚀 Pace vs Wickets")
    fig = px.scatter(df, x='Pace (km/h)', y='Wickets', size='Wickets', color='Economy_calc',
                     hover_name='Bowler Name', color_continuous_scale='RdYlGn_r')
    st.plotly_chart(fig)

    st.subheader("📊 Correlation Heatmap")
    corr = df[['Average Runs per Over (PP)', 'Average Runs per Over (MO)', 'Average Runs per Over (DO)', 'Economy_calc']].corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)

    compare_bowlers(df)

if __name__ == "__main__":
    main()
