from typing import List, Annotated, TypedDict, Literal, cast
from pydantic import BaseModel, Field
import operator
import warnings
import re 

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool, BaseTool
from langchain_core.runnables import RunnableConfig
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import MessagesState

from langgraph.types import Command, Send
from langgraph.graph import START, END, StateGraph

from open_deep_research.configuration import MultiAgentConfiguration
from open_deep_research.utils import (
    get_config_value,
    tavily_search,
    duckduckgo_search,
    get_today_str,
)

from open_deep_research.prompts import SUPERVISOR_INSTRUCTIONS, RESEARCH_INSTRUCTIONS


## Tools factory - will be initialized based on configuration
def get_search_tool(config: RunnableConfig):
    """Get the appropriate search tool based on configuration"""
    configurable = MultiAgentConfiguration.from_runnable_config(config)
    search_api = get_config_value(configurable.search_api)

    # Return None if no search tool is requested
    if search_api.lower() == "none":
        return None

    # TODO: Configure other search functions as tools
    if search_api.lower() == "tavily":
        search_tool = tavily_search
    elif search_api.lower() == "duckduckgo":
        search_tool = duckduckgo_search
    else:
        raise NotImplementedError(
            f"The search API '{search_api}' is not yet supported in the multi-agent implementation. "
            f"Currently, only Tavily/DuckDuckGo/None is supported. Please use the graph-based implementation in "
            f"src/open_deep_research/graph.py for other search APIs, or set search_api to 'tavily', 'duckduckgo', or 'none'."
        )

    tool_metadata = {**(search_tool.metadata or {}), "type": "search"}
    search_tool.metadata = tool_metadata
    return search_tool


class ProblemStatement(BaseModel):
    """A single, well-defined business problem, framed for a board-level audience."""
    title: str = Field(description="A short, punchy, and impactful title for the core problem (e.g., 'Direct Financial Drain from High Turnover').")
    description: str = Field(description="A 1-2 sentence description that quantifies the problem's impact on the business. MUST use financial metrics ($), percentages (%), or direct impact on strategic goals. Use strategic placeholders like '[Estimated $X Million]' or '[~Y% below benchmark]' if exact data is not yet available.")

class CoreProblem(BaseModel):
    """Diagnoses the user's query to identify 3-4 core business problems for a Board of Directors."""
    problems: List[ProblemStatement] = Field(description="A list of core business problems identified from the user's query, each structured with a title and a quantified description.")

class FramedSection(BaseModel):
    """A blueprint for a single section of the board report. It serves as a detailed brief for a researcher agent."""
    name: str = Field(description="The full, formal name for this section of the report, including numbering (e.g., 'I. Executive Summary', 'IV. Root Cause Analysis').")
    key_questions_to_answer: List[str] = Field(description="A list of specific, critical questions this section must answer to fulfill its purpose. (e.g., 'How does our turnover rate compare to our top 3 competitors?').")
    writing_style_hint: str = Field(description="A concise directive to the researcher on the required tone and format. Examples: 'Data-Summary & Analytical. Use markdown tables for KPIs.', 'Prescriptive & Action-Oriented. Group solutions into phases.'")
    subsections: List[str] = Field(description="A list of required subsections that must be included within the main section content.")

class Sections(BaseModel):
    """Defines the complete structure of the Board of Directors report based on the diagnosed core problems. The structure MUST follow the standard Board-Ready Template."""
    report_structure: List[FramedSection] = Field(description="A list of all sections that will make up the report, each framed as a detailed brief for a researcher.")

class Question(BaseModel):
    """Asks one strategic follow-up question to the user to clarify the report's scope, objective, or competing priorities before analysis begins."""
    question: str = Field(description="A single, focused question to clarify the strategic intent. Example: 'To frame this analysis, should we prioritize reducing direct costs, improving operational stability, or enhancing our long-term employer brand?'")

# --- Tools for the Researcher Agent ---

class Section(FramedSection):
    """The final, written content for a single section of the report, ready for assembly. This is the output of a researcher agent."""
    content: str = Field(description="The fully written content for the section. MUST be in Markdown format, start with the section title as an H2 (e.g., '## IV. Root Cause Analysis'), be a maximum of 800 words, and MUST conclude with a '### Sources' H3 subsection followed by a numbered list of URL sources.")

