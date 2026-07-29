# Finz AI-Native Accounting & Data Pipeline

An end-to-end financial data pipeline, AI-powered classification engine, QuickBooks Online (QBO) sync manager, and automated P&L reconciliation audit.

## Core Features
1. **Ingestion & Deduplication:** Parses multi-sheet Excel workbooks and CSV files, generating cryptographic transaction fingerprints to flag duplicates across overlapping files.
2. **AI Classification:** Uses Google Gemini to categorize transactions against the QuickBooks Chart of Accounts while filtering out non-P&L items (Transfers, Owner Draws, Fixed Assets).
3. **P&L Statement Engine:** Aggregates cash-basis financials for Q2 2026 (April, May, June, and Consolidated).
4. **Reconciliation Audit:** Performs a line-by-line audit comparing internal pipeline totals against QBO sandbox records with zero variance ($0.00).

## Setup & Execution Instructions

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Ensure your `.env` file inside the `backend/` folder contains your credentials:
   ```env
   MONGODB_URL=your_mongodb_connection_string
   GEMINI_API_KEY=your_google_gemini_api_key
   ```

5. **Run the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

6. **Access the application:**
   Open your browser and navigate to `http://127.0.0.1:8000` to interact with the full dashboard.
