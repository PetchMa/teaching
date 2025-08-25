#!/usr/bin/env python3
"""
Markdown to PDF and HTML Converter

This script converts markdown files to both PDF and HTML formats.
It includes proper styling and formatting for both output types.

Requirements:
- markdown
- weasyprint (for PDF generation)
- jinja2 (for HTML templating)
"""

import argparse
import os
import sys
from pathlib import Path
import markdown
from jinja2 import Template
import weasyprint
from weasyprint import HTML, CSS
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# HTML template for better styling
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        
        .content {
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 30px;
            margin-bottom: 15px;
        }
        
        h1 {
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        
        h2 {
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
        }
        
        h3 {
            color: #34495e;
        }
        
        p {
            margin-bottom: 15px;
        }
        
        ul, ol {
            margin-bottom: 15px;
            padding-left: 25px;
        }
        
        li {
            margin-bottom: 5px;
        }
        
        blockquote {
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding: 10px 20px;
            background-color: #f8f9fa;
            font-style: italic;
        }
        
        code {
            background-color: #f1f2f6;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        
        pre {
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 20px 0;
        }
        
        pre code {
            background-color: transparent;
            color: inherit;
            padding: 0;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        
        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        
        tr:hover {
            background-color: #e8f4f8;
        }
        
        a {
            color: #3498db;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        hr {
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #ecf0f1;
        }
        
        .header h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            color: #7f8c8d;
            font-size: 1.1em;
        }
        
        @media print {
            body {
                background-color: white;
            }
            .content {
                box-shadow: none;
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="content">
        <div class="header">
            <h1>{{ title }}</h1>
            {% if subtitle %}
            <div class="subtitle">{{ subtitle }}</div>
            {% endif %}
        </div>
        {{ content }}
    </div>
</body>
</html>
"""

def convert_markdown_to_html(markdown_content, title="Document", subtitle=None):
    """Convert markdown content to HTML with custom styling."""
    # Convert markdown to HTML
    html_content = markdown.markdown(
        markdown_content,
        extensions=[
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
            'markdown.extensions.attr_list',
            'markdown.extensions.def_list',
            'markdown.extensions.footnotes'
        ]
    )
    
    # Use Jinja2 template
    template = Template(HTML_TEMPLATE)
    html = template.render(
        title=title,
        subtitle=subtitle,
        content=html_content
    )
    
    return html

def save_html(html_content, output_path):
    """Save HTML content to file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"HTML saved to: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving HTML: {e}")
        return False

def save_pdf(html_content, output_path):
    """Convert HTML content to PDF and save."""
    try:
        # Create PDF from HTML
        pdf = weasyprint.HTML(string=html_content).write_pdf()
        
        with open(output_path, 'wb') as f:
            f.write(pdf)
        logger.info(f"PDF saved to: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        return False

def convert_markdown_file(input_path, output_dir=None, title=None, subtitle=None):
    """Convert a markdown file to both HTML and PDF formats."""
    
    # Read markdown file
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except Exception as e:
        logger.error(f"Error reading markdown file: {e}")
        return False
    
    # Determine output directory and filename
    input_file = Path(input_path)
    if output_dir is None:
        output_dir = input_file.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
    
    # Use filename as title if not provided
    if title is None:
        title = input_file.stem
    
    # Generate output filenames
    html_path = output_dir / f"{input_file.stem}.html"
    pdf_path = output_dir / f"{input_file.stem}.pdf"
    
    # Convert to HTML
    html_content = convert_markdown_to_html(markdown_content, title, subtitle)
    
    # Save HTML
    if not save_html(html_content, html_path):
        return False
    
    # Save PDF
    if not save_pdf(html_content, pdf_path):
        return False
    
    logger.info(f"Conversion completed successfully!")
    logger.info(f"HTML: {html_path}")
    logger.info(f"PDF: {pdf_path}")
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Convert markdown files to HTML and PDF formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python markdown_converter.py document.md
  python markdown_converter.py document.md -o output_folder
  python markdown_converter.py document.md -t "My Document" -s "Subtitle"
  python markdown_converter.py document.md -o output_folder -t "Custom Title"
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Input markdown file path'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        help='Output directory (default: same as input file)'
    )
    
    parser.add_argument(
        '-t', '--title',
        help='Custom title for the document'
    )
    
    parser.add_argument(
        '-s', '--subtitle',
        help='Custom subtitle for the document'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Markdown Converter 1.0'
    )
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        logger.error(f"Input file not found: {args.input_file}")
        sys.exit(1)
    
    # Check if input file is markdown
    if not args.input_file.lower().endswith(('.md', '.markdown')):
        logger.warning(f"Input file doesn't have .md or .markdown extension: {args.input_file}")
    
    # Perform conversion
    success = convert_markdown_file(
        args.input_file,
        args.output_dir,
        args.title,
        args.subtitle
    )
    
    if success:
        logger.info("Conversion completed successfully!")
        sys.exit(0)
    else:
        logger.error("Conversion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
