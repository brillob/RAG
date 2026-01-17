#!/usr/bin/env python3
"""
Generate HTML viewers for all markdown files in the project.

Usage:
    python scripts/generate_html_viewers.py

Requirements:
    pip install markdown
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Try to import markdown library
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("Warning: markdown library not found. Install with: pip install markdown")
    print("Falling back to basic markdown conversion...")

# HTML template with Mermaid support
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }}
        }});
    </script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 40px;
        }}
        
        h1 {{
            color: #333;
            border-bottom: 4px solid #667eea;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-size: 2.5em;
        }}
        
        h2 {{
            color: #555;
            margin-top: 40px;
            margin-bottom: 20px;
            border-left: 5px solid #667eea;
            padding-left: 20px;
            font-size: 1.8em;
        }}
        
        h3 {{
            color: #666;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.4em;
        }}
        
        h4 {{
            color: #777;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 1.2em;
        }}
        
        p {{
            margin: 15px 0;
            color: #444;
        }}
        
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 8px 0;
            color: #444;
        }}
        
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #e83e8c;
        }}
        
        pre {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        pre code {{
            background: transparent;
            padding: 0;
            color: inherit;
            font-size: 0.9em;
        }}
        
        .mermaid {{
            text-align: center;
            overflow-x: auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 30px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: 2px solid #e9ecef;
        }}
        
        blockquote {{
            border-left: 4px solid #667eea;
            padding-left: 20px;
            margin: 20px 0;
            color: #666;
            font-style: italic;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        
        tr:hover {{
            background: #f5f5f5;
        }}
        
        a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        .note {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            padding: 20px;
            margin: 30px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .note strong {{
            display: block;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .warning {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        .info {{
            background: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        .success {{
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #e9ecef;
            margin: 40px 0;
        }}
        
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border-radius: 5px;
            text-decoration: none;
        }}
        
        .back-link:hover {{
            background: #5568d3;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="index.html" class="back-link">← Back to Documentation Index</a>
        {content}
    </div>
</body>
</html>
"""


def extract_title(markdown_content: str) -> str:
    """Extract title from markdown (first H1)."""
    lines = markdown_content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return "Documentation"


def markdown_to_html(markdown_content: str) -> str:
    """Convert markdown to HTML with Mermaid diagram support."""
    if MARKDOWN_AVAILABLE:
        return markdown_to_html_with_library(markdown_content)
    else:
        return markdown_to_html_basic(markdown_content)


def markdown_to_html_with_library(markdown_content: str) -> str:
    """Convert markdown using markdown library, preserving Mermaid blocks."""
    # Extract Mermaid code blocks first
    mermaid_pattern = r'```mermaid\n(.*?)```'
    mermaid_blocks = []
    placeholders = []
    
    def replace_mermaid(match):
        idx = len(mermaid_blocks)
        mermaid_blocks.append(match.group(1))
        placeholders.append(f'MERMAID_BLOCK_{idx}')
        return f'\n\nMERMAID_PLACEHOLDER_{idx}\n\n'
    
    # Replace Mermaid blocks with placeholders
    content_with_placeholders = re.sub(mermaid_pattern, replace_mermaid, markdown_content, flags=re.DOTALL)
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=['fenced_code', 'tables', 'codehilite'])
    html_content = md.convert(content_with_placeholders)
    
    # Replace placeholders with Mermaid divs
    for idx, mermaid_code in enumerate(mermaid_blocks):
        placeholder = f'MERMAID_PLACEHOLDER_{idx}'
        mermaid_div = f'<div class="mermaid">\n{mermaid_code.strip()}\n</div>'
        html_content = html_content.replace(placeholder, mermaid_div)
    
    return html_content


def markdown_to_html_basic(markdown_content: str) -> str:
    """Basic markdown to HTML conversion (fallback)."""
    lines = markdown_content.split('\n')
    html_lines = []
    in_code_block = False
    in_mermaid_block = False
    code_block_lang = ''
    code_content = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Handle code blocks
        if line.startswith('```'):
            if in_code_block:
                # End code block
                code_text = '\n'.join(code_content)
                if in_mermaid_block:
                    html_lines.append(f'<div class="mermaid">\n{code_text}\n</div>')
                else:
                    html_lines.append(f'<pre><code>{escape_html(code_text)}</code></pre>')
                code_content = []
                in_code_block = False
                in_mermaid_block = False
            else:
                # Start code block
                in_code_block = True
                code_block_lang = line[3:].strip()
                in_mermaid_block = (code_block_lang == 'mermaid')
        elif in_code_block:
            code_content.append(line)
        else:
            # Regular markdown processing
            html_line = process_markdown_line(line)
            if html_line:
                html_lines.append(html_line)
        
        i += 1
    
    # Handle any remaining code block
    if in_code_block and code_content:
        code_text = '\n'.join(code_content)
        if in_mermaid_block:
            html_lines.append(f'<div class="mermaid">\n{code_text}\n</div>')
        else:
            html_lines.append(f'<pre><code>{escape_html(code_text)}</code></pre>')
    
    return '\n'.join(html_lines)


