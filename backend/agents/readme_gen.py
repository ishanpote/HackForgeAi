from pydantic import BaseModel, Field
from backend.agents.base_agent import BaseAgent

class ReadmeOutput(BaseModel):
    readme_content: str = Field(description="The complete, professionally written README.md content in markdown format. Must include title, features, setup, installation, architecture overview, and usage instructions.")

class ReadmeGeneratorAgent(BaseModel, BaseAgent):
    class Config:
        arbitrary_types_allowed = True
        
    def __init__(self):
        instruction = (
            "You are the README Generator Agent of HackForge AI. Your goal is to write a highly professional, "
            "comprehensive README.md for the selected hackathon project. It must look ready for a top-tier GitHub "
            "repository. You must include sections for: Setup, Features, Architecture Overview, Installation, "
            "and Usage. Fill in all details (no placeholders!). Use markdown tables and lists to enhance readability."
        )
        BaseAgent.__init__(self, "README Generator Agent", instruction)

    def execute(self, project_id: str, best_idea: str, description: str, tech_stack: str, architecture_text: str, api_key: str = None) -> ReadmeOutput:
        self.log(project_id, "Drafting production-ready README.md document...")
        prompt = (
            f"Project Idea: {best_idea}\n"
            f"Description: {description}\n"
            f"Technology Stack: {tech_stack}\n"
            f"Architecture Details: {architecture_text}\n\n"
            "Generate a professional README.md. Write it in markdown inside the readme_content field."
        )
        
        response = self.run_llm(
            project_id=project_id,
            prompt=prompt,
            api_key=api_key,
            response_schema=ReadmeOutput
        )
        
        import json
        data = json.loads(response.text)
        self.log(project_id, "README document generated.")
        return ReadmeOutput(**data)
