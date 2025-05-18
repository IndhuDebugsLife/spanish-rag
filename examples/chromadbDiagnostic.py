import os
import sys
import tempfile

def find_optimal_chroma_db_path():
    """
    Find the most suitable path for storing ChromaDB data.
    
    Returns a list of potential paths in order of preference.
    """
    potential_paths = []

    # 1. Current working directory
    current_dir = os.getcwd()
    potential_paths.append(os.path.join(current_dir, 'chroma_db'))

    # 2. Project root directory (assuming script is in a subdirectory)
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        potential_paths.append(os.path.join(project_root, 'chroma_db'))
    except Exception:
        pass

    # 3. User's home directory
    home_dir = os.path.expanduser('~')
    potential_paths.append(os.path.join(home_dir, '.chroma_db'))

    # 4. Temporary directory
    temp_dir = tempfile.gettempdir()
    potential_paths.append(os.path.join(temp_dir, 'chroma_db'))

    # 5. Additional potential locations based on platform
    if sys.platform.startswith('win'):
        # Windows-specific paths
        potential_paths.extend([
            os.path.join(os.environ.get('LOCALAPPDATA', home_dir), 'ChromaDB'),
            r'C:\ProgramData\ChromaDB'
        ])
    elif sys.platform.startswith('darwin'):
        # macOS-specific paths
        potential_paths.extend([
            os.path.join(home_dir, 'Library', 'Application Support', 'ChromaDB')
        ])
    elif sys.platform.startswith('linux'):
        # Linux-specific paths
        potential_paths.extend([
            os.path.join(home_dir, '.local', 'share', 'chroma_db'),
            '/var/lib/chroma_db'
        ])

    return potential_paths

def test_path_writability(paths):
    """
    Test paths for writability and return the first writable path.
    
    Args:
        paths (list): List of potential paths to test
    
    Returns:
        str: First writable path, or None if no writable path found
    """
    for path in paths:
        try:
            # Ensure the directory exists
            os.makedirs(path, exist_ok=True)
            
            # Test writability by creating a temporary file
            test_file = os.path.join(path, '.chroma_writability_test')
            with open(test_file, 'w') as f:
                f.write('test')
            
            # Remove the test file
            os.remove(test_file)
            
            print(f"✓ Writable path found: {path}")
            return path
        except Exception as e:
            print(f"✗ Path not writable: {path}")
            print(f"  Reason: {e}")
    
    return None

def generate_config_snippet(chroma_path):
    """
    Generate a config.py snippet with the found ChromaDB path.
    
    Args:
        chroma_path (str): Path to use for ChromaDB
    
    Returns:
        str: Config snippet to add to config.py
    """
    config_snippet = f"""
# ChromaDB Configuration
CHROMA_DB_PATH = '{chroma_path}'
CHROMA_COLLECTION_NAME = 'my_rag_collection'

# OpenAI Configuration (ensure these are set correctly)
OPENAI_API_KEY = 'your_openai_api_key_here'
OPENAI_EMBEDDING_MODEL = 'text-embedding-ada-002'
OPENAI_QA_MODEL = 'gpt-3.5-turbo'

# Chunking Configuration
TOP_K_CHUNKS = 4
OPENAI_TEMPERATURE = 0.7
OPENAI_MAX_TOKENS = 200
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
"""
    return config_snippet

def main():
    print("ChromaDB Path Finder and Configuration Helper")
    print("============================================")
    
    # Find potential paths
    potential_paths = find_optimal_chroma_db_path()
    
    # Test and find a writable path
    writable_path = test_path_writability(potential_paths)
    
    if writable_path:
        print("\n📍 Recommended ChromaDB Path:")
        print(writable_path)
        
        # Generate config snippet
        config_snippet = generate_config_snippet(writable_path)
        
        # Option to write to config.py
        try:
            with open('config.py', 'w') as f:
                f.write(config_snippet)
            print("\n✓ Created/Updated config.py with ChromaDB configuration")
        except Exception as e:
            print(f"\n✗ Could not write to config.py: {e}")
            print("\nPlease manually add the following to your config.py:")
            print(config_snippet)
    else:
        print("\n❌ No writable path found for ChromaDB.")
        print("Please manually create and set a writable directory in your config.py")

if __name__ == "__main__":
    main()