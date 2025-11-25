"""
CV Digital Twin MCP Server
Takes a CV PDF as input and behaves like a digital twin, answering questions about the person.
"""

import os
from pathlib import Path
from typing import Optional
import json

from fastmcp import FastMCP

# Load .env file if it exists
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value

# Try importing OpenAI
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    OpenAI = None

# Try importing PDF libraries
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

# Create server
mcp = FastMCP("CV Digital Twin Server")

# Global storage for CV content
cv_content: Optional[str] = None
cv_metadata: dict = {}

# OpenAI configuration
openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5-mini-2025-08-07")
openai_client: Optional[OpenAI] = None


def get_openai_client() -> OpenAI:
    """Get or create OpenAI client."""
    global openai_client
    
    if not HAS_OPENAI:
        raise ImportError(
            "OpenAI library not installed. Please install it:\n"
            "  pip install openai"
        )
    
    if openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Please set it with: export OPENAI_API_KEY='your-api-key'"
            )
        openai_client = OpenAI(api_key=api_key)
    
    return openai_client


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    text = ""
    
    if HAS_PDFPLUMBER:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pages_text = []
                for page in pdf.pages:
                    pages_text.append(page.extract_text() or "")
                text = "\n\n".join(pages_text)
                return text
        except Exception as e:
            print(f"Error with pdfplumber: {e}")
    
    if HAS_PYPDF2:
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pages_text = []
                for page in pdf_reader.pages:
                    pages_text.append(page.extract_text())
                text = "\n\n".join(pages_text)
                return text
        except Exception as e:
            print(f"Error with PyPDF2: {e}")
    
    raise ImportError(
        "No PDF library available. Please install pdfplumber or PyPDF2:\n"
        "  pip install pdfplumber\n"
        "  or\n"
        "  pip install PyPDF2"
    )


def find_cv_in_docs() -> Optional[str]:
    """Try to find CV PDF in docs directory."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    docs_dir = script_dir / "docs"
    
    if not docs_dir.exists():
        return None
    
    # Look for common CV file names
    cv_names = ["CV.pdf", "cv.pdf", "resume.pdf", "Resume.pdf", "CV.pdf"]
    
    for cv_name in cv_names:
        cv_path = docs_dir / cv_name
        if cv_path.exists():
            return str(cv_path)
    
    # If no standard name found, look for any PDF in docs
    pdf_files = list(docs_dir.glob("*.pdf"))
    if pdf_files:
        return str(pdf_files[0])
    
    return None


def load_cv(pdf_path: str) -> None:
    """Load and parse CV from PDF file."""
    global cv_content, cv_metadata
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"CV file not found: {pdf_path}")
    
    print(f"Loading CV from: {pdf_path}")
    cv_content = extract_text_from_pdf(pdf_path)
    
    cv_metadata = {
        "file_path": pdf_path,
        "file_name": os.path.basename(pdf_path),
        "content_length": len(cv_content),
        "loaded": True
    }


def _chat_with_me_impl(message: str, cv_path: Optional[str] = None) -> str:
    """
    Chat with the digital twin based on your CV.
    If a CV path is provided and no CV is loaded, it will load the CV first.
    Then answers your question or message using OpenAI based on the CV content.
    
    Args:
        message: Your message or question (e.g., "What is your work experience?", 
                 "Tell me about yourself", "What are your skills?")
        cv_path: Optional path to CV PDF file. If not provided, will automatically 
                 look for CV.pdf in the docs/ directory.
        
    Returns:
        Response from the digital twin based on CV content
    """
    global cv_content, cv_metadata
    
    # Load CV if path provided and CV not already loaded
    if cv_path:
        try:
            load_cv(cv_path)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Failed to load CV: {str(e)}"
            }, indent=2)
    
    # If CV not loaded, try to find it in docs directory
    if cv_content is None:
        auto_cv_path = find_cv_in_docs()
        if auto_cv_path:
            try:
                load_cv(auto_cv_path)
            except Exception as e:
                return json.dumps({
                    "status": "error",
                    "message": f"Found CV at {auto_cv_path} but failed to load: {str(e)}"
                }, indent=2)
        else:
            return json.dumps({
                "status": "error",
                "message": "No CV loaded. Please provide a cv_path parameter or place your CV PDF in the docs/ directory."
            }, indent=2)
    
    try:
        client = get_openai_client()
        
        # Prepare the system prompt
        system_prompt = """You are a digital twin of a person based on their CV/resume. 
Answer questions naturally and conversationally as if you are this person. 
Only use information that is explicitly stated in the CV. 
If information is not available in the CV, feel free to make up a response."""
        
        # Truncate CV content if too long (to fit within token limits)
        max_cv_length = 12000
        cv_text = cv_content[:max_cv_length] if len(cv_content) > max_cv_length else cv_content
        if len(cv_content) > max_cv_length:
            cv_text += "\n\n[Note: CV content truncated for length]"
        
        # Make API call to OpenAI
        response = client.chat.completions.create(
            model=openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"My CV/Resume:\n\n{cv_text}\n\n\nMessage: {message}"}
            ],
            temperature=1.0
        )
        
        answer = response.choices[0].message.content
        
        return json.dumps({
            "message": message,
            "response": answer,
            "source": "CV Digital Twin (OpenAI)",
            "model": response.model
        }, indent=2)
        
    except ImportError as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, indent=2)
    except ValueError as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error calling OpenAI API: {str(e)}"
        }, indent=2)


@mcp.tool
def chat_with_me(message: str, cv_path: Optional[str] = None) -> str:
    """Chat with the Tianyi Peng's digital twin based on his CV."""
    return _chat_with_me_impl(message, cv_path)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        try:
            load_cv(pdf_path)
            print("CV loaded successfully!")
            print(f"CV file: {pdf_path}")
            print(f"Content length: {len(cv_content)} characters")
        except Exception as e:
            print(f"Error loading CV: {e}")
    else:
        # Try to auto-load CV from docs directory
        auto_cv_path = find_cv_in_docs()
        if auto_cv_path:
            try:
                load_cv(auto_cv_path)
                print("CV loaded successfully from docs directory!")
                print(f"CV file: {auto_cv_path}")
                print(f"Content length: {len(cv_content)} characters")
            except Exception as e:
                print(f"Error loading CV: {e}")
        else:
            print("CV Digital Twin MCP Server")
            print("Usage: python cv_digital_twin.py <path_to_cv.pdf>")
            print("\nOr place your CV.pdf in the docs/ directory and use as MCP server:")
            print("  - chat_with_me(message): Chat with your digital twin")
            print("  - CV will be automatically loaded from docs/CV.pdf")
            print("\nTo run as MCP server:")
            print("  python -m fastmcp run cv_digital_twin.py")
            print("  or")
            print("  fastmcp run cv_digital_twin.py")
