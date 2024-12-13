#!/usr/bin/env python3
import sys
from datetime import datetime, date
from pathlib import Path
import re
import unicodedata
import shutil

def get_post_date(post_dir):
    """Get post date from date.txt if it exists, otherwise use current date."""
    date_file = post_dir / 'date.txt'
    if date_file.exists():
        with open(date_file, 'r') as f:
            date_str = f.read().strip()
            try:
                # Expect format like "2024-12-08"
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                print(f"Warning: Invalid date format in date.txt, using current date")
                return datetime.now()
    return datetime.now()

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
        paragraphs = [p.strip() for p in main_content.split('\n\n')]
        for para in paragraphs:
            if para:
                if para.startswith('# '):
                    html_parts.append(f'<h3>{para[2:].strip()}</h3>')
                else:
                    html_parts.append(f'<p>{para}</p>')
        
        # Process signoff - keep all remaining lines
        signoff = '<br>'.join(line.strip() for line in lines[signoff_start:] if line.strip())
        html_parts.append(f'<p class="signoff">{signoff}</p>')
    else:
        # No signoff detected, process everything normally
        paragraphs = [p.strip() for p in content.split('\n\n')]
        for para in paragraphs:
            if para:
                if para.startswith('# '):
                    html_parts.append(f'<h3>{para[2:].strip()}</h3>')
                else:
                    html_parts.append(f'<p>{para}</p>')
    
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

def generate_post_html(title, content, date):
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

def update_or_create_post(source_path, is_update=False):
    """Create a new post or update an existing one."""
    title = source_path.parent.name.replace('-', ' ').title()
    post_dir = source_path.parent
    date = get_post_date(post_dir)
    
    # Read new content
    with open(source_path, 'r') as f:
        new_content = f.read().strip()
    
    if is_update:
        # Check if content has changed
        html_path = post_dir / 'index.html'
        with open(html_path, 'r') as f:
            current_content = f.read()
            
        # Convert new content to HTML
        new_html = generate_post_html(title, text_to_html(new_content), date)
        
        if current_content == new_html:
            # No changes detected
            return post_dir, date, False
    
    # Either new post or content has changed
    # Convert content to HTML and save
    html_content = text_to_html(new_content)
    post_html = generate_post_html(title, html_content, date)
    with open(post_dir / 'index.html', 'w') as f:
        f.write(post_html)
    
    if not is_update:
        # Only update index for new posts
        update_essays_index(title, date, post_dir)
    
    return post_dir, date, True

def main():
    if len(sys.argv) != 2:
        print("Usage: python create_post.py <year/post-name>")
        print("Example: python create_post.py 2024/a-new-start")
        sys.exit(1)
    
    # Get year and post directory from argument
    post_path = sys.argv[1].rstrip('/')
    year, post_name = post_path.split('/')
    
    # Construct full directory path and source.txt path
    post_dir = Path(f'essays/posts/{year}/{post_name}')
    source_path = post_dir / 'source.txt'
    
    if not source_path.exists():
        print(f"Error: source.txt not found in {post_dir}")
        print(f"Please ensure source.txt is in the directory.")
        sys.exit(1)
    
    # Check if this is a new post or update
    is_update = (post_dir / 'index.html').exists()
    
    # Process the post
    post_dir, post_date, was_changed = update_or_create_post(source_path, is_update)
    
    if is_update:
        if was_changed:
            print(f"\nPost updated successfully!")
        else:
            print(f"\nNo changes detected, post remains the same.")
    else:
        print(f"\nPost created successfully!")
    
    print(f"- Post URL: {post_dir}")
    print(f"- Title: {post_name.replace('-', ' ').title()}")
    print(f"- Date: {post_date.strftime('%B %d, %Y')}")
    print("\nFiles:")
    print(f"1. {post_dir}/index.html (HTML version)")
    print(f"2. {source_path} (Source file)")
    print(f"3. {post_dir}/date.txt (Date override - optional)")

if __name__ == '__main__':
    main()