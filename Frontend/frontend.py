import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config("MOVIE RECOMMENDATION ENGINE", page_icon="🎬", layout="wide")

with st.sidebar:
    st.header('About App')
    st.write('''\n This app is for users to get movie recommendations using various techniques learned in ***CS 254: Introduction to Artificial Intelligence***. \n 
    This project is being developed 
    by **Vladimir Noel Aduama**, 
    **Nii Sowah Kwabla Sowah**, 
    **Natalie Rose Andzie-Mensah**, and
    **Lisa Denise Baer**.''')

left_space, middle_content, right_space = st.columns([2, 9, 1])

home_page = st.Page("pages/homepage.py", title = "Home", default = True)
questionnaire_page = st.Page("pages/questionnaire.py", title = "Questionnaire")
profile_page = st.Page("pages/userprofile.py", title = "Profile")

pg = st.navigation([home_page, questionnaire_page, profile_page], position="top")

pg.run()
