import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config("🏏 IPL 2025 Bowler Dashboard", layout="wide")

# --- Data Loading & Cleaning ---
@st.cache_data
def load_and_clean_data(min_overs=10):
    url = "https://raw.githubusercontent.com/kanadkapil/Data/main/IPL2025_BowlerData.csv"
    df = pd.read_csv(url, on_bad_lines='skip')
    numeric_cols = [
        'Overs', 'Pace (km/h)', 'Runs Conceded', 'Boundary % (4s & 6s)', 'Dot Ball %',
        'Average Runs per Over (PP)', 'Average Runs per Over (MO)', 'Average Runs per Over (DO)', 'Wickets'
    ]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    df.dropna(subset=numeric_cols, inplace=True)
    df = df[df['Overs'] >= min_overs].copy()
    df['Economy_calc'] = df['Runs Conceded'] / df['Overs']
    return df

# --- Sidebar Filters ---
def add_filters(df):
    st.sidebar.header("🎛️ Filter Options")
    overs = st.sidebar.slider("Minimum Overs", 0, int(df['Overs'].max()), 10)
    wickets = st.sidebar.slider("Minimum Wickets", 0, int(df['Wickets'].max()), 0)
    pace = st.sidebar.slider("Pace (km/h)", int(df['Pace (km/h)'].min()), int(df['Pace (km/h)'].max()), (120, 150))
    economy = st.sidebar.slider("Max Economy", 0.0, float(df['Economy_calc'].max()), float(df['Economy_calc'].max()))
    return df[(df['Overs'] >= overs) & (df['Wickets'] >= wickets) & (df['Pace (km/h)'].between(*pace)) & (df['Economy_calc'] <= economy)]

# --- Data Table & Dot/Boundary Efficiency ---
def show_data_table(df):
    st.subheader("📋 Complete Bowler Dataset")
    st.dataframe(df.sort_values(by='Wickets', ascending=False), use_container_width=True)

def dot_vs_boundary_ratio(df):
    st.subheader("🔥 Top 5 Most Disciplined Bowlers (Dot/Boundary Ratio)")
    df['Dot/Boundary Ratio'] = df['Dot Ball %'] / df['Boundary % (4s & 6s)']
    top5 = df.nlargest(5, 'Dot/Boundary Ratio')
    st.dataframe(top5[['Bowler Name', 'Dot Ball %', 'Boundary % (4s & 6s)', 'Dot/Boundary Ratio']], use_container_width=True)

# --- Additional Visuals ---
def extra_visuals(df):
    st.header("✨ Additional Visualizations")
    top = df.nlargest(10, 'Wickets')

    # Area chart: cumulative wickets & overs for top bowlers
    area_df = top.sort_values('Wickets')
    st.markdown("## ⛰️ Area Chart: Wickets vs Overs")
    area_fig = go.Figure()
    area_fig.add_trace(go.Scatter(x=area_df['Bowler Name'], y=area_df['Wickets'], name='Wickets', fill='tozeroy'))
    area_fig.add_trace(go.Scatter(x=area_df['Bowler Name'], y=area_df['Overs'], name='Overs', fill='tonexty'))
    st.plotly_chart(area_fig, use_container_width=True)
    
    
        # Phase-wise Economy Chart
    st.subheader("📊 Average Economy by Match Phase")
    melt_df = df.melt(
        id_vars='Bowler Name',
        value_vars=['Average Runs per Over (PP)', 'Average Runs per Over (MO)', 'Average Runs per Over (DO)'],
        var_name='Phase', value_name='Economy'
    )
    phase_fig = px.bar(melt_df, x='Economy', y='Bowler Name', color='Phase', orientation='h')
    st.plotly_chart(phase_fig, use_container_width=True)

    # Pace vs Wickets
    st.subheader("🚀 Pace vs Wickets")
    scatter_fig = px.scatter(
        df, x='Pace (km/h)', y='Wickets',
        size='Wickets', color='Economy_calc',
        hover_name='Bowler Name', color_continuous_scale='RdYlGn_r'
    )
    st.plotly_chart(scatter_fig, use_container_width=True)

    # Bubble Chart
    st.markdown("## 🫧 Bubble Chart: Pace vs Economy (Bubble = Wickets)")
    bubble_fig = px.scatter(df, x='Pace (km/h)', y='Economy_calc',
                            size='Wickets', color='Wickets',
                            hover_name='Bowler Name', size_max=40,
                            color_continuous_scale='Viridis')
    st.plotly_chart(bubble_fig, use_container_width=True)

    # Donut Chart
    st.markdown("## 🍩 Donut Chart: Top 5 Wicket Shares")
    donut = top[['Bowler Name', 'Wickets']]
    donut_fig = px.pie(donut, names='Bowler Name', values='Wickets', hole=0.5)
    st.plotly_chart(donut_fig, use_container_width=True)

    # Gauge Chart for one chosen bowler
    st.markdown("## ⏱️ Economy Gauge")
    b = st.selectbox("Select a bowler for economy gauge", df['Bowler Name'].unique())
    econ = float(df.loc[df['Bowler Name'] == b, 'Economy_calc'].iloc[0])
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=econ,
        domain={'x':[0,1],'y':[0,1]},
        title={'text':f"{b}'s Economy Rate"},
        gauge={'axis': {'range': [0, max(df['Economy_calc'])]},
               'bar': {'color': "darkblue"}}
    ))
    st.plotly_chart(gauge_fig, use_container_width=True)

    # Treemap for runs conceded
    st.markdown("## 🗺️ Treemap: Runs Conceded Overview")
    tree = top[['Bowler Name', 'Runs Conceded']]
    tree_fig = px.treemap(tree, path=['Bowler Name'], values='Runs Conceded',
                          color='Runs Conceded', color_continuous_scale='RdBu')
    st.plotly_chart(tree_fig, use_container_width=True)

