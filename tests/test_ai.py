
import unittest
import random

from environment import City
from ai.pathfinding import a_star, manhattan
from ai.qlearning import QLearningAgent, encode_state


class TestManhattanDistance(unittest.TestCase):
    def test_manhattan_distance_calculation(self):
        self.assertEqual(manhattan((0, 0), (3, 4)), 7)
        self.assertEqual(manhattan((5, 5), (5, 5)), 0)


class TestAStarPathfinding(unittest.TestCase):
    def setUp(self):
        self.city = City(width=10, height=10, rng=random.Random(1))

    def test_returns_empty_path_when_start_equals_goal(self):
        path = a_star(self.city, (5, 5), (5, 5))
        self.assertEqual(path, [])

    def test_finds_a_path_on_open_grid(self):
        path = a_star(self.city, (0, 0), (5, 5))
        self.assertGreater(len(path), 0)
        self.assertEqual(path[-1], (5, 5))

    def test_path_length_matches_manhattan_distance_on_open_grid(self):

        start, goal = (0, 0), (4, 3)
        path = a_star(self.city, start, goal)
        self.assertEqual(len(path), manhattan(start, goal))

    def test_path_avoids_occupied_cells(self):

        class DummyAgent:
            def __init__(self):
                self.position = None
                self.alive = True

        blockers = [DummyAgent() for _ in range(3)]
        for i, blocker in enumerate(blockers):
            self.city.place_agent(blocker, 2, i)

        path = a_star(self.city, (0, 0), (2, 3))
        self.assertGreater(len(path), 0)
        for step in path:
            self.assertNotIn(step, [(2, 0), (2, 1), (2, 2)])


class TestQLearningAgent(unittest.TestCase):
    def test_choose_action_returns_one_of_the_available_actions(self):
        agent = QLearningAgent(actions=["a", "b", "c"], epsilon=0.0, rng=random.Random(1))
        chosen = agent.choose_action(state="s1", available_actions=["a", "b"])
        self.assertIn(chosen, ["a", "b"])

    def test_choose_action_returns_none_when_no_actions_available(self):
        agent = QLearningAgent(actions=["a", "b"], rng=random.Random(1))
        self.assertIsNone(agent.choose_action(state="s1", available_actions=[]))

    def test_learn_updates_q_value(self):
        agent = QLearningAgent(actions=["a", "b"], alpha=0.5, gamma=0.9, rng=random.Random(1))
        agent.learn(state="s1", action="a", reward=10.0, next_state="s2")
        self.assertGreater(agent.q_table["s1"]["a"], 0.0)

    def test_greedy_selection_picks_highest_value_action(self):
        agent = QLearningAgent(actions=["a", "b"], epsilon=0.0, rng=random.Random(1))
        agent.q_table["s1"] = {"a": 1.0, "b": 5.0}
        chosen = agent.choose_action(state="s1")
        self.assertEqual(chosen, "b")

    def test_decay_epsilon_reduces_exploration_over_time(self):
        agent = QLearningAgent(actions=["a"], epsilon=0.5, rng=random.Random(1))
        agent.decay_epsilon(factor=0.9)
        self.assertLess(agent.epsilon, 0.5)

    def test_epsilon_never_drops_below_minimum(self):
        agent = QLearningAgent(actions=["a"], epsilon=0.5, rng=random.Random(1))
        for _ in range(500):
            agent.decay_epsilon(factor=0.9, minimum=0.05)
        self.assertGreaterEqual(agent.epsilon, 0.05)


class TestStateEncoding(unittest.TestCase):
    def test_encode_state_returns_expected_buckets(self):
        state = encode_state(num_active_incidents=0, stamina_level=100, is_night=False)
        self.assertEqual(state, ("none", "high", "day"))

    def test_encode_state_low_stamina_and_many_incidents(self):
        state = encode_state(num_active_incidents=5, stamina_level=10, is_night=True)
        self.assertEqual(state, ("many", "low", "night"))


if __name__ == "__main__":
    unittest.main()
