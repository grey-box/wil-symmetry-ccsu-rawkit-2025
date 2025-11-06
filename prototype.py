from typing import Any, Dict, List, Optional # Annotations for readability
from pydantic import BaseModel, Field # Classes for data-validation
from fastapi import FastAPI, HTTPException # Fast-API class to start API server
from table_extraction import extract_tables_from_wikipedia, get_table_details

"""
Purpose:
    * Process Wikipedia Structural Data -> Tables, Citations, Categories, and Info-Boxes 
    * Identify the best table by data entry count 
    * Compute article scores based on data volume and citation accuracy
"""

application:FastAPI = FastAPI(title="Wikipedia Data Extraction API", version="1.0.0") # Instance of FastAPI


@application.get("/") # Root endpoint to check API status
async def root() -> Dict[str, str]:
    """Root endpoint to check if API is running"""
    return {"message": "Wikipedia Data Extraction API is running", "docs": "/docs"}


# Data-Structures to hold various types of content

class WikipediaTable(BaseModel): # Representation of a Wikipedia Table
    table_id: str = Field(min_length=1, description="An ID to each table within a Wikipedia article") # Unique ID to identify a table
    headers: List[str] = Field(min_length=1, description="First row that contains column names") # Column identifiers
    rows: List[List[str]] = Field(min_length=1, description="One or more rows of data extracted from each table")# Data entries
    caption: Optional[str] = Field(default=None, description="Associated metadata to identify the table") # Any additional captions or metadata


class WikipediaInfoBox(BaseModel): # Representation of a Wikipedia Info-Box
    fields:Dict[str, Any] = Field(min_length=1, description="Key-Value Pairs to store extracted Info-Boxes") # Use key/value pairs to hold any info-box information


class WikipediaCitation(BaseModel): # Representation of a Wikipedia Citation
    reference_id:str = Field(min_length=1, description="An ID to uniquely identify each citation in the article") # Unique ID to identify a citation
    source_url:str = Field(min_length=1, description="Source URL where the reference was retrieved from") # Origin source of the given citation
    title:Optional[str] = Field(min_length=1, description="Title of the Source article referenced in citation") # Title of the source article
    reliability_score:Optional[float] = Field(default=0.0, decription="A score given to each citation to identify its credibility and accuracy") # A score based on domain or metadata


class WikipediaHeader(BaseModel): # Representation of a Wikipedia Headers to separate each section of the article
    header:str = Field(min_length=1, description="A header to separate sections of the Wikipedia article") # Name of the tag



class ArticleScore(BaseModel): # Aggregated score for one article
    article_title:str = Field(min_length=1, description="Title of the article used to identify it") # Title of the article
    best_table_id:Optional[str] = Field(default=None, description="ID of the best table from the article") # Best table with most data entries
    data_item_count:int = Field(gt=0, description="Store aggregated data count from the article") # Total number of data entry count
    citation_accuracy:float = Field(gt=0, description="Score to determine accuracy, reliability, and credibility of all the citations in the article") # Accuracy of the citations
    final_score:float = Field(gt=0.0, description="An aggregated final score assigned to the article based on various aspects") # A final score to the article
    details:Dict[str, Any] = Field(default=None, description="Any comments and details assigned to the article for additional information") # Any additional description or details


class TableExtractionRequest(BaseModel): # Request model for table extraction
    page_title: str = Field(min_length=1, description="Title of the Wikipedia article to extract tables from")
    language: str = Field(default="english", description="Language of the Wikipedia article (e.g., 'english', 'spanish', 'german', 'dutch')")


class TableExtractionResponse(BaseModel): # Response model for table extraction
    article_title: str = Field(description="Title of the Wikipedia article")
    language: str = Field(description="Language of the article")
    number_of_tables: int = Field(description="Total number of tables found")
    tables: List[WikipediaTable] = Field(description="List of extracted tables")
    table_details: Dict[str, str] = Field(description="Detailed information about each table (rows and columns)")


# Extract and parsing input data

@application.post("/tables", response_model=WikipediaTable) # POST Request that accepts table-data from an article which will be parsed into WikipediaTable
async def parse_article_tables(article_json:Dict[str, Any]) -> List[WikipediaTable]: pass # Extract and parse all tables from Wikipedia article (JSON)


