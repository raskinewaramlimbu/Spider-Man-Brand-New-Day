

import unittest
import random

from environment import City, Incident, IncidentType
from agents.civilian import Civilian
from monitoring import MonitoringSystem


class TestCivilianRiskPerception(unittest.TestCase):
    def setUp(self):
        self.city = City(width=20, height=20, rng=random.Random(1))
        self.civilian = Civilian("Test Civilian", rng=random.Random(1))
        self.city.place_agent(self.civilian, 10, 10)

    def test_fear_increases_when_incident_nearby(self):
        incident = Incident(IncidentType.ASSAULT, (11, 10), severity=5)
        self.civilian.perceive_risk(self.city, [incident])
        self.assertGreater(self.civilian.fear_level, 0.0)

    def test_fear_decreases_over_time_without_danger(self):
        self.civilian.fear_level = 0.5
        self.civilian.perceive_risk(self.city, [])
        self.assertLess(self.civilian.fear_level, 0.5)

    def test_fear_never_exceeds_one(self):
        incident = Incident(IncidentType.ASSAULT, (10, 11), severity=5)
        for _ in range(20):
            self.civilian.perceive_risk(self.city, [incident])
        self.assertLessEqual(self.civilian.fear_level, 1.0)

    def test_far_away_incident_does_not_raise_fear(self):
        incident = Incident(IncidentType.THEFT, (19, 19), severity=5)
        self.civilian.perceive_risk(self.city, [incident])
        self.assertEqual(self.civilian.fear_level, 0.0)


class TestCivilianFleeing(unittest.TestCase):
    def test_scared_civilian_moves_away_from_danger(self):
        city = City(width=20, height=20, rng=random.Random(2))
        civilian = Civilian("Test Civilian", rng=random.Random(2))
        city.place_agent(civilian, 10, 10)
        civilian.fear_level = 0.8

        incident = Incident(IncidentType.ASSAULT, (11, 10), severity=8)
        distance_before = civilian.distance_to(incident.position)
        civilian.decide_move(city, [incident])
        distance_after = civilian.distance_to(incident.position)

        self.assertGreaterEqual(distance_after, distance_before)


class TestCivilianCrowdBehaviour(unittest.TestCase):
    def test_frightened_civilian_raises_fear_of_neighbours(self):
        city = City(width=10, height=10, rng=random.Random(3))
        scared = Civilian("Scared", rng=random.Random(3))
        calm = Civilian("Calm", rng=random.Random(3))
        city.place_agent(scared, 5, 5)
        city.place_agent(calm, 5, 6)

        scared.fear_level = 0.9
        calm.fear_level = 0.0

        scared.share_fear_with_neighbours([scared, calm])
        self.assertGreater(calm.fear_level, 0.0)

    def test_calm_civilian_does_not_spread_fear(self):
        city = City(width=10, height=10, rng=random.Random(4))
        calm1 = Civilian("Calm1", rng=random.Random(4))
        calm2 = Civilian("Calm2", rng=random.Random(4))
        city.place_agent(calm1, 5, 5)
        city.place_agent(calm2, 5, 6)

        calm1.fear_level = 0.1
        calm1.share_fear_with_neighbours([calm1, calm2])
        self.assertEqual(calm2.fear_level, 0.0)


class TestCivilianReporting(unittest.TestCase):
    def test_request_assistance_reports_to_monitoring_system(self):
        monitoring = MonitoringSystem()
        civilian = Civilian("Victim", rng=random.Random(5))
        civilian.position = (0, 0)
        incident = Incident(IncidentType.ROBBERY, (0, 0), severity=6)

        civilian.request_assistance(monitoring, incident)
        self.assertIn(incident, monitoring.reported_incidents)


if __name__ == "__main__":
    unittest.main()
