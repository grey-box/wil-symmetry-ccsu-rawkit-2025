from fastapi import APIRouter, HTTPException, Path
from Utility import get_translation
from starlette import status
import Table, InfoBox, Header, Citation, Images
from pydantic import BaseModel, Field

operations_router = APIRouter(
    prefix="/operations",
    tags=["Analysis"],
)

LANGUAGES = {
    "en": "English",
    "es": "Spanish (Español)",
    "fr": "French (Français)",
    "de": "German (Deutsch)",
    "pt": "Portuguese (Português)",
    "ar": "Arabic (العربية)"
}

class FinalResponse(BaseModel):
    title:str = Field(title="Final Page Title")
    table_analysis:Table.TableResponse = Field(title="Table Analysis")
    header_analysis:Header.HeaderCount = Field(title="Header Analysis")
    info_box:InfoBox.InfoBoxResponse = Field(title="InfoBox Analysis")
    citations:Citation.CitationResponse = Field(title="Citation Analysis")
    total_images:int = Field(title="Total Images/Media Files")


def calculate_single_score(article_response: FinalResponse) -> float:
    """Calculates the combined quality score for a single article's response object."""
    total_tables = article_response.table_analysis.number_of_tables
    total_infobox_attrs = article_response.info_box.total_attributes
    total_citations = article_response.citations.total_citations
    total_headers = article_response.header_analysis.total_count
    total_images = article_response.total_images

    # Structural scoring formula:
    score = ((0.5 * total_citations) + (0.3 * total_tables) +
             (0.10 * total_infobox_attrs) + (0.05 * total_headers) + (0.05 * total_images))
    return score


# --- Helper Function 2: Single Article Analysis ---
def analyze_single_article(title: str, language: str) -> FinalResponse:
    """Performs all structural analyses (Table, Header, Infobox, Citation) for a single article."""

    try:
        # Perform all analysis calls
        table_analysis = Table.analyze_tables(title, language)
        header_counter = Header.count_html_headers(title, language)
        infobox_analysis = InfoBox.analyze_infobox(title, language)
        citation_analysis = Citation.extract_citation_from_wikitext(title, language)
        image_count = Images.get_image_count(title, language)

        return FinalResponse(
            title=title,
            table_analysis=table_analysis,
            header_analysis=header_counter,
            info_box=infobox_analysis,
            citations=citation_analysis,
            total_images=image_count
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Structural analysis error for {title} ({language}): {str(e)}")


# --- Main API Endpoint (Modified) ---

# REMOVED the redundant '{language}' path parameter
@operations_router.get("/{source_language}/{title}", status_code=status.HTTP_200_OK)
async def get_results(title: str, source_language: str = Path(min_length=1)):
    """
    Analyzes the structural quality score for the given article across all 6 supported languages.
    """

    all_scores = []
    normalized_title = title.replace(" ", "_")
    target_languages = list(LANGUAGES.keys())

    for lang_code in target_languages:
        current_title = ""

        # 1. Determine Title (Source vs. Translation)
        if lang_code == source_language:
            # For the user's source language, use the original title
            current_title = normalized_title
        else:
            # For all other languages, attempt translation
            current_title = get_translation(normalized_title, source_language, lang_code)

        # 2. Check for Translation Success
        if not current_title:
            all_scores.append({
                "lang_code": lang_code,
                "lang_name": LANGUAGES[lang_code],
                "title": None,
                "score": -1,  # -1 indicates the article could not be found/translated
                "is_user_language": lang_code == source_language,
                "is_authority_article": False,
                "error": "Translation or article not available."
            })
            continue

        try:
            # 3. Analyze and Score
            article_response = analyze_single_article(current_title, lang_code)
            score = calculate_single_score(article_response)

            # 4. Store Result
            all_scores.append({
                "lang_code": lang_code,
                "lang_name": LANGUAGES[lang_code],
                "title": current_title,
                "score": round(score, 3),
                "is_user_language": lang_code == source_language,
                "is_authority_article": False
            })

        except HTTPException as e:
            # Handle analysis errors (e.g., 404 from a downstream function)
            all_scores.append({
                "lang_code": lang_code,
                "lang_name": LANGUAGES[lang_code],
                "title": current_title,
                "score": -1,
                "is_user_language": lang_code == source_language,
                "is_authority_article": False,
                "error": e.detail
            })
        except Exception as e:
            # Handle unexpected errors
            all_scores.append({
                "lang_code": lang_code,
                "lang_name": LANGUAGES[lang_code],
                "title": current_title,
                "score": -1,
                "is_user_language": lang_code == source_language,
                "is_authority_article": False,
                "error": f"Internal Error during analysis: {str(e)}"
            })
    valid_scores = [d['score'] for d in all_scores if d.get('score', -1) >= 0]
    max_score = max(valid_scores) if valid_scores else -float('inf')

    for item in all_scores:
        is_authority = (item.get('score', -1) >= 0) and (item.get('score') == max_score)
        item['is_authority_article'] = is_authority
    sorted_scores = sorted(all_scores, key=lambda x: x.get('score', -float('inf')), reverse=True)

    # 5. Return the combined results
    return {
        "article": title,
        "source_language_code": source_language,
        "scores_by_language": sorted_scores
    }
