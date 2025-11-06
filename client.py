import requests # Library for making HTTP requests
import json # Library for JSON manipulation
from typing import Dict, Any, Optional


API_BASE_URL = "http://localhost:8000" # Base URL for the FastAPI server


def extract_tables(article_title: str, language: str = "english") -> Optional[Dict[str, Any]]:
    """
    Extract tables from a Wikipedia article using the FastAPI endpoint.
    
    Args:
        article_title: Title of the Wikipedia article
        language: Language of the article (default: "english")
    
    Returns:
        Dictionary containing table extraction response or None if error
    """
    endpoint = f"{API_BASE_URL}/extract-tables"
    
    payload = {
        "page_title": article_title,
        "language": language
    }
    
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return None


def display_table_extraction_results(results: Dict[str, Any]) -> None:
    """Display table extraction results in a formatted way"""
    if not results:
        print("No results to display")
        return
    
    print("=" * 80)
    print(f"Article: {results.get('article_title', 'N/A')}")
    print(f"Language: {results.get('language', 'N/A')}")
    print(f"Number of Tables: {results.get('number_of_tables', 0)}")
    print("=" * 80)
    
    # Display table details
    table_details = results.get('table_details', {})
    if table_details:
        print("\nTable Details:")
        for table_id, details in table_details.items():
            print(f"  Table {table_id}: {details}")
    
    # Display tables
    tables = results.get('tables', [])
    if tables:
        print("\n" + "=" * 80)
        print("EXTRACTED TABLES:")
        print("=" * 80)
        
        for idx, table in enumerate(tables, start=1):
            print(f"\n--- Table {idx} (ID: {table.get('table_id', 'N/A')}) ---")
            
            caption = table.get('caption')
            if caption:
                print(f"Caption: {caption}")
            
            headers = table.get('headers', [])
            if headers:
                print(f"Headers: {', '.join(headers)}")
            
            rows = table.get('rows', [])
            if rows:
                print(f"Rows ({len(rows)}):")
                for row_idx, row in enumerate(rows[:5], start=1): # Show first 5 rows
                    print(f"  Row {row_idx}: {', '.join(str(cell) for cell in row)}")
                if len(rows) > 5:
                    print(f"  ... and {len(rows) - 5} more rows")
    
    print("\n" + "=" * 80)


def main():
    """Main function to demonstrate API usage"""
    print("Wikipedia Table Extraction API Client")
    print("=" * 80)
    
    # Example 1: Extract tables from an English article
    print("\nExample 1: Extracting tables from 'Python (programming language)' article...")
    results = extract_tables("Python (programming language)", "english")
    if results:
        display_table_extraction_results(results)
    else:
        print("Failed to extract tables")
    
    # Example 2: Extract tables from a Spanish article
    print("\n\nExample 2: Extracting tables from 'Python' article in Spanish...")
    results = extract_tables("Python", "spanish")
    if results:
        display_table_extraction_results(results)
    else:
        print("Failed to extract tables")
    
    # Interactive mode
    print("\n" + "=" * 80)
    print("INTERACTIVE MODE")
    print("=" * 80)
    
    while True:
        print("\nEnter article details (or 'quit' to exit):")
        article_title = input("Article title: ").strip()
        
        if article_title.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not article_title:
            print("Please enter a valid article title")
            continue
        
        language = input("Language (default: english): ").strip()
        if not language:
            language = "english"
        
        print(f"\nExtracting tables from '{article_title}' ({language})...")
        results = extract_tables(article_title, language)
        
        if results:
            display_table_extraction_results(results)
        else:
            print("Failed to extract tables. Make sure the API server is running on localhost:8000")


if __name__ == "__main__":
    main()

