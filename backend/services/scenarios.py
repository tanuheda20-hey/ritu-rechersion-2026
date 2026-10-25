"""
Realistic demo datasets.

Each scenario is three cycles of plausible daily logs. Switching between them
live during the demo proves the engine generalises instead of returning canned
output — which is exactly what a judge is trying to find out.
"""
from __future__ import annotations

import json
from datetime import date, timedelta


def _pcos(day: int, L: int, gi: int) -> tuple[str, int, list[str]]:
    flow = ["medium", "medium", "light", "light", "spotting"][day] if day < 5 else "none"
    pain = 4 if day < 2 else (2 if day < 4 else 0)
    syms: list[str] = []
    if day < 3:
        syms.append("cramps")
    if gi % 3 == 0:
        syms.append("acne")
    if gi % 6 == 0:
        syms.append("hair_loss")
    if gi % 9 == 0:
        syms.append("weight_gain")
    if gi % 4 == 0:
        syms.append("fatigue")
    if day > 16 and gi % 6 == 0:
        syms.append("mood_swings")
    if day <= 14 and gi % 5 == 0:
        syms.append("low_mood")
    if gi % 5 == 0:
        syms.append("bloating")
    return flow, pain, syms


def _endometriosis(day: int, L: int, gi: int) -> tuple[str, int, list[str]]:
    flow = ["heavy", "heavy", "medium", "light", "spotting"][day] if day < 5 else "none"
    pain = 9 if day < 2 else (7 if day == 2 else (4 if day == 3 else (5 if day in (11, 13, 15) else 0)))
    syms: list[str] = []
    if day < 4:
        syms.append("cramps")
    if day in (11, 13, 15):
        syms.append("pelvic_pain")
    if gi % 8 == 0:
        syms.append("pain_intercourse")
    if gi % 4 == 0:
        syms.append("fatigue")
    if day < 3:
        syms.append("heavy_clots")
    if gi % 5 == 0:
        syms.append("lower_back_pain")
    if day > 18 and gi % 4 == 0:
        syms.append("low_mood")
    if day <= 14 and gi % 9 == 0:
        syms.append("low_mood")
    return flow, pain, syms


def _anaemia(day: int, L: int, gi: int) -> tuple[str, int, list[str]]:
    flow = ["very_heavy", "very_heavy", "heavy", "heavy", "medium", "light", "spotting"][day] if day < 7 else "none"
    pain = 5 if day < 3 else (3 if day < 5 else 0)
    syms: list[str] = []
    if day < 4:
        syms.append("cramps")
    if day < 3:
        syms.append("heavy_clots")
    if day < 2:
        syms.append("soaking_through")
    if gi % 3 == 0:
        syms.append("fatigue")
    if gi % 5 == 0:
        syms.append("dizziness")
    if gi % 6 == 0:
        syms.append("headache")
    if gi % 8 == 0:
        syms.append("brain_fog")
    return flow, pain, syms


def _healthy(day: int, L: int, gi: int) -> tuple[str, int, list[str]]:
    flow = ["medium", "medium", "light", "light", "spotting"][day] if day < 5 else "none"
    pain = 3 if day == 0 else (2 if day == 1 else 0)
    syms: list[str] = []
    if day < 2:
        syms.append("cramps")
    if day > 18:
        syms.append("breast_tenderness")
    if gi % 7 == 0:
        syms.append("bloating")
    return flow, pain, syms


SCENARIOS: dict[str, dict] = {
    "pcos": {
        "label": "Priya, 21 — irregular cycles",
        "description": "Cycles of 34–52 days with acne, hair thinning, weight gain and fatigue. "
                       "The classic pattern that gets dismissed as 'stress'.",
        "cycles": [34, 52, 29, 41],
        "day_fn": _pcos,
    },
    "endometriosis": {
        "label": "Ananya, 24 — severe pain",
        "description": "Regular cycles, but pain 9/10 for two days each month, off-period "
                       "pelvic pain and pain during intercourse. Told for years it was normal.",
        "cycles": [28, 28, 27, 29],
        "day_fn": _endometriosis,
    },
    "anaemia": {
        "label": "Meera, 27 — heavy bleeding",
        "description": "Seven-day periods with clots and soaking through, plus fatigue, "
                       "dizziness and headaches. Iron loss that is rarely tested for.",
        "cycles": [28, 28, 28, 28],
        "day_fn": _anaemia,
    },
    "healthy": {
        "label": "Ishita, 22 — no strong pattern",
        "description": "Regular cycles, mild cramps, no systemic symptoms. Included to show "
                       "the engine does NOT fire when there is nothing to find.",
        "cycles": [28, 28, 29, 28],
        "day_fn": _healthy,
    },
}


def build(scenario: str, profile: str = "me") -> list[tuple]:
    """Returns rows ready for db.insert_logs."""
    cfg = SCENARIOS[scenario]
    cycles: list[int] = cfg["cycles"]
    total = sum(cycles)

    start = date.today() - timedelta(days=total - 4)
    rows: list[tuple] = []
    gi = 0
    d = start
    for L in cycles:
        for day in range(L):
            ld = d + timedelta(days=day)
            if ld > date.today():
                break
            flow, pain, syms = cfg["day_fn"](day, L, gi)
            rows.append((
                profile,
                ld.isoformat(),
                day + 1,
                1 if day == 0 else 0,
                flow,
                pain,
                json.dumps(syms),
                "",
            ))
            gi += 1
        d += timedelta(days=L)
    return rows
