"""
Markdown to LaTeX Converter
===========================

This script converts Markdown files to LaTeX format with special handling for:
- Callouts (theorems, examples, warnings, etc.)
- Math expressions
- Images and code blocks
- Tables and lists
- Special formatting (bold, italics, etc.)
"""

# Standard Library Imports
import re
import argparse
import os
import glob

# =============================================================================
# REGEX PATTERNS DEFINITION
# =============================================================================
# Define regex patterns for various Markdown elements to be converted to LaTeX

patterns = {
    # Callouts without content (single line)
    'cor_no_content': re.compile(r'>\s*\[!cor\]\s*(.+)', re.MULTILINE),
    'example_no_content': re.compile(r'>\s*\[!example\]\s*(.+)', re.MULTILINE),
    'warning_no_content': re.compile(r'>\s*\[!warning\]\s*(.+)', re.MULTILINE),
    'bigexample_no_content': re.compile(r'>\s*\[!iexample\]\s*(.+)', re.MULTILINE),
    'lemma_no_content': re.compile(r'>\s*\[!lemma\]\s*(.+)', re.MULTILINE),
    'note_no_content': re.compile(r'>\s*\[!note\]\s*(.+)', re.MULTILINE),

    # Callouts with titles
    'example_with_title': re.compile(r'>\s*\[!example\]\s*(.+?)\s*\@\s*(.*)', re.MULTILINE),
    'bigexample_with_title': re.compile(r'>\s*\[!iexample\]\s*(.+?)\s*\@\s*(.*)', re.MULTILINE),
    'lemma_with_title': re.compile(r'>\s*\[!lemma\]\s*(.+?)\s*\@\s*(.*)', re.MULTILINE),
    'note_with_title': re.compile(r'>\s*\[!note\]\s*(.+?)\s*\@\s*(.*)', re.MULTILINE),

    # Callouts with content blocks
    'summary_with_content': re.compile(r'>\s*\[!summary\]\s*(.+?)\n(>(?:[^\n]+\n?)+)', re.MULTILINE),
    'algo_with_content': re.compile(r'>\s*\[!algorithm\]\s*(.+?)\n(>(?:[^\n]+\n?)+)', re.MULTILINE),
    'target_with_content': re.compile(r'>\s*\[!target\]\s*(.+?)\n(>(?:[^\n]+\n?)+)', re.MULTILINE),
    'concept_with_content': re.compile(r'>\s*\[!concept\]\s*(.+?)\n(>(?:[^\n]+\n?)+)', re.MULTILINE),

    # Special elements
    'hint': re.compile(r'>\s*\[!hint\]\s*(.+)', re.MULTILINE),
    'math': re.compile(r'\$\$(.*?)\$\$', re.MULTILINE | re.DOTALL),
    'enumerate': re.compile(r'^(?:-\s.+\n?)+', re.MULTILINE),
    'fine': re.compile(r'\[fine\](.+?)\[fine\]', re.MULTILINE),
    'fine_with_percent': re.compile(r'%%(.+?)%%', re.MULTILINE),
    'fine_with_num': re.compile(r'%%\s*\[(-?\d*\.?\d+)\]\s*(.+?)\s*%%', re.MULTILINE),
    'href': re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
    'qed': re.compile(r'\b(Q\.?E\.?D\.?)(\.|!|\?|\s)*$', re.MULTILINE),
    'quote': re.compile(r'^(>.*(?:\n|$))+', re.MULTILINE),
    'fullwidth_block': re.compile(r'~~(?:u\n|\n)(.*?)~~(?:d\n|\n)', re.DOTALL)
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def convert_tags(text):
    """Convert custom warning tags to LaTeX equivalents."""
    text = re.sub(r'#Warning', r'!!', text)
    return text

def protect_math_symbols(text):
    """Protect special math symbols from being processed by other conversions."""
    def replace_symbols(match):
        content = match.group(2)
        content = (
            content.replace("*", "MATHSTAR")
            .replace(">", "ANGLE")
            .replace("[", "LEFTBRACKET")
            .replace("]", "RIGHTBRACKET")
            .replace("-", "MINUS")
        )
        return f"{match.group(1)}{content}{match.group(3)}"

    text = re.sub(r'(\$)(.*?)(\$)', replace_symbols, text)
    text = re.sub(r'(\$\$)(.*?)(\$\$)', replace_symbols, text, flags=re.DOTALL)
    return text

def restore_math_symbols(text):
    """Restore protected math symbols after processing."""
    text = (
        text.replace("MATHSTAR", "*")
        .replace("ANGLE", ">")
        .replace("LEFTBRACKET", "[")
        .replace("RIGHTBRACKET", "]")
        .replace("MINUS", "-")
    )
    return text

def clean_callout_content(content):
    """Clean callout content by removing Markdown formatting."""
    lines = content.splitlines()
    cleaned_lines = [re.sub(r'^> *', '', line) for line in lines]
    return '\n'.join(cleaned_lines)

def wrap_latex_environment(env_name, content, options=None, blank=True, space="5pt"):
    """
    Wrap content in a LaTeX environment with optional settings.
    
    Args:
        env_name: Name of the LaTeX environment
        content: Content to wrap
        options: Optional parameters for the environment
        blank: Add vertical space around the environment
        space: Amount of vertical space to add
    """
    env_start = f"\\begin{{{env_name}}}"
    env_end = f"\\end{{{env_name}}}"
    
    if options:
        env_start = f"\\begin{{{env_name}}}[{options}]"
    
    if blank:
        latex_code = (
            f"\\vspace{{{space}}}\n"
            f"{env_start}\n"
            f"{content}\n"
            f"{env_end}\n"
            f"\\vspace{{{space}}}\n"
        )
    else:
        latex_code = f"{env_start}\n{content}\n{env_end}"
    
    return latex_code

# =============================================================================
# CORE CONVERSION FUNCTIONS
# =============================================================================

def convert_callouts(text):
    """Convert all callout types to their LaTeX equivalents."""
    # Callouts with titles
    text = patterns['note_with_title'].sub(lambda m: wrap_latex_environment('theorem', clean_callout_content(m.group(2)), m.group(1)), text)
    text = patterns['example_with_title'].sub(lambda m: wrap_latex_environment('eg', clean_callout_content(m.group(2)), m.group(1)), text)
    text = patterns['bigexample_with_title'].sub(lambda m: wrap_latex_environment('xeg', clean_callout_content(m.group(2)), m.group(1)), text)
    text = patterns['lemma_with_title'].sub(lambda m: wrap_latex_environment('lemma', clean_callout_content(m.group(2)), m.group(1)), text)

    # Callouts without content
    text = patterns['note_no_content'].sub(lambda m: wrap_latex_environment('theorem', m.group(1)), text)
    text = patterns['cor_no_content'].sub(lambda m: wrap_latex_environment('corollary', m.group(1)), text)
    text = patterns['example_no_content'].sub(lambda m: wrap_latex_environment('eg', m.group(1)), text)
    text = patterns['warning_no_content'].sub(lambda m: wrap_latex_environment('warning', m.group(1)), text)
    text = patterns['bigexample_no_content'].sub(lambda m: wrap_latex_environment('xeg', m.group(1)), text)
    text = patterns['lemma_no_content'].sub(lambda m: wrap_latex_environment('lemma', m.group(1)), text)

    # Callouts with content blocks
    text = patterns['summary_with_content'].sub(lambda m: wrap_latex_environment('definition', clean_callout_content(m.group(2)), m.group(1)), text)
    text = patterns['algo_with_content'].sub(lambda m: wrap_latex_environment('algo', clean_callout_content(m.group(2)), m.group(1)), text)
    text = patterns['target_with_content'].sub(lambda m: wrap_latex_environment('target', clean_callout_content(m.group(2)), m.group(1)), text)
    text = patterns['concept_with_content'].sub(lambda m: wrap_latex_environment('concept', clean_callout_content(m.group(2)), m.group(1)), text)

    # Special elements
    text = patterns['hint'].sub(lambda m: f"\\fine{{{m.group(1)}}}", text)
    text = patterns['fine'].sub(lambda m: f"\\fine{{{m.group(1)}}}", text)
    text = patterns['fine_with_num'].sub(lambda m: f"\\fine[{m.group(1)}]{{{m.group(2)}}}", text)
    text = patterns['fine_with_percent'].sub(lambda m: f"\\fine{{{m.group(1)}}}", text)
    text = patterns['href'].sub(lambda m: f"\\href{{{m.group(2).replace('#', 'TheSharp').replace('%', 'ThePercent')}}}{{{m.group(1)}}}", text)
    text = text.replace('TheSharp', '\\#').replace('ThePercent', '\\%')
    text = patterns['qed'].sub(r'\\qedz\n', text)
    text = patterns['quote'].sub(lambda m: wrap_latex_environment('zoe',
        '\n'.join([line.strip('> ').strip() for line in m.group(0).splitlines()])), text)
    text = patterns['fullwidth_block'].sub(lambda m: wrap_latex_environment('fullwidth', m.group(1).strip()), text)
    
    return text

def convert_math(text):
    """Convert math expressions to LaTeX format."""
    text = re.sub(r'\n?\$\$(.*?)\$\$', r'\\begin{equation*}\1\\end{equation*}', text, flags=re.DOTALL)
    return text

def convert_images(text):
    """Convert image references to LaTeX figure environments."""
    def replace_match(match):
        raw_path = match.group(1).strip()
        options = match.group(2)

        if raw_path.startswith("../Assets/"):
            path = raw_path[3:]
        else:
            path = f"Assets/Images/{raw_path}"

        if options and "fullwidth" in options:
            return f"{{\\centering\\begin{{figure*}}[h]\n\\includegraphics[width=0.5\\textwidth]{{{path}}}\n\\end{{figure*}}}}"
        else:
            return f"\\begin{{figure*}}[h]\n\\centering\n\\includegraphics[width=0.5\\textwidth]{{{path}}}\n\\end{{figure*}}\\par"

    pattern = r'!\[\[([^\|\]]+)(?:\|([^]]+))?\]\]'
    return re.sub(pattern, replace_match, text)

def convert_codes(text):
    """Convert code references to LaTeX code inclusion commands."""
    code_pattern = re.compile(r'\[\[(.+?)\|(.+?)(?:\|(\d+):(\d+))?\]\]')

    def escape_underscores(string):
        return string.replace("_", r"\_")

    def process_path(path):
        path = re.sub(r'^\.\.?/', '', path)
        if not path.startswith('Assets/Codes/'):
            path = f"Assets/Codes/{path}"
        return path

    def replacement(match):
        file_path = match.group(1)
        label = match.group(2)
        start_line = match.group(3) or "1"
        end_line = match.group(4) or "500"
        
        file_name = file_path.split('/')[-1]
        extension = os.path.splitext(file_name)[1][1:]
        
        return (f"\\includecode[{extension}]"
                f"{{{escape_underscores(label)}}}"
                f"{{{start_line}}}"
                f"{{{end_line}}}"
                f"{{{process_path(escape_underscores(file_path))}}}")

    return code_pattern.sub(replacement, text)

def escape_latex_special_chars(text):
    """Escape special LaTeX characters in regular text."""
    replacements = {
        '\\': r'\textbackslash',
        '#': r'\#',
        '$': r'\$',
        '%': r'\%',
        '&': r'\&',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\~',
        '^': r'\^'
    }
    for char, escaped in replacements.items():
        text = text.replace(char, escaped)
    return text

def convert_code_pieces(text):
    """Convert inline and block code snippets to LaTeX format."""
    text = re.sub(r'```(.*?)```', 
                 r'\\begin{lstlisting}[style=py,breaklines=true,breakatwhitespace=true,lineskip=-0.3ex,xleftmargin=2em,xrightmargin=2em]\1\\end{lstlisting}', 
                 text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+?)`', 
                 lambda m: r'\texttt{' + escape_latex_special_chars(m.group(1)) + r'}', 
                 text)
    return text

def convert_tables(text):
    """Convert Markdown tables to LaTeX tabular environments."""
    tables = extract_markdown_tables(text)

    for i, table in enumerate(tables):
        placeholder = f"@@TABLE_{i}@@"
        text = text.replace(table, placeholder)

    latex_tables = []
    for table in tables:
        latex_table = markdown_to_latex_table(table)
        latex_tables.append(latex_table)

    for i, latex_table in enumerate(latex_tables):
        placeholder = f"@@TABLE_{i}@@"
        text = text.replace(placeholder, latex_table)

    return text

def extract_markdown_tables(text):
    """Extract all Markdown tables from the text."""
    table_pattern = re.compile(
        r'(\|.*\|\n\|[-:| ]+\|[\s\S]*?)(?=\n\n|\Z)', re.MULTILINE
    )
    return table_pattern.findall(text)

def markdown_to_latex_table(markdown_table):
    """Convert a single Markdown table to LaTeX format."""
    lines = markdown_table.strip().split('\n')
    header = lines[0]
    separator = lines[1]
    data_rows = lines[2:]
    num_columns = len(re.findall(r'\|\s*([^|]+)\s*', header))
    
    latex_table = "\\vspace{10pt}{\\centering\n\\begin{tabular}{" + "c|" * (num_columns - 1) + "c}\n"
    header_cells = re.findall(r'\|\s*([^|]+)\s*', header)
    latex_table += " & ".join(header_cells) + " \\\\\n"
    latex_table += "\\hline\n"
    
    for row in data_rows[:-1]:
        row_cells = re.findall(r'\|\s*([^|]+)\s*', row)
        latex_table += " & ".join(row_cells) + " \\\\\n"
        latex_table += "\\hline\n"
    
    row_cells = re.findall(r'\|\s*([^|]+)\s*', data_rows[-1])
    latex_table += " & ".join(row_cells) + " \\\\\n"
    latex_table += "\\end{tabular}\\par}\\vspace{10pt}"
    
    return latex_table

def convert_enumerate(markdown):
    """Convert Markdown lists to LaTeX enumerate environments with proper nesting."""
    lines = markdown.strip().split('\n')
    output = []
    current_depth = -1
    
    for line in lines:
        match = re.match(r'^(\s*)-\s*(.*)$', line)
        if match:
            leading_whitespace, content = match.groups()
            normalized_whitespace = leading_whitespace.replace('\t', '    ')
            current_level = len(normalized_whitespace) // 4
            
            if current_level > current_depth:
                for _ in range(current_level - current_depth):
                    output.append(r"\begin{enumerate}[leftmargin=3.0em]")
                current_depth = current_level
            elif current_level < current_depth:
                for _ in range(current_depth - current_level):
                    output.append(r"\end{enumerate}")
                current_depth = current_level
                
            output.append(r"\item " + content.strip())
        else:
            if current_depth != -1:
                for _ in range(current_depth + 1):
                    output.append(r"\end{enumerate}")
                current_depth = -1
            output.append(line)
    
    if current_depth != -1:
        for _ in range(current_depth + 1):
            output.append(r"\end{enumerate}")
    
    return '\n'.join(output)

# =============================================================================
# MAIN CONVERSION PIPELINE
# =============================================================================

def convert_markdown(text):
    """Main function to convert Markdown to LaTeX with proper processing order."""
    # Step 1: Protect code blocks and inline code with placeholders
    code_blocks = []
    inline_codes = []
    
    def code_block_replacer(match):
        code_blocks.append(match.group(0))
        return f"@@CODE_BLOCK_{len(code_blocks)-1}@@"
    
    def inline_code_replacer(match):
        inline_codes.append(match.group(0))
        return f"@@INLINE_CODE_{len(inline_codes)-1}@@"
    
    text = re.sub(r'```.*?```', code_block_replacer, text, flags=re.DOTALL)
    text = re.sub(r'`[^`]+?`', inline_code_replacer, text)

    # Step 2: Convert various Markdown elements
    text = convert_tags(text)
    text = convert_images(text)
    text = convert_codes(text)
    text = convert_tables(text)
    
    # Text formatting and headers
    text = re.sub(r'<u>(.*?)</u>', r'\\underline{\1}', text)
    text = re.sub(r'<font color="#ff0000">(.*?)</font>', r'\\textcolor{red}{\1}', text)
    text = re.sub(r'^####\s*(.+)', r'\\subsubsection{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^###\s*(.+)', r'\\subsection{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^##\s*(.+)', r'\\section{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^#\s*(.+)', r'\\section{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'\*(.+?)\*', r'\\textit{\1}', text)
    
    # Horizontal rules
    text = re.sub(r'^\s*---\s*$', r'\n\\noindent\\rule{\\textwidth}{1pt}\n', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*!---\s*$', r'\n\\begin{fullwidth}\\noindent\\rule{0.75\\linewidth}{1pt}\\end{fullwidth}\n', text, flags=re.MULTILINE)
    
    # Step 3: Convert callouts and lists
    text = convert_callouts(text)
    text = convert_enumerate(text)

    # Step 4: Restore and convert code blocks
    for i, code in enumerate(code_blocks):
        text = text.replace(f'@@CODE_BLOCK_{i}@@', code)
    for i, code in enumerate(inline_codes):
        text = text.replace(f'@@INLINE_CODE_{i}@@', code)
    
    text = convert_code_pieces(text)
    return text

# =============================================================================
# FILE HANDLING FUNCTIONS
# =============================================================================

def ensure_texfiles_subfolder():
    """Ensure the output directory for LaTeX files exists."""
    if not os.path.exists('../TeXFiles'):
        os.makedirs('../TeXFiles')

def get_output_file_path(md_file):
    """Generate output path for converted LaTeX file."""
    return os.path.join('../TeXFiles', md_file.replace('.md', '.tex'))

def convert_md_to_tex(input_file, output_file):
    """Convert a single Markdown file to LaTeX format."""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    content = protect_math_symbols(content)
    content = convert_markdown(content)
    content = convert_math(content)
    content = restore_math_symbols(content)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

def convert_all_md_in_directory():
    """Convert all Markdown files in the current directory to LaTeX."""
    ensure_texfiles_subfolder()
    md_files = glob.glob("*.md")
    
    for md_file in md_files:
        output_file = get_output_file_path(md_file)
        print(f"Converting {md_file} to {output_file}...")
        convert_md_to_tex(md_file, output_file)
    
    print("Conversion completed for all markdown files in the current directory.")

# =============================================================================
# COMMAND LINE INTERFACE
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert Markdown to LaTeX.')
    parser.add_argument('input', nargs='?', help='Input Markdown file (optional)')
    parser.add_argument('output', nargs='?', help='Output LaTeX file (optional)')
    args = parser.parse_args()

    if args.input and args.output:
        ensure_texfiles_subfolder()
        output_file = get_output_file_path(args.output)
        convert_md_to_tex(args.input, output_file)
    else:
        convert_all_md_in_directory()
