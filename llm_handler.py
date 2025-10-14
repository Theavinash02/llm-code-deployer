import os
import google.generativeai as genai

# Configure the Gemini API key from environment variables
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_app_code(brief, existing_code=None):
    """Generates application code (HTML/JS/CSS) based on a brief using an LLM."""
    model = genai.GenerativeModel('gemini-2.5-flash') # Or your working model
    
    # --- THIS IS THE UPDATED PROMPT ---
    # --- THIS IS THE NEW, HYPER-DETAILED PROMPT ---
    prompt = f"""
    You are an expert full stack developer creating a single, self-contained index.html file based on the task provided.
    Analyze the user's brief with extreme care and follow these rules precisely.

    **CRITICAL DEVELOPMENT RULES:**
    1.  **HTML Structure:** If the brief mentions specific HTML element IDs (e.g., `#markdown-output`, `#markdown-tabs`), you MUST create those exact elements with those exact `id` attributes. This is non-negotiable.
    2.  **External Libraries:** If the brief mentions loading external libraries from a CDN (e.g., 'marked', 'highlight.js', 'bootstrap'), you MUST include a `<script>` or `<link>` tag for EACH ONE in the `<head>` section. Do not miss any.
    3.  **JavaScript Logic:** You must write all necessary JavaScript to fulfill the brief's requirements. If it requires converting Markdown, create the logic. If it requires creating tabs, write the event listeners for the buttons.
    4.  **Self-Contained Code:** All HTML, CSS, and JavaScript must be in one file. Do not use `fetch()` for local files like 'input.md'; embed any provided data directly into a JavaScript variable.

    **USER BRIEF:**
    ---
    {brief}
    ---
    """

    if existing_code:
        prompt += f"""
        This is a revision request. Update the following code based on the new USER BRIEF and all the CRITICAL DEVELOPMENT RULES above.
        --- EXISTING CODE ---
        {existing_code}
        --- END OF EXISTING CODE ---
        Return only the complete, updated index.html file content.
        """
    else:
        prompt += "Return only the complete index.html file content. Do not add explanations."

    print("Sending hyper-detailed prompt to LLM...")
    response = model.generate_content(prompt)
    
    generated_text = response.text.strip()
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