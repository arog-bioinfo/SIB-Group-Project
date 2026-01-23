import math
import mesa
from mesa import Model
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector

from .agents import State, VirusAgentContinuous


def number_state(model, state):
    return sum(1 for a in model.agents if a.state is state)

def number_infected(model):
    return number_state(model, State.INFECTED)

def number_susceptible(model):
    return number_state(model, State.SUSCEPTIBLE)

def number_resistant(model):
    return number_state(model, State.RESISTANT)


class VirusModelContinuous(Model):
    """
    Moving-dots ABM:
    - agents move in ContinuousSpace
    - infection spreads within a radius
    - measures_index (Module 1) controls virus_spread_chance
    """

    def __init__(
        self,
        N=200,
        width=100,
        height=100,
        initial_outbreak_size=5,

        # Module 1 hook:
        measures_index=0.0,                 # in [0,1], 0=no measures, 1=max restriction
        base_virus_spread_chance=0.25,      # baseline transmissibility

        # ABM params:
        infection_radius=2.0,
        movement_speed=1.0,
        virus_check_frequency=0.4,
        recovery_chance=0.3,
        gain_resistance_chance=0.5,
        rng=None,
    ):
        super().__init__(rng=rng)

        self.N = N
        self.width = width
        self.height = height
        self.space = ContinuousSpace(width, height, torus=True)


        # Module 1 → Module 2 mapping
        self.measures_index = measures_index
        self.base_virus_spread_chance = base_virus_spread_chance
        self.virus_spread_chance = self.base_virus_spread_chance * (1 - self.measures_index)

        self.infection_radius = infection_radius
        self.movement_speed = movement_speed
        self.virus_check_frequency = virus_check_frequency
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance

        # Create agents 
        self.agents_list = []
        for i in range(N):
            a = VirusAgentContinuous(model=self, initial_state=State.SUSCEPTIBLE)
            self.agents_list.append(a)
            x = self.random.random() * width
            y = self.random.random() * height
            self.space.place_agent(a, (x, y))

        # Infect some agents
        initial_outbreak_size = min(initial_outbreak_size, len(self.agents_list))
        initial_infected = self.random.sample(self.agents_list, initial_outbreak_size)

        for agent in initial_infected:
            agent.state = State.INFECTED


        self.datacollector = DataCollector(
            {
                "Infected": number_infected,
                "Susceptible": number_susceptible,
                "Resistant": number_resistant,
                "R over S": self.resistant_susceptible_ratio,
            }
        )

        self.running = True
        self.datacollector.collect(self)

    @property
    def agents(self):
        # convenience for counting
        return self._agents

    def resistant_susceptible_ratio(self):
        try:
            return number_resistant(self) / number_susceptible(self)
        except ZeroDivisionError:
            return math.inf

    def update_from_module1(self, measures_index: float):
        """Call this if measures change over time (dataset)."""
        self.measures_index = max(0.0, min(1.0, measures_index))
        self.virus_spread_chance = self.base_virus_spread_chance * (1 - self.measures_index)

    def step(self):
        # if you have time-varying measures, call update_from_module1(...) here

        for a in self._agents:
            a.step()

        self.datacollector.collect(self)
