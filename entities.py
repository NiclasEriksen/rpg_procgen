from components import *
from utils.ebs import Entity


class Player(Entity):
    def __init__(self, world):
        self.charname = CharName(name="Player")
        self.physbody = PhysBody()
        self.position = Position()
        self.staticposition = StaticPosition(x=640, y=360)
        self.movement = Movement()
        # self.velocity = Velocity(x=4)
        self.sprite = Sprite(world.textures["player"])
        self.batch = Batch("player")
        self.isplayer = IsPlayer()
        self.input = Input()
        self.xp = XP()
        self.level = Level()
        self.hp = HP()
        self.stamina = Stamina()
        self.mana = Mana()


class Enemy(Entity):
    def __init__(self, world):
        self.charname = CharName()
        self.windowposition = WindowPosition()
        self.physbody = PhysBody()
        self.position = Position()
        self.movement = Movement()
        # self.velocity = Velocity(y=3)
        self.sprite = Sprite(world.textures["enemy"])
        self.batch = Batch("creatures")
        self.ismob = IsMob()
        self.level = Level()
        self.hp = HP()
