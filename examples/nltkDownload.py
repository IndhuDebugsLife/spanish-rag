import nltk
import os

print(f"NLTK Version: {nltk.__version__}")
print(f"NLTK Data Path: {nltk.data.path}")

nltk_data_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'nltk_data')
if nltk_data_path not in nltk.data.path:
    nltk.data.path.append(nltk_data_path)
    print(f"Added NLTK data path: {nltk_data_path}")
else:
    print(f"NLTK data path already includes: {nltk_data_path}")
print(f"Updated NLTK Data Path: {nltk.data.path}")


try:
    tokenizer = nltk.tokenize.PunktTokenizer()
    print("Default PunktTokenizer initialized successfully.")
except Exception as e:
    print(f"Error initializing default PunktTokenizer: {e}")

try:
    spanish_tokenizer_pickle = nltk.tokenize.PunktTokenizer(os.path.join(nltk_data_path, 'tokenizers', 'punkt', 'spanish.pickle'))
    print("Spanish PunktTokenizer initialized successfully using pickle path.")
except LookupError as e:
    print(f"LookupError initializing Spanish PunktTokenizer with pickle: {e}")
except Exception as e:
    print(f"Error initializing Spanish PunktTokenizer with pickle: {e}")

try:
    spanish_tokenizer_lang = nltk.tokenize.PunktTokenizer('spanish')
    print("Spanish PunktTokenizer initialized successfully using language code.")
except LookupError as e:
    print(f"LookupError initializing Spanish PunktTokenizer with language code: {e}")
except Exception as e:
    print(f"Error initializing Spanish PunktTokenizer with language code: {e}")

print("\nAttempting to tokenize a Spanish sentence...")
try:
    test_sentence_es = "Hola, ¿cómo estás? Estoy bien."
    tokens_es = nltk.sent_tokenize(test_sentence_es, language='spanish')
    print(f"Tokenized Spanish sentence: {tokens_es}")
except LookupError as e:
    print(f"LookupError during Spanish sentence tokenization: {e}")
except Exception as e:
    print(f"Error during Spanish sentence tokenization: {e}")

print("\nAttempting to tokenize an English sentence...")
try:
    test_sentence_en = "Hello, how are you? I'm fine."
    tokens_en = nltk.sent_tokenize(test_sentence_en, language='english')
    print(f"Tokenized English sentence: {tokens_en}")
except LookupError as e:
    print(f"LookupError during English sentence tokenization: {e}")
except Exception as e:
    print(f"Error during English sentence tokenization: {e}")