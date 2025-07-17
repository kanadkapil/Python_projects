import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Setup
st.set_page_config(page_title="IPL Dashboard", layout="wide")
st.title("🏏 IPL Match Analysis Dashboard (2008–2019)")
st.markdown("Explore team stats, toss trends, venues, margins, finals and more.")

# Load data
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/kanadkapil/Data/main/IPL_MatchData_08_19.csv"
    df = pd.read_csv(url)
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df = df.drop_duplicates()
    df['toss_match_win'] = df['toss_winner'] == df['winner']
    return df

df = load_data()
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)

# Toss Insights
with st.expander("🎲 Toss Insights", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        toss_win_rate = df['toss_match_win'].mean() * 100
        st.metric("Toss → Match Win Rate", f"{toss_win_rate:.2f}%")

        fig, ax = plt.subplots()
        sns.countplot(data=df, x='toss_decision', palette='Set2', ax=ax)
        ax.set_title("Toss Decision: Bat vs Field")
        st.pyplot(fig)

    with col2:
        fig2, ax2 = plt.subplots()
        sns.barplot(x=['Win toss & win match', 'Win toss & lose match'],
                    y=[df[df['toss_match_win']].shape[0], df[~df['toss_match_win']].shape[0]],
                    palette='Blues', ax=ax2)
        ax2.set_title("Outcomes After Winning Toss")
        st.pyplot(fig2)

# Team Performance
with st.expander("🏆 Team Performance", expanded=False):
    wins_by_season = df.groupby(['Season', 'winner']).size().unstack(fill_value=0)
    st.subheader("Season-wise Wins by Team")
    st.bar_chart(wins_by_season)

    st.subheader("📈 Win % Normalized by Matches Played")
    team_matches = df.groupby(['Season', 'team1']).size().add(df.groupby(['Season', 'team2']).size(), fill_value=0).reset_index(name='matches_played')
    team_wins = df.groupby(['Season', 'winner']).size().reset_index(name='wins')
    win_pct_df = team_matches.merge(team_wins, left_on=['Season', 'team1'], right_on=['Season', 'winner'], how='left').fillna(0)
    win_pct_df['win_rate'] = (win_pct_df['wins'] / win_pct_df['matches_played']).fillna(0)
    pivot = win_pct_df.pivot_table(index='Season', columns='team1', values='win_rate').fillna(0)
    st.line_chart(pivot)

# Venues
with st.expander("📍 Venue Stats", expanded=False):
    top_venues = df['venue'].value_counts().nlargest(10)
    fig, ax = plt.subplots()
    top_venues.plot(kind='barh', color='orchid', ax=ax)
    ax.set_title("Top 10 IPL Venues by Match Count")
    ax.invert_yaxis()
    st.pyplot(fig)

    st.subheader("🏟️ Top Teams at Selected Venues")
    venue_wins = df.groupby(['venue', 'winner']).size().reset_index(name='wins')
    selected_venues = st.multiselect("Choose Venues:", top_venues.index.tolist(), default=top_venues.index[:3])
    filtered = venue_wins[venue_wins['venue'].isin(selected_venues)]
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=filtered, x='venue', y='wins', hue='winner', ax=ax2)
    ax2.set_title("Wins by Team at Selected Venues")
    st.pyplot(fig2)

# Win Margins
with st.expander("📏 Win Margins", expanded=False):
    fig, ax = plt.subplots()
    sns.histplot(df[df['win_by_runs'] > 0]['win_by_runs'], bins=30, color='steelblue', ax=ax)
    ax.set_title("Distribution of Win Margins (Runs)")
    st.pyplot(fig)

    fig2, ax2 = plt.subplots()
    sns.countplot(data=df[df['win_by_wickets'] > 0], x='win_by_wickets', color='darkorange', ax=ax2)
    ax2.set_title("Distribution of Win Margins (Wickets)")
    st.pyplot(fig2)

# Close Matches
with st.expander("⚔️ Close Matches", expanded=False):
    close_matches = df[
        ((df['win_by_runs'] > 0) & (df['win_by_runs'] <= 10)) |
        ((df['win_by_wickets'] > 0) & (df['win_by_wickets'] <= 2))
    ]
    st.metric("Close Matches (≤10 runs or ≤2 wickets)", len(close_matches))

    fig, ax = plt.subplots()
    sns.histplot(data=close_matches, x='Season', bins=12, color='tomato', ax=ax)
    ax.set_title("Close Matches by Season")
    st.pyplot(fig)

# Season Overview
with st.expander("📆 Season Overview", expanded=False):
    matches_per_season = df['Season'].value_counts().sort_index()
    fig, ax = plt.subplots()
    matches_per_season.plot(marker='o', linestyle='-', color='green', ax=ax)
    ax.set_title("Matches Played Per Season")
    st.pyplot(fig)

    toss_trend = df.groupby(['Season', 'toss_decision']).size().unstack().fillna(0)
    fig2, ax2 = plt.subplots()
    toss_trend.plot(marker='o', linestyle='-', ax=ax2)
    ax2.set_title("Toss Decision Trends Over Time")
    st.pyplot(fig2)

# Finals
with st.expander("🏁 IPL Finals Analysis", expanded=False):
    final_dates = df.groupby('Season')['date'].max().reset_index()
    finals = df.merge(final_dates, on=['Season', 'date'])
    fig, ax = plt.subplots()
    sns.countplot(data=finals, y='winner', order=finals['winner'].value_counts().index, palette='coolwarm', ax=ax)
    ax.set_title("Finals Won by Teams (2008–2019)")
    st.pyplot(fig)

# Advanced Toss Efficiency
with st.expander("🧠 Toss Efficiency by Team", expanded=False):
    team_toss_outcome = df.copy()
    team_toss_outcome['toss_win_and_match_win'] = team_toss_outcome['toss_winner'] == team_toss_outcome['winner']
    grouped = team_toss_outcome.groupby(['toss_winner', 'toss_decision'])['toss_win_and_match_win'].mean().reset_index()
    grouped['toss_decision'] = pd.Categorical(grouped['toss_decision'], categories=['bat', 'field'], ordered=True)
    fig, ax = plt.subplots(figsize=(12,6))
    sns.barplot(data=grouped, x='toss_winner', y='toss_win_and_match_win', hue='toss_decision', ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.set_title("Match Win % After Toss (Bat vs Field)")
    st.pyplot(fig)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and IPL data from 2008 to 2019.")
