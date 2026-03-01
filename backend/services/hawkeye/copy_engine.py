import logging
import re
from typing import Dict, Any

from backend.services.hawkeye.schemas import CopyMetricsSchema

logger = logging.getLogger(__name__)

class CopyEngine:
    """
    Applies deterministic regex mapping and simulated NLP sequence classifications 
    to extract Urgency, Tone, and Core Offer hooks.
    """

    def _calculate_readability(self, text: str) -> float:
        """Simulates Flesch-Kincaid basic math"""
        words = len(text.split())
        sentences = max(1, len(re.split(r'[.!?]+', text)) - 1)
        return round(min(1.0, 10.0 / max(1, (words / sentences))), 2)

    def analyze_copy(self, primary_text: str, headline: str) -> CopyMetricsSchema:
        """
        Transforms string inputs into strict mathematical NLP signatures.
        """
        logger.info("Hawkeye Copy Engine analyzing linguistic patterns...")
        full_text = f"{headline} {primary_text}".lower()
        
        urgency_regex = r"\b(now|limited|hurry|expires|today|fast|exclusive)\b"
        trust_regex = r"\b(guarantee|secure|proven|rated|trusted|certified)\b"
        problem_regex = r"\b(tired|struggling|hard|pain|costly|bad|issue)\b"
        
        urgency_detected = bool(re.search(urgency_regex, full_text))
        
        # Simulating DistilBERT classification vectors
        emotion = "urgency" if urgency_detected else ("trust" if re.search(trust_regex, full_text) else "neutral")
        
        problem_score = min(1.0, len(re.findall(problem_regex, full_text)) * 0.3)
        benefit_score = 1.0 - problem_score
        
        # Extract Offer Type logic (E.g. Discount vs Trial)
        offer = "Standard"
        if "% off" in full_text or "discount" in full_text:
             offer = "Discount"
        elif "free trial" in full_text:
             offer = "Trial"
             
        metric = CopyMetricsSchema(
             readability_score=self._calculate_readability(full_text),
             urgency_detected=urgency_detected,
             sentiment_polarity=0.8 if emotion == "trust" else (0.2 if problem_score > 0.5 else 0.5), # Fake polarity map
             benefit_framing_score=round(benefit_score, 2),
             problem_framing_score=round(problem_score, 2),
             primary_emotion=emotion,
             offer_extracted=offer
        )
        
        logger.debug(f"Copy Engine inference complete. Primary Tone: {metric.primary_emotion}")
        return metric
