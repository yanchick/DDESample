from prefect import flow, task
from scrap import ArxivCollector
from preproc import LLMProcessor
from database import Database


@task
def collect_papers(max_papers):
    collector = ArxivCollector()
    return collector.collect_papers(max_results=max_papers)


@task
def process_papers(papers):
    processor = LLMProcessor()
    return [processor.process_paper(paper) for paper in papers]



@task
def save_to_database(papers):
    db = Database()
    db.save_papers(papers)


@flow
def arxiv_analysis_flow(max_papers):
    # Collect papers
    papers = collect_papers(max_papers)

    # Process with LLM
    processed_papers = process_papers(papers)

    # Save to database
    save_to_database(processed_papers)

    return processed_papers
