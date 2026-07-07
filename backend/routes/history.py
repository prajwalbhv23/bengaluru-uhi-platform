import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from models import UploadDataset

router = APIRouter(prefix="/api")

@router.get("/history")
async def get_upload_history(db: Session = Depends(get_db)):
    """
    Lists history of all uploaded datasets and their processing status.
    """
    datasets = db.query(UploadDataset).order_by(UploadDataset.upload_time.desc()).all()
    
    results = []
    for d in datasets:
        results.append({
            "id": d.id,
            "filename": d.filename,
            "file_type": d.file_type,
            "upload_time": d.upload_time.isoformat(),
            "status": d.status,
            "records_count": d.records_count,
            "file_path": d.file_path,
            "is_default": getattr(d, "is_default", False)
        })
        
    return results

@router.delete("/history/{dataset_id}")
async def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """
    Deletes an uploaded dataset, cascading and deleting all its predictions and recommendations,
    and removes the file from local storage.
    """
    dataset = db.query(UploadDataset).filter(UploadDataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
        
    # Prevent deletion of system/default datasets
    if getattr(dataset, "is_default", False) or dataset.filename in ["Bangalore_UHI_Production.csv", "Bengaluru_UHI_Production.csv"]:
        raise HTTPException(
            status_code=403,
            detail="The default Bengaluru dataset is protected and cannot be deleted."
        )
        
    # Delete file from local disk
    try:
        if os.path.exists(dataset.file_path):
            os.remove(dataset.file_path)
    except Exception as e:
        print(f"Error removing file from disk: {e}")
        
    # Remove from DB (cascading takes care of hotspots and recommendations)
    db.delete(dataset)
    db.commit()
    
    return {"message": f"Dataset {dataset_id} successfully deleted from database and storage."}
