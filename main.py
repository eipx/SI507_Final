from flask import Flask, render_template, request
from flask_caching import Cache
from scraper import scrape_genres
from graph import create_genre_graph, recommend_genres

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/')
def index():
    genre_data = scrape_genres()
    return render_template('index.html', genre_data=genre_data) # Create an 'index.html' template in a 'templates' folder

@app.route('/recommend', methods=['POST'])
def recommend():
    user_genres = request.form.getlist('genres')
    genre_graph = cache.get('genre_graph')
    if genre_graph is None:
        genres = scrape_genres()
        genre_graph = create_genre_graph(genres)
        cache.set('genre_graph', genre_graph)
    recommendations = recommend_genres(user_genres, genre_graph)
    return render_template('recommendations.html', recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
