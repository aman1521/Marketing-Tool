# 👁️ Hawkeye System (Solid Matter)

The intelligence layer governing Creative Persuasion, Friction Modeling, and Emotive Hooking.

While Atlas tracks "What" happened and Captain tracks "Why" financially, Hawkeye tracks "How" the asset actually functioned. It intercepts Ad Media, Copy definitions, and Landing Page environments and systematically converts them into structured numeric signals the rest of the OS can act upon.

## 🏗 Architecture Components

1. **`VisionEngine`**: Extracts pacing, visual complexities, and structural hooks. (e.g. "Does this video change scenes in < 3 seconds?").
2. **`CopyEngine`**: Reduces string prose into NLP classification vectors. Translates headlines directly into `[Urgency]`, `[Trust]`, `[Pain-Point]` mapping.
3. **`FunnelEngine`**: Reverses rendered destination bounds evaluating friction probabilities producing a final `Funnel Gap Score`.
4. **`FatigueEngine`**: Combines `AtlasSignals` scaling trajectories dynamically against the mathematical redundancy of the physical creative.
5. **`EmbeddingEngine`**: Projects exact asset combinations into 16-Dimensional spaces (Qdrant semantic index abstractions) generating an immutable map of precisely what visual array corresponds to successful `CaptainDiagnose` states.

## 🛡 Validations & Safety

- **Strict Dependencies**: The Output JSON payload matches specific Float structures bounded entirely [0.0 - 1.0] to prevent mathematical overflows in Captain Diagnose models.
- **Immutable Knowledge Logs**: Re-running similar variations does not duplicate effort, `creative_id` logic natively hashes duplicates securely within `models.py`.

## 🚀 Validating Hawkeye Locally

```bash
cd backend/services/hawkeye
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Execute Matrix Inference Loops
pytest test_hawkeye.py -v
```
