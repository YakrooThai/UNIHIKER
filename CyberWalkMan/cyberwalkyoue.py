import sys
from pinpong.board import Board
from pinpong.libs.dfrobot_ssd1306 import SSD1306_I2C
import time
from unihiker import Audio
from pinpong.board import *
from pinpong.extension.unihiker import *
from pydub import AudioSegment
from pydub.playback import play

import tkinter as tk
from PIL import Image, ImageTk
import os
import threading
import random

# Variables for controlling audio playback
current_audio = None  # Stores the currently playing audio object
stop_event = threading.Event()  # Used to stop audio playback

# Check and create the music folder if it doesn't exist
MUSIC_FOLDER = "music"
if not os.path.exists(MUSIC_FOLDER):
    os.makedirs(MUSIC_FOLDER)

# Read audio files from the music folder
def load_playlist(folder):
    playlist = []
    for file in os.listdir(folder):
        if file.endswith(".mp3"):
            playlist.append(os.path.join(folder, file))
    return playlist

playlist = load_playlist(MUSIC_FOLDER)  # Load songs from the music folder
current_song_index = 0

# Flag to indicate if the song is playing
is_playing = False

# Variable to store the start time of the song
start_time = None

# Variable to store the current volume level (initially 50%)
current_volume = 1

def draw_bmp_with_position(oled, bmp_path, offset_x=0, offset_y=0):
    """
    Draws a BMP image at the specified position (offset_x, offset_y) on the SSD1306 OLED display.
    """
    bmp_image = Image.open(bmp_path).convert("1")  # Convert to 1-bit color
    width, height = bmp_image.size

    # Ensure the BMP image dimensions fit within the OLED display
    if width > 128 or height > 64:
        raise ValueError("BMP image size must fit within the OLED display dimensions (128x64).")

    # Ensure the BMP image position does not exceed the OLED display boundaries
    if offset_x + width > 128 or offset_y + height > 64:
        raise ValueError("BMP image position exceeds OLED display boundaries.")

    # Draw the BMP image at the specified position (offset_x, offset_y)
    for y in range(height):
        for x in range(width):
            pixel = bmp_image.getpixel((x, y))
            oled.pixel(x + offset_x, y + offset_y, 1 if pixel == 255 else 0)  # Apply offset
    oled.show()

# Initialize the UNIHIKER
Board().begin()

oled1 = SSD1306_I2C(width=128, height=64)
# Initialize Audio instance
audio = Audio()

# Display the BMP image at (10, 10)
draw_bmp_with_position(oled1, "val4.bmp", offset_x=0, offset_y=0)

current_time = time.localtime()  # Get current local time
hours = current_time.tm_hour
minutes = current_time.tm_min

time_str = f"{hours:02}:{minutes:02}"

# Clear the area where the time is displayed
oled1.fill_rect(86, 0, 128, 14, 0)  # Clear bottom section for time display
oled1.text(time_str, 86, 6)
oled1.show()

# Function to increase the volume
def volume_up():
    global current_volume
    if current_volume < 100:  # Maximum volume is 100%
        current_volume += 10
        audio.set_volume(current_volume / 100)  # Set volume as a float (0.0 to 1.0)
        volume_label.config(text=f"Volume: {current_volume}%")

# Function to decrease the volume
def volume_down():
    global current_volume
    if current_volume > 0:  # Minimum volume is 0%
        current_volume -= 10
        audio.set_volume(current_volume / 100)  # Set volume as a float (0.0 to 1.0)
        volume_label.config(text=f"Volume: {current_volume}%")

# Function to handle button presses
def handle_buttons():
    if button_a.is_pressed():
        volume_up()
        time.sleep(0.2)  # Debounce delay
    if button_b.is_pressed():
        volume_down()
        time.sleep(0.2)  # Debounce delay
    root.after(100, handle_buttons)

