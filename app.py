from flask import Flask, render_template, request, redirect, flash, session

from database.database import (
    create_tables, get_songs, get_song, add_song, search_songs,
    get_total_songs, delete_song, update_song, like_song,
    get_liked_songs, create_playlist, get_playlists, get_playlist,
    add_song_to_playlist, get_playlist_songs, remove_song_from_playlist,
    delete_playlist, get_playlist_song_count, get_total_views,
    get_total_likes, increase_song_view, increase_song_download,
    get_total_downloads, get_most_played_songs
)

import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "flunix_secret_key")

create_tables()

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "tunexa123")


def is_admin_logged_in():
    return session.get("admin_logged_in") == True


@app.context_processor
def inject_playlists():
    playlists = get_playlists()
    playlist_data = []

    for playlist in playlists:
        playlist_data.append({
            "id": playlist["id"],
            "name": playlist["name"],
            "cover_image": playlist["cover_image"],
            "count": get_playlist_song_count(playlist["id"])
        })

    return {"sidebar_playlists": playlist_data}


@app.route("/")
def home():
    songs = get_songs()
    return render_template("home.html", songs=songs)


@app.route("/search")
def search():
    keyword = request.args.get("q", "")
    songs = search_songs(keyword) if keyword else []
    return render_template("search.html", songs=songs, keyword=keyword)


@app.route("/category/<genre>")
def category(genre):
    songs = search_songs(genre)
    return render_template("category.html", songs=songs, genre=genre)


@app.route("/library")
def library():
    playlists = get_playlists()
    liked_songs = get_liked_songs()
    return render_template("library.html", playlists=playlists, liked_songs=liked_songs)


@app.route("/settings")
def settings():
    return render_template("settings.html")


@app.route("/favorites")
@app.route("/liked")
def liked():
    songs = get_liked_songs()
    return render_template("liked.html", songs=songs)


@app.route("/like/<int:song_id>")
def like(song_id):
    like_song(song_id)
    return redirect(request.referrer or "/")


@app.route("/track-view/<int:song_id>")
def track_view(song_id):
    increase_song_view(song_id)
    return {"success": True}


@app.route("/download/<int:song_id>")
def download_song(song_id):
    increase_song_download(song_id)
    song = get_song(song_id)
    return redirect("/static/uploads/songs/" + song["song_file"])


@app.route("/playlists", methods=["GET", "POST"])
def playlists():
    if request.method == "POST":
        name = request.form["name"]
        cover = request.files.get("cover")
        cover_filename = ""

        os.makedirs("static/uploads/playlists", exist_ok=True)

        if cover and cover.filename:
            cover_filename = cover.filename
            cover.save(os.path.join("static/uploads/playlists", cover_filename))

        create_playlist(name, cover_filename)
        flash("Playlist created successfully!")
        return redirect("/playlists")

    playlists = get_playlists()
    return render_template("playlists.html", playlists=playlists)


@app.route("/playlist/<int:playlist_id>")
def playlist_detail(playlist_id):
    playlist = get_playlist(playlist_id)
    songs = get_playlist_songs(playlist_id)
    all_songs = get_songs()

    return render_template(
        "playlist_detail.html",
        playlist=playlist,
        songs=songs,
        all_songs=all_songs
    )


@app.route("/playlist/<int:playlist_id>/add/<int:song_id>")
def add_to_playlist(playlist_id, song_id):
    add_song_to_playlist(playlist_id, song_id)
    flash("Song added to playlist!")
    return redirect(f"/playlist/{playlist_id}")


@app.route("/playlist/<int:playlist_id>/remove/<int:song_id>")
def remove_from_playlist(playlist_id, song_id):
    remove_song_from_playlist(playlist_id, song_id)
    flash("Song removed from playlist!")
    return redirect(f"/playlist/{playlist_id}")


@app.route("/playlist/delete/<int:playlist_id>")
def delete_playlist_route(playlist_id):
    delete_playlist(playlist_id)
    flash("Playlist deleted successfully!")
    return redirect("/playlists")


@app.route("/song/<int:song_id>")
def song(song_id):
    increase_song_view(song_id)
    song = get_song(song_id)
    playlists = get_playlists()

    return render_template(
        "song.html",
        song=song,
        playlists=playlists
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if is_admin_logged_in():
        return redirect("/admin")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            flash("Admin login successful!")
            return redirect("/admin")

        flash("Invalid username or password!")
        return redirect("/login")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect("/login")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if not is_admin_logged_in():
        flash("Please login as admin first.")
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        artist = request.form["artist"]
        album = request.form["album"]
        genre = request.form["genre"]

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

        add_song(title, artist, album, genre, cover_filename, song_filename)

        flash("Song uploaded successfully!")
        return redirect("/upload")

    return render_template("upload.html")


@app.route("/admin")
def admin():
    if not is_admin_logged_in():
        flash("Please login as admin first.")
        return redirect("/login")

    songs = get_songs()

    total_songs = get_total_songs()
    total_views = get_total_views()
    total_likes = get_total_likes()
    total_downloads = get_total_downloads()
    most_played_songs = get_most_played_songs()

    return render_template(
        "admin.html",
        songs=songs,
        total_songs=total_songs,
        total_views=total_views,
        total_likes=total_likes,
        total_downloads=total_downloads,
        most_played_songs=most_played_songs
    )


@app.route("/delete/<int:song_id>")
def delete(song_id):
    if not is_admin_logged_in():
        flash("Please login as admin first.")
        return redirect("/login")

    delete_song(song_id)
    flash("Song deleted successfully!")
    return redirect("/admin")


@app.route("/edit/<int:song_id>", methods=["GET", "POST"])
def edit(song_id):
    if not is_admin_logged_in():
        flash("Please login as admin first.")
        return redirect("/login")

    song = get_song(song_id)

    if request.method == "POST":
        title = request.form["title"]
        artist = request.form["artist"]
        album = request.form["album"]
        genre = request.form["genre"]

        cover = request.files.get("cover")
        audio = request.files.get("song")

        cover_filename = song["cover_image"]
        song_filename = song["song_file"]

        os.makedirs("static/uploads/covers", exist_ok=True)
        os.makedirs("static/uploads/songs", exist_ok=True)

        if cover and cover.filename:
            cover_filename = cover.filename
            cover.save(os.path.join("static/uploads/covers", cover_filename))

        if audio and audio.filename:
            song_filename = audio.filename
            audio.save(os.path.join("static/uploads/songs", song_filename))

        update_song(
            song_id,
            title,
            artist,
            album,
            genre,
            cover_filename,
            song_filename
        )

        flash("Song updated successfully!")
        return redirect("/admin")

    return render_template("edit.html", song=song)


if __name__ == "__main__":
    app.run(debug=True)