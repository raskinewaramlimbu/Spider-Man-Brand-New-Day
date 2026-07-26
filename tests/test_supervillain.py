

import unittest
import random

from environment import City
from agents.supervillain import GreenGoblin, Vulture, Mysterio, Supervillain
from agents.spiderman import SpiderMan
from monitoring import MonitoringSystem


class TestSupervillainSharedBehaviour(unittest.TestCase):
    def test_take_damage_reduces_health(self):
        villain = GreenGoblin(rng=random.Random(1))
        villain.take_damage(20)
        self.assertEqual(villain.health, 100)

    def test_health_cannot_go_negative(self):
        villain = Vulture(rng=random.Random(1))
        villain.take_damage(500)
        self.assertEqual(villain.health, 0)

    def test_defeated_flag_set_when_health_reaches_zero(self):
        villain = Mysterio(rng=random.Random(1))
        villain.take_damage(70)
        self.assertTrue(villain.defeated)
        self.assertFalse(villain.alive)

    def test_not_defeated_while_health_remains(self):
        villain = GreenGoblin(rng=random.Random(1))
        villain.take_damage(10)
        self.assertFalse(villain.defeated)
        self.assertTrue(villain.alive)


class TestGreenGoblinAggression(unittest.TestCase):
    def test_moves_towards_spiderman_when_far(self):
        city = City(width=20, height=20, rng=random.Random(2))
        goblin = GreenGoblin(rng=random.Random(2))
        spiderman = SpiderMan(rng=random.Random(2))
        city.place_agent(goblin, 0, 0)
        city.place_agent(spiderman, 10, 10)
        monitoring = MonitoringSystem()

        distance_before = goblin.distance_to(spiderman.position)
        goblin.act(city, spiderman, monitoring)
        distance_after = goblin.distance_to(spiderman.position)

        self.assertLessEqual(distance_after, distance_before)

    def test_attacks_when_adjacent_to_spiderman(self):
        city = City(width=20, height=20, rng=random.Random(3))
        goblin = GreenGoblin(rng=random.Random(3))
        spiderman = SpiderMan(rng=random.Random(3))
        city.place_agent(goblin, 5, 5)
        city.place_agent(spiderman, 6, 5)
        monitoring = MonitoringSystem()

        incident = goblin.act(city, spiderman, monitoring)
        self.assertIsNotNone(incident)


class TestVultureHitAndRun(unittest.TestCase):
    def test_begins_retreating_after_attacking(self):
        city = City(width=20, height=20, rng=random.Random(4))
        vulture = Vulture(rng=random.Random(4))
        spiderman = SpiderMan(rng=random.Random(4))
        city.place_agent(vulture, 5, 5)
        city.place_agent(spiderman, 6, 5)
        monitoring = MonitoringSystem()

        vulture.act(city, spiderman, monitoring)
        self.assertTrue(vulture.retreating)

    def test_react_to_damage_triggers_retreat(self):
        vulture = Vulture(rng=random.Random(5))
        self.assertFalse(vulture.retreating)
        vulture.react_to_damage()
        self.assertTrue(vulture.retreating)


class TestMysterioDeception(unittest.TestCase):
    def test_creates_decoy_incident_eventually(self):
        city = City(width=20, height=20, rng=random.Random(6))
        mysterio = Mysterio(rng=random.Random(6))
        spiderman = SpiderMan(rng=random.Random(6))
        city.place_agent(mysterio, 0, 0)
        city.place_agent(spiderman, 15, 15)
        monitoring = MonitoringSystem()

        mysterio.decoy_cooldown = 0
        incident = mysterio.act(city, spiderman, monitoring)
        self.assertIsNotNone(incident)

    def test_moves_away_from_spiderman_when_close(self):
        city = City(width=20, height=20, rng=random.Random(7))
        mysterio = Mysterio(rng=random.Random(7))
        spiderman = SpiderMan(rng=random.Random(7))
        city.place_agent(mysterio, 5, 5)
        city.place_agent(spiderman, 6, 5)
        monitoring = MonitoringSystem()

        distance_before = mysterio.distance_to(spiderman.position)
        mysterio.act(city, spiderman, monitoring)
        distance_after = mysterio.distance_to(spiderman.position)

        self.assertGreaterEqual(distance_after, distance_before)


class TestVillainsAreDistinct(unittest.TestCase):


    def test_villains_have_different_health_values(self):
        goblin = GreenGoblin()
        vulture = Vulture()
        mysterio = Mysterio()
        healths = {goblin.health, vulture.health, mysterio.health}
        self.assertEqual(len(healths), 3)

    def test_villains_are_all_supervillain_subclasses(self):
        for villain_class in (GreenGoblin, Vulture, Mysterio):
            self.assertTrue(issubclass(villain_class, Supervillain))


if __name__ == "__main__":
    unittest.main()
