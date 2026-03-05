"""
Strategy Gap Analyzer
=====================
Consumes crawled content, ad creatives, cluster signals, and market
pressure data to produce structured JSON strategy gap insights
for CaptainStrategy.

Output is READ-ONLY signal — no execution side effects.
CaptainStrategy decides whether and how to act on these signals.

Gap types:
  POSITIONING   — how competitor frames themselves vs company
  CONTENT       — content themes competitor targets that company doesn't
  OFFER         — pricing / bundling / trial structure gaps
  TONE          — emotional register mismatch
  CHANNEL       — platform presence gaps
  CREATIVE      — creative format and angle gaps
"""

import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Gap confidence thresholds
HIGH_CONFIDENCE   = 0.80
MEDIUM_CONFIDENCE = 0.55


class StrategyGapAnalyzer:
    """
    Deterministic rule-based gap analysis layer.
    Produces structured gap signals without LLM dependency.
    (Claude integration available as optional enhancement layer.)
    """

    # ── Main analysis entry point ─────────────────────────────────

    def analyze(self, company_id: str, competitor_profiles: List[Dict],
                 cluster_data: Dict[str, Any], pressure_signal: Dict[str, Any],
                 ad_list: List[Dict], page_texts: List[str]) -> Dict[str, Any]:
        """
        Full gap analysis pipeline.

        Returns:
          {
            "company_id": ...,
            "gap_signals": [...],
            "summary": {...},
            "generated_at": ...
          }
        """
        gaps: List[Dict] = []

        gaps.extend(self._positioning_gaps(cluster_data, page_texts, competitor_profiles))
        gaps.extend(self._offer_gaps(ad_list))
        gaps.extend(self._tone_gaps(ad_list))
        gaps.extend(self._content_theme_gaps(cluster_data, page_texts))
        gaps.extend(self._channel_gaps(ad_list))
        gaps.extend(self._creative_format_gaps(ad_list))

        # Enrich with pressure context
        for g in gaps:
            g["market_pressure_score"] = pressure_signal.get("pressure_score", 0)
            g["pressure_tier"]         = pressure_signal.get("pressure_tier", "UNKNOWN")

        # Sort by severity
        severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        gaps.sort(key=lambda g: severity_order.get(g["severity"], 3))

        summary = {
            "total_gaps":     len(gaps),
            "high_severity":  sum(1 for g in gaps if g["severity"] == "HIGH"),
            "medium_severity":sum(1 for g in gaps if g["severity"] == "MEDIUM"),
            "low_severity":   sum(1 for g in gaps if g["severity"] == "LOW"),
            "top_gap_type":   gaps[0]["gap_type"] if gaps else "NONE",
            "opportunity_flag": pressure_signal.get("unique_angle_opportunity", False),
            "dominant_competitor_theme": cluster_data.get("dominant_theme", "unknown"),
        }

        result = {
            "company_id":   company_id,
            "gap_signals":  gaps,
            "summary":      summary,
            "generated_at": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"Strategy gap analysis complete [{company_id}]: "
            f"{len(gaps)} gaps | HIGH={summary['high_severity']}"
        )
        return result

    # ── Gap detectors ─────────────────────────────────────────────

    def _positioning_gaps(self, cluster_data: Dict, page_texts: List[str],
                           profiles: List[Dict]) -> List[Dict]:
        gaps = []
        dominant = cluster_data.get("dominant_theme", "")
        saturation = cluster_data.get("saturation_index", 0.0)

        if saturation > 0.65:
            gaps.append(self._gap(
                gap_type="POSITIONING",
                severity="HIGH",
                description=(
                    f"Competitors have converged on '{dominant}' messaging with "
                    f"{saturation:.0%} saturation. Your positioning risk is high "
                    "if you use similar language."
                ),
                opportunity=(
                    "Differentiate with a contrarian or category-creating angle. "
                    "High saturation creates opening for a clearly distinct voice."
                ),
                confidence=HIGH_CONFIDENCE,
                data_source="similarity_cluster",
                payload={"dominant_theme": dominant, "saturation": saturation}
            ))
        elif saturation > 0.35:
            gaps.append(self._gap(
                gap_type="POSITIONING",
                severity="MEDIUM",
                description=f"Moderate messaging convergence detected around '{dominant}'.",
                opportunity="Monitor trend — consider pre-empting category before saturation increases.",
                confidence=MEDIUM_CONFIDENCE,
                data_source="similarity_cluster"
            ))

        return gaps

    def _offer_gaps(self, ad_list: List[Dict]) -> List[Dict]:
        gaps = []
        offer_types = [a.get("offer_type", "") for a in ad_list]
        offer_freq  = {}
        for o in offer_types:
            offer_freq[o] = offer_freq.get(o, 0) + 1

        dominant_offer = max(offer_freq, key=offer_freq.get) if offer_freq else None

        if dominant_offer == "trial":
            gaps.append(self._gap(
                gap_type="OFFER",
                severity="HIGH",
                description="Competitor ad library is dominated by free trial offers.",
                opportunity=(
                    "If you lack a trial, this is a conversion friction disadvantage. "
                    "Consider a time-limited trial or freemium entry point."
                ),
                confidence=0.85,
                data_source="ad_library",
                payload={"dominant_offer": dominant_offer, "distribution": offer_freq}
            ))
        elif dominant_offer == "discount":
            gaps.append(self._gap(
                gap_type="OFFER",
                severity="MEDIUM",
                description="Competitors are competing heavily on price/discount signals.",
                opportunity="Price-based competition erodes margins for all. Value-based positioning may outperform.",
                confidence=0.75,
                data_source="ad_library",
                payload={"dominant_offer": dominant_offer, "distribution": offer_freq}
            ))
        elif dominant_offer == "demo":
            gaps.append(self._gap(
                gap_type="OFFER",
                severity="LOW",
                description="Competitors are primarily offering demos — typically B2B enterprise play.",
                opportunity="If targeting mid-market, self-serve trial may outconvert demo gates.",
                confidence=MEDIUM_CONFIDENCE,
                data_source="ad_library"
            ))

        return gaps

    def _tone_gaps(self, ad_list: List[Dict]) -> List[Dict]:
        gaps = []
        tones = [a.get("emotional_tone", "") for a in ad_list if a.get("emotional_tone")]
        if not tones:
            return []

        tone_freq = {}
        for t in tones:
            tone_freq[t] = tone_freq.get(t, 0) + 1

        dominant_tone = max(tone_freq, key=tone_freq.get)
        share = tone_freq[dominant_tone] / len(tones)

        if share > 0.60:
            gaps.append(self._gap(
                gap_type="TONE",
                severity="MEDIUM",
                description=(
                    f"Competitor creative tone is predominantly '{dominant_tone}' "
                    f"({share:.0%} of ads)."
                ),
                opportunity=(
                    f"If your tone differs, you may stand out. "
                    f"If similar, ensure tone authenticity — forced '{dominant_tone}' tone gets no attention."
                ),
                confidence=0.70,
                data_source="ad_library",
                payload={"tone_distribution": tone_freq}
            ))

        return gaps

    def _content_theme_gaps(self, cluster_data: Dict, page_texts: List[str]) -> List[Dict]:
        gaps = []
        clusters = cluster_data.get("clusters", [])
        saturated_themes = [c["theme"] for c in clusters if c.get("is_saturated")]

        if saturated_themes:
            gaps.append(self._gap(
                gap_type="CONTENT",
                severity="MEDIUM",
                description=(
                    f"Content themes that are fully saturated across competitors: "
                    f"{', '.join(set(saturated_themes))}."
                ),
                opportunity=(
                    "Create content in adjacent but unsaturated categories. "
                    "Original research, contrarian takes, and niche use-cases cut through."
                ),
                confidence=0.72,
                data_source="crawl_cluster",
                payload={"saturated_themes": saturated_themes}
            ))

        # Check for enterprise/compliance content gap
        combined = " ".join(page_texts).lower()
        if "compliance" not in combined and "enterprise" not in combined:
            gaps.append(self._gap(
                gap_type="CONTENT",
                severity="LOW",
                description="No enterprise/compliance content detected in competitor pages.",
                opportunity="If targeting upmarket, compliance and security content builds trust with procurement teams.",
                confidence=0.55,
                data_source="crawl"
            ))

        return gaps

    def _channel_gaps(self, ad_list: List[Dict]) -> List[Dict]:
        gaps = []
        platforms = set(a.get("platform", "") for a in ad_list if a.get("platform"))
        all_platforms = {"meta", "google", "tiktok", "linkedin", "twitter", "reddit"}
        missing = all_platforms - platforms

        if "tiktok" in missing and len(ad_list) > 5:
            gaps.append(self._gap(
                gap_type="CHANNEL",
                severity="LOW",
                description="Competitors appear absent from TikTok Ads.",
                opportunity="First-mover advantage on TikTok for your category — CPMs typically lower with earlier entry.",
                confidence=0.60,
                data_source="ad_library",
                payload={"active_platforms": list(platforms), "absent": list(missing)}
            ))

        if "linkedin" in platforms and "linkedin" not in {a.get("platform") for a in ad_list}:
            gaps.append(self._gap(
                gap_type="CHANNEL",
                severity="MEDIUM",
                description="Competitor is running LinkedIn ads. B2B intent signal.",
                opportunity="If B2B is your target, LinkedIn presence gap is significant.",
                confidence=0.65,
                data_source="ad_library"
            ))

        return gaps

    def _creative_format_gaps(self, ad_list: List[Dict]) -> List[Dict]:
        gaps = []
        has_image = any(a.get("image_url") for a in ad_list)
        has_video = any("video" in str(a.get("body_text","")).lower() for a in ad_list)

        if not has_video:
            gaps.append(self._gap(
                gap_type="CREATIVE",
                severity="LOW",
                description="No video ad creatives detected in competitor library.",
                opportunity="Video ads typically outperform static by 20–30% CTR. Early video adoption is an advantage.",
                confidence=0.55,
                data_source="ad_library"
            ))

        return gaps

    # ── Gap factory ───────────────────────────────────────────────

    @staticmethod
    def _gap(gap_type: str, severity: str, description: str,
              opportunity: str = "", confidence: float = 0.5,
              data_source: str = "mixed", payload: Optional[Dict] = None) -> Dict:
        return {
            "gap_type":    gap_type,
            "severity":    severity,
            "description": description,
            "opportunity": opportunity,
            "confidence":  round(confidence, 3),
            "data_source": data_source,
            "payload":     payload or {},
            "generated_at": datetime.utcnow().isoformat()
        }

    # ── JSON export ───────────────────────────────────────────────

    @staticmethod
    def to_json(analysis_result: Dict) -> str:
        return json.dumps(analysis_result, indent=2, default=str)
