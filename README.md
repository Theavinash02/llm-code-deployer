LLM-Powered Automated Application Deployer
This project is an automated, API-driven application that receives a project brief, uses a Large Language Model (LLM) to generate a complete web application, and then automatically deploys it to GitHub Pages. It is designed to handle both initial project creation and subsequent revisions, creating a full CI/CD (Continuous Integration/Continuous Deployment) pipeline powered by generative AI.

## Project Overview
The core of this project is a FastAPI application hosted on Hugging Face Spaces that listens for task requests. Upon receiving a valid request, it performs the entire development and deployment lifecycle without any human intervention.

Build 🏗️: Receives a JSON request with a brief, verifies a secret, uses the Google Gemini API to generate HTML, CSS, and JavaScript code, and creates a professional README.md.

Deploy 🚀: Creates a new public repository on GitHub, commits the generated files (including an MIT LICENSE), and activates GitHub Pages to make the web application live.

Revise ✍️: Can receive a second request for the same task (round: 2), fetch the existing code, instruct the LLM to modify it based on a new brief, and redeploy the changes.

Notify 📢: After each successful deployment, it sends the repository and live page URLs back to a specified evaluation server.

## Core Features
API-Driven: Fully automated via a single POST endpoint.

AI Code Generation: Leverages Google's Gemini models to write code and documentation from natural language briefs.

Automated DevOps: Handles repository creation, file commits, and GitHub Pages deployment automatically using the GitHub API.

Secure: Uses environment variables and repository secrets to manage sensitive API keys and tokens, keeping them out of the codebase.

Scalable & Robust: Containerized with Docker and deployed on Hugging Face Spaces for consistent and reliable operation.

## Tech Stack
Backend: Python

API Framework: FastAPI

AI Model: Google Gemini (gemini-1.5-flash)

GitHub Integration: PyGithub

Hosting: Hugging Face Spaces

Containerization: Docker

Web Server: Uvicorn

## Project Structure
/
|-- app.py                # Main FastAPI server, handles requests and background tasks
|-- llm_handler.py        # Logic for interacting with the Gemini API to generate content
|-- github_handler.py     # Manages all interactions with the GitHub API
|-- utils.py              # Helper functions (e.g., for decoding attachments)
|-- requirements.txt      # List of Python dependencies
|-- Dockerfile            # Instructions for building the Docker container for deployment
|-- .env.example          # Example file for environment variables
|-- README.md             # This file
## Setup and Deployment Guide
Follow these steps to deploy your own instance of this application.

1. Clone the Repository
Bash

git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
2. Configure Secrets
This application requires three secret keys. Create a file named .env in the root of the project and add your keys.

.env file:

# A secret string to authenticate requests from the evaluation server
STUDENT_SECRET="your_super_secret_string"

# Your GitHub Personal Access Token with `repo` and `workflow` permissions
GITHUB_TOKEN="ghp_..."

# Your Google Gemini API Key from Google AI Studio
GEMINI_API_KEY="AIzaSy..."
3. Deploy to Hugging Face Spaces
The easiest way to run this application is to deploy it on a free Hugging Face Space.

Create a New Space: Go to Hugging Face and create a New Space.

Set SDK: Select Docker as the Space SDK and choose the Blank template.

Upload Files: Upload all the project files (including the Dockerfile) to the new Space repository.

Add Secrets: In your Space's Settings tab, go to Repository secrets and add the three secrets from your .env file (STUDENT_SECRET, GITHUB_TOKEN, and GEMINI_API_KEY). Do not upload the .env file itself.

Hugging Face will automatically build the Docker image and start the application. Your API will be live at https://YOUR_HF_USERNAME-YOUR_SPACE_NAME.hf.space.

## Usage
To trigger the application, send an HTTP POST request to the /api-endpoint URL of your running application.

Endpoint: https://YOUR_HF_USERNAME-YOUR_SPACE_NAME.hf.space/api-endpoint

Method: POST

Body (JSON):

JSON

{
  "email": "student@example.com",
  "secret": "your_super_secret_string",
  "task": "unique-task-name-12345",
  "round": 1,
  "nonce": "a-unique-identifier-for-this-request",
  "brief": "Create a simple webpage with a single button that says 'Click Me'. When clicked, it should show an alert that says 'Hello, World!'.",
  "checks": [
    "Button exists",
    "Alert shows on click"
  ],
  "evaluation_url": "https://instructor-server.com/notify",
  "attachments": []
}
The application will immediately respond with a 200 OK message and begin the build/deployment process in the background.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.