import wikipedia
from bs4 import BeautifulSoup
from typing import List, Dict, Any

def extract_images_from_wikipedia(page_title: str, language: str) -> List[Dict[str, Any]]:
    """Extracts all images from a Wikipedia article."""
    if language == 'spanish':
        wikipedia.set_lang('es')
    elif language == 'german':
        wikipedia.set_lang('de')
    elif language == 'dutch':
        wikipedia.set_lang('nl')
    else:
        wikipedia.set_lang(language[0:2])

    try:
        page = wikipedia.search(query=page_title)
        if not page:
            raise ValueError(f"No Wikipedia page found for '{page_title}'")
        
        html = wikipedia.WikipediaPage(title=page[0]).html()
        soup = BeautifulSoup(html, 'html.parser')
        
        content = soup.find("div", class_="mw-parser-output")
        if not content:
             content = soup

        images_data = []
        
        imgs = content.find_all('img')
        
        for idx, img in enumerate(imgs):
            src = img.get('src')
            if not src:
                continue
            
            # Ensure full URL
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = 'https://wikipedia.org' + src
                
            alt = img.get('alt', '')
            
            caption = None
            
            # Check for thumb caption
            parent = img.find_parent('div', class_='thumbinner')
            if parent:
                caption_div = parent.find('div', class_='thumbcaption')
                if caption_div:
                    caption = caption_div.get_text(strip=True)
            
            # Check for gallery caption
            if not caption:
                gallery_box = img.find_parent('li', class_='gallerybox')
                if gallery_box:
                    gallery_text = gallery_box.find('div', class_='gallerytext')
                    if gallery_text:
                        caption = gallery_text.get_text(strip=True)

            # Check for infobox caption if image is inside infobox
            if not caption:
                 infobox_image = img.find_parent('td', class_='infobox-image')
                 if infobox_image:
                     # Sometimes the caption is in the next row or in a span
                     # Simple heuristic: check parent text or next sibling text
                     caption = infobox_image.get_text(strip=True)
                     if not caption:
                         # Look for a caption class nearby
                         next_elem = infobox_image.find_next('div', class_='infobox-caption')
                         if next_elem:
                             caption = next_elem.get_text(strip=True)

            # If still no caption, check title attribute
            if not caption:
                caption = img.get('title', '')

            # Skip small icons (width < 30) unless they have meaningful alt/caption
            try:
                width = int(img.get('width', 100))
                if width < 30 and not caption and not alt:
                    continue
            except:
                pass

            images_data.append({
                'id': f"image_{idx+1}",
                'url': src,
                'alt_text': alt,
                'caption': caption
            })
            
        return images_data

    except Exception as e:
        raise ValueError(f"Error extracting images: {e}")
