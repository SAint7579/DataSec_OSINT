import streamlit as st


def search_profile(email):
    pass

st.title("Efficient Search")
st.markdown(
    "This mini-app lets you search for a person's social media profile using their email."
)

email = st.text_input(label="Email", placeholder="johndoe@example.com")

search_button = st.button(
            label="Search",
            type="primary",
            on_click=search_profile,
            args = [email]
        )