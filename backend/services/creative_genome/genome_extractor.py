"""
Genome Extractor
================
Decomposes a creative asset into its genetic components.

Input:
  CreativeInput dict {
    headline:    str
    body_text:   str
    cta_text:    str
    description: str  (optional)
    platform:    str  (optional)
    is_video:    bool (optional)
  }

Output:
  CreativeGenome dict {
    hook_type, emotion, authority_signal,
    offer_type, cta_style, pacing, structure
  }

Algorithm:
  Priority-ordered keyword rules → fast, deterministic, no model required.
  Optional LLM enhancement layer (falls back gracefully if unavailable).
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Keyword rule tables ────────────────────────────────────────────────────

HOOK_RULES: List[Tuple[str, List[str]]] = [
    ("problem_agitation",  ["tired of", "struggling with", "frustrated", "sick of",
                             "problem", "pain", "challenge", "broken", "failing"]),
    ("curiosity",          ["secret", "little known", "what nobody tells", "discover",
                             "hidden", "surprising", "shocking truth", "find out", "weird trick"]),
    ("authority",          ["award", "trusted by", "#1", "leading", "certified", "expert",
                             "according to", "study shows", "proven", "doctor"]),
    ("story",              ["i was", "i used to", "my story", "it started when",
                             "one day", "we built", "our founder", "years ago"]),
    ("shock",              ["stop", "warning", "danger", "never do this", "biggest mistake",
                             "you're wrong about", "myth busted"]),
    ("question",           ["are you", "do you", "have you ever", "what if", "did you know",
                             "how many", "when was the last time"]),
    ("bold_claim",         ["fastest", "easiest", "guaranteed", "100%", "zero", "instant",
                             "in 24 hours", "in 7 days", "completely"]),
    ("pattern_interrupt",  ["wait", "hold on", "before you scroll", "this is different",
                             "not another", "unlike anything"]),
]

EMOTION_RULES: List[Tuple[str, List[str]]] = [
    ("urgency",       ["now", "today", "limited", "expires", "last chance", "ending soon",
                        "hurry", "don't wait", "act fast", "before it's too late"]),
    ("fear",          ["risk", "danger", "lose", "miss out", "left behind", "penalty",
                        "consequence", "failure", "too late"]),
    ("joy",           ["love", "amazing", "incredible", "delight", "happy", "fun",
                        "enjoy", "celebrate", "smile", "best day"]),
    ("trust",         ["safe", "secure", "guaranteed", "proven", "verified", "reliable",
                        "honest", "transparent", "no risk"]),
    ("curiosity",     ["wonder", "discover", "explore", "find out", "reveal", "learn",
                        "curious", "surprising", "unexpected"]),
    ("pride",         ["achieve", "accomplish", "elite", "exclusive", "top performer",
                        "better than", "outperform", "status"]),
    ("guilt",         ["still doing", "wasting time", "falling behind", "leaving money",
                        "you should", "you know better"]),
    ("excitement",    ["launch", "new", "introducing", "just released", "breaking",
                        "game changer", "revolutionary", "unstoppable"]),
    ("aspirational",  ["imagine", "dream", "become", "transform", "vision", "future",
                        "potential", "level up", "next level"]),
]

AUTHORITY_RULES: List[Tuple[str, List[str]]] = [
    ("expert",       ["dr.", "expert", "specialist", "ceo", "founder", "scientist",
                       "phd", "professor", "coach", "advisor"]),
    ("celebrity",    ["as seen on", "featured in", "endorsed by", "celebrity", "influencer"]),
    ("social_proof", ["customers", "users", "people", "businesses", "brands",
                       "join", "community", "members", "reviews", "rated"]),
    ("data_stats",   ["%", "million", "billion", "x faster", "x more", "study", "research",
                       "data shows", "according to", "statistic"]),
    ("award",        ["award", "winner", "best in class", "top rated", "g2", "capterra",
                       "recognized", "certified"]),
    ("media_logo",   ["as seen on", "featured in", "forbes", "techcrunch", "wired",
                       "bloomberg", "bbc", "cnn", "nyt"]),
    ("testimonial",  ["testimonial", "review", "quote", "said", "says", "told us",
                       '"', "★", "⭐", "stars"]),
]

OFFER_RULES: List[Tuple[str, List[str]]] = [
    ("discount",    ["% off", "save", "discount", "deal", "offer", "coupon", "promo"]),
    ("trial",       ["free trial", "try free", "14-day", "30-day", "no credit card",
                      "risk-free trial", "test drive"]),
    ("demo",        ["demo", "book a call", "see it in action", "live demo", "walkthrough"]),
    ("bundle",      ["bundle", "package", "combo", "toolkit", "suite", "all-in-one"]),
    ("guarantee",   ["guarantee", "money back", "refund", "no questions", "or your money"]),
    ("gift",        ["free gift", "bonus", "get free", "included free", "complimentary"]),
    ("exclusivity", ["exclusive", "vip", "members only", "invite only", "limited access"]),
]

CTA_RULES: List[Tuple[str, List[str]]] = [
    ("scarcity",      ["only", "left", "spots", "limited", "today only", "ends tonight"]),
    ("benefit_lead",  ["get", "start", "unlock", "access", "claim", "grab", "download"]),
    ("social",        ["join", "community", "others", "together", "us", "team"]),
    ("question",      ["ready to", "want to", "tired of", "curious about"]),
    ("soft_invite",   ["learn more", "find out", "see how", "discover", "explore"]),
    ("direct_command",["click", "buy", "sign up", "register", "order", "shop", "subscribe"]),
]

STRUCTURE_PATTERNS = {
    "pain_solution_proof":   ["problem", "solution", "proof"],
    "before_after_bridge":   ["before", "after", "bridge"],
    "hook_story_offer_cta":  ["hook", "story", "offer"],
    "problem_agit_solution": ["problem", "agit", "solution"],
    "testimonial_proof":     ["testimonial", "proof", "cta"],
    "curiosity_reveal":      ["curiosity", "reveal", "proof"],
    "features_benefits_cta": ["feature", "benefit", "cta"],
    "direct_offer":          ["offer", "cta"],
}

# Pacing keyword signals
FAST_SIGNALS = ["now", "instantly", "immediately", "fast", "quick", "today", "right now",
                 "don't wait", "limited time", "hurry", "today only"]
SLOW_SIGNALS = ["discover", "learn", "explore", "understand", "journey", "story", "imagine",
                 "slowly", "take your time", "at your own pace"]


def _first_match(text: str, rules: List[Tuple[str, List[str]]],
                  default: str = "unknown") -> str:
    low = text.lower()
    for label, kws in rules:
        if any(kw in low for kw in kws):
            return label
    return default


def _all_matches(text: str, rules: List[Tuple[str, List[str]]]) -> List[str]:
    low = text.lower()
    return [label for label, kws in rules if any(kw in low for kw in kws)]


class GenomeExtractor:
    """
    Decomposes a creative into its genomic components using
    priority-ordered keyword matching.  No model dependency required.
    """

    def extract(self, creative: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main extraction entry point.
        Returns a complete genome dict.
        """
        combined  = self._combine(creative)
        headline  = creative.get("headline", "")
        cta_text  = creative.get("cta_text", "")
        body      = creative.get("body_text", "")

        genome = {
            "hook_type":        self._hook(headline or combined),
            "emotion":          self._emotion(combined),
            "authority_signal": self._authority(combined),
            "offer_type":       self._offer(combined),
            "cta_style":        self._cta(cta_text or combined),
            "pacing":           self._pacing(combined, is_video=creative.get("is_video", False)),
            "structure":        self._structure(combined),
            "persuasion_hints": _all_matches(combined, HOOK_RULES + EMOTION_RULES),
        }

        logger.info(
            f"[GenomeExtractor] hook={genome['hook_type']} "
            f"emotion={genome['emotion']} "
            f"structure={genome['structure']} "
            f"authority={genome['authority_signal']}"
        )
        return genome

    def extract_batch(self, creatives: List[Dict]) -> List[Dict]:
        return [self.extract(c) for c in creatives]

    # ── Component extractors ──────────────────────────────────────────────

    def _hook(self, text: str) -> str:
        # Look only at first 200 chars for hook
        return _first_match(text[:200], HOOK_RULES, default="bold_claim")

    def _emotion(self, text: str) -> str:
        return _first_match(text, EMOTION_RULES, default="neutral")

    def _authority(self, text: str) -> str:
        return _first_match(text, AUTHORITY_RULES, default="none")

    def _offer(self, text: str) -> str:
        return _first_match(text, OFFER_RULES, default="direct")

    def _cta(self, text: str) -> str:
        return _first_match(text, CTA_RULES, default="direct_command")

    def _pacing(self, text: str, is_video: bool = False) -> str:
        low = text.lower()
        fast_score = sum(1 for w in FAST_SIGNALS if w in low)
        slow_score = sum(1 for w in SLOW_SIGNALS if w in low)
        # Video ads default toward faster
        if is_video:
            fast_score += 1
        if fast_score > slow_score + 1:
            return "fast"
        if slow_score > fast_score + 1:
            return "slow"
        if fast_score == slow_score and fast_score > 0:
            return "varied"
        return "medium"

    def _structure(self, text: str) -> str:
        """Heuristically detect narrative structure from keyword presence."""
        low = text.lower()

        pain    = any(w in low for w in ["problem", "struggling", "tired of", "pain", "broken"])
        proof   = any(w in low for w in ["proof", "proven", "testimonial", "results", "trusted", "study"])
        story   = any(w in low for w in ["story", "i was", "my journey", "it started", "i used to"])
        offer   = any(w in low for w in ["offer", "trial", "discount", "% off", "get", "free"])
        before  = any(w in low for w in ["before", "used to", "once"])
        after   = any(w in low for w in ["after", "now", "today", "transformed"])
        curiosity = any(w in low for w in ["discover", "secret", "hidden", "find out"])
        feature = any(w in low for w in ["feature", "includes", "comes with", "designed"])

        if pain and proof and offer:   return "pain_solution_proof"
        if before and after:           return "before_after_bridge"
        if story and offer:            return "hook_story_offer_cta"
        if pain and not proof:         return "problem_agit_solution"
        if curiosity and proof:        return "curiosity_reveal"
        if proof and not pain:         return "testimonial_proof"
        if feature and offer:          return "features_benefits_cta"
        if offer:                      return "direct_offer"
        return "unknown"

    @staticmethod
    def _combine(creative: Dict[str, Any]) -> str:
        parts = [
            creative.get("headline", ""),
            creative.get("body_text", ""),
            creative.get("cta_text", ""),
            creative.get("description", ""),
            creative.get("raw_transcript", ""),
        ]
        return " ".join(p for p in parts if p)
