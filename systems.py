from components import *
from utils.ebs import Applicator, System
import pyglet.graphics
from pyglet.gl import *
from pyglet.window import key
from pymunk import Body as pymunk_body
from pymunk import BB
from pymunk import Circle as pymunk_circle
from pymunk import Poly as pymunk_poly
from pymunk import moment_for_circle
from functions import get_dist, get_angle, smooth_in_out
import math
from timer import Timer
# import aistates


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
        # self.tt = TaskTimer()

    def create_triangles(self, wl, ox, oy):
        # ox, oy = world.window.offset_x, world.window.offset_y
        vertices = []
        for i, l in enumerate(wl):
            x1, y1, x2, y2 = l
            try:
                vertices += [
                    x1 + ox,
                    y1 + oy,
                    x2 + ox,
                    y2 + oy,
                    wl[i+1][2] + ox,
                    wl[i+1][3] + oy,
                ]
            except IndexError:
                vertices += [
                    x1 + ox,
                    y1 + oy,
                    x2 + ox,
                    y2 + oy,
                    wl[0][2] + ox,
                    wl[0][3] + oy,
                ]
        return vertices

    def create_fan(self, wl, ox, oy):
        vertices = []
        start = wl[0]
        end = wl[1]
        vertices += [start[0] + ox, start[1] + oy]
        vertices += [start[2] + ox, start[3] + oy]
        vertices += [end[2] + ox, end[3] + oy]
        for l in wl[2:]:
            vertices += [l[2] + ox, l[3] + oy]
        vertices += [start[2] + ox, start[3] + oy]
        return vertices

    def draw_triangles(self, wl, ox, oy):
        # print(len(self.create_fan(wl, ox, oy)))
        vc = len(wl) * 2 + 4
        # print(vc)
        vertices_gl = (
            GLfloat * vc
        )(*self.create_fan(wl, ox, oy))

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, vertices_gl)
        glColor3f(1, 1, 1)
        glDrawArrays(GL_TRIANGLE_FAN, 0, vc // 2)

    def draw_triangles_2(self, wl, ox, oy):
        vc = len(wl) * 6
        vertices_gl = (
            GLfloat * vc
        )(*self.create_triangles(wl, ox, oy))

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, vertices_gl)
        glColor3f(1, 1, 1)
        glDrawArrays(GL_TRIANGLES, 0, vc // 2)

    # @profile
    def process(self, world, components):
        light = world.cfg["lighting_enabled"]
        ox, oy = world.window.offset_x, world.window.offset_y
        glClearColor(0.2, 0.2, 0.2, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glLoadIdentity()

        if light:
            wl = world.viewlines
            glEnable(GL_STENCIL_TEST)
            glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
            glDepthMask(GL_FALSE)
            glStencilFunc(GL_ALWAYS, 1, 0xFF)
            glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
            glStencilMask(0xFF)
            glClear(GL_STENCIL_BUFFER_BIT)

            # print(len(wl) * 6, len(vertices))
            # vertices = self.create_triangles(wl, ox, oy)
            # vertices_gl = (GLfloat * len(vertices))(*vertices)

            if wl:
                # self.draw_triangles_2(wl, ox, oy)
                self.draw_triangles(wl, ox, oy)

            glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
            glDepthMask(GL_TRUE)
            glStencilMask(0x00)
        glEnable(GL_BLEND)
        glBlendFunc(
            GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
        )
        if light:
            glDisable(GL_STENCIL_TEST)

        # shader.bind()
        for s in components:
            if s.batchless:
                s.sprite.draw()
        for k, v in world.batches.items():
            if k == "enemies":
                if light:
                    glEnable(GL_STENCIL_TEST)
                    glStencilFunc(GL_EQUAL, 1, 0xFF)
                v.draw()
                if light:
                    glDisable(GL_STENCIL_TEST)
            else:
                v.draw()
        # glUseProgram(0)

        # self.draw_triangles()

        if light:
            glEnable(GL_STENCIL_TEST)
            glStencilFunc(GL_EQUAL, 0, 0xFF)
            glColor4f(0.15, 0.10, 0.05, 0.8)
            x1, x2, y1, y2 = world.view_area
            pyglet.graphics.draw(
                4, GL_QUADS,
                ('v2f', [
                    x1, y1, x2, y1, x2, y2, x1, y2
                ])
            )

            glDisable(GL_STENCIL_TEST)
            if world.cfg["show_rays"]:
                glColor4f(1, 1, 1, 0.4)
                iox, ioy = int(ox), int(oy)
                for l in wl:
                    x1, y1, x2, y2 = l
                    pyglet.graphics.draw(
                        2, GL_LINES,
                        ('v2i', (
                            int(x1) + iox,
                            int(y1) + ioy,
                            int(x2) + iox,
                            int(y2) + ioy
                        ))
                    )
        glDisable(GL_BLEND)


class MobNamingSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (CharName, IsMob)

    def process(self, world, sets):
        for n, *rest in sets:
            pass
            # if not n.name:
            #     n.name = "Enemy"


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


class GlowPosSystem(Applicator):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (GlowEffect, Sprite)

    def process(self, world, sets):
        for g, s in sets:
            # print("sprite: ", s.sprite.x, s.sprite.y)
            if not (g.sprite.x, g.sprite.y) == (s.sprite.x, s.sprite.y):
                g.sprite.x = s.sprite.x
                g.sprite.y = s.sprite.y
                g.sprite.image.anchor_x = s.sprite.image.anchor_x
                g.sprite.image.anchor_y = s.sprite.image.anchor_y


class HideSpriteSystem(Applicator):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (Sprite, WindowPosition)

    def process(self, world, sets):
        w_min, w_max, h_min, h_max = world.view_area
        for s, wp in sets:
            if (
                wp.x + s.sprite.width < w_min or
                wp.y + s.sprite.height < h_min or
                wp.x - s.sprite.width > w_max or
                wp.y - s.sprite.height > h_max
            ):
                if s.sprite.visible:
                    # print("Hidden")
                    s.sprite.visible = False
            else:
                if not s.sprite.visible:
                    # print("Shown")
                    s.sprite.visible = True


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


class StaticGlowEffectPosSystem(Applicator):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (GlowEffect, Sprite, StaticPosition)

    def process(self, world, sets):
        for g, s, *rest in sets:
            g.sprite.x = s.sprite.x
            g.sprite.y = s.sprite.y
            g.sprite.image.anchor_x = s.sprite.image.anchor_x
            g.sprite.image.anchor_y = s.sprite.image.anchor_y


class PulseAnimationSystem(Applicator):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (PulseAnimation,)

    def process(self, world, sets):
        dt = world.dt
        for anim, *rest in sets:
            if anim.cur_time < anim.max_time and not anim.settle:
                value = smooth_in_out(
                    anim.cur_time / anim.max_time * 1
                )
                anim.owner.sprite.opacity = value * (anim.max_opacity * 255)
                anim.owner.sprite.scale = anim.scale_min + (
                    value * (anim.scale_max - anim.scale_min)
                )
                anim.cur_time += dt
            else:
                anim.cur_time = 0


class HeadBobbingSystem(Applicator):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (HeadBobbing, Sprite, PhysBody)

    def process(self, world, sets):
        dt = world.dt
        for hb, s, pb in sets:
            if pb.body:
                v = abs(pb.body.velocity.x) + abs(pb.body.velocity.y)
            else:
                v = 0
            if v >= 30:
                hb.settle = False
            else:
                hb.settle = True
            if hb.cur_time < hb.max_time and not hb.settle:
                hb.offset_y = hb.max_offset * smooth_in_out(
                    hb.cur_time / hb.max_time * 1
                )
                hb.cur_time += dt
            else:
                if hb.settle:
                    if hb.offset_y > 0:
                        hb.offset_y -= hb.max_offset * dt * 2
                    else:
                        hb.offset_y = 0
                else:
                    hb.cur_time = 0

            s.sprite.image.anchor_y = 16 - hb.offset_y


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
                        s.sprite.group = pyglet.graphics.OrderedGroup(b.group)


class GlowBatchSystem(Applicator):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (GlowEffect, Batch)

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


# class ApplyGlowEffectSystem(Applicator):
#     def __init__(self, world):
#         self.is_applicator = True
#         self.componenttypes = (GlowEffect,)

#     def process(self, world, sets):
#         for g, *rest in sets:
#             if not g.sprite.opacity == g.opacity:
#                 g.sprite.opacity = g.opacity
#             if not g.sprite.color == g.color:
#                 g.sprite.color = g.color
#             if not g.sprite.scale == g.scale:
#                 g.sprite.scale = g.scale


class PhysicsSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (PhysBody, Position)
        self.interval = 0.1
        self.interval_counter = 0

    def process(self, world, sets):
        for x in range(10):
            world.phys_space.step(world.dt / 5)
        for b, p in sets:
            if not b.body:
                b.body, shape, static = self.create_body(b, p)
                if static:
                    world.phys_space.add(shape)
                else:
                    world.phys_space.add(b.body, shape)
            else:
                p.set(*b.body.position)
                if abs(b.body.velocity.x) + abs(b.body.velocity.y) <= 0.1:
                    b.body.velocity.x = 0
                    b.body.velocity.y = 0

        # Checks if there are any ghost bodies in the physics engine
        if self.interval_counter >= self.interval:
            self.interval_counter = 0
            if not (
                len(world.get_components(PhysBody)) ==
                len(world.phys_space.bodies)
            ):
                body_checklist = [b.body for b in world.get_components(PhysBody)]
                self.cleanup_bodies(world, body_checklist)
        else:
            self.interval_counter += world.dt

    def create_body(self, b, p):
        if b.shape == "circle":
            static = False
            inertia = moment_for_circle(b.mass, 0, b.width / 2, (0, 0))
            body = pymunk_body(b.mass, inertia)
            body.position = (p.x + 0.001, p.y + 0.001)
            shape = pymunk_circle(body, b.width / 2, (0, 0))
            shape.elasticity = 0.2
            shape.group = 0
        elif b.shape == "square":
            static = True
            body = pymunk_body()
            w, h = b.width, b.height
            body.position = p.x, p.y
            box_points = [(0, 0), (0, h), (w, h), (w, 0)]
            shape = pymunk_poly(body, box_points, (0, 0))
        else:
            raise PhysicsError("No method to handle {0}".format(b.shape))
        return body, shape, static

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
            ba.spd = es.type["aspd"]


class CheckDeadSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (HP,)

    def process(self, world, sets):
        for hp, *rest in sets:
            if hp.value <= 0:
                p = world.get_entities(hp)
                print("Killed! {0}".format(p))
                world.delete_entities(p)


class CheckAttackTargetSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (AttackTarget,)

    def process(self, world, sets):
        for at, *rest in sets:
            if at.who not in world.entities:
                o = world.get_entities(at)[0]
                delattr(o, "attacktarget")


class CheckAutoAttackTargetSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (AutoAttackTarget,)

    def process(self, world, sets):
        for at, *rest in sets:
            if at.who not in world.entities:
                o = world.get_entities(at)[0]
                delattr(o, "autoattacktarget")


class CheckFollowTargetSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (FollowTarget,)

    def process(self, world, sets):
        for ft, *rest in sets:
            if ft.who not in world.entities:
                o = world.get_entities(ft)[0]
                delattr(o, "followtarget")


class AutoAttackInRangeSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (AttackTarget,)

    def process(self, world, sets):
        for at, *rest in sets:
            e = world.get_entities(at)[0]
            dist = get_dist(
                e.position.x, e.position.y,
                at.who.position.x, at.who.position.y
            )
            if getattr(e, "autoattacktarget"):
                if dist > 32:
                    delattr(e, "autoattacktarget")
            elif dist <= 32:
                e.autoattacktarget = AutoAttackTarget(target=at.who)


class SearchTargetSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (SearchingTarget, Allegiance)
        self.interval = 0.25
        self.interval_counter = 0

    def process(self, world, sets):
        if self.interval_counter >= self.interval:
            # print("Now!")
            self.interval_counter = 0
            for st, a in sets:
                o = world.get_entities(st)[0]
                pos = getattr(o, "physbody")
                if pos:
                    if pos.body:
                        p1 = pos.body.position.x, pos.body.position.y
                        for tpos, ta in world.combined_components(
                            (PhysBody, Allegiance)
                        ):
                            if not ta.value == a.value:
                                if tpos.body:
                                    p2 = (
                                        tpos.body.position.x,
                                        tpos.body.position.y
                                    )
                                    if get_dist(
                                        *p1, *p2
                                    ) <= 150:
                                        for s in pos.body.shapes:
                                            pos_old = s.group
                                            s.group = 2
                                        for s in tpos.body.shapes:
                                            tpos_old = s.group
                                            s.group = 2

                                        ps = world.phys_space
                                        c = ps.segment_query_first(
                                            p1, p2, group=2
                                        )
                                        for s in pos.body.shapes:
                                            s.group = pos_old
                                        for s in tpos.body.shapes:
                                            s.group = tpos_old
                                        # print(c)
                                        if not c:
                                            t = world.get_entities(tpos)[0]
                                            o.attacktarget = AttackTarget(t)
                                            delattr(o, "searchingtarget")
                                            print("Found target!")
        else:
            self.interval_counter += world.dt


class AutoAttackSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (BasicAttack, AutoAttackTarget)

    def process(self, world, sets):
        for ba, aat in sets:
            if ba.cd <= 0:
                if aat.who:
                    if hasattr(aat.who, "hp"):
                        aat.who.hp.value -= ba.dmg
                        print(aat.who.hp.value)
                        ba.cd = 3 - 3 / 100 * ba.spd
            else:
                ba.cd -= world.dt


class ApplyMovementSpeedSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (EffectiveStats, Movement)

    def process(self, world, sets):
        for es, m in sets:
            m.max_speed = es.type["ms"]
            m.acceleration = m.max_speed / 15


class FollowSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (FollowTarget, Movement, Position, PhysBody)

    def process(self, world, sets):
        for ft, m, p, pb in sets:
            if ft.who and pb.body:
                if (
                    get_dist(
                        ft.who.position.x, ft.who.position.y,
                        p.x, p.y
                    ) > ft.range
                ):
                    velx = ft.who.position.x - p.x
                    vely = ft.who.position.y - p.y
                    pb.body.velocity.x += velx / 10
                    pb.body.velocity.y += vely / 10


class TargetMobSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (IsPlayer, MouseClicked)

    def process(self, world, sets):
        # p = world.get_player()
        enemies = world.combined_components((IsMob, Position))
        # print(enemies)
        for player, mc in sets:
            for e, pos in enemies:
                if (
                    get_dist(
                        mc.x, mc.y,
                        pos.x, pos.y
                    ) <= 32
                ):
                    if mc.button == 1:
                        print("Targeted.")
                    elif mc.button == 4:
                        print("Attack!")
                    mc.handled = True


class CleanupClickSystem(System):
    """Removes mouse clicked objects for all entities."""

    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (MouseClicked,)

    def process(self, world, sets):
        for mc, *rest in sets:
            p = world.get_entities(mc)[0]
            delattr(p, "mouseclicked")
            print("Removed")


class LightingSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (LightSource, PhysBody)
        self.skipframes = 1
        self.counter = 0
        self.old_pos = (0, 0)

    # @profile
    def create_midpoints(self, shapes):
        l = []
        for sd in shapes:
            s = sd["shape"]
            if not isinstance(s, pymunk_circle):
                if not s.group == 2:
                    l += [
                        (s.bb.left, s.bb.bottom),
                        (s.bb.left, s.bb.top),
                        (s.bb.right, s.bb.top),
                        (s.bb.right, s.bb.bottom)
                    ]
            else:
                s.group = 2
        return l

    def move_in_angle(self, a, p, d):
        return p[0] + d*math.cos(a), p[1] + d*math.sin(a)

    def cast_ray(self, phys_space, origin, targets, single=False):
        collisions = []
        view_dist = 500
        a_offset = 0.00001
        col_group = 2
        for target in targets:
            a = -get_angle(*origin, *target)
            c1p = self.move_in_angle(a, origin, view_dist)
            c1 = phys_space.segment_query_first(
                origin, c1p, group=col_group
            )
            if c1:
                hp = c1.get_hit_point()
                collisions.append((hp.x, hp.y, a))
            else:
                collisions.append((c1p[0], c1p[1], a))
            if not single:
                a2 = a - a_offset
                c2p = self.move_in_angle(a2, origin, view_dist)
                # print(pos, mp, c2p)
                c2 = phys_space.segment_query_first(
                    origin, c2p, group=col_group
                )
                a3 = a + a_offset
                c3p = self.move_in_angle(a3, origin, view_dist)
                c3 = phys_space.segment_query_first(
                    origin, c3p, group=col_group
                )
                if c2:
                    hp = c2.get_hit_point()
                    collisions.append((hp.x, hp.y, a2))
                else:
                    collisions.append((*c2p, a2))
                if c3:
                    hp = c3.get_hit_point()
                    collisions.append((hp.x, hp.y, a3))
                else:
                    collisions.append((*c3p, a3))

        return collisions

    def process(self, world, sets):
        if self.counter < self.skipframes:
            self.counter += 1
        else:
            self.counter = 0
            dist = 600
            # world.viewlines = []
            midpoints = []
            collisions = []

            if world.cfg["lighting_enabled"]:
                for ls, pb in sets:
                    pos = (pb.body.position.x, pb.body.position.y)
                    if pos == self.old_pos:
                        # print("OLD")
                        continue
                    else:
                        world.viewlines = []
                        self.old_pos = pos

                    midpoints = self.create_midpoints(
                        world.phys_space.nearest_point_query(
                            pos, dist, group=2
                        )
                    )

                    collisions += self.cast_ray(
                        world.phys_space, pos, midpoints
                    )

                    for s in pb.body.shapes:
                        s.group = 0

                if not world.viewlines:
                    collisions.sort(key=lambda x: x[2], reverse=True)
                    world.viewlines = [(*pos, c[0], c[1]) for c in collisions]


class AIBehaviorSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (AIBehavior,)

    def process(self, world, sets):
        for aib, *rest in sets:
            aib.update()


class Ray:
    def __init__(self, p1, p2):
        self.p1, self.p2 = p1, p2
        self.angle = get_angle(*p1, *p2)


class BaseSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = ()

    def process(self, world, sets):
        pass
