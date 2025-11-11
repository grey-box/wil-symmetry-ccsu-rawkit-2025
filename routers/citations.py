from typing import Any, Dict, List, Optional
from models import WikipediaCitation
from fastapi import APIRouter

router = APIRouter()

@router.post("/citation", response_model=WikipediaCitation)
async def parse_article_citation(article_json:Dict[str, Any]) -> List[WikipediaCitation]: return []