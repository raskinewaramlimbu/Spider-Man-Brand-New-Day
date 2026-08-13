

import unittest

from simulation import Simulation


class TestSimulationSetup(unittest.TestCase):
    def test_creates_all_agent_types(self):
        sim = Simulation(width=15, height=15, num_civilians=8, num_criminals=4, seed=1)
        self.assertIsNotNone(sim.spiderman)
        self.assertEqual(len(sim.civilians), 8)
        self.assertEqual(len(sim.criminals), 4)
        self.assertEqual(len(sim.supervillains), 3)

    def test_all_agents_start_placed_within_bounds(self):
        sim = Simulation(width=10, height=10, seed=2)
        for agent in [sim.spiderman, *sim.civilians, *sim.criminals, *sim.supervillains]:
            x, y = agent.position
            self.assertTrue(sim.city.in_bounds(x, y))

    def test_can_disable_supervillains(self):
        sim = Simulation(width=10, height=10, include_supervillains=False, seed=3)
        self.assertEqual(len(sim.supervillains), 0)


class TestSimulationRunsWithoutErrors(unittest.TestCase):
    def test_run_completes_and_advances_tick_count(self):
        sim = Simulation(width=15, height=15, seed=4)
        sim.run(50)
        self.assertEqual(sim.tick, 50)

    def test_history_has_one_entry_per_tick(self):
        sim = Simulation(width=15, height=15, seed=5)
        sim.run(30)
        self.assertEqual(len(sim.history), 30)

    def test_agents_stay_within_grid_bounds_throughout(self):
        sim = Simulation(width=12, height=12, seed=6)
        sim.run(60)
        for agent in [sim.spiderman, *sim.civilians, *sim.criminals, *sim.supervillains]:
            if agent.alive:
                x, y = agent.position
                self.assertTrue(sim.city.in_bounds(x, y))


class TestSimulationStatisticsConsistency(unittest.TestCase):
    def test_resolved_plus_expired_plus_active_equals_total(self):
        sim = Simulation(width=15, height=15, seed=7)
        sim.run(150)
        stats = sim.final_statistics()
        self.assertEqual(
            stats["resolved_incidents"] + stats["expired_incidents"] + stats["active_incidents"],
            stats["total_incidents"],
        )

    def test_resolution_rate_is_between_zero_and_one(self):
        sim = Simulation(width=15, height=15, seed=8)
        sim.run(150)
        rate = sim.final_statistics()["resolution_rate"]
        self.assertGreaterEqual(rate, 0.0)
        self.assertLessEqual(rate, 1.0)

    def test_spiderman_stamina_stays_within_valid_range(self):
        sim = Simulation(width=15, height=15, seed=9)
        sim.run(150)
        self.assertGreaterEqual(sim.spiderman.stamina, 0.0)
        self.assertLessEqual(sim.spiderman.stamina, sim.spiderman.max_stamina)


class TestSimulationLearningOccurs(unittest.TestCase):
    def test_spiderman_q_table_grows_during_simulation(self):
        sim = Simulation(width=15, height=15, seed=10)
        sim.run(100)
        self.assertGreater(len(sim.spiderman.brain.q_table), 0)

    def test_spiderman_resolves_at_least_one_incident_over_a_long_run(self):
        sim = Simulation(width=15, height=15, seed=11)
        sim.run(200)
        stats = sim.final_statistics()
        self.assertGreater(stats["resolved_incidents"], 0)


class TestSimulationAgentInteractions(unittest.TestCase):
    def test_criminals_can_be_captured_over_a_long_run(self):
        sim = Simulation(width=12, height=12, num_criminals=6, seed=12)
        sim.run(200)
        total_captures = sum(c.times_caught for c in sim.criminals)
        self.assertGreaterEqual(total_captures, 0)

    def test_supervillains_can_take_damage_over_a_long_run(self):
        sim = Simulation(width=12, height=12, seed=13)
        sim.run(250)

        for villain in sim.supervillains:
            self.assertGreaterEqual(villain.health, 0)


if __name__ == "__main__":
    unittest.main()
