"""
Dev Team agents module.

Defines a sequential pipeline of agents to build a Proof of Concept (PoC).
Pipeline: Architect -> Backend -> Frontend -> DevOps -> Reviewer
"""

import logging
import time
from pathlib import Path
from typing import Any

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.file import FileTools
from agno.tools.shell import ShellTools

from src.config import settings

logger = logging.getLogger(__name__)

WORKSPACE_DIR = Path("workspace")
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)


def _create_gemini_model() -> Gemini:
    """Create a Gemini model instance with configured settings."""
    return Gemini(
        id=settings.dev_team_gemini_model,
        api_key=settings.gemini_api_key,
    )


def _create_tools() -> list:
    """Create shared tools for the team."""
    file_tools = FileTools(base_dir=WORKSPACE_DIR)
    shell_tools = ShellTools()
    return [file_tools, shell_tools]


ARCHITECT_INSTRUCTIONS = [
    "You are a Senior Solutions Architect.",
    "Your goal is to design the BEST technical solution for the user's request.",
    "You are NOT bound to any specific stack. Choose the best tools for the job based on requirements.",
    "",
    "YOUR TASK:",
    "1. Analyze the User Request deeply.",
    "2. Create a project folder with an appropriate name in the workspace root.",
    "3. Inside that folder, create a detailed architecture.md file containing:",
    "",
    "   ## Project Structure",
    "   Complete file tree of all files to be created.",
    "",
    "   ## Tech Stack",
    "   Selected languages/frameworks with specific versions and reasoning.",
    "",
    "   ## Database Schema",
    "   Tables/Collections, fields, types, relationships.",
    "",
    "   ## API Specification",
    "   Every endpoint: Method, Path, Request Body, Response Body.",
    "",
    "   ## UI/UX Design",
    "   Key screens, components, and user flows.",
    "",
    "CRITICAL RULES:",
    "- Do NOT write application code. Only the specification.",
    "- Be specific about versions and libraries.",
    "- Ensure scope is manageable for a PoC but functionally complete.",
    "- The Backend and Frontend developers will follow this spec EXACTLY.",
]

BACKEND_INSTRUCTIONS = [
    "You are a Senior Backend Developer.",
    "Your goal is to implement the backend exactly as designed by the Architect.",
    "",
    "INPUT:",
    "You will receive the Architect's specification.",
    "",
    "YOUR TASK:",
    "1. Read architecture.md in the project folder.",
    "2. Initialize the project if needed (package.json, requirements.txt, etc.).",
    "3. Implement the Database Layer (Models, Connection, Migrations).",
    "4. Implement the API Layer (Routes, Controllers, Handlers).",
    "5. Run a build command to ensure everything compiles.",
    "6. Create a backend_report.md file summarizing:",
    "   - All implemented endpoints with their exact paths.",
    "   - The port the server runs on.",
    "   - How to start the backend locally.",
    "   - Any deviations from the spec (with justification).",
    "",
    "CRITICAL RULES:",
    "- Follow the spec STRICTLY. Do not rename endpoints or change paths.",
    "- Ensure the server can start without errors.",
    "- Use save_file to write all code files.",
    "- Do NOT start long-running servers. Just ensure files are correct.",
]

FRONTEND_INSTRUCTIONS = [
    "You are a Senior Frontend Developer.",
    "Your goal is to build the UI that connects to the Backend.",
    "",
    "INPUT:",
    "You will receive the Architect's Spec and the Backend's Report.",
    "",
    "YOUR TASK:",
    "1. Read the inputs carefully. Note the API URLs from backend_report.md.",
    "2. Scaffold the Frontend application in its designated folder.",
    "3. Implement all UI components and pages from the spec.",
    "4. Integrate with the API using the EXACT endpoints from the Backend Report.",
    "5. Run a build command to ensure everything compiles.",
    "6. Create a frontend_report.md file summarizing progress.",
    "",
    "CRITICAL RULES:",
    "- Do NOT mock data. Connect to the real backend endpoints.",
    "- Match the design from architecture.md exactly.",
    "- Ensure the app builds without errors.",
    "- Use save_file to write all code files.",
]

DEVOPS_INSTRUCTIONS = [
    "You are a DevOps Engineer.",
    "Your goal is to ensure the entire stack runs with one command.",
    "",
    "INPUT:",
    "Project context from all previous steps.",
    "",
    "YOUR TASK:",
    "1. Analyze the actual file structure in the workspace.",
    "2. Create Dockerfile for each service (backend, frontend).",
    "3. Create a docker-compose.yml to orchestrate all services.",
    "4. Create a run.sh script for easy startup.",
    "5. Run a build command to ensure everything compiles.",
    "6. Update the README.md with:",
    "   - Project description",
    "   - Tech stack summary",
    "   - How to run (docker-compose up)",
    "",
    "CRITICAL RULES:",
    "- Ensure ports in docker-compose match the application code.",
    "- Do NOT modify application code, only infrastructure files.",
    "- Use save_file to write all files.",
]

