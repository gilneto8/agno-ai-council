from pydantic import BaseModel, Field


class NoteInput(BaseModel):
    """Input model for the council endpoint."""

    content: str = Field(
        ...,
        description="The note content to be debated by the council",
        min_length=1,
        examples=["I want to build an AI-powered todo app that learns user habits."],
    )


class CouncilResponse(BaseModel):
    """Response model from the council debate."""

    status: str = Field(default="success", description="Status of the request")
    conclusion: str = Field(..., description="The council's debate conclusion")


class DevTeamResponse(BaseModel):
    """Response model from the dev team."""

    status: str = Field(default="success", description="Status of the request")
    result: str = Field(..., description="The dev team's execution result")
