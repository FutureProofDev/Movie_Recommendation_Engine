<<<<<<< HEAD:AIFINAL/movie_icon_api.py
import os
=======
import streamlit as st
>>>>>>> 7991b5f466c519f0032bce605d8000ef61579984:frontend/movie_icon_api.py
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # reads variables from a local .env file into the environment

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

@st.cache_data(ttl=86400)
def get_movie_poster(title, year=None):
    resp = requests.get(
        "https://api.themoviedb.org/3/search/movie",
        params={"api_key": TMDB_API_KEY, "query": title, "year": year}
    )
    results = resp.json().get("results")
    if not results:
        return None, None
    movie = results[0]
    poster_url = f"https://image.tmdb.org/t/p/w342{movie['poster_path']}" if movie.get("poster_path") else None
    imdb_link = f"https://www.themoviedb.org/movie/{movie['id']}"
    return poster_url, imdb_link