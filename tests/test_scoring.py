import pytest
from app.scoring import score_topic

def test_score_is_on_zero_to_ten_scale():
    result = score_topic(trend=8, audience_need=9, competition=6, monetization=8)
    assert result["score"] == 7.9
    assert 0 <= result["score"] <= 10

def test_lower_competition_scores_better():
    common = dict(trend=5, audience_need=5, monetization=5)
    assert score_topic(**common, competition=2)["score"] > score_topic(**common, competition=9)["score"]

def test_invalid_weights_rejected():
    with pytest.raises(ValueError):
        score_topic(trend=5, audience_need=5, competition=5, monetization=5, weights={"bad": 1})

def test_non_finite_inputs_rejected():
    with pytest.raises(ValueError):
        score_topic(trend=float("nan"), audience_need=5, competition=5, monetization=5)
    with pytest.raises(ValueError):
        score_topic(trend=5, audience_need=5, competition=5, monetization=5,
                    weights={"trend": float("inf"), "audience_need": 1,
                             "competitive_advantage": 1, "monetization": 1})
