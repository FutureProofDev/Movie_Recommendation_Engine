import streamlit as st

col1, col2, col3 = st.columns([9,25,5])

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



