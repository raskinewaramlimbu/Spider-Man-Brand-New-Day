
from agents.base_agent import Agent


class Civilian(Agent):
    def __init__(self, name, rng=None):
        super().__init__(name, rng=rng)
        self.is_victim = False
        self.fear_level = 0.0
        self.awareness_radius = 3

    def perceive_risk(self, city, active_incidents):

        nearby_danger = False
        for incident in active_incidents:
            if self.distance_to(incident.position) <= self.awareness_radius:
                nearby_danger = True
                break

        if nearby_danger:
            self.fear_level = min(1.0, self.fear_level + 0.3)
        else:
            self.fear_level = max(0.0, self.fear_level - 0.1)

        return nearby_danger

    def share_fear_with_neighbours(self, all_civilians):

        if self.fear_level < 0.6:
            return
        for other in all_civilians:
            if other is self or not other.alive:
                continue
            if self.distance_to(other.position) <= 1:
                other.fear_level = min(1.0, other.fear_level + 0.15)

    def decide_move(self, city, active_incidents):

        if self.fear_level >= 0.4 and active_incidents:
            nearest = min(active_incidents, key=lambda i: self.distance_to(i.position))
            self._flee_from(city, nearest.position)
        else:
            self.random_move(city)

    def _flee_from(self, city, danger_pos):

        x, y = self.position
        dx, dy = danger_pos
        step_x = -1 if dx > x else (1 if dx < x else 0)
        step_y = -1 if dy > y else (1 if dy < y else 0)
        if not city.move_agent(self, x + step_x, y + step_y):
            self.random_move(city)

    def request_assistance(self, monitoring_system, incident):

        monitoring_system.report_incident(incident, reported_by=self)

    def report_incident_seen(self, monitoring_system, incident):

        monitoring_system.report_incident(incident, reported_by=self)
# Fixed civilian panic state not resetting after incident resolves
# Fixed civilian panic state not resetting after incident resolves
