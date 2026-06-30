from fastapi import FastAPI, BackgroundTasks, Header, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import uvicorn

# Load .env file automatically if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional — env vars may already be set in the environment

from backend.db.db_manager import (
    init_db,
    create_project,
    get_project,
    list_projects,
    delete_project
)
from backend.orchestration.workflow import run_workflow

# Initialize FastAPI App
app = FastAPI(title="HackForge AI API", description="AI-powered hackathon project co-pilot")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Pydantic Schemas for inputs
class ProjectCreateRequest(BaseModel):
    name: Optional[str] = ""
    theme: Optional[str] = ""
    problem_statement: str
    constraints: Optional[str] = ""
    tech_preferences: Optional[str] = ""

class ProjectListResponse(BaseModel):
    id: str
    name: str
    theme: str
    problem_statement: str
    status: str
    created_at: str
    summary: Optional[str] = ""

# API Endpoints
@app.get("/")
def read_root():
    return RedirectResponse(url="/static/index.html")

@app.post("/api/projects", status_code=status.HTTP_201_CREATED)
def forge_project(
    request: ProjectCreateRequest, 
    background_tasks: BackgroundTasks, 
    x_gemini_key: Optional[str] = Header(None)
):
    if not request.problem_statement.strip():
        raise HTTPException(status_code=400, detail="Problem statement is required.")
    
    # 1. Create entry in DB
    project_id = create_project(
        name=request.name or "Untitled Hack",
        theme=request.theme or "General",
        problem_statement=request.problem_statement,
        constraints=request.constraints or "None",
        tech_preferences=request.tech_preferences or "No preference",
    )
    
    # 2. Add workflow to FastAPI background tasks
    # We pass the custom gemini key if supplied in headers, otherwise it defaults to None (env fallback)
    background_tasks.add_task(
        run_workflow,
        project_id,
        request.name or "Untitled Hack",
        request.theme or "General",
        request.problem_statement,
        request.constraints or "None",
        request.tech_preferences or "No preference",
        x_gemini_key
    )
    
    return {"project_id": project_id, "status": "PENDING"}

@app.get("/api/projects", response_model=List[ProjectListResponse])
def get_all_projects():
    return list_projects()

@app.get("/api/projects/{project_id}")
def get_project_details(project_id: str):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project blueprint not found.")
    return project

@app.delete("/api/projects/{project_id}")
def delete_project_entry(project_id: str):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project blueprint not found.")
    delete_project(project_id)
    return {"status": "SUCCESS", "message": "Project blueprint deleted successfully."}

# Mount static directory. Crucial: StaticFiles must be mounted AFTER routes to avoid route shadowing.
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
    
app.mount("/static", StaticFiles(directory=static_dir), name="static")

if __name__ == "__main__":
    # Start web server on port 8000
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
