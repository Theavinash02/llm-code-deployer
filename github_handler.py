import os
import time
from github import Github, GithubException

# Initialize the GitHub client using the token from environment variables
g = Github(os.getenv("GITHUB_TOKEN"))
github_user = g.get_user()

MIT_LICENSE = """
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The foregoing copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

def create_or_get_repo(repo_name):
    """Creates a new public GitHub repo or gets it if it already exists for Round 2."""
    try:
        print(f"Creating new repository: {repo_name}")
        repo = github_user.create_repo(repo_name, private=False)
        time.sleep(2) # Brief pause to ensure repo is ready
        return repo
    except GithubException as e:
        if e.status == 422: # Repository already exists
            print(f"Repository {repo_name} already exists. Fetching it.")
            return g.get_repo(f"{github_user.login}/{repo_name}")
        else:
            raise e

def get_file_content(repo, file_path):
    """Gets the content of a file from a repo, used for Round 2 revisions."""
    try:
        file_content = repo.get_contents(file_path, ref=repo.default_branch)
        return file_content.decoded_content.decode('utf-8')
    except GithubException:
        return None # File not found

def update_repo_files(repo, files_to_commit, round_num):
    """Creates or updates files in the repo and returns the commit SHA."""
    commit_message = f"feat: Round {round_num} - initial project setup"
    if round_num > 1:
        commit_message = f"feat: Round {round_num} - revision based on new brief"

    # Check if the repo is empty to decide commit strategy
    try:
        repo.get_contents("/")
        # If not empty, we need to get the latest commit to build on top of
        master_ref = repo.get_git_ref(f'heads/{repo.default_branch}')
        master_sha = master_ref.object.sha
        base_tree = repo.get_git_tree(master_sha)

        element_list = [
            {'path': path, 'mode': '100644', 'type': 'blob', 'content': content}
            for path, content in files_to_commit.items()
        ]
        
        tree = repo.create_git_tree(element_list, base_tree)
        parent = repo.get_git_commit(master_sha)
        commit = repo.create_git_commit(commit_message, tree, [parent])
        master_ref.edit(commit.sha)

    except GithubException: # Repo is empty
        for path, content in files_to_commit.items():
            repo.create_file(path, f"init: create {path}", content, branch=repo.default_branch)
        commit = repo.get_commits().get_page(0)[0] # Get the latest commit

    print(f"Successfully committed changes. SHA: {commit.sha}")
    return commit.sha

def enable_github_pages(repo):
    """Enables GitHub Pages for the repository and returns the URL."""
    try:
        repo.create_pages_site(source={'branch': repo.default_branch, 'path': '/'})
        print("GitHub Pages enabled. It may take a minute to deploy.")
    except GithubException as e:
        if "already has a GitHub Pages site" in str(e.data.get('message', '')):
            print("GitHub Pages is already enabled.")
        else:
            print(f"Error enabling GitHub Pages: {e}")
            raise e

    pages_url = f"https://{github_user.login}.github.io/{repo.name}/"
    return pages_url

def deploy_project(task_id, files, round_num):
    """Full workflow: create repo, push files, enable pages, and return details."""
    repo = create_or_get_repo(task_id)

    # Add MIT license with the user's name
    files['LICENSE'] = MIT_LICENSE.replace("Your Name", github_user.name or github_user.login)

    commit_sha = update_repo_files(repo, files, round_num)
    pages_url = enable_github_pages(repo)
    
    print("Waiting 30 seconds for GitHub Pages to build...")
    time.sleep(30) 

    return {
        "repo_url": repo.html_url,
        "commit_sha": commit_sha,
        "pages_url": pages_url
    }