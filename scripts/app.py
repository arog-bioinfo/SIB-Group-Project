import math
import solara

from mesa.visualization import SolaraViz, Slider, SpaceRenderer, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle

from model import VirusModelContinuous, State  # <-- your continuous model


def agent_portrayal(agent):
    color = {
        State.INFECTED: "red",
        State.SUSCEPTIBLE: "green",
        State.RESISTANT: "gray",
    }[agent.state]

    # size controls dot size; marker circle makes it look like “bolinhas”
    return AgentPortrayalStyle(color=color, size=40, marker="circle")


def get_resistant_susceptible_ratio(model):
    # if your continuous model doesn't have this method, remove this component
    ratio = model.resistant_susceptible_ratio()
    ratio_text = r"$\infty$" if ratio is math.inf else f"{ratio:.2f}"
    infected_text = str(model.number_infected())  # implement in model.py or adapt
    return solara.Markdown(
        f"Resistant/Susceptible Ratio: {ratio_text}<br>Infected Remaining: {infected_text}"
    )


model_params = {
    "rng": {"type": "InputText", "value": 42, "label": "Random Seed"},
    "N": Slider("Number of agents", value=200, min=50, max=1000, step=10),

    # Module 1 → Module 2 link can be represented as a slider for now
    # Later you replace it with the real Module 1 output
    "measures_index": Slider("Measures Index (Module 1)", value=0.0, min=0.0, max=1.0, step=0.05),

    # base virus transmissibility (without measures)
    "base_virus_spread_chance": Slider("Base Virus Spread Chance", value=0.25, min=0.0, max=1.0, step=0.01),

    # movement policy (stay home => slower)
    "movement_speed": Slider("Movement speed (stay home)", value=1.0, min=0.0, max=5.0, step=0.1),

    "virus_check_frequency": Slider("Virus Check Frequency", value=0.4, min=0.0, max=1.0, step=0.05),
    "recovery_chance": Slider("Recovery Chance", value=0.3, min=0.0, max=1.0, step=0.05),
    "gain_resistance_chance": Slider("Gain Resistance Chance", value=0.5, min=0.0, max=1.0, step=0.05),
}


def post_process_lineplot(chart):
    return chart.properties(width=400, height=400).configure_legend(
        strokeColor="black",
        fillColor="#ECE9E9",
        orient="right",
        cornerRadius=5,
        padding=10,
        strokeWidth=1,
    )


# Instantiate the *continuous* model (dots move because the model moves agents each step)
model1 = VirusModelContinuous(
    N=200,
    measures_index=0.0,
    base_virus_spread_chance=0.25,
    movement_speed=1.0,
    virus_check_frequency=0.4,
    recovery_chance=0.3,
    gain_resistance_chance=0.5,
    rng=42,
)

# Renderer: NO setup_structure (that was only for networks)
renderer = SpaceRenderer(model1, backend="altair").setup_agents(agent_portrayal)

# Optional: line plot of counts if your model collects them
StatePlot = make_plot_component(
    {"Infected": "red", "Susceptible": "green", "Resistant": "gray"},
    backend="altair",
    post_process=post_process_lineplot,
)

page = SolaraViz(
    model1,
    renderer,
    components=[
        StatePlot,
        # get_resistant_susceptible_ratio,  # enable only if your model implements it
    ],
    model_params=model_params,
    name="Moving Dots Virus Model",
)

page
