from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.auth import get_current_user
from app.database import get_database
from app.report_engine import build_report
from app.schemas import MedicalReportCreate, ReportSummary

router = APIRouter(tags=["reports"])
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}


def _build_report_summary(current_user: dict, payload: MedicalReportCreate, file_url: str | None = None) -> dict:
    report = build_report(
        patient={
            "name": payload.patient_name,
            "id": payload.patient_name.replace(" ", "-").upper(),
            "date": datetime.now(timezone.utc).date().isoformat(),
        },
        vitals={
            "heart_rate": payload.heart_rate,
            "bp_systolic": payload.bp_systolic,
            "bp_diastolic": payload.bp_diastolic,
            "temperature": payload.temperature,
            "spo2": payload.spo2,
            "ecg": payload.ecg,
        },
    )
    return {
        "user_id": current_user["_id"],
        "patient_name": payload.patient_name,
        "age": payload.age,
        "vitals": {
            "heart_rate": payload.heart_rate,
            "bp": f"{payload.bp_systolic}/{payload.bp_diastolic}",
            "temperature": payload.temperature,
            "spo2": payload.spo2,
            "ecg": payload.ecg,
            "notes": payload.notes,
        },
        "diagnosis": report["diagnosis"],
        "insights": report["insights"],
        "alerts": report["alerts"],
        "recommendation": report["recommendation"],
        "file_url": file_url,
        "created_at": datetime.now(timezone.utc),
    }


async def _store_report(db, current_user: dict, payload: MedicalReportCreate, file_url: str | None = None):
    record = _build_report_summary(current_user, payload, file_url)
    result = await db.reports.insert_one(record)
    return ReportSummary(
        id=str(result.inserted_id),
        patient_name=record["patient_name"],
        age=record["age"],
        condition=record["diagnosis"]["condition"],
        severity=record["diagnosis"]["severity"],
        file_url=record["file_url"],
        created_at=record["created_at"],
        diagnosis=record["diagnosis"],
        vitals=record["vitals"],
        insights=record["insights"],
        alerts=record["alerts"],
        recommendation=record["recommendation"],
    )


@router.post("/submit-report", response_model=ReportSummary)
async def submit_report(payload: MedicalReportCreate, current_user=Depends(get_current_user), db=Depends(get_database)):
    return await _store_report(db, current_user, payload)


@router.post("/upload-report", response_model=ReportSummary)
async def upload_report(
    patient_name: str = Form(...),
    age: int = Form(...),
    heart_rate: int = Form(...),
    bp_systolic: int = Form(...),
    bp_diastolic: int = Form(...),
    temperature: float = Form(...),
    spo2: float = Form(...),
    ecg: str = Form(...),
    notes: str = Form(default=""),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db=Depends(get_database),
):
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only JPG, PNG, and PDF files are allowed")

    safe_name = f"{uuid4()}{extension}"
    file_path = UPLOAD_DIR / safe_name
    contents = await file.read()
    file_path.write_bytes(contents)
    file_url = f"/uploads/{safe_name}"

    payload = MedicalReportCreate(
        patient_name=patient_name,
        age=age,
        heart_rate=heart_rate,
        bp_systolic=bp_systolic,
        bp_diastolic=bp_diastolic,
        temperature=temperature,
        spo2=spo2,
        ecg=ecg,
        notes=notes,
    )
    return await _store_report(db, current_user, payload, file_url=file_url)


@router.get("/reports", response_model=list[ReportSummary])
async def list_reports(current_user=Depends(get_current_user), db=Depends(get_database)):
    cursor = db.reports.find({"user_id": current_user["_id"]}).sort("created_at", -1).limit(50)
    reports: list[ReportSummary] = []
    async for item in cursor:
        reports.append(
            ReportSummary(
                id=str(item["_id"]),
                patient_name=item["patient_name"],
                age=int(item["age"]),
                condition=item["diagnosis"]["condition"],
                severity=item["diagnosis"]["severity"],
                file_url=item.get("file_url"),
                created_at=item["created_at"],
                diagnosis=item["diagnosis"],
                vitals=item["vitals"],
                insights=item.get("insights", []),
                alerts=item.get("alerts", []),
                recommendation=item.get("recommendation", ""),
            )
        )
    return reports