class FinishResearch(BaseModel):
    """Signals that the research and writing for a specific section are complete."""
    pass

# --- Tools for State Management / Final Assembly ---

class AssembleReport(BaseModel):
    """Signals that all sections are complete and the report is ready to be compiled into a final document."""
    pass

class FinishReport(BaseModel):
    """Signals that the entire report-writing process is complete."""
    pass

## State
class ReportStateOutput(MessagesState):
    final_report: str  # Final report
    # for evaluation purposes only
    # this is included only if configurable.include_source_str is True
    source_str: str  # String of formatted source content from web search


class ReportState(MessagesState):
    framed_sections: Annotated[
        list[FramedSection], operator.add
    ]  # List of framed sections
    completed_sections: Annotated[list[Section], operator.add]  # Send() API key
    final_report: str  # Final report
    # for evaluation purposes only
    # this is included only if configurable.include_source_str is True
    source_str: Annotated[
        str, operator.add
    ]  # String of formatted source content from web search


class SectionState(MessagesState):
    framed_section: FramedSection  # Framed section to be researched
    completed_sections: list[
        Section
    ]  # Final key we duplicate in outer state for Send() API
    # for evaluation purposes only
    # this is included only if configurable.include_source_str is True
    source_str: str  # String of formatted source content from web search


class SectionOutputState(TypedDict):
    completed_sections: list[
        Section
    ]  # Final key we duplicate in outer state for Send() API
    # for evaluation purposes only
    # this is included only if configurable.include_source_str is True
    source_str: str  # String of formatted source content from web search


async def _load_mcp_tools(
    config: RunnableConfig,
    existing_tool_names: set[str],
) -> list[BaseTool]:
    configurable = MultiAgentConfiguration.from_runnable_config(config)
    if not configurable.mcp_server_config:
        return []

    mcp_server_config = configurable.mcp_server_config
    client = MultiServerMCPClient(mcp_server_config)
    mcp_tools = await client.get_tools()
    filtered_mcp_tools: list[BaseTool] = []
    for tool in mcp_tools:
        # TODO: this will likely be hard to manage
        # on a remote server that's not controlled by the developer
        # best solution here is allowing tool name prefixes in MultiServerMCPClient
        if tool.name in existing_tool_names:
            warnings.warn(
                f"Trying to add MCP tool with a name {tool.name} that is already in use - this tool will be ignored."
            )
            continue

        if (
            configurable.mcp_tools_to_include
            and tool.name not in configurable.mcp_tools_to_include
        ):
            continue

        filtered_mcp_tools.append(tool)

    return filtered_mcp_tools

async def get_supervisor_tools(config: RunnableConfig) -> list[BaseTool]:
    """Get supervisor tools based on configuration, using the new strategic tool schemas."""
    configurable = MultiAgentConfiguration.from_runnable_config(config)
    
    # Use the new, more specific tool names
    tools = [
        tool(CoreProblem), 
        tool(Sections), 
        tool(AssembleReport), 
        tool(FinishReport)
    ]
    
    if configurable.ask_for_clarification:
        tools.append(tool(Question))
        
    return tools

async def supervisor(state: ReportState, config: RunnableConfig):
    """The supervisor node: invokes the LLM to decide the next action."""
    messages = state["messages"]
    configurable = MultiAgentConfiguration.from_runnable_config(config)
    supervisor_model = get_config_value(configurable.supervisor_model)
    llm = init_chat_model(model=supervisor_model)

    # If all research is done but the report isn't assembled, prompt the LLM to assemble it.
    if state.get("completed_sections") and not state.get("final_report"):
        messages = messages + [
            {
                "role": "user",
                "content": "All research sections are complete. You MUST call the AssembleReport tool now to compile the final document.",
            }
        ]

    supervisor_tool_list = await get_supervisor_tools(config)
    llm_with_tools = llm.bind_tools(
        supervisor_tool_list,
        parallel_tool_calls=False,
        tool_choice="any", # Force a tool call unless it's finished
    )

    system_prompt = SUPERVISOR_INSTRUCTIONS.format(today=get_today_str())
    if configurable.mcp_prompt:
        system_prompt += f"\n\n{configurable.mcp_prompt}"

    # Invoke the LLM with the current state to get the next tool call
    return {
        "messages": [
            await llm_with_tools.ainvoke(
                [{"role": "system", "content": system_prompt}] + messages
            )
        ]
    }