# --- Bowler Comparison with Dual Selection ---
def compare_bowlers(df):
    st.header("🆚 Compare Two Bowlers")

    bowler_list = df['Bowler Name'].unique()
    # Visual comparison
    st.subheader("🎯 Radar & Charts Comparison")
    c1, c2 = st.columns(2)
    b1 = c1.selectbox("Bowler for Charts: A", bowler_list)
    b2 = c2.selectbox("Bowler for Charts: B", bowler_list, index=1)
    if b1 != b2:
        sub = df[df['Bowler Name'].isin([b1, b2])]
        stats = ['Dot Ball %', 'Wickets', 'Economy_calc']
        nd = MinMaxScaler().fit_transform(sub[stats])
        rd = pd.DataFrame(nd, columns=stats); rd['Bowler Name']=sub['Bowler Name'].values
        fig = go.Figure()
        for _, r in rd.iterrows():
            fig.add_trace(go.Scatterpolar(r=list(r[stats])+[r[stats[0]]], theta=stats+[stats[0]], fill='toself', name=r['Bowler Name']))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
        st.bar_chart(sub.set_index('Bowler Name')[["Wickets", "Economy_calc"]])
        pie_fig = px.pie(sub, names='Bowler Name', values='Overs', title='Overs Distribution')
        st.plotly_chart(pie_fig, use_container_width=True)
        ph = ['Average Runs per Over (PP)', 'Average Runs per Over (MO)', 'Average Runs per Over (DO)']
        ld = sub.melt(id_vars='Bowler Name', value_vars=ph, var_name='Phase', value_name='Economy')
        line_fig = px.line(ld, x='Phase', y='Economy', color='Bowler Name', markers=True)
        st.plotly_chart(line_fig, use_container_width=True)
    else:
        st.warning("Select two different bowlers for charts.")

    # Side-by-side table
    st.subheader("📋 Side-by-Side Comparison Table")
    c3, c4 = st.columns(2)
    s1 = c3.selectbox("Bowler for Table: A", bowler_list, key='t1')
    s2 = c4.selectbox("Bowler for Table: B", bowler_list, index=1, key='t2')
    if s1 != s2:
        subs = df[df['Bowler Name'].isin([s1, s2])]
        cols = [col for col in df.columns if col!='Bowler Name']
        sel = st.multiselect("Choose Stats", options=cols, default=['Wickets','Economy_calc','Dot Ball %','Overs'])
        if sel:
            st.dataframe(subs[['Bowler Name']+sel].set_index('Bowler Name').T, use_container_width=True)
        else:
            st.info("Select at least one stat.")
    else:
        st.warning("Select two different bowlers for the table.")

# --- Main App ---
def main():
    st.title("🏏 IPL 2025 Bowler Dashboard")
    st.sidebar.header("📥 Filters & Settings")
    df = load_and_clean_data(st.sidebar.number_input("Start Minimum Overs", value=10, min_value=0))
    df = add_filters(df)
    show_data_table(df)
    dot_vs_boundary_ratio(df)
    extra_visuals(df)
    compare_bowlers(df)

if __name__ == "__main__":
    main()
