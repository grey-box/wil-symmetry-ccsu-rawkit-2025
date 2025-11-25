# Wikipedia Data Extraction API

FastAPI-based service for extracting structured data (tables, infoboxes, citations, etc.) from Wikipedia articles.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the API Server

Start the FastAPI server:
```bash
uvicorn Application:application --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Using the Client Script

Run the client script to interact with the API:
```bash
python client.py
```

The client script includes:
- Example requests for extracting tables from Wikipedia articles
- Interactive mode for testing different articles and languages

## API Endpoints

### POST `/extract-tables`
Extract all tables from a Wikipedia article.

**Request Body:**
```json
{
  "page_title": "Python (programming language)",
  "language": "english"
}
```

**Response:**
```json
{
  "article_title": "Python (programming language)",
  "language": "english",
  "number_of_tables": 2,
  "tables": [
    {
      "table_id": "table_1",
      "headers": ["Column1", "Column2"],
      "rows": [["Value1", "Value2"]],
      "caption": "Table caption"
    }
  ],
  "table_details": {
    "1": "5 rows and 3 columns",
    "2": "10 rows and 4 columns"
  }
}
```

### POST `/info-box`
Extract infobox from Wikipedia article (JSON input).

### POST `/tables`
Parse tables from article JSON (legacy endpoint).

### POST `/citation`
Extract citations from Wikipedia article.

### POST `/head`
Extract headers from Wikipedia article.

## Example Usage

### Using Python requests:
```python
import requests

response = requests.post(
    "http://localhost:8000/extract-tables",
    json={
        "page_title": "Python (programming language)",
        "language": "english"
    }
)
print(response.json())
```

### Using curl:
```bash
curl -X POST "http://localhost:8000/extract-tables" \
  -H "Content-Type: application/json" \
  -d '{"page_title": "Python (programming language)", "language": "english"}'
```

## Supported Languages

- english (en)
- spanish (es)
- german (de)
- dutch (nl)
- Or any ISO 639-1 two-letter language code

