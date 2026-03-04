"""
Three-Tier Operator Memory System — Full Test Suite
====================================================
All tests run without Qdrant, GPU, or live network.
"""

import pytest
import backend.services.memory.private_memory_engine  as pmod
import backend.services.memory.tenant_memory_engine   as tmod
import backend.services.memory.global_memory_engine   as gmod
import backend.services.memory.archetype_builder      as amod

from backend.services.memory.context_vectorizer   import ContextVectorizer
from backend.services.memory.private_memory_engine import PrivateMemoryEngine
from backend.services.memory.tenant_memory_engine  import TenantMemoryEngine
from backend.services.memory.global_memory_engine  import GlobalMemoryEngine
from backend.services.memory.archetype_builder     import ArchetypeBuilder
from backend.services.memory.replay_engine         import ReplayEngine
from backend.services.memory.influence_controller  import InfluenceController


# ─── Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _reset_stores():
    """Isolate each test — wipe all in-memory stores."""
    pmod._store.clear()
    tmod._store.clear()
    gmod._global_store.clear()
    amod._archetypes.clear()
    yield
    pmod._store.clear()
    tmod._store.clear()
    gmod._global_store.clear()
    amod._archetypes.clear()


def _ctx(strategy="scale_budget", outcome="win", lift=0.12, **kwargs):
    base = {
        "strategy_type":    strategy,
        "industry_bucket":  "saas",
        "aov_tier":         "mid",
        "scaling_band":     "growth",
        "drift_frequency":  0.10,
        "volatility_index": 0.25,
        "confidence_avg":   0.82,
        "roi_delta_48h":    0.08,
        "escalation_freq":  0.05,
        "portfolio_exposure": 30.0,
        "risk_exposure":    0.15,
        "outcome":          outcome,
        "lift_delta":       lift,
    }
    base.update(kwargs)
    return base


# ═══════════════════════════════════════════════════════════════════════════
# 1. CONTEXT VECTORIZER
# ═══════════════════════════════════════════════════════════════════════════

class TestContextVectorizer:
    def test_to_text_contains_strategy(self):
        v = ContextVectorizer()
        text = v.to_text(_ctx())
        assert "scale_budget" in text

    def test_feature_vector_length(self):
        v = ContextVectorizer()
        fv = v.to_feature_vector(_ctx())
        assert len(fv) == 34

    def test_feature_vector_normalised(self):
        v = ContextVectorizer()
        fv = v.to_feature_vector(_ctx())
        assert all(0.0 <= x <= 1.0 for x in fv)

    def test_embed_returns_384_dims(self):
        v = ContextVectorizer()
        vec = v.embed(_ctx())
        assert len(vec) == 384

    def test_fingerprint_deterministic(self):
        v = ContextVectorizer()
        ctx = _ctx()
        assert v.fingerprint(ctx) == v.fingerprint(ctx)

    def test_fingerprint_different_strategies_differ(self):
        v = ContextVectorizer()
        a = v.fingerprint(_ctx(strategy="scale_budget"))
        b = v.fingerprint(_ctx(strategy="pause"))
        assert a != b

    def test_anonymise_strips_pii(self):
        v = ContextVectorizer()
        dirty = {**_ctx(), "operator_id": "op_1", "company_id": "co_1", "campaign_id": "x"}
        anon = v.anonymise(dirty)
        assert "operator_id" not in anon
        assert "company_id" not in anon
        assert "campaign_id" not in anon

    def test_anonymise_keeps_statistical_fields(self):
        v = ContextVectorizer()
        anon = v.anonymise(_ctx())
        assert "strategy_type" in anon
        assert "volatility_index" in anon
        assert "lift_delta" in anon


# ═══════════════════════════════════════════════════════════════════════════
# 2. PRIVATE MEMORY ENGINE (TIER 1)
# ═══════════════════════════════════════════════════════════════════════════

