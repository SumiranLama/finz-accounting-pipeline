import os
import json
from dotenv import load_dotenv

load_dotenv()

def rule_based_classify(tx: dict, chart_of_accounts: list) -> dict:
    """Classifies transactions according to BrightFix Home Services accounting rules."""
    desc = tx.get("description", "").upper()
    amount = tx.get("amount", 0.0)

    # 1. Fixed Asset (Tools & Equipment) -> Excluded from P&L
    if "EQUIPMENT" in desc or "TOOL" in desc:
        return {
            "account_name": "Tools & Equipment",
            "account_code": "1500",
            "transaction_type": "Fixed Asset",
            "confidence": 0.98,
            "rationale": "Commercial equipment or tool purchase mapped to Fixed Assets (Balance Sheet)."
        }

    # 2. Owner Activity (Equity) -> Excluded from P&L
    if "OWNER" in desc or "CAPITAL" in desc or "DRAW" in desc or "MAYA PATEL" in desc:
        return {
            "account_name": "Owner's Equity",
            "account_code": "3000",
            "transaction_type": "Owner Activity",
            "confidence": 0.98,
            "rationale": "Owner equity contribution or distribution (Balance Sheet)."
        }

    # 3. Tax Reserve Transfers -> Excluded from P&L
    if "TAX RESERVE" in desc or "INTERNAL TRANSFER" in desc:
        return {
            "account_name": "Tax Reserve",
            "account_code": "1010",
            "transaction_type": "Transfer",
            "confidence": 0.98,
            "rationale": "Internal bank transfer between operating and reserve accounts."
        }

    # 4. Customer Refunds
    if "REFUND" in desc and amount < 0:
        return {
            "account_name": "Customer Refunds",
            "account_code": "4100",
            "transaction_type": "Revenue",
            "confidence": 0.95,
            "rationale": "Contra-revenue refund granted to customer."
        }

    # 5. Revenue Categories
    if amount > 0:
        if "INSTALL" in desc:
            return {
                "account_name": "Installation Revenue",
                "account_code": "4010",
                "transaction_type": "Revenue",
                "confidence": 0.95,
                "rationale": "Customer payment received for installation project."
            }
        elif "MAINTENANCE" in desc or "PLAN" in desc:
            return {
                "account_name": "Maintenance Plan Revenue",
                "account_code": "4020",
                "transaction_type": "Revenue",
                "confidence": 0.95,
                "rationale": "Recurring maintenance plan revenue."
            }
        else:
            return {
                "account_name": "Repair Service Revenue",
                "account_code": "4000",
                "transaction_type": "Revenue",
                "confidence": 0.92,
                "rationale": "Customer payment received for repair and maintenance service."
            }

    # 6. Cost of Goods Sold (COGS)
    if "HOME DEPOT" in desc or "HARDWARE" in desc or "SUPPLIES" in desc or "MATERIALS" in desc:
        return {
            "account_name": "Materials & Supplies",
            "account_code": "5000",
            "transaction_type": "COGS",
            "confidence": 0.95,
            "rationale": "Job materials and supplies consumed on customer work."
        }
    if "SUBCONTRACTOR" in desc or "LABOR" in desc or "CRAFT" in desc:
        return {
            "account_name": "Subcontractor Costs",
            "account_code": "5010",
            "transaction_type": "COGS",
            "confidence": 0.95,
            "rationale": "Third-party contractor labor utilized for jobs."
        }

    # 7. Operating Expenses
    if "PAYROLL" in desc or "GUSTO" in desc or "ADP" in desc or "WAGES" in desc:
        return {
            "account_name": "Payroll Expense",
            "account_code": "6000",
            "transaction_type": "Operating Expense",
            "confidence": 0.98,
            "rationale": "Employee compensation and payroll processing costs."
        }
    if "RENT" in desc or "PARKSIDE COMMERCIAL" in desc or "LEASE" in desc:
        return {
            "account_name": "Rent Expense",
            "account_code": "6010",
            "transaction_type": "Operating Expense",
            "confidence": 0.98,
            "rationale": "Commercial office and facility lease payment."
        }
    if "SHELL" in desc or "CHEVRON" in desc or "FUEL" in desc or "AUTO" in desc:
        return {
            "account_name": "Vehicle & Fuel",
            "account_code": "6020",
            "transaction_type": "Operating Expense",
            "confidence": 0.95,
            "rationale": "Fuel and service vehicle operating expenses."
        }
    if "SOFTWARE" in desc or "AWS" in desc or "GOOGLE" in desc or "MICROSOFT" in desc or "SLACK" in desc or "INTUIT" in desc:
        return {
            "account_name": "Software & Subscriptions",
            "account_code": "6030",
            "transaction_type": "Operating Expense",
            "confidence": 0.95,
            "rationale": "Operational cloud software and SaaS subscriptions."
        }
    if "GOOGLE ADS" in desc or "META" in desc or "MARKETING" in desc or "YELP" in desc:
        return {
            "account_name": "Marketing & Advertising",
            "account_code": "6040",
            "transaction_type": "Operating Expense",
            "confidence": 0.95,
            "rationale": "Digital advertising and customer lead generation."
        }
    if "INSURANCE" in desc or "POLICY" in desc or "STATE FARM" in desc:
        return {
            "account_name": "Insurance Expense",
            "account_code": "6050",
            "transaction_type": "Operating Expense",
            "confidence": 0.95,
            "rationale": "Commercial liability business insurance policy premium."
        }
    if "POWER" in desc or "ELECTRIC" in desc or "UTILITIES" in desc or "COMCAST" in desc or "WATER" in desc:
        return {
            "account_name": "Utilities",
            "account_code": "6060",
            "transaction_type": "Operating Expense",
            "confidence": 0.95,
            "rationale": "Utility, power, internet, and phone operating expenses."
        }
    if "CPA" in desc or "LEGAL" in desc or "ACCOUNTING" in desc or "ATTORNEY" in desc:
        return {
            "account_name": "Professional Fees",
            "account_code": "6070",
            "transaction_type": "Operating Expense",
            "confidence": 0.95,
            "rationale": "Professional accounting and legal retainer fees."
        }
    if "BANK FEE" in desc or "SERVICE CHARGE" in desc or "WIRE FEE" in desc:
        return {
            "account_name": "Bank Fees",
            "account_code": "6080",
            "transaction_type": "Operating Expense",
            "confidence": 0.98,
            "rationale": "Standard bank processing and wire service charges."
        }
    if "REPAIR" in desc or "MAINTENANCE" in desc:
        return {
            "account_name": "Repairs & Maintenance",
            "account_code": "6100",
            "transaction_type": "Operating Expense",
            "confidence": 0.92,
            "rationale": "Equipment or vehicle repair expense."
        }

    # General Fallback Expense
    return {
        "account_name": "Office & General",
        "account_code": "6090",
        "transaction_type": "Operating Expense",
        "confidence": 0.85,
        "rationale": "General office administrative expense."
    }

async def classify_batch_with_gemini(tx_batch: list, chart_of_accounts: list) -> list:
    results = []
    for idx, tx in enumerate(tx_batch):
        classification = rule_based_classify(tx, chart_of_accounts)
        classification["tx_index"] = idx
        results.append(classification)
    return results