from pydantic import BaseModel, Field
from typing import List
from backend.agents.base_agent import BaseAgent

class Slide(BaseModel):
    slide_number: int = Field(description="Slide number in sequence")
    title: str = Field(description="Slide title")
    bullet_points: List[str] = Field(description="Main bullet points or talking points for this slide")
    visual_suggestion: str = Field(description="Description of what visuals or charts to show on this slide")

class PitchGeneratorOutput(BaseModel):
    elevator_pitch: str = Field(description="A powerful, concise 30-second elevator pitch (1-2 sentences)")
    presentation_outline: List[Slide] = Field(description="Slide-by-slide structure for a 3-5 minute hackathon presentation (approx 7-10 slides)")
    demo_flow: List[str] = Field(description="Step-by-step walkthrough script for the project demo video or live presentation")
    future_scope: List[str] = Field(description="Key directions for future features, scaling, or business model extension beyond the hackathon")

class PitchGeneratorAgent(BaseModel, BaseAgent):
    class Config:
        arbitrary_types_allowed = True
        
    def __init__(self):
        instruction = (
            "You are the Pitch Generator Agent of HackForge AI. Your goal is to draft a compelling pitch strategy "
            "for the hackathon submission. You need to write a catchy elevator pitch, design a 7-10 slide deck "
            "presentation structure (with visual ideas), formulate a step-by-step product demonstration flow "
            "script, and outline the future scope of the project."
        )
        BaseAgent.__init__(self, "Pitch Generator Agent", instruction)

    def execute(self, project_id: str, best_idea: str, description: str, innovation_gaps: str, api_key: str = None) -> PitchGeneratorOutput:
        self.log(project_id, "Formulating elevator pitch, presentation slide outline, and demo script...")
        prompt = (
            f"Project Idea: {best_idea}\n"
            f"Description: {description}\n"
            f"Market Gaps Identified: {innovation_gaps}\n\n"
            "Build a compelling slide deck outline, demo walkthrough flow, elevator pitch, and future scope items."
        )
        
        response = self.run_llm(
            project_id=project_id,
            prompt=prompt,
            api_key=api_key,
            response_schema=PitchGeneratorOutput
        )
        
        import json
        data = json.loads(response.text)
        self.log(project_id, "Pitch presentation outlines generated.")
        return PitchGeneratorOutput(**data)
