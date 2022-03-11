from sense_emu import SenseHat
from time import sleep
from random import randint
from gtts import gTTS
from pygame import mixer
from Adafruit_IO import Client, Feed, Data, RequestError
from user_key import my_username, my_key
import time

sense = SenseHat()

feeds_keys = ['level1', 'level2', 'level3']
aio = Client(my_username, my_key)

y = [255, 255, 0]
x = [0, 0, 0]
b = [0, 0, 255]
r = [255, 0, 0]
g = [0, 255, 0]

charx = 0
chary = 0

path1 = [
    y, y, y, x, x, x, x, x,
    x, x, y, x, x, x, x, x,
    y, y, y, y, y, y, y, x,
    y, x, x, y, x, x, y, x,
    y, y, y, y, y, y, y, y,
    x, y, x, x, y, x, x, y,
    y, y, y, y, y, y, y, y,
    g, x, x, x, x, x, x, x
]
path2_clear = [x] * 56 + [g] + [x] * 7

path2_a = [
    y, y, y, x, x, x, x, x,
    x, x, y, x, x, x, x, x,
    y, y, y, y, y, y, y, x,
    y, x, x, y, x, x, y, x,
    y, y, y, y, y, y, y, y,
    x, x, x, x, y, x, x, y,
    y, y, y, x, y, y, y, y,
    g, x, y, y, y, x, x, x
]

path2_b = [
    y, x, y, y, y, y, y, y,
    y, x, y, x, x, x, x, y,
    y, y, y, y, y, y, y, y,
    y, x, x, y, x, y, x, x,
    x, x, x, y, y, y, y, y,
    y, y, y, x, x, x, x, y,
    y, x, y, x, y, y, y, y,
    g, x, y, y, y, x, y, x
]

path2_c = [
    y, y, y, y, y, y, y, x,
    x, x, y, x, x, x, y, x,
    y, y, y, y, y, y, y, y,
    y, x, x, x, x, x, x, y,
    y, y, y, y, y, y, y, y,
    x, x, x, x, y, x, x, y,
    y, y, y, x, y, y, y, y,
    g, x, y, y, y, x, y, x
]

paths2 = [path2_a, path2_b, path2_c]

path3 = [x] * 64

victory = [
    x, x, y, y, y, y, x, x,
    x, y, y, y, y, y, y, x,
    y, x, y, y, y, y, x, y,
    y, x, y, y, y, y, x, y,
    x, y, y, y, y, y, y, x,
    x, x, y, y, y, y, x, x,
    x, x, x, y, y, x, x, x,
    x, x, y, y, y, y, x, x,
]

#crate all the audio file
tts1 = gTTS(text=' Choose the level on the dashboard, press the joystick to end the game ')
tts1.save('start.mp3')

tts1 = gTTS(text=' Congratulations! You won ')
tts1.save('win.mp3')

tts1 = gTTS(text=' Good bye ')
tts1.save('bye.mp3')

tts1 = gTTS(text=' Follow the path until u reach the green dot and don\'t step on the mine ')
tts1.save('tutorial1.mp3')

tts1 = gTTS(text=' Follow the path until u reach the green dot ')
tts1.save('tutorial2.mp3')

tts1 = gTTS(text=' Collect as many coin as possible in 30 second. 3 2 1 GO ')
tts1.save('tutorial3.mp3')

mixer.init()
mixer.music.load('start.mp3')
mixer.music.play()
while mixer.music.get_busy() == True:
    pass

status_dict = {}

#create a dictionary for check the status of the button
def dashboard_status(feeds_keys):
    for level in feeds_keys:
        status = aio.feeds(level)
        status_dict[level] = aio.receive(status.key).value
    return status_dict


# play the win audio
def win(victory):
    sense.set_pixels(victory)
    mixer.music.load('win.mp3')
    mixer.music.play()
    while mixer.music.get_busy() == True:
        pass
    sleep(3)
    sense.clear()
    return 0

#say how many coins you have collected
def coin_count(victory, count):
    sense.clear()
    tts1 = gTTS(text='Congratulations! you earned ' + str(count) + 'coins')
    tts1.save('earned_coin.mp3')
    sense.set_pixels(victory)
    mixer.music.load('earned_coin.mp3')
    mixer.music.play()
    while mixer.music.get_busy() == True:
        pass
    sleep(3)
    sense.clear()

#create a coin
def treasure(path3, y):
    treasure = [randint(0, 7), randint(0, 7)]
    sense.set_pixel(treasure[0], treasure[1], y)
    return treasure


