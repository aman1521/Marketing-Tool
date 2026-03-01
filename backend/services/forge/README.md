# 🧪 Forge System (Experimentation Layer)

The structured closed-loop variation testing environment inside the Marketing Intelligence OS.

Forge transforms purely observational system behavior into systemic, structurally guaranteed improvement loops. It sits dynamically between `CaptainStrategy` and `CaptainExecute` to test predictions against strict mathematical reality safely.

## 🏗 Architecture Components

1. **`VariationGenerator`**: Maps categorical Dark Matter tags (`CREATIVE_FATIGUE`, `CONVERSION_PROBLEM`) into structured JSON A/B tests. Example: Automatically injecting a structural audience pivot for scaling blockages.
2. **`AllocationManager`**: Routes financial execution weights utilizing Genesis Governance caps (`Aggressive` tier unlocks up to 15% sandbox budget, `Low` tier unlocks 5%).
3. **`SignificanceEngine`**: Bayesian & Z-Test validation matrix rejecting naive CTR deltas. Forge requires statistical rigor (>95% confidence bounds) before it labels an event a winner.
4. **`PromotionEngine` / `SandboxController`**: The action router mapping outcomes to CaptainExecute and protecting core campaign environments via naming exclusions.
5. **`ExperimentLogger` & `Registry`**: Appends exact Hypothesis vs Event Output records mechanically into `AtlasMemory` powering massive ML feedback loop architectures natively.

## 🛡 Validations & Safety

- **Strict Dependencies**: Absolute reliance upon `GenesisConstraints` matrixes. Forge natively cannot mutate main DB parameters without creating an isolated `[FORGE-SANDBOX]` namespace logically.
- **Fail-safes**: Automatically blocks `max_daily_budget` leaks by mathematically calculating `(core + sandbox_alloc) > limit`.
- **Closed Loop Trackable**: Tests directly mapping significance outputs mechanically directly to `<Model_Registry>` outputs natively via asynchronous logging endpoints.

## 🚀 Validating Forge Locally

```bash
cd backend/services/forge
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Execute Sandbox Validation Core Mechanics
pytest test_forge.py -v
```
