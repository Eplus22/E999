import os
import re

def convert_box(match):
    """Convert Markdown box to LaTeX subbox."""
    title = match.group(1).strip()
    content = match.group(2).strip()
    return f"\\begin{{subbox}}{{{title}}}\n{content}\n\\end{{subbox}}"

def md_to_tex(md_content):
    """Convert Markdown content to LaTeX."""

    # Convert headings (# to \section, ## to \subsection, ### to \subsubsection)
    md_content = re.sub(r'###\s*(.*)', r'\\subsubsection{\1}', md_content)
    md_content = re.sub(r'##\s*(.*)', r'\\subsection{\1}', md_content)
    md_content = re.sub(r'#\s*(.*)', r'\\section{\1}', md_content)

    # Convert unordered lists (- to \item)
    md_content = re.sub(r'(?m)^\s*-\s+(.*)', r'\\item \1', md_content)

    # Surround \item with itemize environment
    md_content = re.sub(r'\\item (.*)(?=\n|$)', r'\\begin{itemize}\n\\item \1\n\\end{itemize}', md_content)

    # Convert box sections surrounded by `---`
    box_pattern = re.compile(r'---\n(.*?)\n(.*?)\n---', re.DOTALL)
    tex_content = re.sub(box_pattern, convert_box, md_content)

    # Additional conversion rules can be added here
    
    return tex_content

def convert_md_to_tex(md_file, tex_file):
    """Read the markdown file, convert it to LaTeX, and save the result."""
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    tex_content = md_to_tex(md_content)

    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(tex_content)

def convert_all_md_files():
    """Convert all .md files in the current directory to .tex files."""
    for file in os.listdir('.'):
        if file.endswith('CheatSheet.md'):
            tex_file = file.replace('.md', '.tex')
            convert_md_to_tex(file, tex_file)
            print(f"Converted {file} to {tex_file}")

if __name__ == "__main__":
    convert_all_md_files()
