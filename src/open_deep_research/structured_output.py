from pydantic import BaseModel, Field

class VizResponse(BaseModel):
    """
    Structured answer returned by the visualization agent.
    """
    python_code: str = Field(
        ..., description="Standalone Python snippet that renders the chart."
    )
    reason: str = Field(
        ..., description="Explain reasoning behind the visualization choice and how it relates to the data."
    )
    explain_result: str = Field(
        ..., description="Explain the result of the visualization, including any insights or patterns observed."
    )

class SQLResponse(BaseModel):
    """
    Structured answer returned by the visualization agent.
    """
    query: str = Field(
        ..., description="SQL query"
    )
    