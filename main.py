import os
from threading import Thread
from time import time, sleep

import cv2 as cv
import pyautogui as py

from vision import Vision
from windowcapture import WindowCapture

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class StateEnum:
    INITIALIZING = 0
    READY = 1
    UPGRADING = 2
    UPGRADED = 3
    INVENTORY_COMPLETED = 4  # Lets us re-initialize when whole inventory is completed.


wincap = WindowCapture(None)
vision = Vision('commonUpgradeScroll.jpg', 'magePad.jpg', 'confirmButton.jpg')

upgrade_scroll_position = []
confirm_button_position = []
item_positions = []
upgraded_items = []

for i in list(range(3))[::-1]:
    print('Starting in ', i + 1)
    sleep(1)

loop_time = time()

state = StateEnum.INITIALIZING


def detect_upgrade_scroll():
    global upgrade_scroll_position

    if len(upgrade_scroll_position):
        return upgrade_scroll_position

    rectangles = vision.findUpgradeScroll(screenshot, 0.7)
    positions = vision.get_click_points(rectangles)
    target = wincap.get_screen_position(positions[0])

    upgrade_scroll_position = target

    return rectangles


def detect_confirm_button():
    global confirm_button_position

    if len(confirm_button_position):
        return confirm_button_position

    rectangles = vision.findConfirmButton(screenshot, 0.7)
    positions = vision.get_click_points(rectangles)
    target = wincap.get_screen_position(positions[0])

    confirm_button_position = target

    return rectangles


def click_upgrade_scroll():
    global upgrade_scroll_position

    x = upgrade_scroll_position[0]
    y = upgrade_scroll_position[1]

    py.moveTo(x, y)
    py.click(button='right', x=x, y=y)


def upgrade_the_item():
    global confirm_button_position

    x = confirm_button_position[0]
    y = confirm_button_position[1]

    py.moveTo(x, y)
    py.click(x=x, y=y)
    py.moveTo(x + 60, y + 50)
    py.click()
    print('An item is upgraded.')


def initialize_upgradable_items():
    global item_positions

    if len(item_positions):
        return item_positions

    rectangles = vision.find(screenshot, 0.8)
    item_positions = vision.get_click_points(rectangles)


def detect_and_click_first_upgradable_item():
    global item_positions, upgraded_items

    for item in item_positions:
        if item not in upgraded_items:
            x, y = item
            py.click(button='right', x=x, y=y)
            upgraded_items.append(item)
            break


def run():
    global upgraded_items, item_positions
    print(len(item_positions), len(upgraded_items))

    if len(item_positions) == len(upgraded_items):
        print('All items are upgraded. Preparing the next stage.')
        upgraded_items = []
        item_positions = []
        sleep(1)
        initialize_upgradable_items()
        run()
    else:
        detect_and_click_first_upgradable_item()
        sleep(0.2)
        click_upgrade_scroll()
        sleep(0.2)
        upgrade_the_item()
        sleep(0.2)  # In case 'No Animation' option gets removed from the game, improve the sleep duration.


while True:
    screenshot = wincap.get_screenshot()

    # upgrade_scroll_rectangles = detectAndClickUpgradeScroll()
    # upgrade_scroll_positions = vision.get_click_points(upgrade_scroll_rectangles)
    # detected_upgrade_scroll = vision.draw_crosshairs(screenshot, upgrade_scroll_positions)
    # cv.imshow('Display', detected_upgrade_scroll)

    # rectangles = vision.findConfirmButton(screenshot, 0.7)
    # positions = vision.get_click_points(rectangles)
    # image = vision.draw_crosshairs(screenshot, positions)
    # cv.imshow('Display', image)

    detect_upgrade_scroll()
    detect_confirm_button()
    initialize_upgradable_items()

    thread = Thread(target=run())

    key = cv.waitKey(1) & 0xFF

    if key == ord("q"):
        cv.destroyAllWindows()
        break
