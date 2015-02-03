from PIL import ImageGrab
from rgb_cie import Converter
import colorsys


def tup_to_hex(rgb_tuple):
    """ Convert an (R, G, B) tuple to #RRGGBB """
    hexcolor = '#%02x%02x%02x' % rgb_tuple

    return hexcolor


def screen_avg_no_black_white():
    """ Grabs screenshot of current window, returns avg RGB of all pixels """
    # print 'Firing screen_avg()...'
    img = ImageGrab.grab()

    # Grab width and height
    width, height = img.size

    # Make list of all pixels
    pixels = img.load()
    data = []
    # loop_start = datetime.now()
    for x in range(width / 2):
        for y in range(height / 2):
            cpixel = pixels[x, y]
            data.append(cpixel)
    # loop_end = datetime.now()
    # loop_time = loop_end - loop_start
    # print 'First loop took %s microseconds' % loop_time.microseconds

    r = 0
    g = 0
    b = 0
    counter = 0

    # Loop through all pixels
    # loop_start = datetime.now()
    black_pixels = 0
    total_pixles = 0
    white_pixels = 0
    for x in range(len(data)):
        try:
            # Ignore black pixels
            if data[x] == (0, 0, 0):
                black_pixels += 1
                total_pixles += 1
                continue
            # Ignore white pixels
            elif data[x] == (255, 255, 255):
                total_pixles += 1
                white_pixels += 1
            # Ignore transparent pixels
            elif data[x][3] > 200 / 255:
                r += data[x][0]
                g += data[x][1]
                b += data[x][2]
                total_pixles += 1
        except IndexError:
            r += data[x][0]
            g += data[x][1]
            b += data[x][2]
            total_pixles += 1

        counter += 1
    # loop_end = datetime.now()
    # loop_time = loop_end - loop_start
    # print 'Second loop took %s microseconds' % loop_time.microseconds

    # Compute average RGB values
    r_avg = r / counter
    g_avg = g / counter
    b_avg = b / counter

    screen_color = r_avg, g_avg, b_avg
    screen_hex = tup_to_hex(screen_color)
    hue_color = converter.rgbToCIE1931(screen_color[0], screen_color[1], screen_color[2])
    hsv_color = colorsys.rgb_to_hsv((float(r_avg) / 255), (float(g_avg) / 255), (float(b_avg) / 255))
    hsv_color = ('%.1f, %.1f, %.1f' % (hsv_color[0] * 360, hsv_color[1] * 100, hsv_color[2] * 100))

    print 'Black Pixels: ', black_pixels
    print 'White Pixels: ', white_pixels
    print 'Total Pixels: ', total_pixles
    data = {
        'screen_color': screen_color,
        'screen_hex': screen_hex,
        'hue_color': hue_color,
        'hsv_color': hsv_color
    }

    return data


def screen_avg_luma():
    """ Grabs screenshot of current window, returns avg RGB of all pixels """
    # print 'Firing screen_avg()...'
    img = ImageGrab.grab()

    # Grab width and height
    width, height = img.size

    # Make list of all pixels
    pixels = img.load()
    data = []
    # loop_start = datetime.now()
    for x in range(width / 2):
        for y in range(height / 2):
            cpixel = pixels[x, y]
            data.append(cpixel)
    # loop_end = datetime.now()
    # loop_time = loop_end - loop_start
    # print 'First loop took %s microseconds' % loop_time.microseconds

    r = 0
    g = 0
    b = 0
    counter = 0
    too_dark = 0

    # Loop through all pixels
    # If alpha is greater than 200/255 (non-transparent), add it to the average
    # loop_start = datetime.now()
    for x in range(len(data)):
        # Luma coefficient for brightness
        luma = 0.2126 * data[x][0] + 0.7152 * data[x][1] + 0.0722 * data[x][2]
        try:
            if luma < 9:
                too_dark += 1
                continue
            elif data[x][3] > 200 / 255:
                r += data[x][0]
                g += data[x][1]
                b += data[x][2]
        except IndexError:
            if luma < 9:
                too_dark += 1
                continue
            else:
                r += data[x][0]
                g += data[x][1]
                b += data[x][2]

        counter += 1
    # loop_end = datetime.now()
    # loop_time = loop_end - loop_start
    # print 'Second loop took %s microseconds' % loop_time.microseconds

    # Compute average RGB values
    r_avg = r / counter
    g_avg = g / counter
    b_avg = b / counter

    screen_color = r_avg, g_avg, b_avg
    screen_hex = tup_to_hex(screen_color)
    hue_color = converter.rgbToCIE1931(screen_color[0], screen_color[1], screen_color[2])
    hsv_color = colorsys.rgb_to_hsv((float(r_avg) / 255), (float(g_avg) / 255), (float(b_avg) / 255))
    hsv_color = ('%.1f, %.1f, %.1f' % (hsv_color[0] * 360, hsv_color[1] * 100, hsv_color[2] * 100))

    print 'Pixels which are too dark: ', too_dark
    data = {
        'screen_color': screen_color,
        'screen_hex': screen_hex,
        'hue_color': hue_color,
        'hsv_color': hsv_color
    }

    return data


def screen_avg():
    """ Grabs screenshot of current window, returns avg RGB of all pixels """
    # print 'Firing screen_avg()...'
    img = ImageGrab.grab()

    # Grab width and height
    width, height = img.size

    # Make list of all pixels
    pixels = img.load()
    data = []
    # loop_start = datetime.now()
    for x in range(width / 2):
        for y in range(height / 2):
            cpixel = pixels[x, y]
            data.append(cpixel)
    # loop_end = datetime.now()
    # loop_time = loop_end - loop_start
    # print 'First loop took %s microseconds' % loop_time.microseconds

    r = 0
    g = 0
    b = 0
    counter = 0

    # Loop through all pixels
    # If alpha is greater than 200/255 (non-transparent), add it to the average
    # loop_start = datetime.now()
    for x in range(len(data)):
        try:
            if data[x][3] > 200 / 255:
                r += data[x][0]
                g += data[x][1]
                b += data[x][2]
        except IndexError:
            r += data[x][0]
            g += data[x][1]
            b += data[x][2]

        counter += 1
    # loop_end = datetime.now()
    # loop_time = loop_end - loop_start
    # print 'Second loop took %s microseconds' % loop_time.microseconds

    # Compute average RGB values
    r_avg = r / counter
    g_avg = g / counter
    b_avg = b / counter

    screen_color = r_avg, g_avg, b_avg
    screen_hex = tup_to_hex(screen_color)
    hue_color = converter.rgbToCIE1931(screen_color[0], screen_color[1], screen_color[2])
    hsv_color = colorsys.rgb_to_hsv((float(r_avg) / 255), (float(g_avg) / 255), (float(b_avg) / 255))
    hsv_color = ('%.1f, %.1f, %.1f' % (hsv_color[0] * 360, hsv_color[1] * 100, hsv_color[2] * 100))

    data = {
        'screen_color': screen_color,
        'screen_hex': screen_hex,
        'hue_color': hue_color,
        'hsv_color': hsv_color
    }

    return data

converter = Converter()

values = screen_avg()
values_2 = screen_avg_no_black_white()
values_3 = screen_avg_luma()
print 'Normal run: ', values['screen_hex']
print 'Black/White pixels removed: ', values_2['screen_hex']
print 'Dim pixels removed: ', values_3['screen_hex']