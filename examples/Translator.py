from deep_translator import GoogleTranslator
import re

def translate_file(input_file, output_file):
    """
    Translate text from Spanish to English from a file without any word limit.
    
    Args:
        input_file (str): Path to the input file containing Spanish text
        output_file (str): Path to save the translated English text
    """
    print(f"Reading file: {input_file}")
    
    try:
        # Read the source file
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f"Translating text ({len(text)} characters)...")
        
        # Initialize translator
        translator = GoogleTranslator(source='es', target='en')
        
        # For large texts, split into chunks and translate each chunk
        # This bypasses any character limits in the API
        chunk_size = 4000  # Safe chunk size for Google Translate
        translated_text = ""
        
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i+chunk_size]
            translated_chunk = translator.translate(chunk)
            
            # --- MODIFICATION STARTS HERE ---
            pattern = r"--- Processsed Block \d+ \([^)]+\) ---"
            if re.search(pattern, translated_chunk):
                print(f"modification starts")
                # Add newline before each occurrence
                translated_chunk = re.sub(pattern, r"\n\n\n\g<0>", translated_chunk)
            # --- MODIFICATION ENDS HERE ---

            translated_text += translated_chunk
            print(f"Translated chunk {i//chunk_size+1}/{(len(text)//chunk_size)+1}")
        
        # Write the translated text to the output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(translated_text)
            
        print(f"Translation complete! Saved to: {output_file}")
    
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    # Hard-coded file paths as requested
    input_file = "C:\\Indhu\\AI\\PROD\\Spanish RAG\\rag_queries.txt"
    output_file = "C:\\Indhu\\AI\\PROD\\Spanish RAG\\English_rag_queries.txt"
    
    print(f"Using hard-coded paths:")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    
    translate_file(input_file, output_file)