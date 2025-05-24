# coding: utf-8
import nltk
from nltk.tokenize import sent_tokenize
import re
from config import CHUNK_SIZE, CHUNK_OVERLAP


# Add this at the top of your chunking.py file

# Global variable to store chunk metadata
chunk_metadata = []

# Make sure the required resources are downloaded
def ensure_nltk_resources():
    """Ensure all required NLTK resources are downloaded."""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("Downloading punkt tokenizer")
        nltk.download('punkt')

    # No need to look for punkt_tab, use the standard punkt tokenizer


# Call this function at the beginning of your script
ensure_nltk_resources()


def preprocess_special_content(text):
    """Identify and mark tables (HTML and text-based), lists, and other special content"""
    print("\n--- preprocess_special_content input ---")
    print(text[:200])  # Print the first 200 characters of the input
    print("...")

    # --- Existing logic for HTML tables ---
    html_table_pattern = r'---\s+PROCESSED BLOCK \d+ \(HTML_TABLE\)\s+---.*?(?=---\s+PROCESSED BLOCK)'
    html_tables = re.findall(html_table_pattern, text, re.DOTALL)
    html_table_markers = {}
    for i, table in enumerate(html_tables):
        marker = f"[HTML_TABLE_{i}]"
        text = text.replace(table, marker)
        html_table_markers[marker] = table
        print(f"\n  Found HTML table, replaced with marker: {marker}")

    # --- New logic for text-based tables ---
    text_table_pattern = r'---\s+PROCESSED BLOCK \d+ \(TABLE\)\s+---.*?(?=---\s+PROCESSED BLOCK)'
    text_tables = re.findall(text_table_pattern, text, re.DOTALL)
    text_table_markers = {}
    for i, table in enumerate(text_tables):
        marker = f"[TEXT_TABLE_{i}]"
        text = text.replace(table, marker)
        text_table_markers[marker] = table
        print(f"  Found text table, replaced with marker: {marker}")

    # --- Logic for lists (numbered and bulleted) ---
    list_pattern = r'---\s+PROCESSED BLOCK \d+ \((NUMBERED_LIST|BULLETED_LIST)\)\s+---.*?(?=---\s+PROCESSED BLOCK)'
    lists = re.findall(list_pattern, text, re.DOTALL)
    list_markers = {}
    for i, lst in enumerate(lists):
        marker = f"[{lst.split('(')[1].split(')')[0].upper()}_{i}]"
        text = text.replace(lst, marker)
        list_markers[marker] = lst
        print(f"  Found list, replaced with marker: {marker}")

    # Combine the markers maps
    special_content_map = {**html_table_markers, **text_table_markers, **list_markers}

    print("\n--- preprocess_special_content output ---")
    print(text[:200])  # Print the first 200 characters of the output
    print("...")
    return text, special_content_map

def find_semantic_boundaries(sentences, language='spanish'):
    """Find good semantic break points between sentences"""
    transition_words_es = [
        "Por lo tanto", "En conclusión", "Finalmente", "Asimismo",
        "Por otro lado", "En consecuencia", "Sin embargo",
        "Además", "No obstante", "En resumen", "Es decir"
    ]
    transition_words_en = [
        "Therefore", "In conclusion", "Finally", "Furthermore",
        "On the other hand", "Consequently", "However",
        "Moreover", "Nevertheless", "In summary", "That is"
    ]

    transition_words = transition_words_es if language.startswith('es') else transition_words_en

    boundary_scores = []
    for i, sentence in enumerate(sentences[:-1]):
        score = 0
        # Check for transition words at the beginning of the next sentence
        if i + 1 < len(sentences) and any(sentences[i + 1].lower().startswith(word.lower() + ' ') for word in transition_words):
            score += 5
        # Check for paragraph boundaries (inferred)
        if sentence.endswith(('.', '?', '!')) and len(sentences[i + 1].split()) > 5:
            score += 3
        # Favor breaking at the end of numbered/lettered items
        if re.search(r'^\s*[a-z\d]+\.\s', sentence) or re.search(r'^\s*[\(\)a-z\d]+\s', sentence):
            score += 2
        elif re.search(r'^\s*[-*]\s', sentence):  # Bullet points
            score += 2

        boundary_scores.append(score)

    return boundary_scores


