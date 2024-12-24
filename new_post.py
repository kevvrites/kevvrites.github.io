#!/usr/bin/env python3
import sys
import shutil
from pathlib import Path
import re

def slugify(title):
    """Convert title to URL-friendly slug."""
    # Remove special characters and convert spaces to hyphens
    return re.sub(r'[^\w\s-]', '', title.lower().strip()).replace(' ', '-')

def main():
    if len(sys.argv) != 2:
        print("Usage: python new_post.py <path-to-txt-file>")
        print("Example: python new_post.py ~/Downloads/Holiday-Thoughts.txt")
        sys.exit(1)
    
    # Get source file path
    source_file = Path(sys.argv[1]).expanduser()
    if not source_file.exists():
        print(f"Error: File not found: {source_file}")
        sys.exit(1)
    
    # Create post directory name from file name
    post_name = slugify(source_file.stem)
    
    # Create post directory
    post_dir = Path(f'essays/posts/2024/{post_name}')
    post_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy file as source.txt
    shutil.copy(source_file, post_dir / 'source.txt')
    
    # Run create_post.py
    import subprocess
    subprocess.run(['python3', 'create_post.py', f'2024/{post_name}'])

if __name__ == '__main__':
    main()
