# Marketing OS App (SaaS Presentation Layer)

This layer physically isolates the volatile external request arrays (APIs, Authentication, Roles, Paywalls) away from the immutable logical arrays running the mathematical Artificial Intelligence. It protects the deterministic bounds from being improperly formatted by standard web traffic.

## 🏗 Architecture Components

1. **`API Gateway` ([router.py])**: The only external ingestion route allowed to hit the OS. Intercepts web payloads mapping them to dict constraints the Core expects cleanly.
2. **`Authentication` ([jwt_manager.py] + [rbac.py])**: Embeds the Tenant's `company_id` and structural `role` bounds strictly into every API invocation.
3. **`Tenant Isolation` ([isolation_layer.py])**: Rejects explicitly any logic loop trying to query another company's structural Data, Profiles, or Outputs.
4. **`Feature Flags` ([feature_manager.py])**: Handles the SaaS paywalls, enabling "Beta" access logic seamlessly (e.g. `Shadow Only` plans cannot query the `Pulse` arrays).
5. **`Dashboards` ([autonomy_status_service.py])**: Normalizes complex architectural vectors into simple presentation structures (Aggregating Sentinel DB logs into a single Output Index integer).
6. **`Admin` ([override_controls.py])**: Standardized endpoints for Owner/Admin SaaS accounts to approve the native `Calibration` suggestions explicitly.
7. **`Billing` ([billing_engine.py] + [usage_meter.py])**: Extracts exact counts on AUM execution scaling seamlessly into dynamic API routes securely feeding systems like Stripe continuously without altering the intelligence logic directly.

## 🔒 Security Posture

The SaaS shell is strictly "Read Heavy." Any external modification requests MUST map definitively back into the `Genesis` layer (Liquid Governance). **The SaaS UI is legally prohibited from modifying execution logic directly**. It only manages human governance rules safely communicating downstream into the Intelligence engines.
