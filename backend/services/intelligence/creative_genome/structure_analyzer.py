"""
Structure Analyzer
==================
Detects storytelling / narrative structure patterns in creative copy.

Supports:
  Pattern A: Hook → Problem → Agitation → Offer → CTA
  Pattern B: Hook → Story → Transformation → CTA
  Pattern C: Pain → Solution → Proof → CTA
  Pattern D: Question → Curiosity → Reveal → CTA
  Pattern E: Before → After → Bridge → CTA
  Pattern F: Authority → Claim → Proof → Guarantee → CTA
  Pattern G: Feature → Benefit → Social Proof → CTA
  Pattern H: Direct Offer → CTA

Outputs:
  {
    detected_pattern:  str              — best matching pattern name
    pattern_code:      str              — A/B/C/D/E/F/G/H
    stages:            List[str]        — ordered narrative stages found
    completeness:      float            — 0-1: how complete the pattern is
    narrative_flow:    List[str]        — human-readable stage labels
    pattern_variants:  List[str]        — other patterns partially matched
    word_count:        int
    estimated_read_s:  float            — read time in seconds
  }
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Structural stage signals ──────────────────────────────────────────────

STAGE_SIGNALS: Dict[str, List[str]] = {
    "hook":          ["stop", "listen", "wait", "before you", "are you", "do you",
                       "this is", "imagine", "what if", "picture this"],
    "problem":       ["problem", "struggling", "challenge", "difficulty", "tired of",
                       "frustrated", "don't know how", "can't figure out", "pain"],
    "agitation":     ["worse", "getting worse", "failing", "costing you", "every day you",
                       "money down", "falling behind", "competitors are", "it's not your fault"],
    "story":         ["story", "i was", "my name is", "we started", "it began",
                       "when i", "years ago", "one day"],
    "transformation":["until", "then i", "that's when", "everything changed",
                       "transformed", "breakthrough", "discovered", "found"],
    "solution":      ["solution", "answer", "introducing", "that's why", "so we built",
                       "we created", "now you can", "here's how"],
    "proof":         ["proof", "proven", "results", "testimonial", "case study",
                       "% increase", "% growth", "trusted by", "rated", "reviews"],
    "offer":         ["offer", "get", "now for", "only $", "save", "free trial",
                       "bonus", "discount", "bundle", "package"],
    "guarantee":     ["guarantee", "money back", "risk free", "no questions", "refund"],
    "cta":           ["click", "sign up", "get started", "shop now", "learn more",
                       "download", "book", "subscribe", "try", "start today"],
    "curiosity":     ["secret", "discover", "find out", "what nobody", "hidden",
                       "not what you think", "the truth"],
    "reveal":        ["here's what", "the answer is", "that's why", "this is how"],
    "before":        ["before", "used to", "once i", "a year ago", "at first"],
    "after":         ["after", "now i", "today", "since then", "has changed"],
    "bridge":        ["thanks to", "with this", "using", "because of", "that's how"],
    "authority":     ["dr.", "expert", "certified", "years of experience", "study", "research"],
    "claim":         ["guarantees", "delivers", "produces", "generates", "achieves"],
    "feature":       ["includes", "comes with", "features", "designed to", "built for"],
    "benefit":       ["so you can", "which means", "allowing you", "helping you", "giving you"],
    "social_proof":  ["customers love", "users say", "people trust", "join", "rated"],
    "direct_offer":  ["get yours", "order now", "buy now", "limited time", "available now"],
}

# Named patterns with required stage sequences
PATTERNS: List[Tuple[str, str, List[str]]] = [
    ("A", "Hook → Problem → Agitation → Offer → CTA",    ["hook","problem","agitation","offer","cta"]),
    ("B", "Hook → Story → Transformation → CTA",          ["hook","story","transformation","cta"]),
    ("C", "Pain → Solution → Proof → CTA",                ["problem","solution","proof","cta"]),
    ("D", "Question → Curiosity → Reveal → CTA",          ["hook","curiosity","reveal","cta"]),
    ("E", "Before → After → Bridge → CTA",                ["before","after","bridge","cta"]),
    ("F", "Authority → Claim → Proof → Guarantee → CTA",  ["authority","claim","proof","guarantee","cta"]),
    ("G", "Feature → Benefit → Social Proof → CTA",       ["feature","benefit","social_proof","cta"]),
    ("H", "Direct Offer → CTA",                           ["direct_offer","cta"]),
]

WORDS_PER_MINUTE = 238.0


class StructureAnalyzer:
    """
    Detects narrative structure from creative copy.
    Scores each known pattern and selects the best match.
    """

    def analyze(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return self._empty()

        low        = text.lower()
        word_count = len(text.split())
        read_time  = round(word_count / WORDS_PER_MINUTE * 60, 1)

        # Detect which stages are present
        detected_stages = self._detect_stages(low)

        # Score each pattern
        best_code   = "H"
        best_name   = "Direct Offer → CTA"
        best_stages: List[str] = []
        best_score  = 0.0
        variants    = []

        for code, name, required in PATTERNS:
            present = [s for s in required if s in detected_stages]
            score   = len(present) / len(required)
            if score > best_score:
                best_score, best_code, best_name, best_stages = score, code, name, present
            if 0.40 <= score < best_score:
                variants.append(name)

        completeness   = round(best_score, 3)
        narrative_flow = [self._stage_label(s) for s in best_stages]

        result = {
            "detected_pattern":  best_name,
            "pattern_code":      best_code,
            "stages":            best_stages,
            "completeness":      completeness,
            "narrative_flow":    narrative_flow,
            "pattern_variants":  variants,
            "word_count":        word_count,
            "estimated_read_s":  read_time,
            "all_detected_stages": list(detected_stages),
        }

        logger.debug(
            f"[StructureAnalyzer] pattern={best_code} completeness={completeness:.0%} "
            f"stages={best_stages}"
        )
        return result

    def get_stage_sequence(self, text: str) -> List[str]:
        """Return ordered list of detected stage labels."""
        return self.analyze(text)["stages"]

    # ── Internals ─────────────────────────────────────────────────────────

    @staticmethod
    def _detect_stages(text: str) -> set:
        found = set()
        for stage, signals in STAGE_SIGNALS.items():
            if any(sig in text for sig in signals):
                found.add(stage)
        return found

    @staticmethod
    def _stage_label(stage: str) -> str:
        labels = {
            "hook": "Hook", "problem": "Problem", "agitation": "Agitation",
            "story": "Story", "transformation": "Transformation", "solution": "Solution",
            "proof": "Proof", "offer": "Offer", "guarantee": "Guarantee", "cta": "CTA",
            "curiosity": "Curiosity Build", "reveal": "Reveal", "before": "Before",
            "after": "After", "bridge": "Bridge", "authority": "Authority",
            "claim": "Bold Claim", "feature": "Feature", "benefit": "Benefit",
            "social_proof": "Social Proof", "direct_offer": "Direct Offer",
        }
        return labels.get(stage, stage.title())

    @staticmethod
    def _empty() -> Dict[str, Any]:
        return {
            "detected_pattern": "unknown", "pattern_code": "X",
            "stages": [], "completeness": 0.0, "narrative_flow": [],
            "pattern_variants": [], "word_count": 0, "estimated_read_s": 0.0,
            "all_detected_stages": [],
        }
