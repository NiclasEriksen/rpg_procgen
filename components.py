import pyglet.sprite


class Batch(object):
    def __init__(self, batchname):
        self.batch = batchname


class XP(object):
    def __init__(self):
        self.count = 0
        self.rate = 1


class Level(object):
    def __init__(self):
        self.lvl = 1
        self.lvlup_xp = 30


class IsPlayer(object):
    def __init__(self):
        pass


class IsMob(object):
    def __init__(self):
        pass


class Input(object):
    def __init__(self):
        pass


class KeyboardControl(object):
    def __init__(self):
        pass


class Movement(object):
    def __init__(self):
        self.max_speed = 120
        self.acceleration = 8


class StaticPosition(object):
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y


class CharName(object):
    def __init__(self, name=None):
        self.name = name


class Position(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.old_x, self.old_y = x, y

    def set(self, x, y):
        self.old_x, self.old_y = self.x, self.y
        self.x, self.y = x, y


class WindowPosition(object):
    def __init__(self, x=0, y=0, static=False):
        self.x = x
        self.y = y
        self.static = static


class Velocity(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class Sprite(object):
    def __init__(self, img):
        self.sprite = pyglet.sprite.Sprite(img, subpixel=True)
        self.batchless = False


class PhysBody(object):
    def __init__(self, mass=10, width=24, height=24, shape="circle"):
        self.body = None
        self.mass = mass
        self.width = width
        self.height = height
        self.shape = shape


class HP(object):
    def __init__(self, amount=10):
        self.value = amount


class Stamina(object):
    def __init__(self, amount=10):
        self.value = amount


class Mana(object):
    def __init__(self, amount=10):
        self.value = amount


class LastAttacker(object):
    def __init__(self):
        self.who = None


class AutoAttackTarget(object):
    def __init__(self):
        self.who = None


class FocusTarget(object):
    def __init__(self):
        self.who = None
