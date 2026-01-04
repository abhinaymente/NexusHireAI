from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import os
import time

from google_auth import get_credentials, SCOPES_SHEETS_DRIVE
from resume_reader import extract_text
from ai_evaluator import check_resume
from email_sender import send_email
from calendar_invite import schedule_interview
from database import init_db, SessionLocal, ScreeningBatch, CandidateResult, User, get_db
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()
    port = os.getenv("PORT", "unknown")
    print(f"--- NexusHire AI Starting on Port: {port} ---")

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- GLOBAL STATE ----------
LOGS = []
RESULTS = []

def log(msg: str):
    timestamp = time.strftime("%H:%M:%S")
    LOGS.append(f"[{timestamp}] {msg}")

# ---------- REQUEST MODEL ----------
class SheetRequest(BaseModel):
    sheet_link: str
    company_name: str = "DUDE TECH"
    tagline: str = "Building smart hiring systems"
    role_name: str = "Software Engineer"
    role_requirements: str = "Programming skills AND CS/IT education"
    use_own_smtp: bool = False
    smtp_config: dict = None

# ---------- HELPERS ----------
def get_services():
    """Lazy load services to avoid startup crash if creds are missing"""
    print("Loading Google Credentials...")
    creds = get_credentials(SCOPES_SHEETS_DRIVE)
    sheets = build("sheets", "v4", credentials=creds)
    drive = build("drive", "v3", credentials=creds)
    return sheets, drive

def extract_sheet_id(link: str):
    return link.split("/d/")[1].split("/")[0]

def extract_file_id(link: str):
    if "id=" in link:
        return link.split("id=")[1]
    return link.split("/d/")[1].split("/")[0]

def download_resume(drive_service, file_id: str, filename: str):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(filename, "wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

# ---------- BACKGROUND JOB ----------
def run_processing(req: SheetRequest, user_id: int):
    LOGS.clear()
    RESULTS.clear()

    db = SessionLocal()
    try:
        log("Initializing services...")
        try:
            sheets_service, drive_service = get_services()
        except Exception as e:
            log(f"CRITICAL ERROR: Failed to load Google Credentials: {e}")
            return

        log(f"Started screening for {req.role_name} at {req.company_name}")

        sheet_id = extract_sheet_id(req.sheet_link)
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="Form Responses 1"
        ).execute()

        rows = result.get("values", [])

        if len(rows) < 2:
            log("No responses found in Google Sheet")
            log("All resumes processed")
            return

        headers = rows[0]
        data_rows = rows[1:]
        total_rows = len(data_rows)

        lower_headers = [h.lower().strip() for h in headers]
        
        try:
            email_idx = -1
            resume_idx = -1
            for i, h in enumerate(lower_headers):
                if "email" in h: email_idx = i
                if "resume" in h or "upload" in h or "cv" in h: resume_idx = i

            if email_idx == -1 or resume_idx == -1:
                log(f"Error: Columns not found. Headers: {headers}")
                return
        except Exception as e:
            log(f"Header parsing error: {e}")
            return

        # Save Batch to DB
        new_batch = ScreeningBatch(
            user_id=user_id,
            company_name=req.company_name,
            tagline=req.tagline,
            role_name=req.role_name,
            role_requirements=req.role_requirements
        )
        db.add(new_batch)
        db.commit()
        db.refresh(new_batch)

        for i, row in enumerate(data_rows, start=1):
            progress = int((i / total_rows) * 100)
            if len(row) <= max(email_idx, resume_idx):
                log(f"[{progress}%] Skipping empty row {i}")
                continue

            email = row[email_idx]
            resume_link = row[resume_idx]

            log(f"[{progress}%] Processing {email}")

            try:
                file_id = extract_file_id(resume_link)
                filename = f"resume_{i}.pdf"

                log(f"[{progress}%] Analyzing {email}...")
                download_resume(drive_service, file_id, filename)
                resume_text = extract_text(filename)
                
                decision = check_resume(resume_text, req.role_name, req.role_requirements)
                status = "ELIGIBLE" if decision.startswith("ELIGIBLE") else "NOT ELIGIBLE"

                log(f"[{progress}%] Sending result to {email}...")
                if status == "ELIGIBLE":
                    meet = schedule_interview()
                    send_email(
                        email, f"ELIGIBLE\nMeet: {meet}",
                        company_name=req.company_name,
                        tagline=req.tagline,
                        role_name=req.role_name,
                        use_own_smtp=req.use_own_smtp,
                        smtp_config=req.smtp_config
                    )
                else:
                    send_email(
                        email, "NOT ELIGIBLE",
                        company_name=req.company_name,
                        tagline=req.tagline,
                        role_name=req.role_name,
                        use_own_smtp=req.use_own_smtp,
                        smtp_config=req.smtp_config
                    )

                RESULTS.append({"email": email, "status": status})
                
                # Save Individual Result to DB
                new_res = CandidateResult(batch_id=new_batch.id, email=email, status=status)
                db.add(new_res)
                db.commit()

                if os.path.exists(filename): os.remove(filename)

            except Exception as e:
                log(f"[{progress}%] ERROR for {email}: {str(e)}")
                RESULTS.append({"email": email, "status": "ERROR"})

        log("100% - All resumes processed")
    except Exception as e:
        log(f"FATAL ERROR: {str(e)}")
    finally:
        db.close()

# ---------- ROUTES ----------
# ---------- AUTH ROUTES ----------
@app.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(email=email, hashed_password=get_password_hash(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success"}

@app.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# ---------- CORE ROUTES ----------
@app.get("/")
def health_check():
    return {"status": "ok", "message": "NexusHire AI Secure API is running"}

@app.post("/process")
def start(data: SheetRequest, bg: BackgroundTasks, user: dict = Depends(get_current_user)):
    bg.add_task(run_processing, data, user["id"])
    return {"status": "started"}

@app.get("/logs")
def get_logs(user: dict = Depends(get_current_user)):
    return {"logs": LOGS}

@app.get("/results")
def get_results(user: dict = Depends(get_current_user)):
    return {"results": RESULTS}

@app.get("/history")
def get_history(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    batches = db.query(ScreeningBatch).filter(ScreeningBatch.user_id == user["id"]).order_by(ScreeningBatch.timestamp.desc()).all()
    history = []
    for b in batches:
        history.append({
            "id": b.id,
            "company": b.company_name,
            "role": b.role_name,
            "date": b.timestamp.strftime("%Y-%m-%d %H:%M"),
            "count": len(b.results)
        })
    return {"history": history}

@app.get("/history/{batch_id}")
def get_batch_results(batch_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    batch = db.query(ScreeningBatch).filter(ScreeningBatch.id == batch_id, ScreeningBatch.user_id == user["id"]).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    results = [{"email": r.email, "status": r.status} for r in batch.results]
    return {
        "company": batch.company_name,
        "role": batch.role_name,
        "results": results
    }
