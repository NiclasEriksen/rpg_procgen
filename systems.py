from components import *
from utils.ebs import Applicator, System
import pyglet.graphics
from pyglet.window import key
from pymunk import Body as pymunk_body
from pymunk import Circle as pymunk_circle
from pymunk import moment_for_circle


class MoveSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (Position, Velocity)

    def process(self, world, componentsets):
        # print(*componentsets)
        for pos, vel, *rest in componentsets:
            pos.set(
                pos.x + vel.x * world.dt,
                pos.y + vel.y * world.dt
            )


class RenderSystem(System):
    def __init__(self, world):
        self.componenttypes = (Sprite,)

    def process(self, world, components):
        world.window.clear()
        for k, v in world.batches.items():
            v.draw()
        for s in components:
            if s.batchless:
                s.draw()


class MobNamingSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (CharName, IsMob)

    def process(self, world, sets):
        for n, *rest in sets:
            if not n.name:
                n.name = "Enemy"


class SpritePosSystem(Applicator):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (Sprite, WindowPosition)

    def process(self, world, sets):
        for s, pos in sets:
            # print("sprite: ", s.sprite.x, s.sprite.y)
            if not (s.sprite.x, s.sprite.y) == (pos.x, pos.y):
                s.sprite.x = pos.x
                s.sprite.y = pos.y


class StaticSpritePosSystem(Applicator):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (Position, StaticPosition, Sprite)

    def process(self, world, sets):
        for pos, s_pos, sprite in sets:
            sprite.sprite.x = s_pos.x
            sprite.sprite.y = s_pos.y
            world.window.offset_x += (pos.old_x - pos.x)
            world.window.offset_y += (pos.old_y - pos.y)


class SpriteBatchSystem(Applicator):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (Sprite, Batch)

    def process(self, world, sets):
        for s, b in sets:
            if not s.batchless:
                if not s.sprite.batch:
                    try:
                        s.sprite.batch = world.batches[b.batch]
                    except KeyError:
                        print(
                            "No such batch defined: {0}, creating.".format(
                                b.batch
                            )
                        )
                        world.batches[b.batch] = pyglet.graphics.Batch()
                        s.sprite.batch = world.batches[b.batch]


class PhysicsSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (PhysBody, Position)

    def process(self, world, sets):
        for x in range(10):
            world.phys_space.step(world.dt / 10)
        for b, p in sets:
            if not b.body:
                b.body, shape = self.create_body(b, p)
                world.phys_space.add(b.body, shape)
            else:
                p.set(*b.body.position)

        # Checks if there are any ghost bodies in the physics engine
        if not (
            len(world.get_components(PhysBody)) ==
            len(world.phys_space.bodies)
        ):
            body_checklist = [b.body for b in world.get_components(PhysBody)]
            self.cleanup_bodies(world, body_checklist)

    def create_body(self, b, p):
        if b.shape == "circle":
            inertia = moment_for_circle(b.mass, 0, b.width / 2, (0, 0))
            body = pymunk_body(b.mass, inertia)
            body.position = (p.x, p.y)
            shape = pymunk_circle(body, b.width / 2, (0, 0))
            shape.elasticity = 0.2
            shape.group = 0
        else:
            raise PhysicsError("No method to handle {0}".format(b.shape))
        return body, shape

    def cleanup_bodies(self, world, checklist):
        for body in world.phys_space.bodies:
            if body not in checklist:
                for s in body.shapes:
                    world.phys_space.remove(s)
                world.phys_space.remove(body)
                print("Removed a physical body.")


class WindowPosSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (Position, WindowPosition)

    def process(self, world, sets):
        for pos, wpos in sets:
            wpos.x = pos.x + world.window.offset_x
            wpos.y = pos.y + world.window.offset_y


class InputMovementSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (Input, PhysBody, Movement)

    def process(self, world, sets):
        k = world.input_keys
        for i, b, m in sets:
            if b.body:
                if (
                    abs(b.body.velocity.x) +
                    abs(b.body.velocity.y) <
                    m.max_speed
                ):
                    acc = m.acceleration * m.max_speed * world.dt
                    if k[key.W]:
                        b.body.velocity.y += acc
                    if k[key.S]:
                        b.body.velocity.y -= acc
                    if k[key.A]:
                        b.body.velocity.x -= acc
                    if k[key.D]:
                        b.body.velocity.x += acc


class KeyboardHandling(System):
    def __init__(self, world):
        self.is_applicator = False
        self.componenttypes = (KeyboardControl,)

    def process(self, world, components):
        world.process_keyboard_input()


class LevelUpSystem(Applicator):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (XP, Level)

    def process(self, world, sets):
        for xp, lvl in sets:
            if xp.count >= lvl.lvlup_xp:
                rest = xp.count - lvl.lvlup_xp
                lvl.lvl += 1
                lvl.lvlup_xp = int(lvl.lvlup_xp * 1.25)
                xp.count = rest


class ApplyTargetEffectsSystem(Applicator):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (TargetEffects, EffectTarget)

    def process(self, world, sets):
        pass


class InitializeEffectiveStatsSystem(Applicator):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (BaseStats, EffectiveStats)

    def process(self, world, sets):
        for bs, es in sets:
            if not es.initialized:
                es.type = bs.type.copy()
                es.initialized = True


class ApplyAttributeStatsSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (BaseStats, Attributes, EffectiveStats)

    def process(self, world, sets):
        for bs, a, es in sets:
            if a.updated:
                # Strength modifiers
                es.type["hp_max"] = bs.type["hp_max"] + a.points["str"] * 5
                es.type["dmg"] = bs.type["dmg"] + a.points["str"] * 2
                # Agility modifiers
                es.type["sta_max"] = bs.type["sta_max"] + a.points["agi"] * 5
                es.type["armor"] = bs.type["armor"] + a.points["agi"] * 0.5
                es.type["aspd"] = bs.type["aspd"] + a.points["agi"] * 0.5
                es.type["crit_chance"] = (
                    bs.type["crit_chance"] + a.points["agi"] * 0.2
                )
                # Intelligence modifiers
                es.type["mana_max"] = bs.type["mana_max"] + a.points["int"] * 5
                es.type["sp"] = bs.type["sp"] + a.points["int"] * 2
                es.type["sp_crit_chance"] = (
                    bs.type["sp_crit_chance"] + a.points["int"] * 0.2
                )

                a.updated = False


class ApplyHPSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (EffectiveStats, HP)

    def process(self, world, sets):
        for es, hp in sets:
            hp.max = es.type["hp_max"]


class ApplyStaminaSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (EffectiveStats, Stamina)

    def process(self, world, sets):
        for es, sta in sets:
            sta.max = es.type["sta_max"]


class ApplyManaSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (EffectiveStats, Mana)

    def process(self, world, sets):
        for es, mana in sets:
            mana.max = es.type["mana_max"]


class ApplyBasicAttackSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (EffectiveStats, BasicAttack)

    def process(self, world, sets):
        for es, ba in sets:
            ba.dmg = es.type["dmg"]


class ApplyMovementSpeedSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (EffectiveStats, Movement)

    def process(self, world, sets):
        for es, m in sets:
            m.max_speed = es.type["ms"]
            m.acceleration = m.max_speed / 15


class BaseSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = ()

    def process(self, world, sets):
        pass
