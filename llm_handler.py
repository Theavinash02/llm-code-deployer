import os
import google.generativeai as genai

# Configure the Gemini API key from environment variables
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_app_code(brief, existing_code=None):
    """Generates application code (HTML/JS/CSS) based on a brief using an LLM."""
    model = genai.GenerativeModel('gemini-2.5-flash') # Or your working model
    
    # --- THIS IS THE UPDATED PROMPT ---
    prompt = f"""
    You are an expert web developer building a single-page web application in one index.html file.
    Use inline CSS and inline JavaScript. Do not use external files unless explicitly asked for (e.g., CDN links).

    IMPORTANT: If the brief mentions attachments (like .csv or .json data), you MUST embed the content of those attachments directly into a JavaScript variable within the <script> tag. Do NOT generate code that uses fetch() to load local files, as they will not exist on the server.

    BRIEF: "{brief}"
    """

    # If it's a revision request, add the existing code for context
    if existing_code:
        prompt += f"""
        This is a revision request. Modify the following existing code based on the new brief:
        --- EXISTING CODE ---
        {existing_code}
        --- END OF EXISTING CODE ---

        Return only the complete, updated index.html file content. Do not add any explanations.
        """
    else:
        prompt += "Return only the complete index.html file content. Do not include any other text or explanations."

    print("Sending prompt to LLM to generate app code...")
    response = model.generate_content(prompt)
    
    # Clean the LLM response to ensure only code is returned
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