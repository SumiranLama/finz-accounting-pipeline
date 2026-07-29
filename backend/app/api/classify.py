from fastapi import APIRouter, HTTPException
from app.database.connection import get_database
from app.services.classifier import classify_batch_with_gemini

router = APIRouter(prefix="/api/v1", tags=["AI Classification"])

@router.post("/classify")
async def run_ai_classification():
    db = await get_database()
    
    # 1. Load Chart of Accounts
    accounts = await db.chart_of_accounts.find({}, {"_id": 0}).to_list(length=100)
    if not accounts:
        raise HTTPException(status_code=400, detail="Chart of Accounts not found. Run /upload first.")

    # 2. Fetch all unique transactions
    transactions = await db.transactions.find({
        "$or": [{"is_duplicate": False}, {"is_duplicate": {"$exists": False}}]
    }).to_list(length=500)
    
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found in MongoDB. Please re-run /api/v1/upload.")

    print(f"Processing {len(transactions)} transactions through Classification Engine...")

    batch_size = 50
    classified_count = 0

    for i in range(0, len(transactions), batch_size):
        chunk = transactions[i:i + batch_size]
        results = await classify_batch_with_gemini(chunk, accounts)

        for res in results:
            idx = res.get("tx_index")
            if idx is None or idx >= len(chunk):
                continue
            
            tx_id = chunk[idx]["_id"]
            
            await db.transactions.update_one(
                {"_id": tx_id},
                {
                    "$set": {
                        "classification": res,
                        "account_name": res.get("account_name"),
                        "transaction_type": res.get("transaction_type"),
                        "confidence": res.get("confidence"),
                        "status": "classified",
                        "review_status": "unreviewed"
                    }
                }
            )
            classified_count += 1

    return {
        "status": "success",
        "total_classified": classified_count,
        "message": f"Successfully classified {classified_count} transactions across all accounts."
    }