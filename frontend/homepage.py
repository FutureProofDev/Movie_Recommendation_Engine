import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import random
import pandas as pd
import backend.recommender as rc
import movie_icon_api as mia

def generate_real_recommendations(user_profile, selected_genres, movies_df, top_n=3):
    """
    Filters catalog by selected genres, scores candidates using recommender.predict_rating,
    and returns top_n ranked recommendations.
    """
    pattern = '|'.join(selected_genres)
    candidates = movies_df[movies_df['genres'].str.contains(pattern, case=False, na=False)].copy()

    if candidates.empty:
        candidates = movies_df.copy()

    predictions = []

    for idx, row in candidates.iterrows():
        movie_genres = str(row.get('genres', '')).split('|')
        genre_flags = {g: 1 if g in movie_genres else 0 for g in rc.GENRE_COLS}

        # Predict rating using Random Forest model
        score = rc.predict_rating(
            age=user_profile.get('age', 25),
            gender=user_profile.get('gender', 'F'),
            occupation=user_profile.get('occupation', 'student'),
            genre_flags=genre_flags
        )
        predictions.append(score)

    candidates['Predicted Rating'] = predictions
    candidates = candidates.sort_values(by='Predicted Rating', ascending=False)

    recommendations = candidates[['title', 'genres', 'Predicted Rating']].head(top_n).copy()
    recommendations.columns = ['Title', 'Main Genre', 'Predicted Rating']
    return recommendations


st.set_page_config(page_title="MOVIE RECOMMENDATION ENGINE", page_icon="🎬", layout="wide")


# --- DATA LOADING ---
# --- DATA LOADING ---
@st.cache_data
def load_movie_catalog():
    """Loads and parses the MovieLens movie dataset directly."""
    # Base path relative to project root
    catalog_path = Path(__file__).resolve().parent.parent / "data" / "ml-100k" / "u.item"

    # Check if u.item exists (standard MovieLens 100k format)
    if catalog_path.exists():
        cols = ['movie_id', 'title', 'release_date', 'video_release_date', 'IMDb_URL',
                'unknown', 'Action', 'Adventure', 'Animation', "Children's", 'Comedy',
                'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror',
                'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
        df = pd.read_csv(catalog_path, sep='|', names=cols, encoding='latin-1')

        # Build the 'genres' pipe-separated string for compatibility
        genre_cols = cols[5:]

        def extract_genres(row):
            active = [g for g in genre_cols if row[g] == 1]
            return '|'.join(active) if active else 'Unknown'

        df['genres'] = df.apply(extract_genres, axis=1)
        return df[['title', 'genres']]

    # Alternative: check for movies.csv if using ml-latest / ml-25m format
    csv_path = Path(__file__).resolve().parent.parent / "data" / "movies.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)

    # Fallback error if dataset file isn't found in expected paths
    raise FileNotFoundError("Could not locate u.item or movies.csv in the data directory.")


movies_df = load_movie_catalog()

# --- SIDEBAR ---
with st.sidebar:
    st.header('About App')
    st.write('''\n This app is for users to get movie recommendations using various techniques learned in **CS 254: Introduction to Artificial Intelligence**. \n 
    This project is being developed 
    by *Vladimir Noel Aduama*, 
    *Nii Sowah Kwabla Sowah*, 
    *Natalie Rose Andzie-Mensah*, and
    *Lisa Denise Baer*.''')

col1, col2, col3 = st.columns([9, 25, 5])

with col2:
    st.title("🎬 MOVIE RECOMMENDATION ENGINE")
    st.caption("Personalized picks based on your AI cluster & selected mood")

st.divider()

# Initialize session state for user profile
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "age": None,
        "gender": None,
        "occupation": None
    }

st.subheader("🎭 Today's Vibe Questionnaire")

st.markdown("#### 👤 Tell us about yourself")
d1, d2, d3 = st.columns(3)

# 1. Age Input
with d1:
    saved_age = st.session_state.user_profile.get("age")
    age_str = st.text_input(
        "Age",
        value=str(saved_age) if saved_age is not None else "",
        max_chars=3,
        placeholder="Choose an option"
    )
    user_age = int(age_str) if age_str.isdigit() else None

# 2. Gender Dropdown
with d2:
    gender_options = ["F", "M"]
    saved_gender = st.session_state.user_profile.get("gender")
    gender_idx = gender_options.index(saved_gender) if saved_gender in gender_options else None

    user_gender = st.selectbox(
        "Gender",
        options=gender_options,
        index=gender_idx,
        placeholder="Choose an option"
    )

