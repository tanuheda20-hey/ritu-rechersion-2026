"""Daily symptom logs + the insight engine that turns them into something actionable."""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta

from fastapi import APIRouter, HTTPException, Query

import db
from schemas import LogCreate, LogOut
from services.insights import analyze, SYMPTOM_TAGS, RED_FLAGS, DISCLAIMER
from services import scenarios

router = APIRouter(tags=["logs"])


def _row_to_out(row) -> dict:
    d = dict(row)
    raw = d.get("symptoms") or "[]"
    try:
        d["symptoms"] = json.loads(raw) if isinstance(raw, str) else list(raw)
    except Exception:
        d["symptoms"] = []
    d["is_period_start"] = bool(d.get("is_period_start"))
    return d


@router.get("/symptoms", tags=["meta"])
def symptom_vocabulary() -> dict:
    """The frontend renders its logger from this, so the two can never drift."""
    grouped: dict[str, list[dict]] = {}
    for key, (label, cat) in SYMPTOM_TAGS.items():
        grouped.setdefault(cat, []).append({"key": key, "label": label})
    order = ["pain", "bleeding", "cycle", "mood", "systemic", "androgen",
             "metabolic", "neuro", "gastro", "cyclic", "red_flag"]
    return {
        "groups": [{"category": c, "label": c.replace("_", " ").title(), "symptoms": grouped[c]}
                   for c in order if c in grouped],
        "red_flags": RED_FLAGS,
        "disclaimer": DISCLAIMER,
    }


@router.get("/logs", response_model=list[LogOut])
def list_logs(profile: str = Query("me"), limit: int = Query(400, ge=1, le=1000)) -> list[dict]:
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM logs WHERE profile = ? ORDER BY log_date DESC LIMIT ?",
            (profile, limit),
        ).fetchall()
    return [_row_to_out(r) for r in rows]


@router.post("/logs", response_model=LogOut, status_code=201)
def create_log(payload: LogCreate) -> dict:
    # Cycle day derives from the most recent period start — including today's.
    start = db.latest_period_start(payload.profile, payload.log_date)
    if payload.is_period_start:
        cycle_day = 1
    elif start:
        d0 = datetime.strptime(start, "%Y-%m-%d").date()
        d1 = datetime.strptime(payload.log_date, "%Y-%m-%d").date()
        cycle_day = (d1 - d0).days + 1
        cycle_day = cycle_day if 1 <= cycle_day <= 60 else None
    else:
        cycle_day = None

    with db.get_conn() as conn:
        cur = conn.execute(
            """INSERT OR REPLACE INTO logs
               (profile, log_date, cycle_day, is_period_start, flow, pain, symptoms, notes)
               VALUES (?,?,?,?,?,?,?,?)""",
            (payload.profile, payload.log_date, cycle_day,
             int(payload.is_period_start), payload.flow, payload.pain,
             json.dumps(payload.symptoms), payload.notes),
        )
        row = conn.execute("SELECT * FROM logs WHERE id = ?", (cur.lastrowid,)).fetchone()

    # Recompute cycle days for later entries if a new period started.
    if payload.is_period_start:
        with db.get_conn() as conn:
            later = conn.execute(
                "SELECT id, log_date FROM logs WHERE profile = ? AND log_date > ? ORDER BY log_date",
                (payload.profile, payload.log_date),
            ).fetchall()
            d0 = datetime.strptime(payload.log_date, "%Y-%m-%d").date()
            for r in later:
                d1 = datetime.strptime(r["log_date"], "%Y-%m-%d").date()
                cd = (d1 - d0).days + 1
                conn.execute("UPDATE logs SET cycle_day = ? WHERE id = ?",
                             (cd if 1 <= cd <= 60 else None, r["id"]))

    return _row_to_out(row)


@router.delete("/logs/{log_id}")
def delete_log(log_id: int) -> dict:
    with db.get_conn() as conn:
        cur = conn.execute("DELETE FROM logs WHERE id = ?", (log_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"Log {log_id} not found")
    return {"deleted": log_id}


@router.get("/insights")
def get_insights(profile: str = Query("me")) -> dict:
    """⭐ The core flow: months of logs → patterns a doctor can act on."""
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM logs WHERE profile = ? ORDER BY log_date ASC", (profile,)
        ).fetchall()
    logs = [_row_to_out(r) for r in rows]
    return analyze(logs, profile=profile)


@router.get("/report")
def get_report(profile: str = Query("me")) -> dict:
    """One-page summary, ready to print or hand over in the appointment."""
    insights = get_insights(profile)
    return {
        "profile": profile,
        "urgency": insights["urgency"],
        "markdown": insights["report_markdown"],
        "disclaimer": DISCLAIMER,
    }


@router.post("/scenario")
def load_scenario(req: dict) -> dict:
    """
    Loads a realistic demo dataset. Lets you switch cases live on camera to
    prove the engine generalises rather than returning canned output.
    """
    scenario = req.get("scenario", "pcos")
    profile = req.get("profile", "me")
    if scenario not in scenarios.SCENARIOS:
        raise HTTPException(status_code=422, detail=f"Unknown scenario '{scenario}'")
    rows = scenarios.build(scenario, profile)
    db.reset_profile(profile)
    db.insert_logs(rows)
    return {
        "scenario": scenario,
        "profile": profile,
        "days": len(rows),
        "description": scenarios.SCENARIOS[scenario]["description"],
        "insights": get_insights(profile),
    }
