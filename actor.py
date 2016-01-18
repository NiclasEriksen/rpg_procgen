from brain import Brain
from functions import get_dist
from random import randrange
from dungeon_generator import Collidable


class Actor:

    def __init__(self):
        self.brain = Brain()
        self.max_velocity = 800
        self.move_target = None
        self.attack_target = None
        self.brain.push_state(self.ai_idle)

    def remove_body(self):
        try:
            for s in self.body.shapes:
                self.game.space.remove(s)
            self.game.space.remove(self.body)
        except:
            print("Something fucky with physics.")

    def ai_wander(self):
        if self.body:
            self.body.apply_impulse(
                (randrange(-2500, 2500), randrange(-2500, 2500))
            )
            self.brain.pop_state()

    def ai_move_to_target(self, *args, **kwargs):
        if self.move_target:
            d = get_dist(
                self.move_target.x,
                self.move_target.y,
                self.x,
                self.y
            )
            if d > self.get_stat("arng"):
                line_of_sight = True
                line = (
                    (self.x, self.y), (self.move_target.x, self.move_target.y)
                )
                raycast_objects = self.game.spatial_hash.get_objects_from_line(
                    *line,
                    type=Collidable
                )
                for o in raycast_objects:
                    for s in o.body.shapes:
                        if s.segment_query(*line):
                            line_of_sight = False
                            break
                if line_of_sight:
                    velx = self.move_target.x - self.x
                    vely = self.move_target.y - self.y
                    self.body.velocity.x += velx / 10
                    self.body.velocity.y += vely / 10
                else:
                    self.brain.pop_state()
            else:
                self.brain.pop_state()
        else:
            self.brain.pop_state()

    def ai_feared(self, *args, **kwargs):
        pass

    def ai_attack(self):
        if self.attack_target:
            d = get_dist(
                self.attack_target.x,
                self.attack_target.y,
                self.x,
                self.y
            )
            if d < 40:
                pass
            else:
                self.move_target = self.attack_target
                self.brain.push_state(self.ai_move_to_target)
        else:
            self.brain.pop_state()

    def ai_idle(self):
        if self.game.player:
            d = get_dist(
                self.game.player.x,
                self.game.player.y,
                self.x,
                self.y
            )
            if d <= 100:
                self.attack_target = self.game.player
                self.brain.push_state(self.ai_attack)
