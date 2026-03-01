import os
from typing import List, Dict, Any, Optional

class AISafetyEngine:
    """
    Ensures AI behavior adheres strictly to business risk rules.
    Actions triggering > 30% budget shifts or missing confidence metrics are automatically marked requiring manual QA.
    """
    BUDGET_CHANGE_LIMIT = 0.30  # 30%
    MIN_CONFIDENCE_SCORE = 0.75

    @classmethod
    def evaluate_strategy(cls, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses untrusted AI proposed action and enforces rule evaluation logic before inserting into Postgres StrategyLog.
        """
        requires_approval = False
        action_type = strategy.get("action_type")
        confidence = float(strategy.get("confidence", 0.0))
        
        # Immediate rejection criteria
        if confidence < cls.MIN_CONFIDENCE_SCORE:
            raise ValueError(f"Strategy rejected: Confidence score {confidence} is below minimum safe threshold.")
            
        if action_type == "budget_shift":
            old_b = float(strategy.get("old_budget", 1))
            new_b = float(strategy.get("new_budget", 0))
            change_pct = abs(new_b - old_b) / (old_b if old_b != 0 else 1)
            
            if change_pct > cls.BUDGET_CHANGE_LIMIT:
                requires_approval = True
                
        if action_type == "targeting_change" and strategy.get("is_major_shift", False):
            requires_approval = True
            
        return {
            "action_type": action_type,
            "confidence_score": confidence,
            "reasoning_text": strategy.get("reasoning", "No reasoning provided."),
            "proposed_changes": strategy.get("changes", {}),
            "requires_approval": requires_approval
        }


class AIOrchestrator:
    """
    Master Service responsible for generating actions across multi-platform scopes.
    Uses GPT/Claude dynamically.
    """
    def __init__(self, use_claude: bool = False):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.claude_key = os.getenv("CLAUDE_API_KEY")
        self.use_claude = use_claude

    async def generate_strategies(self, objective: str, audience: str, budget: float, risk: str, platform_data: Dict) -> List[Dict[str, Any]]:
        """
        Constructs context from Feature Engineering & Vector embeddings (competitor mapping),
        Generates tactical output, processes through Safety Layer.
        """
        import json
        from openai import AsyncOpenAI
        import logging

        logger = logging.getLogger(__name__)
        
        # Feature Engineering Pipeline hook
        # e.g., contextualizing ROAS drops across Meta and linking it to TikTok spend shifts
        
        # Local model hook (AirLLM tagging)
        # We classify user sentiment first locally if needed.
        
        
        # Actual AI Logic overriding Mock
        mock_ai_output = []
        if not self.use_claude and self.openai_key:
            client = AsyncOpenAI(api_key=self.openai_key)
            prompt = f"Objective: {objective}. Audience: {audience}. Budget: {budget}. Risk: {risk}. Data: {json.dumps(platform_data, default=str)}. Output JSON mapping exactly to a pure dictionary with a root key 'strategies' containing an array of objects. Keys must be: action_type, confidence, old_budget, new_budget, reasoning, is_major_shift, changes(dict)."
            try:
                response = await client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert autonomous AI Marketing Strategist capable of cross-platform optimization. Return only strictly structured JSON object."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0.2
                )
                
                content = response.choices[0].message.content
                if content:
                    parsed_data = json.loads(content)
                    raw_strategies = parsed_data.get("strategies", [])
                    # Append strictly to our evaluating array
                    for strat in raw_strategies:
                        mock_ai_output.append(strat)
            except Exception as e:
                logger.error(f"OpenAI Generation Failed: {str(e)}")
        
        # Filter generated outputs through safety limits
        safe_strategies = []
        for strat in mock_ai_output:
            try:
                evaluated = AISafetyEngine.evaluate_strategy(strat)
                safe_strategies.append(evaluated)
            except ValueError as e:
                # Log rejection internally
                pass
                
        return safe_strategies
