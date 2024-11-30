from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict
import uuid
from datetime import datetime
from contextlib import contextmanager

from db_model import Base, Paper, Author, Category
from config import DB_PATH
from utils import logger


class Database:
    def __init__(self):
        self.engine = create_engine(f'sqlite:///{DB_PATH}')
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    @contextmanager
    def get_session(self) -> Session:
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def save_papers(self, papers: List[Dict]):
        with self.get_session() as session:
            for paper_data in papers:
                try:
                    # Create paper instance
                    paper = Paper(
                        id=paper_data['id'],
                        title=paper_data['title'],
                        abstract=paper_data['abstract'],
                        published=datetime.strptime(paper_data['published'], '%Y-%m-%d').date(),
                        updated=datetime.strptime(paper_data['updated'], '%Y-%m-%d').date(),
                        llm_analysis=paper_data.get('llm_analysis')
                    )

                    # Add authors
                    for author_name in paper_data['authors']:
                        author = Author(
                            id=str(uuid.uuid4()),
                            author_name=author_name
                        )
                        paper.authors.append(author)

                    # Add categories
                    for category_name in paper_data['categories']:
                        category = Category(
                            id=str(uuid.uuid4()),
                            category_name=category_name
                        )
                        paper.categories.append(category)

                    # Merge paper (update if exists, insert if new)
                    session.merge(paper)

                except SQLAlchemyError as e:
                    logger.error(f"Error saving paper {paper_data['id']}: {str(e)}")
                    raise

    def get_papers(self, limit: int = None) -> List[Dict]:
        with self.get_session() as session:
            query = session.query(Paper)
            if limit:
                query = query.limit(limit)

            papers = query.all()
            return [self._paper_to_dict(paper) for paper in papers]

    def get_paper_by_id(self, paper_id: str) -> Dict:
        with self.get_session() as session:
            paper = session.query(Paper).filter(Paper.id == paper_id).first()
            if paper:
                return self._paper_to_dict(paper)
            return None

    def _paper_to_dict(self, paper: Paper) -> Dict:
        return {
            'id': paper.id,
            'title': paper.title,
            'abstract': paper.abstract,
            'published': paper.published.strftime('%Y-%m-%d'),
            'updated': paper.updated.strftime('%Y-%m-%d'),
            'llm_analysis': paper.llm_analysis,
            'authors': [author.author_name for author in paper.authors],
            'categories': [category.category_name for category in paper.categories]
        }

    def get_papers_by_category(self, category: str) -> List[Dict]:
        with self.get_session() as session:
            papers = session.query(Paper).join(Category).filter(
                Category.category_name == category
            ).all()
            return [self._paper_to_dict(paper) for paper in papers]

    def get_papers_by_author(self, author_name: str) -> List[Dict]:
        with self.get_session() as session:
            papers = session.query(Paper).join(Author).filter(
                Author.author_name == author_name
            ).all()
            return [self._paper_to_dict(paper) for paper in papers]

    def delete_paper(self, paper_id: str):
        with self.get_session() as session:
            paper = session.query(Paper).filter(Paper.id == paper_id).first()
            if paper:
                session.delete(paper)
