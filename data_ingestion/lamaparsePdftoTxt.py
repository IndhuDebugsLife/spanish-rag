import os
from pathlib import Path
from llama_parse import LlamaParse

def convert_pdfs_to_markdown(input_dir, output_dir, api_key, region="eu"):
    """
    Convert all PDFs in a directory to markdown using LlamaParse
    """
    # Initialize LlamaParse with HTML table parsing and region
    parser_kwargs = {
        "api_key": api_key,
        "result_type": "markdown",
        "output_tables_as_HTML":True
    }
    
    # Set base URL for different regions
    if region.lower() == "eu":
        parser_kwargs["base_url"] = "https://api.cloud.eu.llamaindex.ai"
    
    parser = LlamaParse(**parser_kwargs)
    
    # Track results
    successful = []
    failed = []
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Process all PDFs
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                
                # Maintain directory structure
                relative_path = os.path.relpath(root, input_dir)
                output_folder = os.path.join(output_dir, relative_path)
                Path(output_folder).mkdir(parents=True, exist_ok=True)
                
                # Output markdown path
                md_filename = os.path.splitext(file)[0] + '.md'
                md_path = os.path.join(output_folder, md_filename)
                
                try:
                    print(f"Processing: {pdf_path}")
                    
                    # Parse PDF
                    documents = parser.load_data(pdf_path)
                    
                    # Write markdown file
                    with open(md_path, 'w', encoding='utf-8') as f:
                        # Write metadata if available
                        if hasattr(documents[0], 'metadata') and documents[0].metadata:
                            f.write("<!-- PDF Metadata -->\n")
                            for key, value in documents[0].metadata.items():
                                f.write(f"<!-- {key}: {value} -->\n")
                            f.write("\n")
                        
                        # Write content
                        for doc in documents:
                            f.write(doc.text)
                            f.write("\n\n")
                    
                    successful.append(pdf_path)
                    print(f"✓ Successfully converted: {file}")
                    
                except Exception as e:
                    failed.append((pdf_path, str(e)))
                    print(f"✗ Failed to convert: {file} - {str(e)}")
    
    # Print summary
    print("\n" + "="*50)
    print("CONVERSION SUMMARY")
    print("="*50)
    print(f"Total successful: {len(successful)}")
    print(f"Total failed: {len(failed)}")
    
    if successful:
        print("\nSuccessful conversions:")
        for pdf in successful:
            print(f"  ✓ {pdf}")
    
    if failed:
        print("\nFailed conversions:")
        for pdf, error in failed:
            print(f"  ✗ {pdf} - {error}")

# Usage
if __name__ == "__main__":
    # Configuration
    API_KEY = "llx-UOrtzWbRMUyuriQxP5wdhHXyhwxOIO86A1uceMruieSSlqUl"
    INPUT_DIRECTORY = "C:\\Indhu\\AI\\Spanish RAG Updated\\data\\source"
    OUTPUT_DIRECTORY = "C:\\Indhu\\AI\\Spanish RAG Updated\\data\\output"
    
    # Run conversion
    convert_pdfs_to_markdown(INPUT_DIRECTORY, OUTPUT_DIRECTORY, API_KEY)