@application.post("/extract-tables", response_model=TableExtractionResponse) # POST Request to extract tables from Wikipedia article
async def extract_wikipedia_tables(request: TableExtractionRequest) -> TableExtractionResponse:
    """Extract all tables from a Wikipedia article given its title and language"""
    try:
        # Extract tables using the table_extraction module
        tables_data = extract_tables_from_wikipedia(request.page_title, request.language)
        
        if not tables_data:
            raise HTTPException(status_code=404, detail=f"No tables found in article '{request.page_title}'")
        
        # Convert to WikipediaTable models
        wikipedia_tables = []
        for idx, table_data in enumerate(tables_data):
            table_id = f"table_{idx + 1}"
            headers = table_data['headers']
            rows = table_data['rows']
            caption = table_data.get('caption')
            
            wikipedia_table = WikipediaTable(
                table_id=table_id,
                headers=headers,
                rows=rows,
                caption=caption
            )
            wikipedia_tables.append(wikipedia_table)
        
        # Get table details
        table_details = get_table_details(tables_data)
        
        return TableExtractionResponse(
            article_title=request.page_title,
            language=request.language,
            number_of_tables=len(wikipedia_tables),
            tables=wikipedia_tables,
            table_details=table_details
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting tables: {str(e)}")

@application.post("/info-box", response_model=WikipediaInfoBox) # POST Request that accepts info-boxe from an article which will be parsed into WikipediaInfoBox
async def parse_article_infobox(article_json:Dict[str, Any]) -> Optional[WikipediaInfoBox]:
    """Extract and parse the infobox from Wikipedia article (JSON)"""
    
    # Check if the article_json contains infobox data
    if not article_json or "infobox" not in article_json:
        return None
    
    infobox_data = article_json.get("infobox")
    
    # If infobox_data is None or empty, return None
    if not infobox_data:
        return None
    
    # If infobox_data is already a dictionary, use it directly
    if isinstance(infobox_data, dict):
        # Filter out None values and empty strings for cleaner data
        cleaned_fields = {
            key: value for key, value in infobox_data.items() 
            if value is not None and value != ""
        }
        
        # Return WikipediaInfoBox only if there are fields
        if cleaned_fields:
            return WikipediaInfoBox(fields=cleaned_fields)
    
    return None # Extract and parse the infobox from Wikipedia article (JSON)

@application.post("/citation", response_model=WikipediaCitation) # POST Request that accepts citations from an article which will be parsed into WikipediaCitation
async def parse_article_citation(article_json:Dict[str, Any]) -> List[WikipediaCitation]: pass # Extract and parse all citations/references from Wikipedia article (JSON)

@application.post("/head", response_model=WikipediaHeader) # POST Request that accepts headers from an article which will be parsed into WikipediaHeader
async def parse_article_categories(article_json:Dict[str, Any]) -> List[WikipediaHeader]: pass # Extract and parse headers attached to the Wikipedia article (JSON)


# Table Analysis

def compute_table_entry_count(table:WikipediaTable) -> int: pass # Return the number of data entries or rows in a given table
def find_best_table(tables:List[WikipediaTable]) -> Optional[WikipediaTable]: pass # Select the table with the highest number of entries


# Citation Evaluation

def evaluate_citation_reliability(citation:WikipediaCitation) -> float: pass # Return a reliability score based on citation metadata or domain
def compute_citation_accuracy(citations: List[WikipediaCitation]) -> float: pass # Compute average citation reliability score for an article


# Article Scoring

def compute_data_item_count(tables:List[WikipediaTable], infobox:Optional[WikipediaInfoBox], categories:List[WikipediaHeader]) -> int: pass # Compute total number of structured data items in the article
def compute_data_item_score(tables:List[WikipediaTable], infobox:Optional[WikipediaInfoBox],
                            citations: List[WikipediaCitation], categories: List[WikipediaHeader]) -> ArticleScore: pass # Combine table richness, data item volume, and citation accuracy into the final article score


# Comparison of Article Scores and Aggregation

def compare_article_scores(articles:List[ArticleScore]) -> Dict[str, Any]: pass # Compare multiple articles to return a relative rankings and statistics
def aggregate_project_symmetry_report(article_scores: List[ArticleScore]) -> Dict[str, Any]: pass # Produce a final JSON payload for API/UI consumption


# FastAPI Hook

def api_compute_article_score(article_json:Dict[str, Any]) -> ArticleScore: pass # API facing function to compute and return score for a single article