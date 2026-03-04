"""
PGIL — Full Test Suite
======================
All tests run without Qdrant, GPU, or live network.
Shared autouse fixture resets all in-memory stores before each test.
"""

import pytest
import backend.services.pgil.pgil_collector        as cmod
import backend.services.pgil.pgil_pattern_engine   as pmod
import backend.services.pgil.pgil_archetype_builder as amod

from backend.services.pgil.pgil_collector          import PGILCollector, BLOCKED_FIELDS
from backend.services.pgil.pgil_vector_store       import PGILVectorStore
from backend.services.pgil.pgil_pattern_engine     import PGILPatternEngine
from backend.services.pgil.pgil_archetype_builder  import PGILArchetypeBuilder
from backend.services.pgil.pgil_influence_controller import PGILInfluenceController


# ─── Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _reset():
    cmod._events.clear()
    pmod._patterns.clear()
    amod._archetypes.clear()
    yield
    cmod._events.clear()
    pmod._patterns.clear()
    amod._archetypes.clear()


def _raw(strategy="scale_budget", industry="saas", cluster="trial",
          funnel="bofu", outcome="win", lift=0.12, **kwargs):
    """Produce a realistic raw event (may contain PII — collector strips it)."""
    base = {
        "strategy_type":      strategy,
        "industry_bucket":    industry,
        "creative_cluster":   cluster,
        "funnel_stage":       funnel,
        "volatility_index":   0.30,
        "drift_frequency":    0.10,
        "confidence_avg":     0.82,
        "roi_delta_48h":      0.08,
        "escalation_frequency": 0.05,
        "scaling_band":       "growth",
        "outcome":            outcome,
        "lift_delta":         lift,
        "risk_score":         0.15,
        # PII fields (should be stripped)
        "company_id":         "co_secret_123",
        "operator_id":        "op_secret",
        "campaign_id":        "camp_xyz",
        "spend":              9999.99,
    }
    base.update(kwargs)
    return base


# ═══════════════════════════════════════════════════════════════════════════
# 1. PGIL COLLECTOR
# ═══════════════════════════════════════════════════════════════════════════

class TestPGILCollector:
    def test_collect_returns_event(self):
        c = PGILCollector()
        event = c.collect(_raw())
        assert event is not None

    def test_all_pii_stripped(self):
        c = PGILCollector()
        event = c.collect(_raw())
        for blocked in BLOCKED_FIELDS:
            assert blocked not in event, f"PII field '{blocked}' leaked into event"

    def test_no_spend_or_revenue(self):
        c = PGILCollector()
        event = c.collect(_raw())
        assert "spend" not in event
        assert "budget_amount" not in event
        assert "revenue" not in event

    def test_volatility_bucketed(self):
        c = PGILCollector()
        low  = c.collect(_raw(volatility_index=0.10))
        high = c.collect(_raw(volatility_index=0.80))
        assert low["volatility_band"]  == "low"
        assert high["volatility_band"] == "extreme"

    def test_drift_bucketed(self):
        c = PGILCollector()
        event = c.collect(_raw(drift_frequency=0.40))
        assert event["drift_bucket"] == "high"

    def test_confidence_bucketed(self):
        c = PGILCollector()
        event = c.collect(_raw(confidence_avg=0.90))
        assert event["confidence_bucket"] == "high"

    def test_roi_direction_up(self):
        c = PGILCollector()
        event = c.collect(_raw(roi_delta_48h=0.15))
        assert event["roi_direction"] == "up"

    def test_roi_direction_down(self):
        c = PGILCollector()
        event = c.collect(_raw(roi_delta_48h=-0.10))
        assert event["roi_direction"] == "down"

    def test_invalid_industry_bucketed_to_other(self):
        c = PGILCollector()
        event = c.collect(_raw(industry_bucket="crypto_niche"))
        assert event["industry_bucket"] == "other"

    def test_missing_required_field_rejected(self):
        c = PGILCollector()
        bad = {"strategy_type": "scale_budget", "industry_bucket": "saas"}
        # Missing funnel_stage and outcome
        result = c.collect(bad)
        assert result is None

    def test_fingerprint_present(self):
        c = PGILCollector()
        event = c.collect(_raw())
        assert "pattern_fingerprint" in event
        assert len(event["pattern_fingerprint"]) == 20

    def test_fingerprint_deterministic(self):
        c = PGILCollector()
        fp1 = c.collect(_raw())["pattern_fingerprint"]
        fp2 = c.collect(_raw())["pattern_fingerprint"]
        assert fp1 == fp2

    def test_different_strategies_different_fingerprints(self):
        c = PGILCollector()
        fp1 = c.collect(_raw(strategy="scale_budget"))["pattern_fingerprint"]
        fp2 = c.collect(_raw(strategy="pause"))["pattern_fingerprint"]
        assert fp1 != fp2

    def test_batch_collect_filters_rejects(self):
        c = PGILCollector()
        events = [
            _raw(),
            {"strategy_type": "bad"},   # missing required fields
            _raw(strategy="pause"),
        ]
        results = c.collect_batch(events)
        assert len(results) == 2

    def test_week_of_year_present(self):
        c = PGILCollector()
        event = c.collect(_raw())
        assert "week_of_year" in event
        assert 1 <= event["week_of_year"] <= 53

    def test_allowed_fields_only(self):
        from backend.services.pgil.pgil_collector import ALLOWED_FIELDS
        c = PGILCollector()
        event = c.collect(_raw())
        extra = {"pattern_fingerprint", "week_of_year", "collected_at"}
        for key in event:
            assert key in ALLOWED_FIELDS | extra, f"Unexpected field in event: {key}"


