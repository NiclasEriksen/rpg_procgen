from components import *
from ai_components import KillPlayer
from utils.ebs import Entity


class Player(Entity):
    def __init__(self, world):
        self.isplayer = IsPlayer()
        self.charname = CharName(name="Player")
        self.gloweffect = GlowEffect(world.textures["player_glow"])
        self.sprite = Sprite(world.textures["player"])
        self.batch = Batch("player")

        self.physbody = PhysBody()
        self.position = Position()
        self.headbobbing = HeadBobbing()
        self.lightsource = LightSource()
        self.pulseanimation = PulseAnimation(self.gloweffect)
        self.staticposition = StaticPosition(x=640, y=360)
        self.movement = Movement()
        self.input = Input()
        self.mousecontrolled = MouseControlled()
        self.keyboardcontrolled = KeyboardControlled()

        self.allegiance = Allegiance()

        self.xp = XP()
        self.level = Level()
        self.hp = HP()
        self.hp.value = 5
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


class Wall(Entity):
    def __init__(self, world):
        self.windowposition = WindowPosition()
        self.position = Position()
        # self.sprite = Sprite(world.textures["wall"])
        # self.batch = Batch("walls")


class BG(Entity):
    def __init__(self, world, img):
        self.windowposition = WindowPosition()
        self.position = Position()
        self.sprite = Sprite(img)
        self.sprite.batchless = True


class FG(Entity):
    def __init__(self, world, img):
        self.windowposition = WindowPosition()
        self.position = Position()
        self.sprite = Sprite(img)
        self.sprite.batchless = True


class Enemy(Entity):
    def __init__(self, world):
        self.charname = CharName(name="Enemy")
        self.windowposition = WindowPosition()
        self.physbody = PhysBody()
        self.position = Position()
        self.movement = Movement()
        self.allegiance = Allegiance(value=1)
        # self.searchingtarget = SearchingTarget()
        # self.followtarget = FollowTarget()
        self.aibehavior = AIBehavior()
        self.aibehavior.set(KillPlayer(self, world))
        self.sprite = Sprite(world.textures["enemy"])
        self.pulseanimation = PulseAnimation(self.sprite)
        self.batch = Batch("enemies")
        self.ismob = IsMob()
        self.level = Level()
        self.hp = HP()
        self.basestats = BaseStats()
        self.effectivestats = EffectiveStats()
        self.activeeffects = ActiveEffects()
        self.basicattack = BasicAttack()

        # self.autoattacktarget = AutoAttackTarget()
        self.lastattacker = LastAttacker()
