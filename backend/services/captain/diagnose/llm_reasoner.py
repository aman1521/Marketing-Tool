from typing import Dict, Any

class LLMReasoner:
    """
    LAYER 5: LLM Reasoning Layer
    Provides narrative summarization and strategy contextualization strictly 
    based on the preceding deterministic outcomes. It CANNOT override the diagnosis.
    """
    
    def __init__(self, provider: str = "openai"):
        self.provider = provider
        
    async def generate_explanation(self, diagnosis_context: Dict[str, Any]) -> Dict[str, str]:
        """
        Constructs a prompt locking the deterministic variables as ground truth, 
        forcing the LLM to output a structured strategy narrative around them.
        """
        account_state = diagnosis_context.get("account_state", "UNKNOWN")
        risk_level = diagnosis_context.get("risk_level", "UNKNOWN")
        confidence = diagnosis_context.get("confidence_score", 0.0)
        
        # In production this calls OpenAI / Anthropic
        # We mock the parsed outcome for structural integrity
        
        if account_state == "CONVERSION_PROBLEM":
            primary = "Optimize landing page Funnel."
            secondary = "Check cart abandonment sequences."
            explanation = "Traffic volume is stable relative to industry benchmarks, but conversions are stalling heavily post-click, flagging high funnel friction."
            strategy = "Pause underperforming bottom-funnel creatives; request immediate Hawkeye Funnel CRO review."
        
        elif account_state == "SCALING_OPPORTUNITY":
            primary = "Increase budget limits systematically."
            secondary = "Duplicate winning adsets."
            explanation = f"Account demonstrates high stability and beats ROAS benchmarks organically. Confidence is {confidence*100}%."
            strategy = "Execute a +15% daily budget scale via CaptainExecute logic safely."
            
        else:
            primary = "Maintain targeting limits."
            secondary = "Refresh creative libraries."
            explanation = f"Ad account exhibits mixed signals. The primary diagnostic reads {account_state}."
            strategy = "Hold spend velocity until stability index increases beyond current baseline."
        
        return {
            "primary_focus": primary,
            "secondary_focus": secondary,
            "strategic_direction": strategy,
            "explanation": explanation
        }