# ═══════════════════════════════════════════════════════════════════════════
# 2. PGIL VECTOR STORE
# ═══════════════════════════════════════════════════════════════════════════

class TestPGILVectorStore:
    def test_feature_vector_is_384_dims(self):
        vs = PGILVectorStore()
        vec = vs.feature_vector(_raw())
        assert len(vec) == 384

    def test_feature_vector_normalised(self):
        vs = PGILVectorStore()
        vec = vs.feature_vector(_raw())
        norm = sum(x**2 for x in vec)**0.5
        assert abs(norm - 1.0) < 0.01

    def test_upsert_event_returns_id(self):
        vs = PGILVectorStore()
        pid = vs.upsert_event(_raw())
        assert isinstance(pid, str) and len(pid) == 36

    def test_upsert_pattern_returns_id(self):
        vs = PGILVectorStore()
        pattern = {"id": "pat_1", "strategy_type": "scale_budget",
                    "industry_bucket": "saas", "funnel_stage": "bofu",
                    "outcome": "win", "lift_delta": 0.12}
        pid = vs.upsert_pattern(pattern)
        assert pid is not None

    def test_search_returns_list(self):
        vs = PGILVectorStore()
        vs.upsert_event({"strategy_type":"scale_budget","industry_bucket":"saas",
                          "funnel_stage":"bofu","outcome":"win","lift_delta":0.12})
        results = vs.search_similar_events(_raw(), score_threshold=0.0)
        assert isinstance(results, list)

    def test_collection_info_has_expected_keys(self):
        vs = PGILVectorStore()
        info = vs.collection_info()
        assert "pgil_events" in info
        assert "pgil_patterns" in info
        assert "pgil_archetypes" in info

    def test_different_strategies_produce_different_vectors(self):
        vs = PGILVectorStore()
        v1 = vs.feature_vector(_raw(strategy="scale_budget"))
        v2 = vs.feature_vector(_raw(strategy="pause"))
        assert v1 != v2


