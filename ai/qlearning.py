

import random


class QLearningAgent:
    def __init__(self, actions, alpha=0.2, gamma=0.9, epsilon=0.2, rng=None):

        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.rng = rng if rng is not None else random.Random()
        self.q_table = {}

    def _ensure_state(self, state):
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in self.actions}

    def choose_action(self, state, available_actions=None):

        self._ensure_state(state)
        options = available_actions if available_actions is not None else self.actions

        if not options:
            return None

        if self.rng.random() < self.epsilon:
            return self.rng.choice(options)

        q_values = self.q_table[state]

        best_action = max(options, key=lambda a: q_values.get(a, 0.0))
        return best_action

    def learn(self, state, action, reward, next_state):

        self._ensure_state(state)
        self._ensure_state(next_state)

        old_value = self.q_table[state][action]
        future_estimate = max(self.q_table[next_state].values())
        new_value = old_value + self.alpha * (reward + self.gamma * future_estimate - old_value)
        self.q_table[state][action] = new_value

    def decay_epsilon(self, factor=0.995, minimum=0.02):

        self.epsilon = max(minimum, self.epsilon * factor)


def encode_state(num_active_incidents, stamina_level, is_night):

    incident_bucket = "none" if num_active_incidents == 0 else (
        "few" if num_active_incidents <= 2 else "many"
    )
    stamina_bucket = "low" if stamina_level < 30 else ("mid" if stamina_level < 70 else "high")
    time_bucket = "night" if is_night else "day"
    return (incident_bucket, stamina_bucket, time_bucket)
