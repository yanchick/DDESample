import arxiv
import time
from typing import List, Dict
from config import PAPERS_PER_REQUEST, WAIT_TIME, SEARCH_QUERY
import loguru

logger = loguru.logger



class ArxivCollector:
    def __init__(self,query: str="Deep learning") -> None:
        self.client = arxiv.Client()
        self.query = query

    def collect_papers(self, max_results: int = 10) -> List[Dict]:
        logger.info(f"Collecting papers using query: {self.query}")
        search = arxiv.Search(
            query=self.query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        papers = []
        for result in self.client.results(search):
            logger.debug(f"Found paper: {result.title}")
            paper = {
                'id': result.entry_id,
                'title': result.title,
                'abstract': result.summary,
                'authors': [author.name for author in result.authors],
                'published': result.published.strftime('%Y-%m-%d'),
                'updated': result.updated.strftime('%Y-%m-%d'),
                'categories': result.categories
            }
            papers.append(paper)
            time.sleep(WAIT_TIME)

        return papers
