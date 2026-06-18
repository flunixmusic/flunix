const songCards = document.querySelectorAll(".song-card, .playlist-song-row");

const audio = document.getElementById("main-audio");
const playPauseBtn = document.getElementById("play-pause-btn");
const playerTitle = document.getElementById("player-title");
const playerArtist = document.getElementById("player-artist");
const playerCover = document.getElementById("player-cover");
const progressBar = document.getElementById("progress-bar");
const currentTimeText = document.getElementById("current-time");
const durationText = document.getElementById("duration");
const muteBtn = document.getElementById("mute-btn");
const volumeSlider = document.getElementById("volume-slider");
const likeBtn = document.getElementById("like-btn");
const downloadBtn = document.getElementById("download-btn");

const prevBtn = document.getElementById("prev-btn");
const nextBtn = document.getElementById("next-btn");
const repeatBtn = document.getElementById("repeat-btn");

let currentSongId = null;
let currentIndex = -1;
let isRepeat = false;

function formatTime(seconds) {
    if (isNaN(seconds)) {
        return "0:00";
    }

    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);

    return minutes + ":" + (secs < 10 ? "0" + secs : secs);
}

function setPlayerCover(coverSrc) {
    if (!playerCover) return;

    if (coverSrc) {
        playerCover.innerHTML = `<img src="${coverSrc}" alt="cover">`;
    } else {
        playerCover.innerHTML = "♪";
    }
}

function playSongByIndex(index) {
    if (!audio || index < 0 || index >= songCards.length) {
        return;
    }

    const card = songCards[index];

    const title = card.getAttribute("data-title");
    const artist = card.getAttribute("data-artist");
    const audioSrc = card.getAttribute("data-audio");
    const songId = card.getAttribute("data-id");
    const coverSrc = card.getAttribute("data-cover");

    if (!audioSrc) {
        return;
    }

    currentIndex = index;
    currentSongId = songId;
    fetch("/track-view/" + songId);

    if (playerTitle) {
        playerTitle.innerText = title || "Unknown Song";
    }

    if (playerArtist) {
        playerArtist.innerText = artist || "Unknown Artist";
    }

    setPlayerCover(coverSrc);

    audio.src = audioSrc;

    if (downloadBtn) {
        downloadBtn.href = audioSrc;
    }

    localStorage.setItem("tunexa_song_src", audioSrc);
    localStorage.setItem("tunexa_song_title", title || "Unknown Song");
    localStorage.setItem("tunexa_song_artist", artist || "Unknown Artist");
    localStorage.setItem("tunexa_song_cover", coverSrc || "");

    audio.play().catch(function(error) {
        console.log("Audio play error:", error);
    });

    if (playerCover) {
        playerCover.classList.add("rotating");
    }

    if (playPauseBtn) {
        playPauseBtn.innerText = "⏸";
    }

    if (likeBtn) {
        likeBtn.innerHTML = "♡";
        likeBtn.classList.remove("active");
    }
}

songCards.forEach((card, index) => {
    card.addEventListener("click", function(event) {
        const clickedButton = event.target.closest("button");

        if (clickedButton) {
            return;
        }

        event.preventDefault();
        playSongByIndex(index);
    });
});

if (playPauseBtn) {
    playPauseBtn.addEventListener("click", function() {
        if (!audio || !audio.src) return;

        if (audio.paused) {
            audio.play();

            if (playerCover) {
                playerCover.classList.add("rotating");
            }

            playPauseBtn.innerText = "⏸";
        } else {
            audio.pause();

            if (playerCover) {
                playerCover.classList.remove("rotating");
            }

            playPauseBtn.innerText = "▶";
        }
    });
}

if (nextBtn) {
    nextBtn.addEventListener("click", function() {
        if (songCards.length === 0) return;

        let nextIndex = currentIndex + 1;

        if (nextIndex >= songCards.length || currentIndex === -1) {
            nextIndex = 0;
        }

        playSongByIndex(nextIndex);
    });
}

