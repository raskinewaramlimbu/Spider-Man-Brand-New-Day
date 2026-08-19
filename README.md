# Spider-Man: Brand New Day — AI Simulation

A multi-agent AI simulation built for **CPS7004C – Artificial Intelligence**, modelling
Spider-Man protecting a simulated New York City from criminals and supervillains,
targeting the **Distinction** grade band (requirements a–h).

## Project Structure

```
spiderman_sim/
├── main.py                  # entry point: GUI / headless / strategy comparison
├── environment.py           # City, grid, districts, locations, incidents        (a)
├── monitoring.py            # Central Monitoring System                          (f)
├── simulation.py            # Main simulation loop tying everything together     (h)
├── gui.py                   # Tkinter live visualisation
├── analytics.py             # matplotlib charts and strategy comparison          (h)
├── agents/
│   ├── base_agent.py        # shared Agent base class
│   ├── spiderman.py         # Spider-Man: utility reasoning, memory, Q-learning  (b)
│   ├── criminal.py          # Criminal FSM, gangs, adaptive caution              (c)
│   ├── supervillain.py      # Green Goblin, Vulture, Mysterio                    (d)
│   └── civilian.py          # Civilian risk perception, crowd behaviour          (e)
├── ai/
│   ├── pathfinding.py       # A* search                                         (g)
│   └── qlearning.py         # Tabular Q-learning                                 (g)
└── tests/                   # pytest / unittest test suite (92 tests)
```

## Requirements Coverage (a–h)

| Req | Feature | Where |
|---|---|---|
| (a) City | Grid, districts, location types, day/night, dynamic events | `environment.py` |
| (b) Spider-Man | Detection, stamina, utility-based selection, memory, Q-learning, A* | `agents/spiderman.py` |
| (c) Criminals | FSM, target selection, escape, gangs, adaptive caution | `agents/criminal.py` |
| (d) Supervillains | 3 unique villains with distinct strategies | `agents/supervillain.py` |
| (e) Civilians | Risk perception, fleeing, crowd fear-sharing, reporting | `agents/civilian.py` |
| (f) Monitoring | Recording, prioritisation, trend analysis, prediction | `monitoring.py` |
| (g) AI | Rule-based FSMs, utility systems, A* search, Q-learning | `ai/`, `agents/` |
| (h) Simulation | Multi-agent loop, GUI, analytics, strategy comparison | `simulation.py`, `gui.py`, `analytics.py` |

## How to Run

```bash
# Install permitted third-party library
pip install matplotlib pytest

# Launch the interactive Tkinter GUI (default)
python main.py

# Run one simulation headlessly and save charts to output/
python main.py --headless

# Compare AI strategies (utility-only vs Q-learning vs random) and save a chart
python main.py --compare

# Run the test suite
python -m pytest tests/ -v
```

## Design Notes

- **Layered Spider-Man decision-making**: a hand-written utility formula (severity,
  distance, stamina) makes the base decision; a tabular Q-learning agent learns which
  incident *type* to prefer in a given situation and nudges the utility choice. This
  keeps the reasoning explainable while still demonstrating genuine reinforcement
  learning (state, action, reward, Q-table updates, epsilon-greedy exploration).
- **Honest statistics**: incidents that expire unattended are tracked separately from
  incidents Spider-Man genuinely resolves, so `resolution_rate` is a meaningful
  measure of performance rather than being inflated by a timeout.
- **Strategy comparison** (`main.py --compare`) evaluates three Spider-Man policies —
  utility-only (no learning), full Q-learning, and random incident-type choice — using
  identical paired random seeds across strategies, so differences reflect the policy
  itself rather than random variation in city layout.

## Status
Project complete as of final review pass.
