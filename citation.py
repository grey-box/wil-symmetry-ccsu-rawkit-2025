import re
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from fastapi import HTTPException
import requests
from requests import RequestException
from starlette import status


class CitationResponse(BaseModel):
    citations_with_doi: int = Field(description="Count of citations containing a DOI identifier.", gt=-1)
    citations_with_isbn:int = Field(description="Count of citations containing a ISBN identifier.", gt=-1)

    see_also_links:int = Field(description="Count of see-also-links containing a DOI identifier.", gt=-1)
    external_links:int = Field(description="Count of external links containing a DOI identifier.", gt=-1)

    page_title:str = Field(description="Page title", min_length=1)
    language:str = Field(description="Language", min_length=1)

    total_citations:int = Field(description="Total number of citations", gt=-1)


def count_links_in_section(html_content: str, section_name: str) -> int:
    soup = BeautifulSoup(html_content, "html.parser")
    content = soup.find("div", class_="mw-parser-output")
    if not content:
        return 0
    heading = content.find(lambda tag: tag.name in ['h2', 'h3'] and re.match(section_name, tag.text.strip(), re.IGNORECASE))
    if not heading:
        return 0
    link_count = 0
    current_element = heading.next_sibling
    while current_element:
        if current_element.name in ['h2', 'h3']:
            break
        if current_element.name in ['ul', 'ol']:
            link_count = len(current_element.find_all('a'))
            break
        current_element = current_element.next_sibling
    return link_count


def count_doi_isbn_in_wikitext(wikitext: str) -> dict[str, int]:
    wikitext_lower = wikitext.lower()

    # Simple regex to count occurrences of DOI= or ISBN= parameter within citation templates
    # This is an approximation but is highly effective.
    doi_count = len(re.findall(r'(\||}})\s*doi\s*=', wikitext_lower))
    isbn_count = len(re.findall(r'(\||}})\s*isbn\s*=', wikitext_lower))
    total_citations_count = len(re.findall(r'\{\{([A-Z])', wikitext))

    return {
        "citations_with_doi": doi_count,
        "citations_with_isbn": isbn_count,
        "total_citations": total_citations_count,
    }

def extract_citation_from_wikitext(page_title:str, language:str):
    api_url = f"https://{language}.wikipedia.org/w/api.php"
    wikitext_params = {
        "action": "query",
        "prop": "revisions",
        "titles": page_title,
        "rvprop": "content",
        "format": "json",
        "rvslots": "main"
    }

    extlinks_params = {
        "action": "query",
        "prop": "extlinks",
        "titles": page_title,
        "ellimit": "max",  # Get up to 500 links
        "format": "json"
    }

    html_params = {
        "action": "parse",
        "page": page_title,
        "format": "json",
        "prop": "text"
    }

    headers = {"User-Agent": "CitationLinkExtractor/1.0"}
    results = {
        "citations_with_doi": 0,
        "citations_with_isbn": 0,
        "see_also_links": 0,
        "external_links": 0
    }

    try:
        text_response = requests.get(api_url, headers=headers, params=wikitext_params, timeout=15)
        text_response.raise_for_status()
        data = text_response.json()

        page_data = data.get("query", {}).get("pages", {})
        page_id = next(iter(page_data.keys()), '-1')

        if page_id == '-1' or 'missing' in page_data[page_id]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error: Page {page_title} not found in {language}")

        if "error" in text_response.json():
            error_msg = text_response.json()["error"].get("info", "Unknown Wikitext API error")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

        wiki_text = page_data[page_id]['revisions'][0]['slots']['main']['*']
        doi_isbn_count = count_doi_isbn_in_wikitext(wiki_text)
        results.update(doi_isbn_count)

        ext_link_response = requests.get(api_url, headers=headers, params=extlinks_params, timeout=15)
        ext_link_response.raise_for_status()
        ext_link_data = ext_link_response.json()

        page_id_ext = next(iter(ext_link_data.get('query', {}).get('pages', {}).keys()), '-1')
        if page_id_ext != '-1':
            external_links_list = ext_link_data['query']['pages'][page_id_ext].get('extlinks', [])
            results['external_links'] = len(external_links_list)

        html_response = requests.get(api_url, headers=headers, params=html_params, timeout=15)
        html_response.raise_for_status()
        html_data = html_response.json()
        html = html_data["parse"]["text"]["*"]

        results['see_also_links'] = count_links_in_section(html, "See also")

        return CitationResponse(page_title=page_title, language=language, **results)
    except RequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (KeyError, ValueError, TypeError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
