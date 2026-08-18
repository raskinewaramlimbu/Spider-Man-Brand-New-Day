

import matplotlib.pyplot as plt


def plot_incident_timeline(history, save_path=None):

    ticks = [h["tick"] for h in history]
    active = [h["active_incidents"] for h in history]
    resolved = [h["resolved_total"] for h in history]

    plt.figure(figsize=(9, 5))
    plt.plot(ticks, active, label="Active incidents")
    plt.plot(ticks, resolved, label="Total resolved (cumulative)")
    plt.xlabel("Simulation tick")
    plt.ylabel("Incidents")
    plt.title("Incident activity over time")
    plt.legend()
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()


def plot_stamina_over_time(history, save_path=None):
    ticks = [h["tick"] for h in history]
    stamina = [h["spiderman_stamina"] for h in history]

    plt.figure(figsize=(9, 4))
    plt.plot(ticks, stamina, color="darkred")
    plt.xlabel("Simulation tick")
    plt.ylabel("Spider-Man stamina")
    plt.title("Spider-Man stamina over time")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()


def plot_strategy_comparison(results, save_path=None):

    names = list(results.keys())
    resolution_rates = [results[name]["resolution_rate"] * 100 for name in names]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(names, resolution_rates, color=["#1f77b4", "#ff7f0e", "#2ca02c"][:len(names)])
    plt.ylabel("Incident resolution rate (%)")
    plt.title("Comparison of AI strategies - city safety outcome")
    plt.ylim(0, 100)
    for bar, rate in zip(bars, resolution_rates):
        plt.text(bar.get_x() + bar.get_width() / 2, rate + 1, f"{rate:.1f}%", ha="center")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()


def plot_incidents_by_district(monitoring_system, save_path=None):
    stats = monitoring_system.basic_statistics()
    districts = list(stats["by_district"].keys())
    counts = list(stats["by_district"].values())

    if not districts:
        return

    plt.figure(figsize=(8, 5))
    plt.bar(districts, counts, color="slateblue")
    plt.ylabel("Number of incidents")
    plt.title("Incidents by district")
    plt.xticks(rotation=20)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()
