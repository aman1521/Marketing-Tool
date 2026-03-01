# 🧬 Genesis System (Liquid Matter)

Governance and Strategic Identity definition layer for the Marketing Intelligence OS.

Genesis dictates *who* the automated system works for, *what* limits are imposed on it, and *which* metrics matter strategically. It replaces hardcoded logic with a dynamically configurable, strict-audited governance backbone.

## 🏗 Architecture Components

1. **`GenesisProfile`**: Structural metadata defining AOV, Gross Margin, and Budget tiers. Maps precisely to `AtlasBenchmarks`.
2. **`GenesisGoals`**: Targets and modes. E.g., moving a company from `PROFIT_FIRST` to `SCALE_FIRST` logically blocks safe margins, escalating CaptainExecute directives.
3. **`GenesisConstraints`**: The ultimate hard-blocks. E.g., `max_daily_budget`, `min_allowed_roas`, and `auto_execution_enabled`. CaptainRisk strictly obeys these schemas.
4. **`GenesisMapping`**: Translates Profile & Goal schemas into string literals recognizable by down-stream ML clusters (e.g., grading a "mid" budget + "scaling" firm into "Aggressive" `aggression_tiers`).
5. **`VersioningManager`**: Append-Only point-in-time logging. Every API `PUT` increments the `GenesisState.version` by 1 and drops an exact copy of the schema into `GenesisHistory`.

## 🛡 Validations & Safety

- **Strict Dependencies**: The Pydantic Schemas (`schemas.py`) enforce explicit cross-field checks utilizing `@field_validator("target_roas", mode="after")` blocking Profit paths if a user fails to specify the target ROAS.
- **Auditable Safety**: Historical `GenesisHistory` snapshots are Immutable in the database.
- **Complete Test Coverage**: Core state permutations, increments, and validation cascades are verified safely inside `test_genesis.py`.

## 🚀 Running Genesis Locally

```bash
cd backend/services/genesis
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start local ASGI Endpoint
uvicorn backend.services.genesis.api:app --host 0.0.0.0 --port 8004 --reload

# Execute Test Suites
pytest test_genesis.py -v
```