def process_markdown_line(line: str) -> str:
    """Process a single markdown line."""
    line = line.rstrip()
    
    if not line:
        return '<br>'
    
    # Headers
    if line.startswith('# '):
        return f'<h1>{line[2:]}</h1>'
    elif line.startswith('## '):
        return f'<h2>{line[3:]}</h2>'
    elif line.startswith('### '):
        return f'<h3>{line[4:]}</h3>'
    elif line.startswith('#### '):
        return f'<h4>{line[5:]}</h4>'
    
    # Horizontal rule
    if line.strip() == '---':
        return '<hr>'
    
    # Lists
    if line.startswith('- ') or line.startswith('* '):
        content = inline_markdown(line[2:])
        return f'<li>{content}</li>'
    elif re.match(r'^\d+\.\s', line):
        content = inline_markdown(re.sub(r'^\d+\.\s', '', line))
        return f'<li>{content}</li>'
    
    # Blockquote
    if line.startswith('> '):
        content = inline_markdown(line[2:])
        return f'<blockquote>{content}</blockquote>'
    
    # Regular paragraph
    if line.strip():
        content = inline_markdown(line)
        return f'<p>{content}</p>'
    
    return ''


def inline_markdown(text: str) -> str:
    """Process inline markdown (bold, italic, code, links)."""
    # Escape HTML first
    text = escape_html(text)
    
    # Code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', text)
    
    # Italic
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)
    
    # Links [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    
    # Special handling for checkmarks and emojis
    text = text.replace('✅', '✅')
    text = text.replace('⚠️', '⚠️')
    text = text.replace('📌', '📌')
    text = text.replace('💡', '💡')
    
    return text


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


def wrap_list_items(html_lines: List[str]) -> List[str]:
    """Wrap consecutive list items in <ul> or <ol> tags."""
    result = []
    i = 0
    while i < len(html_lines):
        if html_lines[i].startswith('<li>'):
            # Find end of list
            j = i
            while j < len(html_lines) and html_lines[j].startswith('<li>'):
                j += 1
            
            # Check if numbered list
            is_ordered = False
            for k in range(i, min(j, len(html_lines))):
                if html_lines[k].startswith('<li>') and re.search(r'^\d+\.', html_lines[k]):
                    is_ordered = True
                    break
            
            tag = '<ol>' if is_ordered else '<ul>'
            result.append(tag)
            result.extend(html_lines[i:j])
            result.append(f'</{"ol" if is_ordered else "ul"}>')
            i = j
        else:
            result.append(html_lines[i])
            i += 1
    
    return result


def find_markdown_files(root_dir: Path) -> List[Path]:
    """Find all markdown files in the project."""
    md_files = []
    exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}
    
    for path in root_dir.rglob('*.md'):
        # Skip files in excluded directories
        if any(part in exclude_dirs for part in path.parts):
            continue
        md_files.append(path)
    
    return sorted(md_files)


def generate_html_file(md_path: Path, output_dir: Path) -> Path:
    """Generate HTML file from markdown."""
    print(f"Processing: {md_path}")
    
    # Read markdown
    content = md_path.read_text(encoding='utf-8')
    
    # Extract title
    title = extract_title(content)
    
    # Convert to HTML
    html_content = markdown_to_html(content)
    
    # Wrap list items
    html_lines = html_content.split('\n')
    html_lines = wrap_list_items(html_lines)
    html_content = '\n'.join(html_lines)
    
    # Create full HTML document
    full_html = HTML_TEMPLATE.format(title=title, content=html_content)
    
    # Write HTML file
    html_filename = md_path.stem + '.html'
    html_path = output_dir / html_filename
    html_path.write_text(full_html, encoding='utf-8')
    
    print(f"  → Generated: {html_path}")
    return html_path


