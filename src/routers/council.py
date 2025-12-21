"""
Council router module.

Defines the /call_council endpoint for running council debates.
"""

import logging

from fastapi import APIRouter, HTTPException

from src.council import create_council_team
from src.models import NoteInput, CouncilResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/council", tags=["council"])


@router.post(
    "/call_council",
    response_model=CouncilResponse,
    summary="Run a council debate",
    description="Submit a note to be debated by a council of 5 AI experts with distinct personas.",
)
async def call_council(note: NoteInput) -> CouncilResponse:
    """
    Run a council debate on the provided note.

    The council consists of 5 members:
    - Victoria Chen (Venture Capitalist): Market viability and ROI
    - Marcus Webb (Tech Architect): Technical feasibility
    - Priya Sharma (UX Lead): User experience and adoption
    - Dr. Raven Cross (Contrarian): Challenges assumptions
    - Jordan Ellis (Synthesizer): Brings perspectives together

    Args:
        note: The input note containing the idea to debate.

    Returns:
        CouncilResponse with the debate conclusion.

    Raises:
        HTTPException: If the debate fails to execute.
    """
    try:
        logger.info("Starting council debate for note: %s...", note.content[:50])

        # Create fresh council team for each request to prevent state leakage
        council_team = create_council_team()

        # Run the debate
        prompt = f"Here is the idea to evaluate:\n\n{note.content}"
        response = council_team.run(prompt)

        logger.info("Council debate completed successfully")

        return CouncilResponse(
            status="success",
            conclusion=response.content,
        )

    except Exception as e:
        logger.exception("Council debate failed: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Council debate failed: {str(e)}",
        ) from e
