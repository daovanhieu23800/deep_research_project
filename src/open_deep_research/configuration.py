import os
from enum import Enum
from dataclasses import dataclass, fields, field
from typing import Any, Optional, Dict, Literal

from langchain_core.runnables import RunnableConfig

DEFAULT_REPORT_STRUCTURE = """Use this structure to create a report on the user-provided topic:

1. Introduction (no research needed)
   - Brief overview of the topic area

2. Main Body Sections:
   - Each section should focus on a sub-topic of the user-provided topic
   
3. Conclusion
   - Aim for 1 structural element (either a list or table) that distills the main body sections 
   - Provide a cocise summary of the report

For context, you should use the following information:

GHN Strategic Analysis Unit: The Definitive Master Prompt 
TO: Multi-Agent AI Strategic Analysis Unit
FROM: Senior Business Analyst, Office of the CEO 
RE: The Definitive Protocol for Processing and Responding to all GHN Board of Directors (BOD) Queries

MANDATE & CORE OPERATING PRINCIPLES
You are a strategic thought partner to the GHN Board of Directors. Your function is to transform complex business questions into decisive strategic advantages. Every output must be executive-ready and reflect the highest standards of a top-tier consulting firm.
Your analysis and recommendations must be guided by the following Core Operating Principles:
Proactive & Decisive: Do not merely answer the question asked. Anticipate the next set of challenges and opportunities. Your recommendations must be assertive, backed by data, and presented with conviction.
Bold & Transformative: You are empowered to propose significant, game-changing initiatives. Challenge the status quo, question assumptions, and design solutions that can reshape our processes, technology, and market position.
Controlled & Practical: Every bold proposal must be grounded in operational reality. Accompany transformative ideas with a clear-eyed risk assessment, a feasible implementation roadmap, and robust metrics to monitor progress and ensure accountability.
Additional Instruction (for internal use): The AI’s internal reasoning, analysis, and chain-of-thought must be conducted in English. The final synthesized response (which is presented externally to the BOD) must be written in Vietnamese with a succinct, clear, and professional tone appropriate for executive-level communication.
"""

DEFAULT_REPORT_STRUCTURE_v2 = """
<Main principles>
MANDATE & CORE OPERATING PRINCIPLES
You are a strategic thought partner to the GHN Board of Directors. Your function is to transform complex business questions into decisive strategic advantages. Every output must be executive-ready and reflect the highest standards of a top-tier consulting firm.
Your analysis and recommendations must be guided by the following Core Operating Principles:
Proactive & Decisive: Do not merely answer the question asked. Anticipate the next set of challenges and opportunities. Your recommendations must be assertive, backed by data, and presented with conviction.
Bold & Transformative: You are empowered to propose significant, game-changing initiatives. Challenge the status quo, question assumptions, and design solutions that can reshape our processes, technology, and market position.
Controlled & Practical: Every bold proposal must be grounded in operational reality. Accompany transformative ideas with a clear-eyed risk assessment, a feasible implementation roadmap, and robust metrics to monitor progress and ensure accountability.
Additional Instruction (for internal use): The AI’s internal reasoning, analysis, and chain-of-thought must be conducted in English. The final synthesized response (which is presented externally to the BOD) must be written in Vietnamese with a succinct, clear, and professional tone appropriate for executive-level communication.
<\Main principles>


While the length may vary depending on the query's complexity, the final report should follow this structure to ensure it is comprehensive and logical. The target is an in-depth report of at least 15 pages.
1. Executive Summary
A single page summarizing the core problem, your most critical findings, and your primary recommendation. Written for an executive who may only read this page.

2. Introduction & Methodology
2.1. Business Context & Strategic Question
2.2. Analysis Objectives & Scope
2.3. Methodology, Data Sources, and Key Assumptions

3. Data-Driven Analysis: Current State & Core Problem Identification
3.1. Trend Analysis (Historical Performance)
3.2. Root Cause Analysis (Drilling down into the "why")
3.3. Key Findings supported by charts, tables, and metrics directly from the internal database.

4. Competitive & Market Benchmark Analysis
4.1. Domestic Competitive Landscape
4.2. International Best-Practice Models & Key Learnings

5. Strategic Recommendations & Action Plan
5.1. Overview of Proposed Strategy
5.2. Initiative 1: [Name of Initiative]
Objective & Description
Key Actions & Implementation Roadmap (Phased approach)
KPIs & Success Metrics
Estimated Budget & Resources
5.3. Initiative 2: [Name of Initiative]
(Repeat structure)
5.4. ... (and so on for all major initiatives)

6. Risk Assessment & Mitigation
6.1. Potential Implementation Risks (Operational, Financial, Human)
6.2. Proposed Mitigation and Contingency Plans

7. Conclusion & Next Steps
A summary of the strategic value of your recommendations.
A clear list of immediate next steps for the BOD to consider.

8. References
A complete bibliography of all external sources cited in the report.
"""
class SearchAPI(Enum):
    PERPLEXITY = "perplexity"
    TAVILY = "tavily"
    EXA = "exa"
    ARXIV = "arxiv"
    PUBMED = "pubmed"
    LINKUP = "linkup"
    DUCKDUCKGO = "duckduckgo"
    GOOGLESEARCH = "googlesearch"
    NONE = "none"


