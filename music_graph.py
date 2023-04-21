import requests
from credentials import *
from collections import defaultdict

class MusicGraph:
    def __init__(self, max_tags_per_song=5, max_tags_total=20):
        self.api_key = API_KEY
        self.graph = defaultdict(dict)
        self.max_tags_per_song = max_tags_per_song
        self.max_tags_total = max_tags_total
        self.latest_songs = []
    
    #Serizalize the graph
    def to_dict(self):
        return {
            'graph': {k: dict(v) for k, v in self.graph.items()},
            'max_tags_per_song': self.max_tags_per_song,
            'max_tags_total': self.max_tags_total,
            "latest_songs": self.latest_songs
        }

    @classmethod
    def from_dict(cls, data):
        graph_obj = cls(
            max_tags_per_song=data['max_tags_per_song'],
            max_tags_total=data['max_tags_total']
        )
        graph_obj.graph = {k: dict(v) for k, v in data['graph'].items()}
        graph_obj.latest_songs = data.get("latest_songs", [])
        return graph_obj
    
    def add_tag(self, tag):
        if tag not in self.graph:
            if len(self.graph) == self.max_tags_total:
                self.remove_tag(next(iter(self.graph)))
            self.graph[tag] = {}

    def remove_tag(self, tag):
        for other_tag in self.graph:
            if tag in self.graph[other_tag]:
                del self.graph[other_tag][tag]
        if tag in self.graph:
            del self.graph[tag]

    def add_edge(self, tag1, tag2, shared_songs):
        self.add_tag(tag1)
        self.add_tag(tag2)
        self.graph[tag1][tag2] = shared_songs
        self.graph[tag2][tag1] = shared_songs

    def get_tags(self):
        return list(self.graph.keys())

    def update_graph(self, new_tags):
        # Add new tags and remove the oldest tags if the limit is reached
        for tag in new_tags:
            self.add_tag(tag)

        # Update edges for the new tags
        for tag1 in new_tags:
            for tag2 in new_tags:
                if tag1 != tag2:
                    if tag2 in self.graph[tag1]:
                        self.graph[tag1][tag2] += 1
                        self.graph[tag2][tag1] += 1
                    else:
                        self.add_edge(tag1, tag2, 1)

    def get_top_track_for_tag(self, tag):
        url = f'http://ws.audioscrobbler.com/2.0/?method=tag.gettoptracks&tag={tag}&api_key={API_KEY}&format=json'
        response = requests.get(url)
        data = response.json()

        if 'tracks' in data and 'track' in data['tracks'] and len(data['tracks']['track']) > 0:
            top_track = data['tracks']['track'][0]
            return f"{top_track['name']} by {top_track['artist']['name']}"
        else:
            return None
        
    def get_latest_songs(self):
        return self.latest_songs
            
    def get_tags_for_song(self, song, artist):
        self.latest_songs.append((song, artist))
        if len(self.latest_songs) > 5:
            self.latest_songs.pop(0)

        print("Currently getting tags for song")
        params = {
            "method": "track.getTopTags",
            "track": song,
            "artist": artist,
            "api_key": self.api_key,
            "format": "json",
        }
        response = requests.get("http://ws.audioscrobbler.com/2.0/", params=params)
        data = response.json()
        return [tag["name"] for tag in data["toptags"]["tag"]][:self.max_tags_per_song]

    def dijkstra(self, start_tag):
        unvisited = {tag: float('inf') for tag in self.graph}
        unvisited[start_tag] = 0
        visited = {}

        while unvisited:
            current_min_tag = min(unvisited, key=unvisited.get)
            visited[current_min_tag] = unvisited[current_min_tag]
            del unvisited[current_min_tag]

            for neighbor, count in self.graph[current_min_tag].items():
                if neighbor in visited:
                    continue

                new_distance = visited[current_min_tag] + (1 / count)
                if new_distance < unvisited[neighbor]:
                    unvisited[neighbor] = new_distance

        return visited

    def recommendations(self, chosen_tag, num_recommendations=5):
        distances = self.dijkstra(chosen_tag)

        sorted_distances = sorted(distances.items(), key=lambda x: x[1])
        recommended_tags = [tag for tag, _ in sorted_distances[:num_recommendations]]
        result_songs = []
        for tag in recommended_tags:
            result_songs.append(self.get_top_track_for_tag(tag))
        return result_songs, recommended_tags