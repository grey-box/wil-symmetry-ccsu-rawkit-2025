import wikipedia  # Library for fetching Wikipedia content
import json
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from typing import Any, Dict, List
from models import WikipediaHeader
from fastapi import APIRouter

router = APIRouter()

# Set up language selection
def set_wikipedia_language(lang: str) -> None:
    """Set Wikipedia language based on language string"""
    if lang.lower() == 'spanish':
        wikipedia.set_lang('es')
    elif lang.lower() == 'german':
        wikipedia.set_lang('de')
    elif lang.lower() == 'dutch':
        wikipedia.set_lang('nl')
    elif lang.lower() == 'english':
        wikipedia.set_lang('en')
    else:
        wikipedia.set_lang(lang[0:2])


# Define a Pydantic model for the output
class HeaderCount(BaseModel):
    total_headers: int = Field(..., description="The total number of h1-h6 headers found.")
    h1_count: int
    h2_count: int
    h3_count: int
    h4_count: int
    h5_count: int
    h6_count: int

# Function to parse HTML and count headers using Beautiful Soup
def count_html_headers(page_title: str, language: str) -> json:
    """Parses HTML content and returns counts of all header tags."""
  
    try:
      
        # Capitalize the first letter of the current language
        language = language.capitalize()

        # Set Wikipedia language
        set_wikipedia_language(language)

        # Search for article
        search_results = wikipedia.search(query=page_title)
        if not search_results:
            print(f"Error: the {language} page for {page_title} was not found.  ")
            return None

        # Get Wikipedia page HTML
        page = wikipedia.page(page_title, auto_suggest=False)
        html = page.html()
        soup_html_parser = BeautifulSoup(html, "html.parser")
        # soup_lxml_parser = BeautifulSoup(html, "lxml-html")

        # Find main content area in HTML
        content = soup_html_parser.find("div", class_="mw-parser-output")
        if not content:
            raise ValueError("Could not find article content in HTML")

        # Count specific header tags
        h1s = len(soup_html_parser.find_all('h1'))
        h2s = len(soup_html_parser.find_all('h2'))
        h3s = len(soup_html_parser.find_all('h3'))
        h4s = len(soup_html_parser.find_all('h4'))
        h5s = len(soup_html_parser.find_all('h5'))
        h6s = len(soup_html_parser.find_all('h6'))

        # Calculate the total
        total = h1s + h2s + h3s + h4s + h5s + h6s

        # Use Pydantic to structure and validate the counts
        counts = HeaderCount(

            h1_count = h1s,
            h2_count = h2s,
            h3_count = h3s,
            h4_count = h4s,
            h5_count = h5s,
            h6_count = h6s,
            total_headers = total

        )

        header_list = {

            "h1": h1s,
            "h2": h2s,
            "h3": h3s,
            "h4": h4s,
            "h5": h5s,
            "h6": h6s,
            "Total Headers": total

        }

        header_json = json.dumps(header_list, indent=4)

        return header_json

    except wikipedia.exceptions.PageError:
        print(f"The page for '{page_title}' in {language} was not found.")
        return None
    except wikipedia.exceptions.DisambiguationError as e:
        print(f"Disambiguation page for '{page_title}'. Options: {e.options}")
        return None

@router.post("/head", response_model=WikipediaHeader)
async def parse_article_categories(article_json:Dict[str, Any]) -> List[WikipediaHeader]: return []
