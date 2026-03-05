"""
Creative Genome Mapping Engine - Full Test Suite
================================================
All tests run without GPU, Models, or Qdrant locally.
"""

import pytest
import math

from backend.services.intelligence.creative_genome.genome_extractor import GenomeExtractor
from backend.services.intelligence.creative_genome.persuasion_classifier import PersuasionClassifier
from backend.services.intelligence.creative_genome.structure_analyzer import StructureAnalyzer
from backend.services.intelligence.creative_genome.genome_vectorizer import GenomeVectorizer
from backend.services.intelligence.creative_genome.genome_cluster_engine import GenomeClusterEngine
from backend.services.intelligence.creative_genome.creative_archetype_builder import CreativeArchetypeBuilder
from backend.services.intelligence.creative_genome.creative_strategy_engine import CreativeStrategyEngine
from backend.services.intelligence.creative_genome.models import CreativeStrategySignal


# --- 1. Genome Extractor ---

class TestGenomeExtractor:
    def test_extract_hook_problem(self):
        e = GenomeExtractor()
        g = e.extract({"headline": "Tired of wasting money on ads?"})
        assert g["hook_type"] == "problem_agitation"

    def test_extract_emotion_urgency(self):
        e = GenomeExtractor()
        g = e.extract({"body_text": "Act fast before this limited time offer ends today."})
        assert g["emotion"] == "urgency"

    def test_extract_authority(self):
        e = GenomeExtractor()
        g = e.extract({"body_text": "expert certified PhD recommended."})
        assert g["authority_signal"] == "expert"

    def test_pacing_fast_video(self):
        e = GenomeExtractor()
        g = e.extract({"cta_text": "hurry now", "is_video": True})
        assert g["pacing"] == "fast"

    def test_structure_pain(self):
        e = GenomeExtractor()
        g = e.extract({"body_text": "problem scaling? here is our solution with proven results. 50% discount."})
        assert g["structure"] == "pain_solution_proof"


# --- 2. Persuasion Classifier ---

class TestPersuasionClassifier:
    def test_scarcity(self):
        p = PersuasionClassifier()
        res = p.classify("selling out fast, only 3 spots left! limited time.")
        assert "scarcity" in res["techniques"]
        assert res["primary_technique"] == "scarcity"

    def test_social_proof(self):
        p = PersuasionClassifier()
        res = p.classify("Join 100k+ happy customers and trusted brands today.")
        assert "social_proof" in res["techniques"]

    def test_reciprocity(self):
        p = PersuasionClassifier()
        res = p.classify("Take this free gift on us, no strings attached.")
        assert "reciprocity" in res["techniques"]

    def test_high_manipulation(self):
        p = PersuasionClassifier()
        # Mix high intensity techniques
        text = "only 2 left! only 5 spots! hurry hurry! dr. phd recommended. dr. expert miss out miss out risk danger. free gift free gift. secret discover secret hidden."
        res = p.classify(text)
        assert res["manipulation_risk"] == "high"


# --- 3. Structure Analyzer ---

class TestStructureAnalyzer:
    def test_pain_solution_proof(self):
        s = StructureAnalyzer()
        res = s.analyze("tired of this problem? the answer is here. proven to work by case study. click here.")
        assert res["pattern_code"] == "C" # Pain -> Solution -> Proof
        assert "problem" in res["stages"]

    def test_story_transformation(self):
        s = StructureAnalyzer()
        res = s.analyze("I was just like you, until everything changed. Now I'm successful. sign up.")
        assert "story" in res["stages"]
        assert "transformation" in res["stages"]

    def test_direct_offer(self):
        s = StructureAnalyzer()
        res = s.analyze("get 50% discount today. buy now.")
        assert "offer" in res["stages"] or "direct_offer" in res["stages"]


# --- 4. Vectorizer ---

class TestGenomeVectorizer:
    def test_feature_vector_dimension(self):
        v = GenomeVectorizer()
        g = GenomeExtractor().extract({"headline": "problem. act fast."})
        vec = v.feature_vector(g)
        assert len(vec) == 384

    def test_fingerprint_deterministic(self):
        v = GenomeVectorizer()
        g = {"hook_type": "curiosity", "emotion": "fear", "authority_signal": "expert"}
        f1 = v.fingerprint(g)
        f2 = v.fingerprint(g)
        assert f1 == f2


# --- 5. Cluster Engine ---

@pytest.fixture
def ce():
    import backend.services.intelligence.creative_genome.genome_cluster_engine as mod
    mod._clusters.clear()
    mod._genome_store.clear()
    return GenomeClusterEngine()

