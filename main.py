

import sys
import os
import random

from simulation import Simulation
import analytics


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def run_headless(ticks=300, seed=1):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    sim = Simulation(seed=seed)
    sim.run(ticks)

    print("Final statistics:")
    for key, value in sim.final_statistics().items():
        print(f"  {key}: {value}")

    analytics.plot_incident_timeline(sim.history, save_path=os.path.join(OUTPUT_DIR, "timeline.png"))
    analytics.plot_stamina_over_time(sim.history, save_path=os.path.join(OUTPUT_DIR, "stamina.png"))
    analytics.plot_incidents_by_district(sim.monitoring, save_path=os.path.join(OUTPUT_DIR, "districts.png"))
    print(f"Charts saved to {OUTPUT_DIR}/")


def run_strategy_comparison(ticks=400, trials=15):

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    strategies = {
        "utility_only": 0.0,
        ##"full_learning": 0.2,
        "full_learning": 0.05,
        "random_choice": 1.0,
    }


    seeds = [100 * trial + 7 for trial in range(trials)]

    results = {}
    for strategy_name, epsilon in strategies.items():
        resolution_rates = []
        for seed in seeds:
            sim = Simulation(seed=seed)
            sim.spiderman.brain.epsilon = epsilon
            sim.spiderman.brain.alpha = 0.0 if strategy_name == "random_choice" else 0.2
            sim.run(ticks)
            resolution_rates.append(sim.final_statistics()["resolution_rate"])

        average_rate = sum(resolution_rates) / len(resolution_rates)
        results[strategy_name] = {"resolution_rate": average_rate, "total_incidents": ticks}
        print(f"{strategy_name}: average resolution rate = {average_rate*100:.1f}% over {trials} trials "
              f"(runs: {[round(r*100,1) for r in resolution_rates]})")

    analytics.plot_strategy_comparison(results, save_path=os.path.join(OUTPUT_DIR, "strategy_comparison.png"))
    print(f"Comparison chart saved to {OUTPUT_DIR}/strategy_comparison.png")


def run_gui():
    import tkinter as tk
    from gui import SimulationGUI
    root = tk.Tk()
    SimulationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    if "--compare" in sys.argv:
        run_strategy_comparison()
    elif "--headless" in sys.argv:
        run_headless()
    else:
        run_gui()
