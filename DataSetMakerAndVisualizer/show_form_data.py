import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page config
st.set_page_config(page_title="Form Data Dashboard", layout="wide")

st.title("📋 Form Data Dashboard")

# Load CSV
try:
    df = pd.read_csv("form_data.csv")
    st.success(f"✅ Loaded {len(df)} records from form_data.csv")

    # Sidebar filters
    st.sidebar.header("🔍 Filter Data")
    gender_filter = st.sidebar.multiselect("Filter by Gender", options=df["Gender"].unique())
    interest_filter = st.sidebar.multiselect("Filter by Interests", options=["AI", "Web Dev", "Music", "Gaming", "Sports", "Art"])

    filtered_df = df.copy()

    if gender_filter:
        filtered_df = filtered_df[filtered_df["Gender"].isin(gender_filter)]
    if interest_filter:
        filtered_df = filtered_df[filtered_df["Interests"].str.contains('|'.join(interest_filter))]

    # Show basic stats
    st.subheader("📊 Dataset Overview")
    st.write(df.describe(include='all'))

    st.subheader("📄 Filtered Data")
    st.dataframe(filtered_df, use_container_width=True)
    st.info(f"Showing {len(filtered_df)} of {len(df)} records")

    # Visualization section
    st.subheader("📊 Visual Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🎂 Age Distribution")
        fig1, ax1 = plt.subplots()
        sns.histplot(filtered_df["Age"], bins=10, kde=True, color='skyblue', ax=ax1)
        ax1.set_xlabel("Age")
        ax1.set_ylabel("Count")
        st.pyplot(fig1)

    with col2:
        st.markdown("#### 🚻 Gender Distribution")
        gender_counts = filtered_df["Gender"].value_counts()
        fig2, ax2 = plt.subplots()
        ax2.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("pastel"))
        ax2.axis('equal')
        st.pyplot(fig2)

    # Interests breakdown
    st.markdown("#### 🎯 Top Interests")
    interest_counts = {}

    for interests in filtered_df["Interests"]:
        for interest in [i.strip() for i in interests.split(",")]:
            interest_counts[interest] = interest_counts.get(interest, 0) + 1

    interest_df = pd.DataFrame(list(interest_counts.items()), columns=["Interest", "Count"]).sort_values("Count", ascending=False)

    fig3, ax3 = plt.subplots()
    sns.barplot(data=interest_df, x="Count", y="Interest", palette="viridis", ax=ax3)
    ax3.set_xlabel("Number of People Interested")
    st.pyplot(fig3)

except FileNotFoundError:
    st.error("❌ form_data.csv not found. Please run the generator script first.")

