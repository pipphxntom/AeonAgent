from typing import Dict, Any, List, Optional
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import Graph, StateGraph, END
from dataclasses import dataclass
import json
import time
import logging

from core.config import settings
from services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


@dataclass
class AgentState:
    """State for agent execution."""
    query: str
    context: List[str]
    response: str
    metadata: Dict[str, Any]
    error: Optional[str] = None


class AgentOrchestrator:
    """LangGraph-based agent orchestration service."""
    
    def __init__(self, agent_config: Dict[str, Any]):
        self.config = agent_config
        self.llm = ChatOpenAI(
            model=agent_config.get("model", "gpt-3.5-turbo"),
            temperature=agent_config.get("temperature", 0.7),
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.vector_store = VectorStoreService()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the agent execution graph."""
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("retrieve", self._retrieve_context)
        graph.add_node("generate", self._generate_response)
        graph.add_node("postprocess", self._postprocess_response)
        
        # Add edges
        graph.add_edge("retrieve", "generate")
        graph.add_edge("generate", "postprocess")
        graph.add_edge("postprocess", END)
        
        # Set entry point
        graph.set_entry_point("retrieve")
        
        return graph.compile()
    
    async def _retrieve_context(self, state: AgentState) -> AgentState:
        """Retrieve relevant context for the query."""
        try:
            collection_name = self.config.get("collection_name")
            if not collection_name:
                logger.warning("No collection name configured for retrieval")
                return state
            
            # Search for relevant documents
            results = await self.vector_store.search_documents(
                collection_name=collection_name,
                query=state.query,
                top_k=self.config.get("top_k", 5)
            )
            
            # Extract context text
            context = [result["text"] for result in results]
            
            # Update state
            state.context = context
            state.metadata["retrieval_results"] = len(results)
            state.metadata["top_scores"] = [r["score"] for r in results[:3]]
            
            logger.info(f"Retrieved {len(context)} context chunks")
            return state
            
        except Exception as e:
            logger.error(f"Error in retrieve_context: {e}")
            state.error = f"Retrieval error: {str(e)}"
            return state
    
    async def _generate_response(self, state: AgentState) -> AgentState:
        """Generate response using LLM."""
        try:
            # Build prompt
            system_prompt = self.config.get("system_prompt", 
                "You are a helpful AI assistant. Use the provided context to answer questions accurately.")
            
            context_text = "\n\n".join(state.context) if state.context else "No relevant context found."
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", f"Context:\n{context_text}\n\nQuestion: {state.query}")
            ])
            
            # Generate response
            start_time = time.time()
            messages = prompt.format_messages()
            response = await self.llm.agenerate([messages])
            
            # Extract response text
            response_text = response.generations[0][0].text
            
            # Update state
            state.response = response_text
            state.metadata["generation_time_ms"] = int((time.time() - start_time) * 1000)
            state.metadata["model"] = self.config.get("model", "gpt-3.5-turbo")
            
            logger.info("Generated response successfully")
            return state
            
        except Exception as e:
            logger.error(f"Error in generate_response: {e}")
            state.error = f"Generation error: {str(e)}"
            return state
    
    async def _postprocess_response(self, state: AgentState) -> AgentState:
        """Postprocess the response (sanitization, formatting, etc.)."""
        try:
            if state.error:
                return state
            
            # Basic sanitization (can be extended)
            response = state.response.strip()
            
            # Add any postprocessing logic here
            # - PII redaction
            # - Format improvement
            # - Fact checking
            
            state.response = response
            state.metadata["postprocessed"] = True
            
            logger.info("Postprocessed response successfully")
            return state
            
        except Exception as e:
            logger.error(f"Error in postprocess_response: {e}")
            state.error = f"Postprocessing error: {str(e)}"
            return state
    
    async def execute(self, query: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the agent workflow."""
        try:
            # Initialize state
            initial_state = AgentState(
                query=query,
                context=[],
                response="",
                metadata=metadata or {}
            )
            
            # Execute graph
            start_time = time.time()
            final_state = await self.graph.ainvoke(initial_state)
            total_time = int((time.time() - start_time) * 1000)
            
            # Return results
            return {
                "response": final_state.response,
                "context_used": len(final_state.context),
                "execution_time_ms": total_time,
                "metadata": final_state.metadata,
                "error": final_state.error,
                "success": final_state.error is None
            }
            
        except Exception as e:
            logger.error(f"Error executing agent: {e}")
            return {
                "response": "I apologize, but I encountered an error processing your request.",
                "context_used": 0,
                "execution_time_ms": 0,
                "metadata": {},
                "error": str(e),
                "success": False
            }


class AgentFactory:
    """Factory for creating agent instances."""
    
    @staticmethod
    def create_agent(agent_type: str, config: Dict[str, Any]) -> AgentOrchestrator:
        """Create an agent instance based on type and configuration."""
        
        # Default configurations for different agent types
        default_configs = {
            "hr_assistant": {
                "system_prompt": """You are an HR assistant AI. Help with HR-related questions using the provided context.
                Focus on being helpful, accurate, and compliant with employment laws.
                If you're unsure about something, recommend consulting with HR professionals.""",
                "model": "gpt-3.5-turbo",
                "temperature": 0.3,
                "top_k": 5
            },
            "sales_ops": {
                "system_prompt": """You are a Sales Operations AI assistant. Help with sales processes, 
                lead management, pipeline analysis, and sales strategy using the provided context.
                Be data-driven and focus on actionable insights.""",
                "model": "gpt-4",
                "temperature": 0.4,
                "top_k": 7
            },
            "legal": {
                "system_prompt": """You are a Legal AI assistant. Provide guidance on legal matters 
                using the provided context. Always remind users that this is not legal advice 
                and they should consult with qualified attorneys for specific legal matters.""",
                "model": "gpt-4",
                "temperature": 0.1,
                "top_k": 8
            }
        }
        
        # Merge default config with provided config
        base_config = default_configs.get(agent_type, default_configs["hr_assistant"])
        merged_config = {**base_config, **config}
        
        return AgentOrchestrator(merged_config)
