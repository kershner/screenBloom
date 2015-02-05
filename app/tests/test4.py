from PIL import ImageGrab
from datetime import datetime
import colorsys
from rgb_cie import Converter
import time


def tup_to_hex(rgb_tuple):
    """ Convert an (R, G, B) tuple to #RRGGBB """
    hexcolor = '#%02x%02x%02x' % rgb_tuple

    return hexcolor


def screen_avg():
    """ Grabs screenshot of current window, returns avg color values of all pixels """
    # print 'Firing screen_avg()...'

    # Grab image of current screen
    img = ImageGrab.grab()

    # Resize image so it's faster to process
    size = (32, 32)
    img = img.resize(size)

    # Create list of pixels
    pixels = list(img.getdata())

    black_pixels = 0
    total_pixels = 0
    r = 0
    g = 0
    b = 0
    counter = 0

    # Loop through all pixels
    # loop_start = datetime.now()
    for x in range(len(pixels)):
        try:
            # Ignore really dark pixels
            if pixels[x][0] < 70 and pixels[x][1] < 70 and pixels[x][2] < 70:
                black_pixels += 1
                total_pixels += 1
            # Ignore transparent pixels
            elif pixels[x][3] > 200 / 255:
                r += pixels[x][0]
                g += pixels[x][1]
                b += pixels[x][2]
                total_pixels += 1
        # In case pixel doesn't have an alpha channel
        except IndexError:
            r += pixels[x][0]
            g += pixels[x][1]
            b += pixels[x][2]
            total_pixels += 1

        counter += 1
    # loop_end = datetime.now()
    # loop_time = loop_end - loop_start
    # print 'Loop took %s microseconds' % loop_time.microseconds

    # Compute average RGB values
    try:
        r_avg = r / counter
        g_avg = g / counter
        b_avg = b / counter
    # Will divide by zero if mostly black pixels in image, if so set to default value
    except ZeroDivisionError:
        r_avg = 230
        g_avg = 230
        b_avg = 230

    screen_color = r_avg, g_avg, b_avg
    screen_hex = tup_to_hex(screen_color)
    hue_color = converter.rgbToCIE1931(screen_color[0], screen_color[1], screen_color[2])
    hsv_color = colorsys.rgb_to_hsv((float(r_avg) / 255), (float(g_avg) / 255), (float(b_avg) / 255))
    hsv_color = ('%.1f, %.1f, %.1f' % (hsv_color[0] * 360, hsv_color[1] * 100, hsv_color[2] * 100))

    dark_percent = (float(black_pixels) / float(total_pixels)) * 100
    brightness = 254
    max_brightness = 254
    min_brightness = 50

    if dark_percent >= 40.0:
        brightness -= (dark_percent * max_brightness) / 100
        brightness += 50
        if brightness < min_brightness:
            brightness = min_brightness

    print '\nScreen is %.2f%% dark pixels' % dark_percent
    print 'Current Brightness: %d' % brightness
    data = {
        'screen_color': screen_color,
        'screen_hex': screen_hex,
        'hue_color': hue_color,
        'hsv_color': hsv_color,
        'dark_percent': dark_percent
    }

    return data

converter = Converter()  # Class for easy conversion of RGB to Hue CIE

while True:
    screen_avg()
    time.sleep(1.5)