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
    description="Submit a note to be debated by a council of 7 AI experts (Portugal-based team context). Returns GO/NO-GO decision.",
)
async def call_council(note: NoteInput) -> CouncilResponse:
    """
    Run a council debate on the provided note.

    The council consists of 7 members (6 voters + 1 facilitator):
    - Carlos Mendes (Tech Architect): Technical feasibility, stack recommendations
    - Sofia Almeida (VC): Market fit, 0-10 potential score
    - Inês Ferreira (UX Designer): User journeys, 3-click core task
    - Miguel Santos (Security Auditor): Compliance, GDPR, data risks
    - Ana Costa (Product Owner): Target audience, value proposition
    - Dr. Raven Cruz (Contrarian): Challenges assumptions, stress-tests ideas
    - João Oliveira (Synthesizer): Facilitates consensus (non-voting)

    Context: Portugal-based small team, fast results preferred.
    Output: Clear GO/NO-GO decision (no pivots allowed).

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