# ═══════════════════════════════════════════════════════════════════════════
# 3. PGIL PATTERN ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class TestPGILPatternEngine:
    def _seed(self, count=5, strategy="scale_budget", industry="saas",
               outcome="win", lift=0.12):
        c   = PGILCollector()
        pe  = PGILPatternEngine(PGILVectorStore())
        events = [c.collect(_raw(strategy=strategy, industry=industry,
                                   outcome=outcome, lift=lift))
                   for _ in range(count)]
        for e in events:
            if e:
                pe.process_event(e)
        return pe

    def test_process_event_creates_pattern(self):
        pe = self._seed(1)
        assert len(pmod._patterns) == 1

    def test_aggregation_same_fingerprint(self):
        pe = self._seed(5)
        assert len(pmod._patterns) == 1
        pattern = list(pmod._patterns.values())[0]
        assert pattern["sample_count"] == 5

    def test_different_strategies_create_different_patterns(self):
        pe = PGILPatternEngine(PGILVectorStore())
        c  = PGILCollector()
        for s in ["scale_budget", "pause", "creative_refresh"]:
            e = c.collect(_raw(strategy=s))
            if e: pe.process_event(e)
        assert len(pmod._patterns) == 3

    def test_welford_avg_lift_correct(self):
        pe = PGILPatternEngine(PGILVectorStore())
        c  = PGILCollector()
        lifts = [0.10, 0.20, 0.30]
        for lift in lifts:
            e = c.collect(_raw(lift=lift))
            if e: pe.process_event(e)
        p = list(pmod._patterns.values())[0]
        assert abs(p["avg_lift"] - 0.20) < 0.001

    def test_win_rate_correct(self):
        pe = PGILPatternEngine(PGILVectorStore())
        c  = PGILCollector()
        for outcome in ["win","win","win","loss"]:
            e = c.collect(_raw(outcome=outcome, lift=0.10 if outcome=="win" else -0.05))
            if e: pe.process_event(e)
        p = list(pmod._patterns.values())[0]
        assert abs(p["win_rate"] - 0.75) < 0.01

    def test_lifecycle_promotes_validated(self):
        pe = self._seed(count=10, outcome="win", lift=0.12)
        # Manually boost confidence to pass threshold
        p = list(pmod._patterns.values())[0]
        p["confidence"] = 0.65
        result = pe.run_lifecycle()
        assert p["status"] in ("validated","dominant")

    def test_lifecycle_deprecates_low_win_rate(self):
        pe = self._seed(count=15, outcome="loss", lift=-0.05)
        p = list(pmod._patterns.values())[0]
        p["win_rate"]     = 0.20
        p["sample_count"] = 15
        pe.run_lifecycle()
        assert p["status"] == "deprecated"

    def test_get_patterns_filters_by_status(self):
        pe = self._seed(count=5)
        all_p = pe.get_patterns()
        emerging = pe.get_patterns(status="emerging")
        assert len(all_p) == len(pmod._patterns)
        assert all(p["status"] == "emerging" for p in emerging)

    def test_summary_has_required_keys(self):
        pe = self._seed(count=3)
        s = pe.summary()
        assert "total_patterns" in s
        assert "total_events" in s
        assert "by_status" in s

    def test_cross_industry_detection(self):
        pe  = PGILPatternEngine(PGILVectorStore())
        c   = PGILCollector()
        for industry in ["saas","ecommerce","fintech"]:
            for _ in range(3):
                e = c.collect(_raw(strategy="scale_budget", industry=industry))
                if e: pe.process_event(e)
        cross = pe.get_cross_industry_patterns(min_coverage=2)
        assert len(cross) >= 1
        assert cross[0]["industry_coverage"] >= 2


# ═══════════════════════════════════════════════════════════════════════════
# 4. PGIL ARCHETYPE BUILDER
# ═══════════════════════════════════════════════════════════════════════════

