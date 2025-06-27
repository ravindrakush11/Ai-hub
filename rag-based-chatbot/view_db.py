from database import SessionLocal, Complaint

db = SessionLocal()
complaints = db.query(Complaint).all()

for c in complaints:
    print(f"""
Complaint ID : {c.complaint_id}
Name         : {c.name}
Phone Number : {c.phone_number}
Email        : {c.email}
Details      : {c.complaint_details}
Created At   : {c.created_at}
    """)
