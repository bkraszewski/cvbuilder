# CV Generator

Generates PDF CVs from Markdown files with YAML front matter using WeasyPrint.

## Prerequisites

- Python 3.10+
- Homebrew (macOS)

## Setup

```bash
# Install system dependencies (pango is required by WeasyPrint)
brew install pango libffi

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Activate venv (if not already active)
source venv/bin/activate

# Generate a CV PDF
python generate.py cvs/staff-generalist.md

# Generate with custom output path
python generate.py cvs/staff-generalist.md -o output/my-cv.pdf

# Also save intermediate HTML
python generate.py cvs/staff-generalist.md --html
```

Output PDFs are saved to the `output/` directory by default.

## Project Structure

```
cvs/           - Markdown CV source files (YAML front matter + Markdown)
templates/     - Jinja2 HTML template and CSS
fonts/         - Custom fonts
output/        - Generated PDFs
```