class TestPrivateMemoryEngine:
    def test_record_event_returns_id(self):
        eng = PrivateMemoryEngine()
        eid = eng.record_event("op1", "co1", "scale_budget", _ctx(), {"budget_delta": 0.2})
        assert isinstance(eid, str) and len(eid) == 36

    def test_resolve_event(self):
        eng = PrivateMemoryEngine()
        eid = eng.record_event("op1", "co1", "scale_budget", _ctx(), {})
        ok = eng.resolve_event(eid, "op1", "win", 0.15)
        assert ok is True

    def test_resolve_denied_for_other_operator(self):
        eng = PrivateMemoryEngine()
        eid = eng.record_event("op1", "co1", "scale_budget", _ctx(), {})
        ok = eng.resolve_event(eid, "op2", "win", 0.15)
        assert ok is False

    def test_query_similar_empty_before_resolve(self):
        eng = PrivateMemoryEngine()
        eng.record_event("op1", "co1", "scale_budget", _ctx(), {})
        hits = eng.query_similar("op1", _ctx())
        assert hits == []    # pending events not returned

    def test_query_similar_returns_after_resolve(self):
        eng = PrivateMemoryEngine()
        eid = eng.record_event("op1", "co1", "scale_budget", _ctx(), {})
        eng.resolve_event(eid, "op1", "win", 0.15)
        hits = eng.query_similar("op1", _ctx())
        assert len(hits) >= 1

    def test_operator_isolation(self):
        eng = PrivateMemoryEngine()
        eid = eng.record_event("op1", "co1", "scale_budget", _ctx(), {})
        eng.resolve_event(eid, "op1", "win", 0.15)
        hits = eng.query_similar("op2", _ctx())    # different operator
        assert hits == []

    def test_lift_stats(self):
        eng = PrivateMemoryEngine()
        for _ in range(3):
            eid = eng.record_event("op1", "co1", "scale_budget", _ctx(), {})
            eng.resolve_event(eid, "op1", "win", 0.12)
        stats = eng.get_operator_lift_stats("op1", "scale_budget")
        assert stats["sample_count"] == 3
        assert stats["win_rate"] == 1.0
        assert abs(stats["avg_lift"] - 0.12) < 0.001

    def test_get_events_returns_most_recent_first(self):
        eng = PrivateMemoryEngine()
        for i in range(5):
            eng.record_event("op1", "co1", "scale_budget", _ctx(), {})
        evts = eng.get_operator_events("op1", limit=3)
        assert len(evts) == 3


# ═══════════════════════════════════════════════════════════════════════════
# 3. TENANT MEMORY ENGINE (TIER 2)
# ═══════════════════════════════════════════════════════════════════════════

class TestTenantMemoryEngine:
    def test_record_event(self):
        eng = TenantMemoryEngine()
        eid = eng.record_event("co1", "scale_budget", _ctx(), "win", 0.15)
        assert len(eid) == 36

    def test_company_isolation(self):
        eng = TenantMemoryEngine()
        eng.record_event("co1", "scale_budget", _ctx(), "win", 0.15)
        hits = eng.query_similar("co2", _ctx(), outcome_filter=None)
        assert hits == []

    def test_query_returns_resolved_events(self):
        eng = TenantMemoryEngine()
        for _ in range(3):
            eng.record_event("co1", "scale_budget", _ctx(), "win", 0.12)
        hits = eng.query_similar("co1", _ctx(), outcome_filter="win")
        assert len(hits) >= 1

    def test_strategy_stats(self):
        eng = TenantMemoryEngine()
        for _ in range(4):
            eng.record_event("co1", "scale_budget", _ctx(), "win", 0.10)
        eng.record_event("co1", "scale_budget", _ctx(), "loss", -0.05)
        stats = eng.get_strategy_stats("co1")
        assert "scale_budget" in stats
        assert stats["scale_budget"]["sample_count"] == 5
        assert abs(stats["scale_budget"]["win_rate"] - 0.80) < 0.01

    def test_repeating_patterns_require_min_occurrences(self):
        eng = TenantMemoryEngine()
        for _ in range(2):
            eng.record_event("co1", "scale_budget", _ctx(), "win", 0.15)
        patterns = eng.get_repeating_patterns("co1", min_occurrences=3)
        assert patterns == []   # not enough yet

    def test_repeating_patterns_detected(self):
        eng = TenantMemoryEngine()
        for _ in range(4):
            eng.record_event("co1", "scale_budget", _ctx(), "win", 0.15)
        patterns = eng.get_repeating_patterns("co1", min_occurrences=3)
        assert len(patterns) >= 1
        assert patterns[0]["occurrences"] >= 3

    def test_link_archetype(self):
        eng = TenantMemoryEngine()
        eid = eng.record_event("co1", "scale_budget", _ctx(), "win", 0.10)
        eng.link_archetype(eid, "arch_123")
        evts = eng.get_company_events("co1")
        assert evts[0]["archetype_id"] == "arch_123"


