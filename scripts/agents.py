from enum import Enum
import math

from mesa import Agent

class State(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RESISTANT = 2


class VirusAgentContinuous(Agent):
    def __init__(self, model, initial_state):
        super().__init__(model)
        self.state = initial_state
        self.pos = None

    @property
    def random(self):
        return self.model.random

    def move(self):
        dx = self.random.uniform(-1, 1)
        dy = self.random.uniform(-1, 1)

        x, y = self.pos
        speed = self.model.movement_speed

        new_pos = (x + dx * speed, y + dy * speed)
        self.model.space.move_agent(self, new_pos)


    def try_to_infect_nearby(self):
        pos = self.pos
        space = self.model.space
        
        if hasattr(space, "_agent_region"):
            neighbors = self.model.space.get_neighbors(self.pos, self.model.infection_radius, include_center=False, same_country_only=True)
        else:
            neighbors = self.model.space.get_neighbors(pos, radius=self.model.infection_radius, include_center=False)

        for other in neighbors:
            if other.state is State.SUSCEPTIBLE:
                if self.random.random() < self.model.virus_spread_chance:
                    other.state = State.INFECTED

    def try_gain_resistance(self):
        if self.random.random() < self.model.gain_resistance_chance:
            self.state = State.RESISTANT

    def try_remove_infection(self):
        if self.random.random() < self.model.recovery_chance:
            self.state = State.SUSCEPTIBLE
            self.try_gain_resistance()
        else:
            self.state = State.INFECTED

    def check_situation(self):
        if self.state is State.INFECTED and (
            self.random.random() < self.model.virus_check_frequency
        ):
            self.try_remove_infection()

    def step(self):
        self.move()
        if self.state is State.INFECTED:
            self.try_to_infect_nearby()
        self.check_situation()
