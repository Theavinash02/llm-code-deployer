import os
import google.generativeai as genai

# Configure the Gemini API key from environment variables
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_app_code(brief, existing_code=None):
    """Generates application code (HTML/JS/CSS) based on a brief using an LLM."""
    model = genai.GenerativeModel('gemini-1.5-flash') # Using the model you specified

    # --- THIS IS THE NEW, HIGH-PRECISION PROMPT ---
    prompt = f"""
    You are a meticulous, senior full-stack developer tasked with creating a flawless, single-page web application in a single `index.html` file.
    Your work will be automatically graded by a testing script that executes JavaScript checks against the live webpage. Absolute precision is required to pass. Any deviation from the brief will result in failure.

    **CRITICAL REQUIREMENTS (NON-NEGOTIABLE):**

    1.  **HTML Element IDs:** If the brief specifies an HTML element with an ID (e.g., `#github-created-at`, `#markdown-source`), you MUST create that exact element with that exact `id` attribute. This is the most common reason for failure. Double-check every required ID.

    2.  **External Libraries:** If the brief mentions loading external libraries from a CDN (e.g., 'marked.js', 'highlight.js', 'bootstrap'), you MUST include a `<script>` or `<link>` tag in the `<head>` section for EVERY library mentioned. Do not omit any.

    3.  **Data Handling:** If the brief provides data in an attachment (like CSV or JSON content), you MUST embed this data directly into a JavaScript variable (e.g., `const csvData = \`...\`;`). DO NOT write code that tries to `fetch()` a local file, as it will not exist and will cause an immediate failure.

    4.  **Functional Logic:** You MUST write all necessary JavaScript logic to fully implement the brief's requirements.
        - If a sum needs to be calculated, perform the calculation and display it in the correct element.
        - If an API call is needed (e.g., to `api.github.com`), write the complete `fetch` request, handle the JSON response, and correctly display the required data in the specified element.
        - If UI elements like tabs or buttons are required, you must write the JavaScript event listeners (`.addEventListener`) to make them functional.

    **SELF-CORRECTION CHECKLIST:**
    Before you output the final code, you must mentally review this checklist against your generated code:
    - Did I include EVERY required HTML element with the EXACT `id` specified in the brief?
    - Did I include a `<script>` or `<link>` tag for EVERY required CDN library?
    - Is all data from attachments EMBEDDED directly in a JavaScript variable?
    - Is all functionality (calculations, API calls, event listeners) fully implemented and correct?

    **USER BRIEF:**
    ---
    {brief}
    ---
    """

    if existing_code:
        prompt += f"""
        This is a revision request. Update the following code based on the new USER BRIEF. You must adhere to all the CRITICAL REQUIREMENTS and run through the SELF-CORRECTION CHECKLIST.
        --- EXISTING CODE ---
        {existing_code}
        --- END OF EXISTING CODE ---
        Return only the complete, updated and corrected index.html file content.
        """
    else:
        prompt += "Return only the complete, final index.html file content. Do not add explanations or markdown formatting."

    print("Sending high-precision prompt to LLM...")
    response = model.generate_content(prompt)
    
    generated_text = response.text.strip()
    
    if '```html' in generated_text:
        generated_text = generated_text.split('```html')[1].split('```')[0]
        
    return generated_text.strip()
    if '```html' in generated_text:
        generated_text = generated_text.split('```html')[1].split('```')[0]
        
    return generated_text.strip()


def generate_readme(brief, code):
    """Generates a professional README.md file content."""
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are a technical writer. Create a professional README.md for a GitHub repository.
    The brief for the project was: "{brief}"
    
    The README should include these sections:
    - A project title.
    - A summary of what the application does.
    - Setup instructions (e.g., "Just open the index.html file in a browser").
    - A brief explanation of the code.
    - A "License" section mentioning it is under the MIT License.

    Return only the complete README.md content.
    """
    print("Generating README...")
    response = model.generate_content(prompt)
    return response.text.strip()