# Function to play the song
def play_song():
    global is_playing, current_song_index, start_time, current_audio

    if is_playing:
        stop_song()  # Stop the currently playing song

    if not playlist:  # If the playlist is empty
        song_label.config(text="No songs in playlist")
        return

    is_playing = True
    song_path = playlist[current_song_index]
    current_audio = AudioSegment.from_mp3(song_path)  # Load a new song
    song_label.config(text=f"Playing: {os.path.basename(song_path)}")
    start_time = time.time()

    # Use threading to play the song
    stop_event.clear()  # Reset stop_event
    threading.Thread(target=play_audio, args=(current_audio,)).start()
    update_time()

# Function to handle audio playback (in separate thread)
def play_audio(audio_segment):
    global is_playing
    try:
        play(audio_segment)  # Play the song
    except Exception as e:
        print("Error playing audio:", e)
    finally:
        is_playing = False

# Function to stop the current song
def stop_song():
    global is_playing, current_audio
    if is_playing:
        is_playing = False
        stop_event.set()  # Signal to stop the song
        song_label.config(text="Stopped")
        time_label.config(text="00:00 / 00:00")

# Function to play the next song and loop back to the first song after the last one
def next_song():
    global current_song_index
    if not playlist:  # If the playlist is empty
        return
    current_song_index = (current_song_index + 1) % len(playlist)
    play_song()

# Function to update song time and check if song is finished
def update_time():
    global is_playing, start_time, current_audio

    if is_playing and current_audio:
        total_time = current_audio.duration_seconds  # Total duration of the song
        elapsed_time = time.time() - start_time  # Time elapsed since the song started

        current_time_str = f"{int(elapsed_time // 60):02}:{int(elapsed_time % 60):02}"
        total_time_str = f"{int(total_time // 60):02}:{int(total_time % 60):02}"

        time_label.config(text=f"{current_time_str} / {total_time_str}")

        if elapsed_time >= total_time and is_playing:
            next_song()  # Play the next song when the current one ends

        root.after(1000, update_time)

# Create Tkinter window
root = tk.Tk()
root.title("UNIHIKER MiniWinamp")
root.geometry("240x320")

# Add a background image
bg_image = Image.open("background2.jpg")
bg_image = bg_image.resize((240, 320), Image.ANTIALIAS)
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Song label
song_label = tk.Label(root, text="No Song Playing", bg="black", fg="white", font=("TH Sarabun", 12))
song_label.place(x=10, y=10)

# Time label
time_label = tk.Label(root, text="00:00 / 00:00", bg="black", fg="skyblue", font=("TH Sarabun", 18))
time_label.place(x=36, y=30)

# Volume label
volume_label = tk.Label(root, text=f"Volume: {current_volume}%", bg="black", fg="white", font=("TH Sarabun", 12))
volume_label.place(x=10, y=210)

# Control buttons
play_button = tk.Button(root, text="Play", command=play_song, font=("TH Sarabun", 12), width=5, height=2)
play_button.place(x=1, y=250)

stop_button = tk.Button(root, text="Stop", command=stop_song, font=("TH Sarabun", 12), width=5, height=2)
stop_button.place(x=84, y=250)

next_button = tk.Button(root, text="Next", command=next_song, font=("TH Sarabun", 12), width=5, height=2)
next_button.place(x=160, y=250)

equalizer_frame = tk.Frame(root, bg="black")
equalizer_frame.place(x=14, y=64, width=214, height=40)

bars_upper = []
for i in range(20):
    bar = tk.Label(equalizer_frame, bg="white", width=2, height=1)
    bar.pack(side=tk.LEFT, padx=1)
    bars_upper.append(bar)

def animate_equalizer():
    for bar in bars_upper:
        bar.config(height=random.randint(1, 5))
    root.after(200, animate_equalizer)

animate_equalizer()

# Call the handle_buttons function
handle_buttons()

# Start the Tkinter main loop
root.mainloop()

