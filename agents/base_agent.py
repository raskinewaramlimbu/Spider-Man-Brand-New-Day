
import random


class Agent:


    def __init__(self, name, rng=None):
        self.name = name
        self.position = None
        self.rng = rng if rng is not None else random.Random()
        self.alive = True

    def random_move(self, city):

        x, y = self.position
        dx, dy = self.rng.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)])
        city.move_agent(self, x + dx, y + dy)

    def move_towards(self, city, target_pos):

        x, y = self.position
        tx, ty = target_pos
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)


        if dx != 0 and city.move_agent(self, x + dx, y):
            return True
        if dy != 0 and city.move_agent(self, x, y + dy):
            return True
        return self.random_move(city) or True

    def distance_to(self, other_pos):

        x, y = self.position
        ox, oy = other_pos
        return abs(x - ox) + abs(y - oy)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}@{self.position})"
