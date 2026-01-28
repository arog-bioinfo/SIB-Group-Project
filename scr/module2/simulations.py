import numpy as np
import pandas as pd

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from IPython.display import HTML

def run_and_store(model, steps):
    """
    Runs a model and stores agent positions and states at each step.
    Returns:
        frames: list of arrays (N, 3) -> x, y, state
        df: datacollector dataframe
    """
    frames = []

    for _ in range(steps):
        snapshot = []
        for agent in model.agents:
            x, y = agent.pos
            snapshot.append((x, y, agent.state.value))
        frames.append(np.array(snapshot))
        model.step()

    df = model.datacollector.get_model_vars_dataframe()
    return frames, df

def animate_frames(frames, width, height, interval=100, regions=None):
    fig, ax = plt.subplots()
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_title("Agent-Based Model – Moving Points")

    # ---- draw country borders (static) ----
    if regions:
        for r in regions:
            rect = plt.Rectangle(
                (r["x_min"], r["y_min"]),
                r["x_max"] - r["x_min"],
                r["y_max"] - r["y_min"],
                fill=False,
                linewidth=2,
            )
            ax.add_patch(rect)

        # optional labels
        for r in regions:
            cx = (r["x_min"] + r["x_max"]) / 2
            cy = (r["y_min"] + r["y_max"]) / 2
            ax.text(cx, cy, r["name"], ha="center", va="center", alpha=0.6)

    scatter = ax.scatter([], [], s=30)

    def color_map(states):
        # 0: Susceptible (green), 1: Infected (red), 2: Resistant (gray)
        return np.where(
            states == 1, "red",
            np.where(states == 2, "gray", "green")
        )

    def update(frame_idx):
        data = frames[frame_idx]
        scatter.set_offsets(data[:, :2])
        scatter.set_color(color_map(data[:, 2].astype(int)))
        ax.set_xlabel(f"Step {frame_idx}")
        return scatter,

    anim = FuncAnimation(
        fig, update, frames=len(frames),
        interval=interval, blit=True
    )
    plt.close(fig)
    return HTML(anim.to_jshtml())

def run_n_sims_mean_df(
    bridge,
    module1_params,
    module2_params,
    steps: int,
    n_sims: int = 10,
):
    dfs = []

    for i in range(n_sims):

        module2_params_run = module2_params

        model, fitness = bridge.build_model(module1_params, module2_params_run)
        frames, df = run_and_store(model, steps)

        df = df.copy()
        df["sim"] = i
        dfs.append(df)

    # Stack and average by timestep (index)
    all_df = pd.concat(dfs, axis=0)
    mean_df = all_df.groupby(all_df.index).mean(numeric_only=True)

    return mean_df, all_df