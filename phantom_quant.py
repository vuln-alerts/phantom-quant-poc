import json
from typing import Dict

def detect_gap(data: Dict) -> Dict:

    expected = data.get("expected_direction")
    actual = data.get("actual_direction")

    gap = expected != actual

    gap_score = 1.0 if gap else 0.0

    if gap:
        explanation = (
            f"Expected '{expected}' but actual '{actual}'. "
            f"Structural inconsistency detected."
        )
    else:
        explanation = "No structural gap detected."

    return {
        "gap": gap,
        "gap_score": gap_score,
        "explanation": explanation,
        "input": data
    }

if __name__ == "__main__":

    sample = {
        "expected_direction": "up",
        "actual_direction": "down",
        "context": "AI demand increasing",
        "metric": "semiconductor price"
    }

    result = detect_gap(sample)

    print(json.dumps(result, indent=2))