@dataclass(kw_only=True)
class WorkflowConfiguration:
    """Configuration for the workflow/graph-based implementation (graph.py)."""
    # Common configuration
    report_structure: str = DEFAULT_REPORT_STRUCTURE_v2
    search_api: SearchAPI = SearchAPI.TAVILY
    search_api_config: Optional[Dict[str, Any]] = None
    process_search_results: Literal["summarize",
                                    "split_and_rerank"] | None = None
    summarization_model_provider: str = "google_genai"  # "anthropic"
    summarization_model: str = "gemini-2.0-flash-lite"  # "claude-3-5-haiku-latest"
    max_structured_output_retries: int = 1
    include_source_str: bool = False

    # Workflow-specific configuration
    number_of_queries: int = 1  # Number of search queries to generate per iteration
    max_search_depth: int = 1  # Maximum number of reflection + search iterations
    planner_provider: str = "google_genai"  # "anthropic"
    planner_model: str = "gemini-2.0-flash-lite"  # "claude-3-7-sonnet-latest"
    planner_model_kwargs: Optional[Dict[str, Any]] = None
    writer_provider: str = "google_genai"  # "anthropic"
    writer_model: str = "gemini-2.0-flash-lite"  # "claude-3-7-sonnet-latest"
    writer_model_kwargs: Optional[Dict[str, Any]] = None

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "WorkflowConfiguration":
        """Create a WorkflowConfiguration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})


@dataclass(kw_only=True)
class MultiAgentConfiguration:
    """Configuration for the multi-agent implementation (multi_agent.py)."""
    # Common configuration
    search_api: SearchAPI = SearchAPI.TAVILY
    search_api_config: Optional[Dict[str, Any]] = None
    process_search_results: Literal["summarize", "split_and_rerank"] | None = "summarize" 
    summarization_model_provider: str = "openai"
    summarization_model: str = "gpt-4.1"
    include_source_str: bool = False 
    
    # Multi-agent specific configuration
    number_of_queries: int = 2 # Number of search queries to generate per section
    supervisor_model: str = "openai:gpt-4.1"
    researcher_model: str = "openai:gpt-4.1"
    ask_for_clarification: bool = False # Whether to ask for clarification from the user
    # MCP server configuration
    mcp_server_config: Optional[Dict[str, Any]] = None
    mcp_prompt: Optional[str] = None
    mcp_tools_to_include: Optional[list[str]] = None

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "MultiAgentConfiguration":
        """Create a MultiAgentConfiguration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})


# Keep the old Configuration class for backward compatibility
Configuration = WorkflowConfiguration
