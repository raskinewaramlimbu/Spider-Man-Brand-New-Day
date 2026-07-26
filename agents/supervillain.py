

from environment import Incident, IncidentType
from agents.base_agent import Agent


class Supervillain(Agent):


    def __init__(self, name, rng=None, health=100):
        super().__init__(name, rng=rng)
        self.health = health
        self.max_health = health
        self.times_fought = 0
        self.defeated = False

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        self.times_fought += 1
        if self.health <= 0:
            self.defeated = True
            self.alive = False

    def create_incident(self, incident_type=IncidentType.SUPERVILLAIN_ATTACK, severity=None):
        severity = severity if severity is not None else self.rng.randint(7, 10)
        incident = Incident(incident_type, self.position, severity, culprit=self)
        return incident

    def act(self, city, spiderman, monitoring_system):

        raise NotImplementedError


class GreenGoblin(Supervillain):


    def __init__(self, rng=None):
        super().__init__("Green Goblin", rng=rng, health=120)
        self.attack_cooldown = 0

    def act(self, city, spiderman, monitoring_system):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        distance = self.distance_to(spiderman.position)
        if distance <= 1 and self.attack_cooldown == 0:
            self.attack_cooldown = 3
            incident = self.create_incident(severity=self.rng.randint(8, 10))
            monitoring_system.report_incident(incident, reported_by=None)
            return incident

        self.move_towards(city, spiderman.position)
        return None

    def react_to_damage(self):

        self.attack_cooldown = max(0, self.attack_cooldown - 1)


class Vulture(Supervillain):


    def __init__(self, rng=None):
        super().__init__("Vulture", rng=rng, health=80)
        self.retreating = False
        self.retreat_target = None

    def act(self, city, spiderman, monitoring_system):
        if self.retreating:
            self._continue_retreat(city)
            return None

        distance = self.distance_to(spiderman.position)
        if distance <= 1:
            incident = self.create_incident(severity=self.rng.randint(6, 9))
            monitoring_system.report_incident(incident, reported_by=None)
            self._begin_retreat(city)
            return incident

        self.move_towards(city, spiderman.position)
        return None

    def _begin_retreat(self, city):
        self.retreating = True
        self.retreat_target = (
            self.rng.randrange(city.width),
            self.rng.randrange(city.height),
        )

    def _continue_retreat(self, city):
        if self.retreat_target is None:
            self.retreating = False
            return
        self.move_towards(city, self.retreat_target)
        if self.distance_to(self.retreat_target) <= 1:
            self.retreating = False

    def react_to_damage(self):

        self.retreating = True


class Mysterio(Supervillain):


    def __init__(self, rng=None):
        super().__init__("Mysterio", rng=rng, health=70)
        self.decoy_cooldown = 0

    def act(self, city, spiderman, monitoring_system):
        if self.decoy_cooldown > 0:
            self.decoy_cooldown -= 1


        distance = self.distance_to(spiderman.position)
        if distance < 4:
            self._move_away_from(city, spiderman.position)
        else:
            self.random_move(city)

        if self.decoy_cooldown == 0:
            self.decoy_cooldown = 15
            decoy_x = self.rng.randrange(city.width)
            decoy_y = self.rng.randrange(city.height)
            incident = Incident(
                IncidentType.HOSTAGE, (decoy_x, decoy_y),
                severity=self.rng.randint(6, 9), culprit=self,
            )
            monitoring_system.report_incident(incident, reported_by=None, is_decoy=True)
            return incident
        return None

    def _move_away_from(self, city, threat_pos):
        x, y = self.position
        tx, ty = threat_pos
        step_x = -1 if tx > x else (1 if tx < x else 0)
        step_y = -1 if ty > y else (1 if ty < y else 0)
        if not city.move_agent(self, x + step_x, y + step_y):
            self.random_move(city)

    def react_to_damage(self):

        self.decoy_cooldown = max(0, self.decoy_cooldown - 5)
