# Music Recommendation System

This is a music recommendation system built using Flask and Last.fm API. The system allows users to register, log in, add songs, and get personalized music recommendations based on the tags of the songs they've added.

## Requirements

- Python 3.x
- Flask
- Requests
- The credentials for my project are uploaded to canvas separately.
  so they are not available on GitHub.

## Installation

1. Install the required packages:

```bash
pip install Flask requests
```
2. Usage

Start the Flask app:

```bash
python app.py
```
Open your browser and navigate to http://127.0.0.1:5000/.

Register an account and log in.

Add songs to your library by entering the song title and artist name.

Get personalized music recommendations based on the tags of the songs you've added.

We employ a graph-based approach to organize and provide music recommendations. The graph is composed of tags (genres) as nodes, with edges representing relationships between them. When a user inputs a song, we initially request more tag information from the last.fm API for that specific song. We then add an edge count of 1 between the tags in the song. The default size of the tag data is not substantial (limited to 50 at most), and we use the LRU ideology to remove tags that are not frequently used.