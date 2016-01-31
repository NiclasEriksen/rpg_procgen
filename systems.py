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
from functions import get_dist, get_midpoint, rotate2d, get_angle, smooth_in_out
import math


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
        glClearColor(0.2, 0.2, 0.2, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glLoadIdentity()

        wl = world.viewlines
        if wl:
            glEnable(GL_STENCIL_TEST)
            glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
            glDepthMask(GL_FALSE)
            glStencilFunc(GL_ALWAYS, 1, 0xFF)
            glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
            glStencilMask(0xFF)
            glClear(GL_STENCIL_BUFFER_BIT)

            i = 0
            end = len(world.viewlines) - 1
            vertices = []
            while i <= end:
                if i != end:
                    # vlist = pyglet.graphics.vertex_list(
                    #     3, (
                    #         'v2f',
                    #         [
                    #             wl[i].p1[0] + world.window.offset_x,
                    #             wl[i].p1[1] + world.window.offset_y,
                    #             wl[i].p2[0] + world.window.offset_x,
                    #             wl[i].p2[1] + world.window.offset_y,
                    #             wl[i+1].p2[0] + world.window.offset_x,
                    #             wl[i+1].p2[1] + world.window.offset_y,
                    #         ]
                    #     )
                    # )
                    vertices += [
                        wl[i].p1[0] + world.window.offset_x,
                        wl[i].p1[1] + world.window.offset_y,
                        wl[i].p2[0] + world.window.offset_x,
                        wl[i].p2[1] + world.window.offset_y,
                        wl[i+1].p2[0] + world.window.offset_x,
                        wl[i+1].p2[1] + world.window.offset_y,
                    ]
                else:
                    # vlist = pyglet.graphics.vertex_list(
                    #     3, (
                    #         'v2f',
                    #         [
                    #             wl[i].p1[0] + world.window.offset_x,
                    #             wl[i].p1[1] + world.window.offset_y,
                    #             wl[i].p2[0] + world.window.offset_x,
                    #             wl[i].p2[1] + world.window.offset_y,
                    #             wl[0].p2[0] + world.window.offset_x,
                    #             wl[0].p2[1] + world.window.offset_y,
                    #         ]
                    #     )
                    # )
                    vertices += [
                        wl[i].p1[0] + world.window.offset_x,
                        wl[i].p1[1] + world.window.offset_y,
                        wl[i].p2[0] + world.window.offset_x,
                        wl[i].p2[1] + world.window.offset_y,
                        wl[0].p2[0] + world.window.offset_x,
                        wl[0].p2[1] + world.window.offset_y,
                    ]
                # vlist.draw(GL_TRIANGLES)
                i += 1

            vertices_gl = (GLfloat * len(vertices))(*vertices)
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(2, GL_FLOAT, 0, vertices_gl)
            glColor3f(1, 1, 1)
            glDrawArrays(GL_TRIANGLES, 0, len(vertices) // 2)

            glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
            glDepthMask(GL_TRUE)
            glStencilMask(0x00)
        glEnable(GL_BLEND)
        glBlendFunc(
            GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
        )
        glDisable(GL_STENCIL_TEST)

        # shader.bind()
        for s in components:
            if s.batchless:
                s.sprite.draw()
        for k, v in world.batches.items():
            if k == "enemies":
                if wl:
                    glEnable(GL_STENCIL_TEST)
                    glStencilFunc(GL_EQUAL, 1, 0xFF)
                v.draw()
                if wl:
                    glDisable(GL_STENCIL_TEST)
            else:
                v.draw()
        # glUseProgram(0)

        if wl:
            glEnable(GL_STENCIL_TEST)
            glStencilFunc(GL_EQUAL, 0, 0xFF)
        glColor4f(0.1, 0.1, 0.1, 0.8)
        pyglet.graphics.draw(
            4, GL_QUADS,
            ('v2f', [
                0, 0, 1600, 0, 1600, 1600, 0, 1600
            ])
        )

        glDisable(GL_STENCIL_TEST)
        # glColor4f(1, 1, 1, 1.)
        # for l in wl:
        #     pyglet.graphics.draw(
        #         2, GL_LINES,
        #         ('v2i', (
        #             int(l.p1[0]) + int(world.window.offset_x),
        #             int(l.p1[1]) + int(world.window.offset_y),
        #             int(l.p2[0]) + int(world.window.offset_x),
        #             int(l.p2[1]) + int(world.window.offset_y)
        #         ))
        #     )
        glDisable(GL_BLEND)


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

    def process(self, world, sets):
        for x in range(10):
            world.phys_space.step(world.dt / 10)
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
        if not (
            len(world.get_components(PhysBody)) ==
            len(world.phys_space.bodies)
        ):
            body_checklist = [b.body for b in world.get_components(PhysBody)]
            self.cleanup_bodies(world, body_checklist)

    def create_body(self, b, p):
        if b.shape == "circle":
            static = False
            inertia = moment_for_circle(b.mass, 0, b.width / 2, (0, 0))
            body = pymunk_body(b.mass, inertia)
            body.position = (p.x, p.y)
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

    def create_midpoints(self, bb):
        midpoints = []
        # midpoints.append(
        #     get_midpoint(
        #         (bb.left, bb.top), (bb.left, bb.bottom)
        #     )
        # )
        # midpoints.append(
        #     get_midpoint(
        #         (bb.left, bb.top), (bb.right, bb.top)
        #     )
        # )
        # midpoints.append(
        #     get_midpoint(
        #         (bb.right, bb.top), (bb.right, bb.bottom)
        #     )
        # )
        # midpoints.append(
        #     get_midpoint(
        #         (bb.left, bb.bottom), (bb.right, bb.bottom)
        #     )
        # )
        midpoints.append((bb.left, bb.bottom))
        midpoints.append((bb.left, bb.top))
        midpoints.append((bb.right, bb.top))
        midpoints.append((bb.right, bb.bottom))
        return midpoints

    def move_in_angle(self, a, p, d):
        deltax = d*math.cos(a)
        deltay = d*math.sin(a)
        return p[0] + deltax, p[1] + deltay

    def cast_ray(self, phys_space, origin, target, single=False):
        collisions = []
        view_dist = 500
        a_offset = 0.00001
        col_group = 2
        a = -get_angle(*origin, *target)
        c1p = self.move_in_angle(a, origin, view_dist)
        c1 = phys_space.segment_query_first(
            origin, c1p, group=col_group
        )
        if c1:
            hp = c1.get_hit_point()
            collisions.append((hp.x, hp.y))
        else:
            collisions.append((c1p[0], c1p[1]))
        if not single:
            c2p = self.move_in_angle(a - a_offset, origin, view_dist)
            # print(pos, mp, c2p)
            c2 = phys_space.segment_query_first(
                origin, c2p, group=col_group
            )
            c3p = self.move_in_angle(a + a_offset, origin, view_dist)
            c3 = phys_space.segment_query_first(
                origin, c3p, group=col_group
            )
            if c2:
                hp = c2.get_hit_point()
                collisions.append((hp.x, hp.y))
            else:
                collisions.append((c2p[0], c2p[1]))
            if c3:
                hp = c3.get_hit_point()
                collisions.append((hp.x, hp.y))
            else:
                collisions.append((c3p[0], c3p[1]))

        return collisions

    def process(self, world, sets):
        dist = 520
        world.viewlines = []
        midpoints = []
        collisions = []
        #  world_corners = [(0, 0), (1200, 0), (1200, 1000), (0, 1000)]
        # for wc in world_corners:
        #     midpoints.append(wc)

        # o = (0, 0)
        # p = (10, 10)
        # # a = get_angle(*o, *p)
        # # print(a)
        # p2 = rotate2d(0.1, p, o)
        # p3 = rotate2d(-0.1, p, o)
        # print(p2, p3)

        for ls, pb in sets:
            pos = (pb.body.position.x, pb.body.position.y)
            bb = BB(
                (pos[0] - dist),
                (pos[1] - dist),
                (pos[0] + dist),
                (pos[1] + dist)
            )
            p_shapes = world.phys_space.bb_query(bb)
            for s in pb.body.shapes:
                s.group = 2
                p_shapes.remove(s)
            for s in p_shapes:
                if not isinstance(s, pymunk_circle):
                    if not s.group == 2:
                        mp = self.create_midpoints(s.bb)
                        for p in mp:
                            midpoints.append(p)
                else:
                    s.group = 2
            for mp in midpoints:
                collisions += self.cast_ray(world.phys_space, pos, mp)
            # for mp in world_corners:
            #     collisions += self.cast_ray(
            #         world.phys_space, pos, mp, single=True
            #     )
            for s in pb.body.shapes:
                s.group = 0

            for c in collisions:
                world.viewlines.append(
                    Ray((pos[0], pos[1]), c)
                )
            world.viewlines.sort(key=lambda r: r.angle, reverse=True)
        # for ls, pos in sets:
        # for s in p_shapes:
        # print(collisions)


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