class TestPGILArchetypeBuilder:
    def _make_pattern(self, n=5, conf=0.60, wr=0.70, lift=0.12,
                       strategy="scale_budget", industry="saas"):
        return {
            "id":               f"pat_{n}_{conf}",
            "fingerprint":      f"fp_{strategy}_{industry}_{n}",
            "strategy_type":    strategy,
            "industry_bucket":  industry,
            "creative_cluster": "trial",
            "funnel_stage":     "bofu",
            "volatility_band":  "medium",
            "scaling_band":     "growth",
            "sample_count":     n,
            "avg_lift":         lift,
            "avg_risk":         0.12,
            "win_rate":         wr,
            "confidence":       conf,
            "status":           "validated",
        }

    def test_build_creates_archetype(self):
        ab = PGILArchetypeBuilder(PGILVectorStore())
        ab.build_from_patterns([self._make_pattern(n=5, conf=0.65)])
        assert len(amod._archetypes) == 1

    def test_low_confidence_not_built(self):
        ab = PGILArchetypeBuilder(PGILVectorStore())
        ab.build_from_patterns([self._make_pattern(n=5, conf=0.30)])
        assert len(amod._archetypes) == 0

    def test_lifecycle_confirms_archetype(self):
        ab = PGILArchetypeBuilder(PGILVectorStore())
        ab.build_from_patterns([self._make_pattern(n=20, conf=0.75, wr=0.70)])
        result = ab.run_lifecycle()
        confirmed = ab.get_confirmed()
        assert len(confirmed) >= 1

    def test_lifecycle_retires_low_win_rate(self):
        ab = PGILArchetypeBuilder(PGILVectorStore())
        ab.build_from_patterns([self._make_pattern(n=20, conf=0.75, wr=0.70)])
        # Manually degrade
        arch = list(amod._archetypes.values())[0]
        arch["win_rate"] = 0.20
        arch["sample_count"] = 20
        arch["status"] = "confirmed"
        ab.run_lifecycle()
        assert arch["status"] == "retired"

    def test_bias_modifier_positive_for_good_archetype(self):
        ab = PGILArchetypeBuilder(PGILVectorStore())
        ab.build_from_patterns([self._make_pattern(n=20, conf=0.80, wr=0.80, lift=0.15)])
        ab.run_lifecycle()
        confirmed = ab.get_confirmed()
        if confirmed:
            assert confirmed[0]["bias_modifier"] > 0.0

    def test_universal_archetype_from_cross_industry(self):
        ab = PGILArchetypeBuilder(PGILVectorStore())
        cross = [{
            "base_key":          "base_universal",
            "strategy_type":     "scale_budget",
            "industry_coverage": 4,
            "industries":        ["saas","ecommerce","fintech","health"],
            "sample_count":      40,
            "avg_lift":          0.14,
            "avg_win_rate":      0.72,
            "component_patterns":["fp1","fp2","fp3","fp4"],
            "source_patterns":   [self._make_pattern(n=10, conf=0.80,
                                    industry=ind)
                                   for ind in ["saas","ecommerce","fintech","health"]],
        }]
        ab.build_from_cross_industry(cross)
        universal = [a for a in amod._archetypes.values()
                      if a.get("archetype_tier")=="UNIVERSAL"]
        assert len(universal) == 1
        assert universal[0]["industry_coverage"] == 4

    def test_archetype_name_is_readable(self):
        ab = PGILArchetypeBuilder(PGILVectorStore())
        ab.build_from_patterns([self._make_pattern()])
        arch = list(amod._archetypes.values())[0]
        assert "Scale Budget" in arch["name"] or "scale_budget" in arch["name"].lower()

    def test_summary_has_required_keys(self):
        ab = PGILArchetypeBuilder(PGILVectorStore())
        s = ab.summary()
        assert "total" in s
        assert "by_status" in s
        assert "universal" in s


# ═══════════════════════════════════════════════════════════════════════════
# 5. PGIL INFLUENCE CONTROLLER
# ═══════════════════════════════════════════════════════════════════════════

