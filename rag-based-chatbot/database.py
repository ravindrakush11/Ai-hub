from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()

class Complaint(Base):
    __tablename__ = 'complaints'
    complaint_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    phone_number = Column(String)
    email = Column(String)
    complaint_details = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

engine = create_engine("sqlite:///complaints.db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
