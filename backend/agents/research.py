from pydantic import BaseModel, Field
from typing import List
from backend.agents.base_agent import BaseAgent

class CompetitorProject(BaseModel):
    name: str = Field(description="Name of the similar/competing project or product")
    url: str = Field(description="URL or search source where this was found")
    description: str = Field(description="Short description of what the project does")
    features: List[str] = Field(description="Key features of the competitor project")

class ResearchOutput(BaseModel):
    similar_projects: List[CompetitorProject] = Field(description="List of similar projects found via search")
    existing_solutions: str = Field(description="A summary of how the problem is currently addressed in the industry")
    innovation_gaps: List[str] = Field(description="Key limitations in existing solutions and areas where our project can excel")
    research_summary: str = Field(description="A thorough, professional markdown summary of the research findings")

class ResearchAgent(BaseAgent):
    def __init__(self):
        instruction = (
            "You are the Research Agent of HackForge AI. Your job is to conduct comprehensive market research "
            "on the user's hackathon statement. You MUST use the Google Search tool to search for existing projects, "
            "open-source repos, or enterprise tools that address the same problem. Analyze their features, identify "
            "existing solutions, spot gaps in innovation (e.g., lack of mobile support, complex setup, poor AI utilization), "
            "and write a professional research summary in markdown."
        )
        BaseAgent.__init__(self, "Research Agent", instruction)

    def execute(self, project_id: str, problem_statement: str, theme: str, api_key: str = None) -> ResearchOutput:
        self.log(project_id, "Searching the web for competitors and similar projects...")
        prompt = (
            f"Hackathon Theme: {theme}\n"
            f"Problem Statement: {problem_statement}\n\n"
            "Search for existing solutions, projects, and apps. Analyze their strengths and weaknesses, "
            "highlight what is missing, and provide a competitor list."
        )
        
        # We run with google_search=True to enable native grounding!
        response = self.run_llm(
            project_id=project_id,
            prompt=prompt,
            api_key=api_key,
            response_schema=ResearchOutput,
            google_search=True
        )
        
        import json
        data = json.loads(response.text)
        self.log(project_id, "Competitor research completed.")
        return ResearchOutput(**data)