if (prevBtn) {
    prevBtn.addEventListener("click", function() {
        if (songCards.length === 0) return;

        let prevIndex = currentIndex - 1;

        if (prevIndex < 0) {
            prevIndex = songCards.length - 1;
        }

        playSongByIndex(prevIndex);
    });
}

if (repeatBtn) {
    repeatBtn.addEventListener("click", function() {
        isRepeat = !isRepeat;

        if (audio) {
            audio.loop = isRepeat;
        }

        if (isRepeat) {
            repeatBtn.classList.add("active-repeat");
        } else {
            repeatBtn.classList.remove("active-repeat");
        }
    });
}

if (audio) {
    audio.addEventListener("loadedmetadata", function() {
        if (durationText) {
            durationText.innerText = formatTime(audio.duration);
        }
    });

    audio.addEventListener("timeupdate", function() {
        if (audio.duration) {
            const progress = (audio.currentTime / audio.duration) * 100;

            if (progressBar) {
                progressBar.value = progress;
            }

            if (currentTimeText) {
                currentTimeText.innerText = formatTime(audio.currentTime);
            }
        }
    });

    audio.addEventListener("ended", function() {
        if (isRepeat) return;

        let nextIndex = currentIndex + 1;

        if (nextIndex < songCards.length) {
            playSongByIndex(nextIndex);
        } else {
            if (playPauseBtn) {
                playPauseBtn.innerText = "▶";
            }

            if (playerCover) {
                playerCover.classList.remove("rotating");
            }

            if (progressBar) {
                progressBar.value = 0;
            }

            if (currentTimeText) {
                currentTimeText.innerText = "0:00";
            }
        }
    });
}

if (progressBar) {
    progressBar.addEventListener("input", function() {
        if (audio && audio.duration) {
            audio.currentTime = (progressBar.value / 100) * audio.duration;
        }
    });
}

if (volumeSlider) {
    volumeSlider.addEventListener("input", function() {
        if (!audio) return;

        audio.volume = volumeSlider.value;

        if (muteBtn) {
            muteBtn.innerText = audio.volume == 0 ? "🔇" : "♫";
        }
    });
}

if (muteBtn) {
    muteBtn.addEventListener("click", function() {
        if (!audio || !volumeSlider) return;

        if (audio.muted) {
            audio.muted = false;
            muteBtn.innerText = "♫";
            volumeSlider.value = audio.volume;
        } else {
            audio.muted = true;
            muteBtn.innerText = "🔇";
            volumeSlider.value = 0;
        }
    });
}

if (likeBtn) {
    likeBtn.addEventListener("click", function() {
        if (!currentSongId) {
            alert("Pehle song play karo");
            return;
        }

        fetch("/like/" + currentSongId)
            .then(() => {
                likeBtn.classList.toggle("active");

                if (likeBtn.classList.contains("active")) {
                    likeBtn.innerHTML = "♥";
                } else {
                    likeBtn.innerHTML = "♡";
                }
            });
    });
}

/* Theme Save */
const themeSelect = document.getElementById("theme-select");
const appBody = document.getElementById("app-body");

const savedTheme = localStorage.getItem("tunexa_theme");

if (savedTheme && appBody) {
    if (savedTheme === "light") {
        appBody.classList.add("light-theme");
    }
}

if (themeSelect) {
    if (savedTheme) {
        themeSelect.value = savedTheme;
    }

    themeSelect.addEventListener("change", function() {
        if (this.value === "light") {
            appBody.classList.add("light-theme");
            localStorage.setItem("tunexa_theme", "light");
        } else {
            appBody.classList.remove("light-theme");
            localStorage.setItem("tunexa_theme", "dark");
        }
    });
}

/* Language Save */
const languageSelect = document.getElementById("language-select");
const savedLanguage = localStorage.getItem("tunexa_language");

