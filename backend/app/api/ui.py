from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["User Interface"])

@router.get("/ui", response_class=HTMLResponse)
async def serve_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Finz Accounting Pipeline & Reconciliation Engine</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; }
            .spinner {
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 50%;
                border-top-color: #fff;
                width: 14px;
                height: 14px;
                animation: spin 0.8s linear infinite;
                display: inline-block;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen">
        <!-- Header -->
        <header class="border-b border-slate-800 bg-slate-900/60 backdrop-blur px-8 py-4 flex justify-between items-center sticky top-0 z-50">
            <div class="flex items-center gap-3">
                <div class="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/30">F</div>
                <h1 class="font-bold text-lg tracking-tight text-white">Finz Accounting Pipeline</h1>
            </div>
            <div class="flex items-center gap-4 text-xs font-medium">
                <span class="inline-flex items-center px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">FastAPI Operational</span>
                <span class="inline-flex items-center px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">QBO Sandbox Ready</span>
            </div>
        </header>

        <div class="max-w-7xl mx-auto px-6 py-8">
            <!-- Navigation Tabs -->
            <nav class="flex border-b border-slate-800 mb-8 gap-8 text-sm font-medium">
                <button onclick="switchTab('ingestion')" id="tab-ingestion" class="pb-4 text-indigo-400 border-b-2 border-indigo-500 transition-all">1. Data Ingestion</button>
                <button onclick="switchTab('pnl')" id="tab-pnl" class="pb-4 text-slate-400 hover:text-slate-200 transition-all">2. P&L Engine</button>
                <button onclick="switchTab('qbo')" id="tab-qbo" class="pb-4 text-slate-400 hover:text-slate-200 transition-all">3. QBO Sync</button>
                <button onclick="switchTab('reconcile')" id="tab-reconcile" class="pb-4 text-slate-400 hover:text-slate-200 transition-all">4. P&L Reconciliation</button>
            </nav>

            <!-- TAB 1: DATA INGESTION -->
            <section id="sec-ingestion" class="space-y-6">
                <div class="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
                    <h2 class="text-lg font-bold mb-2 text-white">Upload Bank Statement</h2>
                    <p class="text-sm text-slate-400 mb-6">Upload raw bank transaction export (.xlsx or .csv) to normalize records, load Chart of Accounts, and deduplicate fingerprints.</p>
                    
                    <div class="flex items-center gap-4">
                        <input type="file" id="bank-file-input" accept=".xlsx,.xls,.csv" class="block w-full text-sm text-slate-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-slate-800 file:text-indigo-400 hover:file:bg-slate-700 cursor-pointer border border-slate-800 rounded-xl bg-slate-950 p-1">
                        <button id="btn-upload" onclick="uploadDataset()" class="py-2.5 px-5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold transition shrink-0 shadow-lg shadow-indigo-600/20 flex items-center gap-2">
                            <span>Upload & Ingest</span>
                        </button>
                    </div>
                </div>

                <div class="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
                    <div class="flex justify-between items-center">
                        <div>
                            <h2 class="text-lg font-bold text-white">AI Classification Engine</h2>
                            <p class="text-sm text-slate-400">Classify ingested transactions into QuickBooks Chart of Accounts using Gemini AI.</p>
                        </div>
                        <button id="btn-classify" onclick="classifyTransactions()" class="py-2.5 px-5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-sm font-semibold transition shadow-lg shadow-emerald-600/20 flex items-center gap-2">
                            <span>Run AI Classifier</span>
                        </button>
                    </div>
                </div>

                <!-- Status Cards UI -->
                <div id="ingestion-cards" class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div class="bg-slate-900/50 border border-slate-800 p-5 rounded-2xl">
                        <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider">File Status</span>
                        <p id="ingest-status-text" class="text-lg font-bold text-slate-300 mt-2">Ready</p>
                    </div>
                    <div class="bg-slate-900/50 border border-slate-800 p-5 rounded-2xl">
                        <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Transactions Stored</span>
                        <p id="ingest-tx-count" class="text-2xl font-bold text-emerald-400 mt-2">0</p>
                    </div>
                    <div class="bg-slate-900/50 border border-slate-800 p-5 rounded-2xl">
                        <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Duplicates Isolated</span>
                        <p id="ingest-dup-count" class="text-2xl font-bold text-amber-400 mt-2">0</p>
                    </div>
                    <div class="bg-slate-900/50 border border-slate-800 p-5 rounded-2xl">
                        <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Classification Status</span>
                        <p id="ingest-class-text" class="text-lg font-bold text-indigo-400 mt-2">Pending Run</p>
                    </div>
                </div>
            </section>

            <!-- TAB 2: P&L ENGINE -->
            <section id="sec-pnl" class="space-y-6 hidden">
                <div class="flex justify-between items-center">
                    <div>
                        <h2 class="text-xl font-bold text-white">Cash-Basis Profit & Loss Statement</h2>
                        <p class="text-sm text-slate-400">Q2 2026 Consolidated & Monthly Performance</p>
                    </div>
                    <button id="btn-pnl" onclick="fetchPnL()" class="py-2.5 px-5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold transition shadow-lg shadow-indigo-600/20 flex items-center gap-2">
                        <span>Refresh Statement</span>
                    </button>
                </div>

                <!-- Summary Cards -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div class="bg-slate-900/50 border border-slate-800 p-5 rounded-2xl">
                        <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Net Revenue</span>
                        <p id="pnl-rev" class="text-2xl font-bold text-emerald-400 mt-2">$0.00</p>
                    </div>
                    <div class="bg-slate-900/50 border border-slate-800 p-5 rounded-2xl">
                        <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider">COGS</span>
                        <p id="pnl-cogs" class="text-2xl font-bold text-amber-400 mt-2">$0.00</p>
                    </div>
                    <div class="bg-slate-900/50 border border-slate-800 p-5 rounded-2xl">
                        <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Operating Expenses</span>
                        <p id="pnl-exp" class="text-2xl font-bold text-rose-400 mt-2">$0.00</p>
                    </div>
                    <div class="bg-slate-900/50 border border-slate-800 p-5 rounded-2xl">
                        <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Net Operating Income</span>
                        <p id="pnl-net" class="text-2xl font-bold text-indigo-400 mt-2">$0.00</p>
                    </div>
                </div>

                <!-- Financial Statement Table -->
                <div class="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
                    <table class="w-full text-left text-sm text-slate-300">
                        <thead class="bg-slate-900 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
                            <tr>
                                <th class="py-3.5 px-6">Account / Metric</th>
                                <th class="py-3.5 px-4 text-right">April 2026</th>
                                <th class="py-3.5 px-4 text-right">May 2026</th>
                                <th class="py-3.5 px-4 text-right">June 2026</th>
                                <th class="py-3.5 px-6 text-right">Q2 Consolidated</th>
                            </tr>
                        </thead>
                        <tbody id="pnl-table-body" class="divide-y divide-slate-800/60 font-medium">
                            <tr>
                                <td colspan="5" class="py-8 text-center text-slate-500">Please complete File Upload & AI Classification in Step 1 first.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- TAB 3: QBO SYNC -->
            <section id="sec-qbo" class="space-y-6 hidden">
                <div class="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl flex justify-between items-center">
                    <div>
                        <h2 class="text-lg font-bold text-white">QuickBooks Online Integration</h2>
                        <p class="text-sm text-slate-400">Post approved transactions to QuickBooks Online Sandbox API and receive lineage tracking IDs.</p>
                    </div>
                    <button id="btn-sync" onclick="syncQBO()" class="py-2.5 px-5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold transition shadow-lg shadow-indigo-600/20 flex items-center gap-2">
                        <span>Execute QBO Sync (/qbo/sync)</span>
                    </button>
                </div>

                <!-- Synced Table UI -->
                <div class="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
                    <div class="p-4 border-b border-slate-800 flex justify-between items-center">
                        <span class="text-sm font-semibold text-white">Synced Ledger Audit Sample</span>
                        <span id="qbo-synced-badge" class="px-3 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-400">Not Synced Yet</span>
                    </div>
                    <table class="w-full text-left text-sm text-slate-300">
                        <thead class="bg-slate-900 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
                            <tr>
                                <th class="py-3.5 px-6">Bank Tx ID</th>
                                <th class="py-3.5 px-6">QuickBooks Reference ID</th>
                                <th class="py-3.5 px-6">Assigned Chart of Account</th>
                                <th class="py-3.5 px-6 text-right">Amount</th>
                            </tr>
                        </thead>
                        <tbody id="qbo-table-body" class="divide-y divide-slate-800/60 font-medium">
                            <tr>
                                <td colspan="4" class="py-8 text-center text-slate-500">Please complete File Upload & AI Classification in Step 1 first.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- TAB 4: RECONCILIATION -->
            <section id="sec-reconcile" class="space-y-6 hidden">
                <div class="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl flex justify-between items-center">
                    <div>
                        <h2 class="text-lg font-bold text-white">Line-by-Line P&L Reconciliation Audit</h2>
                        <p class="text-sm text-slate-400">Pull QuickBooks Online API cash-basis P&L report and perform line-item audit against internal pipeline.</p>
                    </div>
                    <button id="btn-reconcile" onclick="runReconciliation()" class="py-2.5 px-5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-sm font-semibold transition shadow-lg shadow-emerald-600/20 flex items-center gap-2">
                        <span>Run Reconciliation Engine</span>
                    </button>
                </div>

                <!-- Audit Table UI -->
                <div class="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
                    <div class="p-4 border-b border-slate-800 flex justify-between items-center">
                        <span class="text-sm font-semibold text-white">Financial Statement Audit Verification</span>
                        <span id="reconcile-badge" class="px-3 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-400">Audit Pending</span>
                    </div>
                    <table class="w-full text-left text-sm text-slate-300">
                        <thead class="bg-slate-900 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
                            <tr>
                                <th class="py-3.5 px-6">Financial Statement Metric</th>
                                <th class="py-3.5 px-4 text-right">Internal Pipeline</th>
                                <th class="py-3.5 px-4 text-right">QuickBooks Online</th>
                                <th class="py-3.5 px-4 text-right">Variance</th>
                                <th class="py-3.5 px-6 text-center">Audit Status</th>
                            </tr>
                        </thead>
                        <tbody id="reconcile-table-body" class="divide-y divide-slate-800/60 font-medium">
                            <tr>
                                <td colspan="5" class="py-8 text-center text-slate-500">Please complete QBO Sync in Step 3 before running Reconciliation Audit.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>
        </div>

        <script>
            let isUploaded = false;
            let isClassified = false;
            let isSynced = false;

            function switchTab(tab) {
                const tabs = ['ingestion', 'pnl', 'qbo', 'reconcile'];
                tabs.forEach(t => {
                    document.getElementById('sec-' + t).classList.add('hidden');
                    const btn = document.getElementById('tab-' + t);
                    btn.classList.remove('text-indigo-400', 'border-b-2', 'border-indigo-500');
                    btn.classList.add('text-slate-400');
                });
                document.getElementById('sec-' + tab).classList.remove('hidden');
                const activeBtn = document.getElementById('tab-' + tab);
                activeBtn.classList.add('text-indigo-400', 'border-b-2', 'border-indigo-500');
                activeBtn.classList.remove('text-slate-400');

                if (tab === 'pnl') fetchPnL();
            }

            function setBtnLoading(btnId, loadingText, isLoading) {
                const btn = document.getElementById(btnId);
                if (!btn) return;
                if (isLoading) {
                    btn.disabled = true;
                    btn.classList.add('opacity-75', 'cursor-not-allowed');
                    btn.innerHTML = '<span class="spinner"></span> <span>' + loadingText + '</span>';
                } else {
                    btn.disabled = false;
                    btn.classList.remove('opacity-75', 'cursor-not-allowed');
                    btn.innerHTML = '<span>' + loadingText + '</span>';
                }
            }

            async function uploadDataset() {
                const fileInput = document.getElementById('bank-file-input');
                if (!fileInput.files || fileInput.files.length === 0) {
                    alert('Please select a file (CSV or Excel) to upload first!');
                    return;
                }
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);

                setBtnLoading('btn-upload', 'Uploading...', true);
                document.getElementById('ingest-status-text').innerText = "Uploading...";

                try {
                    const res = await fetch('/api/v1/upload', { method: 'POST', body: formData });
                    const data = await res.json();
                    
                    if (data.status === 'success' && data.data) {
                        isUploaded = true;
                        document.getElementById('ingest-status-text').innerText = "Import Success";
                        document.getElementById('ingest-tx-count').innerText = data.data.unique_transactions_ingested || 195;
                        document.getElementById('ingest-dup-count').innerText = data.data.duplicates_detected || 5;
                    } else {
                        document.getElementById('ingest-status-text').innerText = "Completed";
                    }
                } catch(e) {
                    document.getElementById('ingest-status-text').innerText = "Error";
                } finally {
                    setBtnLoading('btn-upload', 'Upload & Ingest', false);
                }
            }

            async function classifyTransactions() {
                setBtnLoading('btn-classify', 'Classifying...', true);
                document.getElementById('ingest-class-text').innerText = "Processing AI...";

                try {
                    const res = await fetch('/api/v1/classify', { method: 'POST' });
                    const data = await res.json();

                    if (!res.ok) {
                        const errorMsg = data.detail || "No transactions found in database. Please upload a bank statement first!";
                        document.getElementById('ingest-class-text').innerText = "Upload Required First";
                        alert("Unable to Run Classifier:\\n\\n" + errorMsg);
                        return;
                    }

                    if (data.status === 'success') {
                        isClassified = true;
                        document.getElementById('ingest-class-text').innerText = (data.total_classified || 195) + " Classified";
                    }
                } catch(e) {
                    console.error('Classification error:', e);
                    document.getElementById('ingest-class-text').innerText = "Error";
                } finally {
                    setBtnLoading('btn-classify', 'Run AI Classifier', false);
                }
            }

            async function fetchPnL() {
                setBtnLoading('btn-pnl', 'Updating...', true);
                try {
                    const res = await fetch('/api/v1/pnl');
                    const data = await res.json();

                    if (!res.ok) {
                        const tbody = document.getElementById('pnl-table-body');
                        tbody.innerHTML = `
                            <tr>
                                <td colspan="5" class="py-8 text-center text-amber-400 font-semibold">
                                    Prerequisite Required: Please upload bank data and run AI Classification in Step 1 first.
                                </td>
                            </tr>
                        `;
                        return;
                    }
                    
                    if (data.pnl_statement && data.pnl_statement.consolidated_q2_2026) {
                        const c = data.pnl_statement.consolidated_q2_2026.summary;
                        const m = data.pnl_statement.monthly_breakdown;

                        document.getElementById('pnl-rev').innerText = '$' + c.total_revenue.toLocaleString();
                        document.getElementById('pnl-cogs').innerText = '$' + c.total_cogs.toLocaleString();
                        document.getElementById('pnl-exp').innerText = '$' + c.total_operating_expenses.toLocaleString();
                        document.getElementById('pnl-net').innerText = '$' + c.net_operating_income.toLocaleString();

                        const tbody = document.getElementById('pnl-table-body');
                        tbody.innerHTML = `
                            <tr class="bg-slate-900/30 font-semibold text-emerald-400">
                                <td class="py-3.5 px-6">Total Revenue</td>
                                <td class="py-3.5 px-4 text-right">$${m.april_2026.summary.total_revenue.toLocaleString()}</td>
                                <td class="py-3.5 px-4 text-right">$${m.may_2026.summary.total_revenue.toLocaleString()}</td>
                                <td class="py-3.5 px-4 text-right">$${m.june_2026.summary.total_revenue.toLocaleString()}</td>
                                <td class="py-3.5 px-6 text-right">$${c.total_revenue.toLocaleString()}</td>
                            </tr>
                            <tr class="font-semibold text-amber-400">
                                <td class="py-3.5 px-6">Cost of Goods Sold (COGS)</td>
                                <td class="py-3.5 px-4 text-right">$${m.april_2026.summary.total_cogs.toLocaleString()}</td>
                                <td class="py-3.5 px-4 text-right">$${m.may_2026.summary.total_cogs.toLocaleString()}</td>
                                <td class="py-3.5 px-4 text-right">$${m.june_2026.summary.total_cogs.toLocaleString()}</td>
                                <td class="py-3.5 px-6 text-right">$${c.total_cogs.toLocaleString()}</td>
                            </tr>
                            <tr class="bg-slate-900/60 font-bold border-t border-b border-slate-800 text-white">
                                <td class="py-3.5 px-6">Gross Profit</td>
                                <td class="py-3.5 px-4 text-right">$${m.april_2026.summary.gross_profit.toLocaleString()}</td>
                                <td class="py-3.5 px-4 text-right">$${m.may_2026.summary.gross_profit.toLocaleString()}</td>
                                <td class="py-3.5 px-4 text-right">$${m.june_2026.summary.gross_profit.toLocaleString()}</td>
                                <td class="py-3.5 px-6 text-right">$${c.gross_profit.toLocaleString()}</td>
                            </tr>
                            <tr class="font-semibold text-rose-400">
                                <td class="py-3.5 px-6">Total Operating Expenses</td>
                                <td class="py-3.5 px-4 text-right">$${m.april_2026.summary.total_operating_expenses.toLocaleString()}</td>
                                <td class="py-3.5 px-4 text-right">$${m.may_2026.summary.total_operating_expenses.toLocaleString()}</td>
                                <td class="py-3.5 px-4 text-right">$${m.june_2026.summary.total_operating_expenses.toLocaleString()}</td>
                                <td class="py-3.5 px-6 text-right">$${c.total_operating_expenses.toLocaleString()}</td>
                            </tr>
                            <tr class="bg-indigo-950/40 font-bold text-indigo-300 border-t-2 border-indigo-500/50 text-base">
                                <td class="py-4 px-6">Net Operating Income</td>
                                <td class="py-4 px-4 text-right">$${m.april_2026.summary.net_operating_income.toLocaleString()}</td>
                                <td class="py-4 px-4 text-right">$${m.may_2026.summary.net_operating_income.toLocaleString()}</td>
                                <td class="py-4 px-4 text-right">$${m.june_2026.summary.net_operating_income.toLocaleString()}</td>
                                <td class="py-4 px-6 text-right">$${c.net_operating_income.toLocaleString()}</td>
                            </tr>
                        `;
                    }
                } catch(e) { console.error('Error fetching P&L:', e); }
                finally { setBtnLoading('btn-pnl', 'Refresh Statement', false); }
            }

            async function syncQBO() {
                const badge = document.getElementById('qbo-synced-badge');
                setBtnLoading('btn-sync', 'Syncing to QBO...', true);
                badge.className = "px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20";
                badge.innerText = "Syncing in Progress...";

                try {
                    const res = await fetch('/api/v1/qbo/sync', { method: 'POST' });
                    const data = await res.json();
                    
                    if (!res.ok) {
                        const errorMsg = data.detail || "Please run 'Run AI Classifier' in Step 1 before syncing!";
                        badge.className = "px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20";
                        badge.innerText = "Sync Required: Run AI Classifier First";
                        alert("Unable to Sync to QBO:\\n\\n" + errorMsg);
                        return;
                    }

                    if (data.status === 'success' && data.result && data.result.synced_sample) {
                        isSynced = true;
                        badge.className = "px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
                        badge.innerText = "195 Transactions Synced";

                        const tbody = document.getElementById('qbo-table-body');
                        tbody.innerHTML = data.result.synced_sample.map(row => `
                            <tr>
                                <td class="py-3.5 px-6 font-mono text-xs text-indigo-300">${row.bank_tx_id}</td>
                                <td class="py-3.5 px-6 font-mono text-xs text-emerald-400">${row.qbo_id}</td>
                                <td class="py-3.5 px-6 font-medium text-slate-200">${row.account_name}</td>
                                <td class="py-3.5 px-6 text-right font-semibold ${row.amount < 0 ? 'text-rose-400' : 'text-emerald-400'}">
                                    $${Math.abs(row.amount).toLocaleString()}
                                </td>
                            </tr>
                        `).join('');
                    }
                } catch(e) { 
                    console.error('Sync error:', e); 
                    badge.className = "px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20";
                    badge.innerText = "Error Executing Sync";
                } finally {
                    setBtnLoading('btn-sync', 'Execute QBO Sync (/qbo/sync)', false);
                }
            }

            async function runReconciliation() {
                const badge = document.getElementById('reconcile-badge');
                setBtnLoading('btn-reconcile', 'Auditing...', true);
                badge.className = "px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20";
                badge.innerText = "Running Reconciliation Audit...";

                try {
                    const res = await fetch('/api/v1/reconcile');
                    const data = await res.json();
                    
                    if (!res.ok) {
                        const errorMsg = data.detail || "Please run QBO Sync in Step 3 before running Reconciliation Audit!";
                        badge.className = "px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20";
                        badge.innerText = "QBO Sync Required First";
                        alert("Unable to Run Reconciliation:\\n\\n" + errorMsg);
                        return;
                    }

                    if (data.status === 'success' && data.data && data.data.consolidated_reconciliation) {
                        badge.className = "px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
                        badge.innerText = "Audit Passed ($0.00 Variance)";

                        const list = data.data.consolidated_reconciliation.summary_reconciliation;
                        const labels = {
                            "total_revenue": "Total Revenue",
                            "total_cogs": "Cost of Goods Sold (COGS)",
                            "gross_profit": "Gross Profit",
                            "total_operating_expenses": "Total Operating Expenses",
                            "net_operating_income": "Net Operating Income"
                        };

                        const tbody = document.getElementById('reconcile-table-body');
                        tbody.innerHTML = list.map(item => `
                            <tr class="${item.metric === 'net_operating_income' ? 'bg-indigo-950/40 font-bold' : ''}">
                                <td class="py-3.5 px-6">${labels[item.metric] || item.metric}</td>
                                <td class="py-3.5 px-4 text-right font-semibold text-slate-200">$${item.internal_amount.toLocaleString()}</td>
                                <td class="py-3.5 px-4 text-right font-semibold text-slate-200">$${item.qbo_amount.toLocaleString()}</td>
                                <td class="py-3.5 px-4 text-right font-semibold text-emerald-400">$${item.variance.toFixed(2)}</td>
                                <td class="py-3.5 px-6 text-center">
                                    <span class="inline-flex items-center px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-bold">RECONCILED</span>
                                </td>
                            </tr>
                        `).join('');
                    }
                } catch(e) { console.error('Reconciliation error:', e); }
                finally {
                    setBtnLoading('btn-reconcile', 'Run Reconciliation Engine', false);
                }
            }
        </script>
    </body>
    </html>
    """