def _assemble_and_reindex_report(completed_sections: List[Section]) -> str:
    """
    Assembles the final report from completed sections, creating a consolidated
    and re-indexed reference list at the end.

    This function performs three main tasks:
    1. Parses all sections to find their local source lists and builds a master,
       deduplicated list of all references.
    2. Creates a mapping from each section's local citation number (e.g., [1], [2])
       to the new global citation number in the master list.
    3. Rewrites the content of each section to use the new global citation numbers,
       removes the old local source lists, and appends a final "References"
       section to the complete report.
    """
    master_references = []
    seen_references = set()
    reindexing_map = {}  # {section_idx: {old_citation_idx: new_master_idx}}

    # --- Step 1: Parse and Consolidate All References ---
    for section_idx, section in enumerate(completed_sections):
        reindexing_map[section_idx] = {}
        # Find the '### Sources' block in the section's content
        sources_match = re.search(r'###\s+Sources\s*\n(.*)', section.content, re.DOTALL)
        if not sources_match:
            continue

        source_text = sources_match.group(1)
        # Find all numbered list items (the URLs)
        local_sources = re.findall(r'^\s*\d+\.\s*(.*)', source_text, re.MULTILINE)

        for local_idx, url in enumerate(local_sources):
            url = url.strip()
            if url not in seen_references:
                seen_references.add(url)
                master_references.append(url)
            
            # Create the mapping from the old index to the new master index
            master_idx = master_references.index(url) + 1  # Citations are 1-based
            reindexing_map[section_idx][local_idx + 1] = master_idx

    # --- Step 2: Rewrite Section Content with New Citations ---
    processed_content_parts = []
    for section_idx, section in enumerate(completed_sections):
        # Remove the old '### Sources' block from the content
        content_without_sources = re.split(r'###\s+Sources', section.content)[0].strip()

        # Define a replacer function for re.sub
        def replacer(match):
            old_idx = int(match.group(1))
            # Look up the new index from our map
            new_idx = reindexing_map.get(section_idx, {}).get(old_idx)
            if new_idx:
                return f'[{new_idx}]'
            # If for some reason a citation can't be mapped, leave it as is
            return match.group(0)

        # Use re.sub with the replacer function to update all citations like [1], [2], etc.
        new_content = re.sub(r'\[(\d+)\]', replacer, content_without_sources)
        processed_content_parts.append(new_content)

    # --- Step 3: Assemble Final Report with Master Reference List ---
    final_report_body = "\n\n".join(processed_content_parts)
    
    # Create the final, consolidated references section
    if master_references:
        references_header = "\n\n\n## References"
        references_list = "\n".join([f"{i+1}. {url}" for i, url in enumerate(master_references)])
        final_report_body += f"{references_header}\n{references_list}"

    return final_report_body

