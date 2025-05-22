import streamlit as st
import os
from pathlib import Path
import markdown
import base64
from PIL import Image

def get_markdown_files():
    """Get list of markdown files in docs directory"""
    docs_dir = Path("docs")
    if not docs_dir.exists():
        st.error("Documentation directory not found!")
        return []
    
    return sorted([f for f in docs_dir.glob("*.md") if f.is_file()])

def read_markdown(file_path):
    """Read and convert markdown file to HTML"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return markdown.markdown(content)
    except Exception as e:
        st.error(f"Error reading {file_path}: {str(e)}")
        return ""

def create_markdown_viewer():
    """Create the markdown viewer UI"""
    st.title("Documentation")
    
    # Get list of markdown files
    md_files = get_markdown_files()
    
    if not md_files:
        st.info("No documentation files found. Please add .md files to the docs directory.")
        return
    
    # Create sidebar with file list
    st.sidebar.header("Documentation")
    
    # Add custom CSS for the list
    st.markdown("""
    <style>
        .doc-list {
            list-style-type: none;
            padding: 0;
        }
        .doc-list li {
            padding: 8px;
            margin: 4px 0;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .doc-list li:hover {
            background-color: #f0f2f6;
        }
        .doc-list li a {
            text-decoration: none;
            color: inherit;
            display: block;
            width: 100%;
            height: 100%;
        }
        .doc-list li a:hover {
            color: #1a73e8;
        }
        .doc-list li a.active {
            color: #1a73e8;
            background-color: #e3f2fd;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Display files as a static list
    st.sidebar.markdown("""
    <ul class="doc-list">
    """, unsafe_allow_html=True)
    
    # Find index.md and show it first
    index_file = None
    other_files = []
    for file in md_files:
        if file.name == "index.md":
            index_file = file
        else:
            other_files.append(file)
    
    # Show index.md first
    if index_file:
        st.sidebar.markdown(f"""
        <li>
            <a href="?file=index" class="active">
                {index_file.stem.replace("_", " ").title()}
            </a>
        </li>
        """, unsafe_allow_html=True)
    
    # Show other files
    for file in other_files:
        st.sidebar.markdown(f"""
        <li>
            <a href="?file={file.stem}">
                {file.stem.replace("_", " ").title()}
            </a>
        </li>
        """, unsafe_allow_html=True)
    
    st.sidebar.markdown("""
    </ul>
    """, unsafe_allow_html=True)
    
    # Get the file from URL parameters
    file_name = st.query_params.get('file', 'index')
    
    # Find the selected file
    selected_file = None
    for file in md_files:
        if file.stem == file_name:
            selected_file = file
            break
    
    # If no file selected, show index.md
    if not selected_file and index_file:
        selected_file = index_file
    
    # Display selected file
    if selected_file:
        # Read and convert markdown to HTML
        html_content = read_markdown(selected_file)
        
        # Display content
        st.markdown(html_content, unsafe_allow_html=True)

def main():
    """Main entry point for the documentation app"""
    create_markdown_viewer()

if __name__ == "__main__":
    main()
