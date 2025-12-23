"""
Dev Team router module.

Defines the /build_poc endpoint for running the virtual dev team.
"""

import logging

from fastapi import APIRouter, HTTPException

from src.dev_team import create_dev_team
from src.models import NoteInput, DevTeamResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dev_team", tags=["dev_team"])


@router.post(
    "/build_poc",
    response_model=DevTeamResponse,
    summary="Build a Proof of Concept",
    description="Submit a request for the dev team to build a PoC. They will write files to the workspace.",
)
async def build_poc(note: NoteInput) -> DevTeamResponse:
    """
    Run the dev team on the provided request.

    The team consists of:
    - Team Leader (Coordinator)
    - Frontend Dev (React)
    - Backend Dev (FastAPI)
    - DevOps Engineer (Infrastructure)

    Args:
        note: The input request describing the PoC to build.

    Returns:
        DevTeamResponse with the execution result.

    Raises:
        HTTPException: If the execution fails.
    """
    try:
        logger.info("Starting dev team for request: %s...", note.content[:50])

        # Create fresh team for each request
        team_leader = create_dev_team()

        # Run the team
        # We give a clear prompt to start the process
        prompt = f"User Request: {note.content}\n\nPlease start the development process."
        response = team_leader.run(prompt)

        logger.info("Dev team execution completed successfully")

        return DevTeamResponse(
            status="success",
            result=response.content,
        )

    except Exception as e:
        logger.exception("Dev team execution failed: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Dev team execution failed: {str(e)}",
        ) from e
