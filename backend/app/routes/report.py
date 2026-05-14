from fastapi import APIRouter, Depends, Query

from app.auth import get_current_user
from app.report_engine import build_report
from app.schemas import HealthReportResponse

router = APIRouter(tags=["report"])


@router.get("/report", response_model=HealthReportResponse)
async def get_report(
    patient_name: str = Query(default="Unknown Patient"),
    patient_id: str = Query(default="Unknown"),
    report_date: str | None = Query(default=None),
    heart_rate: int = Query(..., ge=0),
    bp_systolic: int = Query(..., ge=0),
    bp_diastolic: int = Query(..., ge=0),
    temperature: float = Query(...),
    spo2: float = Query(...),
    ecg: str = Query(default="Normal"),
    current_user=Depends(get_current_user),
):
    _ = current_user
    return build_report(
        patient={"name": patient_name, "id": patient_id, "date": report_date or ""},
        vitals={
            "heart_rate": heart_rate,
            "bp_systolic": bp_systolic,
            "bp_diastolic": bp_diastolic,
            "temperature": temperature,
            "spo2": spo2,
            "ecg": ecg,
        },
    )
