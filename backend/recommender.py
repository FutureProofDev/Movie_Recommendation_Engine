"""
recommender.py

Interface module for the Movie Recommendation Engine's ML backend.
Wraps the trained K-Means clustering model and Random Forest rating
predictor behind simple functions, so the frontend (Streamlit) doesn't
need to know anything about feature engineering, encoding, or model internals.

Usage (from Streamlit or anywhere else):

    from recommender import predict_rating, get_user_cluster

    rating = predict_rating(age=25, gender="M", occupation="student",
                             genres={"Action": 1, "Comedy": 0, ...})

    cluster = get_user_cluster(age=25, gender="M", occupation="student",
                                genre_avg_ratings={"Action": 4.2, "Comedy": 3.1, ...})
"""

import joblib
import pandas as pd
import os

# Load models once

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")



rf_model = joblib.load(os.path.join(MODEL_DIR, "random_forest_model.pkl"))
kmeans_model = joblib.load(os.path.join(MODEL_DIR, "kmeans_model.pkl"))
scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
rf_feature_columns = joblib.load(os.path.join(MODEL_DIR, "feature_columns.pkl"))
cluster_feature_columns = joblib.load(os.path.join(MODEL_DIR, "combined_features_v2.pkl"))

GENRE_COLS = ['unknown', 'Action', 'Adventure', 'Animation', "Children's", 'Comedy',
              'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror',
              'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']

OCCUPATIONS = ['administrator', 'artist', 'doctor', 'educator', 'engineer',
               'entertainment', 'executive', 'healthcare', 'homemaker', 'lawyer',
               'librarian', 'marketing', 'none', 'other', 'programmer', 'retired',
               'salesman', 'scientist', 'student', 'technician', 'writer']


# Internal helpers

def _build_user_row(age, gender, occupation, genre_values, expected_columns):
    """
    Builds a single-row DataFrame matching the exact column structure the
    model was trained on (same one-hot encoding, same column order).
    genre_values: dict mapping genre name -> numeric value (rating or flag)
    """
    row = {"age": age}

    # Fill genre columns (default 0 for any not provided)
    for genre in GENRE_COLS:
        row[genre] = genre_values.get(genre, 0)

    # One-hot encode gender 
    row["gender_M"] = 1 if str(gender).upper() == "M" else 0

    # One-hot encode occupation 
    for occ in OCCUPATIONS:
        col_name = f"occupation_{occ}"
        if col_name in expected_columns:
            row[col_name] = 1 if occupation == occ else 0

    df = pd.DataFrame([row])

    # Ensuring all the columns the model expects are present.
    for col in expected_columns:
        if col not in df.columns:
            df[col] = 0
    df = df[expected_columns]

    return df


# Public functions: these are what the frontend should call

def predict_rating(age, gender, occupation, genre_flags):
    """
    Predicts what rating a user would give a movie.

    Parameters
    ----------
    age : int
    gender : str, "M" or "F"
    occupation : str, one of OCCUPATIONS
    genre_flags : dict, e.g. {"Action": 1, "Comedy": 0, "Drama": 1, ...}
                  1 if the movie belongs to that genre, 0 otherwise.
                  Any genre not included defaults to 0.

    Returns
    -------
    float : predicted rating (roughly 1-5 scale)
    """
    user_row = _build_user_row(age, gender, occupation, genre_flags, rf_feature_columns)
    prediction = rf_model.predict(user_row)[0]
    return round(float(prediction), 2)


def get_user_cluster(age, gender, occupation, genre_avg_ratings):
    """
    Assigns a user to one of the K-Means taste clusters.

    Parameters
    ----------
    age : int
    gender : str, "M" or "F"
    occupation : str, one of OCCUPATIONS
    genre_avg_ratings : dict, e.g. {"Action": 4.2, "Comedy": 3.1, ...}
                        the user's average rating given to each genre.
                        Any genre not included defaults to 0.

    Returns
    -------
    int : cluster ID (0 to 5)
    """
    user_row = _build_user_row(age, gender, occupation, genre_avg_ratings, cluster_feature_columns)
    scaled_row = scaler.transform(user_row)
    cluster_id = kmeans_model.predict(scaled_row)[0]
    return int(cluster_id)


def get_model_info():
    """Quick sanity-check function Lisa can call to confirm models loaded correctly."""
    return {
        "rf_features": len(rf_feature_columns),
        "cluster_features": len(cluster_feature_columns),
        "n_clusters": kmeans_model.n_clusters,
    }
