import nltk
from nltk.tokenize import sent_tokenize
import re
from config import CHUNK_SIZE, CHUNK_OVERLAP


# Add this at the top of your chunking.py file


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
    # --- Existing logic for HTML tables ---
    html_table_pattern = r'---\s+PROCESSED BLOCK \d+ \(HTML_TABLE\)\s+---.*?(?=---\s+PROCESSED BLOCK)'
    html_tables = re.findall(html_table_pattern, text, re.DOTALL)
    html_table_markers = {}
    for i, table in enumerate(html_tables):
        marker = f"[HTML_TABLE_{i}]"
        text = text.replace(table, marker)
        html_table_markers[marker] = table

    # --- New logic for text-based tables ---
    text_table_pattern = r'---\s+PROCESSED BLOCK \d+ \(TABLE\)\s+---.*?(?=---\s+PROCESSED BLOCK)'
    text_tables = re.findall(text_table_pattern, text, re.DOTALL)
    text_table_markers = {}
    for i, table in enumerate(text_tables):
        marker = f"[TEXT_TABLE_{i}]"
        text = text.replace(table, marker)
        text_table_markers[marker] = table

    # --- Logic for lists (numbered and bulleted) ---
    list_pattern = r'---\s+PROCESSED BLOCK \d+ \((NUMBERED_LIST|BULLETED_LIST)\)\s+---.*?(?=---\s+PROCESSED BLOCK)'
    lists = re.findall(list_pattern, text, re.DOTALL)
    list_markers = {}
    for i, lst in enumerate(lists):
        marker = f"[{lst.split('(')[1].split(')')[0].upper()}_{i}]"
        text = text.replace(lst, marker)
        list_markers[marker] = lst

    # Combine the markers maps
    special_content_map = {**html_table_markers, **text_table_markers, **list_markers}
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
        if sentence.endswith(('.', '?', '!')) and len(sentences[i+1].split()) > 5:
            score += 3
        # Favor breaking at the end of numbered/lettered items
        if re.search(r'^\s*[a-z\d]+\.\s', sentence) or re.search(r'^\s*[\(\)a-z\d]+\s', sentence):
            score += 2
        elif re.search(r'^\s*[-*]\s', sentence): # Bullet points
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
                split_chunk = " ".join(sentences_in_current_chunk[:best_split_index+1])
                section_chunks.append(split_chunk)
                overlap_sentences = sentences_in_current_chunk[max(0, best_split_index + 1 - (chunk_overlap // (len(sentences_in_current_chunk[0].split()) + 1) if sentences_in_current_chunk else 1)):] # Rough overlap by sentences
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

    base_size = CHUNK_SIZE # Use the global CHUNK_SIZE from config
    if has_tables:
        return int(base_size * 0.7)
    elif has_lists:
        return int(base_size * 0.8)
    elif has_technical_terms:
        return int(base_size * 0.85)

    return base_size

def chunk_text(text, language='spanish'):
    """Split text into chunks with dynamic size based on content."""
    print(f"\n{'='*20} chunk_text called (with dynamic size) {'='*20}")
    processed_text, table_map = preprocess_special_content(text)
    print(f"Number of special content blocks found: {len(table_map)}")

    section_patterns = [
        r'#{1,3}\s+[A-ZÑÁÉÍÓÚ].*$',  # Markdown headings
        r'^[IVX]+\.\s+[A-ZÑÁÉÍÓÚ].*$',  # Roman numeral sections
        r'^\d+\.\d+\s+[A-ZÑÁÉÍÓÚ].*$',    # Numbered sections
        r'^\s*[a-z\d]+\.\s+[A-ZÑÁÉÍÓÚ].*$', # Lettered/numbered list items as sections
        r'^\s*[-*]\s+.*$' # Bullet points as potential sections
    ]

    sections = []
    current_section = ""
    for line in processed_text.split('\n'):
        if any(re.match(pattern, line) for pattern in section_patterns) and current_section.strip():
            sections.append(current_section.strip())
            current_section = line
        else:
            current_section += '\n' + line

    if current_section.strip():
        sections.append(current_section.strip())

    chunks = []
    for section in sections:
        # Determine the chunk size for the current section
        section_chunk_size = determine_chunk_size(section)
        print(f"\nProcessing section (first 50 chars): '{section[:50]}...', determined chunk size: {section_chunk_size}")
        section_chunks = sentence_based_chunking_with_semantic(section, section_chunk_size, CHUNK_OVERLAP, language)
        chunks.extend(section_chunks)

    final_chunks = []
    for chunk in chunks:
        for marker, special_content in table_map.items():
            chunk = chunk.replace(marker, special_content)
        final_chunks.append(chunk)

    print(f"Total number of chunks created: {len(final_chunks)}")
    return final_chunks

def chunk_text_with_semantic_and_dynamic_size(text, language='spanish'):
    """Split text into chunks with dynamic size and semantic boundaries."""
    print(f"\n{'='*20} chunk_text called (with semantic and dynamic size) {'='*20}")
    processed_text, table_map = preprocess_special_content(text)
    print(f"Number of special content blocks found: {len(table_map)}")

    section_patterns = [
        r'#{1,3}\s+[A-ZÑÁÉÍÓÚ].*$',  # Markdown headings
        r'^[IVX]+\.\s+[A-ZÑÁÉÍÓÚ].*$',  # Roman numeral sections
        r'^\d+\.\d+\s+[A-ZÑÁÉÍÓÚ].*$',    # Numbered sections
        r'^\s*[a-z\d]+\.\s+[A-ZÑÁÉÍÓÚ].*$', # Lettered/numbered list items as sections
        r'^\s*[-*]\s+.*$' # Bullet points as potential sections
    ]

    sections = []
    current_section = ""
    for line in processed_text.split('\n'):
        if any(re.match(pattern, line) for pattern in section_patterns) and current_section.strip():
            sections.append(current_section.strip())
            current_section = line
        else:
            current_section += '\n' + line

    if current_section.strip():
        sections.append(current_section.strip())

    chunks = []
    for section in sections:
        section_chunk_size = determine_chunk_size(section)
        print(f"\nProcessing section (first 50 chars): '{section[:50]}...', determined chunk size: {section_chunk_size}")
        section_chunks = sentence_based_chunking_with_semantic(section, section_chunk_size, CHUNK_OVERLAP, language)
        chunks.extend(section_chunks)

    final_chunks = []
    for chunk in chunks:
        for marker, special_content in table_map.items():
            chunk = chunk.replace(marker, special_content)
        final_chunks.append(chunk)

    print(f"Total number of chunks created: {len(final_chunks)}")
    return final_chunks

if __name__ == "__main__":
    from config import CHUNK_SIZE, CHUNK_OVERLAP # Ensure these are defined

    sample_text_semantic = """
# Introduction
This is the first topic we will discuss. Por lo tanto, the following sentences will elaborate on it. This is a continuation of the same idea.

# New Topic
Finalmente, we are moving on to a completely different subject. This new subject has several aspects. 1) The first aspect is important. This explains the first aspect in detail. 2) The second aspect is also key.

En conclusión, this summarizes the main points.

- Point one is important.
- Point two is also key.

1. First step.
2. Second step.

a. Item A.
b. Item B.
"""

    chunks_semantic = chunk_text_with_semantic_and_dynamic_size(sample_text_semantic, language='english')
    print("\nChunks with Semantic Boundaries and Dynamic Size:")
    for i, chunk in enumerate(chunks_semantic):
        print(f"Chunk {i+1}: {chunk}\n---")