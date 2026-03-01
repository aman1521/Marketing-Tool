# Internal Pilot Playbook: Autonomous Marketing Intelligence OS

## 1. Pilot Objectives

The primary objective of the Internal Pilot is to validate the safety, stability, and intelligence of the Autonomous Marketing OS before introducing real client capital to its full capabilities.

### Key Objectives

* **Stability Validation:** Ensure zero unhandled exceptions within continuous execution loops across the 5 Matter Layers (Atlas, Genesis, Captain, Hawkeye, Pulse, Sentinel, Calibration).
* **Capital Preservation:** Ensure that the system respects hard-coded Genesis governance constraints and aggressively rolls back risky actions before they realize loss.
* **Drift Detection Reliability:** Prove that Sentinel accurately detects deviations between simulated 24h ROI and realized historical ROI.
* **Execution Precision:** Validate the mathematical accuracy of Forge experiments and the semantic stability of Hawkeye classifications.
* **ROI Delta vs Manual Optimization:** Quantify the actual decision lift or penalty vs. human-operated baseline accounts.

## 2. Risk Containment Protocol

During the pilot, the system will operate under strictly constrained boundaries.

* **Initial `max_budget_change_percent`:** Locked to **5–10%** absolute limit per 24 hours.
* **Sandbox-Only Scaling (Day 0-14):** Autonomy is restricted to Forge sandbox experiment allocation only. Core campaign modification is prohibited.
* **Auto-Rollback Thresholds:** Sentinel is configured to trigger immediate `PlatformRouter` inverses if a executed change exceeds a 15% negative CPA/ROAS drift within 12 hours.
* **Manual Override Procedure:** Any system drift automatically flips `shadow_mode_enabled` to TRUE in Genesis, instantly preventing the next Execution loop.
* **Emergency Shutdown:** A single hard-kill endpoint in Genesis immediately reverts the active Configuration state to strictly `auto_execution_enabled: false`.

## 3. Autonomy Exposure Phases

Moving the Pilot horizontally across scaling risks systematically.

* **Phase 1: Shadow Mode (no execution)**
  * **Timeline:** Days 1–7
  * **Action:** `shadow_mode_enabled = True`. CaptainStrategy builds complete payloads. CaptainExecute simulates and logs them.
  * **Goal:** Compare what the AI *would* have done vs. human team decisions. Validate Sentinel Drift tracking passively.
* **Phase 2: Partial Autonomy (sandbox only)**
  * **Timeline:** Days 8–21
  * **Action:** Auto-Execution is enabled *only* for Forge Sandbox budget allocations and Creative Fatigue tagging.
  * **Goal:** Prove Hawkeye determinism and Significance Engine mathematics using real but isolated fraction budgets.
* **Phase 3: Controlled Scaling Autonomy**
  * **Timeline:** Days 22–45
  * **Action:** CaptainExecute is permitted to adjust budgets up to 5% daily on pre-defined low-volatility 'Winner' campaigns.
  * **Goal:** Verify rolling 7-day ROI positive lifts securely.
* **Phase 4: Full Bounded Autonomy**
  * **Timeline:** Day 45+
  * **Action:** Full mapping enabled. All components (Pulse Gravity modifications, Hawkeye classifications, Captain executes) are active within Genesis global constraints.

## 4. Metrics to Track Daily

The Quantitative parameters to review rigorously.

* **Autonomy Precision Score:** Tracks success vs. failure of API execution handling.
* **Simulation vs Actual Delta:** Measures Captain's original logic projection vs actual resulting platform ROAS/CPA.
* **Rollback Frequency:** How often did ExecutionMonitor trigger a safety reversal payload?
* **Drift Incidents:** Instances where variance exceeded safe threshold limits natively.
* **Classification Stability:** Did Hawkeye flip an asset continuously between states erratically?
* **Budget Exposure Ratio:** Live Sandbox Allocation vs Total Global Spent.
* **Creative Fatigue Accuracy:** Validating `FATIGUE_FALSE_POSITIVE` anomaly labels.
* **Macro Misclassification Rate:** Validating Pulse market phases (e.g., flagging 'Volatile Decline' correctly).

## 5. Exit Criteria

To graduate from the Internal Pilot to the Beta Client Rollout Framework, the system must definitively prove:

* **Minimum 30-day continuous loop stability** without OS crashing or halting.
* **Rollback rate < 5%** across all executed payloads.
* **ROI lift positive vs baseline** tracking against standard manual operations.
* **Zero catastrophic anomalies** involving runaway budgets or destructive logic loops.
