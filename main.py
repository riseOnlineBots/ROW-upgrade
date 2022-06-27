import os
import sys
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


class DebugEnum:
    UPGRADE_SCROLL = 0
    UPGRADABLE_ITEMS = 1
    MONEY = 2
    CONFIRM_BUTTON = 3
    NO_ANIMATION = 4


wincap = WindowCapture(None)
vision = Vision('commonUpgradeScroll.jpg', 'priest/paper/pauldron.jpg', 'confirmButton.jpg')

upgrade_scroll_position = []
confirm_button_position = []
item_positions = []
upgraded_items = []
stage = 1
max_stage = 7

for i in list(range(3))[::-1]:
    print('Starting in ', i + 1)
    sleep(1)

print('Get ready! All upgradable slots will be upgraded to level +{}.'.format(max_stage + 1))
loop_time = time()

state = StateEnum.INITIALIZING

# DEBUG = DebugEnum.UPGRADABLE_ITEMS
DEBUG = None


def detect_upgrade_scroll():
    global upgrade_scroll_position, DEBUG

    if len(upgrade_scroll_position):
        return upgrade_scroll_position

    rectangles = vision.findUpgradeScroll(screenshot, 0.7)
    positions = vision.get_click_points(rectangles)

    if not positions:
        print('There is no upgrade scroll in your inventory.')
        stop()

    target = wincap.get_screen_position(positions[0])

    if DEBUG == DebugEnum.UPGRADE_SCROLL:
        image = vision.draw_crosshairs(screenshot, positions)
        cv.imshow('Display', image)

    upgrade_scroll_position = target

    return rectangles


def detect_confirm_button():
    global confirm_button_position, DEBUG

    if len(confirm_button_position):
        return confirm_button_position

    rectangles = vision.findConfirmButton(screenshot, 0.7)
    positions = vision.get_click_points(rectangles)

    if not positions:
        print("Did you open the upgrade window? I couldn't detect the confirm button.")
        stop()

    target = wincap.get_screen_position(positions[0])

    if DEBUG == DebugEnum.CONFIRM_BUTTON:
        image = vision.draw_crosshairs(screenshot, positions)
        cv.imshow('Display', image)

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
    global item_positions, DEBUG

    if len(item_positions):
        return item_positions

    rectangles = vision.find(screenshot, 0.8)
    item_positions = vision.get_click_points(rectangles)

    if not item_positions:
        print("I couldn't find any upgradable item. Shutting down the bot.")
        stop()

    if DEBUG == DebugEnum.UPGRADABLE_ITEMS:
        image = vision.draw_crosshairs(screenshot, item_positions)
        cv.imshow('Display', image)


def detect_and_click_first_upgradable_item():
    global item_positions, upgraded_items

    for item in item_positions:
        if item not in upgraded_items:
            x, y = item
            py.click(button='right', x=x, y=y)
            upgraded_items.append(item)
            break


def stop():
    cv.destroyAllWindows()
    sys.exit()


def run():
    global upgraded_items, item_positions, stage, max_stage

    print('Total: {} Current: {}'.format(len(item_positions), len(upgraded_items)))

    if len(item_positions) == len(upgraded_items):
        if stage == max_stage:
            print('All slots have been upgraded to the desired level: {} '.format(stage + 1))
            stop()
        else:
            stage += 1

            print('All items are upgraded. Preparing the next stage : {} '.format(stage + 1))

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
