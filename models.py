from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HeaderCount(BaseModel):
    # TODO: Total headers should be a method, not a value, because it should always be true even when you didn't finish calculating values
    total_headers: int = Field(..., description="The total number of h1-h6 headers found.")
    # TODO: This should be a dictionary {"h1":0,"h2":3,...}
    h1_count: int
    h2_count: int
    h3_count: int
    h4_count: int
    h5_count: int
    h6_count: int


class WikipediaInfoBox(BaseModel):
    fields: Dict[str, Any] = Field(min_length=1, description="Key-Value Pairs to store extracted Info-Boxes")


class WikipediaCitation(BaseModel):
    reference_id: str = Field(min_length=1, description="An ID to uniquely identify each citation in the article")
    source_url: str = Field(min_length=1, description="Source URL where the reference was retrieved from")
    title: Optional[str] = Field(min_length=1, description="Title of the Source article referenced in citation")
    reliability_score: Optional[float] = Field(default=0.0, description="A score given to each citation to identify its credibility and accuracy")


class WikipediaTable(BaseModel):
    table_id: str = Field(min_length=1, description="An ID to each table within a Wikipedia article")
    headers: List[str] = Field(min_length=1, description="First row that contains column names")
    rows: List[List[str]] = Field(min_length=1, description="One or more rows of data extracted from each table")
    caption: Optional[str] = Field(default=None, description="Associated metadata to identify the table")


class TableExtractionRequest(BaseModel):
    page_title: str = Field(min_length=1, description="Title of the Wikipedia article to extract tables from")
    language: str = Field(default="english", description="Language of the Wikipedia article (e.g., 'english', 'spanish', 'german', 'dutch')")


class TableExtractionResponse(BaseModel):
    article_title: str = Field(description="Title of the Wikipedia article")
    language: str = Field(description="Language of the article")
    number_of_tables: int = Field(description="Total number of tables found")
    tables: List[WikipediaTable] = Field(description="List of extracted tables")
    table_details: Dict[str, str] = Field(description="Detailed information about each table (rows and columns)")


class WikipediaHeader(BaseModel):
    header: str = Field(min_length=1, description="A header to separate sections of the Wikipedia article")


class ArticleScore(BaseModel):
    article_title: str = Field(min_length=1, description="Title of the article used to identify it")
    best_table_id: Optional[str] = Field(default=None, description="ID of the best table from the article")
    data_item_count: int = Field(gt=0, description="Store aggregated data count from the article")
    citation_accuracy: float = Field(gt=0, description="Score to determine accuracy, reliability, and credibility of all the citations in the article")
    final_score: float = Field(gt=0.0, description="An aggregated final score assigned to the article based on various aspects")
    details: Dict[str, Any] = Field(default={}, description="Any comments and details assigned to the article for additional information")