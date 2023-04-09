import requests
from collections import defaultdict

API_KEY = '0ccc3255b892733da52768a1acac1455'
API_URL = 'http://ws.audioscrobbler.com/2.0/'

class MusicGraph:
    def __init__(self, api_key):
        self.api_key = api_key
        self.graph = defaultdict(set)
        self.top_tracks_cache = {}
        self.max_tags_per_song = 5

    def add_tag(self, tag):
        if tag not in self.graph:
            self.graph[tag] = set()

    def remove_tag(self, tag):
        if tag in self.graph:
            del self.graph[tag]

    def add_edge(self, tag1, tag2):
        self.add_tag(tag1)
        self.add_tag(tag2)
        self.graph[tag1].add(tag2)
        self.graph[tag2].add(tag1)

    def get_related_tags(self, tag):
        return self.graph.get(tag, set())

    def get_top_tracks(self, tag):
        if tag in self.top_tracks_cache:
            return self.top_tracks_cache[tag]

        params = {
            "method": "tag.gettoptracks",
            "tag": tag,
            "api_key": self.api_key,
            "format": "json",
        }
        response = requests.get("http://ws.audioscrobbler.com/2.0/", params=params)
        data = response.json()

        if "error" in data:
            print(f"Error in API response: {data['message']}")
            return []

        if "tracks" not in data:
            print("No 'tracks' key in API response")
            return []

        top_tracks = [track["name"] for track in data["tracks"]["track"]]
        self.top_tracks_cache[tag] = top_tracks
        return top_tracks

    # Update the add_tags method to limit the number of tags per song
    def add_tags(self, tags):
        if len(tags) > self.max_tags_per_song:
            tags = tags[:self.max_tags_per_song]

        for tag in tags:
            self.add_tag(tag)

    def build_graph(self, tags):
        for tag1 in tags:
            top_tracks1 = self.get_top_tracks(tag1)
            for tag2 in tags:
                if tag1 != tag2:
                    top_tracks2 = self.get_top_tracks(tag2)
                    common_tracks = set(top_tracks1).intersection(set(top_tracks2))
                    if common_tracks:
                        self.add_edge(tag1, tag2)

    def get_tags_for_song(self, song, artist):
        params = {
            "method": "track.getTopTags",
            "track": song,
            "artist": artist,
            "api_key": self.api_key,
            "format": "json",
        }
        response = requests.get("http://ws.audioscrobbler.com/2.0/", params=params)
        data = response.json()
        return [tag["name"] for tag in data["toptags"]["tag"]]

    def calculate_jaccard_similarity(self, set1, set2):
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        return len(intersection) / len(union)

    def recommendations(self, user_tags, num_recommendations=5):
        user_tags = set(user_tags)
        tag_similarity = []

        for tag in self.graph:
            if tag not in user_tags:
                similarity = self.calculate_jaccard_similarity(user_tags, self.graph[tag])
                tag_similarity.append((tag, similarity))

        tag_similarity.sort(key=lambda x: x[1], reverse=True)
        recommended_tags = [tag for tag, _ in tag_similarity[:num_recommendations]]
        return recommended_tags