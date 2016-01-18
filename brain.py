

class Brain:

    def __init__(self):
        self.stack = []

    def push_state(self, state):
        if self.get_state() is not state:
            self.stack.append(state)

    def pop_state(self):
        self.stack.pop()

    def get_state(self):
        if len(self.stack):
            return self.stack[-1]
        else:
            return None

    def update(self):
        s = self.get_state()
        if s:
            s()


# class Agent:

#     def __init__(self):
#         self.brain = Brain()
#         self.brain.push_state(self.state1)
#         self.brain.push_state(self.state2)

#     def state1(self):
#         print("Using state 1")
#         self.brain.pop_state()

#     def state2(self):
#         print("Using state 2")
#         self.brain.pop_state()

#     def update(self):
#         self.brain.update()


# a = Agent()
# a.update()
# a.update()
# # b = Brain()
# # b.update()
# # # b.pop_state()
# # b.update()