def create_index_html(md_files: List[Path], html_files: List[Path], output_dir: Path):
    """Create an index HTML file linking to all documentation."""
    index_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation Index</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 40px;
        }
        
        h1 {
            color: #333;
            border-bottom: 4px solid #667eea;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        
        .doc-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .doc-card {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .doc-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border-color: #667eea;
        }
        
        .doc-card h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.3em;
        }
        
        .doc-card p {
            color: #666;
            margin-bottom: 15px;
            font-size: 0.9em;
        }
        
        .doc-card a {
            display: inline-block;
            padding: 8px 16px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: 500;
        }
        
        .doc-card a:hover {
            background: #5568d3;
        }
        
        .category {
            margin-top: 40px;
        }
        
        .category h2 {
            color: #555;
            border-left: 5px solid #667eea;
            padding-left: 15px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Documentation Index</h1>
        <p>All project documentation in HTML format for easy reading.</p>
        
        <div class="category">
            <h2>Getting Started</h2>
            <div class="doc-grid">
                <div class="doc-card">
                    <h3>README</h3>
                    <p>Main project documentation and overview</p>
                    <a href="README.html">View →</a>
                </div>
                <div class="doc-card">
                    <h3>Quick Start</h3>
                    <p>Quick start guide for local testing and Azure deployment</p>
                    <a href="QUICKSTART.html">View →</a>
                </div>
                <div class="doc-card">
                    <h3>Project Summary</h3>
                    <p>High-level project overview and features</p>
                    <a href="PROJECT_SUMMARY.html">View →</a>
                </div>
            </div>
        </div>
        
        <div class="category">
            <h2>Architecture & Design</h2>
            <div class="doc-grid">
                <div class="doc-card">
                    <h3>Architecture</h3>
                    <p>Complete system architecture and file structure</p>
                    <a href="ARCHITECTURE.html">View →</a>
                </div>
                <div class="doc-card">
                    <h3>Architecture Diagrams</h3>
                    <p>Visual architecture diagrams with Mermaid</p>
                    <a href="ARCHITECTURE_DIAGRAM.html">View →</a>
                </div>
                <div class="doc-card">
                    <h3>Production Architecture</h3>
                    <p>Azure and Docker production deployment architecture</p>
                    <a href="PRODUCTION_ARCHITECTURE.html">View →</a>
                </div>
            </div>
        </div>
        
        <div class="category">
            <h2>Testing & Development</h2>
            <div class="doc-grid">
                <div class="doc-card">
                    <h3>Local Testing</h3>
                    <p>Guide for local testing with vector database</p>
                    <a href="LOCAL_TESTING.html">View →</a>
                </div>
                <div class="doc-card">
                    <h3>Swagger Guide</h3>
                    <p>Complete Swagger UI testing guide</p>
                    <a href="SWAGGER_GUIDE.html">View →</a>
                </div>
                <div class="doc-card">
                    <h3>Swagger Quick Start</h3>
                    <p>Quick reference for Swagger UI</p>
                    <a href="SWAGGER_QUICK_START.html">View →</a>
                </div>
                <div class="doc-card">
                    <h3>Run Swagger Locally</h3>
                    <p>Step-by-step guide to run Swagger UI locally</p>
                    <a href="RUN_SWAGGER_LOCALLY.html">View →</a>
                </div>
                <div class="doc-card">
                    <h3>Swagger Steps</h3>
                    <p>5-minute quick start for Swagger UI</p>
                    <a href="SWAGGER_STEPS.html">View →</a>
                </div>
            </div>
        </div>
        
        <div class="category">
            <h2>Deployment</h2>
            <div class="doc-grid">
                <div class="doc-card">
                    <h3>Deployment Guide</h3>
                    <p>Complete Azure deployment guide</p>
                    <a href="DEPLOYMENT.html">View →</a>
                </div>
                <div class="doc-card">
                    <h3>Setup Guide</h3>
                    <p>Setup instructions for the project</p>
                    <a href="SETUP_GUIDE.html">View →</a>
                </div>
            </div>
        </div>
        
        <div class="category">
            <h2>Features & Configuration</h2>
            <div class="doc-grid">
                <div class="doc-card">
                    <h3>Chunking Strategies</h3>
                    <p>Guide to different text chunking strategies</p>
                    <a href="CHUNKING_STRATEGIES.html">View →</a>
                </div>
                <div class="doc-card">
                    <h3>Conversation Memory</h3>
                    <p>How conversation memory works for follow-up questions</p>
                    <a href="CONVERSATION_MEMORY.html">View →</a>
                </div>
                <div class="doc-card">
                    <h3>View Diagrams</h3>
                    <p>Guide on how to view Mermaid diagrams</p>
                    <a href="VIEW_DIAGRAMS.html">View →</a>
                </div>
                <div class="doc-card">
                    <h3>Test Coverage</h3>
                    <p>Unit test coverage summary</p>
                    <a href="TEST_COVERAGE_SUMMARY.html">View →</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    index_path = output_dir / 'index.html'
    index_path.write_text(index_content, encoding='utf-8')
    print(f"Created index: {index_path}")


def main():
    """Main function to generate HTML viewers for all markdown files."""
    project_root = Path(__file__).parent.parent
    output_dir = project_root / 'docs_html'
    output_dir.mkdir(exist_ok=True)
    
    print("Finding markdown files...")
    md_files = find_markdown_files(project_root)
    print(f"Found {len(md_files)} markdown files\n")
    
    html_files = []
    for md_file in md_files:
        try:
            html_path = generate_html_file(md_file, output_dir)
            html_files.append(html_path)
        except Exception as e:
            print(f"  ❌ Error processing {md_file}: {e}")
    
    # Create index
    create_index_html(md_files, html_files, output_dir)
    
    print(f"\n✅ Generated {len(html_files)} HTML files in {output_dir}")
    print(f"📄 Open index.html to browse all documentation")


if __name__ == '__main__':
    main()
