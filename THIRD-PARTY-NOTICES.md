# Third-Party Notices — Ritu

The recHERsion 2026 rulebook requires that all third-party libraries, frameworks,
APIs, datasets, assets and AI tools be acknowledged. Judges check this file.

## Frameworks & Libraries

| Name | Version | Licence | Use |
|------|---------|---------|-----|
| FastAPI | 0.115.6 | MIT | Backend web framework and API layer |
| Uvicorn | 0.34.0 | BSD-3-Clause | ASGI server |
| Pydantic | 2.10.4 | MIT | Request/response validation and models |
| HTTPX | 0.28.1 | BSD-3-Clause | Async HTTP client (available, not used in the product path) |
| python-dotenv | 1.0.1 | BSD-3-Clause | Environment configuration |
| python-multipart | 0.0.20 | Apache-2.0 | Multipart form parsing |
| React | 18.3.1 | MIT | Frontend UI library |
| React DOM | 18.3.1 | MIT | DOM rendering |
| Vite | 5.4.11 | MIT | Frontend build tooling and dev server |
| @vitejs/plugin-react | 4.3.4 | MIT | React support for Vite |
| SQLite | 3 (Python stdlib) | Public domain | Local data storage |

## APIs & Services

**None.** Ritu makes zero external API calls in the product path. This is a
deliberate privacy decision — women's health data never leaves the device.

*(If you add an integration, declare it here.)*

## Datasets

| Dataset | Source | Licence | Notes |
|---------|--------|---------|-------|
| Demo symptom scenarios | **Synthetically generated** by `services/scenarios.py` | Own work | No real patient data. Generated deterministically for demonstration only. |
| Symptom vocabulary | Authored by the team | Own work | 27 symptoms across 11 categories |

## Clinical Knowledge Sources

The screening criteria in `services/insights.py` were authored from **published,
publicly documented screening criteria** for:

- PCOS — Rotterdam-style criteria (cycle irregularity + hyperandrogenism)
- Endometriosis — severe dysmenorrhea, chronic pelvic pain, deep dyspareunia
- Iron-deficiency anaemia — heavy menstrual bleeding with systemic symptoms
- Thyroid dysfunction — constitutional symptom clusters with cycle change
- PMDD — prospectively tracked, cycle-phase-constrained mood symptoms

⚠️ **These rules have not been reviewed or validated by a clinician.** They are
screening heuristics in a student prototype, not medical guidance. Ritu is not a
diagnostic device. State this in your presentation.

## Assets

| Asset | Source | Licence |
|-------|--------|---------|
| Fonts: system font stack (Segoe UI / system-ui) | OS-provided | — |
| All icons and glyphs | Unicode characters (◐ ▪ ▶ ▼ ✓) | — |
| Colour palette | Original | — |

## AI Tools Used

Declare these explicitly — transparency here is required, not optional.

| Tool | How it was used |
|------|-----------------|
| Arena.ai Agent Mode (AI assistant) | Architecture guidance, backend and frontend scaffolding, rule-engine logic, README and slide-copy drafting, debugging |

**Original work:** the rule engine design, the screening criteria, the report
format, the symptom vocabulary and all scenario data are the team's own work
produced during the hackathon.

## Code Reused

| Source | What was reused | Licence |
|--------|-----------------|---------|
| *(e.g. Stack Overflow answer — include link)* | *(function)* | CC BY-SA |

---

**Reminder:** the rulebook requires this file to be accurate. Fill in the AI-tools
row before you submit — leaving it blank is worse than any honest entry.
