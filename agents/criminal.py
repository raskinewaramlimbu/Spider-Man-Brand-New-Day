

from enum import Enum
from agents.base_agent import Agent
from environment import Incident, IncidentType


class CriminalState(Enum):
    WANDERING = "Wandering"
    APPROACHING = "Approaching Target"
    COMMITTING_CRIME = "Committing Crime"
    FLEEING = "Fleeing"


class Criminal(Agent):
    def __init__(self, name, rng=None, gang=None):
        super().__init__(name, rng=rng)
        self.state = CriminalState.WANDERING
        self.target = None
        self.detection_radius = 4
        self.caution = 0.0
        self.times_caught = 0
        self.gang = gang



    def decide_and_act(self, city, civilians, spiderman, monitoring_system):

        spiderman_nearby = self.distance_to(spiderman.position) <= self.detection_radius


        if spiderman_nearby and self.state != CriminalState.FLEEING:
            self.state = CriminalState.FLEEING
            self.target = None

        if self.state == CriminalState.WANDERING:
            self._wander_or_find_target(city, civilians)
        elif self.state == CriminalState.APPROACHING:
            self._approach_target(city)
        elif self.state == CriminalState.COMMITTING_CRIME:
            return self._commit_crime(city, monitoring_system)
        elif self.state == CriminalState.FLEEING:
            self._flee(city, spiderman)

        return None

    def _wander_or_find_target(self, city, civilians):

        candidates = [c for c in civilians if c.alive and not c.is_victim]
        nearby = [c for c in candidates if self.distance_to(c.position) <= 5]


        min_required_distance = 5 - int(self.caution * 3)
        nearby = [c for c in nearby if self.distance_to(c.position) <= max(1, min_required_distance)]

        if nearby:
            self.target = min(nearby, key=lambda c: self.distance_to(c.position))
            self.state = CriminalState.APPROACHING
        else:
            self.random_move(city)

    def _approach_target(self, city):
        if self.target is None or not self.target.alive:
            self.state = CriminalState.WANDERING
            return
        if self.distance_to(self.target.position) <= 1:
            self.state = CriminalState.COMMITTING_CRIME
        else:
            self.move_towards(city, self.target.position)

    def _commit_crime(self, city, monitoring_system):

        if self.target is None or not self.target.alive:
            self.state = CriminalState.WANDERING
            return None

        self.target.is_victim = True

        incident_type = self.rng.choice([IncidentType.THEFT, IncidentType.ROBBERY, IncidentType.ASSAULT])
        severity_ranges = {
            IncidentType.THEFT: (2, 4),
            IncidentType.ROBBERY: (4, 7),
            IncidentType.ASSAULT: (5, 9),
        }
        low, high = severity_ranges[incident_type]
        severity = self.rng.randint(low, high)
        incident = Incident(incident_type, self.position, severity, victim=self.target, culprit=self)
        self.target.request_assistance(monitoring_system, incident)

        self.state = CriminalState.FLEEING
        self.target = None
        return incident

    def _flee(self, city, spiderman):

        x, y = self.position
        sx, sy = spiderman.position
        step_x = 1 if x >= sx else -1
        step_y = 1 if y >= sy else -1
        if not city.move_agent(self, x + step_x, y + step_y):
            self.random_move(city)

        if self.distance_to(spiderman.position) > self.detection_radius + 2:
            self.state = CriminalState.WANDERING



    def record_capture(self):

        self.times_caught += 1
        self.caution = min(1.0, self.caution + 0.25)
        self.detection_radius = min(8, self.detection_radius + 1)


class CriminalGang:


    def __init__(self, name, members=None):
        self.name = name
        self.members = members if members is not None else []
        self.shared_objective_district = None

    def add_member(self, criminal):
        criminal.gang = self
        self.members.append(criminal)

    def choose_shared_objective(self, districts, rng):

        self.shared_objective_district = rng.choice(districts)
        return self.shared_objective_district

    def alert_members_to_flee(self, spotted_by):

        for member in self.members:
            if member is not spotted_by and member.alive:
                member.state = CriminalState.FLEEING
# Fixed stale target bug when criminal is arrested mid-chase
# Fixed stale target bug when criminal is arrested mid-chase
# Fixed stale target bug when criminal is arrested mid-chase
