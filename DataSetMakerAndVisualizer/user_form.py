import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="User Data Form", layout="centered")
st.title("📋 User Data Input Form")

# CSV file to store data
CSV_FILE = "form_data.csv"

# Initialize CSV file if it doesn't exist
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["Name", "Email", "Age", "Gender", "DOB", "Time", "Interests", "Bio", "Agreed"])
    df_init.to_csv(CSV_FILE, index=False)

# Create the form
with st.form("user_form"):
    st.subheader("Fill in your details")

    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
    gender = st.radio("Gender", ["Male", "Female", "Other"])
    dob = st.date_input("Date of Birth")
    time = st.time_input("Preferred Contact Time")
    interests = st.multiselect("Your Interests", ["AI", "Web Dev", "Music", "Gaming", "Sports", "Art"])
    bio = st.text_area("Short Bio")
    agreed = st.checkbox("I agree to the terms and conditions")

    submitted = st.form_submit_button("Submit")

# Handle submission
if submitted:
    if not agreed:
        st.warning("You must agree to the terms and conditions.")
    elif not name or not email:
        st.warning("Please complete all required fields.")
    else:
        new_data = {
            "Name": name,
            "Email": email,
            "Age": age,
            "Gender": gender,
            "DOB": dob,
            "Time": time,
            "Interests": ", ".join(interests),
            "Bio": bio,
            "Agreed": agreed
        }

        df = pd.read_csv(CSV_FILE)
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)


        st.success("✅ Your data has been saved successfully!")

        st.write("### Submitted Data:")
        st.write(pd.DataFrame([new_data]))
