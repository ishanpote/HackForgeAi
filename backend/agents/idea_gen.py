from pydantic import BaseModel, Field
from typing import List
from backend.agents.base_agent import BaseAgent

class ProjectIdea(BaseModel):
    name: str = Field(description="Name of the project idea")
    tagline: str = Field(description="Catchy tagline for the project")
    description: str = Field(description="Detailed overview of the idea and how it works")
    innovation_score: int = Field(description="Score from 1 to 10 evaluating how unique and innovative the idea is")
    feasibility_score: int = Field(description="Score from 1 to 10 evaluating how achievable this is in a short hackathon")
    reasoning: str = Field(description="Explanation for the given scores")

class IdeaGenOutput(BaseModel):
    ideas: List[ProjectIdea] = Field(description="List of at least 3 distinct project ideas")
    best_idea_name: str = Field(description="The name of the selected best project idea")
    selection_reasoning: str = Field(description="Detailed explanation of why this specific idea was chosen as the best fit")

class IdeaGenerationAgent(BaseAgent):
    def __init__(self):
        instruction = (
            "You are the Idea Generation Agent of HackForge AI. Your goal is to brainstorm at least three "
            "innovative and distinct project ideas based on the user's hackathon details. For each idea, "
            "you must rate its Innovation (1-10) and Feasibility (1-10) and explain your reasoning. "
            "Finally, select the single best idea that balances feasibility and innovation and write a "
            "thorough justification for why it should be forged."
        )
        super().__init__("Idea Generation Agent", instruction)

    def execute(self, project_id: str, name: str, theme: str, problem_statement: str, constraints: str, tech_preferences: str, api_key: str = None) -> IdeaGenOutput:
        self.log(project_id, "Brainstorming and scoring project ideas...")
        prompt = (
            f"Hackathon Name: {name}\n"
            f"Theme: {theme}\n"
            f"Problem Statement: {problem_statement}\n"
            f"Constraints: {constraints}\n"
            f"Preferred Technologies: {tech_preferences}\n\n"
            "Generate at least 3 distinct project ideas. Rate each, select the best one, and justify the choice."
        )
        
        response = self.run_llm(
            project_id=project_id,
            prompt=prompt,
            api_key=api_key,
            response_schema=IdeaGenOutput
        )
        
        import json
        data = json.loads(response.text)
        self.log(project_id, f"Idea generation complete. Selected: '{data['best_idea_name']}'")
        return IdeaGenOutput(**data)
