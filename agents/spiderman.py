

from ai.pathfinding import a_star
from ai.qlearning import QLearningAgent, encode_state
from agents.base_agent import Agent
from environment import IncidentType


class SpiderMan(Agent):
    def __init__(self, name="Spider-Man", rng=None):
        super().__init__(name, rng=rng)
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.detection_radius = 6
        self.threat_memory = []
        self.district_threat_counts = {}
        self.rescues = 0
        self.arrests = 0
        self.villains_defeated = 0

        action_labels = [t.value for t in IncidentType]
        self.brain = QLearningAgent(actions=action_labels, rng=rng)
        self._last_state = None
        self._last_action = None



    def detect_incidents(self, monitoring_system):

        all_active = monitoring_system.get_active_incidents()
        detected = [
            i for i in all_active
            if self.distance_to(i.position) <= self.detection_radius or i.severity >= 8
        ]
        return detected

    def spend_stamina(self, amount):
        self.stamina = max(0.0, self.stamina - amount)

    def rest(self, amount=2.0):

        self.stamina = min(self.max_stamina, self.stamina + amount)

    def is_exhausted(self):
        return self.stamina <= 10.0



    def remember(self, incident, tick, city):

        district = city.get_district_at(*incident.position)
        self.threat_memory.append({
            "position": incident.position,
            "type": incident.incident_type,
            "severity": incident.severity,
            "tick": tick,
            "district": district.name,
        })
        self.district_threat_counts[district.name] = self.district_threat_counts.get(district.name, 0) + 1

        if len(self.threat_memory) > 200:
            self.threat_memory.pop(0)

    def select_incident(self, incidents, preferred_type=None):

        if not incidents:
            return None

        def utility(incident):
            distance = self.distance_to(incident.position)
            stamina_cost_penalty = 0.3 * distance
            severity_score = incident.severity * 2.0
           ## type_bonus = 8.0 if preferred_type and incident.incident_type.value == preferred_type else 0.0
            type_bonus = 14.0 if preferred_type and incident.incident_type.value == preferred_type else 0.0

            low_stamina_caution = -5.0 if self.stamina < 20 and distance > 5 else 0.0
            return severity_score - stamina_cost_penalty + type_bonus + low_stamina_caution

        return max(incidents, key=utility)



    def district_risk_estimate(self):

        if not self.district_threat_counts:
            return None
        return max(self.district_threat_counts, key=self.district_threat_counts.get)



    def choose_priority_type(self, incidents, city):

        state = encode_state(
            num_active_incidents=len(incidents),
            stamina_level=self.stamina,
            is_night=city.is_night(),
        )
        available_types = list({i.incident_type.value for i in incidents}) or None
        action = self.brain.choose_action(state, available_actions=available_types)

        self._last_state = state
        self._last_action = action
        return action

    def learn_from_outcome(self, reward, next_incidents, city):

        if self._last_state is None or self._last_action is None:
            return
        next_state = encode_state(
            num_active_incidents=len(next_incidents),
            stamina_level=self.stamina,
            is_night=city.is_night(),
        )
        self.brain.learn(self._last_state, self._last_action, reward, next_state)
        self.brain.decay_epsilon()



    def move_towards_incident(self, city, incident_position):

        path = a_star(city, self.position, incident_position)
        if path:
            next_step = path[0]
            city.move_agent(self, *next_step)
        else:
            self.move_towards(city, incident_position)

    def respond_to_incident(self, incident, monitoring_system, tick):

        if self.distance_to(incident.position) > 1:
            return False, 0.0

        cost = 5 + incident.severity
        self.spend_stamina(cost)
        monitoring_system.mark_resolved(incident, tick=tick)

        reward = incident.severity
        if incident.victim is not None:
            incident.victim.is_victim = False
            self.rescues += 1
            reward += 2

        if incident.culprit is not None:
            culprit = incident.culprit
            from agents.criminal import Criminal
            from agents.supervillain import Supervillain
            if isinstance(culprit, Criminal):
                culprit.record_capture()
                self.arrests += 1
            elif isinstance(culprit, Supervillain):
                culprit.take_damage(30)
                culprit.react_to_damage()
                if culprit.defeated:
                    self.villains_defeated += 1
                    reward += 10

        return True, reward
# Fixed spiderman target-lock not clearing after criminal despawn
# Fixed spiderman target-lock not clearing after criminal despawn
