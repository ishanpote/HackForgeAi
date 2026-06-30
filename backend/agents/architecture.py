from pydantic import BaseModel, Field
from backend.agents.base_agent import BaseAgent

class ArchitectureOutput(BaseModel):
    architecture_overview: str = Field(description="High-level description of the system architecture design pattern")
    mermaid_diagram: str = Field(description="Valid Mermaid.js diagram markup (e.g. using `graph TD` or similar) illustrating the architecture components and connections")
    data_flow_explanation: str = Field(description="Step-by-step documentation of user request inputs and responses traversing the system")
    ai_workflow_explanation: str = Field(description="Explanation of how the AI model (Gemini, vector stores, prompt routing) behaves within the system")

class SystemArchitectureAgent(BaseModel, BaseAgent):
    class Config:
        arbitrary_types_allowed = True
        
    def __init__(self):
        instruction = (
            "You are the System Architecture Agent of HackForge AI. Your responsibility is to design a robust, "
            "production-grade system architecture for the selected project. You must output a valid Mermaid.js "
            "diagram that depicts the client, server, database, external APIs, and AI models. Explain the data flow "
            "and detail the AI agents/LLM workflow. Ensure the Mermaid code is clean, syntax-error-free, and contains "
            "no markdown surrounding it inside the JSON field. DO NOT use brackets inside Mermaid labels unless quoted (e.g., id1[\"Label (Details)\"])."
        )
        BaseAgent.__init__(self, "System Architecture Agent", instruction)

    def execute(self, project_id: str, best_idea: str, description: str, tech_stack: str, api_key: str = None) -> ArchitectureOutput:
        self.log(project_id, "Designing architecture and rendering Mermaid diagram...")
        prompt = (
            f"Project Idea: {best_idea}\n"
            f"Description: {description}\n"
            f"Technology Stack Summary: {tech_stack}\n\n"
            "Generate a complete software architecture report. Ensure the mermaid_diagram field contains valid, compile-ready Mermaid code."
        )
        
        response = self.run_llm(
            project_id=project_id,
            prompt=prompt,
            api_key=api_key,
            response_schema=ArchitectureOutput
        )
        
        import json
        data = json.loads(response.text)
        self.log(project_id, "System architecture designed.")
        return ArchitectureOutput(**data)
