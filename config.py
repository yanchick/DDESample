import os
from datetime import datetime, timedelta

# API Configuration
ARXIV_API_BASE_URL = "http://export.arxiv.org/api/query"
PAPERS_PER_REQUEST = 100
WAIT_TIME = 3  # seconds between requests

# Database Configuration
DB_PATH = "arxiv_papers.db"

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Search parameters
SEARCH_QUERY = "data engineering"
START_DATE = datetime.now() - timedelta(days=30)
