from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

# SQLite database file path
DATABASE_URL = "sqlite:///./screening.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    batches = relationship("ScreeningBatch", back_populates="user")

class ScreeningBatch(Base):
    __tablename__ = "screening_batches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_name = Column(String)
    tagline = Column(String)
    role_name = Column(String)
    role_requirements = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship to results
    results = relationship("CandidateResult", back_populates="batch")
    user = relationship("User", back_populates="batches")

class CandidateResult(Base):
    __tablename__ = "candidate_results"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("screening_batches.id"))
    email = Column(String)
    status = Column(String) # ELIGIBLE or NOT ELIGIBLE
    
    batch = relationship("ScreeningBatch", back_populates="results")

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
