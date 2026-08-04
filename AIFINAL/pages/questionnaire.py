import streamlit as st
import random

col1, col2, col3 = st.columns([9,25,5])

with col2:
    st.title("👩🏽‍💻 MOVIE QUESTIONNAIRE")

user_type = st.radio("Choose User Type: ", ["1. New User", "2. Existing User"], horizontal=True)

st.divider()

if user_type == "1. New User":
    st.caption("You are a new user and need to set up your preference profile")


    st.subheader("What are your top 3 genres?")
    genres = [
        'unknown', 'Action', 'Adventure', 'Animation', "Children's", 'Comedy',
        'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror',
        'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
    ]

    st.info("**Select 3 genres to get recommendations**")

    col1, col2, col3 = st.columns(3)

    with col1:
        g1 = st.selectbox("Genre 1", options=genres, index=None)

    with col2:

        g2_options = [g for g in genres if g != g1]
        g2 = st.selectbox("Genre 2", options=g2_options, index=None)

    with col3:

        g3_options = [g for g in genres if g not in [g1, g2]]
        g3 = st.selectbox("Genre 3", options=g3_options, index=None)

        st.space(300)

    # Gather selected genres
    user_selected = [g for g in [g1, g2, g3] if g is not None]

    selected_count = len(user_selected)

    # Dynamic feedback box
    if selected_count == 3:
        st.success(
            f"***Selected (3/3): {', '.join(user_selected)}***"
        )
    elif selected_count > 0:
        st.info(
            f"***Selected ({selected_count}/3): {', '.join(user_selected)}***"
        )
    else:
        st.info("***You have nothing selected currently***")

    st.write("")

    # Disable the button until all three genres are selected
    find_movies = st.button(
            "**Find Movies**",
        type="primary",
        disabled=selected_count < 3
    )

    if find_movies:
        st.subheader(
            f"Top Picks for: {', '.join(user_selected)}")


    else:
        st.subheader("Choose three genres to get recommendations")



if user_type == "2. Existing User":
    st.caption("You are an existing user and will receive your recommendations")


    st.title("🎭 Today's Vibe Questionnaire")
    st.write(
        "Not feeling your usual recommendations? Tell us what you're in the mood for right now, and we'll generate a custom one-time list just for today.")

    # Official MovieLens genres
    genres = [
        'unknown', 'Action', 'Adventure', 'Animation', "Children's", 'Comedy',
        'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror',
        'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
    ]

    # Initialize session state for the dropdowns
    if "vibe_g1" not in st.session_state:
        st.session_state.vibe_g1 = None
    if "vibe_g2" not in st.session_state:
        st.session_state.vibe_g2 = None
    if "vibe_g3" not in st.session_state:
        st.session_state.vibe_g3 = None

    # Randomizer Button
    if st.button("🎲 I don't know, surprise me!", type="secondary"):
        random_picks = random.sample(genres, 3)
        st.session_state.vibe_g1 = random_picks[0]
        st.session_state.vibe_g2 = random_picks[1]
        st.session_state.vibe_g3 = random_picks[2]
        st.rerun()  # Refresh to show the new random choices

    st.divider()

    # ---------------------------------------------------------------------
    # THE VIBE QUESTIONNAIRE UI
    # ---------------------------------------------------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        idx1 = genres.index(st.session_state.vibe_g1) if st.session_state.vibe_g1 in genres else None
        # Framing as a question!
        g1 = st.selectbox("1. What's the main vibe you want?", options=genres, index=idx1, key="vibe_g1")

    with col2:
        g2_options = [g for g in genres if g != g1]
        idx2 = g2_options.index(st.session_state.vibe_g2) if st.session_state.vibe_g2 in g2_options else None
        # Framing as a question!
        g2 = st.selectbox("2. What else should be in the mix?", options=g2_options, index=idx2, key="vibe_g2")

    with col3:
        g3_options = [g for g in genres if g not in [g1, g2]]
        idx3 = g3_options.index(st.session_state.vibe_g3) if st.session_state.vibe_g3 in g3_options else None
        # Framing as a question!
        g3 = st.selectbox("3. Any final flavor to add?", options=g3_options, index=idx3, key="vibe_g3")

    user_selected = [g for g in [g1, g2, g3] if g is not None]
    selected_count = len(user_selected)

    st.write("")

    # Single action button - NO saving to profile!
    find_movies = st.button("**Generate Session Recommendations**", type="primary", disabled=selected_count < 3)

    if find_movies:
        st.success(f"Finding the best {', '.join(user_selected)} movies for you right now...")

        # -----------------------------------------------------------------
        # BACKEND CALL GOES HERE
        # We just pass `user_selected` to the K-Means function.
        # Because we don't save it to a database, it's strictly temporary!
        # -----------------------------------------------------------------

        st.subheader("🍿 Your Custom Picks for Today:")
        # st.dataframe(your_generated_recommendations_here)

