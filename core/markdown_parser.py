import re
import os

def split_markdown_file_and_extract_tables(file_path, output_file_path="markdown_blocks.txt"):
    """
    Reads a Markdown file, extracts tables as complete blocks, splits the remaining text,
    and interleaves them to maintain order. Writes the output to a file.
    Includes detailed debug print statements.

    Args:
        file_path (str): Path to the input Markdown file.
        output_file_path (str, optional): Path to the output text file.
                                          Defaults to "markdown_blocks.txt".
    """

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        print(f"[Markdown Processor] Successfully loaded Markdown content from: {file_path}")
    except FileNotFoundError:
        print(f"[Markdown Processor] ERROR: File not found at: {file_path}")
        return
    except Exception as e:
        print(f"[Markdown Processor] ERROR: Error reading file: {e}")
        return

    print("[Markdown Processor] Starting table extraction and aware splitting...")

    table_pattern = re.compile(r'(\|.*?\|\n(?:\|[-]+\|[-]+\|\n)?(?:\|.*?\|\n)+)', re.DOTALL)

    # Extract tables
    table_matches = list(table_pattern.finditer(markdown_content))
    tables = [match.group(0).strip() for match in table_matches]
    table_ranges = [(match.start(), match.end()) for match in table_matches]

    print(f"[Markdown Processor] Found {len(tables)} tables.")

    # Remove tables from the main content
    content_without_tables = markdown_content
    for start, end in reversed(table_ranges):
        content_without_tables = content_without_tables[:start] + content_without_tables[end:]

    # Split the remaining content
    split_pattern = re.compile(r'\n\n+|---\n+')
    text_blocks = split_pattern.split(content_without_tables)
    text_blocks = [block.strip() for block in text_blocks if block.strip()]

    print(f"[Markdown Processor] Split non-table content into {len(text_blocks)} text blocks.")

    # Reconstruct blocks by interleaving tables and text
    blocks = []
    table_index = 0
    text_index = 0
    next_expected_pos = 0  # Keep track of the next expected position in the original document

    while text_index < len(text_blocks) or table_index < len(tables):
        # Add text blocks if they come next
        if text_index < len(text_blocks) and (table_index == len(tables) or next_expected_pos <= table_ranges[table_index][0]):
            blocks.append(text_blocks[text_index])
            next_expected_pos += len(text_blocks[text_index]) + (2 if "\n\n" in content_without_tables else 0)  # Account for splitters
            text_index += 1
        # Add tables if they come next
        elif table_index < len(tables):
            blocks.append(tables[table_index])
            next_expected_pos = table_ranges[table_index][1]
            table_index += 1

    print(f"[Markdown Processor] Reconstructed {len(blocks)} total blocks.")
    return blocks


def identify_block_type(block):
    """
    Identifies the type of content in a Markdown block.

    Args:
        block (str): A block of Markdown text.

    Returns:
        str: The identified type of the block ('text', 'table', 'latex', 'heading', 'html_table' etc.).
    """

    if re.match(r'(\|.*?\|\n(?:\|[-]+\|[-]+\|\n)?(?:\|.*?\|\n)+)', block, re.DOTALL):
        return 'table'  # Markdown table
    elif re.search(r'<table', block, re.IGNORECASE) and re.search(r'</table>', block, re.IGNORECASE):
        return 'html_table' # HTML table
    elif re.search(r'\$\$|\$.*\$', block):  # Simple check for LaTeX delimiters
        return 'latex'
    elif re.match(r'#+\s', block):  # Matches lines starting with one or more '#' (headings)
        return 'heading'
    else:
        return 'text'

def process_markdown_blocks(blocks, output_file_path="processed_blocks.txt"):
    """
    Identifies the type of each block and writes the block with its type to a file.

    Args:
        blocks (list): List of Markdown blocks.
        output_file_path (str, optional): Path to the output text file.
                                          Defaults to "processed_blocks.txt".
    """

    print("[Block Processor] Starting block type identification...")
    processed_blocks = []
    for i, block in enumerate(blocks):
        block_type = identify_block_type(block)
        processed_blocks.append((block_type, block))
        print(f"[Block Processor] Block {i + 1} is of type: {block_type}")

    print("[Block Processor] Writing processed blocks to output file...")
    try:
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            for i, (block_type, block) in enumerate(processed_blocks):
                outfile.write(f"--- BLOCK {i + 1} ({block_type.upper()}) ---\n")
                outfile.write(block)
                outfile.write("\n\n")
        print(f"[Block Processor] Successfully wrote {len(processed_blocks)} processed blocks to: {output_file_path}")

    except Exception as e:
        print(f"[Block Processor] ERROR: Error writing to output file: {e}")


# --- Placeholder functions for table conversion ---
def convert_markdown_table_to_text(markdown_table, surrounding_text=""):
    """Converts a Markdown table to a more readable text format (improved)."""
    lines = markdown_table.strip().split('\n')
    if not lines:
        return ""

    header = [h.strip() for h in re.split(r'\|', lines[0])[1:-1]]
    separator = None  # Initialize separator to None
    if len(lines) > 1:
        separator = lines[1] if all(c in ['-', ':', '|', ' '] for c in lines[1]) else None
    data_rows = [re.split(r'\|', line)[1:-1] for line in lines[2:] if '|' in line]

    output = ""
    if surrounding_text:
        output += f"Table related to: {surrounding_text}. "

    if header:
        output += "Columns: " + ", ".join(header) + ". "

    for i, row in enumerate(data_rows):
        row_data = [d.strip() for d in row]
        row_description = ", ".join(f"{h}: {d}" for h, d in zip(header, row_data)) if header and len(header) == len(row_data) else ", ".join(row_data)
        output += f"Row {i+1}: {row_description}. "

    return output.strip()