def level_1(x, b, r, g, charx, chary, path1, victory):
    sense.set_pixels(path1)

    #create a trap that can't make the level uncompletable
    while True:
        trap = [randint(0, 7), randint(2, 6)]
        print (trap)
        if sense.get_pixel(trap[0], trap[1]) != x and trap != [2, 2] and trap != [0, 6] and trap != [1, 6]:
            break

    sense.set_pixel(trap[0], trap[1], r)
    sleep(1)

    while True:
        sense.set_pixels(path1)
        sense.set_pixel(charx, chary, b)

        # controll of the player via joystick
        for event in sense.stick.get_events():
            if event.action == "pressed":
                if event.direction == "up" and chary > 0:
                    chary -= 1
                if event.direction == "down" and chary < 7:
                    chary += 1
                if event.direction == "left" and charx > 0:
                    charx -= 1
                if event.direction == "right" and charx < 7:
                    charx += 1

        current = path1[(charx + chary * 8)]
        player = [charx, chary]

        #controll if the player step over a trap or went out of the path and restart the level
        if current == x or player == trap:
            charx = 0
            chary = 0

        #controll if the player win
        if current == g:
            charx = chary = win(victory)
            break

        sleep(0.2)


def level_2(x, b, g, charx, chary, paths2, victory):
    p2 = paths2[randint(0, 2)]
    sense.set_pixels(p2)
    sleep(1)

    while True:
        sense.set_pixels(path2_clear)
        sense.set_pixel(charx, chary, b)

        # controll of the player via joystick
        for event in sense.stick.get_events():
            if event.action == "pressed":
                if event.direction == "up" and chary > 0:
                    chary -= 1
                if event.direction == "down" and chary < 7:
                    chary += 1
                if event.direction == "left" and charx > 0:
                    charx -= 1
                if event.direction == "right" and charx < 7:
                    charx += 1

        current = sense.get_pixel(charx, chary)
        player = p2[(charx + chary * 8)]

        #controll if the player went out of the path and restart the level
        if player == x:
            charx = 0
            chary = 0
            sense.set_pixels(p2)
            sleep(0.2)

        # controll if the player win
        if player == g:
            charx = chary = win(victory)
            break

        sleep(0.2)


def level_3(y, b, charx, chary, path3, victory):
    count = 0
    end = time.time() + 30
    while time.time() < end:
        sense.set_pixels(path3)
        coin = treasure(path3, y)

        while True:
            sense.set_pixels(path3)
            sense.set_pixel(coin[0], coin[1], y)

            #controll of the player via joystick
            for event in sense.stick.get_events():
                if event.action == "pressed":
                    if event.direction == "up" and chary > 0:
                        chary -= 1
                    if event.direction == "down" and chary < 7:
                        chary += 1
                    if event.direction == "left" and charx > 0:
                        charx -= 1
                    if event.direction == "right" and charx < 7:
                        charx += 1

            player = [charx, chary]

            #control if the player get the coin and increments count
            if player == coin:
                coin = treasure(path3, y)
                count += 1
                break

            sense.set_pixel(charx, chary, b)

            sleep(0.2)
    #say how many coins you have collected
    coin_count(victory, count)


stop = True

while stop:
    #creating a dictionary with the element that are like "feed_key_1":"1" if the botton is pressed else "feed_key_1":"0"
    status_dict = dashboard_status(feeds_keys)

    # start the tutorial and level 1
    if status_dict[feeds_keys[0]] == '1':

        mixer.init()
        mixer.music.load('tutorial1.mp3')
        mixer.music.play()
        while mixer.music.get_busy() == True:
            pass
        level_1(x, b, r, g, charx, chary, path1, victory)

    # start the tutorial and level 2
    elif status_dict[feeds_keys[1]] == '1':

        mixer.init()
        mixer.music.load('tutorial2.mp3')
        mixer.music.play()
        while mixer.music.get_busy() == True:
            pass
        level_2(x, b, g, charx, chary, paths2, victory)

    #start the tutorial and level 3
    elif status_dict[feeds_keys[2]] == '1':

        mixer.init()
        mixer.music.load('tutorial3.mp3')
        mixer.music.play()
        while mixer.music.get_busy() == True:
            pass
        level_3(y, b, charx, chary, path3, victory)

    #if the user press the middle botton of the joystick the game end and say good bye
    for event in sense.stick.get_events():
        if event.action == "pressed":
            if event.direction == "middle":
                mixer.init()
                mixer.music.load('bye.mp3')
                mixer.music.play()
                while mixer.music.get_busy() == True:
                    pass
                stop = False