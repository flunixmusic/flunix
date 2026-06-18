import sqlite3

DATABASE_NAME = "database/tunexa.db"


def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        artist TEXT NOT NULL,
        album TEXT,
        genre TEXT,
        cover_image TEXT,
        song_file TEXT,
        views INTEGER DEFAULT 0,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS artists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        image TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS albums (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        artist TEXT,
        cover_image TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS liked_songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        song_id INTEGER UNIQUE,
        FOREIGN KEY(song_id) REFERENCES songs(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        cover_image TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlist_songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_id INTEGER,
        song_id INTEGER,
        FOREIGN KEY(playlist_id) REFERENCES playlists(id),
        FOREIGN KEY(song_id) REFERENCES songs(id)
    )
    """)

    try:
        cursor.execute("ALTER TABLE playlists ADD COLUMN cover_image TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE songs ADD COLUMN views INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    
    try:
         cursor.execute("ALTER TABLE songs ADD COLUMN downloads INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


def get_songs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM songs ORDER BY id DESC")
    songs = cursor.fetchall()
    conn.close()
    return songs


def add_song(title, artist, album, genre, cover_image, song_file):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO songs
        (title, artist, album, genre, cover_image, song_file, views)
        VALUES (?, ?, ?, ?, ?, ?, 0)
    """, (title, artist, album, genre, cover_image, song_file))

    conn.commit()
    conn.close()


def get_song(song_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
    song = cursor.fetchone()
    conn.close()
    return song


def search_songs(keyword):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM songs
        WHERE title LIKE ?
        OR artist LIKE ?
        OR album LIKE ?
        OR genre LIKE ?
    """, (
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    songs = cursor.fetchall()
    conn.close()
    return songs


def get_total_songs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM songs")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def delete_song(song_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM liked_songs WHERE song_id = ?", (song_id,))
    cursor.execute("DELETE FROM playlist_songs WHERE song_id = ?", (song_id,))
    cursor.execute("DELETE FROM songs WHERE id = ?", (song_id,))
    conn.commit()
    conn.close()


def update_song(
    song_id,
    title,
    artist,
    album,
    genre,
    cover_image,
    song_file
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE songs
        SET
            title = ?,
            artist = ?,
            album = ?,
            genre = ?,
            cover_image = ?,
            song_file = ?
        WHERE id = ?
    """, (
        title,
        artist,
        album,
        genre,
        cover_image,
        song_file,
        song_id
    ))

    conn.commit()
    conn.close()


def like_song(song_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM liked_songs WHERE song_id = ?", (song_id,))
    liked = cursor.fetchone()

    if liked:
        cursor.execute("DELETE FROM liked_songs WHERE song_id = ?", (song_id,))
    else:
        cursor.execute("INSERT INTO liked_songs (song_id) VALUES (?)", (song_id,))

    conn.commit()
    conn.close()


def get_liked_songs():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT songs.* FROM songs
        JOIN liked_songs ON songs.id = liked_songs.song_id
        ORDER BY liked_songs.id DESC
    """)

    songs = cursor.fetchall()
    conn.close()
    return songs


def is_song_liked(song_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM liked_songs WHERE song_id = ?", (song_id,))
    liked = cursor.fetchone()

    conn.close()
    return liked is not None


def create_playlist(name, cover_image=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO playlists (name, cover_image) VALUES (?, ?)",
        (name, cover_image)
    )

    conn.commit()
    conn.close()


def get_playlists():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM playlists ORDER BY id DESC")
    playlists = cursor.fetchall()

    conn.close()
    return playlists


def get_playlist(playlist_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM playlists WHERE id = ?", (playlist_id,))
    playlist = cursor.fetchone()

    conn.close()
    return playlist


def add_song_to_playlist(playlist_id, song_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM playlist_songs
        WHERE playlist_id = ? AND song_id = ?
    """, (playlist_id, song_id))

    exists = cursor.fetchone()

    if not exists:
        cursor.execute("""
            INSERT INTO playlist_songs (playlist_id, song_id)
            VALUES (?, ?)
        """, (playlist_id, song_id))

    conn.commit()
    conn.close()


def get_playlist_songs(playlist_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT songs.* FROM songs
        JOIN playlist_songs ON songs.id = playlist_songs.song_id
        WHERE playlist_songs.playlist_id = ?
        ORDER BY playlist_songs.id DESC
    """, (playlist_id,))

    songs = cursor.fetchall()
    conn.close()
    return songs


def remove_song_from_playlist(playlist_id, song_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM playlist_songs
        WHERE playlist_id = ? AND song_id = ?
    """, (playlist_id, song_id))

    conn.commit()
    conn.close()


def delete_playlist(playlist_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM playlist_songs WHERE playlist_id = ?", (playlist_id,))
    cursor.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))

    conn.commit()
    conn.close()


def get_playlist_song_count(playlist_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM playlist_songs
        WHERE playlist_id = ?
    """, (playlist_id,))

    count = cursor.fetchone()[0]

    conn.close()
    return count


def increase_song_view(song_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE songs
        SET views = COALESCE(views, 0) + 1
        WHERE id = ?
    """, (song_id,))

    conn.commit()
    conn.close()


def get_total_views():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(COALESCE(views, 0)) FROM songs")
    total = cursor.fetchone()[0]

    conn.close()
    return total or 0


def get_total_likes():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM liked_songs")
    total = cursor.fetchone()[0]

    conn.close()
    return total
def increase_song_download(song_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE songs
        SET downloads = COALESCE(downloads, 0) + 1
        WHERE id = ?
    """, (song_id,))

    conn.commit()
    conn.close()


def get_total_downloads():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(COALESCE(downloads, 0)) FROM songs")
    total = cursor.fetchone()[0]

    conn.close()
    return total or 0


def get_most_played_songs(limit=10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM songs
        ORDER BY COALESCE(views, 0) DESC
        LIMIT ?
    """, (limit,))

    songs = cursor.fetchall()
    conn.close()
    return songs