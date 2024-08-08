import cv2
import numpy as np
from unihiker import GUI
from pinpong.board import *
from pinpong.extension.unihiker import *
import os
import time

# ...... classify_image ... my_library
from tensorconv import classify_image

Board().begin()  # Initialize the UNIHIKER

gui = GUI()

# ....................
def load_image(image_path):
    print(f"Loading image from {image_path}...")
    image = cv2.imread(image_path)
    if image is None:
        raise Exception(f"Could not load image from file: {image_path}")
    print("Image loaded successfully.")
    return image

# ..................... labels_ecg.txt
def load_labels(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]

# ..................................
def load_overlay_image(result):
    # ........................................ (.................................)
    cleaned_result = result.split()[0]  # .........................
    overlay_image_path = f"{cleaned_result}.bmp"
    
    # ..........................
    if os.path.exists(overlay_image_path):
        return load_image(overlay_image_path)
    else:
        print(f"Image {overlay_image_path} not found. Loading 'no.bmp'.")
        return load_image("no.bmp")

# ...................................
def draw_text(image, text, pos, font_scale=1, font_thickness=2, text_color=(0, 255, 0), bg_color=(0, 0, 0)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    x, y = pos
    cv2.rectangle(image, (x, y - text_h - 10), (x + text_w, y + 5), bg_color, -1)
    cv2.putText(image, text, (x, y), font, font_scale, text_color, font_thickness)

# ...............................
def resize_image(image, max_height=240, max_width=240):    
    height, width = image.shape[:2]
    if height > max_height or width > max_width:
        scaling_factor = min(max_height / height, max_width / width)
        new_size = (int(width * scaling_factor), int(height * scaling_factor))
        resized_image = cv2.resize(image, new_size)
        return resized_image
    return image

# ..................................... ...
def add_green_border(image, border_thickness=5):
    bordered_image = image.copy()
    height, width = image.shape[:2]
    cv2.rectangle(bordered_image, (0, 0), (width-1, height-1), (0, 255, 0), border_thickness)
    #cv2.rectangle(bordered_image, (0, 0), (width-1, height-1), (255, 255, 0), border_thickness)
    return bordered_image

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    while True:
        captured = False

        window_name = "Camera Feed"
        x, y = -70, 1  # ...................... (.................)
        gui.draw_text(x=50, y=280, text='By YAKROO108')
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
        
            # ...................... 240x320
            frame_resized = resize_image(frame)

            # .................... ...
            frame_with_border = add_green_border(frame_resized)

            # .......... "SmartECG" ...............
            draw_text(frame_with_border, "SmartECG", (5, 28), font_scale=1, font_thickness=2, text_color=(255, 165, 0))

            cv2.imshow(window_name, frame_with_border)
            cv2.moveWindow(window_name, x, y)  # ......................

            key = cv2.waitKey(1) & 0xFF
            if button_b.is_pressed():
                break
            elif button_a.is_pressed():
                time.sleep(0.01)
                if button_a.is_pressed() == True:
                    captured = True
                    buzzer.pitch(1000)  # ...................... 1000 Hz
                    time.sleep(0.1)  # ................. 100 ms
                    buzzer.stop()  # .........
                    captured = True
                    image = frame
                    image_path = "captured_image.jpg"
                    cv2.imwrite(image_path, image)
                    print("Image captured and saved.")
                    break

        if captured:
            # .............................
            print("Classifying image...")
            result, confidence_str, confidences, classes = classify_image(image, "model_ecg.tflite", "labels_ecg.txt")

            # ...........
            print(f"Result: {result}")
            print(f"Confidence:\n{confidence_str}")

            # ..................... 240x320
            resized_image = resize_image(image)

            # ..................
            draw_text(resized_image, f"Result: {result}", (5, 30), font_scale=.6, font_thickness=2, text_color=(0, 255, 0))

            # ....... overlay ..........
            overlay_image = load_overlay_image(result)

            # ........... overlay .......... 120x160
            overlay_image = resize_image(overlay_image, 120, 160)

            # ............. overlay_image ............. resized_image ...
            overlay_height, overlay_width = overlay_image.shape[:2]
            pos_x, pos_y = 10, 200  # ........................ overlay

            print("Overlay image shape:", overlay_image.shape)
            print("Resized image shape:", resized_image.shape)

            if pos_y + overlay_height <= resized_image.shape[0] and pos_x + overlay_width <= resized_image.shape[1]:
                combined_image = resized_image.copy()
                combined_image[pos_y:pos_y + overlay_height, pos_x:pos_x + overlay_width] = overlay_image
            else:
                combined_image = resized_image

            # ...................
            result_window_name = 'Result Image'
            cv2.imshow(result_window_name, combined_image)
            # ................................
            result_x, result_y = -70, 1
            cv2.moveWindow(result_window_name, result_x, result_y)

            # ....... overlay .....................
            cv2.imshow("Overlay Image", overlay_image)
            cv2.moveWindow("Overlay Image", x, 200)
        
            cv2.waitKey(0)
            buzzer.pitch(1500)  # ...................... 1000 Hz
            time.sleep(0.1)  # ................. 100 ms
            buzzer.stop()  # .........
            cv2.destroyAllWindows()

    cap.release()
    cv2.destroyAllWindows()

