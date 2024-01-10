import streamlit as st
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))


from facebook import validate_profile, start_browser, sign_in, get_links

def search_profile(full_name, images):
    browser = start_browser()
    sign_in(browser, "email", "password")
    
    profile_link = validate_profile(full_name, images, browser)
    
    return profile_link



st.title("Exhaustive Search")
st.markdown(
    "This mini-app lets you search for a person's social media profile using their full name and few pictures."
)

full_name = st.text_input(label="Full Name", placeholder="John Doe")

uploaded_files = st.file_uploader("Choose multiple images", type=["jpg", "jpeg"], accept_multiple_files=True)

# Check if any images have been uploaded
if uploaded_files is not None:
    st.write("You have uploaded", len(uploaded_files), "image(s).")

search_button = st.button(
            label="Search",
            type="primary",
            on_click=search_profile,
            args = [full_name, uploaded_files]
        )