# 🎛️ Calibration System (Parameter Tuning)

Calibration sits opposite Sentinel. While Sentinel watches, Calibration calculates: "If I was given looser parameters historically, would we have made more money?"

## 🏗 Architecture Components

1. **`Backtester`**: Simulates the exact Captain logic vectors utilizing historic signals mappings, overlaying different `Confidence Score` or `Fatigue` boundaries against the specific real-world outcomes that occurred.
2. **`OutcomeAnalyzer`**: Detects if the current AI models are fundamentally hallucinating expected Returns compared to 24-48hr realized realities, logging the margin-of-errors specifically.
3. **`ThresholdTuner`**: Heuristically suggests shifting standard bounds (e.g. `min_roas=1.5 -> 1.25`) ONLY if the backtested Lift-To-Penalty ratio exceeds strict 2:1 mapping bounds.
4. **`ParameterRegistry`**: Prevents the models shifting themselves into infinite risky loops by freezing suggestions into a `PENDING_GENESIS_APPROVAL` state, requiring Governance confirmation over AI adjustments passively.

## 🚀 Validating Calibration Locally

```bash
cd backend/services/calibration
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run backtest ratio physics checks
pytest test_calibration.py -v
```