async def supervisor_tools(
    state: ReportState, config: RunnableConfig
) -> Command[Literal["supervisor", "research_team", "__end__"]]:
    """Performs the tool call and sends to the research agent"""
    configurable = MultiAgentConfiguration.from_runnable_config(config)

    source_str = ""
    result_messages = []
    sections_to_research = []

    # Get tools based on configuration
    supervisor_tool_list = await get_supervisor_tools(config)
    supervisor_tools_by_name = {tool.name: tool for tool in supervisor_tool_list}
    search_tool_names = {
        tool.name
        for tool in supervisor_tool_list
        if tool.metadata is not None and tool.metadata.get("type") == "search"
    }

    # First process all tool calls to ensure we respond to each one (required for OpenAI)
    for tool_call in state["messages"][-1].tool_calls:
        # Get the tool
        tool = supervisor_tools_by_name[tool_call["name"]]
        # Perform the tool call - use ainvoke for async tools
        try:
            observation = await tool.ainvoke(tool_call["args"], config)
        except NotImplementedError:
            observation = tool.invoke(tool_call["args"], config)

        # Append to messages
        result_messages.append(
            {
                "role": "tool",
                "content": observation,
                "name": tool_call["name"],
                "tool_call_id": tool_call["id"],
            }
        )

        # Handle specific tool outputs for routing
        if tool_call["name"] == Sections.__name__:
            sections_to_research = cast(Sections, observation).report_structure
        elif tool_call["name"] == AssembleReport.__name__:
            # final_report = "\n\n".join([s.content for s in state["completed_sections"]])
            final_report = _assemble_and_reindex_report(state["completed_sections"])
            state_update = {"messages": state["messages"] + result_messages, "final_report": final_report}
            return Command(goto="supervisor", update=state_update)
        # Store special tool results for processing after all tools have been called
        elif tool_call["name"] == Question.__name__:
            # Question tool was called - return to supervisor to ask the question
            question_obj = cast(Question, observation)
            result_messages.append({"role": "assistant", "content": question_obj.question})
            return Command(goto=END, update={"messages": result_messages})
        elif tool_call["name"] in search_tool_names and configurable.include_source_str:
            source_str += cast(str, observation)

     # After processing all tool calls, decide the next step
    state_update = {"messages": state["messages"] + result_messages}

    if sections_to_research:
        # Delegate the framed sections to the research team
        return Command(
            goto=[Send("research_team", {"framed_section": s}) for s in sections_to_research],
            update=state_update,
        )
    else:
        # Include source string for evaluation
        if configurable.include_source_str and source_str:
            state_update["source_str"] = source_str
        # For other tools (CoreProblem, Question), loop back to the supervisor
        # This allows the supervisor to see its own diagnosis or the answer to its question
        return Command(goto="supervisor", update=state_update)


async def supervisor_should_continue(state: ReportState) -> str:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]
    # End because the supervisor asked a question or is finished
    if not last_message.tool_calls or (
        len(last_message.tool_calls) == 1
        and last_message.tool_calls[0]["name"] == FinishReport.__name__
    ):
        # Exit the graph
        return END

    # If the LLM makes a tool call, then perform an action
    return "supervisor_tools"


async def get_research_tools(config: RunnableConfig) -> list[BaseTool]:
    """Get research tools based on configuration"""
    search_tool = get_search_tool(config)
    tools = [tool(Section), tool(FinishResearch)]
    if search_tool is not None:
        tools.append(search_tool)  # Add search tool, if available
    existing_tool_names = {cast(BaseTool, tool).name for tool in tools}
    mcp_tools = await _load_mcp_tools(config, existing_tool_names)
    tools.extend(mcp_tools)
    return tools

async def research_agent(state: SectionState, config: RunnableConfig):
    """LLM decides whether to call a tool or not"""

    # Get configuration
    configurable = MultiAgentConfiguration.from_runnable_config(config)
    researcher_model = get_config_value(configurable.researcher_model)

    # Initialize the model
    llm = init_chat_model(model=researcher_model)

    # Get tools based on configuration
    research_tool_list = await get_research_tools(config)
    system_prompt = RESEARCH_INSTRUCTIONS.format(
        number_of_queries=configurable.number_of_queries,
        today=get_today_str(),
    )
    if configurable.mcp_prompt:
        system_prompt += f"\n\n{configurable.mcp_prompt}"

    # Ensure we have at least one user message (required by Anthropic)
    messages = state.get("messages", [])
    framed_section: FramedSection = state['framed_section']
    # On the first turn, construct the initial mission brief for the agent
    nl = "\n"
    if not messages:
        mission_brief = f"""
Your mission is to research and write the following section of our Board of Directors report:

**Section Name:** "{framed_section.name}"

**Your Core Task:** You must answer these key questions thoroughly:
- {nl.join(framed_section.key_questions_to_answer)}

**Writing Style & Format:**
- **Style Hint:** {framed_section.writing_style_hint}
- **Required Subsections:** You must structure your content to include these subsections: {', '.join(framed_section.subsections)}

Begin your research. Your first step should be to call a search tool with a query designed to address the core questions.
"""
        messages = [{"role": "user", "content": mission_brief}]
    else:
        # Subsequent turns: Inject a concise reminder to re-focus the agent.
        # This prevents "contextual drift" after multiple search cycles.
        reminder_text = f"""
**REMINDER & FOCUS CHECK:**
You have gathered some research. Before your next action, re-read your mission.

- **Section to Write:** "{framed_section.name}"
- **Key Questions to Answer:** {'; '.join(framed_section.key_questions_to_answer)}
- **Writing Style:** "{framed_section.writing_style_hint}"

Is your research sufficient to answer all the key questions and write the section now?
If YES, you MUST call the `Section` tool.
If NO, perform another targeted search to fill the remaining gaps.
"""
        # We append this as a new user message to put it at the forefront of the LLM's attention.
        messages.append({"role": "user", "content": reminder_text})

    return {
        "messages": [
            # Enforce tool calling to either perform more search or call the Section tool to write the section
            await llm.bind_tools(
                research_tool_list,
                parallel_tool_calls=False,
                # force at least one tool call
                tool_choice="any",
            ).ainvoke([{"role": "system", "content": system_prompt}] + messages)
        ]
    }


