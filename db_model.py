from sqlalchemy import Column, String, Date, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from config import DB_PATH

Base = declarative_base()

class Paper(Base):
    __tablename__ = 'papers'

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    abstract = Column(String)
    published = Column(Date)
    updated = Column(Date)
    llm_analysis = Column(String)

    # Relationships
    authors = relationship("Author", back_populates="paper", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="paper", cascade="all, delete-orphan")

class Author(Base):
    __tablename__ = 'authors'

    id = Column(String, primary_key=True)
    paper_id = Column(String, ForeignKey('papers.id'))
    author_name = Column(String, nullable=False)

    # Relationship
    paper = relationship("Paper", back_populates="authors")

class Category(Base):
    __tablename__ = 'categories'

    id = Column(String, primary_key=True)
    paper_id = Column(String, ForeignKey('papers.id'))
    category_name = Column(String, nullable=False)

    # Relationship
    paper = relationship("Paper", back_populates="categories")
