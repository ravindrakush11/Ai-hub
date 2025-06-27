from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from database import Complaint, SessionLocal
from datetime import datetime
import uuid

app = FastAPI()

class ComplaintIn(BaseModel):
    name: str
    phone_number: str
    email: EmailStr
    complaint_details: str

@app.post("/complaints")
def create_complaint(complaint: ComplaintIn):
    db = SessionLocal()
    new_complaint = Complaint(
        complaint_id=str(uuid.uuid4())[:8],
        name=complaint.name,
        phone_number=complaint.phone_number,
        email=complaint.email,
        complaint_details=complaint.complaint_details
    )
    db.add(new_complaint)
    db.commit()
    return {"complaint_id": new_complaint.complaint_id, "message": "Complaint created successfully"}

@app.get("/complaints/{complaint_id}")
def get_complaint(complaint_id: str):
    db = SessionLocal()
    result = db.query(Complaint).filter_by(complaint_id=complaint_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return {
        "complaint_id": result.complaint_id,
        "name": result.name,
        "phone_number": result.phone_number,
        "email": result.email,
        "complaint_details": result.complaint_details,
        "created_at": result.created_at
    }
