import streamlit as st

# Page setup
st.set_page_config(page_title="Calculator", layout="centered")
st.markdown("<h1 style='text-align: center;'>🧮 Streamlit Calculator</h1>", unsafe_allow_html=True)

# Initialize expression state
if "expression" not in st.session_state:
    st.session_state.expression = ""

# Function to handle button press
def press(key):
    if key == "C":
        st.session_state.expression = ""
    elif key == "=":
        try:
            st.session_state.expression = str(eval(st.session_state.expression))
        except:
            st.session_state.expression = "Error"
    else:
        st.session_state.expression += key

# Custom CSS for button style
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 20px;
        background-color: #f0f0f5;
        color: #333;
        border-radius: 8px;
        border: 1px solid #ccc;
    }
    .stTextInput>div>div>input {
        text-align: right;
        font-size: 28px;
        height: 60px;
    }
    </style>
""", unsafe_allow_html=True)

# Display screen
st.text_input("Display", value=st.session_state.expression, key="display", disabled=True, label_visibility="collapsed")

# Button layout
buttons = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"],
    ["C"]
]

# Create buttons in a grid layout
for row in buttons:
    cols = st.columns(len(row))
    for i, btn in enumerate(row):
        with cols[i]:
            st.button(btn, on_click=press, args=(btn,))


# python -m streamlit run Streamlit_calc.py

# pip install streamlit
# pip show streamlit