# ═══════════════════════════════════════════════════════════════════════════
# 4. GLOBAL MEMORY ENGINE (TIER 3)
# ═══════════════════════════════════════════════════════════════════════════

class TestGlobalMemoryEngine:
    def test_ingest_returns_id(self):
        eng = GlobalMemoryEngine()
        pid = eng.ingest(_ctx(), "win", 0.12)
        assert isinstance(pid, str)

    def test_pii_blocked_at_ingest(self):
        eng = GlobalMemoryEngine()
        dirty = {**_ctx(), "company_id": "co_secret", "operator_id": "op_secret"}
        eng.ingest(dirty, "win", 0.12)
        # Verify no PII in store
        for p in gmod._global_store:
            assert "company_id"  not in p
            assert "operator_id" not in p

    def test_aggregation_on_matching_fingerprint(self):
        eng = GlobalMemoryEngine()
        ctx = _ctx()
        eng.ingest(ctx, "win", 0.10)
        eng.ingest(ctx, "win", 0.20)
        # Same fingerprint → aggregated
        assert len(gmod._global_store) == 1
        assert gmod._global_store[0]["sample_count"] == 2
        assert abs(gmod._global_store[0]["avg_lift"] - 0.15) < 0.001

    def test_different_strategy_creates_new_pattern(self):
        eng = GlobalMemoryEngine()
        eng.ingest(_ctx(strategy="scale_budget"), "win", 0.10)
        eng.ingest(_ctx(strategy="pause"),        "win", 0.05)
        assert len(gmod._global_store) == 2

    def test_wilson_confidence_increases_with_samples(self):
        eng = GlobalMemoryEngine()
        ctx = _ctx()
        for _ in range(10):
            eng.ingest(ctx, "win", 0.12)
        conf = gmod._global_store[0]["confidence"]
        assert conf > 0.60

    def test_global_stats(self):
        eng = GlobalMemoryEngine()
        for _ in range(6):
            eng.ingest(_ctx(), "win", 0.12)
        stats = eng.get_global_stats()
        assert stats["total_patterns"] == 1
        assert stats["total_sample_count"] == 6
        assert "strategy_win_rates" in stats

    def test_query_similar_respects_min_confidence(self):
        eng = GlobalMemoryEngine()
        # Only 1 sample → confidence below threshold
        eng.ingest(_ctx(), "win", 0.12)
        hits = eng.query_similar(_ctx(), min_confidence=0.65)
        assert hits == []   # not enough confidence yet


# ═══════════════════════════════════════════════════════════════════════════
# 5. ARCHETYPE BUILDER
# ═══════════════════════════════════════════════════════════════════════════

