import requests
from fastapi import HTTPException
from starlette import status


def get_image_count(page_title: str, language: str) -> int:

    API_URL = f"https://{language}.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "titles": page_title,
        "prop": "images",  # Prop=images lists all files on the page
        "imlimit": "max",  # Ensure all files are retrieved (up to 500)
        "format": "json"
    }

    headers = {"User-Agent": "ArticleImageCounter/1.0"}

    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        pages = data.get("query", {}).get("pages", {})

        # Check if the page exists
        page_id = next(iter(pages))
        page_data = pages.get(page_id, {})

        if page_id == "-1" or "missing" in page_data:
            # Handle page not found using FastAPI's HTTPException standard
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Page '{page_title}' not found in {language} Wikipedia.")

        # Extract the list of images
        images = page_data.get("images", [])

        # The result includes all types of files (images, audio, video).
        # We count all of them, as they contribute to media content.
        return len(images)

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"API request failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An unexpected error occurred: {e}")
