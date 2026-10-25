"""CLI: load a demo scenario. `python seed.py pcos`"""
from __future__ import annotations

import sys

import db
from services import scenarios
from services.insights import analyze


def load(scenario: str, profile: str = "me") -> None:
    if scenario not in scenarios.SCENARIOS:
        raise SystemExit(f"Unknown scenario '{scenario}'. Choose from: {', '.join(scenarios.SCENARIOS)}")
    db.init_db()
    db.reset_profile(profile)
    rows = scenarios.build(scenario, profile)
    db.insert_logs(rows)

    with db.get_conn() as conn:
        stored = conn.execute(
            "SELECT * FROM logs WHERE profile = ? ORDER BY log_date", (profile,)
        ).fetchall()
    logs = [dict(r) for r in stored]
    result = analyze(logs, profile=profile)

    cfg = scenarios.SCENARIOS[scenario]
    print(f"\n{'='*70}\n  {cfg['label']}\n{'='*70}")
    print(f"  {cfg['description']}")
    print(f"\n  Seeded {len(rows)} days of logs for profile '{profile}'\n")
    cs = result["cycle_stats"]
    print(f"  Cycles logged      : {cs['period_starts']}")
    print(f"  Avg cycle length   : {cs['avg_cycle_length']} days")
    print(f"  Cycle variability  : {cs['cycle_variability_days']} days")
    print(f"  Irregular          : {cs['irregular_cycles']}")
    print(f"  Heavy bleeding days: {cs['heavy_bleeding_days']}")
    print(f"  Avg / peak pain    : {cs['avg_pain']} / {cs['max_pain']}")
    print(f"\n  Urgency: {result['urgency']['label'].upper()} — {result['urgency']['advice']}\n")
    if result["signals"]:
        print("  SIGNALS DETECTED")
        for s in result["signals"]:
            print(f"    • [{s['strength'].upper():8}] {s['name']}")
            for e in s["evidence"]:
                print(f"        - {e}")
    else:
        print("  No signals detected (correctly — this is the healthy scenario).")
    print()


if __name__ == "__main__":
    load(sys.argv[1] if len(sys.argv) > 1 else "pcos",
         sys.argv[2] if len(sys.argv) > 2 else "me")
