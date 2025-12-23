"""
Dev Team agents module.

Defines a virtual software development team:
- Team Leader (Orchestrator)
- Frontend Developer (React/Next.js)
- Backend Developer (Python/FastAPI)
- DevOps Engineer (Docker/CI)
"""

import os
from pathlib import Path

from agno.agent import Agent
from agno.models.google import Gemini
from agno.team import Team
from agno.tools.file import FileTools
from agno.tools.shell import ShellTools

from src.config import settings

# Define workspace for the agents
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
    # Shell tools allowed to run commands
    shell_tools = ShellTools() 
    return [file_tools, shell_tools]

def _create_specialists() -> list[Agent]:
    """
    Create the specialist developers.
    """
    tools = _create_tools()
    
    # 1. Frontend Developer
    frontend = Agent(
        role="Frontend Developer",
        model=_create_gemini_model(),
        tools=tools,
        instructions=[
            "You are an expert Frontend Developer specializing in React and Next.js.",
            "Your goal is to build the user interface based on requirements.",
            "IMPORTANT RULES:",
            "1. ALWAYS check if a file exists before creating it using `file_exists` or `list_files`.",
            "2. Read the markdown files before starting.",
            "3. Use `save_file` to write code. Ensure you write complete, runnable code.",
            "4. If you need to install packages, use `run_shell_command` (e.g., `npm install`).",
            "5. Coordinate with the Backend Dev for API integration.",
        ],
    )

    # 2. Backend Developer
    backend = Agent(
        role="Backend Developer",
        model=_create_gemini_model(),
        tools=tools,
        instructions=[
            "You are an expert Backend Developer specializing in Python (FastAPI) and Node.js.",
            "Your goal is to build the API and business logic.",
            "IMPORTANT RULES:",
            "1. ALWAYS check if a file exists before creating it.",
            "2. Read the markdown files to understand the architecture.",
            "3. Use `save_file` to write code.",
            "4. Provide clear API documentation or specification for the Frontend Dev.",
            "5. Ensure the server can run locally (e.g., `uvicorn main:app`).",
        ],
    )

    # 3. DevOps Engineer
    devops = Agent(
        role="DevOps Engineer",
        model=_create_gemini_model(),
        tools=tools,
        instructions=[
            "You are an expert DevOps Engineer.",
            "Your goal is to ensure the application runs smoothly.",
            "Tasks:",
            "- Create `Dockerfile` and `docker-compose.yml`.",
            "- Create run scripts (e.g., `run.sh`).",
            "- Ensure dependencies are listed in `requirements.txt` or `package.json`.",
            "",
            "IMPORTANT RULES:",
            "1. Check existing files before overwriting.",
            "2. When testing if a server starts, NEVER run blocking commands.",
            "   Use this pattern instead:",
            "   a) Start the server in the background: `python main.py &` or `uvicorn main:app &`",
            "   b) Wait briefly: `sleep 2`",
            "   c) Check if it's running: `curl -s http://localhost:PORT/health || echo 'Server not responding'`",
            "   d) Kill the background process: `pkill -f 'uvicorn|python main'` or `kill %1`",
            "3. NEVER run a server without `&` at the end - it will block forever.",
            "4. Always clean up background processes after testing.",
        ],
    )

    return [frontend, backend, devops]

def create_dev_team() -> Team:
    """
    Create the dev team orchestrated by a Team Leader.
    """
    specialists = _create_specialists()
    
    team_leader = Team(
        name="Team Leader",
        members=specialists,
        model=_create_gemini_model(),
        instructions=[
            "You are the Technical Team Leader of a high-performance software team.",
            "Your goal is to implement a Proof of Concept (PoC) based on the user's request.",
            "The team works in the `./workspace` directory.",
            "",
            "PROCESS:",
            "1. Analyze the user's request.",
            "2. Create a folder for the whole project, with the name of the project (make up a name based on the request).",
            "3. If the request includes a script to run, run it to create the boilerplate files. Otherwise, analyze the request and create the boilerplate code yourself. Don't forget git.",
            "4. Guarantee that the markdown files existing in the project after running the last step include:",
            "   - Project Name & Description",
            "   - Architecture / File Structure",
            "   - Tasks for each team and/or member",
            "5. Based on the management plan, delegate tasks to your specialists (Frontend, Backend, DevOps).",
            "   - Be specific about what they need to do.",
            "   - Ensure they know where to write files.",
            "6. Review their progress. Ask them to verify their work (e.g., 'Did you create the file?').",
            "7. Once the code is written, ask DevOps to ensure it can be run.",
            "8. Check the code and understand whether there are any issues. Clear any clutter. Update any README files with correct information.",
            "9. Report back to the user with a summary of what was built and how to run it.",
            "",
            "CRITICAL:",
            "- Do not hallucinate code. Ask your team to write it to disk.",
            "- If a file is missing, ask the relevant specialist to create it.",
            "- Ensure the final output is a runnable PoC.",
            "- NEVER run blocking commands (like starting a server without `&`). Always run servers in background, test, then kill them.",
        ],
    )

    return team_leader
