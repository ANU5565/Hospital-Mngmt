thon
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from backend.database.models.doctor_models import Doctor
from backend.database.schemas import UserCreate
from backend.database.permissions import check_permissions

doctors = APIRouter()

@doctors.post("/appointments", dependencies=[Depends(check_permissions("DOCTOR"))])
def create_appointment(doctor: str, patient_name: str):
    doctor = Doctor.query.filter_by(name=doctor).first()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    
    appointment = {
        "doctor": doctor.id,
        "patient_name": patient_name
    }
    
    # Add logic to save the appointment in database
    return {"message": "Appointment booked successfully"}