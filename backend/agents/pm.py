from pydantic import BaseModel, Field
from backend.agents.base_agent import BaseAgent

class PMOutput(BaseModel):
    executive_summary: str = Field(description="A concise, highly professional executive summary of the project blueprint (markdown format)")
    polished_blueprint: str = Field(description="The finalized, compiled, and resolved blueprint text (markdown format) merging all components cleanly")

class ProjectManagerAgent(BaseModel, BaseAgent):
    class Config:
        arbitrary_types_allowed = True
        
    def __init__(self):
        instruction = (
            "You are the Project Manager Agent of HackForge AI. Your goal is to synthesize the work of all "
            "specialized agents (ideas, research, stack, architecture, roadmap, pitch, and review findings) into a "
            "singular, highly polished, consistent hackathon project blueprint. You must resolve any conflicting "
            "recommendations highlighted by the Submission Review Agent and write a compelling executive summary."
        )
        BaseAgent.__init__(self, "Project Manager Agent", instruction)

    def execute(self, project_id: str, compiled_artifacts_str: str, review_text: str, api_key: str = None) -> PMOutput:
        self.log(project_id, "Compiling final project blueprint and executive summary...")
        prompt = (
            f"All Generated Artifacts:\n{compiled_artifacts_str}\n\n"
            f"Submission Review Feedback:\n{review_text}\n\n"
            "Combine, clean, resolve any conflicts, and structure this into a professional project blueprint. "
            "Write the executive summary in markdown in the executive_summary field."
        )
        
        response = self.run_llm(
            project_id=project_id,
            prompt=prompt,
            api_key=api_key,
            response_schema=PMOutput
        )
        
        import json
        data = json.loads(response.text)
        self.log(project_id, "Project blueprint and executive summary compiled by PM.")
        return PMOutput(**data)
