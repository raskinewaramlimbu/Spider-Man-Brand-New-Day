
import unittest
import random

from environment import City, Cell, District, Incident, IncidentType, LocationType


class TestCityGrid(unittest.TestCase):
    def setUp(self):
        self.city = City(width=10, height=10, num_districts=3, rng=random.Random(1))

    def test_grid_has_correct_dimensions(self):
        self.assertEqual(len(self.city.grid), 10)
        self.assertEqual(len(self.city.grid[0]), 10)

    def test_every_cell_belongs_to_a_district(self):
        for row in self.city.grid:
            for cell in row:
                self.assertIsInstance(cell.district, District)

    def test_every_cell_has_a_location_type(self):
        for row in self.city.grid:
            for cell in row:
                self.assertIsInstance(cell.location_type, LocationType)

    def test_in_bounds_checks_are_correct(self):
        self.assertTrue(self.city.in_bounds(0, 0))
        self.assertTrue(self.city.in_bounds(9, 9))
        self.assertFalse(self.city.in_bounds(-1, 0))
        self.assertFalse(self.city.in_bounds(10, 0))

    def test_cells_start_empty(self):
        cell = self.city.get_cell(3, 3)
        self.assertTrue(cell.is_empty())


class DummyAgent:

    def __init__(self, name):
        self.name = name
        self.position = None
        self.alive = True


class TestAgentPlacementAndMovement(unittest.TestCase):
    def setUp(self):
        self.city = City(width=5, height=5, num_districts=2, rng=random.Random(2))
        self.agent = DummyAgent("Test Agent")

    def test_place_agent_sets_position_and_occupant(self):
        self.city.place_agent(self.agent, 2, 2)
        self.assertEqual(self.agent.position, (2, 2))
        self.assertIs(self.city.get_cell(2, 2).occupant, self.agent)

    def test_move_agent_updates_position(self):
        self.city.place_agent(self.agent, 0, 0)
        moved = self.city.move_agent(self.agent, 1, 0)
        self.assertTrue(moved)
        self.assertEqual(self.agent.position, (1, 0))
        self.assertTrue(self.city.get_cell(0, 0).is_empty())

    def test_move_agent_rejects_out_of_bounds(self):
        self.city.place_agent(self.agent, 0, 0)
        moved = self.city.move_agent(self.agent, -1, 0)
        self.assertFalse(moved)
        self.assertEqual(self.agent.position, (0, 0))

    def test_move_agent_rejects_occupied_cell(self):
        other = DummyAgent("Other")
        self.city.place_agent(self.agent, 0, 0)
        self.city.place_agent(other, 1, 0)
        moved = self.city.move_agent(self.agent, 1, 0)
        self.assertFalse(moved)


class TestIncidents(unittest.TestCase):
    def test_incident_ids_are_unique_and_increasing(self):
        i1 = Incident(IncidentType.THEFT, (0, 0), 3)
        i2 = Incident(IncidentType.ASSAULT, (1, 1), 5)
        self.assertNotEqual(i1.id, i2.id)
        self.assertLess(i1.id, i2.id)

    def test_incident_starts_unresolved(self):
        incident = Incident(IncidentType.ROBBERY, (0, 0), 5)
        self.assertFalse(incident.resolved)
        self.assertFalse(incident.expired)

    def test_environmental_crime_modifier_higher_at_night(self):
        city = City(width=5, height=5, rng=random.Random(3))
        city.time_of_day = 2
        night_modifier = city.environmental_crime_modifier()
        city.time_of_day = 12
        day_modifier = city.environmental_crime_modifier()
        self.assertGreater(night_modifier, day_modifier)


if __name__ == "__main__":
    unittest.main()
