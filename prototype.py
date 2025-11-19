from typing import Any, Dict, List, Optional
from fastapi import FastAPI
from routers import tables, infoboxes, citations, headers, images
from models import ArticleScore

"""
Purpose:
    * Process Wikipedia Structural Data -> Tables, Citations, Categories, and Info-Boxes
    * Identify the best table by data entry count
    * Compute article scores based on data volume and citation accuracy
"""

application:FastAPI = FastAPI(title="Wikipedia Data Extraction API", version="1.0.0")

application.include_router(tables.router, prefix="/tables", tags=["tables"])
application.include_router(infoboxes.router, prefix="/infoboxes", tags=["infoboxes"])
application.include_router(citations.router, prefix="/citations", tags=["citations"])
application.include_router(headers.router, prefix="/headers", tags=["headers"])
application.include_router(images.router, prefix="/images", tags=["images"])


@application.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint to check if API is running"""
    return {"message": "Wikipedia Data Extraction API is running", "docs": "/docs"}


# Data-Structures to hold various types of content



# Table Analysis

def compute_table_entry_count(table:tables.WikipediaTable) -> int: return 0
def find_best_table(tables:List[tables.WikipediaTable]) -> Optional[tables.WikipediaTable]: return None


# Citation Evaluation

def evaluate_citation_reliability(citation:citations.WikipediaCitation) -> float: return 0.0
def compute_citation_accuracy(citations: List[citations.WikipediaCitation]) -> float: return 0.0


# Article Scoring

def compute_data_item_count(tables:List[tables.WikipediaTable], infobox:Optional[infoboxes.WikipediaInfoBox], categories:List[headers.WikipediaHeader]) -> int: return 0
def compute_data_item_score(tables:List[tables.WikipediaTable], infobox:Optional[infoboxes.WikipediaInfoBox],
                            citations: List[citations.WikipediaCitation], categories: List[headers.WikipediaHeader]) -> Optional[ArticleScore]: return None


# Comparison of Article Scores and Aggregation

def compare_article_scores(articles:List[ArticleScore]) -> Dict[str, Any]: return {}
def aggregate_project_symmetry_report(article_scores: List[ArticleScore]) -> Dict[str, Any]: return {}


# FastAPI Hook

def api_compute_article_score(article_json:Dict[str, Any]) -> Optional[ArticleScore]: return None
