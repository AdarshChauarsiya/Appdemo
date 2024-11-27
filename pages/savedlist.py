import streamlit as st
import mysql.connector

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="prac"
    )

# Check login status
if "logged_in_user" not in st.session_state:
    st.warning("You are not logged in. Please log in first.")
    st.switch_page("app.py")
    st.stop()

username = st.session_state["logged_in_user"]

# Header
st.header("Your Saved Images")
st.write(f"Saved images for **{username}**:")

# Fetch saved images from the database
if st.checkbox("Show Saved Lists"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT code FROM code1 WHERE username = %s", (username,))
    saved_codes = [row[0] for row in cursor.fetchall()]
    conn.close()

    if saved_codes:
        cols = st.columns(3)  # Display images in 3 columns
        for i, code in enumerate(saved_codes):
            img_url = f"https://http.dog/{code}.jpg"
            # cols[i % 3].image(img_url, caption=f"Response Code: {code}")
    else:
        st.info("You have not saved any images.")

    # Show the saved filter DataFrame if available
    if "saved_filter_data" in st.session_state:
        filter_df = st.session_state["saved_filter_data"]
        # st.write("Here is your saved filter DataFrame:")

        # Display DataFrame with clickable filter column
        for index, row in filter_df.iterrows():
            filter_value = row['Filter']
            # Display the filter as a button
            if st.button(f"Search for {filter_value}", key=f"filter_{index}"):
                # Store filtered data for display
                st.session_state["filter_data"] = {filter_value: row['Codes']}
                st.write(f"Displaying codes for filter `{filter_value}`:")
                filtered_codes = row['Codes']

                # Display images in 3 columns
                cols = st.columns(3)  # Set up 3 columns for displaying images
                for i, code in enumerate(filtered_codes):
                    img_url = f"https://http.dog/{code}.jpg"
                    cols[i % 3].image(img_url, caption=f"Response Code: {code}")
                    st.balloons()

# Delete images based on a pattern
pattern = st.text_input("Enter Pattern Which you want to delete (e.g., 101, 10x, 1xx, etc):")
col1, col2 = st.columns(2)

with col1:
    if st.button("Delete Images"):
        if pattern:
            # Replace 'x' with '%' for SQL LIKE pattern
            sql_pattern = pattern.replace("x", "%")

            try:
                # Establish connection
                conn = get_connection()
                cursor = conn.cursor()

                # SQL DELETE query to delete from database
                query = "DELETE FROM code1 WHERE code LIKE %s"
                cursor.execute(query, (sql_pattern,))
                conn.commit()

                # Now remove the corresponding filter from the DataFrame
                if "saved_filter_data" in st.session_state:
                    filter_df = st.session_state["saved_filter_data"]
                    # Remove the rows that match the pattern (based on the filter)
                    st.session_state["saved_filter_data"] = filter_df[~filter_df['Filter'].str.contains(pattern)]

                conn.close()

                # Feedback to the user
                st.success(f"Images with codes matching `{pattern}` have been deleted and removed from the saved filters!")

            except mysql.connector.Error as err:
                st.error(f"Error: {err}")

            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        else:
            st.warning("Please enter a valid pattern.")

with col2:
    if st.button("Search Images"):
        st.switch_page("pages/fetch.py")
