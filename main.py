"""
FastAPI wrapper for LangGraph multi-agent board-report pipeline.
Save as `main.py`, then run:

    uvicorn main:app --reload  # dev
    uvicorn main:app --workers 4 --loop uvloop  # prod

Env vars expected:
  • OPENAI_API_KEY
  • GOOGLE_APPLICATION_CREDENTIALS (for BigQuery)
  • TAVILY_API_KEY  (if you enabled Tavily search)
"""
from __future__ import annotations

import asyncio, pathlib, datetime, json, typing as t
from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field, ValidationError
from starlette.background import BackgroundTask

# ←––––– import your graph module exactly as you defined it ––––→
from open_deep_research import graph
from open_deep_research.configuration import MultiAgentConfiguration
# ------------ FastAPI setup -------------
app = FastAPI(
    title="Board-Report Generator",
    summary="Runs a LangGraph multi-agent workflow and returns a board-ready report.",
    version="1.0.0",
)

# ------------ Request / Response models -------------
class RunConfig(BaseModel):
    """Subset of MultiAgentConfiguration you want to expose via API."""
    supervisor_model: str = Field(default="gpt-4o-mini")
    researcher_model: str = Field(default="gpt-4o-mini")
    ask_for_clarification: bool = False
    search_api: str = Field(default="duckduckgo")  # "tavily" | "none"
    number_of_queries: int = Field(default=3, ge=1, le=10)
    include_source_str: bool = False

    def to_internal(self) -> MultiAgentConfiguration:
        """Translate HTTP payload → internal config dataclass."""
        return MultiAgentConfiguration(
            supervisor_model=self.supervisor_model,
            researcher_model=self.researcher_model,
            ask_for_clarification=self.ask_for_clarification,
            search_api=self.search_api,
            number_of_queries=self.number_of_queries,
            include_source_str=self.include_source_str,
        )

class GenerateRequest(BaseModel):
    messages: t.List[str] = Field(
        description="Conversation history; last element is the NEW user request."
    )
    config: RunConfig = Field(default_factory=RunConfig)

class GenerateResponse(BaseModel):
    report_md_path: str
    report_docx_path: str
    created_at: datetime.datetime

# ------------ Helpers -------------
OUT_DIR = pathlib.Path("reports")
OUT_DIR.mkdir(exist_ok=True, parents=True)

async def _run_graph(req: GenerateRequest) -> pathlib.Path:
    """Actually run the LangGraph pipeline and persist artefacts."""
    # Build LangGraph-flavoured messages list:
    msgs = [{"role": "user", "content": m} for m in req.messages]

    result_state = await graph.ainvoke(
        msgs, config=req.config.to_internal()
    )

    final_report_md: str = result_state["final_report"]
    # Persist (your helper already converts to DOCX & returns md path)
    from open_deep_research.multi_agent import _persist_report  # reuse your fn
    md_path = _persist_report(final_report_md, report_dir=OUT_DIR)
    return md_path

# ------------ REST Endpoints -------------
@app.post("/generate_report", response_model=GenerateResponse, status_code=202)
async def generate_report(req: GenerateRequest):
    """
    Kick off the LangGraph run and return paths when done.
    For heavy workflows you may want to *queue* this and return a job_id.
    """
    try:
        md_path = await _run_graph(req)
    except ValidationError as ve:
        raise HTTPException(422, detail=str(ve))
    except Exception as e:
        raise HTTPException(500, detail=f"LangGraph error: {e}")

    return GenerateResponse(
        report_md_path=str(md_path),
        report_docx_path=str(md_path.with_suffix(".docx")),
        created_at=datetime.datetime.utcnow(),
    )

@app.get("/download/{kind}/{yyyymmdd}")
async def download(kind: str, yyyymmdd: str):
    """
    Simple file download helper:
      /download/md/2025-07-09   → board_report_2025-07-09.md
      /download/docx/2025-07-09 → board_report_2025-07-09.docx
    """
    ext = ".md" if kind == "md" else ".docx"
    f = OUT_DIR / f"board_report_{yyyymmdd}{ext}"
    if not f.exists():
        raise HTTPException(404, "File not found")
    return FileResponse(f)

# ------------ SSE streaming (optional) -------------
async def _sse_encode(aiter):
    async for chunk in aiter:
        yield f"data: {json.dumps(chunk)}\n\n"

@app.post("/stream_report")
async def stream_report(req: GenerateRequest):
    """
    Run the report and stream LangGraph state.json deltas back to the browser.
    Client-side:
        const evt = new EventSource("/stream_report");
        evt.onmessage = e => { const msg = JSON.parse(e.data); ... }
    """
    async def _inner():
        md_path = await _run_graph(req)
        # After finishing, send a final message with file URLs
        yield {"status": "complete",
               "md": f"/download/md/{md_path.stem[-10:]}",
               "docx": f"/download/docx/{md_path.stem[-10:]}"}

    return StreamingResponse(_sse_encode(_inner()), media_type="text/event-stream")

# ------------ Health -------------
@app.get("/healthz")
async def health():
    return {"status": "ok"}
