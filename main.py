#!/usr/bin/env python3
"""
PhantomQuant - Structural Gap Detection Engine
Detects inconsistencies between expected and actual behavior.
Not a prediction engine — a coherence verification engine.

Usage:
    python phantom_quant.py '{"expected_direction":"up","actual_direction":"down","context":"AI demand increasing","metric":"semiconductor price"}'
    echo '{"expected_direction":"up","actual_direction":"up","context":"demand rising","metric":"stock price"}' | python phantom_quant.py
    python phantom_quant.py --demo
"""

import json
import sys


VALID_DIRECTIONS = {"up", "down", "stable", "increase", "decrease", "positive", "negative", "pass", "fail"}

SAMPLE_INPUTS = [
    {
        "expected_direction": "up",
        "actual_direction": "down",
        "context": "AI demand increasing",
        "metric": "semiconductor price",
    },
    {
        "expected_direction": "pass",
        "actual_direction": "pass",
        "context": "all unit tests green",
        "metric": "production deployment",
    },
    {
        "expected_direction": "stable",
        "actual_direction": "down",
        "context": "system under normal load",
        "metric": "API response time",
    },
]


def normalize(direction: str) -> str:
    return direction.strip().lower()


def detect_gap(expected: str, actual: str) -> tuple[bool, float]:
    """
    Core logic: compare expected vs actual direction.
    Returns (gap_detected, gap_score).
    gap_score: 1.0 = full mismatch, 0.0 = full match.
    """
    if normalize(expected) != normalize(actual):
        return True, 1.0
    return False, 0.0


def build_explanation(expected: str, actual: str, context: str, metric: str, gap: bool) -> str:
    if not gap:
        return f"Expected '{expected}', actual '{actual}' — coherent. [{metric}]"
    return f"Expected '{expected}' but got '{actual}' — gap detected. [{metric}] Context: {context}"


def validate_input(data: dict) -> list[str]:
    errors = []
    required = ["expected_direction", "actual_direction", "context", "metric"]
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")
        elif not isinstance(data[field], str) or not data[field].strip():
            errors.append(f"Field '{field}' must be a non-empty string")
    return errors


def analyze(data: dict) -> dict:
    errors = validate_input(data)
    if errors:
        return {"error": errors}

    expected = data["expected_direction"].strip()
    actual = data["actual_direction"].strip()
    context = data["context"].strip()
    metric = data["metric"].strip()

    gap, gap_score = detect_gap(expected, actual)
    explanation = build_explanation(expected, actual, context, metric, gap)

    return {
        "gap": gap,
        "gap_score": gap_score,
        "explanation": explanation,
        "input": {
            "expected_direction": expected,
            "actual_direction": actual,
            "context": context,
            "metric": metric,
        },
    }


def run_demo():
    print("=" * 60)
    print("PhantomQuant — Demo Mode")
    print("=" * 60)
    for i, sample in enumerate(SAMPLE_INPUTS, 1):
        print(f"\n[Sample {i}] Input:")
        print(json.dumps(sample, indent=2, ensure_ascii=False, separators=(",", ": ")))
        result = analyze(sample)
        print(f"\n[Sample {i}] Output:")
        print(json.dumps(result, indent=2, ensure_ascii=False, separators=(",", ": ")))
        print("-" * 60)


def main():
    args = sys.argv[1:]

    if not args:
        # Try reading from stdin
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
        else:
            print(__doc__, file=sys.stderr)
            sys.exit(1)
    elif args[0] == "--demo":
        run_demo()
        return
    elif args[0] in ("-h", "--help"):
        print(__doc__)
        return
    else:
        raw = " ".join(args)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        result = {"error": f"Invalid JSON input: {e}"}
        print(json.dumps(result, indent=2))
        sys.exit(1)

    result = analyze(data)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result.get("gap"):
        sys.exit(2)  # Non-zero exit signals detected gap (useful for CI pipelines)


if __name__ == "__main__":
    main()
