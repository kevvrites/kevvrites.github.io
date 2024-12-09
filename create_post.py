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
    """Convert text content to HTML paragraphs with flexible signoff detection."""
    # Split content into lines first
    lines = content.strip().split('\n')
    
    # Look for common signoff patterns near the end
    signoff_patterns = [
        'See ya!',
        'Until next time',
        'Best',
        'Sincerely',
        'Cheers',
        '-',
        '—'  # em dash
    ]
    
    # Find potential signoff starting position
    signoff_start = -1
    for i in range(len(lines) - 3, len(lines)):  # Check last few lines
        if i >= 0:  # Make sure index is valid
            line = lines[i].strip()
            if any(line.startswith(pattern) for pattern in signoff_patterns) or (
                len(line) < 30 and any(name in line.lower() for name in ['kevin', 'kev'])):
                signoff_start = i
                break
    
    html_parts = []
    
    # If we found a signoff, process the content in two parts
    if signoff_start != -1:
        # Process main content
        main_content = '\n'.join(lines[:signoff_start])
        for para in main_content.split('\n\n'):
            if para.strip():
                if para.startswith('# '):
                    html_parts.append(f'<h3>{para[2:].strip()}</h3>')
                else:
                    html_parts.append(f'<p>{para.strip()}</p>')
        
        # Process signoff - keep all remaining lines
        signoff = '<br>'.join(line.strip() for line in lines[signoff_start:] if line.strip())
        html_parts.append(f'<p class="signoff">{signoff}</p>')
    else:
        # No signoff detected, process everything normally
        for para in content.split('\n\n'):
            if para.strip():
                if para.startswith('# '):
                    html_parts.append(f'<h3>{para[2:].strip()}</h3>')
                else:
                    html_parts.append(f'<p>{para.strip()}</p>')
    
    return '\n'.join(html_parts)

def update_essays_index(title, date, post_path):
    """Add new post to essays/index.html."""
    index_path = Path('essays/index.html')
    year = date.strftime('%Y')
    
    # Create backup
    shutil.copy(index_path, index_path.with_suffix('.html.bak'))
    
    with open(index_path, 'r') as f:
        content = f.read()

    # Find year section
    year_section = re.search(f'<section class="year-section">\s*<h3>{year}</h3>\s*<div class="post-list">', content)
    
    new_post_html = f'''
                <article class="post-preview">
                    <time datetime="{date.strftime('%Y-%m-%d')}">{date.strftime('%B %d, %Y')}</time>
                    <h4><a href="/essays/posts/{year}/{slugify(title)}">{title}</a></h4>
                </article>'''

    if year_section:
        # Add to existing year section
        insert_pos = year_section.end()
        content = content[:insert_pos] + new_post_html + content[insert_pos:]
    else:
        # Create new year section
        new_section = f'''
            <section class="year-section">
                <h3>{year}</h3>
                <div class="post-list">
                    {new_post_html}
                </div>
            </section>'''
        
        # Find the main tag and insert after the Essays heading
        essays_heading = re.search(r'<h2>Essays</h2>', content)
        if essays_heading:
            insert_pos = essays_heading.end()
            content = content[:insert_pos] + new_section + content[insert_pos:]
    
    with open(index_path, 'w') as f:
        f.write(content)

def main():
    if len(sys.argv) != 2:
        print("Usage: python create_post.py <text_file>")
        sys.exit(1)
    
    txt_path = Path(sys.argv[1])
    
    # Use filename as title (remove .txt extension)
    title = txt_path.stem.replace('-', ' ').title()
    
    # Read content
    with open(txt_path, 'r') as f:
        content = text_to_html(f.read().strip())
    
    date = datetime.now()
    
    # Create directory structure
    year = date.strftime('%Y')
    slug = slugify(title)
    post_dir = Path(f'essays/posts/{year}/{slug}')
    post_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate post HTML
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
    update_essays_index(title, date, post_dir)
    
    print(f"\nPost created successfully!")
    print(f"- Post URL: {post_dir}")
    print(f"- Title: {title}")
    print(f"- Date: {date.strftime('%B %d, %Y')}")
    print("\nCheck both files to ensure everything looks correct:")
    print(f"1. {post_dir}/index.html")
    print("2. essays/index.html")

if __name__ == '__main__':
    main()