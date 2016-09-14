from desktopmagic.screengrab_win32 import getDisplaysAsImages
from time import time
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
        if _screen.mode == 'dominant':
            dominant_color = get_dominant_color(img.getcolors(maxcolors=size[0]*size[1]))
            screen_data['rgb'] = dominant_color

    end = time()
    elapsed = end - start
    print 'Time elapsed: %.2f' % elapsed

    return screen_data


def get_dominant_color(colors):
    low_threshold = 10
    high_threshold = 250

    sorted_colors = sorted(colors, key=lambda tup: tup[0], reverse=True)
    dominant_color = sorted_colors[0][1]
    r = dominant_color[0]
    g = dominant_color[1]
    b = dominant_color[2]

    # Prevent dominant color from being solid white or black
    if len(sorted_colors) > 1:
        if r < low_threshold and g < low_threshold and b < low_threshold:
            dominant_color = sorted_colors[1][1]
        elif r > high_threshold and g > high_threshold and b > high_threshold:
            dominant_color = sorted_colors[1][1]

    return dominant_color
