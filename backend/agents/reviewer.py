from pydantic import BaseModel, Field
from typing import List
from backend.agents.base_agent import BaseAgent

class ReviewerOutput(BaseModel):
    consistency_check: str = Field(description="Review of alignment across tech recommendations, roadmap, pitch, and README")
    missing_sections: List[str] = Field(description="List of detected gaps or details that need clarification")
    improvement_suggestions: List[str] = Field(description="List of concrete, actionable suggestions to make the blueprint stand out")
    submission_checklist: List[str] = Field(description="A curated final checklist for submission based on the project blueprint")

class SubmissionReviewAgent(BaseModel, BaseAgent):
    class Config:
        arbitrary_types_allowed = True
        
    def __init__(self):
        instruction = (
            "You are the Submission Review Agent of HackForge AI. Your role is to review all compiled artifacts "
            "(Idea, Research, Stack, Architecture, Roadmap, README, Pitch deck) for consistency, completeness, and feasibility. "
            "Detect if anything is missing, identify logical gaps (e.g. database tech doesn't match the stack explanation, or the README setup "
            "mentions node but we recommended Python), suggest enhancements to impress judges, and compile a final submission checklist."
        )
        BaseAgent.__init__(self, "Submission Review Agent", instruction)

    def execute(self, project_id: str, compiled_artifacts_str: str, api_key: str = None) -> ReviewerOutput:
        self.log(project_id, "Auditing all generated artifacts for consistency and quality...")
        prompt = (
            f"Compiled Artifacts Context:\n{compiled_artifacts_str}\n\n"
            "Review this material carefully. Check for consistency, list any issues, suggest improvements, and write a submission checklist."
        )
        
        response = self.run_llm(
            project_id=project_id,
            prompt=prompt,
            api_key=api_key,
            response_schema=ReviewerOutput
        )
        
        import json
        data = json.loads(response.text)
        self.log(project_id, "Consistency review and checklist compiled.")
        return ReviewerOutput(**data)
