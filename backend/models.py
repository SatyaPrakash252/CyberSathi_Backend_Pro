from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime, os

DB_URI = os.environ.get("CYBERSATHI_DB_PATH", "sqlite:///./cybersathi_pro.db")
engine = create_engine(DB_URI, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(Integer, primary_key=True, index=True)
    ticket = Column(String, index=True, unique=True)
    name = Column(String)
    guardian = Column(String)
    dob = Column(String)
    phone = Column(String, index=True)
    email = Column(String)
    gender = Column(String)
    village = Column(String)
    post_office = Column(String)
    police_station = Column(String)
    district = Column(String)
    pincode = Column(String)
    fraud_category = Column(String)
    fraud_subtype = Column(String)
    description = Column(Text)
    attachments = Column(Text)
    status = Column(String, default="Received")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class MessageLog(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    from_phone = Column(String, index=True)
    body = Column(Text)
    intent = Column(String)
    fraud_category = Column(String)
    emotion_pred = Column(String)
    emotion_conf = Column(Float)
    human_label = Column(String)  # optional true label for training
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("DB initialized")
