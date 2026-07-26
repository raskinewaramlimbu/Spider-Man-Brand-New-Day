

import unittest
import random

from environment import City
from agents.criminal import Criminal, CriminalState, CriminalGang
from agents.civilian import Civilian
from agents.spiderman import SpiderMan
from monitoring import MonitoringSystem


class TestCriminalStateMachine(unittest.TestCase):
    def setUp(self):
        self.city = City(width=20, height=20, rng=random.Random(1))
        self.criminal = Criminal("Test Criminal", rng=random.Random(1))
        self.city.place_agent(self.criminal, 5, 5)
        self.spiderman = SpiderMan(rng=random.Random(1))
        self.city.place_agent(self.spiderman, 18, 18)
        self.monitoring = MonitoringSystem()

    def test_starts_in_wandering_state(self):
        self.assertEqual(self.criminal.state, CriminalState.WANDERING)

    def test_transitions_to_approaching_when_target_found(self):
        civilian = Civilian("Victim", rng=random.Random(1))
        self.city.place_agent(civilian, 6, 5)
        self.criminal.decide_and_act(self.city, [civilian], self.spiderman, self.monitoring)
        self.assertIn(self.criminal.state, (CriminalState.APPROACHING, CriminalState.COMMITTING_CRIME))

    def test_flees_when_spiderman_is_nearby(self):
        self.city.move_agent(self.spiderman, 6, 5)
        civilians = []
        self.criminal.decide_and_act(self.city, civilians, self.spiderman, self.monitoring)
        self.assertEqual(self.criminal.state, CriminalState.FLEEING)

    def test_committing_crime_creates_incident_and_marks_victim(self):
        civilian = Civilian("Victim", rng=random.Random(2))
        self.city.place_agent(civilian, 6, 5)
        self.criminal.state = CriminalState.APPROACHING
        self.criminal.target = civilian


        incident = self.criminal.decide_and_act(self.city, [civilian], self.spiderman, self.monitoring)
        self.assertIsNone(incident)
        self.assertEqual(self.criminal.state, CriminalState.COMMITTING_CRIME)


        incident = self.criminal.decide_and_act(self.city, [civilian], self.spiderman, self.monitoring)
        self.assertIsNotNone(incident)
        self.assertTrue(civilian.is_victim)
        self.assertEqual(self.criminal.state, CriminalState.FLEEING)


class TestCriminalAdaptation(unittest.TestCase):
    def test_record_capture_increases_caution_and_detection_radius(self):
        criminal = Criminal("Test Criminal", rng=random.Random(3))
        initial_caution = criminal.caution
        initial_radius = criminal.detection_radius

        criminal.record_capture()

        self.assertGreater(criminal.caution, initial_caution)
        self.assertGreaterEqual(criminal.detection_radius, initial_radius)
        self.assertEqual(criminal.times_caught, 1)

    def test_caution_never_exceeds_one(self):
        criminal = Criminal("Test Criminal", rng=random.Random(4))
        for _ in range(20):
            criminal.record_capture()
        self.assertLessEqual(criminal.caution, 1.0)


class TestCriminalGang(unittest.TestCase):
    def test_add_member_sets_gang_reference(self):
        gang = CriminalGang("Test Gang")
        criminal = Criminal("Member 1", rng=random.Random(5))
        gang.add_member(criminal)
        self.assertIs(criminal.gang, gang)
        self.assertIn(criminal, gang.members)

    def test_alert_members_to_flee_only_affects_others(self):
        gang = CriminalGang("Test Gang")
        c1 = Criminal("Member 1", rng=random.Random(6))
        c2 = Criminal("Member 2", rng=random.Random(6))
        gang.add_member(c1)
        gang.add_member(c2)

        c1.state = CriminalState.WANDERING
        c2.state = CriminalState.APPROACHING

        gang.alert_members_to_flee(spotted_by=c1)

        self.assertEqual(c1.state, CriminalState.WANDERING)
        self.assertEqual(c2.state, CriminalState.FLEEING)


if __name__ == "__main__":
    unittest.main()
