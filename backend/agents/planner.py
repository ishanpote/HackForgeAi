from pydantic import BaseModel, Field
from typing import List
from backend.agents.base_agent import BaseAgent

class PlannerOutput(BaseModel):
    analysis: str = Field(description="Overview and assessment of the hackathon prompt and requirements")
    subtasks: List[str] = Field(description="A list of broken-down tasks required to fulfill this request")
    execution_order: List[str] = Field(description="The order in which the specialized agents should be executed")

class PlannerAgent(BaseAgent):
    def __init__(self):
        instruction = (
            "You are the Planner Agent of HackForge AI. Your responsibility is to analyze the user's "
            "hackathon input (name, theme, problem statement, constraints, tech preferences) and create "
            "a structured execution plan. You must break the problem down into logical tasks and identify "
            "the order of agent execution. The other agents are: Idea Generation, Research, Dataset Discovery, "
            "Technology Advisor, System Architecture, Development Planner, README Generator, Pitch Generator, "
            "Submission Review, and Project Manager."
        )
        super().__init__("Planner Agent", instruction)

    def execute(self, project_id: str, name: str, theme: str, problem_statement: str, constraints: str, tech_preferences: str, api_key: str = None) -> PlannerOutput:
        self.log(project_id, "Planning workflow execution based on input...")
        prompt = (
            f"Hackathon Name: {name}\n"
            f"Theme: {theme}\n"
            f"Problem Statement: {problem_statement}\n"
            f"Constraints: {constraints}\n"
            f"Preferred Technologies: {tech_preferences}\n\n"
            "Analyze this input, create an execution breakdown, and list the order of agent runs."
        )
        
        response = self.run_llm(
            project_id=project_id,
            prompt=prompt,
            api_key=api_key,
            response_schema=PlannerOutput
        )
        
        # Parse the structured output
        import json
        data = json.loads(response.text)
        self.log(project_id, "Workflow plan finalized.")
        return PlannerOutput(**data)
