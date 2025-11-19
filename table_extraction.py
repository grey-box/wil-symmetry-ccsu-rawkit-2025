import wikipedia # Library for fetching Wikipedia content
import pandas as pd # Pandas for table parsing and DataFrame handling
from bs4 import BeautifulSoup # Class for HTML parsing
from io import StringIO # Wrap HTML strings for Read-HTML function on Pandas library
from typing import List, Dict, Any, Optional
import numpy as np

def extract_tables_from_wikipedia(page_title: str, language: str) -> List[Dict[str, Any]]:
    """Extracts all tables from a Wikipedia article."""
    # TODO: See header extraction. Code language parsing once and use existing libraries.
    if language == 'spanish':
        wikipedia.set_lang('es')
    elif language == 'german':
        wikipedia.set_lang('de')
    elif language == 'dutch':
        wikipedia.set_lang('nl')
    else:
        wikipedia.set_lang(language[0:2])

    try:
        page = wikipedia.search(query=page_title)
        if not page:
            raise ValueError(f"No Wikipedia page found for '{page_title}'")
        html = wikipedia.WikipediaPage(title=page[0]).html()
        soup = BeautifulSoup(html, 'html.parser')
        
        # TODO: Implement Error Management here at each step, including dealing with all possible return types from called functions
        content = soup.find("div", class_="mw-parser-output")
        tables_html = content.find_all('table')
        
        tables_data = []
        for table in tables_html:
            try:
                html_string = StringIO(str(table))
                df = pd.read_html(html_string)[0]
                
                # Replace NaN with empty string and convert all data to string
                df = df.fillna('')
                df = df.astype(str)
                
                # Handle headers
                headers = [str(col) for col in df.columns.tolist()]
                
                # Handle rows
                rows = df.values.tolist()
                
                caption = table.find('caption')
                caption_text = caption.get_text() if caption else None
                
                tables_data.append({
                    'headers': headers,
                    'rows': rows,
                    'caption': caption_text
                })
            except ValueError as e:
                print(f"Could not parse a table: {e}")
        
        return tables_data
    except Exception as e:
        raise ValueError(f"Error extracting tables: {e}")

def get_table_details(tables_data: List[Dict[str, Any]]) -> Dict[str, str]:
    """Returns detailed information about each table."""
    table_details = {}
    for idx, table in enumerate(tables_data, start=1):
        num_rows = len(table['rows'])
        num_cols = len(table['headers'])
        table_details[f"table_{idx}"] = f"{num_rows} rows and {num_cols} columns"
    return table_details
