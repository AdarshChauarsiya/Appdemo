import streamlit as st
import mysql.connector


# Function to establish a database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="prac"
    )


# Function to check if a username exists
def username_exists(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM prac WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None


# Function to validate user login
def validate_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM prac WHERE username = %s AND password = %s", (username, password))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None




# Streamlit app starts here
st.title("Login and Signup Page")

# State management for login
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

# If user is logged in, show their dashboard
if st.session_state["logged_in_user"]:
    st.subheader(f"Welcome, {st.session_state['logged_in_user']}!")
    if st.button("Logout"):
        st.session_state["logged_in_user"] = None  # Clear session state
        st.stop()

# If user is not logged in, show login and signup options
else:
    # Tabs for login and signup
    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login")and username and password:
            if validate_login(username, password):
                st.session_state["logged_in_user"] = username
                st.success("Login successful!")
                st.switch_page("pages/fetch.py")

            else:
                st.error("Invalid username or password.")
        else:
            st.error("Please Enter Username ans Password.")
    with tab2:
        st.subheader("Signup")
        username = st.text_input("New Username", key="signup_username")
        password = st.text_input("New Password", type="password", key="signup_password")
        cnfpassword = st.text_input("New Confirm Password",type="password")
        if st.button("Signup"):
            if username_exists(username):
                st.error("Username already exists. Please choose a different username.")
            else:
                if password == cnfpassword:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO prac (username, password) VALUES (%s, %s)", (username, password))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success("Signup successful! Please log in.")
                else:
                    st.error("Password Not Matched. Please try again.")


