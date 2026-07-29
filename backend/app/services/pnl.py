from typing import Dict, Any, Optional

async def calculate_pnl_statement(db, month: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculates Cash-Basis P&L statements.
    Generates consolidated Q2 2026 totals and monthly breakdowns for April, May, and June.
    """
    match_stage = {
        "status": {"$in": ["classified", "synced"]},
        "transaction_type": {"$in": ["Revenue", "COGS", "Operating Expense"]}
    }

    # Fetch classified and synced transactions
    transactions = await db.transactions.find(match_stage).to_list(length=1000)

    def empty_summary():
        return {
            "total_revenue": 0.0,
            "total_cogs": 0.0,
            "gross_profit": 0.0,
            "total_operating_expenses": 0.0,
            "net_operating_income": 0.0
        }

    def build_pnl_structure(tx_list):
        revenue_map = {}
        cogs_map = {}
        expense_map = {}

        total_rev = 0.0
        total_cogs = 0.0
        total_exp = 0.0

        for tx in tx_list:
            name = tx.get("account_name") or "Uncategorized"
            ttype = tx.get("transaction_type")
            amt = abs(tx.get("amount", 0.0))

            if ttype == "Revenue":
                if name == "Customer Refunds":
                    total_rev -= amt
                    revenue_map[name] = revenue_map.get(name, 0.0) - amt
                else:
                    total_rev += amt
                    revenue_map[name] = revenue_map.get(name, 0.0) + amt
            elif ttype == "COGS":
                total_cogs += amt
                cogs_map[name] = cogs_map.get(name, 0.0) + amt
            elif ttype == "Operating Expense":
                total_exp += amt
                expense_map[name] = expense_map.get(name, 0.0) + amt

        revenue_items = [{"account_name": k, "amount": round(abs(v), 2)} for k, v in revenue_map.items()]
        cogs_items = [{"account_name": k, "amount": round(v, 2)} for k, v in cogs_map.items()]
        expense_items = [{"account_name": k, "amount": round(v, 2)} for k, v in expense_map.items()]

        gross_profit = total_rev - total_cogs
        net_income = gross_profit - total_exp

        return {
            "summary": {
                "total_revenue": round(total_rev, 2),
                "total_cogs": round(total_cogs, 2),
                "gross_profit": round(gross_profit, 2),
                "total_operating_expenses": round(total_exp, 2),
                "net_operating_income": round(net_income, 2)
            },
            "breakdown": {
                "revenue": revenue_items,
                "cost_of_goods_sold": cogs_items,
                "operating_expenses": expense_items
            }
        }

    # Group transactions by month
    monthly_txs = {"2026-04": [], "2026-05": [], "2026-06": []}

    for tx in transactions:
        tx_date = str(tx.get("transaction_date", ""))
        # Extract YYYY-MM prefix
        m_prefix = tx_date[:7]
        if m_prefix in monthly_txs:
            monthly_txs[m_prefix].append(tx)

    consolidated_report = build_pnl_structure(transactions)

    monthly_reports = {
        "april_2026": build_pnl_structure(monthly_txs["2026-04"]),
        "may_2026": build_pnl_structure(monthly_txs["2026-05"]),
        "june_2026": build_pnl_structure(monthly_txs["2026-06"])
    }

    if month:
        target_map = {
            "2026-04": monthly_reports["april_2026"],
            "2026-05": monthly_reports["may_2026"],
            "2026-06": monthly_reports["june_2026"]
        }
        return {
            "period": month,
            "statement": target_map.get(month, empty_summary())
        }

    return {
        "consolidated_q2_2026": consolidated_report,
        "monthly_breakdown": monthly_reports
    }