def sentence_based_chunking_with_semantic(text, chunk_size, chunk_overlap, language='spanish'):
    """Sentence-based chunking that considers semantic boundaries."""
    if not text.strip():
        return []

    # Map language codes to NLTK language names
    language_map = {
        'es': 'spanish',
        'en': 'english',
        # Add more mappings as needed
    }

    # Get the appropriate language for NLTK
    nltk_lang = language_map.get(language, 'spanish')  # Default to Spanish

    try:
        # Use the standard punkt tokenizer with language parameter
        sentences = sent_tokenize(text, language=nltk_lang)
    except LookupError:
        # Fallback to default if language-specific tokenizer is not available
        print(f"Warning: Language-specific tokenizer for {language} not found. Using default.")
        sentences = sent_tokenize(text)

    boundary_scores = find_semantic_boundaries(sentences, language)

    section_chunks = []
    current_chunk = ""
    sentences_in_current_chunk = []

    for i, sentence in enumerate(sentences):
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            # Check if there's a good semantic boundary in the current chunk
            best_split_index = -1
            best_split_score = -1
            for j in range(len(sentences_in_current_chunk) - 1, -1, -1):
                index_in_original = sentences.index(sentences_in_current_chunk[j])
                if index_in_original < len(boundary_scores) and boundary_scores[index_in_original] > best_split_score:
                    best_split_score = boundary_scores[index_in_original]
                    best_split_index = j

            if best_split_index > 0:
                # Split at the best semantic boundary found
                split_chunk = " ".join(sentences_in_current_chunk[:best_split_index + 1])
                section_chunks.append(split_chunk)
                overlap_sentences = sentences_in_current_chunk[max(0, best_split_index + 1 - (chunk_overlap // (
                    len(sentences_in_current_chunk[0].split()) + 1) if sentences_in_current_chunk else 1)):]  # Rough overlap by sentences
                current_chunk = " ".join(overlap_sentences + [sentence])
                sentences_in_current_chunk = overlap_sentences + [sentence]
            else:
                # No good semantic boundary found, force split
                section_chunks.append(current_chunk)
                current_chunk = sentence
                sentences_in_current_chunk = [sentence]
        else:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
            sentences_in_current_chunk.append(sentence)

    if current_chunk:
        section_chunks.append(current_chunk)

    return section_chunks


def determine_chunk_size(text_section):
    """Determine optimal chunk size based on content complexity"""
    has_tables = "TABLE" in text_section
    has_lists = "LIST" in text_section
    has_technical_terms = len(re.findall(r'\b[A-ZÑÁÉÍÓÚ]{2,}\b', text_section)) > 5

    base_size = CHUNK_SIZE  # Use the global CHUNK_SIZE from config
    if has_tables:
        return int(base_size * 0.7)
    elif has_lists:
        return int(base_size * 0.8)
    elif has_technical_terms:
        return int(base_size * 0.85)

    return base_size


def detect_document_title(text):
    """Extract document title and return title with remaining text."""
    title_pattern = re.compile(r'^\s*INFORME N°\s+\d+.*$', re.IGNORECASE | re.MULTILINE)
    title_match = title_pattern.search(text)
    if title_match:
        title = title_match.group(0).strip()
        remaining_text = text[title_match.end():]
        print(f"Found Document Title: '{title}'")
        return title, remaining_text
    else:
        print("No Document Title found matching the pattern.")
        return None, text

def find_sections(text):
    """Find all sections in text and return sorted list with positions and headers."""
    section_patterns = [
        re.compile(r'#{1,3}\s+[A-ZÑÁÉÍÓÚ].*$', re.MULTILINE),   # Markdown headings
        re.compile(r'^[IVX]+\.\s+[A-ZÑÁÉÍÓÚ].*$', re.MULTILINE),   # Roman numeral sections
        re.compile(r'^\d+\.\d+\s+[A-ZÑÁÉÍÓÚ].*$', re.MULTILINE),   # Numbered sections
        re.compile(r'^\s*[a-z\d]+\.\s+[A-ZÑÁÉÍÓÚ].*$', re.MULTILINE),   # Lettered/numbered list items as sections
    ]
    
    sections = []
    for pattern in section_patterns:
        sections.extend([(match.start(), match.end(), match.group(0).strip()) for match in pattern.finditer(text)])
    sections.sort(key=lambda x: x[0])   # Sort sections by their starting position
    print(f"Found {len(sections)} sections")
    return sections

def determine_section_level(header):
    """Determine hierarchy level of section header."""
    if re.match(r'^[IVX]+\.', header):
        return 1
    elif re.match(r'^\d+\.\d+', header):
        return 2
    elif re.match(r'^\s*[a-z\d]+\.', header):
        return 3
    else:
        return 1

def build_parent_path(hierarchy_stack):
    """Build breadcrumb-style parent path from hierarchy stack."""
    if not hierarchy_stack:
        return ""
    return " > ".join([h["title"] for h in hierarchy_stack])

def update_hierarchy_stack(hierarchy_stack, section_header, section_level):
    """Update hierarchy stack with new section, removing deeper levels."""
    # Remove deeper levels
    hierarchy_stack = [h for h in hierarchy_stack if h["level"] < section_level]
    # Add current section
    hierarchy_stack.append({"level": section_level, "title": section_header, "type": "Section"})
    return hierarchy_stack

def create_chunk_with_metadata(text, chunk_type, current_metadata, parent_path=None, section_header=None):
    """Create a chunk with appropriate metadata."""
    chunk_meta = current_metadata.copy()
    chunk_meta["Type"] = chunk_type
    if parent_path:
        chunk_meta["Parent"] = parent_path
    if section_header:
        chunk_meta["Section Heading"] = section_header
    return {"text": text, "metadata": chunk_meta}

