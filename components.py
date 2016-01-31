import pyglet.sprite


class Batch(object):
    def __init__(self, batchname):
        self.batch = batchname
        self.group = 0

class Attributes(object):
    def __init__(self):
        self.point = {
            "str": 0,
            "agi": 0,
            "int": 0
        }
        self.updated = False


class EffectiveStats(object):
    def __init__(self):
        self.type = {
            "hp_max": 0,
            "sta_max": 0,
            "mana_max": 0,
            "armor": 0,
            "magic_def": 0,
            "ms": 0,
            "dmg": 0,
            "aspd": 0,
            "arng": 0,
            "crit_chance": 0,
            "crit_power": 0,
            "armor_pen": 0,
            "sp": 0,
            "sp_crit_chance": 0,
            "sp_crit_power": 0,
            "sp_pen": 0
        }
        self.initialized = False


class BaseStats(object):
    def __init__(self):
        self.type = {
            "hp_max": 10,
            "sta_max": 10,
            "mana_max": 10,
            "armor": 0,
            "magic_def": 0,
            "ms": 80,
            "dmg": 1,
            "aspd": 30,
            "arng": 40,
            "crit_chance": 0,
            "crit_power": 0,
            "armor_pen": 0,
            "sp": 0,
            "sp_crit_chance": 0,
            "sp_crit_power": 0,
            "sp_pen": 0
        }


class ActiveAbilities(object):
    def __init__(self):
        self.slots = {
            1: None, 2: None,
            3: None, 4: None,
            5: None, 6: None,
            7: None, 8: None,
            9: None, 10: None,
            11: None, 12: None,
            13: None, 14: None,
            15: None, 16: None
        }


class PassiveAbilities(object):
    def __init__(self):
        self.slots = {
            1: None, 2: None,
            3: None, 4: None,
            5: None, 6: None,
            7: None, 8: None,
            9: None, 10: None,
            11: None, 12: None,
            13: None, 14: None,
            15: None, 16: None
        }


class Equipment(object):
    def __init__(self):
        self.slots = {
            "head": None,
            "neck": None,
            "torso": None,
            "shoulders": None,
            "wrists": None,
            "hands": None,
            "legs": None,
            "feet": None,
            "ring1": None,
            "ring2": None,
            "trinket1": None,
            "trinket2": None,
            "mainhand": None,
            "offhand": None
        }
        self.changed = False


class ActiveEffects(object):
    def __init__(self):
        self.buffs = []
        self.debuffs = []


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


class KeyboardControlled(object):
    def __init__(self):
        pass


class MouseControlled(object):
    def __init__(self):
        self.x, self.y = 0, 0


class MouseClicked(object):
    def __init__(self, button, x, y):
        self.button, self.x, self.y = button, x, y
        self.handled = False


class Movement(object):
    def __init__(self):
        self.max_speed = 120
        self.acceleration = self.max_speed / 15


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


class HeadBobbing(object):
    def __init__(self, duration=0.5, amount=3):
        self.max_offset = amount
        self.cur_time = 0
        self.max_time = duration
        self.offset_y = 0
        self.settle = False


class Velocity(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class Sprite(object):
    def __init__(self, img):
        self.sprite = pyglet.sprite.Sprite(img, subpixel=True)
        self.batchless = False


class GlowEffect(object):
    def __init__(self, img):
        self.sprite = pyglet.sprite.Sprite(
            img, subpixel=True
        )
        self.sprite.color = (255, 255, 255)
        self.sprite.opacity = 0
        self.batchless = False


class PulseAnimation(object):
    def __init__(
        self, glow_object, frequency=1,
        max_opacity=1., min_scale=0.8, max_scale=1.2
    ):
        self.owner = glow_object
        self.speed = frequency
        self.scale_min, self.scale_max = min_scale, max_scale
        self.max_opacity = max_opacity
        self.color = glow_object.sprite.color
        self.max_time = frequency
        self.cur_time = 0
        self.settle = False


class PhysBody(object):
    def __init__(self, mass=10, width=24, height=24, shape="circle"):
        self.body = None
        self.mass = mass
        self.width = width
        self.height = height
        self.shape = shape


class HP(object):
    def __init__(self, amount=1):
        self.value = amount
        self.max = amount


class Stamina(object):
    def __init__(self, amount=1):
        self.value = amount
        self.max = amount


class Mana(object):
    def __init__(self, amount=1):
        self.value = amount
        self.max = amount


class LastAttacker(object):
    def __init__(self):
        self.who = None


class AutoAttackTarget(object):
    def __init__(self):
        self.who = None


class FocusTarget(object):
    def __init__(self):
        self.who = None


class TargetEffects(object):
    def __init__(self):
        pass


class EffectTarget(object):
    def __init__(self):
        pass


class BasicAttack(object):
    def __init__(self):
        self.dmg = 1
        self.effects = None


class FollowTarget(object):
    def __init__(self):
        self.who = None
        self.range = 60


class LightSource(object):
    def __init__(self):
        self.intensity = 100
