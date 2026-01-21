import agentpy as ap
import matplotlib.pyplot as plt
import numpy as np

class SIRAgent(ap.Agent):
    def setup(self):
        self.state = 'S'
        self.variant = 'Wild'
        self.fitness = 1.0
        self.p_trans = 0.3 * self.fitness
        self.infection_time = 0

    def move(self):
        dx, dy = self.model.rng.integers(-1, 2, 2)
        self.space.move_by((dx, dy))

    def interact(self):
        if self.state == 'I':
            if self.model.t - self.infection_time > self.p['duration']:
                self.state = 'R'
            neighbors = self.space.neighbors(self, moore=True)
            for n in neighbors:
                if n.state == 'S' and self.model.rng.random() < self.p_trans:
                    n.state = 'I'
                    n.variant = self.variant
                    n.infection_time = self.model.t

class SIRModel(ap.Model):
    def setup(self):
        self.agents = ap.AgentList(self, self.p.n_agents, SIRAgent)
        self.space = ap.Space(self, (self.p.width, self.p.height))
        self.space.add_agents(self.agents, random=True)
        
        inf0 = int(0.1 * self.p.n_agents)
        self.agents[:inf0].state = 'I'
        self.agents[:inf0].infection_time = 0
        
        self.infected_history = []

    def step(self):
        self.agents.move()
        self.agents.interact()
        self.infected_history.append(sum(a.state == 'I' for a in self.agents))

if __name__ == "__main__":
    parameters = {
        'n_agents': 200, 'width': 20, 'height': 20, 
        'duration': 15
    }
    
    model = SIRModel(parameters)
    for i in range(100):
        model.step()
    
    plt.plot(model.infected_history)
    plt.title(f'SIR AgentPy - Pico: {max(model.infected_history)}')
    plt.ylabel('Infectados')
    plt.show()
    print(f"Pico de infetados: {max(model.infected_history)}")
