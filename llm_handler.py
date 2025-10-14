import os
import google.generativeai as genai

# Configure the Gemini API key from environment variables
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_app_code(brief, existing_code=None):
    """Generates application code (HTML/JS/CSS) based on a brief using an LLM."""
    model = genai.GenerativeModel('gemini-2.5-flash') # Or your working model
    
    # --- THIS IS THE UPDATED PROMPT ---
    prompt = f"""
    You are an expert web developer. Your task is to build a complete, single-page web application in a single index.html file.

    **CRITICAL RULES:**
    1.  **Element IDs:** Pay extremely close attention to `id` attributes mentioned in the brief (e.g., `#github-created-at`). The generated HTML elements MUST have these exact IDs for the evaluation to pass.
    2.  **API Calls:** If the brief requires fetching data from an API (like the GitHub API), you MUST write the complete JavaScript `fetch` call and the logic to handle the response.
    3.  **Content Display:** Ensure the data retrieved from any API call is correctly placed into the specified HTML elements.
    4.  **Self-Contained:** All HTML, CSS, and JavaScript must be in a single `index.html` file.

    **BRIEF:** "{brief}"
    """

    if existing_code:
        prompt += f"""
        This is a revision request. Modify the following existing code based on the new brief and all the critical rules above:
        --- EXISTING CODE ---
        {existing_code}
        --- END OF EXISTING CODE ---

        Return only the complete, updated index.html file content. Do not add any explanations.
        """
    else:
        prompt += "Return only the complete index.html file content. Do not include any other text or explanations."

    print("Sending detailed prompt to LLM to generate app code...")
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