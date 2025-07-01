import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Form Data Dashboard", layout="wide")
st.title("📋 Form Data Dashboard")

# Load CSV with caching
@st.cache_data
def load_data():
    return pd.read_csv("form_data.csv")

# Try to load data
try:
    df = load_data()
    st.success(f"✅ Loaded {len(df)} records from form_data.csv")

    # Check for required columns
    required_columns = ["Gender", "Age", "Interests"]
    if not all(col in df.columns for col in required_columns):
        st.error("❌ CSV is missing one or more required columns: Gender, Age, Interests.")
        st.stop()

    # Sidebar filters
    st.sidebar.header("🔍 Filter Data")
    gender_filter = st.sidebar.multiselect("Filter by Gender", options=df["Gender"].dropna().unique())
    interest_filter = st.sidebar.multiselect(
        "Filter by Interests",
        options=["AI", "Web Dev", "Music", "Gaming", "Sports", "Art"]
    )

    filtered_df = df.copy()

    # Apply gender filter
    if gender_filter:
        filtered_df = filtered_df[filtered_df["Gender"].isin(gender_filter)]

    # Apply interest filter
    if interest_filter:
        def has_interest(interests):
            return any(interest.strip() in [i.strip() for i in interests.split(",")] for interest in interest_filter)

        filtered_df = filtered_df[filtered_df["Interests"].apply(has_interest)]

    # Show basic stats
    st.subheader("📊 Dataset Overview")
    st.dataframe(df.describe(include='all'), use_container_width=True)

    st.subheader("📄 Filtered Data")
    st.dataframe(filtered_df, use_container_width=True)
    st.info(f"Showing {len(filtered_df)} of {len(df)} records")

    # Visualization section
    st.subheader("📊 Visual Insights")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🎂 Age Distribution")

        # Ensure Age is numeric and clean
        filtered_df["Age"] = pd.to_numeric(filtered_df["Age"], errors="coerce")
        invalid_age_count = filtered_df["Age"].isna().sum()
        filtered_df = filtered_df.dropna(subset=["Age"])

        if invalid_age_count > 0:
            st.warning(f"Dropped {invalid_age_count} records with invalid age values.")

        fig1 = px.histogram(
            filtered_df,
            x="Age",
            nbins=10,
            title="Age Distribution",
            color_discrete_sequence=['#636EFA']  # Custom color
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown("#### 🚻 Gender Distribution")
        gender_counts = filtered_df["Gender"].value_counts().reset_index()
        gender_counts.columns = ["Gender", "Count"]
        fig2 = px.pie(
            gender_counts,
            names="Gender",
            values="Count",
            title="Gender Distribution",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Interests breakdown
    st.markdown("#### 🎯 Top Interests")
    interest_counts = {}

    for interests in filtered_df["Interests"]:
        for interest in [i.strip() for i in interests.split(",")]:
            interest_counts[interest] = interest_counts.get(interest, 0) + 1

    interest_df = pd.DataFrame(list(interest_counts.items()), columns=["Interest", "Count"])
    interest_df = interest_df.sort_values("Count", ascending=False)

    fig3 = px.bar(
        interest_df,
        x="Count",
        y="Interest",
        orientation='h',
        title="Top Interests",
        color='Count',
        color_continuous_scale='viridis'
    )
    st.plotly_chart(fig3, use_container_width=True)

except FileNotFoundError:
    st.error("❌ form_data.csv not found. Please run the generator script first.")
