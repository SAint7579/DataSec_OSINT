import streamlit as st
import time
import tweepy
import re
import altair as alt
from textblob import TextBlob
from collections import defaultdict, namedtuple
import pandas as pd
from datetime import datetime, timedelta
import json
import sys
import os
from bertopic import BERTopic
from textblob import TextBlob
sys.path.append(os.path.join(os.path.dirname(__file__), "C:/Users/vishw/OneDrive/Desktop/Projects/DataSec_OSINT/"))
sys.path.append(os.path.join(os.path.dirname(__file__), "C:/Users/vishw/OneDrive/Desktop/Projects/DataSec_OSINT/Utils"))
from glob import glob
from linkedin_utils import start_browser, sign_in, validate_profile, get_post, get_jobs, model_topic

with open('C:/Users/vishw/OneDrive/Desktop/Projects/DataSec_OSINT/UI/cred.json') as f:
    cred = json.load(f)
    username = cred['linkedin_uname']
    password = cred['linkedin_pass']


def get_posts_and_jobs(full_name, images):
    browser = start_browser()
    sign_in(browser, username, password)

    # links = get_links(full_name, browser)[:5] #Can comment this out if validate_profile works
    # profile_link = links[0] # Can comment this out if validate_profile works

    profile_link = validate_profile(full_name, images, browser) #Commented out since validate_profile is not working
    
    print(profile_link)
    post_list = get_post(browser, profile_link)
    job_list = get_jobs(browser, profile_link)

    return post_list, job_list


st.title("Exhaustive Search")
st.markdown(
    "This mini-app lets you scrape information from an individual's LinkedIn profile using their full name and few pictures."
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
        posts, jobs = get_posts_and_jobs(full_name, glob(traget_folder+"*"))        
        # Display the result in a green box
        st.success("Results:")
        st.write("**WORK**")
        for job in jobs:
            with st.expander(job[0]):
                for item in job[1:]:
                    if item is not None:
                        st.write(item)

        st.write("**POSTS**")
        doc_vis, bar_vis = model_topic(posts)

        ## Plotting visualization
        st.plotly_chart(doc_vis, use_container_width=True)
        st.plotly_chart(bar_vis, use_container_width=True)
            

