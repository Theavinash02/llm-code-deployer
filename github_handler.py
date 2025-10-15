import os
import time
from github import Github, GithubException, BadCredentialsException, InputGitTreeElement

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
    commit_message = f"feat: Round {round_num} - project setup"
    if round_num > 1:
        commit_message = f"feat: Round {round_num} - revision based on new brief"

    # Get the main branch reference
    main_ref = repo.get_git_ref(f'heads/{repo.default_branch}')

    # Get the latest commit to build on top of
    try:
        latest_commit = repo.get_git_commit(main_ref.object.sha)
        base_tree = latest_commit.tree
    except GithubException: # This happens if the repo is brand new and empty
        latest_commit = None
        base_tree = None

    # Create blobs for all files
    blobs = {path: repo.create_git_blob(content, "utf-8") for path, content in files_to_commit.items()}

    tree_elements = [
        InputGitTreeElement(path=path, mode='100644', type='blob', sha=blob.sha)
        for path, blob in blobs.items()
    ]

    # Create a new tree
    new_tree = repo.create_git_tree(tree_elements, base_tree)

    # Create the commit
    parents = [latest_commit] if latest_commit else []
    commit = repo.create_git_commit(commit_message, new_tree, parents)

    # Update the branch to point to the new commit
    main_ref.edit(commit.sha)

    print(f"Successfully committed changes. SHA: {commit.sha}")
    return commit.sha

def enable_github_pages(repo):
    """Enables GitHub Pages for the repository and returns the URL."""
    try:
        source = {"source": {"branch": repo.default_branch, "path": "/"}}
        headers = {'Accept': 'application/vnd.github.v3+json'}
        repo._requester.requestJsonAndCheck("POST", repo.url + "/pages", input=source, headers=headers)
        print("GitHub Pages site created. It may take a minute to deploy.")
    except GithubException as e:
        if e.status == 409:
            print("GitHub Pages is already enabled.")
        else:
            print(f"An unexpected error occurred while enabling GitHub Pages: {e}")
            raise e

    pages_url = f"https://{github_user.login}.github.io/{repo.name}/"
    return pages_url

def deploy_project(task_id, files, round_num):
    """Full workflow: create repo, push files, enable pages, and return details."""
    repo = create_or_get_repo(task_id)

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