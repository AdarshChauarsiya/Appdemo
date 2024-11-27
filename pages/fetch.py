import streamlit as st
import mysql.connector
import requests
import pandas as pd

response_codes = list(range(100, 1001))

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="prac"
    )

# Function to check if an image exists
def image_exists(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Function to filter response codes
def filter_images(filter_value):
    if filter_value.isdigit():
        return [code for code in response_codes if code == int(filter_value)]
    elif "x" in filter_value:
        prefix = filter_value.replace("x", "")
        return [code for code in response_codes if str(code).startswith(prefix) and len(str(code)) == len(filter_value)]
    return []

# Check login status
if "logged_in_user" not in st.session_state:
    st.warning("You are not logged in. Please log in first.")
    st.switch_page("app.py")
    st.stop()

# Get the logged-in user
username = st.session_state["logged_in_user"]

# Initialize session state variables
if "show_save_button" not in st.session_state:
    st.session_state["show_save_button"] = False
if "saved_codes" not in st.session_state:
    st.session_state["saved_codes"] = []
if "filter_data" not in st.session_state:
    st.session_state["filter_data"] = {}

# Header
st.header("HTTP Status Dogs")
st.write(f"Welcome, **{username}**!")
st.write("Dogs for every HyperText Transfer Protocol response status code.")

# Filter input
filter_value = st.text_input("Enter filter (e.g., 203, 2xx, 20x, 3xx):").strip()

# Search button logic
st.session_state["show_save_button"] = True
col1, col2 = st.columns(2)
with col1:
    if st.button("Search"):
        filtered_codes = filter_images(filter_value)

        # Store the filtered codes in session_state under the current filter value
        if filtered_codes:
            st.session_state["filter_data"][filter_value] = filtered_codes
            # st.write(f"Filtered Codes for `{filter_value}`: {filtered_codes}")
        else:
            st.warning(f"No codes found for filter `{filter_value}`.")
     # Show the "Save List" button
with col2:
    if st.button("Logout"):

        st.switch_page("app.py")

# Conditionally render the second button and filtered images
if st.session_state["show_save_button"]:
    col1, col2 = st.columns(2)

    # Save List button
    with col1:
        if st.button("Save List"):
            filter_df = pd.DataFrame(
                list(st.session_state["filter_data"].items()), columns=["Filter", "Codes"]
            )

            # Store the DataFrame in session state
            st.session_state["saved_filter_data"] = filter_df
            # st.write("Saved Filter DataFrame:")
            # st.write(st.session_state["saved_filter_data"])
            conn = get_connection()
            cursor = conn.cursor()
            for code in st.session_state["saved_codes"]:
                try:
                    cursor.execute(
                        "INSERT INTO code1 (username, code) VALUES (%s, %s)",
                        (username, code)
                    )
                except mysql.connector.IntegrityError:
                    st.warning(f"Code `{code}` is already saved.")
            conn.commit()
            conn.close()
            st.success("List saved to the database!")

    # Display the filter data
    if st.session_state["filter_data"]:
        df = pd.DataFrame(
            [{"Filter": key, "Codes": value} for key, value in st.session_state["filter_data"].items()]
        )
        # st.write(df)
    with col2:
        with col2:
            if st.button("See Saved List"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT code FROM code1 WHERE username = %s", (username,))
                saved_codes = [row[0] for row in cursor.fetchall()]
                conn.close()

                st.write("Your Saved Codes:")
                st.switch_page("pages/savedlist.py")
    # Filter images
    filtered_codes = filter_images(filter_value)
    if filtered_codes:
        st.write(f"Filtered images for `{filter_value}`:")
        for code in filtered_codes:
            img_url = f"https://http.dog/{code}.jpg"
            if image_exists(img_url):
                st.image(img_url, caption=f"Response Code: {code}")
                if code not in st.session_state["saved_codes"]:
                    st.session_state["saved_codes"].append(code)
            else:
                st.warning(f"Image for response code `{code}` does not exist.")
    else:
        st.warning(f"No images found for filter `{filter_value}`.")
