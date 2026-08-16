

import tkinter as tk
from tkinter import ttk

from simulation import Simulation
from agents.spiderman import SpiderMan
from agents.civilian import Civilian
from agents.criminal import Criminal
from agents.supervillain import Supervillain
from environment import LocationType

CELL_SIZE = 24

LOCATION_COLOURS = {
    LocationType.STREET: "#dcdcdc",
    LocationType.BUILDING: "#b0a08a",
    LocationType.PUBLIC_SPACE: "#c9e4c5",
}

AGENT_COLOURS = {
    "SpiderMan": "#c0392b",
    "Civilian": "#2980b9",
    "Criminal": "#7f8c8d",
    "Supervillain": "#8e44ad",
}


class SimulationGUI:
    def __init__(self, root, width=18, height=18, seed=None):
        self.root = root
        self.root.title("Spider-Man: Brand New Day - AI Simulation")

        self.width = width
        self.height = height
        self.seed = seed
        self.sim = Simulation(width=width, height=height, seed=seed)

        self.running = False
        self.speed_ms = 300

        self._build_layout()
        self._draw_grid()
        self._refresh_stats()



    def _build_layout(self):
        container = ttk.Frame(self.root, padding=8)
        container.pack(fill="both", expand=True)


        self.canvas = tk.Canvas(
            container, width=self.width * CELL_SIZE, height=self.height * CELL_SIZE,
            bg="white", highlightthickness=1, highlightbackground="black",
        )
        self.canvas.grid(row=0, column=0, rowspan=6, padx=(0, 10))


        ttk.Button(container, text="Start", command=self.start).grid(row=0, column=1, sticky="ew")
        ttk.Button(container, text="Pause", command=self.pause).grid(row=1, column=1, sticky="ew")
        ttk.Button(container, text="Step", command=self.single_step).grid(row=2, column=1, sticky="ew")
        ttk.Button(container, text="Reset", command=self.reset).grid(row=3, column=1, sticky="ew")

        ttk.Label(container, text="Speed").grid(row=4, column=1, sticky="w")
        self.speed_slider = ttk.Scale(
            container, from_=50, to=1000, orient="horizontal", command=self._on_speed_change
        )
        self.speed_slider.set(self.speed_ms)
        self.speed_slider.grid(row=5, column=1, sticky="ew")


        self.stats_text = tk.StringVar()
        stats_label = ttk.Label(container, textvariable=self.stats_text, justify="left",
                                 font=("Consolas", 10))
        stats_label.grid(row=0, column=2, rowspan=6, sticky="nw", padx=(10, 0))

        container.columnconfigure(2, weight=1)



    def _draw_grid(self):
        self.canvas.delete("all")
        city = self.sim.city

        for y in range(city.height):
            for x in range(city.width):
                cell = city.get_cell(x, y)
                colour = LOCATION_COLOURS[cell.location_type]
                x0, y0 = x * CELL_SIZE, y * CELL_SIZE
                x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=colour, outline="#999999")

        self._draw_agents()

    def _draw_agents(self):

        for incident in self.sim.city.active_incidents():
            x, y = incident.position
            x0, y0 = x * CELL_SIZE + 4, y * CELL_SIZE + 4
            x1, y1 = x0 + CELL_SIZE - 8, y0 + CELL_SIZE - 8
            self.canvas.create_rectangle(x0, y0, x1, y1, fill="#e74c3c", outline="")

        for agent in self._all_agents():
            if not agent.alive or agent.position is None:
                continue
            colour = self._colour_for(agent)
            x, y = agent.position
            cx, cy = x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2
            r = CELL_SIZE // 2 - 3
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=colour, outline="black")

    def _colour_for(self, agent):
        if isinstance(agent, SpiderMan):
            return AGENT_COLOURS["SpiderMan"]
        if isinstance(agent, Supervillain):
            return AGENT_COLOURS["Supervillain"]
        if isinstance(agent, Criminal):
            return AGENT_COLOURS["Criminal"]
        if isinstance(agent, Civilian):
            return AGENT_COLOURS["Civilian"]
        return "#000000"

    def _all_agents(self):
        return [self.sim.spiderman, *self.sim.civilians, *self.sim.criminals, *self.sim.supervillains]

    def _refresh_stats(self):
        stats = self.sim.final_statistics()
        sm = self.sim.spiderman
        trends = self.sim.monitoring.analyse_trends()

        text_lines = [
            f"Tick: {self.sim.tick}",
            f"Time of day: {self.sim.city.time_of_day:02d}:00 ({'Night' if self.sim.city.is_night() else 'Day'})",
            "",
            f"Active incidents:  {stats['active_incidents']}",
            f"Resolved:           {stats['resolved_incidents']}",
            f"Resolution rate:   {stats['resolution_rate']*100:.1f}%",
            "",
            f"Spider-Man stamina: {sm.stamina:.0f}/{sm.max_stamina:.0f}",
            f"Rescues:            {sm.rescues}",
            f"Arrests:            {sm.arrests}",
            f"Villains defeated:  {sm.villains_defeated}",
            "",
            f"Hotspot district:   {trends['hotspot_district']}",
            f"Most common crime:  {trends['most_common_type']}",
            f"Learned states:     {len(sm.brain.q_table)}",
        ]
        self.stats_text.set("\n".join(text_lines))



    def start(self):
        if not self.running:
            self.running = True
            self._loop()

    def pause(self):
        self.running = False

    def single_step(self):
        self.sim.step()
        self._draw_grid()
        self._refresh_stats()

    def reset(self):
        self.running = False
        self.sim = Simulation(width=self.width, height=self.height, seed=self.seed)
        self._draw_grid()
        self._refresh_stats()

    def _on_speed_change(self, value):
        self.speed_ms = int(float(value))

    def _loop(self):
        if not self.running:
            return
        self.sim.step()
        self._draw_grid()
        self._refresh_stats()
        self.root.after(self.speed_ms, self._loop)


def launch():
    root = tk.Tk()
    SimulationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch()
