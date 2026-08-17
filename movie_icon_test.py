"""
app.py

Single-file Streamlit demo for the Movie Recommendation Engine.
Combines the homepage + questionnaire flows and TMDb poster/IMDb lookup
into one runnable file, for showing teammates before everything is
split back into separate pages.

Run with:
    streamlit run app.py

Then paste your free TMDb API key into the sidebar field (get one at
https://www.themoviedb.org/settings/api — no cost, just sign up).

NOTE: This currently uses MOCK recommendation data (see the
`get_recommendations()` function) since recommender.py isn't wired in
yet. Swap that function's internals for real calls to
predict_rating() / get_user_cluster() once the models are ready.
"""

import re
import requests
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Movie Recommendation Engine", page_icon="🎬", layout="wide")

GENRES = [
    'unknown', 'Action', 'Adventure', 'Animation', "Children's", 'Comedy',
    'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror',
    'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
]

PLACEHOLDER_POSTER = "https://placehold.co/342x513?text=No+Poster"


# ---------------------------------------------------------------------------
# SIDEBAR — paste your TMDb API key here
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    api_key_input = st.text_input(
        "TMDb API Key",
        type="password",
        placeholder="4d388bda6838402665832c32d1b2aaf2",
        help="Get a free key at https://www.themoviedb.org/settings/api — "
             "no credit card needed, just create an account.",
    )
    st.caption("Posters/IMDb links won't load without a key, but the rest of the app still works.")

    st.divider()
    st.caption("Demo data note: recommendations below are mock data until "
               "recommender.py (K-Means + Random Forest) is wired in.")


# ---------------------------------------------------------------------------
# TMDb HELPERS
# ---------------------------------------------------------------------------
def _parse_title_year(raw_title):
    """MovieLens titles look like 'Toy Story (1995)' -> ('Toy Story', 1995)."""
    match = re.match(r"^(.*)\s\((\d{4})\)$", raw_title.strip())
    if match:
        return match.group(1).strip(), int(match.group(2))
    return raw_title.strip(), None


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def get_movie_media(raw_title, api_key):
    """Looks up a movie on TMDb, returns poster + IMDb/TMDb links."""
    if not api_key:
        return {"poster_url": PLACEHOLDER_POSTER, "tmdb_url": None, "imdb_url": None}

    title, year = _parse_title_year(raw_title)

    try:
        resp = requests.get(
            "https://api.themoviedb.org/3/search/movie",
            params={"api_key": api_key, "query": title, "year": year},
            timeout=5,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
    except requests.RequestException:
        return {"poster_url": PLACEHOLDER_POSTER, "tmdb_url": None, "imdb_url": None}

    if not results:
        return {"poster_url": PLACEHOLDER_POSTER, "tmdb_url": None, "imdb_url": None}

    movie = results[0]
    movie_id = movie["id"]
    poster_path = movie.get("poster_path")
    poster_url = f"https://image.tmdb.org/t/p/w342{poster_path}" if poster_path else PLACEHOLDER_POSTER
    tmdb_url = f"https://www.themoviedb.org/movie/{movie_id}"

    imdb_url = None
    try:
        ext_resp = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            params={"api_key": api_key, "append_to_response": "external_ids"},
            timeout=5,
        )
        ext_resp.raise_for_status()
        imdb_id = ext_resp.json().get("imdb_id")
        if imdb_id:
            imdb_url = f"https://www.imdb.com/title/{imdb_id}/"
    except requests.RequestException:
        pass

    return {"poster_url": poster_url, "tmdb_url": tmdb_url, "imdb_url": imdb_url}


def render_movie_cards(movies_df, api_key):
    """Renders a DataFrame of [Title, Genre, Predicted Rating] as poster cards."""
    cols = st.columns(len(movies_df))
    for col, (_, movie) in zip(cols, movies_df.iterrows()):
        media = get_movie_media(movie["Title"], api_key)
        with col:
            st.image(media["poster_url"], use_container_width=True)
            st.markdown(f"**{movie['Title']}**")
            st.caption(f"{movie['Genre']} · ⭐ {movie['Predicted Rating']}")
            if media["imdb_url"]:
                st.markdown(f"[IMDb ↗]({media['imdb_url']})")
            elif media["tmdb_url"]:
                st.markdown(f"[TMDb ↗]({media['tmdb_url']})")


# ---------------------------------------------------------------------------
# MOCK RECOMMENDATION LOGIC — swap for recommender.py once ready
# ---------------------------------------------------------------------------
def get_recommendations(genre_filter=None):
    mock_movies = pd.DataFrame({
        'Title': ['Star Wars (1977)', 'Godfather, The (1972)', 'Raiders of the Lost Ark (1981)',
                  'Pulp Fiction (1994)', 'Silence of the Lambs, The (1991)'],
        'Genre': ['Sci-Fi', 'Crime', 'Action', 'Crime', 'Drama'],
        'Predicted Rating': [4.9, 4.8, 4.7, 4.6, 4.5]
    })
    if genre_filter:
        filtered = mock_movies[mock_movies['Genre'].isin(genre_filter)]
        return filtered if not filtered.empty else mock_movies
    return mock_movies



