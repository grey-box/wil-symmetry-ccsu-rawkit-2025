from typing import Any, Dict, List
from models import WikipediaHeader
from fastapi import APIRouter

router = APIRouter()

@router.post("/head", response_model=WikipediaHeader)
async def parse_article_categories(article_json:Dict[str, Any]) -> List[WikipediaHeader]: return []