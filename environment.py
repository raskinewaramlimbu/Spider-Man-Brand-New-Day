

import random
from enum import Enum


class LocationType(Enum):

    STREET = "Street"
    BUILDING = "Building"
    PUBLIC_SPACE = "Public Space"


class IncidentType(Enum):

    THEFT = "Theft"
    ASSAULT = "Assault"
    ROBBERY = "Robbery"
    SUPERVILLAIN_ATTACK = "Supervillain Attack"
    HOSTAGE = "Hostage Situation"


class Incident:


    _next_id = 1

    def __init__(self, incident_type, position, severity, victim=None, culprit=None):
        self.id = Incident._next_id
        Incident._next_id += 1

        self.incident_type = incident_type
        self.position = position
        self.severity = severity
        self.victim = victim
        self.culprit = culprit
        self.resolved = False
        self.expired = False
        self.time_created = None
        self.time_resolved = None

    def __repr__(self):
        status = "RESOLVED" if self.resolved else "ACTIVE"
        return f"Incident#{self.id}({self.incident_type.value}, sev={self.severity}, {status})"


class District:


    def __init__(self, name, crime_rate, population_density):

        self.name = name
        self.crime_rate = crime_rate
        self.population_density = population_density

    def __repr__(self):
        return f"District({self.name}, crime={self.crime_rate}, density={self.population_density})"


class Cell:


    def __init__(self, x, y, location_type, district):
        self.x = x
        self.y = y
        self.location_type = location_type
        self.district = district
        self.occupant = None

    def is_empty(self):
        return self.occupant is None

    def __repr__(self):
        occ = self.occupant.name if self.occupant else "empty"
        return f"Cell({self.x},{self.y},{self.location_type.value},{occ})"


class City:


    def __init__(self, width, height, num_districts=4, rng=None):
        self.width = width
        self.height = height
        self.rng = rng if rng is not None else random.Random()

        self.districts = self._create_districts(num_districts)
        self.grid = self._create_grid()
        self._district_cells = self._index_cells_by_district()

        self.incidents = []
        self.time_of_day = 0
        self.tick_count = 0



    def _create_districts(self, num_districts):

        names = ["Queens", "Manhattan", "Brooklyn", "The Bronx", "Harlem", "Chinatown"]
        self.rng.shuffle(names)
        districts = []
        for i in range(num_districts):
            crime_rate = round(self.rng.uniform(0.05, 0.35), 2)
            density = round(self.rng.uniform(0.2, 0.9), 2)
            districts.append(District(names[i % len(names)], crime_rate, density))
        return districts

    def _create_grid(self):

        grid = []
        band_width = max(1, self.width // len(self.districts))

        for y in range(self.height):
            row = []
            for x in range(self.width):
                district_index = min(x // band_width, len(self.districts) - 1)
                district = self.districts[district_index]
                location_type = self.rng.choices(
                    [LocationType.STREET, LocationType.BUILDING, LocationType.PUBLIC_SPACE],
                    weights=[0.5, 0.3, 0.2],
                )[0]
                row.append(Cell(x, y, location_type, district))
            grid.append(row)
        return grid

    def _index_cells_by_district(self):

        index = {district.name: [] for district in self.districts}
        for y in range(self.height):
            for x in range(self.width):
                index[self.grid[y][x].district.name].append((x, y))
        return index

    def cells_in_district(self, district_name):
        return self._district_cells.get(district_name, [])



    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def get_cell(self, x, y):
        return self.grid[y][x]

    def get_district_at(self, x, y):
        return self.get_cell(x, y).district

    def place_agent(self, agent, x, y):

        if agent.position is not None:
            old_x, old_y = agent.position
            if self.in_bounds(old_x, old_y) and self.get_cell(old_x, old_y).occupant is agent:
                self.get_cell(old_x, old_y).occupant = None
        self.get_cell(x, y).occupant = agent
        agent.position = (x, y)

    def move_agent(self, agent, new_x, new_y):

        if not self.in_bounds(new_x, new_y):
            return False
        target = self.get_cell(new_x, new_y)
        if not target.is_empty() and target.occupant is not agent:
            return False
        self.place_agent(agent, new_x, new_y)
        return True

    def random_empty_position(self):

        for _ in range(200):
            x = self.rng.randrange(self.width)
            y = self.rng.randrange(self.height)
            if self.get_cell(x, y).is_empty():
                return x, y
        return self.rng.randrange(self.width), self.rng.randrange(self.height)



    def advance_time(self):

        self.tick_count += 1
        self.time_of_day = (self.time_of_day + 1) % 24

    def is_night(self):
        return self.time_of_day >= 20 or self.time_of_day <= 5

    def environmental_crime_modifier(self):

        return 1.6 if self.is_night() else 1.0


    def maybe_generate_incident(self, civilians, criminals):

        modifier = self.environmental_crime_modifier()

        for district in self.districts:
            chance = district.crime_rate * 0.012 * modifier
            if self.rng.random() < chance:
                x, y = self.random_empty_position()
                incident_type = self.rng.choice(
                    [IncidentType.THEFT, IncidentType.ASSAULT, IncidentType.ROBBERY]
                )
                severity = self.rng.randint(2, 6)
                victim = self.rng.choice(civilians) if civilians else None
                incident = Incident(incident_type, (x, y), severity, victim=victim)
                incident.time_created = self.tick_count
                self.incidents.append(incident)
                return incident
        return None

    def active_incidents(self):
        return [i for i in self.incidents if not i.resolved]
# Adjusted cell traversal cost weighting for edge-case pathing
# Adjusted cell traversal cost weighting for edge-case pathing
