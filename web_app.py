"""
Web Dashboard for Indian Telecom Forensics Tool.
Built with FastAPI, Leaflet.js with Dark Satellite Map Tiles,
Speed/Velocity Analysis, and Geo-fencing Alerts.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from engine import (
    analyze_single_number,
    parse_cdr_records,
    INDIAN_CIRCLES,
    SPECIAL_NUMBERS,
    STD_CODES
)

app = FastAPI(title="Indian Telecom Forensic Analyzer", version="3.0")


class NumberRequest(BaseModel):
    number: str


class BatchRequest(BaseModel):
    numbers: List[str]


class CDRRequest(BaseModel):
    records: List[dict]
    geofence: Optional[dict] = None


@app.post("/api/analyze")
def api_analyze_single(req: NumberRequest):
    return analyze_single_number(req.number)


@app.post("/api/batch")
def api_analyze_batch(req: BatchRequest):
    results = [analyze_single_number(n) for n in req.numbers if n.strip()]
    return {"total": len(results), "results": results}


@app.post("/api/cdr")
def api_analyze_cdr(req: CDRRequest):
    return parse_cdr_records(req.records, req.geofence)


@app.get("/api/reference")
def api_reference():
    return {
        "circles": INDIAN_CIRCLES,
        "special_numbers": SPECIAL_NUMBERS,
        "std_codes": STD_CODES
    }


HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Indian Telecom Forensics & Tactical Triage Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        :root {
            --bg-dark: #070a10;
            --card-bg: #0d121d;
            --card-border: #1e293b;
            --accent: #00f0ff;
            --accent-dim: rgba(0, 240, 255, 0.12);
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --purple: #a855f7;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        header {
            background: #090e18;
            border-bottom: 1px solid #1e293b;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .badge {
            background: #0284c7;
            color: white;
            font-size: 0.72rem;
            padding: 4px 10px;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        .nav-tabs {
            display: flex;
            background: #090e18;
            border-bottom: 1px solid #1e293b;
            padding: 0 2rem;
            gap: 8px;
            overflow-x: auto;
        }
        .tab-btn {
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 0.9rem 1.4rem;
            font-size: 0.95rem;
            font-weight: 500;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
            white-space: nowrap;
        }
        .tab-btn:hover { color: var(--text-main); }
        .tab-btn.active {
            color: var(--accent);
            border-bottom-color: var(--accent);
        }
        main {
            padding: 1.75rem;
            max-width: 1440px;
            margin: 0 auto;
            width: 100%;
            flex: 1;
        }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .card h2 {
            font-size: 1.2rem;
            margin-bottom: 1rem;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .input-group {
            display: flex;
            gap: 12px;
            margin-bottom: 0.5rem;
        }
        input[type="text"], input[type="number"], select, textarea {
            background: #070a10;
            border: 1px solid #334155;
            color: var(--text-main);
            padding: 0.75rem 1rem;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.95rem;
        }
        input[type="text"]:focus, input[type="number"]:focus, textarea:focus, select:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 2px var(--accent-dim);
        }
        .btn {
            background: #0284c7;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
            font-size: 0.9rem;
        }
        .btn:hover { background: #0369a1; }
        .btn-accent {
            background: var(--accent);
            color: #000;
        }
        .btn-accent:hover { background: #38bdf8; }
        .btn-danger {
            background: #dc2626;
            color: white;
        }
        .btn-danger:hover { background: #b91c1c; }
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }
        .grid-3 {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
        }
        .grid-4 {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        @media (max-width: 1000px) {
            .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
        }
        .stat-card {
            background: #090e18;
            border: 1px solid var(--card-border);
            border-radius: 6px;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .stat-card .label {
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            font-family: 'JetBrains Mono', monospace;
        }
        .stat-card .value {
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--text-main);
            font-family: 'JetBrains Mono', monospace;
        }
        .stat-card.alert-card {
            border-color: #ef4444;
            background: rgba(239, 68, 68, 0.08);
        }
        .stat-card.alert-card .value { color: #f87171; }
        .meta-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
        }
        .meta-table tr {
            border-bottom: 1px solid #1e293b;
        }
        .meta-table td {
            padding: 0.75rem 0.5rem;
        }
        .meta-table td:first-child {
            color: var(--text-muted);
            width: 38%;
        }
        .meta-table td:last-child {
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-main);
        }
        .tag {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.78rem;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
        }
        .tag-success { background: rgba(16, 185, 129, 0.2); color: #34d399; }
        .tag-warning { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
        .tag-danger { background: rgba(239, 68, 68, 0.2); color: #f87171; }
        .tag-purple { background: rgba(168, 85, 247, 0.2); color: #c084fc; }
        .guidance-box {
            background: rgba(14, 165, 233, 0.08);
            border-left: 4px solid #0284c7;
            padding: 1rem;
            border-radius: 0 6px 6px 0;
            margin-top: 1rem;
            font-size: 0.88rem;
            line-height: 1.5;
        }
        .alert-banner {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid #ef4444;
            color: #fca5a5;
            padding: 1rem 1.25rem;
            border-radius: 6px;
            margin-bottom: 1.25rem;
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 0.9rem;
        }
        .legal-box {
            background: #181c24;
            border-left: 4px solid var(--warning);
            padding: 1rem;
            border-radius: 0 6px 6px 0;
            margin-top: 1rem;
            font-size: 0.88rem;
        }
        table.data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
            margin-top: 1rem;
        }
        table.data-table th, table.data-table td {
            padding: 0.75rem;
            border: 1px solid #1e293b;
            text-align: left;
        }
        table.data-table th {
            background: #111827;
            color: var(--accent);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            text-transform: uppercase;
        }
        table.data-table tr:hover {
            background: rgba(255, 255, 255, 0.02);
        }
        #map, #cdr-map {
            height: 420px;
            width: 100%;
            border-radius: 8px;
            border: 1px solid var(--card-border);
            margin-top: 0.75rem;
            background: #06090e;
        }
        .quick-samples {
            display: flex;
            gap: 8px;
            margin-top: 8px;
            flex-wrap: wrap;
            align-items: center;
        }
        .sample-pill {
            background: #131b2c;
            color: #94a3b8;
            border: 1px solid #1e293b;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
            cursor: pointer;
            font-family: 'JetBrains Mono', monospace;
            transition: all 0.2s;
        }
        .sample-pill:hover {
            color: var(--accent);
            border-color: var(--accent);
            background: rgba(0, 240, 255, 0.08);
        }
        .geofence-controls {
            background: #090e18;
            border: 1px solid #1e293b;
            border-radius: 6px;
            padding: 1rem;
            display: flex;
            gap: 12px;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <span style="font-size: 1.6rem;">🇮🇳</span>
            <div>
                <h1 style="font-size: 1.25rem; font-weight: 700;">Indian Telecom Forensics Triage Kit</h1>
                <p style="font-size: 0.78rem; color: var(--text-muted);">Tactical Satellite HUD &middot; Velocity Anomaly Engine &middot; Exclusion Geofencing</p>
            </div>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
            <span class="badge" style="background: #10b981;">Satellite Active</span>
            <span class="badge">DoT Compliant</span>
        </div>
    </header>

    <div class="nav-tabs">
        <button class="tab-btn active" onclick="switchTab('single', this)">🔍 Single Number Triage</button>
        <button class="tab-btn" onclick="switchTab('cdr', this)">📡 CDR, Velocity & Geofencing</button>
        <button class="tab-btn" onclick="switchTab('batch', this)">📋 Batch Number Analyzer</button>
        <button class="tab-btn" onclick="switchTab('reference', this)">⚖️ Legal Directives & LSAs</button>
    </div>

    <main>
        <!-- TAB 1: SINGLE NUMBER -->
        <div id="tab-single" class="tab-content active">
            <div class="card">
                <h2>🔍 Single Number Deep Triage</h2>
                <p style="color: var(--text-muted); margin-bottom: 0.75rem; font-size: 0.9rem;">
                    Enter any Indian 10-digit mobile number, landline with STD code, or statutory shortcode:
                </p>
                <div class="input-group">
                    <input type="text" id="single-input" placeholder="e.g. 9810012345 or +919810012345" value="+919810012345" onkeydown="if(event.key==='Enter') analyzeSingle()">
                    <button class="btn btn-accent" id="btn-triage" onclick="analyzeSingle()">Run Forensic Triage</button>
                </div>
                <div class="quick-samples">
                    <span style="font-size: 0.8rem; color: var(--text-muted);">Sample Presets:</span>
                    <span class="sample-pill" onclick="setAndRun('+919810012345')">9810012345 (Delhi Airtel)</span>
                    <span class="sample-pill" onclick="setAndRun('+919820012345')">9820012345 (Mumbai Vi)</span>
                    <span class="sample-pill" onclick="setAndRun('+919845012345')">9845012345 (Karnataka)</span>
                    <span class="sample-pill" onclick="setAndRun('01123344556')">01123344556 (Delhi Landline)</span>
                    <span class="sample-pill" onclick="setAndRun('112')">112 (National Emergency)</span>
                    <span class="sample-pill" onclick="setAndRun('1930')">1930 (Cyber Fraud Helpline)</span>
                </div>
            </div>

            <div id="single-result" style="display: none;">
                <div class="grid-2">
                    <div class="card">
                        <h2>📌 Telecom & Identity Metadata</h2>
                        <table class="meta-table">
                            <tr><td>Standard E.164:</td><td id="res-e164">-</td></tr>
                            <tr><td>National Format:</td><td id="res-national">-</td></tr>
                            <tr><td>Line Classification:</td><td id="res-type">-</td></tr>
                            <tr><td>Original Telecom Circle:</td><td id="res-circle">-</td></tr>
                            <tr><td>LSA Category & HQ:</td><td id="res-lsa">-</td></tr>
                            <tr><td>Original Operator Prefix:</td><td id="res-carrier">-</td></tr>
                            <tr><td>STD Area (If Landline):</td><td id="res-std">-</td></tr>
                            <tr><td>Timezone:</td><td id="res-tz">-</td></tr>
                        </table>

                        <div id="res-guidance" class="guidance-box"></div>
                    </div>

                    <div class="card">
                        <h2>🛰️ Satellite LSA & Regional Telecom View</h2>
                        <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 6px;">
                            Toggle between Dark Tactical, Satellite HD, and OpenStreet views in the top-right map control.
                        </p>
                        <div id="map"></div>
                        <div class="legal-box">
                            <strong>Legal Advisory (Sec 91 CrPC / Sec 94 BNSS):</strong>
                            <p style="margin-top: 4px; font-size: 0.84rem; color: #cbd5e1;">
                                Real-time GPS location and personal subscriber identification (SDR/CAF) are strictly confidential under Indian Telecommunications Law. To requisition CDRs, IPDRs, or subscriber details, submit an authorized legal notice to the Telecom Service Provider (TSP) Nodal Officer.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: CDR & VELOCITY / GEOFENCING -->
        <div id="tab-cdr" class="tab-content">
            <div class="card">
                <h2>📡 Call Detail Record (CDR), Velocity Analysis & Geofencing</h2>
                <p style="color: var(--text-muted); margin-bottom: 1rem; font-size: 0.9rem;">
                    Inspect cell tower hops, calculate speed/velocity between calls, detect impossible travel anomalies, and monitor exclusion geofences.
                </p>

                <!-- Geofence exclusion zone controls -->
                <div class="geofence-controls">
                    <strong style="color: var(--accent); font-size: 0.85rem; text-transform: uppercase; font-family: 'JetBrains Mono', monospace;">🚨 Exclusion Geofence:</strong>
                    <select id="geofence-preset" onchange="applyGeofencePreset()" style="padding: 0.4rem 0.8rem;">
                        <option value="custom">Custom Coordinates</option>
                        <option value="delhi_central" selected>New Delhi (Red Fort / Central - 28.6562, 77.2410)</option>
                        <option value="mumbai_bandra">Mumbai (Bandra Kurla Complex - 19.0600, 72.8680)</option>
                        <option value="bengaluru_vidhana">Bengaluru (Vidhana Soudha - 12.9797, 77.5907)</option>
                    </select>
                    <label style="font-size: 0.85rem;">Lat: <input type="number" id="geo-lat" value="28.6562" step="0.0001" style="width: 105px; padding: 4px 8px;"></label>
                    <label style="font-size: 0.85rem;">Lon: <input type="number" id="geo-lon" value="77.2410" step="0.0001" style="width: 105px; padding: 4px 8px;"></label>
                    <label style="font-size: 0.85rem;">Radius: <input type="number" id="geo-radius" value="5" min="1" max="50" style="width: 65px; padding: 4px 8px;"> km</label>
                    <button class="btn btn-accent" onclick="loadSampleCDR(true)" style="padding: 0.5rem 1rem;">Update & Run Analysis</button>
                </div>
            </div>

            <!-- Threat & Anomaly HUD Cards -->
            <div id="cdr-hud-container" style="display: none;">
                <div class="grid-4">
                    <div class="stat-card">
                        <span class="label">Total Records</span>
                        <span class="value" id="hud-total">-</span>
                    </div>
                    <div class="stat-card">
                        <span class="label">Total Duration</span>
                        <span class="value" id="hud-duration">-</span>
                    </div>
                    <div class="stat-card alert-card">
                        <span class="label">🚨 Velocity Anomalies</span>
                        <span class="value" id="hud-velocity-anomalies">0</span>
                    </div>
                    <div class="stat-card alert-card">
                        <span class="label">⚠️ Geofence Breaches</span>
                        <span class="value" id="hud-geofence-breaches">0</span>
                    </div>
                </div>

                <div id="alerts-container"></div>

                <div class="grid-2">
                    <div class="card">
                        <h2>🛰️ Tactical Trajectory & Geofence Map</h2>
                        <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 6px;">
                            High-resolution Satellite Hybrid with velocity vectors (Pulsing Red circle: Exclusion Geofence).
                        </p>
                        <div id="cdr-map"></div>
                    </div>

                    <div class="card">
                        <h2>📊 Top Cell Site / Tower Activity</h2>
                        <table class="data-table" id="cdr-towers-table">
                            <thead>
                                <tr>
                                    <th>Cell Site Identifier (LAC-CID)</th>
                                    <th>Event Count</th>
                                </tr>
                            </thead>
                            <tbody id="cdr-towers-tbody"></tbody>
                        </table>

                        <h3 style="margin-top: 1.5rem; color: var(--accent); font-size: 0.95rem;">Communication Split</h3>
                        <table class="meta-table" style="margin-top: 0.5rem;">
                            <tr><td>Outgoing Calls:</td><td id="cdr-out">-</td></tr>
                            <tr><td>Incoming Calls:</td><td id="cdr-in">-</td></tr>
                            <tr><td>SMS Events:</td><td id="cdr-sms">-</td></tr>
                        </table>
                    </div>
                </div>

                <div class="card">
                    <h2>Record Level Details with Velocity & Geofence Status</h2>
                    <table class="data-table" id="cdr-records-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Timestamp</th>
                                <th>Calling</th>
                                <th>Called</th>
                                <th>Type</th>
                                <th>Cell Site</th>
                                <th>Speed (km/h)</th>
                                <th>Velocity Status</th>
                                <th>Geofence</th>
                            </tr>
                        </thead>
                        <tbody id="cdr-records-tbody"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- TAB 3: BATCH ANALYZER -->
        <div id="tab-batch" class="tab-content">
            <div class="card">
                <h2>📋 Batch Phone Number Processing</h2>
                <p style="color: var(--text-muted); margin-bottom: 1rem; font-size: 0.9rem;">
                    Paste multiple phone numbers below (one per line, or separated by commas):
                </p>
                <textarea id="batch-input" rows="5" placeholder="9810012345&#10;9820012345&#10;9845012345&#10;01123344556&#10;112">9810012345&#10;9820012345&#10;9845012345&#10;01123344556&#10;1930</textarea>
                <div style="margin-top: 1rem; display: flex; gap: 10px;">
                    <button class="btn btn-accent" onclick="analyzeBatch()">Process Batch</button>
                    <button class="btn" onclick="clearBatch()">Clear</button>
                </div>
            </div>

            <div id="batch-results-container" class="card" style="display: none;">
                <h2>Forensic Batch Summary</h2>
                <table class="data-table" id="batch-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Input Number</th>
                            <th>E.164 Format</th>
                            <th>Type</th>
                            <th>Telecom Circle (State)</th>
                            <th>Original Operator</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="batch-tbody"></tbody>
                </table>
            </div>
        </div>

        <!-- TAB 4: LEGAL & REFERENCE -->
        <div id="tab-reference" class="tab-content">
            <div class="grid-2">
                <div class="card">
                    <h2>⚖️ Indian Statutory Investigation Reference</h2>
                    <div style="font-size: 0.9rem; line-height: 1.6; color: #d1d5db;">
                        <h4 style="color: var(--accent); margin-bottom: 6px;">1. Section 91 CrPC / Section 94 BNSS Notice:</h4>
                        <p style="margin-bottom: 12px;">
                            Investigating officers issue written requisitions to the Designated Nodal Officer of telecom operators (Jio, Airtel, Vi, BSNL) for:
                        </p>
                        <ul style="padding-left: 20px; margin-bottom: 16px;">
                            <li><strong>SDR (Subscriber Detail Record):</strong> Customer Application Form (CAF), KYC photo, address, alternate number.</li>
                            <li><strong>CDR (Call Detail Record):</strong> Call/SMS logs with Cell Global Identity (CGI) at start and termination of call.</li>
                            <li><strong>IPDR (IP Detail Record):</strong> Source/destination IP, port, data session duration.</li>
                        </ul>

                        <h4 style="color: var(--accent); margin-bottom: 6px;">2. Central Equipment Identity Register (CEIR):</h4>
                        <p style="margin-bottom: 12px;">
                            Portal: <code>https://ceir.gov.in</code><br>
                            Used to block stolen or lost mobile handsets by IMEI number across all Indian networks and monitor subsequent SIM insertions.
                        </p>

                        <h4 style="color: var(--accent); margin-bottom: 6px;">3. National Cyber Crime Reporting Portal (NCRP):</h4>
                        <p>
                            Helpline: <strong>1930</strong> | Portal: <code>https://cybercrime.gov.in</code><br>
                            Coordinates financial cyber fraud alerts with banks and telecom authorities.
                        </p>
                    </div>
                </div>

                <div class="card">
                    <h2>🇮🇳 22 Telecom Circles / LSAs Reference</h2>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Circle</th>
                                <th>Name</th>
                                <th>Cat.</th>
                                <th>HQ</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td><strong>DL</strong></td><td>Delhi</td><td>Metro</td><td>New Delhi</td></tr>
                            <tr><td><strong>MUM</strong></td><td>Mumbai</td><td>Metro</td><td>Mumbai</td></tr>
                            <tr><td><strong>KOL</strong></td><td>Kolkata</td><td>Metro</td><td>Kolkata</td></tr>
                            <tr><td><strong>MH</strong></td><td>Maharashtra & Goa</td><td>A</td><td>Pune</td></tr>
                            <tr><td><strong>GJ</strong></td><td>Gujarat</td><td>A</td><td>Ahmedabad</td></tr>
                            <tr><td><strong>AP</strong></td><td>Andhra & Telangana</td><td>A</td><td>Hyderabad</td></tr>
                            <tr><td><strong>KA</strong></td><td>Karnataka</td><td>A</td><td>Bengaluru</td></tr>
                            <tr><td><strong>TN</strong></td><td>Tamil Nadu & Chennai</td><td>A</td><td>Chennai</td></tr>
                            <tr><td><strong>KL</strong></td><td>Kerala</td><td>B</td><td>Kochi</td></tr>
                            <tr><td><strong>PB</strong></td><td>Punjab</td><td>B</td><td>Chandigarh</td></tr>
                            <tr><td><strong>HR</strong></td><td>Haryana</td><td>B</td><td>Ambala</td></tr>
                            <tr><td><strong>UPE</strong></td><td>UP (East)</td><td>B</td><td>Lucknow</td></tr>
                            <tr><td><strong>UPW</strong></td><td>UP (West)</td><td>B</td><td>Meerut</td></tr>
                            <tr><td><strong>RJ</strong></td><td>Rajasthan</td><td>B</td><td>Jaipur</td></tr>
                            <tr><td><strong>MP</strong></td><td>MP & Chhattisgarh</td><td>B</td><td>Bhopal</td></tr>
                            <tr><td><strong>WB</strong></td><td>West Bengal</td><td>B</td><td>Kolkata</td></tr>
                            <tr><td><strong>BR</strong></td><td>Bihar & Jharkhand</td><td>C</td><td>Patna</td></tr>
                            <tr><td><strong>OR</strong></td><td>Odisha</td><td>C</td><td>Bhubaneswar</td></tr>
                            <tr><td><strong>AS</strong></td><td>Assam</td><td>C</td><td>Guwahati</td></tr>
                            <tr><td><strong>NE</strong></td><td>North East</td><td>C</td><td>Shillong</td></tr>
                            <tr><td><strong>HP</strong></td><td>Himachal Pradesh</td><td>C</td><td>Shimla</td></tr>
                            <tr><td><strong>JK</strong></td><td>Jammu & Kashmir</td><td>C</td><td>Jammu</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </main>

    <script>
        let singleMap = null;
        let singleMarker = null;
        let singleCircle = null;

        let cdrMap = null;
        let cdrMarkers = [];
        let cdrPolyline = null;
        let geofenceCircle = null;

        // Tile layer definitions (Satellite, Dark Tactical, Street)
        function createBaseTileLayers() {
            const darkTactical = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; CartoDB &copy; OpenStreetMap',
                maxZoom: 19
            });

            const satelliteHD = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
                maxZoom: 19
            });

            const streetMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap',
                maxZoom: 19
            });

            return {
                "🛰️ Satellite HD": satelliteHD,
                "🕶️ Dark Tactical": darkTactical,
                "🗺️ Street Map": streetMap
            };
        }

        function switchTab(name, btn) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            if (btn) btn.classList.add('active');
            document.getElementById('tab-' + name).classList.add('active');
            
            setTimeout(() => {
                if (name === 'single' && singleMap) singleMap.invalidateSize();
                if (name === 'cdr' && cdrMap) cdrMap.invalidateSize();
            }, 100);
        }

        function setAndRun(num) {
            document.getElementById('single-input').value = num;
            analyzeSingle();
        }

        async function analyzeSingle() {
            const btn = document.getElementById('btn-triage');
            const num = document.getElementById('single-input').value.trim();
            if (!num) return;

            btn.innerText = "Analyzing...";
            btn.disabled = true;

            try {
                const res = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({number: num})
                });
                const data = await res.json();
                document.getElementById('single-result').style.display = 'block';

                document.getElementById('res-e164').innerText = data.e164 || 'N/A';
                document.getElementById('res-national').innerText = data.national || 'N/A';
                
                const typeTag = data.is_valid || data.is_special_service ? 
                    `<span class="tag tag-success">${data.line_type}</span>` : 
                    `<span class="tag tag-danger">Invalid Format</span>`;
                document.getElementById('res-type').innerHTML = typeTag;

                document.getElementById('res-circle').innerText = data.original_circle;
                
                const cm = data.circle_details || {};
                document.getElementById('res-lsa').innerText = cm.circle_code && cm.circle_code !== 'UNKNOWN' ? 
                    `${cm.circle_code} (Cat. ${cm.circle_category}) - HQ: ${cm.circle_hq}` : 'Pan-India / Central';
                document.getElementById('res-carrier').innerText = data.original_carrier;
                
                document.getElementById('res-std').innerText = data.std_code_info ? 
                    `0${data.std_code_info.std_code} (${data.std_code_info.location})` : 'N/A';
                document.getElementById('res-tz').innerText = (data.timezones || []).join(', ');

                const guidanceBox = document.getElementById('res-guidance');
                guidanceBox.innerHTML = '<strong>Forensic Observations:</strong><br>' + 
                    (data.investigative_guidance || []).map(g => '&bull; ' + g).join('<br>');

                initOrUpdateSingleMap(cm);

            } catch (err) {
                alert("Request error: " + err);
            } finally {
                btn.innerText = "Run Forensic Triage";
                btn.disabled = false;
            }
        }

        function initOrUpdateSingleMap(circleMeta) {
            const lat = circleMeta.lat || 20.5937;
            const lon = circleMeta.lon || 78.9629;
            const zoom = circleMeta.lat ? 9 : 5;

            if (!singleMap) {
                const baseLayers = createBaseTileLayers();
                singleMap = L.map('map', {
                    center: [lat, lon],
                    zoom: zoom,
                    layers: [baseLayers["🛰️ Satellite HD"]]
                });
                L.control.layers(baseLayers).addTo(singleMap);
            } else {
                singleMap.setView([lat, lon], zoom);
            }

            if (singleMarker) singleMap.removeLayer(singleMarker);
            if (singleCircle) singleMap.removeLayer(singleCircle);

            singleMarker = L.marker([lat, lon]).addTo(singleMap)
                .bindPopup(`<b>${circleMeta.circle_name || 'India'}</b><br>LSA Code: ${circleMeta.circle_code || 'N/A'}<br>HQ: ${circleMeta.circle_hq || 'N/A'}`)
                .openPopup();

            singleCircle = L.circle([lat, lon], {
                color: '#00f0ff',
                fillColor: '#00f0ff',
                fillOpacity: 0.15,
                radius: 40000
            }).addTo(singleMap);

            singleMap.invalidateSize();
        }

        function applyGeofencePreset() {
            const preset = document.getElementById('geofence-preset').value;
            if (preset === 'delhi_central') {
                document.getElementById('geo-lat').value = '28.6562';
                document.getElementById('geo-lon').value = '77.2410';
                document.getElementById('geo-radius').value = '5';
            } else if (preset === 'mumbai_bandra') {
                document.getElementById('geo-lat').value = '19.0600';
                document.getElementById('geo-lon').value = '72.8680';
                document.getElementById('geo-radius').value = '6';
            } else if (preset === 'bengaluru_vidhana') {
                document.getElementById('geo-lat').value = '12.9797';
                document.getElementById('geo-lon').value = '77.5907';
                document.getElementById('geo-radius').value = '5';
            }
        }

        async function loadSampleCDR(keepView) {
            const gLat = parseFloat(document.getElementById('geo-lat').value);
            const gLon = parseFloat(document.getElementById('geo-lon').value);
            const gRadius = parseFloat(document.getElementById('geo-radius').value);

            // Sample dataset with deliberate movement, including an impossible velocity jump
            const sample = [
                {"timestamp": "2026-10-19 10:15:22", "caller": "9810012345", "callee": "9820098765", "call_type": "OUTGOING", "duration": 182, "lac": "40410", "cell_id": "14201", "lat": 28.6565, "lon": 77.2415},
                {"timestamp": "2026-10-19 10:35:40", "caller": "9810012345", "callee": "9820098765", "call_type": "OUTGOING", "duration": 45, "lac": "40410", "cell_id": "14202", "lat": 28.6650, "lon": 77.2480},
                {"timestamp": "2026-10-19 11:10:11", "caller": "9871122334", "callee": "9810012345", "call_type": "INCOMING", "duration": 340, "lac": "40410", "cell_id": "14208", "lat": 28.6800, "lon": 77.2600},
                {"timestamp": "2026-10-19 12:45:00", "caller": "9810012345", "callee": "9830055443", "call_type": "SMS", "duration": 0, "lac": "40410", "cell_id": "14305", "lat": 28.7200, "lon": 77.2900},
                // High-speed jump / anomaly: 180 km away within 4 minutes!
                {"timestamp": "2026-10-19 12:49:10", "caller": "9810012345", "callee": "9820098765", "call_type": "OUTGOING", "duration": 520, "lac": "40410", "cell_id": "14999", "lat": 27.1767, "lon": 78.0081},
                {"timestamp": "2026-10-19 23:30:25", "caller": "9999887766", "callee": "9810012345", "call_type": "INCOMING", "duration": 60, "lac": "40410", "cell_id": "14999", "lat": 27.1850, "lon": 78.0150}
            ];

            const geofencePayload = {
                lat: gLat,
                lon: gLon,
                radius_km: gRadius
            };

            const res = await fetch('/api/cdr', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({records: sample, geofence: geofencePayload})
            });
            const data = await res.json();

            // Populate HUD
            document.getElementById('hud-total').innerText = data.total_records;
            document.getElementById('hud-duration').innerText = `${data.total_duration_minutes} min`;
            
            const velAnomalies = (data.anomalies || []).filter(a => a.type === 'IMPOSSIBLE_VELOCITY');
            document.getElementById('hud-velocity-anomalies').innerText = velAnomalies.length;
            document.getElementById('hud-geofence-breaches').innerText = (data.geofence_breaches || []).length;

            // Render Alert Banners
            const alertsDiv = document.getElementById('alerts-container');
            alertsDiv.innerHTML = '';
            (data.anomalies || []).forEach(a => {
                if (a.severity === 'CRITICAL') {
                    alertsDiv.innerHTML += `
                        <div class="alert-banner">
                            <span style="font-size: 1.5rem;">🚨</span>
                            <div>
                                <strong>CRITICAL FORENSIC ANOMALY (Record #${a.record_id} at ${a.timestamp}):</strong><br>
                                ${a.description}
                            </div>
                        </div>
                    `;
                }
            });

            if ((data.geofence_breaches || []).length > 0) {
                alertsDiv.innerHTML += `
                    <div class="alert-banner" style="background: rgba(245, 158, 11, 0.15); border-color: #f59e0b; color: #fde68a;">
                        <span style="font-size: 1.5rem;">⚠️</span>
                        <div>
                            <strong>GEOFENCE EXCLUSION BREACH DETECTED:</strong><br>
                            ${data.geofence_breaches.length} cell tower interaction(s) recorded within ${gRadius} km of Target Zone (${gLat}, ${gLon}).
                        </div>
                    </div>
                `;
            }

            document.getElementById('cdr-out').innerText = data.call_type_breakdown.OUTGOING;
            document.getElementById('cdr-in').innerText = data.call_type_breakdown.INCOMING;
            document.getElementById('cdr-sms').innerText = data.call_type_breakdown.SMS;

            // Top Towers Table
            const towerTbody = document.getElementById('cdr-towers-tbody');
            towerTbody.innerHTML = '';
            (data.top_towers || []).forEach(t => {
                towerTbody.innerHTML += `<tr><td><strong>${t[0]}</strong></td><td><span class="tag tag-warning">${t[1]} hits</span></td></tr>`;
            });

            // Record Level Table with Velocity & Geofence
            const recTbody = document.getElementById('cdr-records-tbody');
            recTbody.innerHTML = '';
            (data.records || []).forEach(r => {
                let velTag = `<span class="tag tag-success">Stationary</span>`;
                if (r.velocity_status === 'IMPOSSIBLE_VELOCITY') {
                    velTag = `<span class="tag tag-danger">🚨 ${r.speed_kmh} km/h (IMPOSSIBLE)</span>`;
                } else if (r.velocity_status === 'HIGH_SPEED_TRANSIT') {
                    velTag = `<span class="tag tag-warning">${r.speed_kmh} km/h (High Speed)</span>`;
                } else if (r.speed_kmh) {
                    velTag = `<span class="tag tag-success">${r.speed_kmh} km/h</span>`;
                }

                let geoTag = r.inside_geofence ? 
                    `<span class="tag tag-danger">⚠️ BREACH</span>` : 
                    `<span class="tag" style="background: #1e293b; color: #64748b;">Clear</span>`;

                recTbody.innerHTML += `
                    <tr>
                        <td>${r.record_id}</td>
                        <td>${r.timestamp}</td>
                        <td>${r.caller}</td>
                        <td>${r.callee}</td>
                        <td><span class="tag ${r.call_type === 'OUTGOING' ? 'tag-success' : 'tag-warning'}">${r.call_type}</span></td>
                        <td>${r.tower_identifier}</td>
                        <td>${r.speed_kmh ? r.speed_kmh : '-'}</td>
                        <td>${velTag}</td>
                        <td>${geoTag}</td>
                    </tr>
                `;
            });

            document.getElementById('cdr-hud-container').style.display = 'block';

            // Map Initialization & Updates
            initOrUpdateCDRMap(data.records, gLat, gLon, gRadius);
        }

        function initOrUpdateCDRMap(records, gLat, gLon, gRadius) {
            if (!cdrMap) {
                const baseLayers = createBaseTileLayers();
                cdrMap = L.map('cdr-map', {
                    center: [gLat, gLon],
                    zoom: 11,
                    layers: [baseLayers["🛰️ Satellite HD"]]
                });
                L.control.layers(baseLayers).addTo(cdrMap);
            }

            // Clear old layers
            cdrMarkers.forEach(m => cdrMap.removeLayer(m));
            cdrMarkers = [];
            if (cdrPolyline) cdrMap.removeLayer(cdrPolyline);
            if (geofenceCircle) cdrMap.removeLayer(geofenceCircle);

            // Draw Geofence Exclusion Zone
            geofenceCircle = L.circle([gLat, gLon], {
                color: '#ef4444',
                fillColor: '#ef4444',
                fillOpacity: 0.22,
                weight: 2,
                dashArray: '6, 8',
                radius: gRadius * 1000
            }).addTo(cdrMap).bindPopup(`<b>🚨 EXCLUSION GEOFENCE ZONE</b><br>Radius: ${gRadius} km<br>Center: ${gLat}, ${gLon}`);

            const points = [];
            records.forEach(r => {
                if (r.lat && r.lon) {
                    points.push([r.lat, r.lon]);
                    const isBreach = r.inside_geofence;
                    const isImpossible = r.velocity_status === 'IMPOSSIBLE_VELOCITY';

                    let markerColor = isImpossible ? '#dc2626' : (isBreach ? '#f59e0b' : '#00f0ff');
                    let markerRadius = isImpossible ? 10 : 7;

                    const m = L.circleMarker([r.lat, r.lon], {
                        radius: markerRadius,
                        color: '#ffffff',
                        weight: 2,
                        fillColor: markerColor,
                        fillOpacity: 0.9
                    }).addTo(cdrMap).bindPopup(`
                        <b>Record #${r.record_id} (${r.call_type})</b><br>
                        Time: ${r.timestamp}<br>
                        Tower: ${r.tower_identifier}<br>
                        Speed: ${r.speed_kmh ? r.speed_kmh + ' km/h' : 'Initial / Stationary'}<br>
                        Status: ${r.velocity_status}<br>
                        Geofence: ${isBreach ? '<b style="color:red">INSIDE EXCLUSION ZONE</b>' : 'Clear'}
                    `);
                    cdrMarkers.push(m);
                }
            });

            if (points.length > 1) {
                cdrPolyline = L.polyline(points, {
                    color: '#00f0ff',
                    weight: 3,
                    dashArray: '4, 8'
                }).addTo(cdrMap);
                cdrMap.fitBounds(L.latLngBounds(points).pad(0.2));
            } else {
                cdrMap.setView([gLat, gLon], 11);
            }

            cdrMap.invalidateSize();
        }

        async function analyzeBatch() {
            const raw = document.getElementById('batch-input').value;
            const lines = raw.split(/[\\n,]+/).map(x => x.trim()).filter(x => x.length > 0);
            if (lines.length === 0) return;

            const res = await fetch('/api/batch', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({numbers: lines})
            });
            const data = await res.json();

            const tbody = document.getElementById('batch-tbody');
            tbody.innerHTML = '';
            data.results.forEach((r, idx) => {
                const tr = document.createElement('tr');
                const isVal = r.is_valid || r.is_special_service ? 
                    '<span class="tag tag-success">VALID</span>' : '<span class="tag tag-danger">INVALID</span>';
                tr.innerHTML = `
                    <td>${idx + 1}</td>
                    <td><strong>${r.query_input}</strong></td>
                    <td>${r.e164 || '-'}</td>
                    <td>${r.line_type}</td>
                    <td>${r.original_circle}</td>
                    <td>${r.original_carrier}</td>
                    <td>${isVal}</td>
                `;
                tbody.appendChild(tr);
            });
            document.getElementById('batch-results-container').style.display = 'block';
        }

        function clearBatch() {
            document.getElementById('batch-input').value = '';
            document.getElementById('batch-results-container').style.display = 'none';
        }

        window.addEventListener('DOMContentLoaded', () => {
            analyzeSingle();
            loadSampleCDR();
        });
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=HTML_CONTENT)


if __name__ == "__main__":
    print("[*] Starting Indian Telecom Forensics Web Dashboard on http://127.0.0.1:8899 ...")
    uvicorn.run(app, host="127.0.0.1", port=8899, log_level="info")
