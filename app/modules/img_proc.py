from desktopmagic.screengrab_win32 import getDisplaysAsImages
from time import time
import colorgram
import utility

LOW_THRESHOLD = 10
MID_THRESHOLD = 40
HIGH_THRESHOLD = 145


# Return avg color of all pixels and ratio of dark pixels for a given image
def img_avg(img):
    dark_pixels = 1
    mid_range_pixels = 1
    total_pixels = 1
    r = 1
    g = 1
    b = 1

    # Win version of imgGrab does not contain alpha channel
    if img.mode == 'RGB':
        img.putalpha(0)

    # Create list of pixels
    pixels = list(img.getdata())

    for red, green, blue, alpha in pixels:
        # Don't count pixels that are too dark
        if red < LOW_THRESHOLD and green < LOW_THRESHOLD and blue < LOW_THRESHOLD:
            dark_pixels += 1
        # Or too light
        elif red > HIGH_THRESHOLD and green > HIGH_THRESHOLD and blue > HIGH_THRESHOLD:
            pass
        else:
            if red < MID_THRESHOLD and green < MID_THRESHOLD and blue < MID_THRESHOLD:
                mid_range_pixels += 1
                dark_pixels += 1
            r += red
            g += green
            b += blue
        total_pixels += 1

    n = len(pixels)
    r_avg = r / n
    g_avg = g / n
    b_avg = b / n
    rgb = [r_avg, g_avg, b_avg]

    # If computed average below darkness threshold, set to the threshold
    for index, item in enumerate(rgb):
        if item <= LOW_THRESHOLD:
            rgb[index] = LOW_THRESHOLD

    rgb = (rgb[0], rgb[1], rgb[2])

    data = {
        'rgb': rgb,
        'dark_ratio': float(dark_pixels) / float(total_pixels) * 100
    }
    return data


# Grabs screenshot of current window, calls img_avg (including on zones if present)
def screen_avg(_screen):
    start = time()
    screen_data = {}

    # Grab images of current screens
    imgs = getDisplaysAsImages()
    try:
        img = imgs[int(_screen.display_index)]
    except IndexError as e:
        utility.display_check(_screen)
        img = imgs[int(_screen.display_index)]

    # Resize for performance
    size = (16, 9)
    img = img.resize(size)

    zone_result = []
    if _screen.zone_state:
        for zone in _screen.zones:
            box = (int(zone['x1']), int(zone['y1']), int(zone['x2']), int(zone['y2']))
            part_img = img.copy().crop(box)
            part_data = img_avg(part_img)
            part_data['bulbs'] = zone['bulbs']
            zone_result.append(part_data)
        screen_data['zones'] = zone_result
    else:
        screen_data = img_avg(img)
        if _screen.color_mode != 'average':
            colors = colorgram.extract(img, 6)
            screen_data['rgb'] = choose_color(colors, _screen.color_mode)

    end = time()
    elapsed = end - start
    print 'Time elapsed: %.2f' % elapsed

    return screen_data


def choose_color(colors, sort_type):
    index = 0
    if sort_type == 'hue':
        colors = sorted(colors, key=lambda c: c.hsl.h, reverse=True)

    for color in colors:
        # print 'COLOR: rgb %d %d %d | PROPORTION: %s | HSL : %s' % (color.rgb[0], color.rgb[1], color.rgb[2], str(color.proportion * 100), color.hsl)
        if not threshold_check(color.rgb)['test']:
            index += 1
            continue
    try:
        color = colors[index].rgb
    except IndexError:
        color = colors[0].rgb

    color = threshold_check(color)['color']
    return color[0], color[1], color[2]


def threshold_check(color):
    r = color[0]
    g = color[1]
    b = color[2]
    test = True

    if r < LOW_THRESHOLD and g < LOW_THRESHOLD and b < LOW_THRESHOLD:
        test = False
        color = LOW_THRESHOLD, LOW_THRESHOLD, LOW_THRESHOLD
    elif r > HIGH_THRESHOLD and g > HIGH_THRESHOLD and b > HIGH_THRESHOLD:
        test = False
        color = HIGH_THRESHOLD, HIGH_THRESHOLD, HIGH_THRESHOLD

    return {
        'test': test,
        'color': color
    }


def get_monitor_screenshots():
    return getDisplaysAsImages()
