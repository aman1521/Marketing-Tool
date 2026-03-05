"""
Persuasion Classifier
=====================
Detects Cialdini-style persuasion techniques in creative copy.

Techniques detected:
  SCARCITY      — limited time/quantity signals
  AUTHORITY     — expert/stat-backed credibility
  SOCIAL_PROOF  — crowd/review/user count signals
  RECIPROCITY   — giving value before asking
  COMMITMENT    — micro-yes / consistency signals
  LIKING        — likability / shared identity
  FEAR_FOMO     — fear of missing out / negative outcome
  CURIOSITY     — open loop / information gap
  NOVELTY       — new/different/first signals
  LOSS_AVERSION — framing around what they'll lose, not gain

Output per classification:
  {
    techniques: List[str]          — detected techniques
    primary_technique: str         — dominant technique
    technique_scores: Dict[str, float]  — 0-1 intensity per technique
    persuasion_density: float      — techniques per 100 words
    manipulation_risk: str         — low / medium / high
  }
"""

import re
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

TECHNIQUE_RULES: Dict[str, List[str]] = {
    "scarcity": [
        "limited time", "limited offer", r"only .* left", r"ends (today|tonight|soon)",
        "last chance", "hurry", "selling out", "almost gone", "while supplies last",
        r"only \d+ (spots|seats|units)", "expires", "today only", "48 hours"
    ],
    "authority": [
        r"dr\.", "expert", "scientist", r"\d{4} study", "research shows", "according to",
        "certified", "phd", "professor", r"top \d+", "leading", "#1", "best-selling",
        "award-winning", "industry leader", "pioneer"
    ],
    "social_proof": [
        r"\d{2,}[k,]?\+?\s+(customers|users|brands|businesses|teams|members|reviews)",
        r"join \d+", "trusted by", r"rated \d", r"\d+ stars", "reviews", "community",
        "others are", "people love", "everyone's using"
    ],
    "reciprocity": [
        "free", "give you", "gift", "bonus", "no strings", "without asking",
        "complimentary", "on us", "we'll pay", "you deserve", "thank you"
    ],
    "commitment": [
        "start small", "just try", "one step", "first step", "no commitment",
        "cancel anytime", "take the first", "agree", "save your spot", "join now"
    ],
    "liking": [
        "people like you", "just like", "same as you", "we understand",
        "we've been there", "built by marketers", "made for", "you're not alone",
        "we were in your shoes"
    ],
    "fear_fomo": [
        "miss out", "left behind", "fall behind", "what if you don't", "while others",
        "your competitors", "risk", "don't lose", "before it's too late", "regret"
    ],
    "curiosity": [
        "secret", "discover", "hidden", "what nobody tells", "you won't believe",
        "surprising", "the truth about", "little-known", "mind-blowing", "find out"
    ],
    "novelty": [
        "new", "introducing", "first-ever", "just launched", "breaking", "never before",
        "revolutionar", "game-changing", "unlike anything", "pioneering"
    ],
    "loss_aversion": [
        "don't lose", "stop wasting", "still paying", "you're losing", "every day you wait",
        "money down the drain", "leaving money", "burning", "costly mistake", "you're missing"
    ],
}

# Number of keywords to qualify a technique (weighted by pattern count)
DETECTION_THRESHOLD = 1

MANIPULATION_THRESHOLDS = {
    "low":    (0, 2),
    "medium": (2, 4),
    "high":   (4, 999),
}


class PersuasionClassifier:
    """
    Detects psychological persuasion techniques in ad creative copy.
    Rule-based with regex patterns — no model required.
    """

    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classify persuasion techniques in a text string.
        Returns classification result with scores.
        """
        if not text or not text.strip():
            return self._empty_result()

        low       = text.lower()
        word_count= max(1, len(text.split()))
        scores: Dict[str, float] = {}

        for technique, patterns in TECHNIQUE_RULES.items():
            matches = 0
            for p in patterns:
                try:
                    matches += len(re.findall(p, low))
                except re.error:
                    if p.lower() in low:
                        matches += 1
            # Normalise by text length + pattern count
            raw_score = matches / len(patterns)
            scores[technique] = round(min(1.0, raw_score * 3), 3)

        detected  = [t for t, s in scores.items() if s > 0.05]
        primary   = max(scores, key=scores.get) if scores else "none"
        density   = round(len(detected) / word_count * 100, 2)
        n_high    = sum(1 for s in scores.values() if s > 0.30)
        manip     = self._manipulation_risk(n_high)

        result = {
            "techniques":         detected,
            "primary_technique":  primary if scores.get(primary, 0) > 0.05 else "none",
            "technique_scores":   {t: s for t, s in scores.items() if s > 0},
            "persuasion_density": density,
            "technique_count":    len(detected),
            "manipulation_risk":  manip,
        }

        logger.debug(
            f"[PersuasionClassifier] primary={result['primary_technique']} "
            f"techniques={result['techniques']} density={density}"
        )
        return result

    def classify_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        return [self.classify(t) for t in texts]

    def dominant_technique(self, text: str) -> str:
        result = self.classify(text)
        return result["primary_technique"]

    # ── Intensity helpers ─────────────────────────────────────────────────

    @staticmethod
    def _manipulation_risk(n_high: int) -> str:
        for label, (lo, hi) in MANIPULATION_THRESHOLDS.items():
            if lo <= n_high < hi:
                return label
        return "high"

    @staticmethod
    def _empty_result() -> Dict[str, Any]:
        return {
            "techniques": [], "primary_technique": "none",
            "technique_scores": {}, "persuasion_density": 0.0,
            "technique_count": 0, "manipulation_risk": "low",
        }
