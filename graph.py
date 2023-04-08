import networkx as nx

def create_genre_graph(genre_data):
    G = nx.Graph()

    # Add nodes to the graph
    for genre in genre_data:
        G.add_node(genre['name'])

    # Add edges between genres based on shared sub-genres
    for i in range(len(genre_data)):
        for j in range(i + 1, len(genre_data)):
            genre1 = genre_data[i]
            genre2 = genre_data[j]
            shared_sub_genres = set(genre1['sub_genres']).intersection(set(genre2['sub_genres']))

            if shared_sub_genres:
                G.add_edge(genre1['name'], genre2['name'], weight=len(shared_sub_genres))

    return G

def recommend_genres(user_genres, genre_graph):
    recommendations = []
    for genre in user_genres:
        similar_genres = [n for n in genre_graph.neighbors(genre)]
        recommendations.extend(similar_genres)
    return list(set(recommendations) - set(user_genres))
