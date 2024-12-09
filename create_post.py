#!/usr/bin/env python3
import sys
from datetime import datetime
from pathlib import Path
import re
import unicodedata
import shutil

def slugify(value):
    """Convert a string into a URL-friendly slug."""
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)

def text_to_html(content):
    """Convert text content to HTML paragraphs."""
    paragraphs = content.split('\n\n')
    html_parts = []
    
    for para in paragraphs:
        if para.strip():
            # Check if it's a heading (starts with # like Markdown)
            if para.startswith('# '):
                html_parts.append(f'<h3>{para[2:].strip()}</h3>')
            else:
                html_parts.append(f'<p>{para.strip()}</p>')
    
    return '\n'.join(html_parts)

def update_essays_index(title, date, post_path):
    """Add new post to essays/index.html."""
    essays_index = Path('essays/index.html')
    year = date.strftime('%Y')
    
    # Read current index
    with open(essays_index, 'r') as f:
        content = f.read()
    
    # Create backup
    shutil.copy(essays_index, essays_index.with_suffix('.html.bak'))
    
    # Find the year section or create new one
    year_section_match = re.search(f'<section class="year-section">\s*<h3>{year}</h3>', content)
    
    new_post_html = f'''
                <article class="post-preview">
                    <time datetime="{date.strftime('%Y-%m-%d')}">{date.strftime('%B %d, %Y')}</time>
                    <h4><a href="/{post_path}">{title}</a></h4>
                </article>'''
    
    if year_section_match:
        # Add post to existing year
        insert_pos = year_section_match.end()
        content = content[:insert_pos] + new_post_html + content[insert_pos:]
    else:
        # Create new year section
        new_year_section = f'''
            <section class="year-section">
                <h3>{year}</h3>
                <div class="post-list">{new_post_html}
                </div>
            </section>'''
        
        # Find the main tag and insert after it
        main_tag_pos = content.find('<main>')
        if main_tag_pos != -1:
            content = content[:main_tag_pos+6] + new_year_section + content[main_tag_pos+6:]
    
    # Save updated index
    with open(essays_index, 'w') as f:
        f.write(content)

def main():
    if len(sys.argv) != 2:
        print("Usage: python create_post.py <text_file>")
        sys.exit(1)
    
    txt_path = Path(sys.argv[1])
    
    # Use filename as title (remove .txt extension and convert hyphens to spaces)
    title = txt_path.stem.replace('-', ' ').title()
    
    # Read all content from file
    with open(txt_path, 'r') as f:
        content = text_to_html(f.read().strip())
    
    date = datetime.now()
    
    # Create directory structure
    year = date.strftime('%Y')
    slug = slugify(title)
    post_dir = Path(f'essays/posts/{year}/{slug}')
    post_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate and save post HTML
    post_html = f'''<!DOCTYPE html>
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

    # Save post
    with open(post_dir / 'index.html', 'w') as f:
        f.write(post_html)
    
    # Update essays index
    relative_path = f'essays/posts/{year}/{slug}'
    update_essays_index(title, date, relative_path)
    
    print(f"\nPost created successfully!")
    print(f"- Post URL: {relative_path}")
    print(f"- Title: {title}")
    print(f"- Date: {date.strftime('%B %d, %Y')}")
    print("\nCheck both files to ensure everything looks correct:")
    print(f"1. {post_dir}/index.html")
    print("2. essays/index.html")

if __name__ == '__main__':
    main()
