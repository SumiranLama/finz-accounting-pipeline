import io
import math
import pandas as pd
from typing import Dict, Any, List

def clean_val(val: Any) -> Any:
    """Helper to convert NaN/Float values safely for MongoDB"""
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    if pd.isna(val):
        return None
    return val

def read_sheet_with_header(excel_file: pd.ExcelFile, sheet_name: str, target_col_keyword: str) -> pd.DataFrame:
    """Reads an Excel sheet and dynamically finds the header row containing a target keyword."""
    df_raw = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
    header_idx = 0
    for idx, row in df_raw.iterrows():
        row_str = " ".join([str(cell) for cell in row.values if pd.notna(cell)])
        if target_col_keyword.lower() in row_str.lower():
            header_idx = idx
            break
    return pd.read_excel(excel_file, sheet_name=sheet_name, header=header_idx)

def parse_excel_workbook(file_bytes: bytes) -> Dict[str, Any]:
    file_stream = io.BytesIO(file_bytes)
    excel_file = pd.ExcelFile(file_stream)
    
    # 1. Parse Company Setup dynamically
    company_df = read_sheet_with_header(excel_file, "Company Setup", "Setting")
    company_df = company_df.dropna(how="all")
    company_info = {}
    
    # Extract key-value pairs (Setting -> Value)
    for _, row in company_df.iterrows():
        k = clean_val(row.iloc[1]) if len(row) > 1 else None
        v = clean_val(row.iloc[2]) if len(row) > 2 else None
        if k and str(k).strip().lower() not in ["setting", "nan"]:
            company_info[str(k).strip()] = v

    # 2. Parse Chart of Accounts dynamically
    accounts_df = read_sheet_with_header(excel_file, "QBO Chart of Accounts", "Account No.")
    accounts_df = accounts_df.dropna(how="all")
    chart_of_accounts = []
    for record in accounts_df.to_dict(orient="records"):
        clean_record = {str(k).strip(): clean_val(v) for k, v in record.items() if pd.notna(k) and str(k).strip().lower() != "nan"}
        if clean_record.get("Account No.") and str(clean_record.get("Account No.")).strip().lower() != "account no.":
            chart_of_accounts.append(clean_record)

    # 3. Parse Raw Bank Transactions dynamically
    raw_tx_df = read_sheet_with_header(excel_file, "Raw Bank Transactions", "Transaction Date")
    raw_tx_df = raw_tx_df.dropna(how="all")
    
    # Clean column names
    raw_tx_df.columns = [str(c).strip() for c in raw_tx_df.columns]
    
    transactions: List[Dict[str, Any]] = []
    seen_fingerprints = set()
    duplicates_count = 0

    for idx, row in raw_tx_df.iterrows():
        tx_date = str(clean_val(row.get("Transaction Date", "")) or "").split(" ")[0]
        posted_date = str(clean_val(row.get("Posted Date", "")) or "").split(" ")[0]
        
        raw_amt = row.get("Amount (USD)", 0.0)
        amount = float(raw_amt) if pd.notna(raw_amt) else 0.0
        
        desc = str(clean_val(row.get("Description", "")) or "").strip()
        account = str(clean_val(row.get("Bank Account", "")) or "").strip()
        bank_tx_id = str(clean_val(row.get("Bank Transaction ID", "")) or "").strip()

        # Skip invalid empty rows
        if not tx_date or tx_date.lower() == "nan":
            continue

        fingerprint = f"{tx_date}_{amount}_{desc}_{account}".lower()
        
        is_dup = fingerprint in seen_fingerprints
        if is_dup:
            duplicates_count += 1
        else:
            seen_fingerprints.add(fingerprint)

        tx_doc = {
            "source_file": str(clean_val(row.get("Source File", "")) or ""),
            "bank_transaction_id": bank_tx_id,
            "transaction_date": tx_date,
            "posted_date": posted_date,
            "description": desc,
            "amount": amount,
            "currency": str(clean_val(row.get("Currency", "USD")) or "USD"),
            "bank_account": account,
            "fingerprint": fingerprint,
            "is_duplicate": is_dup,
            "status": "flagged" if is_dup else "pending",
            "review_status": "unreviewed"
        }
        transactions.append(tx_doc)

    return {
        "company_info": company_info,
        "chart_of_accounts": chart_of_accounts,
        "transactions": transactions,
        "total_raw": len(transactions),
        "duplicates_count": duplicates_count,
        "unique_count": len(transactions) - duplicates_count
    }