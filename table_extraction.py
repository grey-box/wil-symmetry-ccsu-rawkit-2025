import wikipedia # Library for fetching Wikipedia content
import pandas as pd # Pandas for table parsing and DataFrame handling
from bs4 import BeautifulSoup # Class for HTML parsing
from io import StringIO # Wrap HTML strings for Read-HTML function on Pandas library


class TableExtraction(object): # Class to extract tables

    def __init__(self, page_title:str, lang:str) -> None: # Constructor with title and language passed

        if lang == 'spanish': wikipedia.set_lang('es') # Set language of article to spanish
        elif lang == 'german': wikipedia.set_lang('de') # Set language of article to german
        elif lang == 'dutch': wikipedia.set_lang('nl') # Set language of article to dutch
        else: wikipedia.set_lang(language[0:2]) # Use first two letters of set languages

        self.page = wikipedia.search(query=page_title) # Search for article based on title
        self.html = wikipedia.WikipediaPage(title=self.page[0]).html() # Extract all HTML components
        self.soup = BeautifulSoup(self.html, 'html.parser') # Parse the HTML content

        self.number_of_tables:int = 0 # An attribute to store total number of tables in the article
        self.tables:list = list() # An attribute to store RAW HTML table tags
        self.frames:list = list() # An attribute to store parsed Data-Frames from tables by Pandas


    def process_article(self) -> None: # Function to process the article to extract tables
        content = self.soup.find("div", class_="mw-parser-output") # Locate main-content area where article tables reside
        tables = content.find_all('table') # Extract all <table> HTML tags from article body
        self.tables = tables # Update table tracking variables
        self.number_of_tables = len(tables) # Update table tracking variables


    def table_processing(self) -> None: # Process each all the table tags extracted
        data_frames:list = [] # Temporary list to store the parsed DataFrames
        if self.number_of_tables != 0: # Ensure at least one table exists before processing starts
            for index, table in enumerate(self.tables): # Iterate through the tables
                try: # Attempt to parse
                    html_string = StringIO(str(table)) # Wrap table HTML in String IO to avoid future-warning
                    data_frame = pd.read_html(html_string)[0] # Parse HTML table into a Pandas Data-Frame
                    data_frames.append(data_frame) # Store Data-Frame if parsed
                except ValueError as e: print(f"Table {index+1} could not be parsed as a DataFrame") # Raise exception because it cannot be parsed
            self.frames = data_frames # Save parsed frames
        else: raise ValueError("No Table Data!") # No tables in the list


    def detailed_information_per_table(self) -> dict: # A function to describe each table
        dictionary:dict = {} # Store number of keys and values per table
        if len(self.frames) != 0: # Ensure DataFrames are available before analyzing
            for index, data_frame in enumerate(self.frames, start=1): # Retrieve each data frame
                number_of_rows, number_of_columns = data_frame.shape # Retrieve number of rows and columns from each table
                dictionary[index] = f'{number_of_rows} rows and {number_of_columns} columns' # Store formatted size description in dictionary
            else: return dictionary # Return table structure information
        else: raise ValueError("No Data-Frames!") # Raise exception because no data-frames available

    def __str__(self) -> str: return f'{self.number_of_tables} tables in this article!' # String representation of instance to show table count


if __name__ == "__main__": # Execute below script if the file is executed directly

    user_input:str = input("Please enter the article title followed by two different languages you want it in (separated by comma) -> ") # Accept user input
    user_input_extracted:list[str] = user_input.strip().split(",") # Split the string input to a list
    title:str = user_input_extracted[0].strip() # Extract title article
    language:str = user_input_extracted[1].strip() # Extract language one
    second_language:str = user_input_extracted[2].strip() # Extract language two

    print(f'Article Details in {language} language')
    instance = TableExtraction(title, language) # Create instance for title and language one
    instance.process_article() # Extract HTML tables first
    instance.table_processing() # Convert tables to Data-Frames
    print(instance) # Number of tables

    for key, value in instance.detailed_information_per_table().items(): # Iterate through dictionary that contains number rows and columns per table
        print(key, value, sep=": ") # Print the information to console

    print('*' * 100)

    print(f'Article Details in {second_language} language')
    instance_es = TableExtraction(title, second_language) # Create instance for title and language two
    instance_es.process_article() # Extract HTML tables firs
    instance_es.table_processing() # Convert tables to Data-Frames
    print(instance_es) # Number of tables

    for key, value in instance_es.detailed_information_per_table().items(): # Iterate through dictionary that contains number rows and columns per table
        print(key, value, sep=": ") # Print the information to console

    #for i, df_de in enumerate(instance_es.frames, start=1):
    #    df_de.to_csv(f"table_{i}.csv", index=False)
    #    print(f"📁 Saved table_{i}.csv")