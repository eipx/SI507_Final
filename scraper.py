import requests

API_KEY = 'puXFYbBBVMXJHiOuNgagxmMSAerdxrEgULowjouj'
API_URL = 'https://api.discogs.com/database/search'

def scrape_genres():
    headers = {
        'Authorization': f'Discogs token={API_KEY}',
        'User-Agent': 'MusicRecApp/0.1'
    }
    
    # Get the list of genres from the Discogs API
    response = requests.get(API_URL, headers=headers, params={'type': 'genre'})
    genres = response.json().get('results', [])

    genre_data = []

    for genre in genres:
        genre_info = {
            'name': genre.get('title'),
            'artists': [],
            'albums': [],
            'sub_genres': [],
        }

        # Get top 5 artists for each genre
        response = requests.get(API_URL, headers=headers, params={'type': 'artist', 'genre': genre_info['name']})
        artists = response.json().get('results', [])[:5]
        genre_info['artists'] = [artist.get('title') for artist in artists]

        # Get top 5 albums for each genre
        response = requests.get(API_URL, headers=headers, params={'type': 'release', 'genre': genre_info['name']})
        albums = response.json().get('results', [])[:5]
        genre_info['albums'] = [album.get('title') for album in albums]

        # Get sub-genres
        response = requests.get(API_URL, headers=headers, params={'type': 'style', 'genre': genre_info['name']})
        sub_genres = response.json().get('results', [])
        genre_info['sub_genres'] = [sub_genre.get('title') for sub_genre in sub_genres]

        genre_data.append(genre_info)

    return genre_data
