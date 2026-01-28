from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Type


@dataclass
class FitnessToABMMapping:
    """
    Multiply module-1 fitness with base ABM spread chance.

    effective_spread = base_spread * fitness
    """
    target_param_name: str = "base_virus_spread_chance"
    min_clip: float = 0.0
    max_clip: float = 1.0

    def apply(self, fitness_score: float, module2_params: Dict[str, Any]) -> Dict[str, Any]:
        f = float(fitness_score)
        f = max(0.0, min(1.0, f))  # clamp fitness

        module2_params = dict(module2_params)  # copy

        if self.target_param_name not in module2_params:
            raise KeyError(
                f"'{self.target_param_name}' must exist in module2_params "
                "for multiplicative mapping."
            )

        base = float(module2_params[self.target_param_name])
        spread = base * f
        spread = max(self.min_clip, min(self.max_clip, spread))

        module2_params[self.target_param_name] = spread
        return module2_params



class Module1Module2Bridge:
    """
    Bridge class: compute viral fitness (Module 1) and configure ABM (Module 2).

    Inputs:
      - module1_params: dict with keys like:
            {"clade": "BA.2", "geo": "Brazil", "days_since_start": 760}
      - module2_params: dict with ABM model init args like:
            {"N": 200, "width": 100, "height": 100, "recovery_chance": 0.05, ...}

    Usage:
      bridge = Module1Module2Bridge(
          abm_model_cls=VirusModelContinuousMeasuresIndex,
          fitness_fn=calculate_viral_fitness,
      )
      model, fitness = bridge.build_model(module1_params, module2_params)
    """

    def __init__(
        self,
        *,
        abm_model_cls: Type[Any],
        fitness_fn: Callable[[str, str, int, Dict[str, Any]], Dict[str, Any]],
        mapping: Optional[FitnessToABMMapping] = None,
    ):
        self.abm_model_cls = abm_model_cls
        self.fitness_fn = fitness_fn
        self.mapping = mapping or FitnessToABMMapping()

    # ---------
    # Core API
    # ---------
    def compute_fitness(self, module1_params: Dict[str, Any]) -> Dict[str, Any]:
        clade = module1_params["clade"]
        geo = module1_params["geo"]
        days = int(module1_params["days_since_start"])

        model_artifact = module1_params.get("model_artifact") or module1_params.get("model")
        if model_artifact is None:
            raise KeyError("module1_params must include 'model_artifact' (or legacy key 'model').")

        return self.fitness_fn(clade, geo, days, model_artifact)


    def build_model(
        self,
        module1_params: Dict[str, Any],
        module2_params: Dict[str, Any],
        *,
        override: Optional[Dict[str, Any]] = None,
    ):
        """
        Returns:
          (model_instance, fitness_result_dict)
        """
        fitness_result = self.compute_fitness(module1_params)
        fitness_score = fitness_result["fitness_score"]

        # Map fitness -> ABM params (e.g., base_virus_spread_chance)
        merged_module2 = self.mapping.apply(fitness_score, module2_params)

        # Optional manual overrides (highest priority)
        if override:
            merged_module2.update(override)

        model = self.abm_model_cls(**merged_module2)
        return model, fitness_result