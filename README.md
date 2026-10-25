# Ritu — Cycle-Aware Symptom Intelligence

**recHERsion 2026 · Problem Statement 1: Women's Healthcare**
ACM-W NITK Surathkal · Engineer NITK 2K26

> **Ritu** turns months of daily symptom logs into patterns a woman can hand to a
> doctor — with the questions to ask and the tests to request.

**The gap we close:** endometriosis takes **7–10 years** to diagnose. Heavy bleeding
goes untested for iron deficiency for years. Not because the data doesn't exist —
because it lives in a woman's memory and gets compressed into "it's probably normal"
during a seven-minute appointment. Ritu makes the data survive the appointment.

---

## ⚡ Run it

```bash
make setup     # install backend + frontend deps
make dev       # API on :8000, app on :5173
```

Open **http://localhost:5173** → the header shows *"backend connected"*.

```bash
make seed      # load a demo case (default: pcos)
make verify    # pre-submission safety checks
```

Then click **"Try a demo case"** in the app to switch between four presentations live.

---

## 🎬 The end-to-end flow *(this is what the demo video shows)*

```
[1] Log a day (20 sec)   →   [2] Engine recomputes patterns   →
[3] Signals appear with evidence   →   [4] One-page doctor report
```

The pattern panel updates **live the moment you save a day**. Log three severe-pain
days on a clean profile and watch an endometriosis signal appear. That live update
is the strongest 30 seconds of the demo — it proves the system computes rather than
replays canned output.

---

## 🧠 Why a rule engine and not a machine-learning model

With 20 hours and no labelled dataset, a neural network would be a black box we
could not explain, validate, or defend. So Ritu uses a **transparent weighted rule
engine built from published screening criteria**:

| | Rule engine (chosen) | ML model (rejected) |
|---|---|---|
| Explainability | Every signal lists the exact criteria that fired | Opaque |
| Data needed | None — works from day one | Labelled dataset we don't have |
| Testability | Deterministic, unit-testable | Probabilistic |
| Honesty | Can say "I don't know" | Always produces a number |

**Explainability is the product.** A woman doesn't need a prediction — she needs a
sentence she can say to a doctor. Every signal in the UI shows its evidence, the
questions to ask, and the tests to discuss.

### Signals the engine detects

| Signal | Fires when |
|---|---|
| **PCOS** | Irregular cycles + androgen signs + weight change + fatigue |
| **Endometriosis** | Severe period pain (7+) + off-period pelvic pain + pain during intercourse + heavy bleeding |
| **Iron deficiency** | Heavy bleeding/clots + fatigue/dizziness + headache/brain fog |
| **Thyroid** | Weight change + fatigue + hair/skin changes + cycle change |
| **PMDD** | Mood symptoms concentrated in the luteal phase across cycles |
| **Red flags** | Bleeding between periods, bleeding after sex, fever with pelvic pain, sudden severe pain |

Red flags bypass scoring entirely and always escalate to *"See a doctor promptly."*

### The negative case matters

The `healthy` scenario produces **zero signals**. The engine deliberately stays
silent when there's nothing to find — that's what makes the signals it does raise
credible. Show this in the demo; judges test for it.

---

## 🏗️ Architecture

```
React + Vite  ──▶  FastAPI  ──▶  SQLite
                      │
                      └──▶ services/insights.py   (the rule engine)
                           services/scenarios.py  (demo datasets)
```

| Layer | Technology | Why |
|---|---|---|
| Frontend | React 18 + Vite 5 | Fast HMR, tiny bundle, plain CSS (no UI-dep risk) |
| Backend | FastAPI + Pydantic | Auto-generated docs, validation for free |
| Database | SQLite (stdlib) | Zero config, runs on any judge's machine |
| Markdown | ~40-line hand-rolled renderer | Avoids a parser dependency for a subset we control |

### API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Health probe |
| `GET` | `/api/symptoms` | Symptom vocabulary — UI renders from this so they can't drift |
| `GET/POST` | `/api/logs` | Daily entries (POST auto-computes cycle day) |
| `DELETE` | `/api/logs/{id}` | Remove an entry |
| `GET` | `/api/insights` | ⭐ **The core flow** — patterns + evidence |
| `GET` | `/api/report` | One-page printable summary |
| `POST` | `/api/scenario` | Load a demo case |

Interactive docs: **http://localhost:8000/docs**

```bash
curl -X POST http://localhost:8000/api/scenario \
  -H 'Content-Type: application/json' \
  -d '{"scenario":"endometriosis","profile":"me"}'
```

---

## 🔒 Privacy by design

Women's health data is some of the most sensitive data that exists. So:

- **No name, email, phone or location is ever collected or stored.** The only
  identifier is a local profile string (`"me"`).
- All data lives in a local SQLite file — no cloud, no analytics, no third-party calls.
- **Zero external API calls** in the product path.
- The report is generated client-side and printed locally; nothing is uploaded.

---

## ♿ Accessibility *(10 marks — already handled)*

- Semantic HTML, one `h1`, landmarks, skip link
- Every input has a real `<label for>`; pain slider has `aria-valuetext`
  (*"7 out of 10, severe"* not just "7")
- Chip groups use `fieldset` + `legend`; toggles expose `aria-pressed`
- `role="status"` + `aria-live="polite"` on the urgency banner and health dot
- Visible 3px focus ring on everything interactive
- Contrast ≥ 4.5:1; meaning never encoded by colour alone (badges have text labels)
- `prefers-reduced-motion` respected
- Responsive to 360px
- **@media print** rules — the report is designed to be handed over on paper

---

## ⚠️ Medical disclaimer

Ritu is a **symptom-awareness tool, not a diagnostic device**. It surfaces screening
signals based on self-reported logs. It does not diagnose and does not replace a
qualified clinician. The disclaimer appears in the API description, the report, the
footer, and the UI. Keep it there — it is the responsible thing to do, and judges
notice.

---

## 👥 Team THEPLAYERS

| Name | College | Role |
|------|---------|------|
| Muskaan Bais | Acropolis Institute of Technology and Research | Ideation & testing — product feedback, manual testing and review |
| Neha Kakade | SKN Sinhgad College of Engineering (SSCoEKP), Korti, Pandharpur, Maharashtra | Ideation & testing — feedback on user flow and testing of the logging screens |
| Tanu Heda | Acropolis Institute of Technology and Research | Full-stack + research — rule engine and cycle maths, FastAPI backend, React frontend, accessibility, demo scenarios, report generator |

> Team of 3. Development was led end-to-end by Tanu Heda; Muskaan and Neha
> supported with feedback and testing.

## ✅ Before you push

```bash
make verify
```

### 🔴 Three rules that disqualify teams

1. **Repo must be Public** — judges can't open a private repo
2. **No commits after 9:00 PM IST, 25 Oct 2026.** Last push by **20:30**
3. **Fill in `THIRD-PARTY-NOTICES.md`** — the rulebook explicitly requires it

---

## 🚀 Deploy

```bash
make build     # frontend → backend/static, single deploy
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

`render.yaml` is preconfigured for exactly this.

---

Built for **recHERsion 2026** · ACM-W NITK Surathkal · Engineer NITK 2K26
