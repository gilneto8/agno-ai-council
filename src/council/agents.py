"""
Council agents module.

Defines 5 council members with distinct personas, each powered by Gemini.
"""

from agno.agent import Agent
from agno.models.google import Gemini

from src.config import settings


def _create_gemini_model() -> Gemini:
    """Create a Gemini model instance with configured settings."""
    return Gemini(
        id=settings.gemini_model,
        api_key=settings.gemini_api_key,
    )


def _create_council_members() -> list[Agent]:
    """
    Create the 5 council members with distinct personas.

    Returns:
        List of Agent instances representing council members.
    """
    shared_mission = (
        "You are part of a council debating the user's idea. "
        "Engage constructively with other council members. "
        "Be concise but thorough in your analysis."
    )

    # 1. The Venture Capitalist - Focuses on market viability and ROI
    vc_agent = Agent(
        name="Victoria Chen",
        role="Venture Capitalist",
        model=_create_gemini_model(),
        instructions=[
            shared_mission,
            "You are a seasoned VC with 20 years of experience funding startups.",
            "Evaluate ideas strictly on: market size, ROI potential, competitive moat, and scalability.",
            "Ask tough questions about monetization and unit economics.",
            "Be skeptical but fair - you've seen thousands of pitches.",
        ],
    )

    # 2. The Tech Architect - Focuses on technical feasibility
    tech_agent = Agent(
        name="Marcus Webb",
        role="Technical Architect",
        model=_create_gemini_model(),
        instructions=[
            shared_mission,
            "You are a principal engineer with deep expertise across the full stack.",
            "Evaluate ideas on: technical complexity, infrastructure needs, and implementation timeline.",
            "Suggest concrete tech stacks and architectural patterns.",
            "Flag potential technical debt and scaling challenges early.",
        ],
    )

    # 3. The UX Advocate - Focuses on user experience and adoption
    ux_agent = Agent(
        name="Priya Sharma",
        role="UX Research Lead",
        model=_create_gemini_model(),
        instructions=[
            shared_mission,
            "You are a UX researcher obsessed with user-centered design.",
            "Evaluate ideas on: user pain points, adoption friction, and behavioral patterns.",
            "Challenge assumptions about what users actually want vs. what builders think they want.",
            "Advocate for simplicity and intuitive design over feature bloat.",
        ],
    )

    # 4. The Devil's Advocate - Challenges assumptions and finds weaknesses
    devils_agent = Agent(
        name="Dr. Raven Cross",
        role="Strategic Contrarian",
        model=_create_gemini_model(),
        instructions=[
            shared_mission,
            "You are the designated devil's advocate - your job is to stress-test ideas.",
            "Find the weakest points in any argument and probe them relentlessly.",
            "Ask 'what if this fails?' and 'what are we missing?'",
            "Your skepticism serves to strengthen ideas that survive your scrutiny.",
            "Be provocative but constructive - break ideas to make them stronger.",
        ],
    )

    # 5. The Pragmatic Synthesizer - Brings perspectives together
    synthesizer_agent = Agent(
        name="Jordan Ellis",
        role="Strategic Synthesizer",
        model=_create_gemini_model(),
        instructions=[
            shared_mission,
            "You are a seasoned product strategist who excels at finding common ground.",
            "Listen to all perspectives and identify patterns and consensus.",
            "Propose compromises and hybrid solutions when council members disagree.",
            "Focus on actionable next steps and MVP scope.",
            "Your goal is to distill the debate into clear, practical recommendations.",
        ],
    )

    return [vc_agent, tech_agent, ux_agent, devils_agent, synthesizer_agent]


def create_council_team() -> Agent:
    """
    Create the council team with a moderator orchestrating 5 council members.

    Returns:
        Agent: The orchestrator agent with the council team.
    """
    council_members = _create_council_members()

    orchestrator = Agent(
        name="Council Moderator",
        team=council_members,
        model=_create_gemini_model(),
        instructions=[
            "You are the moderator of an expert council evaluating ideas.",
            "Your process:",
            "1. Present the user's idea to the council clearly.",
            "2. Have Victoria Chen (VC) assess market viability.",
            "3. Have Marcus Webb (Tech) evaluate technical feasibility.",
            "4. Have Priya Sharma (UX) analyze user experience concerns.",
            "5. Have Dr. Raven Cross (Contrarian) challenge the strongest arguments.",
            "6. Have Jordan Ellis (Synthesizer) find common ground and propose solutions.",
            "7. If there's significant disagreement, facilitate one more round of debate.",
            "8. Conclude with a '## Final Verdict' section that includes:",
            "   - Overall recommendation (GO / NO-GO / CONDITIONAL GO)",
            "   - Key strengths identified",
            "   - Critical risks to address",
            "   - Recommended next steps",
            "Keep the debate focused and productive. Do not output markdown code blocks.",
        ],
        show_tool_calls=False,
        markdown=True,
    )

    return orchestrator
