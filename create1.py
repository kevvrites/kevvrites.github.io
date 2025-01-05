#!/usr/bin/env python3
import sys
import shutil
from pathlib import Path
from datetime import datetime
import re

def slugify(title):
    """Convert title to URL-friendly slug."""
    return re.sub(r'[^\w\s-]', '', title.lower().strip()).replace(' ', '-')

def convert_to_utf8(source_file, dest_file):
    """Copy file and convert to UTF-8 encoding."""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(source_file, 'r', encoding=encoding) as f:
                content = f.read()
                with open(dest_file, 'w', encoding='utf-8') as out:
                    out.write(content)
                return True
        except UnicodeDecodeError:
            continue
    return False

def validate_book_name(name):
    """Validate that book post name follows the 'title-by-author' format."""
    parts = name.split('-by-')
    if len(parts) != 2:
        return False
    return all(part.strip() for part in parts)

def create_post(post_type, source_file):
    """Create a new post directory and copy source file."""
    # Create directory name from file name
    post_name = slugify(source_file.stem)
    
    # Validate book review naming convention
    if post_type == "book" and not validate_book_name(post_name):
        print("Error: Book review filename must be in format: 'Book-Title-by-Author-Name.txt'")
        print("Example: The-Great-Gatsby-by-F-Scott-Fitzgerald.txt")
        sys.exit(1)
    
    current_year = str(datetime.now().year)
    
    # Set base directory based on post type
    if post_type == "essay":
        base_dir = "essays"
    elif post_type == "book":
        base_dir = "books"
    else:
        print(f"Error: Invalid post type '{post_type}'")
        sys.exit(1)
    
    post_dir = Path(f'{base_dir}/posts/{current_year}/{post_name}')

    # Check if post already exists
    if post_dir.exists():
        print(f"Error: Post already exists at {post_dir}")
        print("Use update_post.py to update an existing post")
        sys.exit(1)

    # Create directory and copy file
    post_dir.mkdir(parents=True)
    if not convert_to_utf8(source_file, post_dir / 'source.txt'):
        print("Error: Could not read file with any known encoding")
        shutil.rmtree(post_dir)  # Clean up
        sys.exit(1)

    print(f"\nPost directory created successfully!")
    print(f"- Location: {post_dir}")
    print(f"- Title: {post_name.replace('-', ' ').title()}")
    print("\nNext steps:")
    print("1. Add date.txt with YYYY-MM-DD format (optional)")
    print("2. Run generate_html.py to create the HTML version")

def main():
    if len(sys.argv) < 3:
        print("Usage: python create.py <type> <path-to-txt-file>")
        print("Example: python create.py essay ~/Downloads/My-Post.txt")
        print("Example: python create.py book ~/Downloads/Book-Review.txt")
        sys.exit(1)

    post_type = sys.argv[1].lower()
    source_file = Path(sys.argv[2]).expanduser()
    
    if not source_file.exists():
        print(f"Error: File not found: {source_file}")
        sys.exit(1)
    
    create_post(post_type, source_file)

if __name__ == '__main__':
    main()