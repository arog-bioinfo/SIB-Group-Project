from __future__ import annotations

from typing import Optional
import random

from mesa.space import ContinuousSpace


class BorderedContinuousSpace(ContinuousSpace):
    """
    Mesa ContinuousSpace + rectangular 'country' regions + optional probabilistic crossing.

    regions: list of dicts like:
      {"name": "Portugal", "x_min": 0, "x_max": 50, "y_min": 0, "y_max": 100}

    Key behavior:
      - torus=False recommended for geography.
      - Out-of-bounds moves:
          - blocked if block_out_of_bounds=True
          - else raise (Mesa default)
      - If regions are provided:
          - agents are assigned a region at placement time
          - cross-border moves are:
              - blocked if block_cross_border=True AND border_cross_prob == 0
              - allowed with probability border_cross_prob if attempting to change region
    """

    def __init__(
        self,
        x_max: float,
        y_max: float,
        torus: bool,
        x_min: float = 0,
        y_min: float = 0,
        *,
        regions: Optional[list[dict]] = None,
        block_out_of_bounds: bool = True,
        block_cross_border: bool = True,
        border_cross_prob: float = 0.0,   # 0..1 chance to cross when move enters a different region
        rng: Optional[random.Random] = None,
    ) -> None:
        super().__init__(x_max=x_max, y_max=y_max, torus=torus, x_min=x_min, y_min=y_min)

        if not 0.0 <= border_cross_prob <= 1.0:
            raise ValueError(f"border_cross_prob must be in [0,1], got {border_cross_prob}")

        self.block_out_of_bounds = block_out_of_bounds
        self.block_cross_border = block_cross_border
        self.border_cross_prob = float(border_cross_prob)

        # If you want deterministic runs, pass a seeded random.Random here.
        # If None, we will fall back to agent.random / model.random when available.
        self._rng = rng

        self.regions = list(regions or [])
        if self.regions:
            self._validate_regions(self.regions)

        # agent -> region name
        self._agent_region: dict[object, str] = {}

    # -------------------------
    # Placement / movement
    # -------------------------
    def place_agent(self, agent, pos):
        if not self.torus and self.out_of_bounds(pos):
            raise ValueError(f"Cannot place agent at {pos}: out of bounds.")

        if self.torus:
            pos = self.torus_adj(pos)

        if self.regions:
            region = self._region_of_pos(pos)
            if region is None:
                raise ValueError(f"Cannot place agent at {pos}: not inside any region.")

        super().place_agent(agent, pos)

        if self.regions:
            self._agent_region[agent] = self._region_of_pos(agent.pos)

    def move_agent(self, agent, pos):
        # World boundary handling
        if self.torus:
            pos = self.torus_adj(pos)
        else:
            if self.out_of_bounds(pos):
                if self.block_out_of_bounds:
                    return
                raise Exception("Point out of bounds, and space non-toroidal.")

        # Region handling
        if self.regions:
            current_region = self._agent_region.get(agent)
            new_region = self._region_of_pos(pos)
            if new_region is None:
                return  # outside defined regions -> block

            # Attempting to cross a border
            if current_region is not None and new_region != current_region:
                if self.block_cross_border:
                    # Allow probabilistic crossing if configured
                    if self.border_cross_prob <= 0.0:
                        return

                    if not self._draw(agent) < self.border_cross_prob:
                        return  # crossing attempt rejected

                # else: block_cross_border=False -> always allow

        super().move_agent(agent, pos)

        # Update region membership after a successful move
        if self.regions:
            new_region = self._region_of_pos(agent.pos)
            if new_region is not None:
                self._agent_region[agent] = new_region

    def remove_agent(self, agent):
        super().remove_agent(agent)
        self._agent_region.pop(agent, None)

    # -------------------------
    # Neighbors (optional filter)
    # -------------------------
    def get_neighbors(self, pos, radius, include_center=True, *, same_country_only=False):
        neighbors = super().get_neighbors(pos, radius, include_center=include_center)

        if not same_country_only or not self.regions:
            return neighbors

        region = self._region_of_pos(pos)
        return [a for a in neighbors if self._agent_region.get(a) == region]

    # -------------------------
    # RNG helper (prefers Mesa RNG if available)
    # -------------------------
    def _draw(self, agent) -> float:
        """
        Return a uniform random float in [0,1).
        Preference order:
          1) self._rng if provided
          2) agent.random if available (Mesa Agent has .random)
          3) Python's global random (last resort)
        """
        if self._rng is not None:
            return self._rng.random()
        if hasattr(agent, "random") and agent.random is not None:
            return agent.random.random()
        return random.random()

    # -------------------------
    # Region helpers
    # -------------------------
    def _region_of_pos(self, pos):
        x, y = pos
        for r in self.regions:
            if (r["x_min"] <= x < r["x_max"]) and (r["y_min"] <= y < r["y_max"]):
                return r["name"]
        return None

    @staticmethod
    def _validate_regions(regions):
        required = {"name", "x_min", "x_max", "y_min", "y_max"}
        for r in regions:
            missing = required - set(r.keys())
            if missing:
                raise ValueError(f"Region missing keys {missing}: {r}")
            if not (r["x_min"] < r["x_max"] and r["y_min"] < r["y_max"]):
                raise ValueError(f"Invalid region bounds: {r}")