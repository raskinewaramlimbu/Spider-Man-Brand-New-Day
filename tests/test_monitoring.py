
import unittest
import random

from monitoring import MonitoringSystem
from environment import Incident, IncidentType, City


class TestMonitoringBasics(unittest.TestCase):
    def setUp(self):
        self.monitoring = MonitoringSystem()

    def test_report_incident_adds_to_list(self):
        incident = Incident(IncidentType.THEFT, (0, 0), severity=3)
        self.monitoring.report_incident(incident)
        self.assertIn(incident, self.monitoring.reported_incidents)

    def test_get_active_incidents_excludes_resolved(self):
        active = Incident(IncidentType.THEFT, (0, 0), severity=3)
        resolved = Incident(IncidentType.THEFT, (1, 1), severity=3)
        resolved.resolved = True
        self.monitoring.report_incident(active)
        self.monitoring.report_incident(resolved)

        result = self.monitoring.get_active_incidents()
        self.assertIn(active, result)
        self.assertNotIn(resolved, result)

    def test_mark_resolved_sets_flags(self):
        incident = Incident(IncidentType.THEFT, (0, 0), severity=3)
        self.monitoring.report_incident(incident)
        self.monitoring.mark_resolved(incident, tick=10)
        self.assertTrue(incident.resolved)
        self.assertEqual(incident.time_resolved, 10)


class TestMonitoringStatisticsHonesty(unittest.TestCase):


    def test_expired_incidents_are_not_counted_as_resolved(self):
        monitoring = MonitoringSystem()
        incident = Incident(IncidentType.THEFT, (0, 0), severity=3)
        incident.time_created = 0
        monitoring.report_incident(incident)

        monitoring.expire_stale_incidents(current_tick=100, max_age=40)

        stats = monitoring.basic_statistics()
        self.assertEqual(stats["resolved_incidents"], 0)
        self.assertEqual(stats["expired_incidents"], 1)

    def test_genuinely_resolved_incident_is_counted(self):
        monitoring = MonitoringSystem()
        incident = Incident(IncidentType.THEFT, (0, 0), severity=3)
        incident.time_created = 0
        monitoring.report_incident(incident)
        monitoring.mark_resolved(incident, tick=5)

        stats = monitoring.basic_statistics()
        self.assertEqual(stats["resolved_incidents"], 1)
        self.assertEqual(stats["expired_incidents"], 0)

    def test_expire_stale_incidents_only_affects_old_incidents(self):
        monitoring = MonitoringSystem()
        fresh = Incident(IncidentType.THEFT, (0, 0), severity=3)
        fresh.time_created = 95
        monitoring.report_incident(fresh)

        expired_count = monitoring.expire_stale_incidents(current_tick=100, max_age=40)
        self.assertEqual(expired_count, 0)
        self.assertFalse(fresh.resolved)


class TestMonitoringPrioritisation(unittest.TestCase):
    def test_prioritised_incidents_sorted_by_severity_descending(self):
        monitoring = MonitoringSystem()
        low = Incident(IncidentType.THEFT, (0, 0), severity=2)
        high = Incident(IncidentType.ASSAULT, (0, 0), severity=9)
        medium = Incident(IncidentType.ROBBERY, (0, 0), severity=5)
        for incident in (low, high, medium):
            monitoring.report_incident(incident)

        ordered = monitoring.prioritised_incidents()
        self.assertEqual(ordered, [high, medium, low])


class TestMonitoringAnalytics(unittest.TestCase):
    def test_analyse_trends_identifies_hotspot_district(self):
        monitoring = MonitoringSystem()
        city = City(width=10, height=10, num_districts=2, rng=random.Random(1))

        for _ in range(5):
            incident = Incident(IncidentType.THEFT, (0, 0), severity=3)
            monitoring.report_incident(incident, city=city)

        trends = monitoring.analyse_trends()
        self.assertIsNotNone(trends["hotspot_district"])

    def test_recommend_response_prefers_high_severity_close_incident(self):
        monitoring = MonitoringSystem()
        close_high = Incident(IncidentType.ASSAULT, (1, 0), severity=9)
        far_low = Incident(IncidentType.THEFT, (10, 0), severity=2)
        monitoring.report_incident(close_high)
        monitoring.report_incident(far_low)

        def distance_fn(pos):
            return abs(pos[0] - 0) + abs(pos[1] - 0)

        recommendation = monitoring.recommend_response((0, 0), distance_fn)
        self.assertIs(recommendation, close_high)

    def test_recommend_response_none_when_no_active_incidents(self):
        monitoring = MonitoringSystem()
        self.assertIsNone(monitoring.recommend_response((0, 0), lambda pos: 0))


if __name__ == "__main__":
    unittest.main()
