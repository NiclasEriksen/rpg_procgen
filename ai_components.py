from functions import get_dist
from components import *


class Task(object):
    def __init__(self):
        self._children = []

    def run(self):
        pass

    def add_child(self, c):
        self._children.append(c)


class Selector(Task):
    def __init__(self):
        super().__init__()

    def run(self):
        for c in self._children:
            if c.run():
                return True
        return False


class Sequence(Task):
    def __init__(self):
        super().__init__()

    def run(self):
        for c in self._children:
            if not c.run():
                return False
        return True


class HasTarget(Task):
    def __init__(self, owner, world):
        super().__init__()
        self.o = owner
        self.w = world

    def run(self):
        if getattr(self.o, "attacktarget"):
            return True
        # elif getattr(self.o, "autoattacktarget"):
        #     return True
        else:
            return False


class FindTarget(Task):
    def __init__(self, owner, world):
        super().__init__()
        self.o = owner
        self.w = world

    def run(self):
        if not getattr(self.o, "searchingtarget"):
            self.o.searchingtarget = SearchingTarget()


class AITargetInRange(Task):
    def __init__(self, owner, world):
        super().__init__()
        self.o = owner
        self.w = world

    def run(self):
        if getattr(self.o, "attacktarget"):
            t = self.o.attacktarget.who
            d = get_dist(
                t.position.x, t.position.y,
                self.o.position.x, self.o.position.y
            )
            if d <= 32:
                return True
            else:
                if getattr(self.o, "autoattacktarget"):
                    delattr(self.o, "autoattacktarget")


class AIAttackTarget(Task):
    def __init__(self, owner, world):
        super().__init__()
        self.o = owner
        self.w = world

    def run(self):
        if getattr(self.o, "attacktarget"):
            t = self.o.attacktarget.who
            if getattr(t, "hp"):
                if t.hp.value > 0:
                    self.o.autoattacktarget = AutoAttackTarget(target=t)
                    return True
                else:
                    delattr(self.o, "attacktarget")
                    if getattr(self.o, "autoattacktarget"):
                        delattr(self.o, "autoattacktarget")
            return True


class AIMoveToTarget(Task):
    def __init__(self, owner, world):
        super().__init__()
        self.o = owner
        self.w = world

    def run(self):
        if getattr(self.o, "attacktarget"):
            t = self.o.attacktarget.who
            if not getattr(self.o, "followtarget"):
                self.o.followtarget = FollowTarget()
                self.o.followtarget.who = t
                self.o.followtarget.range = 24
        return False


class AICheckTargetDead(Task):
    def __init__(self, owner, world):
        super().__init__()
        self.o = owner
        self.w = world

    def run(self):
        if getattr(self.o, "attacktarget"):
            if getattr(self.o.attacktarget.who, "hp"):
                if self.o.attacktarget.who.hp.value <= 0:
                    delattr(self.o, "attacktarget")
                    if getattr(self.o, "followtarget"):
                        delattr(self.o, "followtarget")
                    if getattr(self.o, "autoattacktarget"):
                        delattr(self.o, "autoattacktarget")
                    return True


class Inverter(Task):
    def __init__(self, t):
        super().__init__()
        self.add_child(t)

    def run(self):
        for c in self._children:
            return not c.run()


class BehaviorTree:
    def __init__(self):
        self.root = None

    def run(self):
        return self.root.run()


class KillPlayer(BehaviorTree):
    def __init__(self, owner, world):
        super().__init__()
        o, w = owner, world
        root = Sequence()
        # invert = Inverter()
        targ_seq = Sequence()

        hastarget = HasTarget(o, w)
        findtarget = FindTarget(o, w)

        gettarget = Selector()
        gettarget.add_child(hastarget)
        gettarget.add_child(findtarget)

        checkrange = Inverter(AITargetInRange(o, w))
        move_to = AIMoveToTarget(o, w)

        closeenough = Sequence()
        closeenough.add_child(checkrange)
        closeenough.add_child(move_to)

        targ_seq.add_child(gettarget)
        targ_seq.add_child(closeenough)

        root.add_child(targ_seq)

        self.root = root
