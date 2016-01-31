import math
import random
from functions import *
from spanning_tree import get_connections
import gridmancer
import numpy as np
from collections import Counter


class DungeonGenerator:

    def __init__(self, logger, config=None):
        self.logger = logger
        self.config = dict(
            roomcount_min=8,
            roomcount_max=16,
            room_min_size=5,
            room_max_size=30,
            dungeon_size=(60, 40),
            treasure_chance=30,
            enemy_chance=70,
            corridor_min_width=1,
            corridor_max_width=2,
            corridor_wide_chance=30,
            attempts_max=200,
        )
        if config:
            for k, v in config.items():
                if k in self.config:
                    self.config[k] = v
                else:
                    self.logger.error(
                        "No such dungeon config item: {0}".format(k)
                    )
        self.rooms = []
        self.corridors = []
        self.grid = []
        self.startroom = None
        self.enemy_rooms = []
        self.collidable = []
        self.pillars = []
        self.collidable_objects = []

    def set_config(self, setting, value):
        if setting in self.config:
            self.config[setting] = value
        else:
            print("No such config item.")

    def check_config(self):
        if self.config["room_max_size"] > self.config["dungeon_size"][0] - 2:
            return False
        elif self.config["room_max_size"] > self.config["dungeon_size"][1] - 2:
            return False

    def get_all_rects(self):
        rects = []
        for r in self.rooms:
            for x in range(r.x1, r.x2):
                for y in range(r.y1, r.y2):
                    rects.append((x, y))
        for c in self.corridors:
            for x in range(c.x1, c.x2 + 1):
                for y in range(c.y1, c.y2 + 1):
                    if not (x, y) in rects:
                        rects.append((x, y))
        for p in self.pillars:
            rects.remove(p)

        return rects

    def get_tilemap(self):
        img_grid = {}

        floor = self.get_all_rects()
        walkable = []
        for f in floor:
            walkable.append((f[0] * 32, f[1] * 32))
        for tile in walkable:
            # if (tile[0], tile[1] - 32) not in walkable:
            #     img_grid[tile] = "floor_bottom"
            # else:
            img_grid[tile] = "floor"

        for p in self.pillars:
            img_grid[(p[0] * 32, p[1] * 32)] = "pillar"

        for o in self.collidable_objects:
            img_grid[(o[0] * 32, o[1] * 32)] = "col_obj"

        walls = []
        for w in self.walls:
            walls.append(w.p1)
        for tile in walls:
            if (
                (tile[0], tile[1] - 32) not in walls and
                (tile[0], tile[1] + 32) not in walls and
                (tile[0] - 32, tile[1]) not in walls and
                (tile[0] + 32, tile[1]) not in walls
            ):
                img_grid[tile] = "wall_s"
            elif (
                (tile[0], tile[1] - 32) not in walls and
                (tile[0], tile[1] + 32) not in walls and
                (tile[0] - 32, tile[1]) not in walls
            ):
                img_grid[tile] = "wall_s_l"
            elif (
                (tile[0], tile[1] - 32) not in walls and
                (tile[0], tile[1] + 32) not in walls and
                (tile[0] + 32, tile[1]) not in walls
            ):
                img_grid[tile] = "wall_s_r"
            elif (
                (tile[0], tile[1] - 32) not in walls and
                (tile[0] + 32, tile[1]) not in walls and
                (tile[0] - 32, tile[1]) not in walls
            ):
                img_grid[tile] = "wall_s_b"
            elif (
                (tile[0], tile[1] + 32) not in walls and
                (tile[0] + 32, tile[1]) not in walls and
                (tile[0] - 32, tile[1]) not in walls
            ):
                img_grid[tile] = "wall_s_t"
            elif (
                (tile[0] - 32, tile[1]) not in walls and
                (tile[0] + 32, tile[1]) not in walls
            ):
                img_grid[tile] = "wall_s_v"
            elif (
                (tile[0], tile[1] - 32) not in walls and
                (tile[0], tile[1] + 32) not in walls
            ):
                img_grid[tile] = "wall_s_h"
            elif (
                (tile[0], tile[1] + 32) not in walls and
                (tile[0] - 32, tile[1]) not in walls
            ):
                img_grid[tile] = "wall_topleft"
            elif (
                (tile[0], tile[1] + 32) not in walls and
                (tile[0] + 32, tile[1]) not in walls
            ):
                img_grid[tile] = "wall_topright"
            elif (
                (tile[0], tile[1] - 32) not in walls and
                (tile[0] - 32, tile[1]) not in walls
            ):
                img_grid[tile] = "wall_bottomleft"
            elif (
                (tile[0], tile[1] - 32) not in walls and
                (tile[0] + 32, tile[1]) not in walls
            ):
                img_grid[tile] = "wall_bottomright"
            elif (tile[0], tile[1] - 32) not in walls:
                img_grid[tile] = "wall_bottom"
            elif (tile[0], tile[1] + 32) not in walls:
                img_grid[tile] = "wall_top"
            elif (tile[0] - 32, tile[1]) not in walls:
                img_grid[tile] = "wall_left"
            elif (tile[0] + 32, tile[1]) not in walls:
                img_grid[tile] = "wall_right"
            else:
                img_grid[tile] = "wall"

        return img_grid

    def generate(self):
        self.flush()
        self.logger.info(
            "Generating dungeon of size {0} by {1} squares...".format(
                self.config["dungeon_size"][0], self.config["dungeon_size"][1]
            )
        )
        self.place_rooms()
        # if len(self.rooms) < self.config["roomcount_min"]:
        #     self.logger.warning("Could not generate enough rooms, retrying.")
        #     self.generate()
        # oldroom = None
        # for r in self.rooms:
        #     if oldroom:
        #         self.connect_rooms(r, oldroom)
        #     oldroom = r

        self.connect_rooms()
        l = [item for sublist in self.connections for item in sublist]
        sl = sorted(Counter(l).items(), key=lambda x: x[::-1])
        self.startroom = self.rooms[sl[0][0]]

        p1 = self.startroom.center
        longest = 0
        endroom = None
        for r in self.rooms:
            l = get_dist(*p1, *r.center)
            if l > longest:
                endroom = r
                longest = l
        self.endroom = endroom

        self.define_rooms()

        self.grid = self.get_all_rects()
        self.generate_walls()

        self.logger.info(
            "Done, {0} rooms added.".format(
                len(self.rooms)
            )
        )

    def define_rooms(self):
        available_rooms = self.rooms.copy()
        # self.startroom = self.rooms[random.randrange(0, len(self.rooms))]
        available_rooms.remove(self.startroom)
        available_rooms.remove(self.endroom)
        # poi.append(POI(*startroom.center))
        while len(available_rooms):
            r = available_rooms[random.randrange(0, len(available_rooms))]
            if random.randint(0, 101) <= self.config["treasure_chance"]:
                for p in self.generate_pillars(r):
                    self.pillars.append(p)
                    self.collidable.append(
                        Collidable(*p)
                    )
            else:
                # newpoi = POI(*r.center)
                self.enemy_rooms.append(r)
            # poi.append(newpoi)
            available_rooms.remove(r)

        for er in self.enemy_rooms:
            er.set_spawn_locations()
        for r in self.rooms:
            for o in self.generate_collidable_objects(r):
                self.collidable_objects.append(o)
                self.collidable.append(
                    Collidable(*o)
                )

    def generate_collidable_objects(self, room):
        w, h = room.w, room.h
        x, y = room.x1, room.y1
        o = []
        for gx in range(x + 1, x + w - 2):
            for gy in range(y + 1, y + h - 2):
                if (
                    not (gx, gy) in self.pillars and
                    not (gx, gy) in room.spawn_locations and
                    not (gx, gy) == self.startroom.center
                ):
                    if not random.randint(0, 60):
                        o.append((gx, gy))

        return o

    def generate_walls(self):
        self.walls = []
        walls = []
        for x in range(0, self.config["dungeon_size"][0]):
            for y in range(0, self.config["dungeon_size"][1]):
                walls.append((x, y))
        for free in self.grid:
            walls.remove(free)
        for p in self.pillars:
            walls.remove(p)
        for w in walls:
            self.walls.append(Wall(w[0], w[1]))

    def generate_wall_grid(self):
        cols, rows = self.config["dungeon_size"]
        # print(cols, rows)
        # print(self.walls)
        array = [[0 for x in range(cols)] for x in range(rows)]
        # print(len(array), len(array[0]))
        for w in self.walls:
            x, y = w.gx, w.gy
            # print(x, y)
            array[y][x] = -1

        # print(array)
        array, rect_count = gridmancer.grid_reduce(grid=array)
        # print("--------")
        # print(array)
        minimal_grid = np.array(array)
        rects = []
        for i in range(rect_count):
            rects.append(np.asarray(np.where(minimal_grid == i + 1)).T.tolist())

        # print(rect_count, len(rects))
        final_sets = []
        for r in rects:
            final_sets.append(
                [
                    (r[0][1], r[0][0]),
                    (r[-1][1], r[-1][0])
                ]
            )
        return final_sets

        # print(minimal_grid)
        # return minimal_grid

    def generate_pillars(self, room):
        w, h = room.w, room.h
        x, y = room.x1, room.y1
        p = []
        if w >= 7 and h >= 9 and not h % 3:
            y_count = h // 3
            for yi in range(0, y_count):
                p.append(
                    (x + 1, y + yi * 3 + 1)
                )
                p.append(
                    (x + w - 2, y + yi * 3 + 1)
                )
        else:
            self.logger.debug("Room not suitable for pillars.")
        return p

    def flush(self):
        self.rooms = []
        self.corridors = []

    def connect_rooms(self):
        roomcenters = []
        for r in self.rooms:
            roomcenters.append(r.center)
        connections = get_connections(roomcenters)
        self.connections = connections

        for c in connections:
            self.connect_two_rooms(self.rooms[c[0]], self.rooms[c[1]])

    def connect_two_rooms(self, r1, r2):
        x1, y1 = r1.center
        x2, y2 = r2.center
        # 50/50 chance of starting horizontal or vertical
        if random.randint(0, 1):
            c1p1 = (x1, y1)
            c1p2 = (x2, y1)
            c2p1 = (x2, y1)
            c2p2 = (x2, y2)
        else:
            c1p1 = (x1, y1)
            c1p2 = (x1, y2)
            c2p1 = (x1, y2)
            c2p2 = (x2, y2)

        w = self.config["corridor_min_width"]
        if not random.randint(0, 2):
            w = self.config["corridor_max_width"]
        c1 = Corridor(c1p1, c1p2, w=w)
        c2 = Corridor(c2p1, c2p2, w=w)
        self.corridors.append(c1)
        self.corridors.append(c2)

    def place_rooms(self):
        min_roomsize = self.config["room_min_size"]
        max_roomsize = self.config["room_max_size"]
        map_width, map_height = self.config["dungeon_size"]
        i = 0
        attempts = 0
        while i < self.config["roomcount_max"]:
            if attempts > self.config["attempts_max"]:
                self.logger.warning("Failed to add more rooms")
                break
            w = random.randrange(min_roomsize, max_roomsize + 1)
            h = random.randrange(min_roomsize, max_roomsize + 1)
            x = random.randrange(0 + 1, map_width - w - 1)
            y = random.randrange(0 + 1, map_height - h - 1)
            newroom = EnemyRoom(x, y, w, h)
            valid = True
            for r in self.rooms:
                if newroom.check_intersect(r):
                    valid = False
                    attempts += 1
                    break
            if valid:
                attempts = 0
                self.rooms.append(newroom)
                i += 1


