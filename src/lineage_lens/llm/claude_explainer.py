"""
Claude API integration for generating lineage explanations
Supports both standard Anthropic API and Rakuten Open API
"""

import os
import requests
from typing import Optional, List
from anthropic import Anthropic
from ..models.lineage_models import LineageGraph, LineageQuery, LineageExplanation


class ClaudeLineageExplainer:
    """Generate natural language explanations of data lineage using Claude"""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 model_name: Optional[str] = None,
                 temperature: Optional[float] = None):
        """Initialize the Claude Lineage Explainer.
        
        Args:
            api_key: API key or Bearer token
            base_url: Custom base URL for the API (for Rakuten Open API)
            model_name: The Claude model to use
            temperature: Temperature for response generation
        """
        # Try to get values from config first, then environment, then parameters
        try:
            from ..utils.config import settings
            self.api_key = api_key or settings.anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
            self.base_url = base_url or settings.anthropic_base_url or os.getenv('ANTHROPIC_BASE_URL')
            self.model_name = model_name or settings.claude_model or os.getenv('CLAUDE_MODEL', 'claude-3-haiku-20240307')
            self.temperature = temperature or settings.claude_temperature or float(os.getenv('CLAUDE_TEMPERATURE', '0.7'))
        except ImportError:
            # Fallback to environment variables if config import fails
            self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
            self.base_url = base_url or os.getenv('ANTHROPIC_BASE_URL')
            self.model_name = model_name or os.getenv('CLAUDE_MODEL', 'claude-3-haiku-20240307')
            self.temperature = temperature or float(os.getenv('CLAUDE_TEMPERATURE', '0.7'))
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided or set as environment variable")
        
        # Detect if using Rakuten Open API
        self.is_rakuten_api = self.base_url and "rakuten-it.com" in self.base_url
        
        if self.is_rakuten_api:
            # For Rakuten API, we'll use direct HTTP requests with Bearer token
            self.client = None
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        else:
            # Standard Anthropic API
            self.client = Anthropic(api_key=self.api_key)
            self.headers = None
            
        self.max_tokens = 1000
    
    def explain_lineage(self, lineage_graph: LineageGraph, query: LineageQuery) -> LineageExplanation:
        """Generate explanation for a lineage query"""
        context = self._build_context(lineage_graph, query.table_focus)
        prompt = self._build_prompt(context, query.query_text)
        
        try:
            # Call appropriate API based on provider
            if self.is_rakuten_api:
                explanation_text = self._call_rakuten_api(prompt)
            else:
                explanation_text = self._call_anthropic_api(prompt)
            
            affected_tables = self._extract_mentioned_tables(explanation_text, lineage_graph)
            
            return LineageExplanation(
                explanation=explanation_text,
                affected_tables=affected_tables,
                confidence_score=0.85  # Static confidence for demo
            )
            
        except Exception as e:
            return LineageExplanation(
                explanation=f"Error generating explanation: {str(e)}",
                affected_tables=[],
                confidence_score=0.0
            )
    
    def _call_anthropic_api(self, prompt: str) -> str:
        """Call standard Anthropic API"""
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response.content[0].text
    
    def _call_rakuten_api(self, prompt: str) -> str:
        """Call Rakuten Open API with Bearer token authentication"""
        
        # Try both authentication methods for Rakuten API
        headers_bearer = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        headers_api_key = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        # Use the correct endpoint for Rakuten API
        endpoint = f"{self.base_url.rstrip('/')}/v1/chat/completions"
        headers = headers_bearer  # Rakuten uses Bearer token
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # Handle OpenAI-style response format (which Rakuten uses)
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                elif "content" in result and len(result["content"]) > 0:
                    return result["content"][0]["text"]
                else:
                    return str(result)
            else:
                raise Exception(f"Rakuten API error: Status {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            raise Exception(f"Rakuten API error: {str(e)}")
    
    def _build_context(self, lineage_graph: LineageGraph, focus_table: Optional[str] = None) -> str:
        """Build context string from lineage graph"""
        context_parts = []
        
        # Add summary
        context_parts.append(f"Data Lineage Analysis:")
        context_parts.append(f"- Total tables: {len(lineage_graph.tables)}")
        context_parts.append(f"- Source tables: {len(lineage_graph.source_tables)}")
        context_parts.append(f"- Target tables: {len(lineage_graph.target_tables)}")
        context_parts.append("")
        
        # Add detailed table information
        context_parts.append("Table Dependencies:")
        for table_name, table_info in lineage_graph.tables.items():
            upstream = ", ".join(table_info.upstream_tables) if table_info.upstream_tables else "None"
            downstream = ", ".join(table_info.downstream_tables) if table_info.downstream_tables else "None"
            
            context_parts.append(f"• {table_name} ({table_info.table_type.value})")
            context_parts.append(f"  - Upstream: {upstream}")
            context_parts.append(f"  - Downstream: {downstream}")
            
            if table_info.columns:
                columns = ", ".join([col.column_name for col in table_info.columns[:5]])  # First 5 columns
                if len(table_info.columns) > 5:
                    columns += f" (and {len(table_info.columns) - 5} more)"
                context_parts.append(f"  - Columns: {columns}")
            
            context_parts.append("")
        
        # Add focus table SQL if available
        if focus_table and focus_table in lineage_graph.tables:
            table_info = lineage_graph.tables[focus_table]
            if table_info.sql_query:
                context_parts.append(f"SQL for {focus_table}:")
                context_parts.append(f"```sql")
                context_parts.append(table_info.sql_query)
                context_parts.append("```")
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, context: str, query_text: str) -> str:
        """Build the complete prompt for Claude"""
        prompt = f"""You are a data lineage expert helping users understand data flows and dependencies. 

Based on the following data lineage information, please answer the user's question in a clear, concise manner.

{context}

User Question: {query_text}

Please provide a helpful explanation that:
1. Directly answers the user's question
2. Explains the relevant data flow and dependencies
3. Uses business-friendly language (avoid technical jargon)
4. Mentions specific table names when relevant
5. Highlights any important data transformation patterns

Keep your response focused and under 200 words unless more detail is specifically requested."""

        return prompt
    
    def _extract_mentioned_tables(self, explanation: str, lineage_graph: LineageGraph) -> List[str]:
        """Extract table names mentioned in the explanation"""
        mentioned_tables = []
        explanation_lower = explanation.lower()
        
        for table_name in lineage_graph.tables.keys():
            if table_name.lower() in explanation_lower:
                mentioned_tables.append(table_name)
        
        return mentioned_tables
    
    def generate_summary_explanation(self, lineage_graph: LineageGraph) -> str:
        """Generate a high-level summary of the entire lineage"""
        if not lineage_graph.tables:
            return "No data lineage information available."
        
        summary_query = LineageQuery(
            query_text="Please provide a high-level summary of this data pipeline, including the main data flow from sources to targets.",
            query_type="summary"
        )
        
        explanation = self.explain_lineage(lineage_graph, summary_query)
        return explanation.explanation
    
    def suggest_questions(self, lineage_graph: LineageGraph) -> List[str]:
        """Suggest relevant questions users might ask about the lineage"""
        suggestions = []
        
        # Generic suggestions
        suggestions.extend([
            "How does data flow through this pipeline?",
            "What are the main data sources?",
            "Which tables depend on each other?"
        ])
        
        # Table-specific suggestions
        for table_name in list(lineage_graph.target_tables)[:3]:  # First 3 target tables
            suggestions.append(f"Where does data in {table_name} come from?")
        
        for table_name in list(lineage_graph.source_tables)[:3]:  # First 3 source tables
            suggestions.append(f"What uses data from {table_name}?")
        
        return suggestions[:6]  # Return max 6 suggestions
