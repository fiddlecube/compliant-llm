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
        }
        .doc-list li:hover {
            background-color: #f0f2f6;
        }
        .doc-list li.active {
            background-color: #e6f7ff;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Get the selected file from URL parameters
    selected_file = st.query_params.get('file', 'index')
    
    # Create list of files with active state
    st.sidebar.markdown("<ul class='doc-list'>", unsafe_allow_html=True)
    for file in md_files:
        file_name = file.stem
        is_active = file.stem == selected_file
        
        # Create a URL-friendly version of the file name
        # url_name = file.stem.replace('_', '-')
        url_name = file_name
        
        st.sidebar.markdown(f"""
            <li class="{'active' if is_active else ''}">
                <a href="?file={url_name}">
                    {file.stem.replace('_', ' ').title()}
                </a>
            </li>
        """, unsafe_allow_html=True)
    st.sidebar.markdown("</ul>", unsafe_allow_html=True)

    # Display selected file
    selected_path = Path("docs") / f"{selected_file}.md"
    if selected_path.exists():
        content = read_markdown(selected_path)
        st.markdown(content, unsafe_allow_html=True)
    else:
        st.error(f"Documentation file '{selected_file}.md' not found!")

def main():
    """Main entry point for the documentation app"""
    create_markdown_viewer()

if __name__ == "__main__":
    main()
