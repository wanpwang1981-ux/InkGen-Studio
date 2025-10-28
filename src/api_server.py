# -*- coding: utf-8 -*-
"""
InkGen Studio - API Server
==========================

This module provides a web server interface for the InkGen Studio application,
exposing its functionalities through a RESTful API using FastAPI.

This allows for integration with web frontends or other services.

To run the server, use the following command from the project root:
uvicorn src.api_server:app --reload

Author: Jules
Date: 2025-09-30
Version: 1.3 (Full API)
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, Field
from typing import List, Optional, Any
import uuid
import os
import re

from orchestrator import Orchestrator

# --- FastAPI App Initialization ---
app = FastAPI(
    title="InkGen Studio API",
    description="API for orchestrating AI-powered novel generation.",
    version="1.0.0"
)

# --- Global Instances ---
orchestrator = Orchestrator()
# In-memory task store. For production, use a more robust solution like Redis or Celery.
tasks = {}

# --- API Models (Data Contracts) ---

class PersonaCreateRequest(BaseModel):
    author_name: str
    sample_paths: List[str]
    output_path: str
    extra_materials_path: Optional[str] = None

class PersonaCreateResponse(BaseModel):
    message: str
    persona_path: str

class OutlineCreateRequest(BaseModel):
    title: str
    output_path: str
    chapters: int = 10
    persona_path: Optional[str] = None

class OutlineCreateResponse(BaseModel):
    message: str
    outline_path: str

class ProjectInitRequest(BaseModel):
    title: str
    outline_path: str
    persona_path: Optional[str] = None
    output_dir: str = "novels/"

class ProjectInitResponse(BaseModel):
    message: str
    project_path: str

class GenerateNovelRequest(BaseModel):
    project_path: str
    max_revisions: int = 2

class TaskCreationResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None

# --- Background Task Runner ---

def run_generation_task(task_id: str, project_path: str, max_revisions: int):
    """A wrapper function to run the orchestrator's method and update task status."""
    tasks[task_id]["status"] = "running"
    try:
        orchestrator.run_generate_novel(project_path=project_path, max_revisions=max_revisions)
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = f"Novel generation for project '{project_path}' completed successfully."
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["result"] = f"An error occurred: {str(e)}"

# --- API Endpoints ---

@app.get("/", tags=["Status"])
async def read_root():
    """Root endpoint to check if the server is running."""
    return {"message": "Welcome to InkGen Studio API. The AI writing team is ready."}

@app.post("/personas/create", response_model=PersonaCreateResponse, status_code=status.HTTP_201_CREATED, tags=["Content Creation"])
async def create_persona_endpoint(request: PersonaCreateRequest):
    """Creates a new writer persona profile from sample texts."""
    for path in request.sample_paths:
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail=f"Sample file not found: {path}")
    if request.extra_materials_path and not os.path.exists(request.extra_materials_path):
        raise HTTPException(status_code=404, detail=f"Extra materials file not found: {request.extra_materials_path}")

    try:
        orchestrator.run_create_persona(**request.dict())
        return {"message": "Persona created successfully.", "persona_path": request.output_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/outlines/create", response_model=OutlineCreateResponse, status_code=status.HTTP_201_CREATED, tags=["Content Creation"])
async def create_outline_endpoint(request: OutlineCreateRequest):
    """Creates a new novel outline from a title and optional persona."""
    if request.persona_path and not os.path.exists(request.persona_path):
        raise HTTPException(status_code=404, detail=f"Persona file not found: {request.persona_path}")

    try:
        orchestrator.run_create_outline(**request.dict())
        return {"message": "Outline created successfully.", "outline_path": request.output_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/projects/init", response_model=ProjectInitResponse, status_code=status.HTTP_201_CREATED, tags=["Project Management"])
async def init_project_endpoint(request: ProjectInitRequest):
    """Initializes a new novel project directory and its configuration file."""
    if not os.path.exists(request.outline_path):
        raise HTTPException(status_code=404, detail=f"Outline file not found: {request.outline_path}")
    if request.persona_path and not os.path.exists(request.persona_path):
        raise HTTPException(status_code=404, detail=f"Persona file not found: {request.persona_path}")

    try:
        safe_title = re.sub(r'[^\w\s-]', '', request.title).strip().replace(' ', '_')
        project_dir = os.path.join(request.output_dir, safe_title)
        if os.path.exists(project_dir):
            raise HTTPException(status_code=409, detail=f"Project directory '{project_dir}' already exists.")

        orchestrator.run_init_project(
            title=request.title,
            outline_path=request.outline_path,
            persona_path=request.persona_path,
            output_dir_base=request.output_dir
        )

        return {"message": "Project initialized successfully.", "project_path": project_dir}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/projects/generate", response_model=TaskCreationResponse, status_code=status.HTTP_202_ACCEPTED, tags=["Project Management"])
async def generate_novel_endpoint(request: GenerateNovelRequest, background_tasks: BackgroundTasks):
    """Starts a background task to generate a full novel from a project."""
    project_path = request.project_path
    if not os.path.exists(project_path) or not os.path.isdir(project_path) or not os.path.exists(os.path.join(project_path, "project.json")):
        raise HTTPException(status_code=404, detail=f"Project directory '{project_path}' is not valid or does not contain a project.json file.")

    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "pending", "result": None}

    background_tasks.add_task(run_generation_task, task_id, project_path, request.max_revisions)

    return {"task_id": task_id, "status": "pending", "message": "Novel generation task has been accepted and is running in the background."}

@app.get("/tasks/{task_id}", response_model=TaskStatusResponse, tags=["Task Management"])
async def get_task_status(task_id: str):
    """Retrieves the status of a background task."""
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatusResponse(task_id=task_id, status=task["status"], result=task["result"])