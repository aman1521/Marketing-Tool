import openai
import anthropic
from typing import Dict, Any, List
from app.config import settings

class AIReasoningLayer:
    """
    OpenAI: used for strategy generation, deep reasoning, and campaign planning.
    Claude: used for tool orchestration, structured output enforcement, and long context competitor reports.
    """
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.claude_client = anthropic.AsyncAnthropic(api_key=settings.CLAUDE_API_KEY)

    async def generate_strategy(self, company_business_context: Dict[str, Any], historical_performance_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Produce structured JSON output using OpenAI.
        """
        # For production use, we'd enforce JSON schema using `response_format={"type": "json_object"}`
        system_prompt = """
        You are a Senior Paid Strategies Expert. Review this weekly behavior profile and company product context.
        Output MUST be pure JSON outlining:
        - "strategy_summary" (str): Why performance dropped or increased
        - "proposed_actions" (list of objects): [{'type': 'budget_increase|budget_decrease|campaign_pause', 'value': 0.15, 'confidence_score': 0.85, 'justification': 'ROAS is up 12% across 90 days.' }]
        - "overall_confidence" (0.00 to 1.00 float).
        """
        user_prompt = f"Context: {company_business_context}\nPerformance: {historical_performance_json}"
        
        try:
            # Live completion using the real API Key
            import json
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",  # Best for fast JSON structuring
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)

        except Exception as e:
            raise Exception(f"OpenAI reasoning failed: {str(e)}")

    async def orchestrate_claude_competitor_analysis(self, internal_qdrant_embeddings, competitor_qdrant_embeddings) -> Dict[str, Any]:
        """
        Claude hook. Best suited for 200K+ context window parsing and comparison.
        Pass the raw textual results retrieved from Qdrant vectors directly to Claude for strategic gap analysis.
        """
        try:
             # System prompt designed for Claude: "You are identifying gaps in positioning..."
             pass
        except Exception as e:
            raise Exception(f"Claude orchestration failed: {str(e)}")
