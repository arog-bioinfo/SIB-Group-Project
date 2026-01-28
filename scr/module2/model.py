import math
from abc import ABC, abstractmethod

from mesa import Model
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector

from .borderedspace import BorderedContinuousSpace
from .agents import State, VirusAgentContinuous


def number_state(model, state):
    return sum(1 for a in model.agents if a.state is state)

def number_infected(model):
    return number_state(model, State.INFECTED)

def number_susceptible(model):
    return number_state(model, State.SUSCEPTIBLE)

def number_resistant(model):
    return number_state(model, State.RESISTANT)


class VirusModelContinuousBase(Model, ABC):
    """
    Base moving-dots ABM (no measures/policy logic here):
    - agents move in ContinuousSpace (normal) or BorderedContinuousSpace (countries)
    - infection spreads within a radius
    - transmissibility is controlled by `virus_spread_chance`
      (set by subclasses via `_configure_measures_impact()`).
    """

    def __init__(
        self,
        N=200,
        width=100,
        height=100,
        initial_outbreak_size=5,

        base_virus_spread_chance=0.65,

        # ABM params:
        infection_radius=2.0,
        movement_speed=1.0,
        virus_check_frequency=0.4,
        recovery_chance=0.3,
        gain_resistance_chance=0.75,
        rng=None,

        # Space params:
        use_borders: bool = False,
        torus: bool = True,                       # used only for normal ContinuousSpace
        regions: list[dict] | None = None,         # used only if use_borders=True
        block_out_of_bounds: bool = True,          # used only if use_borders=True (torus forced False)
        block_cross_border: bool = True,           # used only if use_borders=True
        border_cross_prob: float = 0.0,            # chance to cross into another region on an attempted crossing
        x_min: float = 0.0,
        y_min: float = 0.0,
        border_rng=None,                           # optional random.Random for deterministic border crossing
    ):
        super().__init__(rng=rng)

        self.N = N
        self.width = width
        self.height = height

        # --------------------
        # Space selection
        # --------------------
        if use_borders:
            # Borders + torus is conceptually inconsistent; enforce non-toroidal
            self.space = BorderedContinuousSpace(
                x_max=width,
                y_max=height,
                torus=False,
                x_min=x_min,
                y_min=y_min,
                regions=regions or [],
                block_out_of_bounds=block_out_of_bounds,
                block_cross_border=block_cross_border,
                border_cross_prob=border_cross_prob,
                rng=border_rng,
            )
            # keep for viz / downstream use
            self.regions = list(regions or [])
        else:
            self.space = ContinuousSpace(
                x_max=width,
                y_max=height,
                torus=torus,
                x_min=x_min,
                y_min=y_min,
            )
            self.regions = None

        # --------------------
        # Baseline transmissibility
        # --------------------
        self.base_virus_spread_chance = base_virus_spread_chance
        self.virus_spread_chance = None

        # --------------------
        # ABM params
        # --------------------
        self.infection_radius = infection_radius
        self.movement_speed = movement_speed
        self.virus_check_frequency = virus_check_frequency
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance

        # Apply measures impact (subclass hook)
        self._configure_measures_impact()

        # --------------------
        # Create agents
        # --------------------
        self.agents_list = []
        for _ in range(N):
            a = VirusAgentContinuous(model=self, initial_state=State.SUSCEPTIBLE)
            self.agents_list.append(a)

            # If borders are on, placement must be inside one of the regions.
            # Ensure regions cover the full map or adjust sampling to region interiors.
            x = self.random.random() * width
            y = self.random.random() * height
            self.space.place_agent(a, (x, y))

        initial_outbreak_size = min(initial_outbreak_size, len(self.agents_list))
        initial_infected = self.random.sample(self.agents_list, initial_outbreak_size)

        cx = self.random.random() * self.width
        cy = self.random.random() * self.height
        spread = 3.0  # how tight the cluster is

        for agent in initial_infected:
            dx = self.random.uniform(-spread, spread)
            dy = self.random.uniform(-spread, spread)
            self.space.move_agent(agent, (cx + dx, cy + dy))
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
        return self._agents

    def resistant_susceptible_ratio(self):
        try:
            return number_resistant(self) / number_susceptible(self)
        except ZeroDivisionError:
            return math.inf

    @abstractmethod
    def _configure_measures_impact(self) -> None:
        """Subclasses set measures impact on model parameters here."""
        raise NotImplementedError

    def step(self):
        for a in self._agents:
            a.step()
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

    @abstractmethod
    def _configure_measures_impact(self) -> None:
        """
        Subclasses must set the measures impact on the model here.
        Example:
            self.virus_spread_chance = self.base_virus_spread_chance * (1 - measure_index)
        """

    def step(self):
        for a in self._agents:
            a.step()
        self.datacollector.collect(self)

class VirusModelContinuousMeasuresIndex(VirusModelContinuousBase):
    def __init__(self, measures_index=0.0, **kwargs):
        self.measures_index = self._validate_01("measures_index", measures_index)
        super().__init__(**kwargs)

    def _configure_measures_impact(self):
        self.virus_spread_chance = self.base_virus_spread_chance * (1 - self.measures_index)
        
    @staticmethod
    def _validate_01(name: str, value: float) -> float:
        value = float(value)
        if not 0.0 <= value <= 1.0:
            raise ValueError(
                f"{name} must be in the interval [0, 1], got {value}"
            )
        return value
    
class VirusModelContinuousSpecificMeasures(VirusModelContinuousBase):
    """
    Policy-specific measures model:
      - masks: reduces transmissibility
      - confinement: reduces movement_speed (fewer contacts)
      - vaccination: increases chance to gain resistance

    All measure intensities are floats in [0, 1].
    """

    def __init__(
        self,
        masks: bool = False,     # FALSE..TRUE (compliance/intensity)
        confinement: bool = False,       # FALSE..TRUE (0 none, 1 strict)
        vaccination: bool = False,       # FALSE..TRUE (coverage/intensity)
        **kwargs,
    ):
        # store measures (validate rather than clamp)
        self.masks = bool(masks)
        self.confinement = bool(confinement)
        self.vaccination = bool(vaccination)

        super().__init__(**kwargs)


    def _configure_measures_impact(self) -> None:
        """
        Map measures -> model parameters.

        You can tune these coefficients to match your scenario assumptions.
        """
        # --- Transmissibility impact ---

        if self.masks:
            self.virus_spread_chance = self.base_virus_spread_chance * 0.25


        # --- Mobility impact ---

        if self.confinement:
            self.movement_speed -= 0.3

        # --- Resistance impact ---

        if self.vaccination:
            self.gain_resistance_chance += 0.3
