from typing import Dict
import numpy as np
import pandas as pd

from sklearn.preprocessing import OneHotEncoder
from sklearn.decomposition import PCA
import xgboost as xgb

def fitness_power(muts: float, mmin: float = 0.0, mmax: float = 50.0, gamma: float = 3.0) -> float:
    f = (muts - mmin) / (mmax - mmin)
    f = np.clip(f, 0.0, 1.0)
    return float(f ** gamma)


def calculate_viral_fitness(clade, geo, days_since_start, model_artifact):
    xgb_model = model_artifact["model"]
    pca = model_artifact["pca"]
    oh = model_artifact["onehotencoder"]

    # Use the exact column names the OneHotEncoder saw during fit
    cols = list(oh.feature_names_in_)

    # Mapping
    row = {}
    for c in cols:
        lc = c.lower()
        if "clade" in lc:
            row[c] = clade
        elif "geo" in lc or "geographic" in lc or "location" in lc:
            row[c] = geo
        elif "day" in lc:
            row[c] = int(days_since_start)
        else:
            raise KeyError(f"Don't know how to populate required feature column: {c}")

    X_cat_df = pd.DataFrame([row], columns=cols)
    X_cat = oh.transform(X_cat_df)

    X_emb_pca = np.zeros((X_cat.shape[0], pca.n_components_))
    X_full = np.hstack([X_emb_pca, X_cat])

    predicted_mutations = float(xgb_model.predict(X_full)[0])

    fitness_score = fitness_power(predicted_mutations, mmin=0.0, mmax=50.0, gamma=0.6)

    return {
        "clade": clade,
        "geo": geo,
        "days": int(days_since_start),
        "predicted_mutations": predicted_mutations,
        "fitness_score": fitness_score,
    }
