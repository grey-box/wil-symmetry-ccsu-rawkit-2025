from typing import Any, Dict, List, Optional
from models import WikipediaTable, TableExtractionRequest, TableExtractionResponse
from fastapi import APIRouter, HTTPException
from table_extraction import extract_tables_from_wikipedia, get_table_details

router = APIRouter()

@router.post("/tables", response_model=WikipediaTable)
async def parse_article_tables(article_json:Dict[str, Any]) -> List[WikipediaTable]: return []

@router.post("/extract-tables", response_model=TableExtractionResponse)
async def extract_wikipedia_tables(request: TableExtractionRequest) -> TableExtractionResponse:
    """Extract all tables from a Wikipedia article given its title and language"""
    try:
        tables_data = extract_tables_from_wikipedia(request.page_title, request.language)
        
        if not tables_data:
            raise HTTPException(status_code=404, detail=f"No tables found in article '{request.page_title}'")
        
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