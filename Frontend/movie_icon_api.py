import requests

TMDB_API_KEY = "your_key_here"  

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