import streamlit as st
import pandas as pd


col1, col2, col3 = st.columns([9,25,5])

with col2:
    st.title("🎬 MOVIE RECOMMENDATION ENGINE")
    st.caption("Personalized picks based on your AI cluster & current mood")

current_user = st.session_state.get("user_id", 1)
st.subheader(f"Welcome back, User #{current_user}!")

tab1= st.tabs(["Top Recommendations For You"])

with tab1[0]:

    #ai generated
    mock_movies = pd.DataFrame({
        'Title': ['Star Wars (1977)', 'Godfather, The (1972)', 'Raiders of the Lost Ark (1981)', 'Pulp Fiction (1994)',
                  'Silence of the Lambs (1991)'],
        'Genre': ['Sci-Fi', 'Crime', 'Action', 'Crime', 'Drama'],
        'Predicted Rating': [4.9, 4.8, 4.7, 4.6, 4.5]
    })

    st.dataframe(mock_movies, use_container_width=True, hide_index=True)

    # Pagination / Load More Button
    if st.button("Load More Recommendations ➕"):
        st.info("Fetching next 5 recommendations from cluster...")




