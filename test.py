import re

def convert_enumerate(markdown):
    lines = markdown.strip().split('\n')
    output = []
    current_depth = -1
    for line in lines:
        # Check if the line is a bullet point
        match = re.match(r'^(\s*)-\s*(.*)$', line)
        if match:
            leading_whitespace, content = match.groups()
            # Normalize tabs to 4 spaces and calculate current level
            normalized_whitespace = leading_whitespace.replace('\t', '    ')
            current_level = len(normalized_whitespace) // 4
            # Adjust environments based on level change
            if current_level > current_depth:
                # Open new environments
                for _ in range(current_level - current_depth):
                    output.append(r"\begin{enumerate}")
                current_depth = current_level
            elif current_level < current_depth:
                # Close excess environments
                for _ in range(current_depth - current_level):
                    output.append(r"\end{enumerate}")
                current_depth = current_level

            # Add the current item
            output.append(r"\item " + content.strip())
        else:
            # Non-bullet line: close all environments first if any are open
            if current_depth != -1:
                for _ in range(current_depth + 1):
                    output.append(r"\end{enumerate}")
                current_depth = -1
            # Add the original line as-is
            output.append(line)
    
    # Close any remaining environments after processing all lines
    if current_depth != -1:
        for _ in range(current_depth + 1):
            output.append(r"\end{enumerate}")

    return '\n'.join(output)

markdown="""
- item1
	- subitem1
	- subitem2
		- subsubitem
		- ...
- item2
	- subitem
- item3
"""

markdown2="""
- **随机存取**: 存储单元的访问时间与其物理位置无关;
- **串行访问**: 对于存储单元的访问必须按照物理地址的顺序寻址; 分为两种: 
	- 完全按照物理地址顺序寻址的访问称为**顺序存取**; 
	- **直接存取**: 先寻找存储器中某个区域, 再在该区域中进行顺序查找;
"""

print(convert_enumerate(markdown2))