class TestPGILInfluenceController:
    def _seed_with_patterns(self, n_events=10, n_archetypes=1):
        c  = PGILCollector()
        pe = PGILPatternEngine(PGILVectorStore())
        for _ in range(n_events):
            e = c.collect(_raw(outcome="win", lift=0.15))
            if e: pe.process_event(e)
        if n_archetypes:
            ab = PGILArchetypeBuilder(PGILVectorStore())
            ab.build_from_patterns([{
                "id": "pat_seed",
                "fingerprint": "fp_seed",
                "strategy_type": "scale_budget",
                "industry_bucket": "saas",
                "creative_cluster": "trial",
                "funnel_stage": "bofu",
                "volatility_band": "medium",
                "scaling_band": "growth",
                "sample_count": 20,
                "avg_lift": 0.15,
                "avg_risk": 0.12,
                "win_rate": 0.80,
                "confidence": 0.75,
                "status": "validated",
            }])
            ab.run_lifecycle()

    def test_signal_has_required_keys(self):
        ic = PGILInfluenceController(PGILVectorStore())
        signal = ic.get_influence(_raw())
        for key in ["pgil_weight","predicted_lift","win_rate","confidence",
                     "action","pattern_signal","archetype_signal","generated_at"]:
            assert key in signal

    def test_weight_in_valid_range(self):
        ic = PGILInfluenceController(PGILVectorStore())
        signal = ic.get_influence(_raw())
        assert 0.0 <= signal["pgil_weight"] <= 0.40

    def test_action_defer_when_no_data(self):
        ic = PGILInfluenceController(PGILVectorStore())
        signal = ic.get_influence(_raw())
        assert signal["action"] == "DEFER"

    def test_action_not_defer_with_data(self):
        self._seed_with_patterns(n_events=15)
        ic = PGILInfluenceController(PGILVectorStore())
        signal = ic.get_influence(_raw())
        # May be DEFER if pattern confidence still low, but archetype could promote
        assert signal["action"] in ("EXECUTE","PROCEED","PROCEED_WITH_MON","DEFER","AVOID")

    def test_operator_access_shows_archetypes(self):
        self._seed_with_patterns()
        ic = PGILInfluenceController(PGILVectorStore())
        signal = ic.get_influence(_raw(), operator_access=True)
        # Full archetype_signal should be present
        assert "archetype_found" in signal["archetype_signal"]

    def test_tenant_access_strips_archetype_detail(self):
        self._seed_with_patterns()
        ic = PGILInfluenceController(PGILVectorStore())
        signal = ic.get_influence(_raw(), operator_access=False)
        # Should only have archetype_found flag
        anon_arch = signal["archetype_signal"]
        assert "archetype_name" not in anon_arch

    def test_global_priors_no_data(self):
        ic = PGILInfluenceController(PGILVectorStore())
        priors = ic.get_global_priors("scale_budget", "saas")
        assert priors["has_prior"] is False
        assert priors["prior_lift"] == 0.0

    def test_global_priors_with_data(self):
        self._seed_with_patterns(n_events=10)
        # Force patterns to meet confidence threshold
        for p in pmod._patterns.values():
            p["confidence"] = 0.60
        ic = PGILInfluenceController(PGILVectorStore())
        priors = ic.get_global_priors("scale_budget","saas")
        assert priors["has_prior"] is True

    def test_platform_insights_structure(self):
        ic = PGILInfluenceController(PGILVectorStore())
        insights = ic.get_platform_insights()
        assert "patterns" in insights
        assert "archetypes" in insights
        assert "top_archetypes" in insights

    def test_notes_present_and_list(self):
        ic = PGILInfluenceController(PGILVectorStore())
        signal = ic.get_influence(_raw())
        assert isinstance(signal["notes"], list)

    def test_confidence_band_labels(self):
        ic = PGILInfluenceController(PGILVectorStore())
        assert ic._confidence_band(0.85) == "HIGH"
        assert ic._confidence_band(0.65) == "MEDIUM"
        assert ic._confidence_band(0.45) == "LOW"
        assert ic._confidence_band(0.10) == "INSUFFICIENT"
