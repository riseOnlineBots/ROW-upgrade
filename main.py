import os
import sys
import threading
from time import time, sleep

import cv2 as cv
import pyautogui
from pynput import keyboard

from vision import Vision
from windowcapture import WindowCapture

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# for i in list(range(3))[::-1]:
#     print('Starting in ', i + 1)
#     sleep(1)

# initialize the WindowCapture class
wincap = WindowCapture(None)
# initialize the Vision class
vision_limestone = Vision('magePad.jpg', 'commonUpgradeScroll.jpg')

running = False

loop_time = time()


def run():
    while running:
        while True:

            # get an updated image of the game
            screenshot = wincap.get_screenshot()

            # display the processed image
            # vision_limestone.find(screenshot, 0.7)
            points = vision_limestone.findUpgradeScroll(screenshot, 0.7)

            if len(points):
                for (x, y) in points:
                    pyautogui.moveTo(x, y)

            cv.imshow('Matches', screenshot)


def stop():
    global running
    running = False
    sys.exit()


def on_press(key):
    global running

    if key == keyboard.Key.esc:
        stop()
        return False  # Stops the listener.
    try:
        k = key.char  # Single-char keys.
    except:
        k = key.name
    if k in ['f12']:
        running = True
        threading.Thread(target=run).start()


with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

print('Done.')
