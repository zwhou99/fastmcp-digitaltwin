# CV Digital Twin MCP Server

An MCP server that takes your CV PDF as input and behaves like your digital twin, answering questions about you based on your CV content.

## Features

- **Single Tool Interface**: One simple `chat_with_me` tool handles everything
- **Automatic CV Loading**: CV is loaded automatically on first use
- **AI-Powered Digital Twin**: Uses OpenAI GPT models to answer questions naturally and conversationally
- **Intelligent Q&A**: Ask about work experience, skills, education, contact info, and more

## Getting Started

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

Or create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

### Usage

#### As an MCP Server

The server provides a single tool:

**`chat_with_me`**: Chat with your digital twin based on your CV
   - Parameters:
     - `message` (required): Your message or question
     - `cv_path` (optional): Path to your CV PDF file (only needed on first call)
   - Examples:
     - First call: `chat_with_me("Tell me about yourself", cv_path="path/to/my_cv.pdf")`
     - Subsequent calls: `chat_with_me("What is your work experience?")`
     - `chat_with_me("What are your skills?")`
     - `chat_with_me("How can I contact you?")`

#### Local Testing

You can also test the server locally:

```bash
python cv_digital_twin.py path/to/your_cv.pdf
```

## Example Questions

The digital twin can answer questions like:
- "What is your work experience?"
- "What are your skills?"
- "Tell me about your education"
- "What technologies do you know?"
- "How can I contact you?"
- "Tell me about yourself"

## Files

- `cv_digital_twin.py` - Main CV Digital Twin MCP server
- `echo.py` - Original echo server example (for reference)
- `requirements.txt` - Python dependencies

## Dependencies

- `fastmcp` - FastMCP framework
- `openai` - OpenAI API client for AI-powered responses
- `pdfplumber` - PDF text extraction (preferred)
- `PyPDF2` - Alternative PDF library (fallback)

## Configuration

The server uses OpenAI's GPT models to generate responses. 

### Default Model
- Default: `gpt-4o-mini` (cost-efficient)
- Can be changed via environment variable: `export OPENAI_MODEL="gpt-4o"`

### Available Models
- `gpt-4o-mini` - Fast and cost-efficient (default)
- `gpt-4o` - More capable, higher cost
- `gpt-4` - Legacy GPT-4
- `gpt-3.5-turbo` - Fast and economical
- `gpt-4-turbo` - Enhanced GPT-4

**Note**: You'll need an OpenAI API key. Get one at https://platform.openai.com/api-keys

## Deployment

This repository is ready to be deployed!

- Create a new [FastMCP Cloud account](http://fastmcp.cloud/signup)
- Connect your GitHub account
- Select `Clone our template` and a deployment will be created for you!

## Learn More

- [FastMCP Documentation](https://gofastmcp.com/)
- [MCP Protocol](https://modelcontextprotocol.io/)

---
*This repository was created from the FastMCP quickstart template and extended with CV Digital Twin functionality.*
