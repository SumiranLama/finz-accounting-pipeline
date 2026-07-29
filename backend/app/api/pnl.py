from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.database.connection import get_database

router = APIRouter(prefix="/api/v1", tags=["P&L Engine"])

@router.get("/pnl")
async def get_pnl_statement() -> Dict[str, Any]:
    """
    Generates Cash-Basis Profit & Loss Statement for Q2 2026 (Monthly & Consolidated).
    Excludes non-P&L items (Transfers, Owner Draws, Fixed Assets, Duplicates).
    """
    db = await get_database()
    
    # 1. Guard Check: Ensure dataset has been ingested & classified
    total_tx_count = await db.transactions.count_documents({"is_duplicate": False})
    if total_tx_count == 0:
        raise HTTPException(
            status_code=400,
            detail="No valid transactions found in database. Please upload a bank statement and run AI Classification in Step 1 first."
        )

    # 2. Query all non-duplicate, classified transactions
    query = {
        "is_duplicate": False,
        "status": {"$in": ["classified", "approved", "synced"]}
    }
    
    cursor = db.transactions.find(query)
    transactions = await cursor.to_list(length=1000)

    if not transactions:
        raise HTTPException(
            status_code=400,
            detail="No classified transactions available. Please run 'Run AI Classifier' in Step 1 first."
        )

    # 3. Initialize P&L Structures
    months = ["april_2026", "may_2026", "june_2026"]
    monthly_data = {
        m: {
            "revenue": {},
            "cogs": {},
            "operating_expenses": {}
        } for m in months
    }

    consolidated_data = {
        "revenue": {},
        "cogs": {},
        "operating_expenses": {}
    }

    # 4. Process Transactions into Accounts
    for tx in transactions:
        tx_date = tx.get("transaction_date", tx.get("date", ""))
        amount = tx.get("amount", 0.0)
        account_name = tx.get("account_name") or tx.get("classified_account")
        account_type = tx.get("account_type", "").lower()

        # Identify target month
        month_key = None
        if "2026-04" in tx_date:
            month_key = "april_2026"
        elif "2026-05" in tx_date:
            month_key = "may_2026"
        elif "2026-06" in tx_date:
            month_key = "june_2026"

        if not month_key or not account_name:
            continue

        # Determine Category Bucket
        category_bucket = None
        if account_type == "revenue" or "revenue" in account_name.lower() or "refund" in account_name.lower():
            category_bucket = "revenue"
        elif account_type in ["cogs", "cost_of_goods_sold"] or "materials" in account_name.lower():
            category_bucket = "cogs"
        elif account_type in ["expense", "operating_expense"] or any(exp in account_name.lower() for exp in ["rent", "payroll", "office", "utilities", "vehicle", "software", "insurance", "professional", "marketing"]):
            category_bucket = "operating_expenses"

        # Skip Non-P&L Transactions (Transfers, Owner Draws, Assets)
        if not category_bucket:
            continue

        # Accrual / Credit adjustments (Revenue is positive, expenses positive in P&L)
        pnl_amount = abs(amount) if category_bucket in ["cogs", "operating_expenses"] else amount

        # Populate Monthly Breakdown
        m_dict = monthly_data[month_key][category_bucket]
        m_dict[account_name] = m_dict.get(account_name, 0.0) + pnl_amount

        # Populate Consolidated Breakdown
        c_dict = consolidated_data[category_bucket]
        c_dict[account_name] = c_dict.get(account_name, 0.0) + pnl_amount

    # Helper function to compute summaries
    def build_summary(cat_data):
        tot_rev = sum(cat_data["revenue"].values())
        tot_cogs = sum(cat_data["cogs"].values())
        gross_profit = tot_rev - tot_cogs
        tot_exp = sum(cat_data["operating_expenses"].values())
        net_income = gross_profit - tot_exp

        return {
            "summary": {
                "total_revenue": round(tot_rev, 2),
                "total_cogs": round(tot_cogs, 2),
                "gross_profit": round(gross_profit, 2),
                "total_operating_expenses": round(tot_exp, 2),
                "net_operating_income": round(net_income, 2)
            },
            "breakdown": {
                "revenue": [{"account_name": k, "amount": round(v, 2)} for k, v in cat_data["revenue"].items()],
                "cost_of_goods_sold": [{"account_name": k, "amount": round(v, 2)} for k, v in cat_data["cogs"].items()],
                "operating_expenses": [{"account_name": k, "amount": round(v, 2)} for k, v in cat_data["operating_expenses"].items()]
            }
        }

    # 5. Build Output Payload
    monthly_breakdown_res = {m: build_summary(monthly_data[m]) for m in months}
    consolidated_res = build_summary(consolidated_data)

    return {
        "status": "success",
        "pnl_statement": {
            "period": "Q2 2026 Consolidated & Monthly Performance",
            "consolidated_q2_2026": consolidated_res,
            "monthly_breakdown": monthly_breakdown_res
        }
    }