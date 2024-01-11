import streamlit as st
import os
import sys
import json
from glob import glob 

sys.path.append(os.path.join(os.path.dirname(__file__), "C:/Users/vishw/OneDrive/Desktop/Projects/DataSec_OSINT/"))
sys.path.append(os.path.join(os.path.dirname(__file__), "C:/Users/vishw/OneDrive/Desktop/Projects/DataSec_OSINT/Utils"))

from facebook_utils import start_browser, sign_in, get_links, get_info, get_friends, validate_profile

## Read cred.json for username and password
with open('C:/Users/vishw/OneDrive/Desktop/Projects/DataSec_OSINT/UI/cred.json') as f:
    cred = json.load(f)
    username = cred['username']
    password = cred['password']

def search_profile(full_name, images):
    browser = start_browser()
    sign_in(browser, username, password)

    # links = get_links(full_name, browser)[:5] #Can comment this out if validate_profile works

    # profile_link = links[0] # Can comment this out if validate_profile works

    profile_link = validate_profile(full_name, images, browser) #Commented out since validate_profile is not working

    personal_info = get_info(profile_link, browser)

    friend_list = get_friends(profile_link, browser)
    
    return personal_info, friend_list



st.title("Exhaustive Search")
st.markdown(
    "This mini-app lets you search for a person's social media profile using their full name and few pictures."
)

full_name = st.text_input(label="Full Name", placeholder="John Doe")

uploaded_files = st.file_uploader("Choose multiple images", type=["jpg", "jpeg"], accept_multiple_files=True)

# Check if any images have been uploaded
if uploaded_files is not None:
    st.write("You have uploaded", len(uploaded_files), "image(s).")
    ## Move the files to Test_images folder
    traget_folder = "C:/Users/vishw/OneDrive/Desktop/Projects/DataSec_OSINT/UI/target_image/"
    ## Clear the target folder
    for file in os.listdir(traget_folder):
        os.remove(os.path.join(traget_folder, file))
    ## Save the uploaded files to target folder
    for file in uploaded_files:
        with open(os.path.join(traget_folder, file.name), "wb") as f:
            f.write(file.getbuffer())


search_button = st.button(
            label="Search",
            type="primary"
        )

result_placeholder = st.empty()

with st.spinner("Fetching information..."):
    if search_button:
        # Trigger the function when the button is pressed
        result, friend_list = search_profile(full_name, glob(traget_folder+"*"))
        print(friend_list)
        
        # Display the result in a green box
        st.success("Result:")
        for category, data in result.items():
            if data is not None:
                st.write(f"**{category.capitalize()}**")
                for lst in data:
                    for item in lst:
                        if item is not None:
                            st.write(item)
                st.markdown("---")

        st.container()

        num_friends_to_display = 10

        st.title("Friends and Social Media Profiles")

        for friend_data in friend_list[1:num_friends_to_display]:
            friend_name = friend_data[0]
            social_media_link = friend_data[1]

            with st.expander(friend_name):
                st.write(f"Social Media Profile: {social_media_link}")