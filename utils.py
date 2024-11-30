import logging
from typing import Any
from functools import wraps
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def retry_decorator(max_retries: int = 3, delay: int = 1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        logger.error(f"Failed after {max_retries} retries: {str(e)}")
                        raise
                    logger.warning(f"Attempt {retries} failed: {str(e)}. Retrying...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

def validate_paper(paper: dict) -> bool:
    """Validate paper data structure"""
    required_fields = ['id', 'title', 'abstract', 'authors', 'published', 'updated', 'categories']
    return all(field in paper for field in required_fields)