async def research_agent_tools(state: SectionState, config: RunnableConfig):
    """Performs the tool call and route to supervisor or continue the research loop"""
    configurable = MultiAgentConfiguration.from_runnable_config(config)

    result = []
    completed_section = None
    source_str = ""

    # Get tools based on configuration
    research_tool_list = await get_research_tools(config)
    research_tools_by_name = {tool.name: tool for tool in research_tool_list}
    search_tool_names = {
        tool.name
        for tool in research_tool_list
        if tool.metadata is not None and tool.metadata.get("type") == "search"
    }

    # Process all tool calls first (required for OpenAI)
    for tool_call in state["messages"][-1].tool_calls:
        # Get the tool
        tool = research_tools_by_name[tool_call["name"]]
        # Perform the tool call - use ainvoke for async tools
        try:
            observation = await tool.ainvoke(tool_call["args"], config)
        except NotImplementedError:
            observation = tool.invoke(tool_call["args"], config)

        # Append to messages
        result.append(
            {
                "role": "tool",
                "content": observation,
                "name": tool_call["name"],
                "tool_call_id": tool_call["id"],
            }
        )

        # Store the section observation if a Section tool was called
        if tool_call["name"] == Section.__name__:
            completed_section = cast(Section, observation)

        # Store the source string if a search tool was called
        if tool_call["name"] in search_tool_names and configurable.include_source_str:
            source_str += cast(str, observation)

    # After processing all tools, decide what to do next
    state_update = {"messages": result}
    if completed_section:
        # Write the completed section to state and return to the supervisor
        state_update["completed_sections"] = [completed_section]
    if configurable.include_source_str and source_str:
        state_update["source_str"] = source_str

    return state_update


async def research_agent_should_continue(state: SectionState) -> str:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls[0]["name"] == FinishResearch.__name__:
        # Research is done - return to supervisor
        return END
    else:
        return "research_agent_tools"


"""Build the multi-agent workflow"""

# Research agent workflow
research_builder = StateGraph(
    SectionState, output=SectionOutputState, config_schema=MultiAgentConfiguration
)
research_builder.add_node("research_agent", research_agent)
research_builder.add_node("research_agent_tools", research_agent_tools)
research_builder.add_edge(START, "research_agent")
research_builder.add_conditional_edges(
    "research_agent", research_agent_should_continue, ["research_agent_tools", END]
)
research_builder.add_edge("research_agent_tools", "research_agent")

# Supervisor workflow
supervisor_builder = StateGraph(
    ReportState,
    input=MessagesState,
    output=ReportStateOutput,
    config_schema=MultiAgentConfiguration,
)
supervisor_builder.add_node("supervisor", supervisor)
supervisor_builder.add_node("supervisor_tools", supervisor_tools)
supervisor_builder.add_node("research_team", research_builder.compile())

# Flow of the supervisor agent
supervisor_builder.add_edge(START, "supervisor")
supervisor_builder.add_conditional_edges(
    "supervisor", supervisor_should_continue, ["supervisor_tools", END]
)
supervisor_builder.add_edge("research_team", "supervisor")

graph = supervisor_builder.compile()
