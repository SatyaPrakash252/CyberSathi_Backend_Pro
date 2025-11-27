from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from backend.init_db import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    father_name = Column(String(100))
    dob = Column(String(20))
    phone = Column(String(20))
    email = Column(String(100))
    village = Column(String(100))
    post_office = Column(String(100))
    police_station = Column(String(100))
    district = Column(String(100))
    pincode = Column(String(10))
    fraud_type = Column(String(100))
    
    # ✅ Problem description text
    description = Column(Text, nullable=True)

    # ✅ Store relative path or filename of uploaded evidence
    media_files = Column(String(255), nullable=True)

    # ✅ Complaint progress
    status = Column(String(50), default="Registered")

    # ✅ Auto timestamp
    date_created = Column(DateTime, default=datetime.utcnow)
