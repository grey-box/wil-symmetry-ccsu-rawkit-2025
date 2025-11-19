from typing import Any, Dict, List
from models import WikipediaImage, ImageExtractionRequest, ImageExtractionResponse
from fastapi import APIRouter, HTTPException
from image_extraction import extract_images_from_wikipedia

router = APIRouter()

@router.post("/extract-images", response_model=ImageExtractionResponse)
async def extract_wikipedia_images(request: ImageExtractionRequest) -> ImageExtractionResponse:
    """Extract all images from a Wikipedia article given its title and language"""
    try:
        images_data = extract_images_from_wikipedia(request.page_title, request.language)
        
        if not images_data:
             raise HTTPException(status_code=404, detail=f"No images found in article '{request.page_title}'")
        
        wikipedia_images = []
        for img in images_data:
            wikipedia_images.append(WikipediaImage(
                image_id=img['id'],
                url=img['url'],
                caption=img['caption'],
                alt_text=img['alt_text']
            ))
        
        return ImageExtractionResponse(
            article_title=request.page_title,
            language=request.language,
            number_of_images=len(wikipedia_images),
            images=wikipedia_images
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting images: {str(e)}")

