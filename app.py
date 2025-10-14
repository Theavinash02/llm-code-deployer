import os
import requests
import time
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from dotenv import load_dotenv

from utils import decode_attachment
from llm_handler import generate_app_code, generate_readme
from github_handler import deploy_project, create_or_get_repo, get_file_content

load_dotenv()
app = FastAPI()
STUDENT_SECRET = os.getenv("STUDENT_SECRET")

# --- Pydantic Models for automatic request validation ---
class Attachment(BaseModel):
    name: str
    url: str

class TaskRequest(BaseModel):
    email: str
    secret: str
    task: str
    round: int
    nonce: str
    brief: str
    checks: List[str]
    evaluation_url: HttpUrl
    attachments: Optional[List[Attachment]] = None

# --- Background Task Processing Logic ---
def process_task(data: TaskRequest):
    """The main function to handle the build and deploy process."""
    print(f"Processing task: {data.task} (Round {data.round})")
    brief = data.brief
    
    if data.attachments:
        for att in data.attachments:
            decoded = decode_attachment(att.dict())
            if decoded:
                brief += f"\n\n--- Attachment: {decoded['name']} ---\n{decoded['content']}"

    code_to_update = None
    if data.round > 1:
        repo = create_or_get_repo(data.task)
        code_to_update = get_file_content(repo, 'index.html')
        if not code_to_update:
            print("Warning: Could not fetch existing code for round 2.")

    app_code = generate_app_code(brief, existing_code=code_to_update)
    if not app_code:
        print("Error: LLM failed to generate code."); return

    readme_content = generate_readme(brief, app_code)
    
    files_to_commit = {'index.html': app_code, 'README.md': readme_content}
    repo_details = deploy_project(data.task, files_to_commit, data.round)

    payload = {
        "email": data.email, "task": data.task, "round": data.round,
        "nonce": data.nonce, "repo_url": repo_details['repo_url'],
        "commit_sha": repo_details['commit_sha'], "pages_url": repo_details['pages_url'],
    }
    
    notify_evaluation(str(data.evaluation_url), payload)

def notify_evaluation(url: str, payload: dict):
    """Sends a POST request to the evaluation URL with exponential backoff retries."""
    max_retries, delay = 5, 1
    for i in range(max_retries):
        try:
            print(f"Notifying evaluation server at {url}...")
            response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
            if response.status_code == 200:
                print("Notification successful!"); return
            else:
                print(f"Attempt {i+1} failed with status {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Attempt {i+1} failed with exception: {e}")
        
        if i < max_retries - 1:
            print(f"Retrying in {delay} seconds..."); time.sleep(delay); delay *= 2
    
    print("Failed to notify evaluation server after all retries.")

# --- API Endpoint ---
@app.post("/api-endpoint")
async def handle_request(task_request: TaskRequest, background_tasks: BackgroundTasks):
    """API endpoint to receive, validate, and process task requests."""
    if task_request.secret != STUDENT_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid secret")
    
    background_tasks.add_task(process_task, task_request)
    
    return {"message": "Request received and is being processed."}

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API is running. Send POST requests to /api-endpoint"}