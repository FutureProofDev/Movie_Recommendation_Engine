import streamlit as st
import random
import pandas as pd
#import recommender as rc
import movie_icon_api as mia

st.set_page_config("MOVIE RECOMMENDATION ENGINE", page_icon="🎬", layout="wide")

with st.sidebar:
    st.header('About App')
    st.write('''\n This app is for users to get movie recommendations using various techniques learned in ***CS 254: Introduction to Artificial Intelligence***. \n 
    This project is being developed 
    by **Vladimir Noel Aduama**, 
    **Nii Sowah Kwabla Sowah**, 
    **Natalie Rose Andzie-Mensah**, and
    **Lisa Denise Baer**.''')

col1, col2, col3 = st.columns([9,25,5])

with col2:
    st.title("🎬 MOVIE RECOMMENDATION ENGINE")
    st.caption("Personalized picks based on your AI cluster & selected mood")

st.divider()



st.subheader("🎭 Today's Vibe Questionnaire")
st.write("Pick your top 3 genres or hit **Surprise me!** to generate instant recommendations.")

#MovieLens genres list
genres = [
    'Action', 'Adventure', 'Animation', "Children's", 'Comedy',
    'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror',
    'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
]

#initializing session state for the randomizer
if "g1_val" not in st.session_state:
    st.session_state.g1_val = None
if "g2_val" not in st.session_state:
    st.session_state.g2_val = None
if "g3_val" not in st.session_state:
    st.session_state.g3_val = None


if "recommendations_df" not in st.session_state:
    st.session_state.recommendations_df = None
if "searched_genres" not in st.session_state:
    st.session_state.searched_genres = []

#randomizer button
if st.button("🎲 I don't know, surprise me!", type="secondary"):
    random_picks = random.sample(genres, 3)
    st.session_state.g1_val = random_picks[0]
    st.session_state.g2_val = random_picks[1]
    st.session_state.g3_val = random_picks[2]
    st.rerun()

st.write("")

#dropdowns for genre selection
c1, c2, c3 = st.columns(3)


with c1:
    idx1 = genres.index(st.session_state.g1_val) if st.session_state.g1_val in genres else None
    g1 = st.selectbox("1.📽️What are you in the mood for?", options=genres, index=idx1, key="g1_val")

with c2:
    g2_options = [g for g in genres if g != g1]
    idx2 = g2_options.index(st.session_state.g2_val) if st.session_state.g2_val in g2_options else None
    g2 = st.selectbox("2.🥤Anything else you want to see?", options=g2_options, index=idx2, key="g2_val")

with c3:
    g3_options = [g for g in genres if g not in [g1, g2]]
    idx3 = g3_options.index(st.session_state.g3_val) if st.session_state.g3_val in g3_options else None
    g3 = st.selectbox("3.🍿Last spice to the sauce!", options=g3_options, index=idx3, key="g3_val")

#selected list
user_selected = [g for g in [g1, g2, g3] if g is not None]
selected_count = len(user_selected)

st.write("")

#find movies button
find_movies = st.button("**Find Movie Recommendations**", type="primary", disabled=selected_count < 3)

# --- RESULTS SECTION ---
if find_movies:
    st.session_state.searched_genres = user_selected

    # Backend Model Integration Point (Initial batch of 3)
    poster, link = mia.get_movie_poster('Chronicles (2021)')
    st.session_state.recommendations_df = pd.DataFrame({
        'Title': [f'{user_selected[0]} Chronicles (2021)', f'{user_selected[1]} Returns (2019)',
                  f'{user_selected[2]} Legacy (2023)'],
        'Main Genre': [user_selected[0], user_selected[1], user_selected[2]],
        'Predicted Rating': [4.9, 4.7, 4.5]
    })



#results
if st.session_state.recommendations_df is not None:
    st.divider()
    st.success(f"Finding the best {', '.join(st.session_state.searched_genres)} movies for you right now...")

    st.subheader("✨Your Custom Picks for Today:")

    # Display the stored DataFrame
    st.dataframe(st.session_state.recommendations_df, use_container_width=True, hide_index=True)

    #load more button
    if st.button("Load More Recommendations ➕"):
        sg = st.session_state.searched_genres

        # Simulated next batch from backend ML model
        more_movies = pd.DataFrame({
            'Title': [f'{sg[0]} Part II (2024)', f'{sg[1]} Reloaded (2022)'],
            'Main Genre': [sg[0], sg[1]],
            'Predicted Rating': [4.4, 4.2]
        })

        # Append new picks to existing session state DataFrame & rerun
        st.session_state.recommendations_df = pd.concat([st.session_state.recommendations_df, more_movies],ignore_index=True)
        st.rerun()