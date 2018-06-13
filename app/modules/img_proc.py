from PIL import ImageEnhance, ImageFilter
from config import params
import utility

if params.BUILD == 'win':
    from desktopmagic.screengrab_win32 import getDisplaysAsImages, getRectAsImage
else:
    from PIL import ImageGrab


LOW_THRESHOLD = 20
MID_THRESHOLD = 40
HIGH_THRESHOLD = 160


# Return avg color of all pixels and ratio of dark pixels for a given image
def img_avg(img):
    dark_pixels = 1
    mid_range_pixels = 1
    total_pixels = 1

    # Win version of imgGrab does not contain alpha channel
    if img.mode == 'RGB':
        img.putalpha(0)

    # Create list of pixels
    pixels = list(img.getdata())

    pixels_to_remove = []

    for red, green, blue, alpha in pixels:
        # Don't count pixels that are too dark
        if red < LOW_THRESHOLD and green < LOW_THRESHOLD and blue < LOW_THRESHOLD:
            dark_pixels += 1
            pixels_to_remove.append((red,green,blue,alpha))
        # Or too light
        elif red > HIGH_THRESHOLD and green > HIGH_THRESHOLD and blue > HIGH_THRESHOLD:
            pixels_to_remove.append((red,green,blue,alpha))
            pass
        else:
            if red < MID_THRESHOLD and green < MID_THRESHOLD and blue < MID_THRESHOLD:
                mid_range_pixels += 1
                dark_pixels += 1
        total_pixels += 1

    pixels_to_remove = set(pixels_to_remove)
    for pixel in pixels_to_remove:
        pixels = filter(lambda a: a != pixel, pixels)

    try:
        most_frequent_pixel = Counter(pixels).most_common()[0]
        rgb = (most_frequent_pixel[0][0],most_frequent_pixel[0][1], most_frequent_pixel[0][2])
    except Exception as e:
        rgb = (0,0,0,)

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
    screen_data = {}

    # Win version uses DesktopMagic for multiple displays
    if params.BUILD == 'win':
        try:
            img = getRectAsImage(_screen.bbox)
        except IndexError:
            utility.display_check(_screen)
            img = getRectAsImage(_screen.bbox)
    # Mac version uses standard PIL ImageGrab
    else:
        img = ImageGrab.grab()

    # Resize for performance - this could be a user editable setting
    size = (16, 9)
    img = img.resize(size)

    # Enhance saturation according to user settings
    sat_scale_factor = float(_screen.sat)
    if sat_scale_factor > 1.0:
        sat_converter = ImageEnhance.Color(img)
        img = sat_converter.enhance(sat_scale_factor)

    zone_result = []
    if _screen.zone_state:
        for zone in _screen.zones:
            box = (int(zone['x1']), int(zone['y1']), int(zone['x2']), int(zone['y2']))
            zone_img = img.copy().crop(box)
            zone_data = img_avg(zone_img)
            zone_data['bulbs'] = zone['bulbs']
            zone_result.append(zone_data)

        screen_data['zones'] = zone_result
    else:
        screen_data = img_avg(img)

    return screen_data


def get_monitor_screenshots():
    return getDisplaysAsImages()
