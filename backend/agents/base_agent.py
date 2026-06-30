from google import genai
from google.genai import types
from backend.db.db_manager import add_project_log
import os
import json
import traceback

class BaseAgent:
    def __init__(self, name: str, instruction: str):
        self.name = name
        self.instruction = instruction
        
    def get_client(self, api_key: str = None):
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise ValueError("Gemini API Key is not set. Please set it in Settings.")
        return genai.Client(api_key=key)

    def log(self, project_id: str, message: str):
        print(f"[{self.name}] {message}")
        if project_id:
            try:
                add_project_log(project_id, self.name, message)
            except Exception as e:
                print(f"Database logging failed: {e}")

    def run_llm(self, project_id: str, prompt: str, api_key: str = None, response_schema = None, google_search: bool = False):
        """
        Run a Gemini LLM call.
        
        IMPORTANT: Gemini API does NOT support simultaneous use of Google Search grounding 
        (tool use) and structured JSON output (response_mime_type=application/json). 
        When google_search=True, we do a two-pass approach:
          Pass 1 — Grounded text search (free-form response with real search results)
          Pass 2 — Structured JSON extraction from the grounded text
        """
        try:
            self.log(project_id, "Preparing model configuration...")
            client = self.get_client(api_key)
            
            # Using gemini-2.5-flash as the default fast and capable model
            model_name = "gemini-2.5-flash"
            
            if google_search and response_schema:
                # ─── TWO-PASS APPROACH ────────────────────────────────────────
                # Pass 1: Grounded web search — free text, no JSON schema
                self.log(project_id, "Pass 1: Enabling Google Search grounding for research...")
                search_config = types.GenerateContentConfig(
                    system_instruction=self.instruction,
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.7,
                )
                self.log(project_id, f"Executing grounded search using model {model_name}...")
                grounded_response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=search_config
                )
                grounded_text = grounded_response.text
                self.log(project_id, "Pass 1 complete. Grounded research retrieved.")

                # Pass 2: Structure the grounded text into JSON schema
                self.log(project_id, "Pass 2: Structuring grounded research into JSON format...")
                schema_name = response_schema.__name__ if hasattr(response_schema, "__name__") else "output"
                structure_prompt = (
                    f"You have retrieved the following research data:\n\n{grounded_text}\n\n"
                    f"Now extract and structure this information into the required JSON format. "
                    f"Return ONLY valid JSON conforming to the {schema_name} schema. Do not add commentary."
                )
                struct_config = types.GenerateContentConfig(
                    system_instruction=self.instruction,
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                )
                final_response = client.models.generate_content(
                    model=model_name,
                    contents=structure_prompt,
                    config=struct_config
                )
                self.log(project_id, "Pass 2 complete. Structured JSON output generated.")
                return final_response
                # ──────────────────────────────────────────────────────────────
                
            elif google_search:
                # Search only, no schema — return grounded text response directly
                self.log(project_id, "Enabling Google Search grounding (no schema)...")
                config = types.GenerateContentConfig(
                    system_instruction=self.instruction,
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.7,
                )
                self.log(project_id, f"Executing grounded search using model {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
                self.log(project_id, "LLM successfully responded.")
                return response
                
            else:
                # Standard call — structured JSON output, no search tools
                config = types.GenerateContentConfig(
                    system_instruction=self.instruction,
                    temperature=0.7,
                )
                if response_schema:
                    config.response_mime_type = "application/json"
                    config.response_schema = response_schema
                    
                self.log(project_id, f"Executing LLM prompt using model {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
                self.log(project_id, "LLM successfully responded.")
                return response
                
        except Exception as e:
            err_msg = f"Error during execution: {str(e)}\n{traceback.format_exc()}"
            self.log(project_id, f"CRITICAL ERROR: {err_msg}")
            raise e
