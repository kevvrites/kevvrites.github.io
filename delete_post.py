#!/usr/bin/env python3
import sys
from pathlib import Path
import shutil
import re

def remove_from_index(post_url):
    """Remove post entry from essays/index.html"""
    index_path = Path('essays/index.html')
    
    # Create backup
    shutil.copy(index_path, index_path.with_suffix('.html.bak'))
    
    with open(index_path, 'r') as f:
        content = f.read()
    
    # Find and remove the post article entry using regex
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
    if len(sys.argv) != 2:
        print("Usage: python delete_post.py <post_url>")
        print("Example: python delete_post.py essays/posts/2024/my-first-post")
        sys.exit(1)
    
    post_url = sys.argv[1].rstrip('/')
    post_path = Path(post_url)
    
    # Check if post exists
    if not post_path.exists():
        print(f"Error: Post not found at {post_url}")
        sys.exit(1)
    
    # Get post title from index.html
    with open(post_path / 'index.html', 'r') as f:
        content = f.read()
        title_match = re.search(r'<h2>(.*?)</h2>', content)
        title = title_match.group(1) if title_match else post_path.name
    
    # Show warning and get confirmation
    print(f"\n⚠️  WARNING: You are about to delete the following post:")
    print(f"Title: {title}")
    print(f"Path: {post_url}")
    print("\nThis action cannot be undone!")
    print('\nTo confirm deletion, type "DELETE POST" (all caps):')
    
    confirmation = input("> ")
    
    if confirmation == "DELETE POST":
        # Delete post directory
        shutil.rmtree(post_path)
        
        # Remove from index
        remove_from_index(post_url)
        
        print("\n✅ Post deleted successfully!")
        print("Note: A backup of essays/index.html was created before modification.")
    else:
        print("\n❌ Deletion cancelled. Post was not deleted.")

if __name__ == '__main__':
    main()
