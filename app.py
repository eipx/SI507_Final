from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import hashlib
from music_graph import MusicGraph, API_KEY

app = Flask(__name__)
app.secret_key = 'super secret key'
DATA_FOLDER = "user_data"

def load_user_data(username):
    with open(os.path.join(DATA_FOLDER, f"{username}.json"), "r") as f:
        return json.load(f)


def save_user_data(username, data):
    with open(os.path.join(DATA_FOLDER, f"{username}.json"), "w") as f:
        json.dump(data, f)


@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user_data = load_user_data(username)
    tags = user_data["tags"]
    recommendations = []

    if tags:
        graph = MusicGraph(API_KEY)
        graph.build_graph(tags)
        recommendations = graph.recommendations(tags)
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

        user_data = {"password": hashed_password, "tags": []}
        save_user_data(username, user_data)
        session["username"] = username
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/add_song", methods=["POST"])
def add_song():
    if "username" not in session:
        return redirect(url_for("login"))

    song_title = request.form["song_title"]
    artist_name = request.form["artist_name"]
    username = session["username"]
    user_data = load_user_data(username)

    # Get the tags for the song
    music_graph = MusicGraph(api_key)
    tags = music_graph.get_tags_for_song(song_title, artist_name)

    # Add the tags to the user's data
    for tag in tags:
        if tag not in user_data["tags"]:
            user_data["tags"].append(tag)
    save_user_data(username, user_data)

    return redirect(url_for("index"))



@app.route("/delete_tag", methods=["POST"])
def delete_tag():
    if "username" not in session:
        return redirect(url_for("login"))

    tag = request.form["tag"]
    username = session["username"]
    user_data = load_user_data(username)

    if tag in user_data["tags"]:
        user_data["tags"].remove(tag)
        save_user_data(username, user_data)

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