class Room:

    def __init__(self, x, y, w, h):
        self.x1, self.y1 = x, y
        self.x2, self.y2 = x + w, y + h
        self.w, self.h = w, h
        self.center = (
            math.floor((self.x1 + self.x2) / 2),
            math.floor((self.y1 + self.y2) / 2)
        )
        self.spawn_locations = []

    def check_intersect(self, room):
        if (
            (self.x1 <= room.x2) and
            (self.x2 >= room.x1) and
            (self.y1 <= room.y2) and
            (self.y2 >= room.y1)
        ):
            return True
        else:
            return False


class EnemyRoom(Room):

    def set_spawn_locations(self):
        try:
            amount = random.randrange(1, max(self.w, self.h) // 3)
        except ValueError:
            amount = 1
        points = []
        for i in range(amount):
            p = (
                random.randrange(self.x1 + 1, self.x2 - 1),
                random.randrange(self.y1 + 1, self.y2 - 1)
            )
            if p not in points:
                points.append(p)

        self.spawn_locations = points


class Corridor:

    def __init__(self, p1, p2, w=1):
        if p1[0] > p2[0] or p1[1] > p2[1]:
            self.x1, self.y1 = p2
            self.x2, self.y2 = p1
        else:
            self.x1, self.y1 = p1
            self.x2, self.y2 = p2
        if self.x1 == self.x2:
            self.orientation = "v"
            self.x2 += w - 1
        elif self.y1 == self.y2:
            self.orientation = "h"
            self.y2 += w - 1
        else:
            raise Exception("Line has to be straight.")

    def check_intersect(self, structure):
        if (
            (self.x1 <= structure.x2) and
            (self.x2 >= structure.x1) and
            (self.y1 <= structure.y2) and
            (self.y2 >= structure.y1)
        ):
            return True
        else:
            return False


class Collidable:

    def __init__(self, gx, gy):
        x, y = gx * 32, gy * 32
        x1 = x
        y1 = y
        x2 = x + 32
        y2 = y + 32
        self.p1, self.p2 = (x1, y1), (x2, y2)
        self.center = x + 16, y + 16


class Wall(Collidable):

    def __init__(self, gx, gy):
        x, y = gx * 32, gy * 32
        x1 = x
        y1 = y
        x2 = x + 32
        y2 = y + 32
        self.gx, self.gy = gx, gy
        self.p1, self.p2 = (x1, y1), (x2, y2)
        self.center = x + 16, y + 16
        # self.vertices = [
        #     (x1, y1), (x1, y2), (x2, y2), (x2, y1)
        # ]

    # def check_collide(
    #     self, p1, p2, get_direction=False, move_dir=None
    # ):
    #     return check_intersect(
    #         p1, p2, self.p1, self.p2,
    #         get_direction=get_direction, move_dir=move_dir
    #     )

    # def collision_test(p):
    #     center = Point(*p)


    # def check_overshoot(self, p1, p2):
    #     print("Checking overshoot")
    #     sides = create_sidelines(self.p1, self.p2)
    #     move_line = LineString([p1, p2])
    #     lines_crossed = []
    #     for key, line in sides.items():
    #         if move_line.intersection(line):
    #             lines_crossed.append(key)

    #     return lines_crossed


class POI:

    def __init__(self, x, y):
        self.x, self.y = x, y


def check_intersect(
    r1p1, r1p2, r2p1, r2p2, get_direction=False, move_dir=None
):
    if get_direction:
        points = create_middlepoints(r1p1, r1p2)
        rect = create_rect(*r2p1, r2p2[0] - r2p1[0], r2p2[1] - r2p1[1])
        for direction, point in points.items():
            if check_point_rectangle(*point, rect):
                return direction
        else:
            return False
    else:
        if (
            (r1p1[0] <= r2p2[0]) and
            (r1p2[0] >= r2p1[0]) and
            (r1p1[1] <= r2p2[1]) and
            (r1p2[1] >= r2p1[1])
        ):
            return True
        else:
            return False


def create_sidelines(p1, p2):
    return dict(
        left=LineString([p1, (p1[0], p2[1])]),
        top=LineString([(p1[0], p2[1]), p2]),
        right=LineString([p2, (p2[0], p1[1])]),
        bottom=LineString([p1, (p2[0], p1[1])])
    )


def create_middlepoints(p1, p2):
    return dict(
        left=(p1[0], (p1[1] + p2[1]) / 2),
        right=(p2[0], (p1[1] + p2[1]) / 2),
        top=((p1[0] + p2[0]) / 2, p2[1]),
        bottom=((p1[0] + p2[0]) / 2, p1[1])
    )
