from desktopmagic.screengrab_win32 import getDisplaysAsImages
from time import time
import colorgram
import utility


# Return avg color of all pixels and ratio of dark pixels for a given image
def img_avg(img):
    low_threshold = 10
    mid_threshold = 40
    high_threshold = 250
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
        if red < low_threshold and green < low_threshold and blue < low_threshold:
            dark_pixels += 1
        # Or too light
        elif red > high_threshold and green > high_threshold and blue > high_threshold:
            pass
        else:
            if red < mid_threshold and green < mid_threshold and blue < mid_threshold:
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
        if item <= low_threshold:
            rgb[index] = low_threshold

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
        colors = colorgram.extract(img, 6)
        if _screen.color_mode == 'dominant':
            screen_data['rgb'] = get_dominant_color(colors)

    end = time()
    elapsed = end - start
    print 'Time elapsed: %.2f' % elapsed

    return screen_data


def get_dominant_color(colors):
    neutral_threshold = 10
    index = 0

    # Get first color that isn't neutral
    for color in colors:
        # print 'COLOR: rgb %d %d %d | PROPORTION: %s' % (color.rgb[0], color.rgb[1], color.rgb[2], str(color.proportion * 100))
        r_g_abs = abs(color.rgb[0] - color.rgb[1])
        g_b_abs = abs(color.rgb[1] - color.rgb[2])
        r_b_abs = abs(color.rgb[0] - color.rgb[2])

        if r_g_abs < neutral_threshold or g_b_abs < neutral_threshold or r_b_abs < neutral_threshold:
            index += 1
        else:
            break

    try:
        color = colors[index].rgb
    except IndexError:
        print 'No non-neutral colors, going with most prominent color...'
        color = colors[0].rgb
    return color[0], color[1], color[2]
