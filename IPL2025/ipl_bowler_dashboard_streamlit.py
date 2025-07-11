import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# Streamlit setup
st.set_page_config(layout="wide")
st.title("🏏 IPL 2025 Bowler Analysis Dashboard")

# Load data
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/kanadkapil/Data/main/IPL2025_BowlerData.csv"
    df = pd.read_csv(url, on_bad_lines='skip')

    # Convert columns
    cols_to_numeric = ['Overs', 'Pace (km/h)', 'Runs Conceded', 'Boundary % (4s & 6s)',
                       'Dot Ball %', 'Average Runs per Over (PP)', 'Average Runs per Over (MO)',
                       'Average Runs per Over (DO)']
    for col in cols_to_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(subset=cols_to_numeric)
    df['Economy_calc'] = df['Runs Conceded'] / df['Overs']
    return df

df = load_data()

# Sidebar filters
min_overs = st.sidebar.slider("Minimum Overs Bowled", min_value=0, max_value=20, value=10)
df = df[df['Overs'] >= min_overs]

# 📊 Section 1: Economy Phase Barplot
st.subheader("1️⃣ Economy Rate by Match Phase")
df_sorted = df.sort_values(by='Runs Conceded', ascending=True)
df_melt = df_sorted.melt(
    id_vars='Bowler Name',
    value_vars=['Average Runs per Over (PP)', 'Average Runs per Over (MO)', 'Average Runs per Over (DO)'],
    var_name='Phase',
    value_name='Economy'
)

fig1, ax1 = plt.subplots(figsize=(12, len(df_sorted) * 0.4))
barplot = sns.barplot(data=df_melt, y='Bowler Name', x='Economy', hue='Phase', orient='h', ax=ax1)
for container in barplot.containers:
    barplot.bar_label(container, fmt='%.2f', label_type='edge', fontsize=7, padding=2)
plt.title("Economy in Each Match Phase (Sorted by Runs Conceded)")
st.pyplot(fig1)

# 📊 Section 2: Speed vs Wickets
st.subheader("2️⃣ Bowling Speed vs Wickets")
fig2, ax2 = plt.subplots(figsize=(12, 6))
scatter = sns.scatterplot(
    data=df,
    x='Pace (km/h)',
    y='Wickets',
    size='Wickets',
    hue='Economy_calc',
    palette='coolwarm',
    alpha=0.7,
    sizes=(50, 300),
    ax=ax2
)
sns.regplot(
    data=df,
    x='Pace (km/h)',
    y='Wickets',
    scatter=False,
    color='black',
    line_kws={"linestyle": "dashed"},
    ax=ax2
)
for i, row in df[df['Wickets'] >= 10].iterrows():
    ax2.text(row['Pace (km/h)'] + 0.3, row['Wickets'] + 0.3, row['Bowler Name'], fontsize=7)

plt.title('Bowling Speed vs Wickets Taken')
plt.xlabel('Pace (km/h)')
plt.ylabel('Wickets')
st.pyplot(fig2)

# 📊 Section 3: Dot/Bdry Ratio
st.subheader("3️⃣ Dot Ball to Boundary % Ratio")
dot_vs_boundary = df[['Bowler Name', 'Dot Ball %', 'Boundary % (4s & 6s)']].copy()
dot_vs_boundary['Dot/Boundary Ratio'] = dot_vs_boundary['Dot Ball %'] / dot_vs_boundary['Boundary % (4s & 6s)']
dot_vs_boundary_sorted = dot_vs_boundary.sort_values(by='Dot/Boundary Ratio', ascending=False)

st.markdown("#### 🏆 Top 5 Most Disciplined Bowlers")
st.dataframe(dot_vs_boundary_sorted.head(5), use_container_width=True)

# 📊 Section 4: Heatmap
st.subheader("4️⃣ Correlation Matrix of Economy")
fig4, ax4 = plt.subplots(figsize=(6, 5))
corr = df[['Average Runs per Over (PP)', 'Average Runs per Over (MO)', 'Average Runs per Over (DO)', 'Economy_calc']].corr()
sns.heatmap(corr, annot=True, cmap='vlag', center=0, ax=ax4)
plt.title("Correlation Matrix")
st.pyplot(fig4)
st.markdown("> 💡 **Note**: Death Over economy has the highest impact on overall economy.")

# 📊 Section 5: Composite Score
st.subheader("5️⃣ Composite Performance Score")

scaler = MinMaxScaler()
df[['Dot Ball %_scaled', 'Wickets_scaled', 'Economy_scaled']] = scaler.fit_transform(
    df[['Dot Ball %', 'Wickets', 'Economy_calc']]
)
df['Performance Score'] = (df['Dot Ball %_scaled'] + df['Wickets_scaled'] + (1 - df['Economy_scaled'])) / 3
df_top = df.sort_values(by='Performance Score', ascending=False)

st.markdown("#### 🎯 Top 5 Bowlers by Composite Score")
st.dataframe(df_top[['Bowler Name', 'Dot Ball %', 'Wickets', 'Economy_calc', 'Performance Score']].head(5), use_container_width=True)
