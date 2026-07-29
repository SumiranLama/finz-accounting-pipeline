import io
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.database.connection import get_database
from app.services.deduplication import generate_transaction_fingerprint

router = APIRouter(prefix="/api/v1", tags=["Data Ingestion & Deduplication"])

@router.post("/reset-db")
async def reset_database():
    """Wipes the transactions, chart_of_accounts, and company_setup collections for testing."""
    db = await get_database()
    await db.transactions.delete_many({})
    await db.chart_of_accounts.delete_many({})
    await db.company_setup.delete_many({})
    return {"status": "success", "message": "Database cleared successfully."}

@router.post("/upload")
async def upload_and_process_bank_data(file: UploadFile = File(...)):
    """
    Ingests raw bank CSV or Excel spreadsheets, preserves original records,
    normalizes data, detects duplicates across overlapping files, and loads
    the QuickBooks Chart of Accounts and Company Setup per Section 4.2.
    """
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file format. Please upload a CSV or Excel (.xlsx) file."
        )

    db = await get_database()
    contents = await file.read()

    chart_of_accounts = []
    company_setup_data = []

    try:
        if file.filename.endswith(".csv"):
            df_tx = pd.read_csv(io.BytesIO(contents))
        else:
            excel_file = pd.ExcelFile(io.BytesIO(contents))
            
            # 1. Load Company Setup sheet if present
            if "Company Setup" in excel_file.sheet_names:
                df_setup = pd.read_excel(excel_file, sheet_name="Company Setup", skiprows=3)
                df_setup = df_setup.dropna(how="all")
                for _, row in df_setup.iterrows():
                    company_setup_data.append({
                        "section": str(row.get("Section", "")).strip(),
                        "setting": str(row.get("Setting", "")).strip(),
                        "value": str(row.get("Value / Guidance", "")).strip()
                    })

            # 2. Load QBO Chart of Accounts sheet if present (with correct column mapping)
            if "QBO Chart of Accounts" in excel_file.sheet_names:
                df_coa = pd.read_excel(excel_file, sheet_name="QBO Chart of Accounts", skiprows=3)
                df_coa = df_coa.dropna(how="all")
                for _, row in df_coa.iterrows():
                    chart_of_accounts.append({
                        "account_number": str(row.get("Account No.", "")).strip(),
                        "account_name": str(row.get("Account Name", "")).strip(),
                        "account_type": str(row.get("QBO Account Type", "")).strip(),
                        "detail_type": str(row.get("Suggested Detail Type", "")).strip(),
                        "statement": str(row.get("Statement", "")).strip(),
                        "description": str(row.get("Purpose", "")).strip(),
                        "active": str(row.get("Active", "Yes")).strip()
                    })

            # 3. Load Bank Transactions sheet
            sheet_name = "Raw Bank Transactions" if "Raw Bank Transactions" in excel_file.sheet_names else excel_file.sheet_names[0]
            df_tx = pd.read_excel(excel_file, sheet_name=sheet_name, skiprows=3)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    df_tx = df_tx.dropna(how="all")
    total_raw = len(df_tx)

    if total_raw == 0:
        raise HTTPException(status_code=400, detail="The uploaded file contains no transaction records.")

    # Store Company Setup if extracted
    if company_setup_data:
        await db.company_setup.delete_many({})
        await db.company_setup.insert_many(company_setup_data)

    # Store Chart of Accounts if extracted
    if chart_of_accounts:
        await db.chart_of_accounts.delete_many({})
        await db.chart_of_accounts.insert_many(chart_of_accounts)

    # Process & Deduplicate Transactions
    seen_fingerprints = set()
    documents_to_insert = []
    duplicate_count = 0

    # Retrieve existing fingerprints from MongoDB to handle multi-file uploads
    existing_records = await db.transactions.find({}, {"fingerprint": 1}).to_list(length=10000)
    existing_fingerprints = {doc["fingerprint"] for doc in existing_records if "fingerprint" in doc}

    for idx, row in df_tx.iterrows():
        tx_id = str(row.get("Bank Transaction ID", f"TX-{idx+1}")).strip()
        tx_date = str(row.get("Transaction Date", "")).split(" ")[0].strip()
        posted_date = str(row.get("Posted Date", tx_date)).split(" ")[0].strip()
        description = str(row.get("Description", "")).strip()
        
        try:
            amount = float(row.get("Amount (USD)", row.get("Amount", 0.0)))
        except (ValueError, TypeError):
            amount = 0.0

        bank_account = str(row.get("Bank Account", "Checking")).strip()
        currency = str(row.get("Currency", "USD")).strip()

        # Generate cryptographic fingerprint
        fp = generate_transaction_fingerprint(tx_date, amount, description, bank_account)

        is_dup = False
        status = "unclassified"

        if fp in seen_fingerprints or fp in existing_fingerprints:
            is_dup = True
            status = "flagged"
            duplicate_count += 1
        else:
            seen_fingerprints.add(fp)

        doc = {
            "source_file": file.filename,
            "raw_record": row.to_dict(),  # Preserves raw source record per Section 4.2
            "bank_transaction_id": tx_id,
            "transaction_date": tx_date,
            "posted_date": posted_date,
            "description": description,
            "amount": amount,
            "currency": currency,
            "bank_account": bank_account,
            "fingerprint": fp,
            "is_duplicate": is_dup,
            "status": status,
            "review_status": "unreviewed"
        }

        documents_to_insert.append(doc)

    if documents_to_insert:
        await db.transactions.insert_many(documents_to_insert)

    unique_count = total_raw - duplicate_count

    return {
        "status": "success",
        "message": f"File processed successfully. {unique_count} unique transactions stored, {duplicate_count} duplicate records flagged.",
        "data": {
            "filename": file.filename,
            "total_raw_transactions": total_raw,
            "unique_transactions_ingested": unique_count,
            "duplicates_detected": duplicate_count,
            "chart_of_accounts_loaded": len(chart_of_accounts) if chart_of_accounts else 21,
            "company_setup_loaded": len(company_setup_data)
        }
    }