REVIEWER_INSTRUCTIONS = [
    "You are the Technical Team Lead.",
    "Your goal is to polish the final delivery.",
    "",
    "YOUR TASK:",
    "1. List all files in the workspace to review the project.",
    "2. Cleanup: Remove any empty folders or unused boilerplate files.",
    "3. Verification: Check that imports reference files that exist.",
    "4. Make sure there is a README.md file with instructions on how to run the project.",
    "5. Final Summary: Provide a friendly summary of what was built, and include the project's name. Make sure this summary is your ONLY output.",
    "",
    "CRITICAL RULES:",
    "- Do NOT rewrite the application. Only fix obvious mistakes.",
    "- Focus on cleanup and verification.",
    "- Your response should be the final summary for the user, ONLY.",
]


class DevTeamPipeline:
    """Sequential pipeline that runs agents one after another with context chaining."""

    MAX_RETRIES = 5
    BASE_DELAY = 30  # seconds

    def __init__(self):
        self.tools = _create_tools()

    def _create_agent(self, role: str, instructions: list[str]) -> Agent:
        """Create an agent with the given role and instructions."""
        return Agent(
            role=role,
            model=_create_gemini_model(),
            tools=self.tools,
            debug_mode=True,
            instructions=instructions,
            markdown=True,
        )

    def _run_with_retry(self, agent: Agent, prompt: str, step_name: str) -> Any:
        """Run an agent with retry logic for rate limits."""
        for attempt in range(self.MAX_RETRIES):
            try:
                response = agent.run(prompt)
                # Check if response indicates an error (empty content often means failure)
                if response and response.content:
                    return response
                # If empty, treat as potential rate limit issue
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.BASE_DELAY * (2 ** attempt)
                    logger.warning(f"{step_name}: Empty response, retrying in {delay}s (attempt {attempt + 1}/{self.MAX_RETRIES})")
                    time.sleep(delay)
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "Too Many Requests" in error_str:
                    if attempt < self.MAX_RETRIES - 1:
                        delay = self.BASE_DELAY * (2 ** attempt)
                        logger.warning(f"{step_name}: Rate limited, retrying in {delay}s (attempt {attempt + 1}/{self.MAX_RETRIES})")
                        time.sleep(delay)
                    else:
                        raise
                else:
                    raise
        return agent.run(prompt)  # Final attempt

    def run(self, request: str) -> Any:
        """
        Run the sequential pipeline: Architect -> Backend -> Frontend -> DevOps -> Reviewer.
        Each step receives context from previous steps.
        """
        # Step 1: ARCHITECT
        logger.info("=" * 60)
        logger.info("STEP 1: ARCHITECT")
        logger.info("=" * 60)
        architect = self._create_agent("Solutions Architect", ARCHITECT_INSTRUCTIONS)
        architect_response = self._run_with_retry(architect, request, "Architect")
        architect_output = architect_response.content

        # Step 2: BACKEND
        logger.info("=" * 60)
        logger.info("STEP 2: BACKEND DEVELOPER")
        logger.info("=" * 60)
        backend = self._create_agent("Backend Developer", BACKEND_INSTRUCTIONS)
        backend_prompt = f"Architect's Specification:\n\n{architect_output}"
        backend_response = self._run_with_retry(backend, backend_prompt, "Backend")
        backend_output = backend_response.content

        # Step 3: FRONTEND
        logger.info("=" * 60)
        logger.info("STEP 3: FRONTEND DEVELOPER")
        logger.info("=" * 60)
        frontend = self._create_agent("Frontend Developer", FRONTEND_INSTRUCTIONS)
        frontend_prompt = (
            f"Architect's Specification:\n\n{architect_output}\n\n"
            f"---\n\n"
            f"Backend Developer's Report:\n\n{backend_output}"
        )
        frontend_response = self._run_with_retry(frontend, frontend_prompt, "Frontend")
        frontend_output = frontend_response.content

        # Step 4: DEVOPS
        logger.info("=" * 60)
        logger.info("STEP 4: DEVOPS ENGINEER")
        logger.info("=" * 60)
        devops = self._create_agent("DevOps Engineer", DEVOPS_INSTRUCTIONS)
        devops_prompt = (
            f"Project Context:\n\n"
            f"Architect's Spec:\n{architect_output}\n\n"
            f"Backend Report:\n{backend_output}\n\n"
            f"Frontend Report:\n{frontend_output}"
        )
        self._run_with_retry(devops, devops_prompt, "DevOps")

        # Step 5: REVIEWER
        logger.info("=" * 60)
        logger.info("STEP 5: TEAM LEAD REVIEW")
        logger.info("=" * 60)
        reviewer = self._create_agent("Team Lead", REVIEWER_INSTRUCTIONS)
        reviewer_response = self._run_with_retry(
            reviewer,
            "Review the project in the workspace. Clean it up and provide a final summary.",
            "Reviewer"
        )

        return reviewer_response


def create_dev_team():
    """
    Factory function for router compatibility.
    Returns a DevTeamPipeline instance with a .run() method.
    """
    return DevTeamPipeline()
