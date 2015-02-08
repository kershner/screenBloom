from PIL import ImageGrab
from datetime import datetime
# import colorsys
from rgb_cie import Converter
import time


def tup_to_hex(rgb_tuple):
    """ Convert an (R, G, B) tuple to #RRGGBB """
    hexcolor = '#%02x%02x%02x' % rgb_tuple

    return hexcolor


# Return modified Hue brightness value from ratio of dark pixels
def get_brightness(dark_pixel_ratio):
    brightness = 254
    max_brightness = 254
    min_brightness = 150

    if dark_pixel_ratio >= 95.0:
        brightness -= (dark_pixel_ratio * max_brightness) / 100
        if brightness < min_brightness:
            brightness = min_brightness

    return int(brightness)


def screen_avg():
    """ Grabs screenshot of current window, returns avg color values of all pixels """
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

    for x in range(len(pixels)):
        try:
            # Ignore black pixels
            if pixels[x][0] < 50 and pixels[x][1] < 50 and pixels[x][2] < 50:
                black_pixels += 1
                total_pixels += 1
                continue
            # Ignore transparent pixels
            elif pixels[x][3] > 200 / 255:
                r += pixels[x][0]
                g += pixels[x][1]
                b += pixels[x][2]
                total_pixels += 1
        # In case pixel doesn't have an alpha channel
        except IndexError:
            # Ignore black pixels
            if pixels[x][0] < 50 and pixels[x][1] < 50 and pixels[x][2] < 50:
                black_pixels += 1
                total_pixels += 1
                continue
            else:
                r += pixels[x][0]
                g += pixels[x][1]
                b += pixels[x][2]
                total_pixels += 1

        counter += 1

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

    dark_ratio = (float(black_pixels) / float(total_pixels)) * 100
    screen_color = r_avg, g_avg, b_avg
    screen_hex = tup_to_hex(screen_color)
    hue_color = converter.rgbToCIE1931(screen_color[0], screen_color[1], screen_color[2])
    # hsv_color = colorsys.rgb_to_hsv((float(r_avg) / 255), (float(g_avg) / 255), (float(b_avg) / 255))
    # hsv_color = ('%.1f, %.1f, %.1f' % (hsv_color[0] * 360, hsv_color[1] * 100, hsv_color[2] * 100))

    # print 'Black Pixels: ', black_pixels
    # print 'Total Pixels: ', total_pixles
    data = {
        'screen_color': screen_color,
        'screen_hex': screen_hex,
        'hue_color': hue_color,
        # 'hsv_color': hsv_color,
        'dark_ratio': dark_ratio
    }

    return data


# Take 3 snapshots of the screen, average their colors
def screen_avg_avg():
    start = datetime.now()
    colors = []
    dark_ratio = []
    counter = 0
    for x in range(3):
        results = screen_avg()
        colors.append(results['screen_color'])
        dark_ratio.append(results['dark_ratio'])
        counter += 1

    r = 0
    g = 0
    b = 0

    for entry in colors:
        r += entry[0]
        g += entry[1]
        b += entry[2]

    r_avg = r / len(colors)
    g_avg = g / len(colors)
    b_avg = b / len(colors)

    final_color = (r_avg, g_avg, b_avg)
    final_dark_ratio = sum(dark_ratio) / len(dark_ratio)

    data = {
        'final_color': final_color,
        'hex': tup_to_hex(final_color),
        'dark_ratio': final_dark_ratio
    }

    end = datetime.now()
    time_took = start - end
    print 'Function took %s microseconds' % str(time_took.microseconds)

    return data

converter = Converter()  # Class for easy conversion of RGB to Hue CIE

while True:
    final_results = screen_avg_avg()
    current_brightness = get_brightness(final_results['dark_ratio'])
    print '\nCurrent Screen Color: ', final_results['hex']
    print 'Current Brightness: ', current_brightness
    time.sleep(1)