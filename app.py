import streamlit as st
import pickle
import pandas as pd
import requests
import os

# Function to download the similarity.pkl file dynamically
def download_similarity_file():
    file_url = "https://drive.google.com/uc?id=1KwOkNv0m6dtHulj-_dz_iOqZL0zu13ZC"
    file_name = "similarity.pkl"
    if not os.path.exists(file_name):
        with st.spinner("Downloading similarity data..."):
            response = requests.get(file_url)
            with open(file_name, "wb") as f:
                f.write(response.content)

# Download the file if not present
download_similarity_file()

# Load data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# Custom CSS for scaled-down pop-up effect
st.markdown(
    """
    <style>
    .main {
        background: #181818;
        padding: 2rem;
    }
    .movie-card {
        border: 1px solid #333;
        border-radius: 15px;
        background-color: #ffffff;
        margin: 10px;
        padding: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        height: 350px;
        width: 150px;
        overflow: hidden;
        position: relative;
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .movie-card img {
        width: 100%;
        height: 75%;
        object-fit: cover;
        border-radius: 10px;
    }
    .movie-title {
        font-size: 14px;
        font-weight: bold;
        margin-top: 10px;
        text-align: center;
        color: #000000;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .popup {
        display: none;
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 1000;
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
    }
    .popup img {
        width: 300px;
        height: auto;
        object-fit: cover;
        border-radius: 10px;
    }
    .popup .close-btn {
        margin-top: 10px;
        padding: 10px 20px;
        background-color: #f44336;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .popup:target {
        display: block;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title('🍿 Movie Recommender System')
st.markdown("### Get tailored movie recommendations based on your favorites! 🎬")

selected_movie_name = st.selectbox(
    'Select a movie to get recommendations:',
    movies['title'].values
)


# Function to fetch poster from TMDB API
def fetch_poster(movie_id):
    response = requests.get(
        "https://api.themoviedb.org/3/movie/{}?api_key=6d55c4781af5599db440d30d82ee47f0".format(movie_id))
    data = response.json()
    if 'poster_path' in data and data['poster_path']:
        return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    return "https://via.placeholder.com/500x750?text=No+Image+Available"


# Recommendation logic
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = i[0]
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movies.iloc[i[0]].movie_id))

    return recommended_movies, recommended_movies_posters


if st.button('Get Recommendations', key='recommend-btn', help="Click to get movie recommendations"):
    names, posters = recommend(selected_movie_name)

    # Display movie recommendations in styled columns with horizontal padding
    cols = st.columns(5, gap="large")
    for i, col in enumerate(cols):
        with col:
            st.markdown(
                f"""
                <div class="movie-card">
                    <img src="{posters[i]}" alt="{names[i]}">
                    <p class="movie-title">{names[i]}</p>
                    <a href="#popup-{i}">
                        <button style="background-color: #6200ea; color: white; border: none; border-radius: 5px; cursor: pointer;">View</button>
                    </a>
                </div>
                <div id="popup-{i}" class="popup">
                    <img src="{posters[i]}" alt="{names[i]}">
                    <p style="font-size: 20px; font-weight: bold;">{names[i]}</p>
                    <a href="#">
                        <button class="close-btn">Close</button>
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )
