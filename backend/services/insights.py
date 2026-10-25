"""
Ritu — symptom pattern engine.

WHY A RULE ENGINE, NOT AN ML MODEL
----------------------------------
With 20 hours and no labelled dataset, a neural net would be a black box we
could not explain, validate, or defend to a judge. A transparent weighted rule
engine built from published screening criteria is:
  • explainable  — every signal reports exactly which criteria matched
  • testable     — deterministic, unit-testable
  • honest       — framed as screening signals, never as a diagnosis

That explainability is the product. A woman does not need a prediction, she
needs a sentence she can say to a doctor who has seven minutes for her.

⚠️  NOT A DIAGNOSTIC DEVICE. Screening signals only. See DISCLAIMER below.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

DISCLAIMER = (
    "Ritu is a symptom-awareness tool, not a diagnostic device. These are "
    "screening signals based on patterns you logged — they are not a diagnosis "
    "and do not replace a qualified medical professional. Always consult a "
    "doctor about symptoms that worry you."
)

# ── Symptom vocabulary ───────────────────────────────────────────────────────
# key: (human label, category)
SYMPTOM_TAGS: dict[str, tuple[str, str]] = {
    "cramps":              ("Menstrual cramps", "pain"),
    "pelvic_pain":         ("Pelvic pain outside your period", "pain"),
    "pain_intercourse":    ("Pain during intercourse", "pain"),
    "lower_back_pain":     ("Lower back pain", "pain"),
    "headache":            ("Headache or migraine", "neuro"),
    "nausea":              ("Nausea", "gastro"),
    "bloating":            ("Bloating", "gastro"),
    "fatigue":             ("Unusual fatigue", "systemic"),
    "dizziness":           ("Dizziness or light-headedness", "systemic"),
    "brain_fog":           ("Brain fog", "systemic"),
    "mood_swings":         ("Mood swings", "mood"),
    "low_mood":            ("Low mood or tearfulness", "mood"),
    "anxiety":             ("Anxiety or irritability", "mood"),
    "sleep_issues":        ("Sleep disturbance", "mood"),
    "acne":                ("Acne flare", "androgen"),
    "hair_loss":           ("Hair thinning or loss", "androgen"),
    "hair_growth":         ("Unwanted facial or body hair", "androgen"),
    "weight_gain":         ("Unexplained weight gain", "metabolic"),
    "weight_loss":         ("Unexplained weight loss", "metabolic"),
    "breast_tenderness":   ("Breast tenderness", "cyclic"),
    "heavy_clots":         ("Passing large clots", "bleeding"),
    "soaking_through":     ("Soaking protection in under 2 hours", "bleeding"),
    "missed_period":       ("Missed period", "cycle"),
    # Red flags — always escalated, never scored
    "bleeding_between":    ("Bleeding between periods", "red_flag"),
    "bleeding_after_sex":  ("Bleeding after intercourse", "red_flag"),
    "fever_pelvic_pain":   ("Fever with pelvic pain", "red_flag"),
    "sudden_severe_pain":  ("Sudden severe pelvic pain", "red_flag"),
}

RED_FLAGS = [k for k, (_, cat) in SYMPTOM_TAGS.items() if cat == "red_flag"]
MOOD_TAGS = ["mood_swings", "low_mood", "anxiety", "sleep_issues"]
ANDROGEN_TAGS = ["acne", "hair_loss", "hair_growth"]

FLOW_LABELS = ["none", "spotting", "light", "medium", "heavy", "very_heavy"]
HEAVY_FLOW = {"heavy", "very_heavy"}


# ── Data structures ──────────────────────────────────────────────────────────
@dataclass
class Criterion:
    key: str
    label: str
    matched: bool
    detail: str = ""


@dataclass
class Signal:
    key: str
    name: str
    strength: str                      # "high" | "moderate" | "low"
    matched: list[str] = field(default_factory=list)   # criterion keys that fired
    evidence: list[str] = field(default_factory=list)  # human-readable proof
    meaning: str = ""
    questions: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "key": self.key, "name": self.name, "strength": self.strength,
            "matched": self.matched, "evidence": self.evidence,
            "meaning": self.meaning, "questions": self.questions, "tests": self.tests,
        }


# ── Cycle maths ──────────────────────────────────────────────────────────────
def _parse(d: Any) -> date:
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    return datetime.strptime(str(d)[:10], "%Y-%m-%d").date()


def compute_cycle_stats(logs: list[dict]) -> dict[str, Any]:
    """Derive cycle length, variability, bleeding and pain profile from logs."""
    if not logs:
        return {"logged_days": 0, "has_enough_data": False}

    rows = sorted(logs, key=lambda r: _parse(r["log_date"]))
    days = [_parse(r["log_date"]) for r in rows]

    starts = [_parse(r["log_date"]) for r in rows if r.get("is_period_start")]

    cycle_lengths: list[int] = []
    if len(starts) >= 2:
        cycle_lengths = [(b - a).days for a, b in zip(starts, starts[1:]) if 0 < (b - a).days <= 90]

    # Period length = run of consecutive bleeding days after each start
    bleeding = {_parse(r["log_date"]) for r in rows if r.get("flow") not in (None, "none", "")}
    period_lengths: list[int] = []
    for s in starts:
        n, cur = 0, s
        while cur in bleeding:
            n += 1
            cur += timedelta(days=1)
        if n:
            period_lengths.append(n)

    pains = [r["pain"] for r in rows if r.get("pain")]
    heavy_days = [r for r in rows if r.get("flow") in HEAVY_FLOW]

    tag_counter: Counter = Counter()
    for r in rows:
        for t in _tags(r):
            tag_counter[t] += 1

    avg_cycle = round(sum(cycle_lengths) / len(cycle_lengths), 1) if cycle_lengths else None
    variability = (max(cycle_lengths) - min(cycle_lengths)) if len(cycle_lengths) >= 2 else None

    irregular = bool(
        (variability is not None and variability > 7)
        or (avg_cycle is not None and (avg_cycle < 21 or avg_cycle > 35))
    )

    return {
        "logged_days": len(rows),
        "has_enough_data": len(rows) >= 5,
        "first_log": str(days[0]),
        "last_log": str(days[-1]),
        "period_starts": len(starts),
        "avg_cycle_length": avg_cycle,
        "cycle_variability_days": variability,
        "irregular_cycles": irregular,
        "avg_period_length": round(sum(period_lengths) / len(period_lengths), 1) if period_lengths else None,
        "heavy_bleeding_days": len(heavy_days),
        "avg_pain": round(sum(pains) / len(pains), 1) if pains else None,
        "max_pain": max(pains) if pains else None,
        "severe_pain_days": sum(1 for p in pains if p >= 7),
        "top_symptoms": [
            {"tag": t, "label": SYMPTOM_TAGS.get(t, (t, ""))[0], "days": c}
            for t, c in tag_counter.most_common(6)
        ],
    }


def _tags(row: dict) -> list[str]:
    raw = row.get("symptoms") or "[]"
    if isinstance(raw, list):
        return list(raw)
    import json
    try:
        return list(json.loads(raw))
    except Exception:
        return [t.strip() for t in str(raw).split(",") if t.strip()]


def _cycle_day(row: dict) -> int | None:
    cd = row.get("cycle_day")
    return int(cd) if cd is not None else None


# ── Signal definitions ───────────────────────────────────────────────────────
def detect_signals(logs: list[dict], stats: dict[str, Any]) -> list[Signal]:
    if not logs:
        return []

    rows = sorted(logs, key=lambda r: _parse(r["log_date"]))
    signals: list[Signal] = []

    all_tags: Counter = Counter()
    for r in rows:
        for t in _tags(r):
            all_tags[t] += 1

    period_pains = [r["pain"] for r in rows if r.get("pain") and r.get("flow") not in (None, "none", "")]
    non_period_pains = [r["pain"] for r in rows if r.get("pain") and r.get("flow") in (None, "none", "")]

    # ── 1. Red flags (always surface, never scored) ──────────────────────────
    present_flags = [t for t in RED_FLAGS if all_tags.get(t)]
    if present_flags:
        signals.append(Signal(
            key="red_flag",
            name="Symptoms that warrant prompt medical attention",
            strength="high",
            matched=present_flags,
            evidence=[f"{SYMPTOM_TAGS[t][0]} — logged {all_tags[t]} time(s)" for t in present_flags],
            meaning=(
                "You logged one or more symptoms that clinical guidance says should be "
                "evaluated by a doctor rather than tracked at home."
            ),
            questions=["I logged these specific symptoms — what could they indicate, and how quickly should I be seen?"],
            tests=["Clinical evaluation; your doctor will decide on examination and imaging"],
        ))

    # ── 2. PCOS pattern (Rotterdam-style: irregular cycles + androgen signals) ─
    c_irregular = Criterion("irregular_cycles", "Irregular or absent cycles",
                            bool(stats.get("irregular_cycles")),
                            f"Cycle length {stats.get('avg_cycle_length')} days "
                            f"(variability {stats.get('cycle_variability_days')} days)")
    c_androgen = Criterion("androgen_signs", "Androgen-related signs (acne, hair loss, unwanted hair growth)",
                           any(all_tags.get(t) for t in ANDROGEN_TAGS),
                           ", ".join(SYMPTOM_TAGS[t][0] for t in ANDROGEN_TAGS if all_tags.get(t)))
    c_weight = Criterion("weight_change", "Unexplained weight change",
                         bool(all_tags.get("weight_gain") or all_tags.get("weight_loss")),
                         "Weight change logged")
    c_fatigue = Criterion("fatigue", "Persistent fatigue", bool(all_tags.get("fatigue")),
                          f"Fatigue logged on {all_tags.get('fatigue')} day(s)")

    pcos_crits = [c_irregular, c_androgen, c_weight, c_fatigue]
    pcos_hits = [c for c in pcos_crits if c.matched]
    if len(pcos_hits) >= 2:
        signals.append(Signal(
            key="pcos", name="Possible PCOS pattern", strength="high" if len(pcos_hits) >= 3 else "moderate",
            matched=[c.key for c in pcos_hits],
            evidence=[f"{c.label} — {c.detail}" for c in pcos_hits],
            meaning=(
                "Your logs show a combination of cycle irregularity with androgen-related "
                "or metabolic signs. This is the pattern PCOS screening looks for. It is "
                "common and very manageable — but it is frequently dismissed, and it often "
                "takes several appointments to be taken seriously."
            ),
            questions=[
                "Could my irregular cycles together with these symptoms fit PCOS?",
                "Which specific criteria are you using to rule PCOS in or out?",
                "Should I be screened for insulin resistance and thyroid function too?",
            ],
            tests=["Pelvic ultrasound", "Total and free testosterone", "LH/FSH ratio",
                   "Fasting glucose, HbA1c and lipid profile", "TSH (to rule out thyroid causes)"],
        ))

    # ── 3. Endometriosis pattern ──────────────────────────────────────────────
    severe_period_pain = sum(1 for p in period_pains if p >= 7)
    chronic_pelvic = sum(1 for p in non_period_pains if p >= 4)

    c_severe = Criterion("severe_period_pain", "Severe period pain (7+/10)",
                         severe_period_pain >= 2,
                         f"{severe_period_pain} day(s) at pain 7 or above during your period")
    pelvic_days = all_tags.get("pelvic_pain", 0)
    c_chronic = Criterion("chronic_pelvic_pain", "Pelvic pain outside your period",
                          chronic_pelvic >= 2 or bool(pelvic_days),
                          f"{pelvic_days} day(s) of pelvic pain logged outside your period"
                          + (f" ({chronic_pelvic} at pain 4 or above)" if chronic_pelvic else ""))
    c_deep = Criterion("deep_dyspareunia", "Pain during intercourse",
                       bool(all_tags.get("pain_intercourse")), "Logged")
    c_heavy = Criterion("heavy_bleeding", "Heavy bleeding or clots",
                        bool(stats.get("heavy_bleeding_days")) or bool(all_tags.get("heavy_clots")),
                        f"{stats.get('heavy_bleeding_days')} heavy day(s)")

    endo_crits = [c_severe, c_chronic, c_deep, c_heavy]
    endo_hits = [c for c in endo_crits if c.matched]
    if len(endo_hits) >= 2:
        signals.append(Signal(
            key="endometriosis", name="Possible endometriosis pattern",
            strength="high" if len(endo_hits) >= 3 else "moderate",
            matched=[c.key for c in endo_hits],
            evidence=[f"{c.label} — {c.detail}" for c in endo_hits],
            meaning=(
                "Severe period pain is widely normalised, but pain this disruptive is not "
                "typical. Endometriosis takes on average 7–10 years to diagnose, largely "
                "because symptoms are dismissed as 'normal periods'."
            ),
            questions=[
                "Given this pain pattern, should endometriosis be actively considered?",
                "What imaging would actually show it, and what would a normal scan rule out?",
                "If pain management is the plan, what is the plan for finding the cause?",
            ],
            tests=["Pelvic examination", "Transvaginal ultrasound", "MRI pelvis",
                   "Diagnostic laparoscopy (gold standard)", "CA-125 (supportive only)"],
        ))

    # ── 4. Iron-deficiency / anaemia pattern ─────────────────────────────────
    c_bleed = Criterion("heavy_bleeding", "Heavy bleeding, clots or soaking through",
                        bool(stats.get("heavy_bleeding_days")) or bool(all_tags.get("heavy_clots"))
                        or bool(all_tags.get("soaking_through")),
                        f"{stats.get('heavy_bleeding_days')} heavy day(s) logged")
    c_fat2 = Criterion("fatigue", "Fatigue or dizziness",
                       bool(all_tags.get("fatigue") or all_tags.get("dizziness")),
                       "Fatigue/dizziness logged")
    c_pale = Criterion("neuro", "Headaches, dizziness or brain fog",
                       bool(all_tags.get("headache") or all_tags.get("brain_fog")),
                       "Headache or brain fog logged")

    anemia_crits = [c_bleed, c_fat2, c_pale]
    anemia_hits = [c for c in anemia_crits if c.matched]
    if len(anemia_hits) >= 2:
        signals.append(Signal(
            key="anaemia", name="Possible iron-deficiency pattern",
            strength="moderate" if len(anemia_hits) == 2 else "high",
            matched=[c.key for c in anemia_hits],
            evidence=[f"{c.label} — {c.detail}" for c in anemia_hits],
            meaning=(
                "Heavy bleeding combined with fatigue and dizziness is the classic picture "
                "of depleted iron stores. It is one of the most under-tested consequences "
                "of heavy periods, and it is straightforward to check and treat."
            ),
            questions=[
                "Could my heavy bleeding be causing iron deficiency?",
                "Please check ferritin, not just haemoglobin — ferritin drops first.",
            ],
            tests=["Complete blood count (CBC)", "Serum ferritin", "Iron studies", "TSH"],
        ))

    # ── 5. Thyroid pattern ───────────────────────────────────────────────────
    c_thy_weight = Criterion("weight_change", "Unexplained weight change",
                             bool(all_tags.get("weight_gain") or all_tags.get("weight_loss")), "Logged")
    c_thy_fat = Criterion("fatigue", "Persistent fatigue or brain fog",
                          bool(all_tags.get("fatigue") or all_tags.get("brain_fog")), "Logged")
    c_thy_hair = Criterion("hair_skin", "Hair thinning or skin changes",
                           bool(all_tags.get("hair_loss") or all_tags.get("acne")), "Logged")
    c_thy_cycle = Criterion("cycle_change", "Change in cycle pattern",
                            bool(stats.get("irregular_cycles")) or bool(all_tags.get("missed_period")),
                            "Cycle change logged")

    thy_crits = [c_thy_weight, c_thy_fat, c_thy_hair, c_thy_cycle]
    thy_hits = [c for c in thy_crits if c.matched]
    if len(thy_hits) >= 3:
        signals.append(Signal(
            key="thyroid", name="Possible thyroid pattern",
            strength="moderate" if len(thy_hits) == 3 else "high",
            matched=[c.key for c in thy_hits],
            evidence=[f"{c.label} — {c.detail}" for c in thy_hits],
            meaning=(
                "Thyroid dysfunction shares almost all of its symptoms with 'being stressed "
                "and tired'. Because it also disrupts cycles, it is worth ruling out before "
                "symptoms are attributed to lifestyle."
            ),
            questions=[
                "Could a thyroid problem explain this cluster of symptoms?",
                "Please test TSH — a single blood test can rule this in or out.",
            ],
            tests=["TSH", "Free T4", "T3", "Anti-TPO antibodies"],
        ))

    # ── 6. PMDD pattern (mood symptoms confined to the luteal phase) ─────────
    luteal_mood = follicular_mood = 0
    for r in rows:
        cd = _cycle_day(r)
        if cd is None or not any(t in MOOD_TAGS for t in _tags(r)):
            continue
        if cd > 14:
            luteal_mood += 1
        else:
            follicular_mood += 1

    if luteal_mood >= 3 and luteal_mood > follicular_mood * 2:
        signals.append(Signal(
            key="pmdd", name="Possible cycle-linked mood pattern (PMDD)",
            strength="moderate",
            matched=["cyclic_mood"],
            evidence=[f"Mood symptoms on {luteal_mood} luteal-phase day(s) vs "
                      f"{follicular_mood} follicular-phase day(s)"],
            meaning=(
                "Your mood symptoms cluster in the second half of your cycle and largely "
                "clear afterwards. That timing is the diagnostic clue — it distinguishes a "
                "cycle-linked condition from a mood disorder, and it changes the treatment."
            ),
            questions=[
                "My mood symptoms follow my cycle almost exactly — could this be PMDD rather than anxiety or depression?",
                "Would a prospective symptom diary across two cycles help confirm it?",
            ],
            tests=["Two-cycle prospective symptom diary (this is the diagnostic tool)",
                   "TSH and prolactin (to rule out other causes)"],
        ))

    priority = {"high": 0, "moderate": 1, "low": 2}
    signals.sort(key=lambda s: priority.get(s.strength, 3))
    return signals


# ── Urgency + report ─────────────────────────────────────────────────────────
def compute_urgency(signals: list[Signal]) -> dict[str, str]:
    if any(s.key == "red_flag" for s in signals):
        return {"level": "urgent", "label": "See a doctor promptly",
                "advice": "You logged symptoms that should not be managed at home. "
                          "Please contact a doctor rather than waiting for your next routine visit."}
    if any(s.strength == "high" for s in signals):
        return {"level": "prioritise", "label": "Book an appointment",
                "advice": "Your logs show a strong pattern worth raising with a doctor. "
                          "Take this report with you."}
    if any(s.strength == "moderate" for s in signals):
        return {"level": "discuss", "label": "Raise at your next visit",
                "advice": "There is a pattern here worth mentioning. Keep logging — "
                          "more data makes it clearer."}
    return {"level": "routine", "label": "Keep logging",
            "advice": "No strong pattern detected yet. Consistency is what makes this "
                      "useful — a few cycles of data is where the signal appears."}


def build_report(profile: str, stats: dict[str, Any], signals: list[Signal]) -> str:
    """A one-page summary a woman can hand to a doctor in a 7-minute consultation."""
    urgency = compute_urgency(signals)
    today = date.today().strftime("%d %B %Y")
    L: list[str] = []

    L.append(f"# Ritu — Symptom Summary for {profile or 'Patient'}")
    L.append(f"*Generated {today} · {stats.get('logged_days', 0)} days of logged data "
             f"({stats.get('first_log','—')} to {stats.get('last_log','—')})*")
    L.append("")
    L.append(f"## Why I'm here  \n**{urgency['label']}** — {urgency['advice']}")
    L.append("")

    L.append("## Cycle overview")
    L.append(f"- Average cycle length: **{stats.get('avg_cycle_length') or '—'} days**")
    L.append(f"- Cycle variability: **{stats.get('cycle_variability_days') or '—'} days** "
             f"{'(irregular)' if stats.get('irregular_cycles') else '(regular)'}")
    L.append(f"- Average period length: **{stats.get('avg_period_length') or '—'} days**")
    L.append(f"- Heavy bleeding days: **{stats.get('heavy_bleeding_days', 0)}**")
    L.append(f"- Average pain score: **{stats.get('avg_pain') or '—'} / 10** "
             f"(peak {stats.get('max_pain') or '—'})")
    L.append(f"- Days at severe pain (7+): **{stats.get('severe_pain_days', 0)}**")
    if stats.get("top_symptoms"):
        L.append("- Most logged symptoms: " + ", ".join(
            f"{s['label']} ({s['days']}d)" for s in stats["top_symptoms"][:5]))
    L.append("")

    if signals:
        L.append("## Patterns I'd like discussed")
        for s in signals:
            L.append(f"### {s.name} — {s.strength.upper()} signal")
            for e in s.evidence:
                L.append(f"- {e}")
            L.append(f"\n{s.meaning}\n")
            L.append("**Questions I have:**")
            for q in s.questions:
                L.append(f"1. {q}")
            L.append("\n**Tests I'd like to discuss:** " + ", ".join(s.tests))
            L.append("")
    else:
        L.append("## Patterns I'd like discussed")
        L.append("No strong pattern detected yet. I am logging prospectively so we have "
                 "real data rather than my recollection in the appointment.")
        L.append("")

    L.append("---")
    L.append(f"*{DISCLAIMER}*")
    return "\n".join(L)


def analyze(logs: list[dict], profile: str = "") -> dict[str, Any]:
    stats = compute_cycle_stats(logs)
    signals = detect_signals(logs, stats)
    urgency = compute_urgency(signals)
    return {
        "profile": profile,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "disclaimer": DISCLAIMER,
        "cycle_stats": stats,
        "signals": [s.as_dict() for s in signals],
        "urgency": urgency,
        "report_markdown": build_report(profile, stats, signals),
    }