def convert_html_table_to_text(html_table, surrounding_text=""):
    """Converts an HTML table to a more readable text format (more robust)."""

    table_data = []
    headers = []
    max_cols = 0
    table_summary = ""

    try:
        # 0. Extract Table Summary (if any)
        summary_match = re.search(r'<table.*?summary="(.*?)"', html_table, re.IGNORECASE)
        if summary_match:
            table_summary = f"Table Summary: {summary_match.group(1)}. "

        # 1. Extract Rows
        rows = re.findall(r'<tr.*?>(.*?)</tr>', html_table, re.IGNORECASE | re.DOTALL)

        for row in rows:
            cells = re.findall(r'<t[dh].*?>(.*?)</t[dh]>', row, re.IGNORECASE | re.DOTALL)
            cleaned_cells = []
            col_count = 0
            for cell in cells:
                clean_cell = re.sub(r'<.*?>', '', cell).strip()
                colspan_match = re.search(r'<t[dh].*?colspan="(\d+)"', cell, re.IGNORECASE)
                colspan = int(colspan_match.group(1)) if colspan_match else 1
                cleaned_cells.extend([clean_cell] * colspan)
                col_count += colspan
            max_cols = max(max_cols, col_count)
            table_data.append(cleaned_cells)

        # 2. Extract Headers (Improved)
        if table_data:
            header_row_index = 0
            # Heuristic: Check for TH in first few rows
            for i, row in enumerate(rows[:2]):  # Check only the first 2 rows
                if any("<th" in cell.lower() for cell in re.findall(r'<t[dh].*?>(.*?)</t[dh]>', row, re.IGNORECASE | re.DOTALL)):
                    header_row_index = i
                    break

            header_cells = re.findall(r'<th.*?>(.*?)</th>', rows[header_row_index], re.IGNORECASE | re.DOTALL)
            if header_cells:
                headers = [re.sub(r'<.*?>', '', cell).strip() for cell in header_cells]
                # Remove header row from table data if it's not the first row
                if header_row_index > 0:
                    table_data.pop(header_row_index)
            else:
                headers = table_data[0]
                table_data = table_data[1:]

        headers = headers[:max_cols]

        # 3. Build Textual Representation
        text_output = table_summary  # Add table summary at the beginning
        if surrounding_text:
            text_output += f"Context: {surrounding_text}. "  # Add surrounding text
        for row in table_data:
            row = row[:max_cols]
            row_text = ", ".join(f"{h}: {d}" for h, d in zip(headers, row))
            text_output += row_text + ". "

        return text_output.strip()

    except Exception as e:
        print(f"[HTML Table Converter] Error processing table: {e}")
        return "Error processing HTML table."
    
def process_content_blocks(processed_blocks, output_file_path="processed_content.txt"):
    """
    Processes each block based on its identified type, passing the preceding
    block's content as context to table conversion functions.

    Args:
        processed_blocks (list): List of tuples, where each tuple is (block_type, block_content).
        output_file_path (str, optional): Path to the output text file.
                                          Defaults to "processed_content.txt".
    """

    print("[Content Processor] Starting content processing with context...")
    final_blocks = []
    previous_block_content = ""
    for i, (block_type, block_content) in enumerate(processed_blocks):
        print(f"[Content Processor] Processing Block {i + 1} (Type: {block_type.upper()})...")
        if block_type == 'table':
            processed_content = convert_markdown_table_to_text(block_content, previous_block_content)
        elif block_type == 'html_table':
            processed_content = convert_html_table_to_text(block_content, previous_block_content)
        elif block_type == 'latex':
            processed_content = block_content  # Keep LaTeX as is for now
        elif block_type == 'heading':
            processed_content = block_content  # Keep headings as is
        else:  # block_type == 'text'
            processed_content = block_content  # Keep text as is

        final_blocks.append((block_type, processed_content))
        previous_block_content = block_content

    print("[Content Processor] Writing processed content with context to output file...")
    try:
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            for i, (block_type, processed_content) in enumerate(final_blocks):
                outfile.write(f"--- PROCESSED BLOCK {i + 1} ({block_type.upper()}) ---\n")
                outfile.write(processed_content)
                outfile.write("\n\n")
        print(f"[Content Processor] Successfully wrote {len(final_blocks)} processed blocks to: {output_file_path}")

    except Exception as e:
        print(f"[Content Processor] ERROR: Error writing to output file: {e}")

    return final_blocks

# Make sure the convert_markdown_table_to_text and convert_html_table_to_text
# functions now accept the 'surrounding_text' argument.

if __name__ == "__main__":
    markdown_file_path = "./data/SpanishRoadContract.md"
    output_blocks_file = "output_blocks.txt"
    output_processed_file = "output_processed.txt"
    output_content_file = "SpanishRoadContract.txt"

    blocks = split_markdown_file_and_extract_tables(markdown_file_path, output_blocks_file)
    if blocks:
        processed_blocks = []
        for block in blocks:
            block_type = identify_block_type(block)
            processed_blocks.append((block_type, block))

        final_blocks = process_content_blocks(processed_blocks, output_content_file)
        print("\n[Main Process] Markdown processing complete with context.")
        print(f"[Main Process] Check '{output_content_file}' for the final processed content with context.")
    else:
        print("\n[Main Process] Markdown processing failed. No further processing.")