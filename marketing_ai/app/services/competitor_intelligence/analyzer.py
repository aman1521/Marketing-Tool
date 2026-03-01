import anthropic
from app.config import settings
from typing import List, Dict

class CompetitorAnalyzer:
    """
    Claude hook - "Automate + MCP Orchestration Brain".
    Consumes enormous Qdrant context windows holding Competitor Data across entire funnels (Pricing, Blogs, Features).
    Uses Claude to perform a Strategic Gap Analysis against the User Company.
    """
    def __init__(self):
         self.claude_client = anthropic.AsyncAnthropic(api_key=settings.CLAUDE_API_KEY)

    async def generate_gap_report(self, company_name: str, competitor_context: List[str]) -> str:
        """
        Claude receives Qdrant Payload Text chunks strings and determines strategic positioning differences.
        """
        if not competitor_context:
            return "Insufficient competitor data extracted for gap report."

        # Truncate context if unreasonably large to save API cost (~8,000 words here is safe)
        massive_context_payload = "\n---\n".join(competitor_context)[:50000]

        system_instruction = f"""
        You are the Chief Intelligence Analyst for '{company_name}'.
        You have been presented with scraped, chunked vector database dumps of a direct competitor.
        
        Analyze the specific details from the competitor content below and produce a Strategic Gap Report.
        Determine:
        1. Positioning Gap (How do they frame themselves vs us?)
        2. Content Theme Gap (What problems are they targeting that we aren't?)
        3. Offer Differentiation Map (Bundling, SaaS pricing structures).
        4. Emotional Tone Comparison (Are they aggressive, educational, premium?)
        
        Write it as an internal executive brief in Markdown format. Keep it sharp and analytical.
        """

        try:
            # Using Haiku or Sonnet given large context capacity over pure Speed
            response = await self.claude_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2048,
                system=system_instruction,
                messages=[
                    {"role": "user", "content": f"Competitor Data Excerpt:\n\n{massive_context_payload}"}
                ]
            )
            return response.content[0].text
            
        except Exception as e:
            return f"Claude analysis failed during orchestration: {str(e)}"
