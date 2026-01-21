import mesa
import matplotlib.pyplot as plt
import numpy as np

class SIRAgent(mesa.Agent):
    def __init__(self, unique_id, model, variant='Wild', fitness=1.0):
        super().__init__(unique_id, model)
        self.state = 'S'  # S, I, R
        self.variant = variant
        self.fitness = fitness
        self.infection_time = 0
        self.p_trans = 0.3 * fitness

    def step(self):
        if self.state == 'I':
            if self.model.schedule.time - self.infection_time > self.model.duration:
                self.state = 'R'
            neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
            for n in neighbors:
                if n.state == 'S' and self.model.random.random() < self.p_trans:
                    n.state = 'I'
                    n.variant = self.variant
                    n.infection_time = self.model.schedule.time

class SIRModel(mesa.Model):
    def __init__(self, N=50, width=10, height=10, infected=5, duration=10, intervention=False):
        self.num_agents = N
        self.duration = duration
        self.intervention = intervention
        
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.datacollector = mesa.DataCollector(
            model_reporters={'Infected': lambda m: sum(1 for a in m.schedule.agents if a.state=='I')}
        )
        
        for i in range(self.num_agents):
            variant = 'Wild' if i < infected else 'Wild'
            fitness = 1.0 if i < infected else 0.8  # Módulo 1
            a = SIRAgent(i, self, variant, fitness)
            x = self.random.integers(0, width)
            y = self.random.integers(0, height)
            self.grid.position_agent(a, (x, y))
            self.schedule.add(a)
            if i < infected:
                a.state = 'I'
                a.infection_time = 0
        
        self.datacollector.collect(self)
        self.running = True

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        if sum(1 for a in self.schedule.agents if a.state == 'I') == 0:
            self.running = False

# Rodar
model = SIRModel(intervention=False)
while model.running and model.schedule.time < 100:
    model.step()

df = model.datacollector.get_model_vars_dataframe()
plt.plot(df['Infected'])
plt.title('Mesa SIR')
plt.show()
print("Pico:", df['Infected'].max())