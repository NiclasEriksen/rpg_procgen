from components import *
from utils.ebs import Entity


class Player(Entity):
    def __init__(self, world):
        self.isplayer = IsPlayer()
        self.charname = CharName(name="Player")
        self.sprite = Sprite(world.textures["player"])
        self.batch = Batch("player")

        self.physbody = PhysBody()
        self.position = Position()
        # self.lightsource = LightSource()
        self.staticposition = StaticPosition(x=640, y=360)
        self.movement = Movement()
        self.input = Input()
        self.mousecontrolled = MouseControlled()
        self.keyboardcontrolled = KeyboardControlled()

        self.xp = XP()
        self.level = Level()
        self.hp = HP()
        self.stamina = Stamina()
        self.mana = Mana()
        self.attributes = Attributes()
        self.basestats = BaseStats()
        self.effectivestats = EffectiveStats()
        self.activeeffects = ActiveEffects()
        self.equipment = Equipment()
        self.activeabilities = ActiveAbilities()
        self.passiveabilities = PassiveAbilities()
        self.basicattack = BasicAttack()

        self.focustarget = FocusTarget()
        self.autoattacktarget = AutoAttackTarget()


class Enemy(Entity):
    def __init__(self, world):
        self.charname = CharName()
        self.windowposition = WindowPosition()
        self.physbody = PhysBody()
        self.position = Position()
        self.movement = Movement()
        self.followtarget = FollowTarget()
        self.sprite = Sprite(world.textures["enemy"])
        self.batch = Batch("creatures")
        self.ismob = IsMob()
        self.level = Level()
        self.hp = HP()
        self.basestats = BaseStats()
        self.effectivestats = EffectiveStats()
        self.activeeffects = ActiveEffects()

        self.autoattacktarget = AutoAttackTarget()
        self.lastattacker = LastAttacker()
