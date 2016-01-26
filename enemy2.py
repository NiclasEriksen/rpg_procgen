from utils.ebs import World, Entity, System
import pyglet


class Enemy(Entity):

    def __init__(self, world, x=0, y=0):
        self.position = Position(x=x, y=y)
        self.windowpos = WindowPos()
        self.sprite = Sprite(world.e_texture, x=x, y=y)
        self.rotation = Rotation()


class Position(object):

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class Rotation(object):

    def __init__(self, angle=0):
        self.angle = angle


class WindowPos(object):

    def __init__(self, x=0, y=0):
        self.x = y
        self.y = y


class Sprite(pyglet.sprite.Sprite):

    def __init__(self, img, x=0, y=0, batch=None):
        super().__init__(img, x=x, y=y, batch=batch, subpixel=True)


class WindowPosSystem(System):

    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (Position, WindowPos)

    def process(self, world, componentsets):
        for pos, wpos in componentsets:
            wpos.x = pos.x + 50
            wpos.y = pos.y + 50
            print(wpos.x, wpos.y)


class SpritePosSystem(System):

    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (Sprite, WindowPos)

    def process(self, world, sets):
        for sprite, pos in sets:
            sprite.x = pos.x
            sprite.y = pos.y


class SpriteRotationSystem(System):

    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (Sprite, Rotation)

    def process(self, world, sets):
        for sprite, rotation in sets:
            if not sprite.rotation == rotation.angle:
                sprite.rotation = rotation.angle


appworld = World()
appworld.e_texture = pyglet.image.load('resources/player.png')

e1 = Enemy(appworld)
e2 = Enemy(appworld, x=20, y=20)

appworld.add_system(WindowPosSystem(appworld))
appworld.add_system(SpritePosSystem(appworld))
appworld.add_system(SpriteRotationSystem(appworld))

appworld.process()