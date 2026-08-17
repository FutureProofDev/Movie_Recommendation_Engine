## Setup Instructions

These steps let anyone clone this repository and run the application locally
to see how it works, end to end — from the trained ML models to the live
recommendation interface.

### 1. Clone the repository

git clone <your-repo-url>
cd Movie_Recommendation_Engine

### 2. Create and activate a virtual environment

python3 -m venv venv

# Mac/Linux

source venv/bin/activate

# Windows (PowerShell)

venv\Scripts\Activate.ps1

### 3. Install dependencies

pip install -r requirements.txt

### 4. Explore the data pipeline (optional)

The dataset (MovieLens 100K) is already included under data/ml-100k/ — no
download needed. To see how the data was explored, cleaned, and turned into
model-ready features, open the notebooks in order:

1. backend/notebooks/01_data_exploration.ipynb   — data loading, cleaning, stats
2. backend/notebooks/02_feature_engineering.ipynb — clustering model + feature design
3. backend/notebooks/03_regression_model.ipynb    — rating-prediction model + evaluation

These notebooks are meant to be read, not just run — each one documents the
reasoning behind key design decisions (e.g. why clustering features were
changed partway through, why certain columns were dropped).

You don't need to re-run these to use the app — trained models are already
saved under backend/models/.

### 5. Understand the backend interface

backend/recommender.py is the single entry point the frontend uses to get
predictions. It exposes three functions:

- predict_rating(age, gender, occupation, genre_flags)
- get_user_cluster(age, gender, occupation, genre_avg_ratings)
- get_model_info()

To confirm it works correctly on your machine, run:

python "testing recommender.py"

This loads the saved models and prints a sample prediction and cluster
assignment — a quick way to verify everything is wired up correctly before
looking at the app itself.

### 6. Set up a TMDB API key (only needed to see movie posters)

Create a file at frontend/.streamlit/secrets.toml with:

TMDB_API_KEY = "your_tmdb_api_key_here"

Get a free key at <https://www.themoviedb.org/> under Settings > API.
The app works without this — you'll still see titles and predicted ratings,
just without poster images.

### 7. Run the app

cd frontend
streamlit run homepage.py

The app opens in your browser automatically (usually <http://localhost:8501>).
Enter your age, gender, and occupation, pick three genres (or hit
"Surprise me!"), and the app will rank movies using the trained models.

### Where everything lives

Movie_Recommendation_Engine/
├── backend/
│   ├── notebooks/          # the ML pipeline, in order — start here to understand the "how"

│   ├── models/              # pre-trained model files (loaded automatically, no retraining needed)

│   └── recommender.py       # the interface between the models and the app

├── frontend/

│   ├── homepage.py          # the Streamlit app itself

│   └── movie_icon_api.py    # fetches movie posters from TMDB

├── data/ml-100k/            # the MovieLens dataset, included directly in the repo

├── testing recommender.py   # a standalone script to verify the backend works

└── requirements.txt

### Project Done By ツ゚:

- [Lisa Baer](https://github.com/lisadbaer)
- [Natalie-Rose Andzie-Mensah](https://github.com/natalierose-am)
- [Vladimir Noel Aduama](https://github.com/FutureProofDev)
- [Nii Sowah Kwabla Sowah](https://github.com/Nii-Sowah)
