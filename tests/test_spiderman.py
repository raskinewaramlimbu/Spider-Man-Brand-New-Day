
import unittest
import random

from environment import City, Incident, IncidentType
from agents.spiderman import SpiderMan
from monitoring import MonitoringSystem


class TestSpiderManBasics(unittest.TestCase):
    def setUp(self):
        self.city = City(width=10, height=10, rng=random.Random(1))
        self.spiderman = SpiderMan(rng=random.Random(1))
        self.city.place_agent(self.spiderman, 5, 5)

    def test_starts_at_full_stamina(self):
        self.assertEqual(self.spiderman.stamina, 100.0)

    def test_spend_stamina_reduces_value(self):
        self.spiderman.spend_stamina(20)
        self.assertEqual(self.spiderman.stamina, 80.0)

    def test_stamina_cannot_go_below_zero(self):
        self.spiderman.spend_stamina(500)
        self.assertEqual(self.spiderman.stamina, 0.0)

    def test_rest_increases_stamina_but_not_above_max(self):
        self.spiderman.spend_stamina(10)
        self.spiderman.rest(amount=50)
        self.assertEqual(self.spiderman.stamina, 100.0)

    def test_is_exhausted_below_threshold(self):
        self.spiderman.stamina = 5
        self.assertTrue(self.spiderman.is_exhausted())
        self.spiderman.stamina = 50
        self.assertFalse(self.spiderman.is_exhausted())


class TestSpiderManDetection(unittest.TestCase):
    def setUp(self):
        self.city = City(width=20, height=20, rng=random.Random(2))
        self.spiderman = SpiderMan(rng=random.Random(2))
        self.city.place_agent(self.spiderman, 10, 10)
        self.monitoring = MonitoringSystem()

    def test_detects_nearby_incident(self):
        incident = Incident(IncidentType.THEFT, (11, 10), severity=3)
        self.monitoring.report_incident(incident)
        detected = self.spiderman.detect_incidents(self.monitoring)
        self.assertIn(incident, detected)

    def test_does_not_detect_far_low_severity_incident(self):
        incident = Incident(IncidentType.THEFT, (19, 19), severity=3)
        self.monitoring.report_incident(incident)
        detected = self.spiderman.detect_incidents(self.monitoring)
        self.assertNotIn(incident, detected)

    def test_always_detects_high_severity_incident_regardless_of_distance(self):
        incident = Incident(IncidentType.SUPERVILLAIN_ATTACK, (19, 19), severity=9)
        self.monitoring.report_incident(incident)
        detected = self.spiderman.detect_incidents(self.monitoring)
        self.assertIn(incident, detected)


class TestSpiderManUtilitySelection(unittest.TestCase):
    def setUp(self):
        self.city = City(width=20, height=20, rng=random.Random(3))
        self.spiderman = SpiderMan(rng=random.Random(3))
        self.city.place_agent(self.spiderman, 10, 10)

    def test_selects_higher_severity_incident_when_distance_equal(self):
        low = Incident(IncidentType.THEFT, (11, 10), severity=2)
        high = Incident(IncidentType.ASSAULT, (10, 11), severity=9)
        chosen = self.spiderman.select_incident([low, high])
        self.assertIs(chosen, high)

    def test_prefers_closer_incident_when_severity_similar(self):
        near = Incident(IncidentType.THEFT, (11, 10), severity=5)
        far = Incident(IncidentType.THEFT, (18, 10), severity=5)
        chosen = self.spiderman.select_incident([near, far])
        self.assertIs(chosen, near)

    def test_select_incident_returns_none_for_empty_list(self):
        self.assertIsNone(self.spiderman.select_incident([]))

    def test_preferred_type_can_change_the_outcome(self):
        theft = Incident(IncidentType.THEFT, (11, 10), severity=5)
        assault = Incident(IncidentType.ASSAULT, (11, 10), severity=5)
        chosen = self.spiderman.select_incident([theft, assault], preferred_type="Theft")
        self.assertIs(chosen, theft)


class TestSpiderManMemory(unittest.TestCase):
    def test_remember_stores_threat_and_updates_district_counts(self):
        city = City(width=10, height=10, rng=random.Random(4))
        spiderman = SpiderMan(rng=random.Random(4))
        city.place_agent(spiderman, 5, 5)

        incident = Incident(IncidentType.ROBBERY, (5, 6), severity=5)
        spiderman.remember(incident, tick=1, city=city)

        self.assertEqual(len(spiderman.threat_memory), 1)
        district_name = city.get_district_at(5, 6).name
        self.assertEqual(spiderman.district_threat_counts[district_name], 1)

    def test_district_risk_estimate_returns_most_frequent_district(self):
        city = City(width=10, height=10, rng=random.Random(5))
        spiderman = SpiderMan(rng=random.Random(5))
        city.place_agent(spiderman, 5, 5)

        spiderman.district_threat_counts = {"Queens": 5, "Harlem": 1}
        self.assertEqual(spiderman.district_risk_estimate(), "Queens")

    def test_district_risk_estimate_none_when_no_memory(self):
        city = City(width=10, height=10, rng=random.Random(6))
        spiderman = SpiderMan(rng=random.Random(6))
        self.assertIsNone(spiderman.district_risk_estimate())


class TestSpiderManQLearningIntegration(unittest.TestCase):
    def test_learn_from_outcome_updates_q_table(self):
        city = City(width=10, height=10, rng=random.Random(7))
        spiderman = SpiderMan(rng=random.Random(7))
        city.place_agent(spiderman, 5, 5)

        incident = Incident(IncidentType.THEFT, (5, 6), severity=4)
        preferred = spiderman.choose_priority_type([incident], city)
        self.assertIsNotNone(preferred)

        spiderman.learn_from_outcome(reward=5.0, next_incidents=[], city=city)

        self.assertIn(spiderman._last_state, spiderman.brain.q_table)


if __name__ == "__main__":
    unittest.main()
