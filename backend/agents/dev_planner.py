from pydantic import BaseModel, Field
from typing import List
from backend.agents.base_agent import BaseAgent

class DevMilestone(BaseModel):
    title: str = Field(description="Title of the milestone (e.g. Phase 1: Core API & DB Setup)")
    description: str = Field(description="Summary of what this milestone accomplishes")
    estimated_hours: int = Field(description="Estimated hours to complete this milestone")
    tasks: List[str] = Field(description="List of specific tasks within this milestone")

class DevPlannerOutput(BaseModel):
    milestones: List[DevMilestone] = Field(description="Sequential list of development phases")
    complexity_estimation: str = Field(description="Estimated project complexity (Easy, Medium, Hard) along with reason")
    prioritization_matrix: str = Field(description="Guidance on which features are core MVPs vs future enhancements")
    roadmap_summary: str = Field(description="A markdown-formatted summary of the roadmap and development flow")

class DevelopmentPlannerAgent(BaseModel, BaseAgent):
    class Config:
        arbitrary_types_allowed = True
        
    def __init__(self):
        instruction = (
            "You are the Development Planner Agent of HackForge AI. Your responsibility is to outline a realistic, "
            "step-by-step development roadmap for the selected project. Group development into 3-4 distinct milestones "
            "(e.g., MVP Core, Integrations, UI Polish, Deploy). List exact tasks, estimate hours, score complexity, "
            "and lay out a prioritization roadmap."
        )
        BaseAgent.__init__(self, "Development Planner Agent", instruction)

    def execute(self, project_id: str, best_idea: str, description: str, tech_stack: str, api_key: str = None) -> DevPlannerOutput:
        self.log(project_id, "Creating milestones and development roadmap...")
        prompt = (
            f"Project Idea: {best_idea}\n"
            f"Description: {description}\n"
            f"Technology Stack: {tech_stack}\n\n"
            "Build a detailed development roadmap. Ensure tasks are concrete and timelines fit within a typical hackathon or immediate post-hackathon scope."
        )
        
        response = self.run_llm(
            project_id=project_id,
            prompt=prompt,
            api_key=api_key,
            response_schema=DevPlannerOutput
        )
        
        import json
        data = json.loads(response.text)
        self.log(project_id, "Development roadmap formulated.")
        return DevPlannerOutput(**data)
