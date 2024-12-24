#!/usr/bin/env python3
import sys
from pathlib import Path
from datetime import datetime
import re

def get_post_date(post_dir):
    """Get post date from date.txt if it exists, otherwise use current date."""
    date_file = post_dir / 'date.txt'
    if date_file.exists():
        with open(date_file, 'r') as f:
            date_str = f.read().strip()
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                print(f"Warning: Invalid date format in date.txt, using current date")
                return datetime.now()
    return datetime.now()

def text_to_html(content):
    """Convert text content to HTML paragraphs."""
    lines = content.strip().split('\n')
    
    # Look for signoff
    signoff_patterns = [
        'See ya!', 'Until next time', 'Best', 'Sincerely', 'Cheers', '-', '—'
    ]
    
    signoff_start = -1
    for i in range(len(lines) - 3, len(lines)):
        if i >= 0:
            line = lines[i].strip()
            if any(line.startswith(pattern) for pattern in signoff_patterns) or (
                len(line) < 30 and any(name in line.lower() for name in ['kevin', 'kev'])):
                signoff_start = i
                break
    
    html_parts = []
    
    if signoff_start != -1:
        # Main content
        for line in lines[:signoff_start]:
            if line.strip():
                if line.strip().startswith('# '):
                    html_parts.append(f'<h3>{line.strip()[2:].strip()}</h3>')
                else:
                    html_parts.append(f'<p>{line.strip()}</p>')
        
        # Signoff
        signoff = '<br>'.join(line.strip() for line in lines[signoff_start:] if line.strip())
        html_parts.append(f'<p class="signoff">{signoff}</p>')
    else:
        for line in lines:
            if line.strip():
                if line.strip().startswith('# '):
                    html_parts.append(f'<h3>{line.strip()[2:].strip()}</h3>')
                else:
                    html_parts.append(f'<p>{line.strip()}</p>')
    
    return '\n'.join(html_parts)

def generate_html(title, content, date):
    """Generate the HTML for a post."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Kevin Liu</title>
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
                    <a href="/engineering">Engineering</a>
                    <a href="/games">Games</a>
                    <a href="/about">About</a>
                </nav>
            </div>
        </header>

        <main class="post-content">
            <article>
                <header class="post-header">
                    <h2>{title}</h2>
                    <time datetime="{date.strftime('%Y-%m-%d')}">{date.strftime('%B %d, %Y')}</time>
                </header>

                <section class="post-body">
                    {content}
                </section>
            </article>

            <nav class="post-navigation">
                <a href="/essays">← Back to Essays</a>
            </nav>
        </main>

        <footer class="footer">
            © 2024 Kevin Liu. All rights reserved.
        </footer>
    </div>
</body>
</html>'''

def main():
    if len(sys.argv) != 2:
        print("Usage: python update_post.py <year/post-name>")
        print("Example: python update_post.py 2024/my-first-post")
        sys.exit(1)

    # Get post directory
    post_path = sys.argv[1].rstrip('/')
    year, post_name = post_path.split('/')
    post_dir = Path(f'essays/posts/{year}/{post_name}')
    source_path = post_dir / 'source.txt'

    # Check if post exists
    if not post_dir.exists() or not source_path.exists():
        print(f"Error: Post not found at {post_dir}")
        print("Make sure both the directory and source.txt exist")
        sys.exit(1)

    # Get post information
    title = post_name.replace('-', ' ').title()
    date = get_post_date(post_dir)

    # Read and convert content
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print("Error: source.txt must be in UTF-8 encoding")
        sys.exit(1)

    html_content = text_to_html(content)
    post_html = generate_html(title, html_content, date)

    # Save HTML
    with open(post_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(post_html)

    print(f"\nPost updated successfully!")
    print(f"- Location: {post_dir}")
    print(f"- Title: {title}")
    print(f"- Date: {date.strftime('%B %d, %Y')}")

if __name__ == '__main__':
    main()