"""
Run with:
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload
Dependencies:
    pip install "fastapi[all]" sse-starlette langchain langgraph open-deep-research
Environment:
    export OPENAI_API_KEY="sk-…"
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import asdict
from typing import Any, AsyncGenerator, Dict, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from open_deep_research.configuration import MultiAgentConfiguration
import open_deep_research.multi_agent as ma  # exposes `graph`  :contentReference[oaicite:0]{index=0}

# ------------------------------------------------------------------------------
# Configuration helpers
# ------------------------------------------------------------------------------

def build_runnable_config(
    supervisor_model: str,
    researcher_model: str,
    number_of_queries: int,
    search_api: str,
) -> RunnableConfig:
    """Create a per-request RunnableConfig for the multi-agent graph."""
    cfg = MultiAgentConfiguration(
        supervisor_model=supervisor_model,
        researcher_model=researcher_model,
        search_api=search_api,
        ask_for_clarification=False,
        include_source_str=False,
        number_of_queries=number_of_queries,
    )
    return RunnableConfig(configurable=asdict(cfg))


# ------------------------------------------------------------------------------
# Pydantic I/O schemas
# ------------------------------------------------------------------------------

class ReportRequest(BaseModel):
    prompt: str = Field(..., description="User question or task.")
    supervisor_model: str = Field("gpt-4o-mini", description="Model for supervisor.")
    researcher_model: str = Field("gpt-4o-mini", description="Model for researchers.")
    search_api: str = Field("none", description="'none', 'tavily', or 'duckduckgo'.")
    number_of_queries: int = Field(2, ge=1, le=5)

class ReportResponse(BaseModel):
    final_report: str
    # Include more metadata here if desired (run time, token count, etc.)


# ------------------------------------------------------------------------------
# FastAPI app
# ------------------------------------------------------------------------------

app = FastAPI(title="Open-Deep-Research Micro-service")


@app.post("/report", response_model=ReportResponse, summary="Blocking report generator")
async def generate_report(req: ReportRequest) -> ReportResponse:
    """Return the full markdown report once ready."""
    rcfg = build_runnable_config(
        supervisor_model=req.supervisor_model,
        researcher_model=req.researcher_model,
        number_of_queries=req.number_of_queries,
        search_api=req.search_api,
    )
    state: Dict[str, Any] = {"messages": [HumanMessage(content=req.prompt)]}

    try:
        result = await ma.graph.ainvoke(state, config=rcfg)
        return ReportResponse(final_report=result["final_report"])
    except Exception as err:
        logging.exception("Graph execution failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err),
        ) from err


# ------------------------------------------------------------------------------
# Streaming version using Server-Sent Events
# ------------------------------------------------------------------------------

async def _stream_worker(
    queue: "asyncio.Queue[str]",
    state: MessagesState,
    rcfg: RunnableConfig,
) -> None:
    """Feeds partial updates into the queue."""
    async for chunk in ma.graph.astream(state, config=rcfg):
        if "final_report" in chunk:
            await queue.put(chunk["final_report"])
    await queue.put("[STREAM_END]")  # sentinel


async def _sse_generator(queue: "asyncio.Queue[str]") -> AsyncGenerator[str, None]:
    """Convert queue messages into SSE data events."""
    while True:
        msg = await queue.get()
        if msg == "[STREAM_END]":
            break
        yield msg

@app.get("/report/stream", summary="Server-Sent Event stream of partial report")
async def generate_report_stream(
    prompt: str,
    supervisor_model: str = "gpt-4o-mini",
    researcher_model: str = "gpt-4o-mini",
    search_api: str = "none",
    number_of_queries: int = 2,
) -> StreamingResponse:
    """Stream markdown as it is produced."""
    rcfg = build_runnable_config(
        supervisor_model=supervisor_model,
        researcher_model=researcher_model,
        number_of_queries=number_of_queries,
        search_api=search_api,
    )
    state: Dict[str, Any] = {"messages": [HumanMessage(content=prompt)]}

    queue: "asyncio.Queue[str]" = asyncio.Queue()
    # Kick off graph in background
    asyncio.create_task(_stream_worker(queue, state, rcfg))
    return EventSourceResponse(_sse_generator(queue))


# ------------------------------------------------------------------------------
# Health probe
# ------------------------------------------------------------------------------

@app.get("/health", summary="Liveness probe")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


# ------------------------------------------------------------------------------
# Uvicorn entry-point (optional)
# ------------------------------------------------------------------------------

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
