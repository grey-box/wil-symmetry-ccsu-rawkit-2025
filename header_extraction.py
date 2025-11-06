import wikipedia # Library for fetching Wikipedia content
import re
from bs4 import BeautifulSoup

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

# Function to parse HTML and count headers using Beautiful Soup
def count_html_headers(page_title: str, language: str) -> str:
    """Parses HTML content and returns counts of all header tags."""

    try:

        # Capitalize the first letter of the current language
        language = language.capitalize()

        # Set Wikipedia language
        set_wikipedia_language(language)

        # Search for article
        search_results = wikipedia.search(query=page_title)
        if not search_results:
            print(f"Error: the page for {page_title} was not found.  ")
            return " "

        # Get Wikipedia page HTML
        page = wikipedia.WikipediaPage(title=search_results[0])
        html = page.html()
        soup_html_parser = BeautifulSoup(html, "html.parser")
        # soup_lxml_parser = BeautifulSoup(html, "lxml-html")

        page = wikipedia.page(page_title, auto_suggest=False)

        # Find main content area in HTML
        content = soup_html_parser.find("div", class_="mw-parser-output")
        if not content:
            raise ValueError("Could not find article content in HTML")

        # Use find_all with a regular expression or a list to get all header tags
        all_headers = content.find_all(re.compile('^h[1-6]$'))

        # Initialize counts
        counts = {f'h{i}': 0 for i in range(1, 7)}

        # Count specific header types
        for header in all_headers:
            if header.name in counts:
                counts[header.name] += 1

        # Calculate the total
        total_headers = len(all_headers)

        return str(total_headers) + " Headers were found on the " + language + " Wikipedia page \n"

    except wikipedia.exceptions.PageError:
        print(f"The page for '{page_title}' in {language} was not found.")
        return " "
    except wikipedia.exceptions.DisambiguationError as e:
        print(f"Disambiguation page for '{page_title}'. Options: {e.options}")
        return " "

if __name__ == "__main__": # Execute below script if the file is executed directly

    user_input:str = input("Please enter the article title followed by two different languages you want it in (separated by comma) -> ") # Accept user input
    user_input_extracted:list[str] = user_input.strip().split(",") # Split the string input to a list
    title:str = user_input_extracted[0].strip() # Extract title article
    language:str = user_input_extracted[1].strip() # Extract language one
    second_language:str = user_input_extracted[2].strip() # Extract language two

    language = language.capitalize() # Capitalize the first letter of the first language
    second_language = second_language.capitalize() # Capitalize the first letter of the second language


    # Perform Search in first language
    print(f'Article Details in the {language} language')

    tally1 = count_html_headers(title,language)
    print(tally1)
    # print(str(tally1) + " Headers in the " + language + " Wikipedia page")


    # Perform Search in second language
    print(f'Article Details in the {second_language} language')

    tally2 = count_html_headers(title,second_language)
    print(tally2)
    # print(str(tally2) + " Headers in the " + second_language + " Wikipedia page")
