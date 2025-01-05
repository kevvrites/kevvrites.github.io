#!/usr/bin/env python3
import sys
from pathlib import Path
import shutil
import re

def remove_from_index(post_url):
    """Remove post entry from index.html"""
    # Extract type from URL (essays or books)
    post_type = post_url.split('/')[0]
    index_path = Path(f'{post_type}/index.html')
    
    # Create backup
    shutil.copy(index_path, index_path.with_suffix('.html.bak'))
    
    with open(index_path, 'r') as f:
        content = f.read()
    
    # Remove post entry
    pattern = re.compile(
        f'<article class="post-preview">.*?href="/{post_url}".*?</article>',
        re.DOTALL
    )
    updated_content = pattern.sub('', content)
    
    # Remove empty year sections
    year_pattern = re.compile(
        '<section class="year-section">.*?<div class="post-list">\s*</div>\s*</section>',
        re.DOTALL
    )
    updated_content = year_pattern.sub('', updated_content)
    
    # Save updated index
    with open(index_path, 'w') as f:
        f.write(updated_content)

def main():
    if len(sys.argv) != 3:
        print("Usage: python delete.py <type> <year/post-name>")
        print("Example: python delete.py essay 2024/my-first-post")
        print("Example: python delete.py book 2024/book-review")
        sys.exit(1)
    
    post_type = sys.argv[1].lower()
    if post_type not in ["essay", "book"]:
        print(f"Error: Invalid post type '{post_type}'")
        sys.exit(1)

    # Get post directory
    post_path = sys.argv[2].rstrip('/')
    year, post_name = post_path.split('/')
    post_dir = Path(f'{post_type}s/posts/{year}/{post_name}')
    
    # Check if post exists
    if not post_dir.exists():
        print(f"Error: Post not found at {post_dir}")
        sys.exit(1)
    
    # Get post title
    try:
        with open(post_dir / 'index.html', 'r') as f:
            content = f.read()
            title_match = re.search(r'<h2>(.*?)</h2>', content)
            title = title_match.group(1) if title_match else post_name.replace('-', ' ').title()
    except:
        title = post_name.replace('-', ' ').title()
    
    # Show warning and get confirmation
    print(f"\n⚠️  WARNING: You are about to delete the following {post_type}:")
    print(f"Title: {title}")
    print(f"Path: {post_type}s/posts/{post_path}")
    print("\nThis action cannot be undone!")
    print(f'\nTo confirm deletion, type "DELETE {post_type.upper()}" (all caps):')
    
    confirmation = input("> ")
    
    if confirmation == f"DELETE {post_type.upper()}":
        # Delete post directory
        shutil.rmtree(post_dir)
        
        # Remove from index
        remove_from_index(f'{post_type}s/posts/{post_path}')
        
        print("\n✅ Post deleted successfully!")
        print(f"Note: A backup of {post_type}s/index.html was created before modification.")
    else:
        print("\n❌ Deletion cancelled. Post was not deleted.")

if __name__ == '__main__':
    main()