
#  -*- coding: UTF-8 -*-
from unihiker import GUI  # Import the packag 
gui = GUI()               # Instantiate the GUI class


txt = gui.draw_text(text="YAKROO108 Picture", x=120, y=10, font_size=16, origin="center", color="#0000FF")
# Load and display an image at (0, 0) with the original size
img_image2 = gui.draw_image(x=0, y=60, image='/root/upload/cats.bmp')

# Load and display an image at (120, 100) with a width of 80 and height of 50
# The image is centered and a lambda function is assigned to the onclick event
img_image = gui.draw_image(x=120, y=180, w=80, h=50, image='/root/upload/cats.bmp', origin='center', onclick=lambda: print("image clicked"))

# Load and display an image using the PIL library at (10, 180)
#img_image3 = gui.draw_image(x=10, y=180, image=Image.open('/root/upload/cats.bmp'))

import time
while True:
    # Add a sleep to prevent the program from exiting and getting stuck
    time.sleep(1)
