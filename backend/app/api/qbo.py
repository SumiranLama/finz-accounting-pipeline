from fastapi import APIRouter, HTTPException
from app.database.connection import get_database
from app.services.qbo_sync import sync_transactions_to_qbo

router = APIRouter(prefix="/api/v1/qbo", tags=["QuickBooks Online Sync Engine"])

@router.post("/sync")
async def trigger_qbo_sync():
    """
    Pushes classified records to QuickBooks Online and records audit trail lineage.
    """
    db = await get_database()
    sync_result = await sync_transactions_to_qbo(db)

    if sync_result["synced_count"] == 0:
        raise HTTPException(
            status_code=400,
            detail="No pending classified transactions to sync. Make sure you have run /classify first."
        )

    return {
        "status": "success",
        "result": sync_result
    }