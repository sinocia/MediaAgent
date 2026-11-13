DEFAULT_WEIGHTS = {
    "trend": 0.30,
    "audience_need": 0.30,
    "competitive_advantage": 0.20,
    "monetization": 0.20,
}

def score_topic(*, trend: float, audience_need: float, competition: float,
                monetization: float, weights: dict[str, float] | None = None) -> dict:
    values = {
        "trend": trend,
        "audience_need": audience_need,
        "competitive_advantage": 10 - competition,
        "monetization": monetization,
    }
    dimensions = [trend, audience_need, competition, monetization]
    if any(not math.isfinite(v) or not 0 <= v <= 10 for v in dimensions):
        raise ValueError("All dimensions must be between 0 and 10")
    selected = weights or DEFAULT_WEIGHTS
    if set(selected) != set(DEFAULT_WEIGHTS):
        raise ValueError(f"Weights must contain: {', '.join(DEFAULT_WEIGHTS)}")
    if any(not math.isfinite(w) or w < 0 for w in selected.values()):
        raise ValueError("Weights cannot be negative")
    largest_weight = max(selected.values())
    if largest_weight <= 0:
        raise ValueError("Sum of weights must be greater than zero")
    # Scaling first avoids overflow when callers supply very large finite weights.
    scaled_weights = {key: value / largest_weight for key, value in selected.items()}
    total = sum(scaled_weights.values())
    score = sum(values[key] * scaled_weights[key] for key in values) / total
    return {"score": round(score, 2), "dimensions": values, "weights": selected, "scale": "0-10"}
import math

