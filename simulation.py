

import random

from environment import City
from monitoring import MonitoringSystem
from agents.spiderman import SpiderMan
from agents.civilian import Civilian
from agents.criminal import Criminal, CriminalGang
from agents.supervillain import GreenGoblin, Vulture, Mysterio


class Simulation:
    def __init__(self, width=20, height=20, num_civilians=15, num_criminals=6,
                 num_gangs=2, include_supervillains=True, seed=None):
        self.rng = random.Random(seed)
        self.city = City(width, height, num_districts=4, rng=self.rng)
        self.monitoring = MonitoringSystem()

        self.spiderman = SpiderMan(rng=self.rng)
        self.city.place_agent(self.spiderman, *self.city.random_empty_position())

        self.civilians = self._spawn_civilians(num_civilians)
        self.criminals, self.gangs = self._spawn_criminals(num_criminals, num_gangs)
        self.supervillains = self._spawn_supervillains() if include_supervillains else []

        self.tick = 0
        self.history = []



    def _spawn_civilians(self, count):
        civilians = []
        for i in range(count):
            c = Civilian(f"Civilian-{i+1}", rng=self.rng)
            self.city.place_agent(c, *self.city.random_empty_position())
            civilians.append(c)
        return civilians

    def _spawn_criminals(self, count, num_gangs):
        criminals = []
        gangs = [CriminalGang(f"Gang-{g+1}") for g in range(max(1, num_gangs))]

        for i in range(count):
            crim = Criminal(f"Criminal-{i+1}", rng=self.rng)
            self.city.place_agent(crim, *self.city.random_empty_position())
            gang = gangs[i % len(gangs)]
            gang.add_member(crim)
            criminals.append(crim)

        for gang in gangs:
            gang.choose_shared_objective(self.city.districts, self.rng)

        return criminals, gangs

    def _spawn_supervillains(self):
        villains = [GreenGoblin(rng=self.rng), Vulture(rng=self.rng), Mysterio(rng=self.rng)]
        for v in villains:
            self.city.place_agent(v, *self.city.random_empty_position())
        return villains



    def step(self):

        self.tick += 1
        self.city.advance_time()

        self._act_civilians()
        self._act_criminals()
        self._act_supervillains()
        self.city.maybe_generate_incident(self.civilians, self.criminals)
        self._act_spiderman()
        self.spiderman.rest()
        self.monitoring.expire_stale_incidents(self.tick)

        snapshot = self._snapshot()
        self.history.append(snapshot)
        return snapshot

    def run(self, num_ticks):
        for _ in range(num_ticks):
            self.step()
        return self.history



    def _act_civilians(self):
        active = self.city.active_incidents()
        for civilian in self.civilians:
            if not civilian.alive:
                continue
            civilian.perceive_risk(self.city, active)
            civilian.decide_move(self.city, active)
        for civilian in self.civilians:
            civilian.share_fear_with_neighbours(self.civilians)


        for civilian in self.civilians:
            for incident in active:
                if civilian.distance_to(incident.position) <= 2 and incident not in self.monitoring.reported_incidents:
                    civilian.report_incident_seen(self.monitoring, incident)

    def _act_criminals(self):
        for criminal in self.criminals:
            if not criminal.alive:
                continue
            incident = criminal.decide_and_act(self.city, self.civilians, self.spiderman, self.monitoring)
            if incident is not None:
                incident.time_created = self.tick
                self.monitoring.report_incident(incident, reported_by=None, city=self.city, tick=self.tick)
                self.city.incidents.append(incident)
                if criminal.gang:
                    pass


            from agents.criminal import CriminalState
            if criminal.state == CriminalState.FLEEING and criminal.gang:
                criminal.gang.alert_members_to_flee(spotted_by=criminal)

    def _act_supervillains(self):
        for villain in self.supervillains:
            if not villain.alive:
                continue
            incident = villain.act(self.city, self.spiderman, self.monitoring)
            if incident is not None:
                incident.time_created = self.tick
                self.city.incidents.append(incident)

    def _act_spiderman(self):
        detected = self.spiderman.detect_incidents(self.monitoring)

        for incident in detected:
            self.spiderman.remember(incident, self.tick, self.city)

        if not detected:

            self._patrol(risky_district=self.spiderman.district_risk_estimate())
            return

        preferred_type = self.spiderman.choose_priority_type(detected, self.city)
        target_incident = self.spiderman.select_incident(detected, preferred_type=preferred_type)

        if self.spiderman.is_exhausted():

            self.spiderman.learn_from_outcome(reward=-1.0, next_incidents=detected, city=self.city)
            return

        resolved, reward = self.spiderman.respond_to_incident(target_incident, self.monitoring, self.tick)
        if not resolved:
            self.spiderman.move_towards_incident(self.city, target_incident.position)
            reward = -0.2

        remaining = [i for i in detected if not i.resolved]
        self.spiderman.learn_from_outcome(reward=reward, next_incidents=remaining, city=self.city)

    def _patrol(self, risky_district):

        if risky_district is None:
            self.spiderman.random_move(self.city)
            return


        candidates = self.city.cells_in_district(risky_district)
        if not candidates:
            self.spiderman.random_move(self.city)
            return

        target = min(candidates, key=lambda pos: self.spiderman.distance_to(pos))
        if self.spiderman.distance_to(target) == 0:
            self.spiderman.random_move(self.city)
        else:
            self.spiderman.move_towards_incident(self.city, target)



    def _snapshot(self):
        stats = self.monitoring.basic_statistics()
        return {
            "tick": self.tick,
            "active_incidents": stats["active_incidents"],
            "resolved_total": stats["resolved_incidents"],
            "spiderman_stamina": self.spiderman.stamina,
            "rescues": self.spiderman.rescues,
            "arrests": self.spiderman.arrests,
            "villains_defeated": self.spiderman.villains_defeated,
        }

    def final_statistics(self):
        return self.monitoring.basic_statistics()
# Tuned spawn rates and district danger thresholds for balance
# Tuned spawn rates and district danger thresholds for balance
