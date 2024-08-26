import time
from pinpong.board import Board, Pin, Servo
import tkinter as tk

# Initialize the UNIHIKER board and servos
Board("UNIHIKER").begin()

s1 = Servo(Pin(Pin.P23))  # Initialize the first servo
s2 = Servo(Pin(Pin.P21))  # Initialize the second servo

# Function to update the angle of the first servo based on slider value
def update_servo1(angle):
    s1.angle(int(angle))

# Function to update the angle of the second servo based on slider value
def update_servo2(angle):
    s2.angle(int(angle))

# Create the main window
root = tk.Tk()
root.title("Servo Control")
root.geometry("240x320")  # Set the window size to 240x320 pixels (full screen on UNIHIKER)

# Create a frame for the sliders
frame = tk.Frame(root)
frame.pack(expand=True, fill="both")

# Create a frame for the first servo
frame1 = tk.Frame(frame)
frame1.pack(side="left", padx=10, pady=10, fill="y")

# Add a label for the first slider
label1 = tk.Label(frame1, text="Servo 1")
label1.pack(side="top")

# Create the first slider for servo1 (vertical orientation)
slider1 = tk.Scale(frame1, from_=0, to=180, orient="vertical", command=update_servo1)
slider1.pack(side="top", fill="y")

# Create a frame for the second servo
frame2 = tk.Frame(frame)
frame2.pack(side="right", padx=10, pady=10, fill="y")

# Add a label for the second slider
label2 = tk.Label(frame2, text="Servo 2")
label2.pack(side="top")

# Create the second slider for servo2 (vertical orientation)
slider2 = tk.Scale(frame2, from_=0, to=180, orient="vertical", command=update_servo2)
slider2.pack(side="top", fill="y")

# Run the GUI loop
root.mainloop()
