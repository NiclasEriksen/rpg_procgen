import math
import random
from itertools import groupby
# from main import logger

stat_names = dict(
    dmg="Damage",
    hp="Hitpoints",
    mp="Mana",
    sta="Stamina",
    sp="Spellpower",
    str="Strength",
    int="Intelligence",
    agi="Agility",
    crit="Critical Chance",
)


def check_consecutive_letters(s, count):
    l = [[k, len(list(g))] for k, g in groupby(s)]
    for letter in l:
        if letter[1] >= count:
            # print(letter)
            return True
    else:
        return False


def set_duration(anim, duration):
    for f in anim.frames:
        f.duration = duration


def translate_stat(stat):
    try:
        return stat_names[stat]
    except KeyError:
        return stat


def check_out_of_bounds(x, y, max_x, max_y):
    if (x < 0 or x > max_x) or (y < 0 or y > max_y):
        return True
    else:
        return False


def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width//2
    image.anchor_y = image.height//2
    return image


def get_color(r, g, b, a):
    """ converts rgba values of 0 - 255 to the equivalent in 0 - 1 """
    return (r / 255.0, g / 255.0, b / 255.0, a / 255.0)


def lookup_color(name, gl=False, opacity=255):
    try:
        color = {
            'blue': (60, 120, 215, opacity),
            'lblue': (130, 190, 225, opacity),
            'darkblue': (20, 80, 175, opacity),
            'yellow': (205, 175, 89, opacity),
            'red': (230, 70, 35, opacity),
            'darkred': (160, 20, 10, opacity),
            'green': (110, 205, 55, opacity),
            'darkgreen': (60, 155, 25, opacity),
            'grey': (128, 128, 128, opacity),
            'lgrey': (196, 196, 196, opacity),
            'dgrey': (65, 45, 45, opacity),
            'white': (255, 255, 255, opacity),
            'black': (0, 0, 0, opacity),
        }[name]
    except LookupError:
        print("No color specified, returning white")
        color = (255, 255, 255, opacity)

    if gl:
        return get_color(*color)
    else:
        return color


def get_color_scheme_by_type(t):
    schemes = {
        'none': ('lgrey', 'grey', 'dgrey'),
        'fire': ('yellow', 'red', 'dgrey'),
        'electric': ('white', 'lblue', 'dgrey'),
    }
    try:
        color = schemes[t]
    except LookupError:
        print("No scheme for that type, using default.")
        color = schemes['none']

    return color


def create_rectangle(cx, cy, w, h, centered=True):
    if centered:
        rectangle = [
                    cx - w // 2, cy - h // 2,
                    cx - w // 2, cy + h // 2,
                    cx + w // 2, cy + h // 2,
                    cx + w // 2, cy - h // 2,
        ]
    else:
        rectangle = [
            cx, cy,
            cx, cy - h,
            cx + w, cy - h,
            cx + w, cy
        ]
    return rectangle


def create_rect(x, y, w, h):
    return [
        x, y,
        x, y + h,
        x + w, y + h,
        x + w, y
    ]


def check_point_rectangle(px, py, rect):
    if rect[0] <= rect[4]:
        x1, x2 = rect[0], rect[4]
    else:
        x1, x2 = rect[4], rect[0]
    if rect[1] <= rect[5]:
        y1, y2 = rect[1], rect[5]
    else:
        y1, y2 = rect[5], rect[1]
    if px >= x1 and px <= x2:
        if py >= y1 and py <= y2:
            return True
    return False


def check_path(m, grid, new):
    update = False
    if new in m.path:
        if m.path.index(new) > m.point:
            update = True
            # if new == m.targetpoint:
            #     print("Tower placed at targetpoint.")
            #     m.targetpoint = m.currentpoint
            #     m.point -= 1
            #     m.currentpoint = m.lastpoint

    else:
        if m.targetpoint in m.path:
            for p in reversed(m.path):
                if m.path.index(p) >= m.path.index(m.targetpoint):
                    dirs = [[1, 0], [0, 1], [-1, 0], [0, -1]]
                    ddirs = [[1, 1], [1, -1], [-1, 1], [-1, -1]]
                    for dir in dirs:
                        neighbor = (p[0] + dir[0], p[1] + dir[1])
                        if neighbor == new:
                            update = True
                            break
                    for dir in ddirs:
                        neighbor = (p[0] + dir[0], p[1] + dir[1])
                        if neighbor == new:
                            update = True
                            break

    return update


def get_diagonal(grid, x, y):
    diagonal_list = []
    ddirs = [[1, 1], [1, -1], [-1, 1], [-1, -1]]
    for dir in ddirs:
        neighbor = (x + dir[0], y + dir[1])
        if neighbor in grid:
            diagonal_list.append(neighbor)

    return diagonal_list


def get_dist(x1, y1, x2, y2):  # Returns distance between to points
    x = (x1 - x2) * (x1 - x2)
    y = (y1 - y2) * (y1 - y2)
    dist = math.sqrt(x + y)
    return dist


def get_midpoint(p1, p2):
    return (p1[0]+p2[0])/2, (p1[1]+p2[1])/2


def check_range(p1, p2, range):
    if get_dist(*p1, *p2) <= range:
        return True
    else:
        return False


def get_diagonal_of_rect(w, h):
    return math.sqrt((w * w) + (h * h))


def get_angle(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    rads = math.atan2(-dy, dx)
    rads %= 2*math.pi
    return rads


def smooth_in_out(x):
    y = -4 * pow(x, 2) + (4 * x)
    return y


def rotate2d(angle, point, origin):
    """
    A rotation function that rotates a point around a point
    to rotate around the origin use [0,0]
    """
    x = point[0] - origin[0]
    y = point[1] - origin[1]
    newx = (x * math.cos(angle)) - (y * math.sin(angle))
    newy = (x * math.sin(angle)) + (y * math.cos(angle))
    newx += origin[0]
    newy += origin[1]

    return newx, newy


def get_diag_ratio():
    return math.sqrt(2)