class TestGenomeClusterEngine:
    def test_cluster_assignment(self, ce):
        g = {"hook_type": "problem_agitation", "emotion": "fear"}
        cid = ce.add_genome(g, outcome="win", ctr_lift=0.10)
        assert len(ce.get_clusters()) == 1
        
        # Add similar
        ce.add_genome(g, outcome="win", ctr_lift=0.15)
        assert ce.get_clusters()[0]["member_count"] == 2
        assert ce.get_clusters()[0]["avg_ctr_lift"] == 0.125

    def test_cluster_saturation(self, ce):
        g = {"hook_type": "curiosity", "emotion": "joy"}
        # Fill it up
        for _ in range(25):
            ce.add_genome(g, outcome="win", ctr_lift=0.05)
        
        ce.run_lifecycle()
        c = ce.get_clusters()[0]
        assert c["saturation_score"] > 0.60

    def test_declining_status(self, ce):
        g = {"hook_type": "story", "emotion": "trust"}
        for _ in range(8):
            ce.add_genome(g, outcome="loss", ctr_lift=-0.1)
            
        ce.run_lifecycle()
        assert ce.get_clusters()[0]["status"] == "declining"


# --- 6. Archetype Builder ---

@pytest.fixture
def ab(ce):
    import backend.services.intelligence.creative_genome.creative_archetype_builder as mod
    mod._archetypes.clear()
    return CreativeArchetypeBuilder(cluster_engine=ce)

class TestCreativeArchetypeBuilder:
    def test_candidate_archetype(self, ab, ce):
        g = {"hook_type": "authority", "emotion": "trust", "authority_signal": "expert"}
        for _ in range(5):
            ce.add_genome(g, outcome="win", ctr_lift=0.15)
        
        ab.build_from_clusters(ce.get_clusters())
        import backend.services.intelligence.creative_genome.creative_archetype_builder as mod
        assert len(mod._archetypes) == 1
        arch = list(mod._archetypes.values())[0]
        assert arch["status"] == "candidate"

    def test_confirmed_archetype(self, ab, ce):
        g = {"hook_type": "bold_claim", "emotion": "urgency", "authority_signal": "data_stats"}
        # High wins, high samples
        for _ in range(15):
            ce.add_genome(g, outcome="win", ctr_lift=0.20)
        
        ce.run_lifecycle()
        ab.build_from_clusters(ce.get_clusters())
        ab.run_lifecycle()
        
        confirmed = ab.get_confirmed()
        assert len(confirmed) == 1
        assert confirmed[0]["expected_ctr_lift"] > 0
        assert confirmed[0]["bias_modifier"] > 0


# --- 7. Strategy Engine ---

@pytest.fixture
def se(ab, ce):
    return CreativeStrategyEngine(cluster_engine=ce, archetype_builder=ab)

class TestCreativeStrategyEngine:
    def test_saturation_signal(self, se, ce, ab):
        g = {"hook_type": "shock", "emotion": "fear", "ctr_lift": 0.01}
        for _ in range(25):
            ce.add_genome(g, outcome="win", ctr_lift=0.01)
        ce.run_lifecycle()

        sig = se.generate_signal(g)
        assert sig is not None
        assert sig["signal_type"] == "CLUSTER_SATURATION"

    def test_fatigue_signal(self, se, ce):
        g = {"hook_type": "question", "emotion": "guilt", "ctr_lift": -0.05}
        for _ in range(12):
            ce.add_genome(g, outcome="loss", ctr_lift=-0.05)
        ce.run_lifecycle()

        sig = se.generate_signal(g)
        assert sig is not None
        assert sig["signal_type"] == "FATIGUE"
        assert sig["severity"] == "HIGH"

    def test_pivot_recommendation(self, se, ce, ab):
        # Create a bad cluster
        bad_g = {"hook_type": "question", "emotion": "guilt", "ctr_lift": -0.05, "industry": "saas"}
        for _ in range(12): ce.add_genome(bad_g, outcome="loss", industry="saas", ctr_lift=-0.05)
        
        # Create a great, confirmed cluster for the same industry
        good_g = {"hook_type": "bold_claim", "emotion": "urgency"}
        for _ in range(15): ce.add_genome(good_g, outcome="win", ctr_lift=0.20, industry="saas")
        
        ce.run_lifecycle()
        ab.build_from_clusters(ce.get_clusters())
        ab.run_lifecycle()

        # Generate signal for bad genome
        sig = se.generate_signal(bad_g, industry="saas")
        assert sig["archetype_id"] is not None
        assert "bold_claim" in str(sig["recommended_tests"])
