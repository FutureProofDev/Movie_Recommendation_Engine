import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load TMDB API key from .env file
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def clean_movie_title(title):
    """
    Converts MovieLens titles into standard search queries.
    Example: "Godfather, The (1972)" -> "The Godfather", "1972"
    """
    year = None

    # 1. Extract the year from parentheses at the end: "(1972)"
    if "(" in title and title.endswith(")"):
        title, year_part = title.rsplit("(", 1)
        year = year_part.rstrip(")").strip()
        title = title.strip()

    # 2. Fix flipped titles: "Godfather, The" -> "The Godfather"
    if ", " in title:
        main_title, article = title.rsplit(", ", 1)
        if article.lower() in ["the", "a", "an"]:
            title = f"{article} {main_title}"

    return title, year


@st.cache_data(ttl=86400)
def get_movie_poster(title, year=None):
    if not TMDB_API_KEY:
        print("Missing TMDB_API_KEY in your .env file.")
        return None, None

    # Clean title and extract year
    clean_name, extracted_year = clean_movie_title(title)
    search_year = year or extracted_year

    # Search TMDB API
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": clean_name, "year": search_year}
    
    results = requests.get(url, params=params).json().get("results", [])

    # If no results with year, retry searching with title only
    if not results and search_year:
        params.pop("year")
        results = requests.get(url, params=params).json().get("results", [])

    # If still no movie found, return empty
    if not results:
        return None, None

    # Build poster image and movie links
    movie = results[0]
    poster_path = movie.get("poster_path")
    
    poster_url = f"https://image.tmdb.org/t/p/w342{poster_path}" if poster_path else None
    tmdb_link = f"https://www.themoviedb.org/movie/{movie['id']}"

    return poster_url, tmdb_link