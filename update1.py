#!/usr/bin/env python3
import sys
from pathlib import Path
from datetime import datetime
import re
import shutil

def get_post_date(post_dir):
    """Get post date from date.txt."""
    date_file = post_dir / 'date.txt'
    if not date_file.exists():
        # If no date.txt exists, create one with current date
        current_date = datetime.now().strftime('%Y-%m-%d')
        with open(date_file, 'w') as f:
            f.write(current_date)
        return datetime.now()
        
    with open(date_file, 'r') as f:
        date_str = f.read().strip()
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid date format in date.txt")
            sys.exit(1)

def text_to_html(content):
    """Convert text content to HTML paragraphs."""
    lines = content.strip().split('\n')
    html_parts = []
    
    for line in lines:
        if line.strip():
            if line.strip().startswith('# '):
                html_parts.append(f'<h3>{line.strip()[2:].strip()}</h3>')
            else:
                html_parts.append(f'<p>{line.strip()}</p>')
    
    return '\n'.join(html_parts)

def generate_html(post_type, title, content, date, author=None):
    """Generate HTML for the post."""
    if post_type == "book":
        page_title = f"{title} by {author} - Book Review - Kevin Liu"
    else:
        page_title = f"{title} - Kevin Liu"

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <link rel="stylesheet" href="/assets/css/styles.css">
</head>
<body>
    <div class="container">
        <header class="header">
            <div>
                <h1>Kevin Liu</h1>
                <nav>
                    <a href="/">Home</a>
                    <a href="/essays">Essays</a>
                    <a href="/books">Books</a>
                    <a href="/engineering">Engineering</a>
                    <a href="/games">Games</a>
                    <a href="/about">About</a>
                </nav>
            </div>
        </header>

        <main class="post-content">
            <article>
                <header class="post-header">
                    <h2>{title}</h2>'''

    if author:  # Add author line for books
        html += f'\n                    <h3 class="book-author">by {author}</h3>'

    html += f'''
                    <time datetime="{date.strftime('%Y-%m-%d')}">{date.strftime('%B %d, %Y')}</time>
                </header>

                <section class="post-body">
                    {content}
                </section>
            </article>

            <nav class="post-navigation">
                <a href="/{post_type}s">← Back to {post_type.title()}s</a>
            </nav>
        </main>

        <footer class="footer">
            © 2024 Kevin Liu. All rights reserved.
        </footer>
    </div>
</body>
</html>'''

    return html

def main():
    if len(sys.argv) != 3:
        print("Usage: python update.py <type> <year/post-name>")
        print("Example: python update.py essay 2024/my-first-post")
        print("Example: python update.py book 2024/the-great-gatsby-by-f-scott-fitzgerald")
        sys.exit(1)

    post_type = sys.argv[1].lower()
    if post_type not in ["essay", "book"]:
        print(f"Error: Invalid post type '{post_type}'")
        sys.exit(1)

    # Get post directory
    post_path = sys.argv[2].rstrip('/')
    year, post_name = post_path.split('/')
    post_dir = Path(f'{post_type}s/posts/{year}/{post_name}')
    source_path = post_dir / 'source.txt'

    # Check if source.txt exists
    if not source_path.exists():
        print(f"Error: source.txt not found at {source_path}")
        print("Make sure source.txt exists in the post directory")
        sys.exit(1)

    # Get or create the post date
    date = get_post_date(post_dir)

    # Create backup of the HTML file if it exists
    html_path = post_dir / 'index.html'
    if html_path.exists():
        backup_path = post_dir / f'index.html.bak'
        shutil.copy(html_path, backup_path)
        print(f"Created backup of existing HTML at {backup_path}")

    # Read and convert content
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print("Error: source.txt must be in UTF-8 encoding")
        sys.exit(1)

    html_content = text_to_html(content)

    # Generate appropriate HTML based on post type
    if post_type == "book":
        parts = post_name.split('-by-')
        if len(parts) != 2:
            print("Error: Book post name must be in format: book-title-by-author")
            sys.exit(1)
        
        book_title = parts[0].replace('-', ' ').title()
        book_author = parts[1].replace('-', ' ').title()
        html = generate_html(post_type, book_title, html_content, date, book_author)
    else:
        title = post_name.replace('-', ' ').title()
        html = generate_html(post_type, title, html_content, date)

    # Save HTML
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n✅ Post HTML generated successfully!")
    print(f"- Location: {post_dir}")
    if post_type == "book":
        print(f"- Title: {book_title}")
        print(f"- Author: {book_author}")
    else:
        print(f"- Title: {title}")
    print(f"- Date: {date.strftime('%B %d, %Y')}")

if __name__ == '__main__':
    main()