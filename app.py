from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import hashlib
from music_graph import MusicGraph, API_KEY
import pickle

app = Flask(__name__)
app.secret_key = 'super secret key'
DATA_FOLDER = "user_data"

def load_graph_data(username):
    graph_file = os.path.join(DATA_FOLDER, f"{username}_graph.json")
    if not os.path.exists(graph_file):
        return None
    with open(graph_file, 'r') as f:
        graph_data = json.load(f)
    return MusicGraph.from_dict(graph_data)

def save_graph_data(username, graph):
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    graph_file = os.path.join(DATA_FOLDER, f"{username}_graph.json")
    with open(graph_file, 'w') as f:
        json.dump(graph.to_dict(), f)

def load_user_data(username):
    with open(os.path.join(DATA_FOLDER, f"{username}.json"), "r") as f:
        return json.load(f)

def save_user_data(username, data):
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    with open(os.path.join(DATA_FOLDER, f"{username}.json"), "w") as f:
        json.dump(data, f)



@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    
    # Load the graph data from the session
    graph_data = session.get("graph")
    if not graph_data:
        graph = MusicGraph()
    else:
        graph = MusicGraph.from_dict(graph_data)

    tags = graph.get_tags()
    recommendations = []

    return render_template("index.html", tags=tags, recommendations=recommendations)



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if os.path.exists(os.path.join(DATA_FOLDER, f"{username}.json")):
            user_data = load_user_data(username)

            if user_data["password"] == hashed_password:
                session["username"] = username
                
                # Load the graph data and store it in the session
                graph = load_graph_data(username)
                if not graph:
                    graph = MusicGraph()
                session["graph"] = graph.to_dict()
                
                return redirect(url_for("index"))
            else:
                return "Incorrect password"
        else:
            return "User not found"

    return render_template("login.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if os.path.exists(os.path.join(DATA_FOLDER, f"{username}.json")):
            return "Username already exists"

        user_data = {"password": hashed_password}
        save_user_data(username, user_data)
        session["username"] = username
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    username = session.get("username")
    if username:
        # Save the graph data to a file before clearing the session
        graph_data = session.get("graph")
        if graph_data:
            graph = MusicGraph.from_dict(graph_data)
            save_graph_data(username, graph)
        session.pop("username", None)

    session.clear()
    return redirect(url_for("login"))



@app.route("/add_song", methods=["POST"])
def add_song():
    if "username" not in session:
        return redirect(url_for("login"))

    song_title = request.form["song"]
    artist_name = request.form["artist"]
    username = session["username"]

    # Load the graph data from the session
    graph_data = session.get("graph")
    if not graph_data:
        graph = MusicGraph()
    else:
        graph = MusicGraph.from_dict(graph_data)

    # Get the tags for the song
    tags = graph.get_tags_for_song(song_title, artist_name)

    # Update the graph with the new song's tags
    graph.update_graph(tags)

    # Save the updated graph to the session
    session["graph"] = graph.to_dict()

    return redirect(url_for("index"))


@app.route("/delete_tag", methods=["POST"])
def delete_tag():
    if "username" not in session:
        return redirect(url_for("login"))

    tag = request.form["tag"]
    username = session["username"]

    # Load the graph data from the session
    graph_data = session.get("graph")
    if not graph_data:
        graph = MusicGraph()
    else:
        graph = MusicGraph.from_dict(graph_data)

    graph.remove_tag(tag)

    # Save the updated graph to the session
    session["graph"] = graph.to_dict()

    return redirect(url_for("index"))


@app.route("/recommend", methods=["POST"])
def recommend():
    if "username" not in session:
        return redirect(url_for("login"))

    chosen_tag = request.form["chosen_tag"]
    username = session["username"]

    # Load the graph data from the session
    graph_data = session.get("graph")
    if not graph_data:
        graph = MusicGraph()
    else:
        graph = MusicGraph.from_dict(graph_data)

    recommendations = graph.recommendations(chosen_tag)

    tags = graph.get_tags()

    return render_template("index.html", tags=tags, recommendations=recommendations)


if __name__ == "__main__":
    app.run(debug=True)
