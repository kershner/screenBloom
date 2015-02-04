from PIL import ImageGrab
from datetime import datetime


def tup_to_hex(rgb_tuple):
    """ Convert an (R, G, B) tuple to #RRGGBB """
    hexcolor = '#%02x%02x%02x' % rgb_tuple

    return hexcolor


def screen_avg():
    func_start = datetime.now()
    img = ImageGrab.grab()
    img_grab_time = datetime.now() - func_start
    size = (32, 32)
    img = img.resize(size)
    pixels = list(img.getdata())
    img.show()

    r = 0
    g = 0
    b = 0
    counter = 0

    # Loop through all pixels
    for x in range(len(pixels)):
        try:
            # Ignore black pixels
            if pixels[x] == (0, 0, 0):
                continue
            # Ignore transparent pixels
            elif pixels[x][3] > 200 / 255:
                r += pixels[x][0]
                g += pixels[x][1]
                b += pixels[x][2]
        # In case pixel has no alpha channel
        except IndexError:
            r += pixels[x][0]
            g += pixels[x][1]
            b += pixels[x][2]

        counter += 1

    try:
        r_avg = r / counter
        g_avg = g / counter
        b_avg = b / counter
    except ZeroDivisionError:
        r_avg = 230
        g_avg = 230
        b_avg = 230

    screen_color = r_avg, g_avg, b_avg
    screen_hex = tup_to_hex(screen_color)

    func_end = datetime.now()
    func_time = func_end - func_start
    print 'ImageGrab took %s microseconds' % img_grab_time.microseconds
    print 'Function took %s microseconds' % func_time.microseconds

    return screen_hex

screen_avg()