def process_text_chunks(text, current_metadata, parent_path, language, chunk_overlap):
    """Process text into chunks with metadata."""
    chunks = []
    if text.strip():
        for c in sentence_based_chunking_with_semantic(text, determine_chunk_size(text), chunk_overlap, language):
            chunks.append(create_chunk_with_metadata(c, "Paragraph", current_metadata, parent_path))
            print(f"    Created Paragraph chunk: '{c[:80]}...'")
    return chunks

def add_dates_to_chunks(chunks):
    """Extract dates from chunks and add to metadata."""
    date_pattern = re.compile(r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}', re.IGNORECASE)
    for chunk in chunks:
        date_match = date_pattern.search(chunk["text"])
        if date_match:
            chunk["metadata"]["Date"] = date_match.group(0)
            print(f"  Found Date '{chunk['metadata']['Date']}' in chunk: '{chunk['text'][:50]}...'")

def replace_special_content_markers(chunks, table_map):
    """Replace special content markers in chunks."""
    final_chunks = []
    for chunk in chunks:
        chunk_text = chunk["text"]
        for marker, special_content in table_map.items():
            chunk_text = chunk_text.replace(marker, special_content)
        final_chunks.append({"text": chunk_text, "metadata": chunk["metadata"]})
    return final_chunks

def chunk_text(text, language='spanish'):
    """Split text into chunks with dynamic size and hierarchical structure, extracting metadata."""
    global chunk_metadata
    print(f"\n{'=' * 20} chunk_text called (with hierarchical chunking and metadata) {'=' * 20}")
    processed_text, table_map = preprocess_special_content(text)
    print(f"Number of special content blocks found: {len(table_map)}")

    chunks_with_metadata = []
    current_metadata = {}
    hierarchy_stack = []
    
    # Extract document title
    title, text_to_chunk = detect_document_title(processed_text)
    if title:
        chunks_with_metadata.append(create_chunk_with_metadata(title, "Document Title", {}, section_header=title))
        current_metadata["Document Title"] = title
        hierarchy_stack.append({"level": 0, "title": title, "type": "Document Title"})

    # Find and process sections
    sections = find_sections(text_to_chunk)
    
    start = 0
    for sec_start, sec_end, section_header in sections:
        print(f"\nProcessing section: '{section_header}' (start: {sec_start}, end: {sec_end})")
        
        # Update hierarchy
        section_level = determine_section_level(section_header)
        hierarchy_stack = update_hierarchy_stack(hierarchy_stack, section_header, section_level)
        parent_path = build_parent_path(hierarchy_stack[:-1])  # Exclude current section
        
        # Process text before section
        chunk_before_section = text_to_chunk[start:sec_start].strip()
        if chunk_before_section:
            print(f"  Chunking text before section:\n'{chunk_before_section[:100]}...'")
            chunks_with_metadata.extend(process_text_chunks(chunk_before_section, current_metadata, parent_path, language, CHUNK_OVERLAP))
        
        # Create section chunk
        section_text = section_header + text_to_chunk[sec_start + len(section_header):sec_end].strip()
        chunks_with_metadata.append(create_chunk_with_metadata(section_text, "Section", current_metadata, parent_path, section_header))
        print(f"  Created Section chunk: '{section_text[:100]}...'")
        current_metadata["Section Heading"] = section_header
        start = sec_end

    # Process remaining text
    chunk_after_sections = text_to_chunk[start:].strip()
    if chunk_after_sections:
        print(f"\nChunking text after last section:\n'{chunk_after_sections[:100]}...'")
        parent_path = build_parent_path(hierarchy_stack)
        chunks_with_metadata.extend(process_text_chunks(chunk_after_sections, current_metadata, parent_path, language, CHUNK_OVERLAP))
    else:
        print("No text found after the last section.")

    # Handle case with no sections
    if not sections and text_to_chunk.strip():
        print("\nNo sections found, chunking the entire remaining text.")
        parent_path = build_parent_path(hierarchy_stack)
        chunks_with_metadata.extend(process_text_chunks(text_to_chunk, current_metadata, parent_path, language, CHUNK_OVERLAP))

    # Post-processing
    add_dates_to_chunks(chunks_with_metadata)
    final_chunks_with_metadata = replace_special_content_markers(chunks_with_metadata, table_map)

    # Prepare output
    chunk_texts = [chunk["text"] for chunk in final_chunks_with_metadata]
    chunk_metadata = final_chunks_with_metadata

    print(f"Total number of chunks created: {len(chunk_texts)}")
    return chunk_texts

if __name__ == "__main__":
    from config import CHUNK_SIZE, CHUNK_OVERLAP  # Ensure these are defined
    import re

    # Load the text from the file
    with open("./data/SpanishTextTest.txt", "r", encoding="utf-8") as file:
        text = file.read()

    chunks = chunk_text(text, language='spanish')  # Assuming your file is in Spanish
    print("\nChunks with Hierarchical Structure and Metadata:")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i + 1}:")
        print(f"  Text: {chunk['text']}")
        print(f"  Metadata: {chunk['metadata']}")
        print("---")