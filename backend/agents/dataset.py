from pydantic import BaseModel, Field
from typing import List
from backend.agents.base_agent import BaseAgent

class PublicDataset(BaseModel):
    name: str = Field(description="Name of the public dataset")
    source: str = Field(description="Platform where it is hosted (e.g. Kaggle, Hugging Face, UCI, AWS Open Data)")
    description: str = Field(description="Detailed explanation of the dataset content")
    usefulness: str = Field(description="How this dataset will be utilized in our hackathon project")
    recommended_url: str = Field(description="Search link or exact source URL for the dataset")

class AlternativeAPI(BaseModel):
    name: str = Field(description="Name of the external API")
    provider: str = Field(description="API Provider or Host")
    purpose: str = Field(description="What data or service this API provides")
    usefulness: str = Field(description="How this API compensates for lack of static datasets")

class DatasetOutput(BaseModel):
    datasets: List[PublicDataset] = Field(description="At least 2 relevant open-source datasets")
    alternative_apis: List[AlternativeAPI] = Field(description="At least 2 developer APIs to ingest real-time data")

class DatasetDiscoveryAgent(BaseModel, BaseAgent):
    class Config:
        arbitrary_types_allowed = True
        
    def __init__(self):
        instruction = (
            "You are the Dataset Discovery Agent of HackForge AI. Your role is to identify and recommend "
            "relevant open-source datasets (from Kaggle, Hugging Face, etc.) that can be used for training models, "
            "seeding databases, or testing the selected project idea. If datasets are scarce, you must recommend "
            "specific developer APIs or public web scraping targets that can supply the necessary data. Explain "
            "how each dataset and API should be integrated."
        )
        BaseAgent.__init__(self, "Dataset Discovery Agent", instruction)

    def execute(self, project_id: str, best_idea: str, description: str, api_key: str = None) -> DatasetOutput:
        self.log(project_id, "Searching for relevant datasets and developer APIs...")
        prompt = (
            f"Selected Project Idea: {best_idea}\n"
            f"Project Description: {description}\n\n"
            "Search for or identify at least 2 datasets and 2 alternative APIs. Outline how they can be used."
        )
        
        # We also enable search grounding here to find actual datasets and URLs!
        response = self.run_llm(
            project_id=project_id,
            prompt=prompt,
            api_key=api_key,
            response_schema=DatasetOutput,
            google_search=True
        )
        
        import json
        data = json.loads(response.text)
        self.log(project_id, "Dataset discovery completed.")
        return DatasetOutput(**data)
