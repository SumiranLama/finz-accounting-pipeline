import uuid
from datetime import datetime
from typing import Dict, Any

async def sync_transactions_to_qbo(db) -> Dict[str, Any]:
    """
    Simulates syncing classified transactions to QuickBooks Online Sandbox API.
    Attaches audit lineage (confidence scores, rationales, timestamps) and updates status.
    """
    # Fetch all classified records that are not duplicates
    transactions = await db.transactions.find({
        "status": "classified",
        "is_duplicate": False
    }).to_list(length=500)

    if not transactions:
        return {
            "synced_count": 0,
            "message": "No pending classified transactions found to sync."
        }

    synced_records = []
    
    for tx in transactions:
        qbo_id = f"QBO-{uuid.uuid4().hex[:8].upper()}"
        sync_timestamp = datetime.utcnow().isoformat() + "Z"

        audit_trail = {
            "qbo_transaction_id": qbo_id,
            "synced_at": sync_timestamp,
            "qbo_sync_status": "SUCCESS",
            "source_file": tx.get("source_file"),
            "original_bank_id": tx.get("bank_transaction_id"),
            "ai_classification": {
                "account_name": tx.get("account_name"),
                "account_code": tx.get("account_code"),
                "confidence": tx.get("confidence"),
                "rationale": tx.get("classification", {}).get("rationale", "")
            }
        }

        # Mark as synced in MongoDB Atlas
        await db.transactions.update_one(
            {"_id": tx["_id"]},
            {
                "$set": {
                    "status": "synced",
                    "qbo_sync": audit_trail
                }
            }
        )

        synced_records.append({
            "bank_tx_id": tx.get("bank_transaction_id"),
            "qbo_id": qbo_id,
            "account_name": tx.get("account_name"),
            "amount": tx.get("amount")
        })

    return {
        "synced_count": len(synced_records),
        "message": f"Successfully synced {len(synced_records)} transactions to QuickBooks Online.",
        "synced_sample": synced_records[:5]
    }