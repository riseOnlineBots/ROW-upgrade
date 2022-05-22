from math import sqrt
from threading import Thread, Lock
from time import sleep, time

import cv2 as cv
import pyautogui

class BotState:
    INITIALIZING = 0
    SEARCHING = 1
    MOVING = 2
    UPGRADING = 3
    UPGRADED = 4

class RiseOnlineBot:
    # Constants.
    INITIALIZING_SECONDS = 6
    UPGRADING_SECONDS = 5
    ITEM_MATCH_THRESHOLD = 0.50

    # Threading properties.
    stopped = True
    lock = None

    # Properties.
    state = None
    targets = []
    screenshot = None
    timestamp = None
    window_offset = (0, 0)
    window_w = 0
    window_h = 0
    upgrading_item = None
    sort_button = None

    def __init__(self, window_offset, window_size):
        # create a thread lock object
        self.lock = Lock()

        # for translating window positions into screen positions, it's easier to just
        # get the offsets and window size from WindowCapture rather than passing in
        # the whole object
        self.window_offset = window_offset
        self.window_w = window_size[0]
        self.window_h = window_size[1]

        # pre-load the needle image used to confirm our object detection
        self.upgrading_item = cv.imread('magePad.jpg', cv.IMREAD_UNCHANGED)
        self.sort_button = cv.imread('sortButton.jpg', cv.IMREAD_UNCHANGED)

        # start bot in the initializing mode to allow us time to get setup.
        # mark the time at which this started so we know when to complete it
        self.state = BotState.INITIALIZING
        self.timestamp = time()

