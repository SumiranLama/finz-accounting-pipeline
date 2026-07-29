import hashlib

def generate_transaction_fingerprint(date: str, amount: float, description: str, bank_account: str) -> str:
    """
    Generates a deterministic SHA-256 fingerprint hash for a bank transaction.
    Identifies identical transactions across overlapping date range bank CSV/Excel exports.
    """
    norm_date = str(date).strip().lower()
    norm_amount = f"{float(amount):.2f}"
    norm_desc = str(description).strip().lower()
    norm_acc = str(bank_account).strip().lower()

    raw_string = f"{norm_date}_{norm_amount}_{norm_desc}_{norm_acc}"
    return hashlib.sha256(raw_string.encode("utf-8")).hexdigest()