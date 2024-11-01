#coding:utf-8

import cv2
import time
import numpy as np

# Load the face cascade classifier
casecade = cv2.CascadeClassifier()
casecade.load(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Load ghost image with transparency
ghost_img = cv2.imread('ghost.png', -1)

# Initialize the camera
cap = cv2.VideoCapture(0)
while not (cap.isOpened()):
    print("Camera not found")
    time.sleep(1)

# Set camera properties
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cv2.namedWindow('camera', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('camera', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    # Read frame from the camera
    success, img = cap.read()
    img = cv2.flip(img, 1)
    if success:
        h, w, c = img.shape
        w1 = h * 240 // 320  # Change the height to fit the render image
        x1 = (w - w1) // 2  # Midpoint of width without resizing
        img = img[:, x1:x1 + w1]  # Crop into the center 
        img = cv2.resize(img, (240, 320))  # Resize according to the screen keeping the aspect ratio 
        outImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        poss = casecade.detectMultiScale(outImg, 1.5, 3)
        print(poss)
        
        # Display text at the top of the screen
        cv2.putText(img, "Halloween By YAKROO108", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        # Detect black objects in frame
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 30])
        black_mask = cv2.inRange(hsv, lower_black, upper_black)
        contours, _ = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) > 500:  # Adjust size threshold
                x, y, w, h = cv2.boundingRect(contour)

                # Draw a rectangle around detected black object
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red rectangle for black object

                # Resize ghost image to match detected black object
                ghost_resized = cv2.resize(ghost_img, (w, h))

                # Insert ghost image using NumPy array slicing
                alpha_s = ghost_resized[:, :, 3] / 255.0  # Alpha channel for ghost
                alpha_l = 1.0 - alpha_s  # Alpha for background

                # For each color channel in BGR
                for c in range(0, 3):
                    img[y:y+h, x:x+w, c] = (alpha_s * ghost_resized[:, :, c] +
                                            alpha_l * img[y:y+h, x:x+w, c])

        for pos in poss:
            x = pos[0]
            y = pos[1]
            w = pos[2]
            h = pos[3]
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2, cv2.FILLED)
            cv2.putText(img, str(x), (100, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Show the window
        cv2.imshow("camera", img)
        if cv2.waitKey(10) & 0xff == ord('a'):
            break

# Release the camera
cap.release()
cv2.destroyAllWindows()
