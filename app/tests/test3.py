from PIL import ImageGrab
from rgb_cie import Converter
import colorsys
from datetime import datetime


def tup_to_hex(rgb_tuple):
    """ Convert an (R, G, B) tuple to #RRGGBB """
    hexcolor = '#%02x%02x%02x' % rgb_tuple

    return hexcolor


def screen_avg():
    """ Grabs screenshot of current window, returns avg color values of all pixels """
    print 'Firing screen_avg()...'

    # Grab image of current screen
    img = ImageGrab.grab()

    # Resize image so it's faster to process
    size = (32, 32)
    img = img.resize(size)

    # Create list of pixels
    pixels = list(img.getdata())

    black_pixels = 0
    total_pixles = 0
    r = 0
    g = 0
    b = 0
    counter = 0

    # Loop through all pixels
    loop_start = datetime.now()
    for x in range(len(pixels)):
        try:
            # Ignore black pixels
            if pixels[x] == (0, 0, 0):
                black_pixels += 1
                total_pixles += 1
                continue
            # Ignore transparent pixels
            elif pixels[x][3] > 200 / 255:
                r += pixels[x][0]
                g += pixels[x][1]
                b += pixels[x][2]
                total_pixles += 1
        # In case pixel doesn't have an alpha channel
        except IndexError:
            r += pixels[x][0]
            g += pixels[x][1]
            b += pixels[x][2]
            total_pixles += 1

        counter += 1
    loop_end = datetime.now()
    loop_time = loop_end - loop_start
    print 'Loop took %s microseconds' % loop_time.microseconds

    # Compute average RGB values
    try:
        r_avg = r / counter
        g_avg = g / counter
        b_avg = b / counter
    # Will divide by zero if lots of black pixels in image, set to default value
    except ZeroDivisionError:
        r_avg = 230
        g_avg = 230
        b_avg = 230

    screen_color = r_avg, g_avg, b_avg
    screen_hex = tup_to_hex(screen_color)
    hue_color = converter.rgbToCIE1931(screen_color[0], screen_color[1], screen_color[2])
    hsv_color = colorsys.rgb_to_hsv((float(r_avg) / 255), (float(g_avg) / 255), (float(b_avg) / 255))
    hsv_color = ('%.1f, %.1f, %.1f' % (hsv_color[0] * 360, hsv_color[1] * 100, hsv_color[2] * 100))

    # print 'Black Pixels: ', black_pixels
    # print 'Total Pixels: ', total_pixles
    data = {
        'screen_color': screen_color,
        'screen_hex': screen_hex,
        'hue_color': hue_color,
        'hsv_color': hsv_color
    }

    return data

converter = Converter()  # Class for easy conversion of RGB to Hue CIE

loop_counter = 0
while loop_counter < 10:
    result = screen_avg()
    print result['screen_hex']
    loop_counter += 1