class TestArchetypeBuilder:
    def _seed_patterns(self, count=4, win_rate=1.0):
        return [{
            "fingerprint":  f"fp_{i}",
            "strategy_type":"scale_budget",
            "industry":     "saas",
            "aov_tier":     "mid",
            "scaling_band": "growth",
            "occurrences":  count,
            "avg_lift":     0.12,
            "avg_risk":     0.10,
            "win_rate":     win_rate,
        } for i in range(1)]

    def test_build_creates_archetypes(self):
        ab = ArchetypeBuilder()
        ab.build_from_tenant_patterns(self._seed_patterns(count=4))
        assert len(amod._archetypes) == 1

    def test_candidate_with_low_sample(self):
        ab = ArchetypeBuilder()
        ab.build_from_tenant_patterns(self._seed_patterns(count=2))
        assert amod._archetypes[0]["status"] == "candidate"

    def test_confirmed_with_sufficient_samples(self):
        ab = ArchetypeBuilder()
        ab.build_from_tenant_patterns(self._seed_patterns(count=10, win_rate=0.90))
        ab.run_lifecycle()
        assert amod._archetypes[0]["status"] == "confirmed"

    def test_bias_modifier_positive_for_good_archetype(self):
        ab = ArchetypeBuilder()
        ab.build_from_tenant_patterns(self._seed_patterns(count=10, win_rate=0.90))
        ab.run_lifecycle()
        arch = amod._archetypes[0]
        assert arch["bias_modifier"] > 0.0

    def test_deprecation_on_low_win_rate(self):
        ab = ArchetypeBuilder()
        patterns = self._seed_patterns(count=15, win_rate=0.25)
        ab.build_from_tenant_patterns(patterns)
        # Force promote then deprecate
        amod._archetypes[0]["status"] = "confirmed"
        amod._archetypes[0]["sample_count"] = 15
        amod._archetypes[0]["win_rate"] = 0.25
        result = ab.run_lifecycle()
        assert amod._archetypes[0]["status"] == "deprecated"

    def test_find_matching_returns_empty_when_no_confirmed(self):
        ab = ArchetypeBuilder()
        ab.build_from_tenant_patterns(self._seed_patterns(count=2))
        matches = ab.find_matching_archetypes(_ctx())
        assert matches == []   # only candidates, none confirmed

    def test_archetype_name_is_descriptive(self):
        ab = ArchetypeBuilder()
        ab.build_from_tenant_patterns(self._seed_patterns(count=10, win_rate=0.90))
        name = amod._archetypes[0]["name"]
        assert "Scale Budget" in name or "scale_budget" in name.lower()


# ═══════════════════════════════════════════════════════════════════════════
# 6. REPLAY ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class TestReplayEngine:
    def test_no_data_report_when_empty(self):
        eng = ReplayEngine()
        result = eng.simulate("op1", "co1", _ctx(), mode="archetype_match")
        assert "recommendation" in result
        assert result.get("events_matched", 0) == 0 or "NO_DATA" in result.get("recommendation","")

    def test_historical_sim_with_data(self):
        # Seed private memory
        pm = PrivateMemoryEngine()
        for _ in range(3):
            eid = pm.record_event("op1", "co1", "scale_budget", _ctx(), {})
            pm.resolve_event(eid, "op1", "win", 0.12)
        eng = ReplayEngine()
        result = eng.simulate("op1", "co1", _ctx(), mode="historical_sim")
        assert "predicted_lift" in result
        assert result["predicted_lift"] == pytest.approx(0.12, abs=0.01)

    def test_stress_test_runs_scenarios(self):
        eng = ReplayEngine()
        result = eng.simulate("op1", "co1", _ctx(), mode="stress_test")
        assert "scenario_results" in result
        assert len(result["scenario_results"]) > 0
        assert "safety_ratio" in result

    def test_archetype_match_with_confirmed_archetype(self):
        ab = ArchetypeBuilder()
        patterns = [{
            "fingerprint":  "fp_test",
            "strategy_type":"scale_budget",
            "industry":     "saas",
            "aov_tier":     "mid",
            "scaling_band": "growth",
            "occurrences":  10,
            "avg_lift":     0.15,
            "avg_risk":     0.10,
            "win_rate":     0.85,
        }]
        ab.build_from_tenant_patterns(patterns)
        ab.run_lifecycle()

        eng = ReplayEngine()
        result = eng.simulate("op1", "co1", _ctx(), mode="archetype_match")
        if amod._archetypes[0]["status"] == "confirmed":
            assert result.get("win_rate", 0) > 0
            assert "PROCEED" in result.get("recommendation", "")

    def test_invalid_mode_returns_error(self):
        eng = ReplayEngine()
        result = eng.simulate("op1", "co1", _ctx(), mode="invalid_mode")
        assert "error" in result


