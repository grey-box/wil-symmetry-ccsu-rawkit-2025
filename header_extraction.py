import wikipedia  # Library for fetching Wikipedia content
import json
from bs4 import BeautifulSoup
from models import HeaderCount


# Set up language selection
def set_wikipedia_language(lang: str) -> None:
    """Set Wikipedia language based on language string"""
    # TODO: Please use existing Python libraries to manage languages. Should work with all existing and future languages
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


# Function to parse HTML and count headers using Beautiful Soup
def count_html_headers(page_title: str, language: str) -> json: # TODO: json is not a Python type 
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


if __name__ == "__main__":  # Execute below script if the file is executed directly

    user_input: str = input(
        "Please enter the article title followed by two different languages you want it in (separated by comma) -> ")  # Accept user input
    user_input_extracted: list[str] = user_input.strip().split(",")  # Split the string input to a list
    title: str = user_input_extracted[0].strip()  # Extract title article
    language: str = user_input_extracted[1].strip()  # Extract language one
    second_language: str = user_input_extracted[2].strip()  # Extract language two

    language = language.capitalize()  # Capitalize the first letter of the first language
    second_language = second_language.capitalize()  # Capitalize the first letter of the second language

    # TODO: Code smell here: use a for comprehension to iterage languages, numbered suffixes on otherwise identical variables is bad practice
    # Perform Search in first language
    print(f'Header Details in the {language} Article: ')

    tally1 = count_html_headers(title, language)
    print(tally1)
    # print(str(tally1) + " Headers in the " + language + " Wikipedia page")

    # Perform Search in second language
    print(f'Header Details in the {second_language} Article: ')

    tally2 = count_html_headers(title, second_language)
    print(tally2)
    # print(str(tally2) + " Headers in the " + second_language + " Wikipedia page")
