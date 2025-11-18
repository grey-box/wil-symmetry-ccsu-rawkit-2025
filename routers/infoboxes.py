from typing import Any, Dict, Optional
from models import WikipediaInfoBox
from fastapi import APIRouter

router = APIRouter()

@router.post("/info-box", response_model=WikipediaInfoBox) # TODO: avoid using a dash in endpoint
async def parse_article_infobox(article_json:Dict[str, Any]) -> Optional[WikipediaInfoBox]:
    """Extract and parse the infobox from Wikipedia article (JSON)"""
    
    if not article_json or "infobox" not in article_json:
        return None
    
    infobox_data = article_json.get("infobox")
    
    if not infobox_data:
        return None
    
    if isinstance(infobox_data, dict):
        cleaned_fields = {
            key: value for key, value in infobox_data.items() 
            if value is not None and value != ""
        }
        
        if cleaned_fields:
            return WikipediaInfoBox(fields=cleaned_fields)
    
    return None