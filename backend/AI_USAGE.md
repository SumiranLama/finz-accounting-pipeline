# AI Usage & Validation Note

## 🛠️ AI Tools Used
* **Primary AI Engine:** Google Gemini API (integrated directly into the application backend for transaction classification).
* **Development Assistants:** ChatGPT, and Gemini for code scaffolding, structuring FastAPI routers, writing MongoDB queries, and designing the frontend user interface.

---

## 💡 What the AI Generated
* **Classification Logic:** Prompt structures and parsing logic to evaluate raw bank transaction descriptions and map them against the QuickBooks Chart of Accounts categories (Revenue, COGS, and Operating Expenses).
* **Boilerplate & Routing:** Initial FastAPI endpoint layouts (`upload.py`, `classify.py`, `pnl.py`, `qbo.py`, `reconcile.py`), asynchronous MongoDB Motor driver connections, and UI templates (`ui.py`).
* **Deduplication Scaffolding:** Hashing logic used to generate cryptographic fingerprints for transaction deduplication across overlapping files.

---

## 🔍 Independent Validation & Auditing
While AI tools assisted with code generation and narrative classification, all financial logic and outputs were rigorously audited and verified independently:
* **Accounting Constraints:** Verified that cash-basis rules, exclusions of owner activity, internal transfers, fixed-asset purchases, and duplicate records were strictly enforced by the backend code per challenge instructions.
* **Numerical Accuracy:** Validated that the application's internal P&L aggregations and reconciliation totals match the QuickBooks Online sandbox records with zero variance ($0.00).