page = st.radio("Navigate", ["🏠 Home", "📋 Questionnaire"], horizontal=True, label_visibility="collapsed")
st.divider()



if page == "🏠 Home":
    col1, col2, col3 = st.columns([9, 25, 5])
    with col2:
        st.title("🎬 MOVIE RECOMMENDATION ENGINE")
        st.caption("Personalized picks based on your AI cluster & current mood")

    current_user = st.session_state.get("user_id", 1)
    st.subheader(f"Welcome back, User #{current_user}!")

    tab1 = st.tabs(["Top Recommendations For You"])
    with tab1[0]:
        movies = get_recommendations()
        render_movie_cards(movies, api_key_input)

        st.divider()
        if st.button("Load More Recommendations ➕"):
            st.info("Fetching next 5 recommendations from cluster...")



elif page == "📋 Questionnaire":
    col1, col2, col3 = st.columns([9, 25, 5])
    with col2:
        st.title("👩🏽‍💻 MOVIE QUESTIONNAIRE")

    user_type = st.radio("Choose User Type: ", ["1. Existing User", "2. New User"], horizontal=True)
    st.divider()

    if user_type == "1. Existing User":
        st.caption("You are an existing user and want a random movie choice")
        st.subheader("Are you in the mood for something aside your recommendation?")
        answer = st.radio("Choose Answer: ", ["Yes", "No"], horizontal=True)

        if answer == "Yes":
            st.subheader("What are you in the mood for now?")
            st.info("**Select 3 genres to get recommendations**")

            c1, c2, c3 = st.columns(3)
            with c1:
                g1 = st.selectbox("Genre 1", options=GENRES, index=None)
            with c2:
                g2_options = [g for g in GENRES if g != g1]
                g2 = st.selectbox("Genre 2", options=g2_options, index=None)
            with c3:
                g3_options = [g for g in GENRES if g not in [g1, g2]]
                g3 = st.selectbox("Genre 3", options=g3_options, index=None)

            user_selected = [g for g in [g1, g2, g3] if g is not None]
            selected_count = len(user_selected)

            if selected_count == 3:
                st.success(f"***Selected (3/3): {', '.join(user_selected)}***")
            elif selected_count > 0:
                st.info(f"***Selected ({selected_count}/3): {', '.join(user_selected)}***")
            else:
                st.info("***You have nothing selected currently***")

            st.write("")
            find_movies = st.button("**Find Movies**", type="primary", disabled=selected_count < 3)

            if find_movies:
                st.subheader(f"Top Picks for: {', '.join(user_selected)}")
                movies = get_recommendations(genre_filter=user_selected)
                render_movie_cards(movies, api_key_input)
            else:
                st.subheader("Choose three genres to get recommendations")

    else:  # New User
        st.subheader("Tell us a bit about yourself")
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("Age", min_value=13, max_value=100, value=25)
        with c2:
            gender = st.selectbox("Gender", ["M", "F"])
        with c3:
            occupation = st.selectbox("Occupation", [
                'administrator', 'artist', 'doctor', 'educator', 'engineer',
                'entertainment', 'executive', 'healthcare', 'homemaker', 'lawyer',
                'librarian', 'marketing', 'none', 'other', 'programmer', 'retired',
                'salesman', 'scientist', 'student', 'technician', 'writer'
            ])

        st.write("")
        st.info("**Pick 3 favorite genres to seed your first recommendations**")
        c1, c2, c3 = st.columns(3)
        with c1:
            ng1 = st.selectbox("Favorite Genre 1", options=GENRES, index=None, key="ng1")
        with c2:
            ng2_options = [g for g in GENRES if g != ng1]
            ng2 = st.selectbox("Favorite Genre 2", options=ng2_options, index=None, key="ng2")
        with c3:
            ng3_options = [g for g in GENRES if g not in [ng1, ng2]]
            ng3 = st.selectbox("Favorite Genre 3", options=ng3_options, index=None, key="ng3")

        new_user_genres = [g for g in [ng1, ng2, ng3] if g is not None]

        if st.button("Create Profile & Get Recommendations", type="primary",
                      disabled=len(new_user_genres) < 3):
            st.success(f"Profile created — Age {age}, {gender}, {occupation}")
            st.caption("(Not yet saved to a database — hook this up once SQLite storage is added.)")
            st.subheader(f"Starter Picks for: {', '.join(new_user_genres)}")
            movies = get_recommendations(genre_filter=new_user_genres)
            render_movie_cards(movies, api_key_input)