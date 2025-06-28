from pydantic import BaseModel, Field
from typing import Annotated, List
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
    sql_script: str = Field(None, description="SQL script ")
    follow_up_questions: List[str] = Field(
        None, description="List of follow-up questions to ask the user based on the SQL script."
    )
    explaination: str = Field(None, description="Explanation of the SQL script.")
    