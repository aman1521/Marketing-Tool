# 🧠 Marketing OS App — Ecosystem Layer

The Ecosystem Layer wraps the Intelligence Core, supporting every human
role that interacts with the system across solo operators, full marketing
teams, agency environments, finance oversight and executive visibility.

## Architecture Summary

```
marketing_os_app/
    collaboration/
        role_matrix.py          — Permission matrix per role (7 roles)
        activity_feed.py        — Real-time event stream
        comment_threads.py      — Per-action decision threads
        task_assigner.py        — Auto-task creation from AI signals
    governance/
        envelope_manager.py     — Budget & strategy guardrails
        escalation_engine.py    — Breach detection + routing
        portfolio_risk_tracker  — Portfolio capital-at-risk
    dashboards/
        translation_layer.py    — Simple / Pro / Executive output modes
        dashboard_views.py      — FastAPI route handlers per view
    usage/
        usage_meter.py          — Per-tenant metering
        ai_impact_engine.py     — ROI delta vs baseline
    admin/
        envelope_editor.py      — Budget/strategy envelope modification
        shadow_mode_toggle.py   — Shadow mode on/off
        override_controls.py    — Escalation approval panel
        cockpit/operator_dashboard.py — Agency Alpha raw cockpit
    ecosystem_models.py         — All SQLAlchemy models
```

## Roles

| Role | Execute | Modify Envelope | Approve Escalation | Visibility |
|---|---|---|---|---|
| Owner | ✅ | ✅ | ✅ | Full |
| CMO | ❌ | ❌ | ✅ | Strategy |
| Media Buyer | ✅ | ❌ | ❌ | Campaigns |
| Creative Strategist | ❌ | ❌ | ❌ | Creative |
| Analyst | ❌ | ❌ | ❌ | Analytics |
| Finance | ❌ | ✅ | ✅ | Budget |
| Viewer | ❌ | ❌ | ❌ | Summary |

## Envelope Flow

```
AI Action Request
    │
    ▼
EnvelopeManager.check_action_within_envelope()
    │
    ├── Within bounds → CaptainExecute.dispatch()
    │
    └── Breach detected → EscalationEngine.trigger_escalation()
            │
            ├── Log full context (envelope + exposure + risk)
            ├── Route to correct roles (Finance, CMO, Owner)
            ├── Emit to ActivityFeed
            └── Block execution until resolved
```

## Dashboard Modes

- **Simple**: Plain English for non-marketers / business owners
- **Pro**: Metrics + creative signals for marketers / analysts
- **Executive**: Capital at risk, ROI delta, autonomy % for CFO/CEO

## Running Tests

```bash
$env:PYTHONPATH="d:\Marketing tool"
pytest backend/marketing_os_app/test_ecosystem.py -v
```
