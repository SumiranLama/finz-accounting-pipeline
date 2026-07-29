from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BankTransaction(BaseModel):
    source_file: str
    bank_transaction_id: str
    transaction_date: str
    posted_date: str
    description: str
    amount: float
    currency: str
    bank_account: str
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    category: Optional[str] = None
    account_code: Optional[str] = None
    status: str = "pending"  # pending, approved, synced, flagged

class UploadResponse(BaseModel):
    filename: str
    company_name: Optional[str] = None
    total_transactions_raw: int
    unique_transactions_count: int
    duplicates_detected_count: int
    accounts_loaded_count: int
    message: str