function applyLanguage(lang) {
    const navHome = document.getElementById("nav-home");
    const navSearch = document.getElementById("nav-search");
    const navLibrary = document.getElementById("nav-library");
    const navLiked = document.getElementById("nav-liked");
    const navSettings = document.getElementById("nav-settings");
    const navPlaylists = document.getElementById("nav-playlists");
    const settingsTitle = document.getElementById("settings-title");

    if (lang === "Hindi") {
        if (navHome) navHome.innerText = "होम";
        if (navSearch) navSearch.innerText = "खोज";
        if (navLibrary) navLibrary.innerText = "लाइब्रेरी";
        if (navLiked) navLiked.innerText = "पसंदीदा गाने";
        if (navSettings) navSettings.innerText = "सेटिंग्स";
        if (navPlaylists) navPlaylists.innerText = "प्लेलिस्ट";
        if (settingsTitle) settingsTitle.innerText = "⚙ सेटिंग्स";
    } else {
        if (navHome) navHome.innerText = "Home";
        if (navSearch) navSearch.innerText = "Search";
        if (navLibrary) navLibrary.innerText = "Your Library";
        if (navLiked) navLiked.innerText = "Liked Songs";
        if (navSettings) navSettings.innerText = "Settings";
        if (navPlaylists) navPlaylists.innerText = "Playlists";
        if (settingsTitle) settingsTitle.innerText = "⚙ Settings";
    }
}

if (savedLanguage) {
    applyLanguage(savedLanguage);
}

if (languageSelect) {
    if (savedLanguage) {
        languageSelect.value = savedLanguage;
    }

    languageSelect.addEventListener("change", function() {
        localStorage.setItem("tunexa_language", this.value);
        applyLanguage(this.value);
    });
}

/* Restore player info after page reload */
window.addEventListener("load", function () {
    const savedSrc = localStorage.getItem("tunexa_song_src");
    const savedTitle = localStorage.getItem("tunexa_song_title");
    const savedArtist = localStorage.getItem("tunexa_song_artist");
    const savedCover = localStorage.getItem("tunexa_song_cover");

    if (savedSrc && audio) {
        audio.src = savedSrc;

        if (downloadBtn) {
            downloadBtn.href = savedSrc;
        }

        if (playerTitle) {
            playerTitle.innerText = savedTitle || "Tunexa Player";
        }

        if (playerArtist) {
            playerArtist.innerText = savedArtist || "Select a song";
        }

        if (savedCover && playerCover) {
            playerCover.innerHTML = `<img src="${savedCover}" alt="cover">`;
        }
    }
});
/* Dynamic Greeting */

const greetingText = document.getElementById("greeting-text");

if (greetingText) {

    const hour = new Date().getHours();

    if (hour >= 5 && hour < 12) {
        greetingText.innerText = "Good Morning ☀️";
    }
    else if (hour >= 12 && hour < 17) {
        greetingText.innerText = "Good Afternoon 🌤️";
    }
    else if (hour >= 17 && hour < 21) {
        greetingText.innerText = "Good Evening 🌇";
    }
    else {
        greetingText.innerText = "Good Night 🌙";
    }
}
function copySongLink(path){
    const fullLink = window.location.origin + path;

    navigator.clipboard.writeText(fullLink).then(function(){
        alert("Song link copied!");
    });
}
const adminSearch = document.getElementById("admin-search");

if(adminSearch){
    adminSearch.addEventListener("input", function(){
        const value = this.value.toLowerCase();
        const rows = document.querySelectorAll(".admin-song-row");

        rows.forEach(row => {
            const title = row.getAttribute("data-title") || "";
            const artist = row.getAttribute("data-artist") || "";
            const genre = row.getAttribute("data-genre") || "";
            const album = row.getAttribute("data-album") || "";

            const text = (title + " " + artist + " " + genre + " " + album).toLowerCase();

            row.style.display = text.includes(value) ? "grid" : "none";
        });
    });
}