# 3. Occupation Dropdown
with d3:
    occupations_list = [
        'administrator', 'artist', 'doctor', 'educator', 'engineer',
        'entertainment', 'executive', 'healthcare', 'homemaker', 'lawyer',
        'librarian', 'marketing', 'none', 'other', 'programmer', 'retired',
        'salesman', 'scientist', 'student', 'technician', 'writer'
    ]
    saved_occ = st.session_state.user_profile.get("occupation")
    occ_idx = occupations_list.index(saved_occ) if saved_occ in occupations_list else None

    user_occ = st.selectbox(
        "Occupation",
        options=occupations_list,
        index=occ_idx,
        placeholder="Choose an option",
        format_func=lambda x: x.capitalize()
    )

# Save demographic choices to session state
st.session_state.user_profile = {
    "age": user_age,
    "gender": user_gender,
    "occupation": user_occ
}

st.divider()

st.write("Pick your top 3 genres or hit *Surprise me!* to generate instant recommendations.")

# MovieLens genres list
genres = [
    'Action', 'Adventure', 'Animation', "Children's", 'Comedy',
    'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror',
    'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
]

# Initializing session state for the randomizer and recommendation count
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
if "rec_count" not in st.session_state:
    st.session_state.rec_count = 3

# Randomizer button
if st.button("🎲 I don't know, surprise me!", type="secondary"):
    random_picks = random.sample(genres, 3)
    st.session_state.g1_val = random_picks[0]
    st.session_state.g2_val = random_picks[1]
    st.session_state.g3_val = random_picks[2]
    st.rerun()

st.write("")

# Dropdowns for genre selection
c1, c2, c3 = st.columns(3)

with c1:
    idx1 = genres.index(st.session_state.g1_val) if st.session_state.g1_val in genres else None
    g1 = st.selectbox("1.What are you in the mood for?", options=genres, index=idx1, placeholder="Choose an option", key="g1_val")

with c2:
    g2_options = [g for g in genres if g != g1]
    idx2 = g2_options.index(st.session_state.g2_val) if st.session_state.g2_val in g2_options else None
    g2 = st.selectbox("2.Anything else you want to see?", options=g2_options, index=idx2, placeholder="Choose an option", key="g2_val")

with c3:
    g3_options = [g for g in genres if g not in [g1, g2]]
    idx3 = g3_options.index(st.session_state.g3_val) if st.session_state.g3_val in g3_options else None
    g3 = st.selectbox("3.Last spice to the sauce", options=g3_options, index=idx3, placeholder="Choose an option", key="g3_val")

# Selected list
user_selected = [g for g in [g1, g2, g3] if g is not None]
selected_count = len(user_selected)

# Check if profile is filled out
profile_complete = (
    st.session_state.user_profile["age"] is not None and
    st.session_state.user_profile["gender"] is not None and
    st.session_state.user_profile["occupation"] is not None
)

st.write("")

# Find movies button (disabled until profile + 3 genres are complete)
find_movies = st.button(
    "*Find Movie Recommendations*",
    type="primary",
    disabled=not (profile_complete and selected_count == 3)
)

# --- RESULTS GENERATION ---
if find_movies:
    st.session_state.searched_genres = user_selected
    st.session_state.rec_count = 3  # Reset count to 3 on new search

    with st.spinner("Calculating custom ML predictions across dataset..."):
        st.session_state.recommendations_df = generate_real_recommendations(
            user_profile=st.session_state.user_profile,
            selected_genres=user_selected,
            movies_df=movies_df,
            top_n=12  # Pre-score top 12 candidates so "Load More" is fast
        )

# --- RESULTS DISPLAY ---
if st.session_state.recommendations_df is not None:
    st.divider()
    st.success(f"Finding the best {', '.join(st.session_state.searched_genres)} movies for you right now...")

    st.subheader("Your Custom Picks for Today:")

    df = st.session_state.recommendations_df.head(st.session_state.rec_count)

    cols = st.columns(min(len(df), 3))
    for i, (_, row) in enumerate(df.iterrows()):
        col = cols[i % 3]
        with col:
            poster, link = mia.get_movie_poster(row['Title'])
            if poster:
                st.image(poster, width=200)
            else:
                st.caption("🎬 (no poster found)")
            st.markdown(f"**{row['Title']}**")
            st.write(f"Predicted Rating: *{row['Predicted Rating']:.2f} / 5.0*")
            if link:
                st.markdown(f"[More info]({link})")
            st.write("---")

    # Load More Button
    if st.session_state.rec_count < len(st.session_state.recommendations_df):
        if st.button("➕ Load More Recommendations"):
            st.session_state.rec_count += 3
            st.rerun()