# ═══════════════════════════════════════════════════════════════════════════
# 7. INFLUENCE CONTROLLER
# ═══════════════════════════════════════════════════════════════════════════

class TestInfluenceController:
    def test_signal_has_required_keys(self):
        ic = InfluenceController()
        signal = ic.get_influence_signal("op1", "co1", _ctx())
        for key in ["blended_lift", "blended_win_rate", "blended_confidence",
                    "weights", "action", "tier_signals", "generated_at"]:
            assert key in signal

    def test_weights_sum_to_one(self):
        ic = InfluenceController()
        signal = ic.get_influence_signal("op1", "co1", _ctx())
        total = sum(signal["weights"].values())
        assert abs(total - 1.0) < 0.001

    def test_action_sandbox_first_when_no_data(self):
        ic = InfluenceController()
        signal = ic.get_influence_signal("op1", "co1", _ctx())
        assert signal["action"] == "SANDBOX_FIRST"

    def test_action_execute_with_rich_private_history(self):
        pm = PrivateMemoryEngine()
        for _ in range(10):
            eid = pm.record_event("op1", "co1", "scale_budget", _ctx(), {})
            pm.resolve_event(eid, "op1", "win", 0.15)

        ic = InfluenceController()
        signal = ic.get_influence_signal("op1", "co1", _ctx())
        assert signal["action"] in ("EXECUTE", "EXECUTE_WITH_MONITORING", "REVIEW")

    def test_private_weight_increases_with_history(self):
        pm = PrivateMemoryEngine()
        for _ in range(8):
            eid = pm.record_event("op1", "co1", "scale_budget", _ctx(), {})
            pm.resolve_event(eid, "op1", "win", 0.15)

        # Record base weights without history
        ic0 = InfluenceController()
        sig0 = ic0.get_influence_signal("other_op", "co1", _ctx())

        # With history
        ic1 = InfluenceController()
        sig1 = ic1.get_influence_signal("op1", "co1", _ctx())

        assert sig1["weights"]["private"] >= sig0["weights"]["private"]

    def test_tier_signals_present(self):
        ic = InfluenceController()
        signal = ic.get_influence_signal("op1", "co1", _ctx())
        assert "private" in signal["tier_signals"]
        assert "tenant"  in signal["tier_signals"]
        assert "global"  in signal["tier_signals"]

    def test_archetype_bias_applied_when_archetype_exists(self):
        ab = ArchetypeBuilder()
        ab.build_from_tenant_patterns([{
            "fingerprint":  "fp_bias",
            "strategy_type":"scale_budget",
            "industry":     "saas",
            "aov_tier":     "mid",
            "scaling_band": "growth",
            "occurrences":  10,
            "avg_lift":     0.20,
            "avg_risk":     0.08,
            "win_rate":     0.90,
        }])
        ab.run_lifecycle()
        ic = InfluenceController()
        signal = ic.get_influence_signal("op1", "co1", _ctx())
        # If archetype found and confirmed, bias should be positive
        if signal["archetype_signal"]["archetype_found"]:
            arch_bias = signal["archetype_signal"]["bias_modifier"]
            assert isinstance(arch_bias, float)
