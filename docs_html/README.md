# HTML Documentation Viewers

This directory contains HTML versions of all markdown documentation files for easy viewing in a browser.

## Quick Start

1. **Generate HTML files:**
   ```bash
   # Windows
   scripts\generate_html.bat
   
   # Linux/Mac
   python scripts/generate_html_viewers.py
   ```

2. **Open index.html:**
   - Open `docs_html/index.html` in your browser
   - Browse all documentation with beautiful formatting

## Requirements

- Python 3.6+
- markdown library: `pip install markdown`

## Features

- ✅ Beautiful, responsive HTML styling
- ✅ Interactive Mermaid diagrams
- ✅ Syntax highlighting for code blocks
- ✅ Easy navigation with index page
- ✅ Mobile-friendly design

## Manual Generation

If the batch script doesn't work, you can run the Python script directly:

```bash
# Install markdown library
pip install markdown

# Generate HTML files
python scripts/generate_html_viewers.py
```

## Viewing

Simply open any `.html` file in this directory with your web browser. All diagrams and formatting will render automatically.
