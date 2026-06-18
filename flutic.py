from flask import Flask, render_template, request, redirect, flash
from database.database import create_tables, get_songs, get_song, add_song, search_songs, get_total_songs
import os

app = Flask(__name__)

app.secret_key = "tunexa_secret_key"

create_tables()


@app.route("/")
def home():
    songs = get_songs()
    return render_template("home.html", songs=songs)


@app.route("/search")
def search():

    keyword = request.args.get("q", "")

    if keyword:
        songs = search_songs(keyword)
    else:
        songs = []

    return render_template(
        "search.html",
        songs=songs,
        keyword=keyword
    )


@app.route("/library")
def library():
    return render_template("library.html")


@app.route("/song/<int:song_id>")
def song(song_id):

    song = get_song(song_id)

    return render_template(
        "song.html",
        song=song
    )


@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":

        title = request.form["title"]
        artist = request.form["artist"]

        cover = request.files["cover"]
        song = request.files["song"]

        cover_filename = ""
        song_filename = ""

        os.makedirs("static/uploads/covers", exist_ok=True)
        os.makedirs("static/uploads/songs", exist_ok=True)

        if cover and cover.filename:
            cover_filename = cover.filename
            cover.save(os.path.join("static/uploads/covers", cover_filename))

        if song and song.filename:
            song_filename = song.filename
            song.save(os.path.join("static/uploads/songs", song_filename))

        add_song(title, artist, cover_filename, song_filename)
        
        flash("Song uploaded successfully!")

    return redirect("/upload")

    return render_template("upload.html")


@app.route("/admin")
def admin():
    songs = get_songs()
    total_songs = get_total_songs()

    return render_template(
        "admin.html",
        songs=songs,
        total_songs=total_songs
    )


if __name__ == "__main__":
    app.run(debug=True)