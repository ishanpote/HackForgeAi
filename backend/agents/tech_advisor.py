from pydantic import BaseModel, Field
from typing import List, Dict
from backend.agents.base_agent import BaseAgent

class TechRecommendation(BaseModel):
    technology: str = Field(description="The recommended language, library, framework, or tool")
    explanation: str = Field(description="Why this technology is recommended for this hackathon project")

class TechAdvisorOutput(BaseModel):
    frontend: TechRecommendation = Field(description="Frontend architecture recommendation")
    backend: TechRecommendation = Field(description="Backend server framework recommendation")
    database: TechRecommendation = Field(description="Primary database technology")
    ai_framework: TechRecommendation = Field(description="AI/ML model, SDK, or vector storage stack")
    cloud_platform: TechRecommendation = Field(description="Hosting and deployment cloud platform")
    apis: List[TechRecommendation] = Field(description="Other essential libraries, services, or APIs")
    summary_rationale: str = Field(description="A concise summary of how this stack synergizes and complies with constraints")

class TechnologyAdvisorAgent(BaseModel, BaseAgent):
    class Config:
        arbitrary_types_allowed = True
        
    def __init__(self):
        instruction = (
            "You are the Technology Advisor Agent of HackForge AI. Your goal is to design a production-ready "
            "and developer-friendly technology stack for the selected hackathon project. You must recommend specific "
            "technologies for Frontend, Backend, Database, AI/ML SDK, and Cloud platform. Account for any user-provided "
            "constraints or preferences, and explain why each tech is optimal for a rapid development cycle."
        )
        BaseAgent.__init__(self, "Technology Advisor Agent", instruction)

    def execute(self, project_id: str, best_idea: str, description: str, constraints: str, tech_preferences: str, api_key: str = None) -> TechAdvisorOutput:
        self.log(project_id, "Formulating custom tech stack recommendations...")
        prompt = (
            f"Project Idea: {best_idea}\n"
            f"Description: {description}\n"
            f"User Constraints: {constraints}\n"
            f"User Preferences: {tech_preferences}\n\n"
            "Formulate recommendations for frontend, backend, database, AI framework, cloud platform, and secondary APIs, and explain your choices."
        )
        
        response = self.run_llm(
            project_id=project_id,
            prompt=prompt,
            api_key=api_key,
            response_schema=TechAdvisorOutput
        )
        
        import json
        data = json.loads(response.text)
        self.log(project_id, "Technology stack recommendations generated.")
        return TechAdvisorOutput(**data)
