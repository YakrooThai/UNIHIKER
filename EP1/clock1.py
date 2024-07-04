from unihiker import GUI
import datetime
import time
import pytz

# Instantiate the GUI class
gui = GUI()
gui.fill_rect(x=0, y=0, w=240, h=320, color="black")
# Define Bangkok timezone
bangkok_tz = pytz.timezone('Asia/Bangkok')

# Function to draw the current time
def draw_time():
    current_time = datetime.datetime.now(bangkok_tz).strftime('%H:%M:%S')
    # Clear the previous time display by drawing a black rectangle
    #gui.draw_rectangle(0, 180, 240, 220, color="black", fill=True)
    gui.fill_rect(x=14, y=176, w=210, h=38, color="black", onclick=lambda: print("fill rect clicked"))
    # Draw the current time
    gui.draw_digit(x=120, y=200, text=current_time, origin="center", color="blue", font_size=30)

# Draw the static date
gui.draw_digit(x=120, y=160, text='2024-07-03', origin="center", color="red", font_size=25)

while True:
    draw_time()
    time.sleep(1)