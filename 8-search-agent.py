import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig
from langchain_community.tools.ddg_search import DuckDuckGoSearchRun
from dotenv import load_dotenv
import uuid

@dataclass
class AgentConfig:
    """Configuration for the search agent."""
    model_name: str = "gpt-4o-mini"
    thread_id: str = str(uuid.uuid4())
    num_verification_searches: int = 2
    max_search_results: int = 5

    def __post_init__(self):
        """Validates the configuration after initialization."""
        if not self.thread_id:
            # Ensure we always have a unique thread_id even if None was provided
            self.thread_id = str(uuid.uuid4())

class SearchAgent:
    """A ReAct agent with verification capabilities."""
    
    AGENT_PROMPT = """You are a helpful assistant with access to a search tool. Follow these steps when responding to queries:

1. Initial Search: Use the search tool to find relevant information about the query.
2. Verification: Perform at least one additional search with different keywords to verify the information from multiple sources.
3. Cross-reference: Compare the information from different searches to ensure consistency.
4. Response: Provide a comprehensive answer that:
   - Synthesizes information from multiple sources
   - Highlights any discrepancies found
   - Indicates the level of confidence in the information
   - Cites sources when possible

Always be transparent about your search process and explain how you verified the information."""

    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the search agent with configuration."""
        self.config = config or AgentConfig()
        self._initialize_environment()
        self.checkpointer = InMemorySaver()
        self.search_tool = DuckDuckGoSearchRun()
        self.agent = self._create_agent()
        self.runnable_config = self._create_runnable_config()

    def _initialize_environment(self) -> None:
        """Initialize environment variables and configurations."""
        load_dotenv()
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") or ""

    def _create_agent(self):
        """Create and configure the ReAct agent."""
        return create_react_agent(
            model=self.config.model_name,
            prompt=self.AGENT_PROMPT,
            name="SearchAgent",
            tools=[self.search_tool],
            checkpointer=self.checkpointer,
        )

    def _create_runnable_config(self) -> RunnableConfig:
        """Create the runnable configuration for the agent."""
        return {"configurable": {"thread_id": self.config.thread_id}}

    def search_and_verify(self, query: str) -> Dict[str, Any]:
        try:
            messages = [{"role": "user", "content": query}]
            response = self.agent.invoke({"messages": messages}, self.runnable_config)
            return response
        except Exception as e:
            print(f"Error during search and verify: {str(e)}")
            return {"error": str(e)}

def main():
    agent = SearchAgent()
    
    queries = [
        "What are the health benefits and risks of intermittent fasting?",
        "What are the latest developments in quantum computing?",
    ]
    
    for query in queries:
        print(f"\nProcessing Query: {query}")
        response = agent.search_and_verify(query)
        
        if "error" in response:
            print(f"Error: {response['error']}")
        else:
            print("\nVerified Response:")
            print(response)
        print("-" * 80)

if __name__ == "__main__":
    main()
