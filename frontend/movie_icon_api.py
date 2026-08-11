import re
import requests
import streamlit as st
from dotenv import load_dotenv

# Load TMDB API key from .env file
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]


def clean_movie_title(title):
    """
    Converts MovieLens titles into standard search queries.
    Example: "Godfather, The (1972)" -> "The Godfather", "1972"
    """
    year = None

    # Extracts 4-digit year at the end inside parentheses
    year_match = re.search(r"\s*\((\d{4})\)\s*$", title)
    if year_match:
        year = year_match.group(1)
        title = title[: year_match.start()].strip()

    # Remove any remaining parenthetical notes
    title = re.sub(r"\s*\([^)]*\)", "", title).strip()

    # Rearrange trailing articles at the end of the title (case-insensitive)
    # Supports English and common foreign articles: The, A, An, Les, La, Le, Das, Der, Die
    article_match = re.search(
        r",\s*(The|A|An|Les|La|Le|Das|Der|Die)\s*$", title, re.IGNORECASE
    )
    if article_match:
        article = article_match.group(1)
        main_title = title[: article_match.start()].strip()
        title = f"{article.capitalize()} {main_title}"

    return title, year  


@st.cache_data(ttl=86400, show_spinner = False)
def get_movie_poster(title, year=None):
    if not TMDB_API_KEY:
        print("Missing TMDB_API_KEY")
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

    poster_url = (
        f"https://image.tmdb.org/t/p/w342{poster_path}" if poster_path else None
    )
    tmdb_link = f"https://www.themoviedb.org/movie/{movie['id']}"

    return poster_url, tmdb_link
