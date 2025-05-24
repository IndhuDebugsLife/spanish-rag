import PyPDF2
import os

def extract_pages_from_pdf(source_pdf_path, output_pdf_path, page_numbers_to_extract):
    """
    Extracts specified pages from a source PDF and saves them to a new PDF.

    Args:
        source_pdf_path (str): The file path to the input PDF document.
        output_pdf_path (str): The file path where the new PDF will be saved.
        page_numbers_to_extract (list): A list of page numbers (0-indexed)
                                        to extract from the source PDF.
    """
    # Check if the source PDF file exists
    if not os.path.exists(source_pdf_path):
        print(f"Error: Source PDF file not found at '{source_pdf_path}'")
        return

    try:
        # Open the source PDF file in read-binary mode
        with open(source_pdf_path, 'rb') as file:
            # Create a PdfReader object
            pdf_reader = PyPDF2.PdfReader(file)

            # Create a PdfWriter object to add selected pages
            pdf_writer = PyPDF2.PdfWriter()

            # Get the total number of pages in the source PDF
            total_pages = len(pdf_reader.pages)
            print(f"Source PDF has {total_pages} pages.")

            # Iterate through the desired page numbers
            for page_num in page_numbers_to_extract:
                # Validate page number (0-indexed)
                if 0 <= page_num < total_pages:
                    # Add the page to the writer
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                    print(f"Added page {page_num + 1} (0-indexed: {page_num}) to the new PDF.")
                else:
                    print(f"Warning: Page number {page_num + 1} (0-indexed: {page_num}) is out of range.")

            # Check if any pages were added to write
            if len(pdf_writer.pages) == 0:
                print("No valid pages were specified for extraction. Output PDF will not be created.")
                return

            # Open the output PDF file in write-binary mode
            with open(output_pdf_path, 'wb') as output_file:
                # Write the new PDF to the output file
                pdf_writer.write(output_file)
            print(f"\nSuccessfully created new PDF: '{output_pdf_path}' with selected pages.")

    except PyPDF2.errors.PdfReadError:
        print(f"Error: Could not read PDF file '{source_pdf_path}'. It might be corrupted or encrypted.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Hardcoded Paths and Page Numbers ---
# IMPORTANT: Replace these paths with your actual file paths.
# Ensure 'source.pdf' exists in the specified directory.
# Page numbers are 0-indexed (e.g., 0 for the first page, 1 for the second, etc.)
SOURCE_PDF = "C:\\Indhu\\AI\\Spanish RAG\\data\\TestGoogleAI.pdf"
OUTPUT_PDF = "C:\\Indhu\\AI\\Spanish RAG\\data\\output_selected_pages.pdf"
PAGES_TO_EXTRACT = [14,15,16,17] # Extracts the 1st, 3rd, and 5th pages.

# Call the function to perform the extraction
if __name__ == "__main__":
    print("Starting PDF page extraction...")
    extract_pages_from_pdf(SOURCE_PDF, OUTPUT_PDF, PAGES_TO_EXTRACT)
    print("PDF extraction process finished.")

